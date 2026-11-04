"""Replay this bounded public review using existing Garden/Safeguard machinery.

The checks enforce recorded source classes and lineage, not legal eligibility or
source truth. --write rebuilds derived artifacts after an explicit reviewed edit.
There is no collection, provider dispatch, monitoring or evidence admission.
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
sys.path.insert(0, str(ROOT / 'scripts'))
import continuity as shared
import cycle
import garden_runtime as garden
import garden_tree
import safeguards as sg

PACKET = Path('reports/care-autonomy/20261104')
OPS = Path('operations/care-autonomy/20261104')
TREE = Path('config/care-autonomy-tree.json')
CASE = OPS / 'case.json'
MANIFEST = OPS / 'safeguard-references.json'
JOURNAL = OPS / 'safeguard-journal.json'
SCENARIO = OPS / 'scenario.json'
INPUTS = OPS / 'inputs.json'
SOURCES = PACKET / 'sources.json'
EVENTS = PACKET / 'events.json'
CORE_INPUTS = (CASE, MANIFEST, JOURNAL, TREE, SOURCES, EVENTS,
               Path('schemas/safeguard.schema.json'),
               Path('operations/continuity/references.json'),
               Path('config/garden-traversal.json'))
require = shared.require
SOURCE_CLASSES = {
    'campaign_statement': {'context', 'reported_concern'},
    'legal_authority': {'formal_text', 'context'},
    'official_guidance': {'formal_text', 'context', 'agency_response'},
    'implementation_report': {'implementation_observation', 'noncompliance_observation',
                              'reported_concern', 'agency_response', 'context'},
    'outcome_record': {'implementation_observation', 'effectiveness_observation',
                       'noncompliance_observation', 'context'},
    'election_reporting': {'context'},
}


def read(root, path):
    return shared.strict_json(Path(root) / path)


def validate_evidence_classes(record, schema, resolved):
    """A supplied type cannot override the type of the pinned supporting record."""
    sg.validate(record, schema, resolved)
    for evidence in record['evidence']:
        cited_ids = set()
        for citation in evidence['citations']:
            source = resolved[citation['source_ref']]['record']
            source_class = source.get('source_kind')
            allowed = source.get('permitted_evidence_kinds')
            require(source_class in SOURCE_CLASSES and isinstance(allowed, list)
                    and set(allowed) <= SOURCE_CLASSES[source_class],
                    'Unknown or overbroad source evidence class')
            require(evidence['kind'] in allowed,
                    'Evidence kind exceeds its reviewed source class')
            cited_ids.add(source['source_id'])
        for event_ref in evidence['event_refs']:
            event = resolved[event_ref]['record']
            require(bool(cited_ids & set(event.get('source_ids', []))),
                    'Evidence event and cited source have different lineage')
        if evidence['kind'] in sg.EMPIRICAL:
            require(bool(evidence['event_refs']),
                    'Empirical material needs a scoped event, not an announcement')


def load_review(root, *, journal=None, manifest=None):
    root = Path(root)
    schema = read(root, sg.SCHEMA)
    journal = read(root, JOURNAL) if journal is None else journal
    manifest = read(root, MANIFEST) if manifest is None else manifest
    state, resolved = sg.replay(root, journal=journal, manifest=manifest, schema=schema)
    for entry in journal['entries']:
        validate_evidence_classes(entry['safeguard'], schema, resolved)
    return state, resolved


def make_scenario(root, case, state, resolved):
    """Project supplied assessments; never infer a person's condition or eligibility."""
    require(case['version'] == 'care-autonomy-case-1', 'Unknown case version')
    require(case['question_id'] == 'Q-CA-CARE-AUTONOMY' and case['question_epoch'] == 1,
            'Use the staged bounded Question snapshot')
    require(case['status'] == 'supplied_public_baseline_not_individual_adjudication',
            'Do not present this baseline as an individual decision')
    require(set(case['safeguard_ids']) == set(state['safeguards']), 'Case safeguard scope differs')
    require(case['eligibility_decision'] == 'not_performed', 'No automated eligibility decision')
    require(case['origin'] == 'public_campaign_statements_and_current_legal_baseline',
            'Preserve the campaign/baseline scope')
    require(case['next_test']['max_records'] == 1
            and case['next_test']['status'] == 'proposed_only', 'Keep one bounded proposed test')
    require(all(record['next_test'] == case['next_test'] for record in state['safeguards'].values()),
            'Safeguards must retain the shared single next test')
    pins = {str(p): hashlib.sha256((Path(root) / p).read_bytes()).hexdigest() for p in CORE_INPUTS}
    refs = sorted({ref for record in state['safeguards'].values() for ref in sg.source_refs(record)})
    actor = {'name': 'Work Aiden', 'runtime': 'Supplied active-session review; offline replay',
             'model': 'Work-session model identifier not recorded'}
    arrival = {'id': 'CARE-AUTONOMY-INTAKE-20261104', 'from': str(JOURNAL),
               'to': 'CARE-AUTONOMY:ROOT-0001',
               'payload': {'kind': 'reviewed_public_baseline', 'case_id': case['case_id'],
                           'input_sha256': pins}}
    sources = [{'ref': ref, 'lineage_id': sg.lineage(ref, resolved), 'kind': 'public_source',
                'binding': resolved[ref]['binding']} for ref in refs]
    start = {'run_id': 'CARE-AUTONOMY-BASELINE-20261104', 'question_id': case['question_id'],
             'epoch': case['question_epoch'], 'actor': actor, 'tree': 'CARE-AUTONOMY',
             'focus': case['scope'], 'status': 'Supplied baseline; no live registry admission',
             'arrival': arrival, 'sources': sources,
             'budget': {'max_steps': 10, 'max_branches': 1, 'max_events': 10,
                        'max_fanout': 0, 'model_calls': 0}}
    outputs = [
        ('ROOT', {'name': case['title']}),
        ('ARRIVAL', {'arrival': arrival, 'language_glance': {'languages': ['English'],
            'basis': 'participant_supplied', 'issuing_office': 'See retained public sources',
            'surface_kind': 'mixed', 'source_refs': refs,
            'note': 'Inspected text and access limits are source metadata, not raw HTTP receipts.'}}),
        ('EPIST', {'prompt': case['question'], 'starting_state': case['starting_state'],
                  'evidence_cutoff': case['evidence_cutoff'],
                  'eligibility_decision': case['eligibility_decision']}),
        ('FUNC', {'task': case['scope'],
                  'function': 'Separate proposals, authority, implementation and protective outcomes.',
                  'safeguards': state['safeguards'], 'assessment_history': state['history'],
                  'offer_review_fields': case['offer_review_fields'],
                  'relay_questions': case['relay_questions']}),
        ('MIRROR', {'comparisons': [{'explanation': item, 'queries': [], 'answers': []}
                                  for item in case['ordinary_explanations']],
                    'contrary_evidence': case['contrary_evidence'],
                    'information_lineage': {'parent_answer_visible': True, 'source_refs': refs,
                        'parent_output_refs': [str(CASE), str(JOURNAL)],
                        'criteria_refs': [str(sg.SCHEMA)], 'api_record_refs': [],
                        'test_origin': 'separately_specified'}}),
        ('CROSS', {'inherited': [{'ref': ref,
                    'status': 'Shared source; reuse is not independent corroboration'} for ref in refs],
                   'independent': [], 'bridge': [{'question': case['next_test']['question'],
                                                   'status': 'proposed_only'}]}),
        ('RESID', {'summary': ' '.join(case['residuals']), 'next_test': case['next_test'],
                   'predicates': {'consequential': True, 'distinct_functions': False,
                                  'language_exception': None}}),
        ('MEAN', {'summary': case['meaning'],
                  'dimensions': {sid: sg.dimensions(record)
                                 for sid, record in state['safeguards'].items()}}),
        ('EXIT', {'kind': 'question', 'summary': case['next_test']['question']}),
        ('RETURN', {'new_arrival': None, 'reason': case['stop_condition']}),
    ]
    return {'schema_version': 'garden-scenario-1', 'recorded_at': case['recorded_at'],
            'recorded_at_meaning': 'Supplied review timestamp; no independent observation or provider call',
            'record_base_url': 'https://github.com/Jaradyne/Dis-Unity/blob/main/' + str(PACKET / 'worked') + '/',
            'question_snapshot': {'questions': {case['question_id']: {
                'epoch': case['question_epoch'], 'status': 'staged_question_not_live_registration'}}},
            'start': start,
            'commands': [{'event_id': 'CARE-AUTONOMY-STEP-' + str(i + 1),
                'expected_revision': i, 'actor': actor, 'branch_id': 'B0',
                'kind': 'step', 'node': node, 'output': output}
                for i, (node, output) in enumerate(outputs)]}


def markdown(case, state):
    lines = ['# Care, Consent and State Power', '', case['question'], '',
             'Supplied public baseline. No individual diagnosis or eligibility determination. '
             'Formal protection is not proof that a person was protected.', '',
             '| Safeguard | Formal | People / procedures / authority | Effectiveness | Failure |',
             '| --- | --- | --- | --- | --- |']
    for record in state['safeguards'].values():
        dims = sg.dimensions(record)
        lines.append('| ' + ' | '.join([record['title'], dims['formal'],
            ' / '.join(dims['operational'][k] for k in ('people', 'procedures', 'authority')),
            dims['effectiveness'], dims['failure']]) + ' |')
    lines += ['', '## Questions about an actual offer', '']
    lines += ['- ' + x for x in case['offer_review_fields']]
    lines += ['', 'These fields are questions for a consent-respecting public-record review; '
              'they are not a diagnosis, eligibility score or resident surveillance form.', '',
              '## Where knowledge stops', '']
    lines += ['- ' + x for x in case['residuals']]
    lines += ['', '**One next test:** ' + case['next_test']['question'], '',
              'Stop: ' + case['next_test']['stop_condition'], '',
              '[Source catalog](../sources.json) · [Event catalog](../events.json) · '
              '[Readable context and handoff](../README.md)', '']
    return '\n'.join(lines)


def build(root=ROOT, *, write=False):
    root = Path(root)
    state, resolved = load_review(root)
    case = read(root, CASE)
    scenario = make_scenario(root, case, state, resolved)
    inputs = {'version': 'care-autonomy-inputs-1',
              'sha256': scenario['start']['arrival']['payload']['input_sha256'],
              'scenario_sha256': hashlib.sha256(cycle.encoded(scenario)).hexdigest()}
    generated = {'SAFEGUARDS.json': cycle.encoded(state),
                 'CARE_AUTONOMY.md': markdown(case, state).encode('utf-8')}
    if write:
        cycle.write_json(root / SCENARIO, scenario, replace=True)
        cycle.write_json(root / INPUTS, inputs, replace=True)
        garden_tree.build(root, scenario, root / PACKET / 'worked', tree_extension=read(root, TREE))
        for name, content in generated.items():
            cycle.write_bytes(root / PACKET / 'generated' / name, content, replace=True)
    require(read(root, INPUTS) == inputs, 'Pinned inputs differ; review changed inputs before rebuilding')
    require(read(root, SCENARIO) == scenario, 'Saved scenario differs from reviewed source and assessment lineage')
    for name, content in generated.items():
        require((root / PACKET / 'generated' / name).read_bytes() == content,
                'Generated assessment differs: ' + name)
    saved = root / PACKET / 'worked'
    paths = {p.relative_to(saved) for p in saved.rglob('*') if p.is_file()}
    with tempfile.TemporaryDirectory() as temporary:
        first = garden_tree.build(root, scenario, Path(temporary) / 'one', tree_extension=read(root, TREE))
        second = garden_tree.build(root, scenario, Path(temporary) / 'two', tree_extension=read(root, TREE))
        require(first == second == garden.replay(copy.deepcopy(first)), 'Replay differs')
        for name in ('one', 'two'):
            folder = Path(temporary) / name
            require(paths == {p.relative_to(folder) for p in folder.rglob('*') if p.is_file()},
                    'Saved output set differs')
            for path in paths:
                require((saved / path).read_bytes() == (folder / path).read_bytes(),
                        'Saved replay output differs: ' + str(path))
    require(first['state']['used'] == {'steps': 10, 'branches': 1, 'model_calls': 0}
            and first['state']['branches']['B0']['status'] == 'resting', 'Unexpected execution')
    return {'status': 'passed', 'run_id': first['state']['run_id'],
            'state_sha256': first['state_sha256'], 'safeguards': len(state['safeguards']),
            'steps': 10, 'branches': 1, 'provider_calls': 0,
            'canonical_admission': False, 'individual_eligibility_decision': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Rebuild derived artifacts after reviewed input edits')
    args = parser.parse_args()
    print(json.dumps(build(write=args.write), indent=2))
