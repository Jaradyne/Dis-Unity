"""Offline consistency checks for the bounded Information Integrity intake."""
import copy
import hashlib
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import continuity as shared
import cycle
import garden_tree
import garden_runtime as garden

PACKET = Path('reports/information-integrity/20261028')
CASE = Path('operations/information-integrity/20261028/case.json')
SCENARIO = Path('operations/information-integrity/20261028/scenario.json')
TREE = Path('config/information-integrity-tree.json')
AXES = {'messages', 'automation', 'coordination', 'operator_or_sponsor',
        'audience_exposure', 'protective_result', 'source_attribution'}
require = shared.require


def validate_case(case, sources):
    require(case['version'] == 'information-integrity-case-1', 'Unknown case format')
    require(set(case['observations']) == AXES, 'Preserve the separate evidence dimensions')
    catalog = {s['id']: s for s in sources['sources']}
    require(len(catalog) == len(sources['sources']), 'Duplicate source ID')
    for axis, observation in case['observations'].items():
        require(set(observation) == {'status', 'source_refs', 'note'}
                and isinstance(observation['note'], str) and observation['note'].strip(),
                'Every assessment needs a status, sources and explanation')
        status, refs = observation['status'], observation['source_refs']
        require(status in {'unknown', 'reported_unverified', 'source_reported', 'source_assessed'},
                'Unsupported status; no automatic verified finding')
        require(isinstance(refs, list) and all(isinstance(r, str) for r in refs)
                and len(set(refs)) == len(refs) and set(refs) <= set(catalog), 'Invalid sources')
        require((not refs) if status == 'unknown' else bool(refs),
                'Unknown has no supporting evidence; other assessments need attributed sources')
        for ref in refs:
            source = catalog[ref]
            require(case['case_id'] in source['scopes'] and axis in source['supports'],
                    'Background or different-axis evidence cannot establish this incident claim')
            expected = 'context' if status == 'reported_unverified' else 'public_source'
            require(source['kind'] == expected, 'Retain the difference between a lead and public evidence')
    require(set(case['background_refs']) <= set(catalog), 'Unknown background source')
    require(all(case['case_id'] not in catalog[r]['scopes'] for r in case['background_refs']),
            'Background must remain separate from incident evidence')


def verify(root=ROOT):
    root = Path(root)
    read = lambda p: shared.strict_json(root / p)
    pins = read(PACKET / 'inputs.json')['sha256']
    expected = {str(CASE), str(SCENARIO), str(TREE), str(PACKET / 'sources.json'),
                'config/garden-traversal.json'}
    require(set(pins) == expected, 'Input manifest must cover exact case inputs')
    for path, sha in pins.items():
        require(hashlib.sha256(shared.local_path(root, path).read_bytes()).hexdigest() == sha,
                'Pinned input changed: ' + path)
    case, sources, scenario = read(CASE), read(PACKET / 'sources.json'), read(SCENARIO)
    require(all(s['kind'] == 'public_source' for s in sources['sources']),
            'Public packet cannot include context or private intake sources')
    validate_case(case, sources)
    require(scenario['start']['arrival']['payload']['input_sha256'] ==
            {p: h for p, h in pins.items() if p != str(SCENARIO)}, 'Arrival lineage differs')
    refs = sources['sources']
    require(scenario['start']['sources'] == [
        {'ref': s['id'], 'lineage_id': s['lineage_id'], 'kind': s['kind'],
         'binding': {'path': str(PACKET / 'sources.json'), 'id': s['id']}, 'scope': s['scopes']}
        for s in refs], 'Source identity/lineage differs')
    func = next(c['output'] for c in scenario['commands'] if c['node'] == 'FUNC')
    for key in ('observations', 'safeguards', 'relay'):
        require(func[key] == case[key], 'Garden projection differs from retained case')
    saved = root / PACKET / 'worked'
    saved_paths = {p.relative_to(saved) for p in saved.rglob('*') if p.is_file()}
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        first = garden_tree.build(root, scenario, temp / 'one', tree_extension=read(TREE))
        second = garden_tree.build(root, scenario, temp / 'two', tree_extension=read(TREE))
        require(first == second == garden.replay(copy.deepcopy(first)), 'Replay differs')
        one_paths = {p.relative_to(temp / 'one') for p in (temp / 'one').rglob('*') if p.is_file()}
        two_paths = {p.relative_to(temp / 'two') for p in (temp / 'two').rglob('*') if p.is_file()}
        require(saved_paths == one_paths == two_paths, 'Saved output set differs')
        for path in saved_paths:
            require((saved / path).read_bytes() == (temp / 'one' / path).read_bytes()
                    == (temp / 'two' / path).read_bytes(), 'Saved replay output differs: ' + str(path))
    require(first['state']['used'] == {'steps': 10, 'branches': 1, 'model_calls': 0}
            and first['state']['branches']['B0']['status'] == 'resting', 'Unexpected execution')
    return {'status': 'pass', 'case_id': case['case_id'], 'state_sha256': first['state_sha256'],
            'steps': 10, 'branches': 1, 'provider_calls': 0,
            'case_status': 'historical_source_reported', 'independent_source_replication': False}


if __name__ == '__main__':
    import json
    print(json.dumps(verify(), indent=2))
