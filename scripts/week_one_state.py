#!/usr/bin/env python3
"""Copy only operational data to/from a separate, fast-forward-only state branch."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BRANCH = 'week-one-state'
PATHS = ['operations/week-one', 'operations/questions.json', 'operations/reflections/mailbox.json']


def git(*args, cwd=ROOT, check=True):
    return subprocess.run(['git', *args], cwd=cwd, check=check, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=['load', 'save'])
    args = p.parse_args()
    git('fetch', '--no-tags', 'origin', BRANCH)
    remote_sha = git('rev-parse', f'origin/{BRANCH}').stdout.strip()
    baseline = Path(git('rev-parse', '--git-path', 'week-one-state-baseline').stdout.strip())
    if not baseline.is_absolute():
        baseline = ROOT / baseline
    if args.command == 'load':
        # Reject symlinks/submodules in imported data. Never import code or policy.
        tree = git('ls-tree', '-r', f'origin/{BRANCH}', '--', *PATHS).stdout
        if any(line.split()[0] != '100644' for line in tree.splitlines()):
            raise RuntimeError('State branch contains a non-regular data file')
        git('restore', '--source', f'origin/{BRANCH}', '--worktree', '--', *PATHS)
        baseline.write_text(remote_sha + '\n')
        return
    if not baseline.exists() or baseline.read_text().strip() != remote_sha:
        raise RuntimeError('Operational state changed since load/save; preserve local work and reconcile before publishing')
    target = Path(tempfile.mkdtemp(prefix='week-one-state-'))
    try:
        git('worktree', 'add', '--detach', str(target), f'origin/{BRANCH}')
        for path in PATHS:
            source, dest = ROOT / path, target / path
            if source.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(source, dest, symlinks=False)
            elif source.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
        git('add', '--', *PATHS, cwd=target)
        if not git('diff', '--cached', '--quiet', cwd=target, check=False).returncode:
            return
        git('-c', 'user.name=Dis-Unity Week One', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
            'commit', '-m', 'Checkpoint Week One ' + os.environ.get('WEEK_ONE_RUN_ID', 'operator'), cwd=target)
        # A concurrent remote edit rejects this write; do not reset or force over it.
        git('push', 'origin', f'HEAD:refs/heads/{BRANCH}', cwd=target)
        baseline.write_text(git('rev-parse', 'HEAD', cwd=target).stdout.strip() + '\n')
        print('Operational checkpoint saved to week-one-state')
    finally:
        git('worktree', 'remove', '--force', str(target), check=False)
        shutil.rmtree(target, ignore_errors=True)


if __name__ == '__main__':
    main()
