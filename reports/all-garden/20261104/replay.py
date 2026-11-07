"""Reconstruct RC-015's supplied, supervised passes with the existing reducer.

No network, provider dispatch, Question registration or evidence admission.
--write only regenerates this packet's derived scenarios and worked output.
Input pins are set separately after review; this command cannot refresh them.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
PACKET = Path('reports/all-garden/20261104')
sys.path.insert(0, str(ROOT / 'scripts'))
import cycle
import garden_runtime as garden
import garden_tree


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return cycle.read_json(ROOT / path)


def file_hash(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def load_inputs():
    manifest = read(PACKET / 'inputs.json')
    require(manifest['version'] == 'rc015-pinned-cycle-1', 'Unknown manifest')
    for path, expected in manifest['sha256'].items():
        require(file_hash(path) == expected, 'Input changed: ' + path)
    lanes = []
    for path in manifest['return_files']:
        packet = read(path)
        require(packet['version'] == 'all-garden-return-1'
                and packet['cycle_id'] == 'RC-015', 'Wrong return version/cycle')
        for lane in packet['lanes']:
            lane = copy.deepcopy(lane)
            lane['return_path'] = path
            lane['return_actor'] = packet['actor']
            lane['checked_at'] = packet['checked_at']
            lanes.append(lane)
    require(sorted(l['lane_id'] for l in lanes) == sorted(manifest['lane_ids']),
            'Missing, duplicate or unexpected lane')
    require(len({l['lane_id'] for l in lanes}) == len(lanes), 'Duplicate lane')
    for lane in lanes:
        require(lane['inspection_status'] in {'new_evidence', 'reconfirmed', 'inconclusive',
                'access_blocked', 'retained_only'}, 'Unknown inspection status')
        require(type(lane['epoch']) is int and lane['epoch'] >= 1, 'Invalid epoch')
        require(lane['baseline_refs'] and lane['findings'] and lane['next_test']
                and lane['stop_reason'], 'Missing scope or stop')
        sources = {s['source_id']: s for s in lane['sources']}
        require(len(sources) == len(lane['sources']), 'Duplicate source ID')
        for source in sources.values():
            require(source['source_family'] and source['access_mode']
                    and source['access_result'] and source['summary'], 'Missing source lineage')
            if source['access_mode'] != 'recorded_http':
                require(source['raw_receipt_path'] is None, 'Transformed text is not raw HTTP')
        for finding in lane['findings']:
            require(finding['epistemic_status'] in {'DOCUMENTED', 'UNKNOWN', 'HYPOTHESIS'}
                    and type(finding['is_new_event']) is bool, 'Invalid finding status')
            require(finding['evidence_refs'], 'Unreferenced finding')
            for ref in finding['evidence_refs']:
                if ref not in sources:
                    require(ref.split('#', 1)[0] in manifest['sha256'],
                            'Unpinned evidence reference: ' + ref)
    return manifest, lanes


def scenario_for(manifest, lane):
    actor = {'name': 'Work Aiden', 'runtime': 'Supervised RC-015 assembly and supplied interpretation',
             'model': 'Work-session model identifier not recorded'}
    source_refs = [s['source_id'] for s in lane['sources']]
    sources = [{'ref': s['source_id'], 'lineage_id': s['source_family'],
                'kind': 'context' if s['access_mode'] == 'retained_repository' else 'public_source',
                'binding': {'path': lane['return_path'], 'lane_id': lane['lane_id'],
                            'source_id': s['source_id'], 'sha256': cycle.digest(s)}}
               for s in lane['sources']]
    run_id = 'RC015-' + lane['lane_id'].upper()
    arrival = {'id': run_id + '-ARRIVAL', 'from': lane['return_path'],
               'to': lane['tree_id'] + ':ROOT-0001',
               'payload': {'lane_id': lane['lane_id'], 'return_actor': lane['return_actor'],
                           'return_sha256': manifest['sha256'][lane['return_path']],
                           'baseline_refs': lane['baseline_refs'],
                           'inspection_status': lane['inspection_status']}}
    start = {'run_id': run_id, 'question_id': lane['question_id'], 'epoch': lane['epoch'],
             'actor': actor, 'tree': lane['tree_id'], 'focus': lane['question'],
             'arrival': arrival, 'sources': sources,
             'budget': {'max_steps': 10, 'max_events': 10, 'max_branches': 1,
                        'max_fanout': 0, 'model_calls': 0}}
    outputs = [
        ('ROOT', {'name': lane['title']}),
        ('ARRIVAL', {'arrival': arrival, 'language_glance': {
            'languages': [], 'basis': 'unknown', 'surface_kind': 'mixed',
            'issuing_office': 'See each pinned source publisher', 'source_refs': source_refs,
            'note': 'No matched original/translation inventory supplied by these returns.'}}),
        ('EPIST', {'prompt': lane['question'],
                   'starting_state': 'Retain the dated baseline; inspect one bounded residual.',
                   'empirical_cutoff': manifest['empirical_cutoff'],
                   'inspection_time': lane['checked_at']}),
        ('FUNC', {'task': lane['question'], 'function': 'Inspect evidence, outcome and access separately.',
                  'findings': lane['findings'], 'research_actor': lane['return_actor'],
                  'inspection_status': lane['inspection_status']}),
        ('MIRROR', {'comparisons': [{'explanation': str(c), 'queries': [], 'answers': []}
                                  for c in lane['counterevidence']],
                    'working_buffers': lane['working_buffers'],
                    'information_lineage': {'parent_answer_visible': True,
                        'source_refs': source_refs, 'parent_output_refs': lane['baseline_refs'],
                        'criteria_refs': [str(PACKET / 'RETURN_CONTRACT.json')],
                        'api_record_refs': [], 'test_origin': 'inherited'}}),
        ('CROSS', {'inherited': [{'ref': ref} for ref in source_refs], 'independent': [],
                   'bridge': [{'question': lane['next_test'], 'status': 'proposed_only',
                               'source_refs': source_refs}]}),
        ('RESID', {'summary': ' '.join(str(x) for x in lane['unknowns']) or 'No additional claim.',
                   'predicates': {'consequential': True, 'distinct_functions': False,
                                  'language_exception': None}, 'next_test': lane['next_test']}),
        ('MEAN', {'summary': 'Read the attributed findings with their contrary evidence and residuals.',
                  'authorship_limits': lane['authorship_limits']}),
        ('EXIT', {'kind': 'question', 'summary': lane['next_test']}),
        ('RETURN', {'new_arrival': None, 'reason': lane['stop_reason']}),
    ]
    return {'schema_version': 'garden-scenario-1', 'recorded_at': manifest['assembled_at'],
            'recorded_at_meaning': 'Actual supervised assembly time, reused deterministically; '
                                   'not an origin fetch time or time of the historical events.',
            'record_base_url': 'https://github.com/Jaradyne/Dis-Unity/blob/main/' + str(PACKET / 'worked') + '/',
            'question_snapshot': {'questions': {lane['question_id']: {'epoch': lane['epoch']}}},
            'start': start, 'commands': [{'event_id': run_id + '-STEP-' + str(i + 1),
                'expected_revision': i, 'actor': actor, 'branch_id': 'B0', 'kind': 'step',
                'node': node, 'output': output} for i, (node, output) in enumerate(outputs)]}


def build_into(manifest, lanes, destination):
    results = []
    for lane in lanes:
        scenario = scenario_for(manifest, lane)
        config = garden.load_config(ROOT)
        if lane['tree_id'] in manifest['extensions']:
            config = garden_tree.load(ROOT, read(manifest['extensions'][lane['tree_id']]))
        doc = garden.new_document(config, scenario['start'], scenario['question_snapshot'])
        for command in scenario['commands']:
            doc = garden.apply_event(doc, command, scenario['recorded_at'])
        require(doc == garden.replay(copy.deepcopy(doc)), 'Reducer replay mismatch')
        require(doc['state']['used'] == {'steps': 10, 'branches': 1, 'model_calls': 0}
                and doc['state']['branches']['B0']['status'] == 'resting', 'Unexpected execution')
        cycle.write_json(destination / 'scenarios' / (lane['lane_id'] + '.json'), scenario, replace=True)
        cycle.write_json(garden.path_for(destination / 'worked', doc['state']['run_id']), doc, replace=True)
        results.append({'lane_id': lane['lane_id'], 'tree_id': lane['tree_id'],
                        'run_id': doc['state']['run_id'], 'state_sha256': doc['state_sha256'],
                        'inspection_status': lane['inspection_status'], 'used': doc['state']['used']})
    garden.project(destination / 'worked', record_base_url=scenario['record_base_url'])
    cycle.write_json(destination / 'RESULTS.json', {'cycle_id': 'RC-015', 'runs': results,
        'repository_model_calls': 0, 'canonical_admission': False, 'question_registration': False}, replace=True)


def artifact_bytes(folder):
    files = [folder / 'RESULTS.json']
    for child in ('scenarios', 'worked'):
        files.extend(p for p in (folder / child).rglob('*') if p.is_file())
    return {str(p.relative_to(folder)): p.read_bytes() for p in files}


def verify(write=False):
    manifest, lanes = load_inputs()
    trees = set(garden.load_config(ROOT)['trees']) | set(manifest['extensions'])
    require({l['tree_id'] for l in lanes} == trees, 'Registered tree coverage is incomplete')
    if write:
        build_into(manifest, lanes, ROOT / PACKET)
    expected = artifact_bytes(ROOT / PACKET)
    with tempfile.TemporaryDirectory() as tmp:
        for name in ('one', 'two'):
            folder = Path(tmp) / name
            build_into(manifest, lanes, folder)
            require(artifact_bytes(folder) == expected, 'Saved reconstruction differs: ' + name)
    return {'status': 'passed', 'lanes': len(lanes), 'trees': len(trees),
            'steps': 10 * len(lanes), 'repository_model_calls': 0,
            'reconstructions': 2, 'canonical_admission': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    print(json.dumps(verify(parser.parse_args().write), indent=2))
