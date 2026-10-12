#!/usr/bin/env python3
"""Rebuild/check the pinned supplied-content case; no network or shared-state writes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

CASE = Path(__file__).resolve().parent
ROOT = CASE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import garden_example
import garden_runtime


def files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob('*') if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((CASE / 'inputs.json').read_text())
    for item in manifest['files']:
        actual = hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest()
        if actual != item['sha256']:
            raise SystemExit('Pinned input changed: ' + item['path'])
    scenario = json.loads((CASE / 'scenario.json').read_text())
    if scenario['question_snapshot'] != json.loads((CASE / 'question-snapshot.json').read_text()):
        raise SystemExit('Question snapshot mismatch')
    evidence = json.loads((CASE / 'evidence.json').read_text())
    func = next(c for c in scenario['commands'] if c['node'] == 'FUNC')
    if func['output']['evidence'] != evidence['events']:
        raise SystemExit('Scenario/ledger mismatch')
    follow = json.loads((CASE / 'follow-up-question.json').read_text())
    resid = next(c for c in scenario['commands'] if c['node'] == 'RESID')
    if resid['output']['specialist'] != follow:
        raise SystemExit('Follow-up/residual mismatch')
    with tempfile.TemporaryDirectory(prefix='cem-garden-') as temp:
        output = Path(temp) if args.check else CASE / 'worked'
        document = garden_example.build(ROOT, scenario, output)
        garden_runtime.replay(document)
        state = document['state']
        if state['used'] != {'steps': 10, 'branches': 1, 'model_calls': 0}:
            raise SystemExit('Unexpected run usage')
        branch = state['branches']['B0']
        if branch['status'] != 'resting' or state['route_decisions']:
            raise SystemExit('Case must rest without routing')
        if [c['node'] for c in scenario['commands']] != garden_runtime.NODES:
            raise SystemExit('Ten-node sequence mismatch')
        if args.check and files(output) != files(CASE / 'worked'):
            raise SystemExit('Saved outputs differ from replay; inspect before rebuilding')
    print('PASS: pinned inputs; ledger/residual consistency; 10 nodes; 1 resting branch; '
          '0 model calls; exact saved-output replay' if args.check else 'Rebuilt case outputs')


if __name__ == '__main__':
    main()
