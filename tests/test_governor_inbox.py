from copy import deepcopy
from pathlib import Path
import json
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import cycle
import governor
import governor_inbox as inbox
import reflections
import week_one

ROOT = Path(__file__).resolve().parents[1]
PLAY = 'PLAY-b803b289-ff43-4f29-aa48-5ce4dd62d24d.json'


class GovernorInboxTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for name in ['operations/governor', 'config', 'agents', 'handoffs/chat_aiden/2026-09-27_digest-threshold']:
            shutil.copytree(ROOT / name, self.root / name)
        # Synthetic histories have no production generation to retire.
        cycle.write_json(self.root / 'config/provider-dispositions.json', {'decisions': []}, replace=True)
        for name in [cycle.CANONICAL, 'CULTURE.md', 'operations/questions.json']:
            shutil.copy2(ROOT / name, self.root / name)

    def feed(self):
        return self.root / inbox.INBOX / PLAY

    def read(self):
        return cycle.read_json(self.feed())

    def write(self, value):
        cycle.write_json(self.feed(), value, replace=True)

    def test_original_play_rederived_and_digest_separate_from_governor(self):
        result = inbox.snapshot(self.root)
        self.assertEqual(result['errors'], [])
        self.assertEqual(len(result['entries']), 2)
        play = next(e for e in result['entries'] if e['kind'] == 'boss_play')
        delivery = play['payload']['governor_input']
        self.assertEqual([r['preserved']['text'] for r in delivery['rounds']],
                         ['Shared direction', 'Until payment', 'Who can carry it?'])
        self.assertTrue(all(r['sunk'] for r in delivery['rounds']))
        self.assertFalse(delivery['evidence_changed'])
        self.assertEqual(delivery['applied_powers'], [])
        self.assertEqual(play['responses'], [])
        digest = next(e for e in result['entries'] if e['kind'] == 'digestion')
        self.assertIn('Digest Aiden', digest['actor']['name'])
        self.assertIn('saṃskāra', digest['context_documents'][0]['text'])
        self.assertFalse((self.root / reflections.STORE).exists())

    def test_repeat_and_interrupted_imports_are_idempotent(self):
        original_post = reflections.post
        calls = []
        def interrupt_after_first(root, value):
            calls.append(value)
            if len(calls) == 2:
                raise OSError('simulated interruption')
            return original_post(root, value)
        with patch.object(reflections, 'post', side_effect=interrupt_after_first):
            with self.assertRaises(OSError):
                inbox.ingest(self.root)
        self.assertEqual(len(reflections.load(self.root)['entries']), 1)
        first = inbox.ingest(self.root)
        before = cycle.digest(reflections.load(self.root))
        second = inbox.ingest(self.root)
        self.assertEqual(before, cycle.digest(reflections.load(self.root)))
        self.assertEqual(len(reflections.load(self.root)['entries']), 2)
        self.assertEqual([e['reflection_id'] for e in first['entries']],
                         [e['reflection_id'] for e in second['entries']])

    def test_tampered_bundle_hash_or_claimed_delivery_never_projects(self):
        original = self.read()
        bad = deepcopy(original)
        bad['bundle_sha256'] = '0' * 64
        self.write(bad)
        result = inbox.ingest(self.root)
        self.assertEqual(len(result['errors']), 1)
        self.assertEqual(len(reflections.load(self.root)['entries']), 1)
        self.write(original)
        bundle_path = self.root / original['bundle_ref']
        bundle = cycle.read_json(bundle_path)
        bundle['governor_input']['rounds'][0]['preserved']['evidence_status'] = 'unknown'
        cycle.write_json(bundle_path, bundle, replace=True)
        original['bundle_sha256'] = cycle.digest(bundle)
        self.write(original)
        result = inbox.snapshot(self.root)
        self.assertIn('differs', result['errors'][0]['reason'])

    def test_bad_paths_and_malformed_input_do_not_hide_valid_digest(self):
        for ref in ['../../CULTURE.md', str(ROOT / 'CULTURE.md')]:
            value = self.read()
            value['bundle_ref'] = ref
            self.write(value)
            result = inbox.ingest(self.root)
            self.assertEqual([e['kind'] for e in result['entries']], ['digestion'])
            self.assertEqual(len(result['errors']), 1)
        self.feed().write_text('{invalid json')
        result = inbox.snapshot(self.root)
        self.assertEqual(len(result['entries']), 1)
        self.assertEqual(len(result['errors']), 1)

    def test_symlink_bundle_cannot_escape_its_folder(self):
        value = self.read()
        path = self.root / value['bundle_ref']
        contents = path.read_bytes()
        path.unlink()
        outside = self.root / 'outside.json'
        outside.write_bytes(contents)
        path.symlink_to(outside)
        result = inbox.snapshot(self.root)
        self.assertIn('symlinks', result['errors'][0]['reason'])

    def test_historical_play_retains_its_epoch_without_mutating_question(self):
        path = self.root / 'operations/questions.json'
        registry = cycle.read_json(path)
        registry['questions']['Q-MEANING-TRANSLATION-BOSS']['epoch'] = 2
        cycle.write_json(path, registry, replace=True)
        before = path.read_bytes()
        play = next(e for e in inbox.ingest(self.root)['entries'] if e['kind'] == 'boss_play')
        self.assertEqual(play['payload']['epoch_status'], 'historical')
        self.assertEqual(play['payload']['governor_input']['epoch'], 1)
        self.assertEqual(before, path.read_bytes())

    def test_review_rest_and_reconsideration_reuse_existing_mailbox(self):
        entry = inbox.ingest(self.root)['entries'][0]
        rid = entry['reflection_id']
        response = {'review_id': 'TEST-GOVERNOR-1', 'actor': 'Test Governor / unittest',
                    'reflection_ids': [rid], 'disposition': 'Let this rest', 'summary': 'Fixture review.',
                    'keep_open': False}
        reflections.respond(self.root, response)
        reviewed = inbox.snapshot(self.root)['entries'][0]
        self.assertEqual(reviewed['status'], 'reviewed')
        self.assertEqual(reviewed['responses'][0]['actor'], 'Test Governor / unittest')
        reflections.respond(self.root, {**response, 'review_id': 'TEST-GOVERNOR-2',
                                        'keep_open': True, 'summary': 'Reconsider with new context.'})
        reconsidered = inbox.snapshot(self.root)['entries'][0]
        self.assertEqual(reconsidered['status'], 'pending')
        self.assertEqual(len(reconsidered['responses']), 2)
        review = governor.prepare(self.root)
        self.assertEqual(len(review['inputs']['direct_inbox']['entries']), 2)

    def test_pagination_exposes_remainder_and_unknown_schema_stays_unhandled(self):
        page = inbox.snapshot(self.root, limit=1)
        self.assertEqual(page['remaining_count'], 1)
        self.assertEqual(page['next_offset'], 1)
        self.assertEqual(inbox.snapshot(self.root, limit=1, offset=1)['remaining_count'], 0)
        value = self.read()
        value['schema_version'] = 'unknown-future-schema'
        self.write(value)
        result = inbox.ingest(self.root)
        self.assertEqual(len(result['errors']), 1)
        self.assertEqual(len(reflections.load(self.root)['entries']), 1)

    def test_provider_brake_still_queues_input_and_imports_separate_governor_reply(self):
        state = {'version': 1, 'runs': {}, 'closed': False, 'brake': {'reason': 'fixture receipt brake'}}
        week_one.write(self.root, week_one.BASE / 'run-manifest.json', state)
        with patch.object(week_one, 'gather', return_value={'items': [], 'sensors': []}), \
                patch.object(week_one, 'durable'):
            result = week_one.prepare(self.root, 'TEST-INBOX', now='2026-09-27T18:00:00Z')
        self.assertEqual(result['result'], 'operator_review_required')
        self.assertTrue(all(e['status'] == 'pending' for e in inbox.snapshot(self.root)['entries']))
        self.assertFalse((self.root / week_one.run_path('TEST-INBOX', 'request.json')).exists())
        entry = inbox.snapshot(self.root)['entries'][0]
        packet = {'question_id': 'Q-MEANING-TRANSLATION-BOSS',
                  'reflection': {'summary': 'Fixture scheduled Governor self-reflection.'},
                  'governor_response': {'reflection_ids': [entry['reflection_id']],
                                        'summary': 'Fixture review; let this input rest.', 'keep_open': False}}
        week_one.write(self.root, Path('handoffs/week_one_governor/2026-09-28.json'), packet)
        self.assertEqual(week_one.ingest_thought_partners(self.root)[0]['status'], 'imported')
        self.assertEqual(inbox.snapshot(self.root)['entries'][0]['status'], 'reviewed')
        before = cycle.digest(reflections.load(self.root))
        week_one.ingest_thought_partners(self.root)
        self.assertEqual(before, cycle.digest(reflections.load(self.root)))


if __name__ == '__main__':
    unittest.main()
