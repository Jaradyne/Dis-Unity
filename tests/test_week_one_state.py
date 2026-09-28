from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import week_one_state as state


class OperationalCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'checkout'
        self.remote = Path(self.temporary.name) / 'remote.git'
        self.root.mkdir()
        self.git('init', '--bare', '--initial-branch=week-one-state', str(self.remote))
        self.git('init', '--initial-branch=week-one-state')
        self.git('config', 'user.name', 'Checkpoint fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        for name in ('operations/week-one/state.json', 'operations/questions.json', 'operations/reflections/mailbox.json'):
            self.write(name, '{}\n')
        self.git('add', '.')
        self.git('commit', '-m', 'Old state without optional folders')
        self.git('remote', 'add', 'origin', str(self.remote))
        self.git('push', 'origin', 'week-one-state')
        self.git('checkout', '-b', 'main')

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True, text=True).stdout

    def write(self, path, contents):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents)

    def invoke(self, action):
        with patch.object(state, 'ROOT', self.root), patch.object(sys, 'argv', ['week_one_state.py', action]):
            state.main()

    def test_old_state_loads_and_new_optional_data_roundtrips_without_code(self):
        self.invoke('load')
        self.invoke('save')  # Missing optional folders must not produce a pathspec failure.
        for path in ('operations/garden/runs/example.json', 'digestion/threshold/garden/example.json',
                     'digestion/threshold/api/runs/example.json'):
            self.write(path, '{"fixture":true}\n')
        self.write('scripts/not-state.py', 'private implementation\n')
        self.invoke('save')
        self.git('fetch', 'origin', 'week-one-state')
        names = self.git('ls-tree', '-r', '--name-only', 'origin/week-one-state').splitlines()
        self.assertIn('operations/garden/runs/example.json', names)
        self.assertIn('digestion/threshold/garden/example.json', names)
        self.assertIn('digestion/threshold/api/runs/example.json', names)
        self.assertNotIn('scripts/not-state.py', names)
        (self.root / 'operations/garden/runs/example.json').unlink()
        self.invoke('load')
        self.assertEqual((self.root / 'operations/garden/runs/example.json').read_text(), '{"fixture":true}\n')

    def test_concurrent_state_change_rejects_publish_without_losing_local_work(self):
        self.invoke('load')
        self.write('operations/garden/runs/local.json', '{"local":true}\n')
        self.write('operations/week-one/state.json', '{"remote":true}\n')
        self.git('add', 'operations/week-one/state.json')
        self.git('commit', '-m', 'Another operator state update')
        self.git('push', 'origin', 'HEAD:week-one-state')
        with self.assertRaisesRegex(RuntimeError, 'changed since'):
            self.invoke('save')
        self.assertTrue((self.root / 'operations/garden/runs/local.json').exists())


if __name__ == '__main__':
    unittest.main()
