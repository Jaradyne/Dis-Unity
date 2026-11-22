#!/usr/bin/env python3
"""A typed reconsideration lens over Patient Care Continuity; supplied/offline only."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import tempfile

import continuity as shared
import cycle
import garden_runtime as garden
import garden_tree
import patient_care as care
import safeguards as safeguards

ROOT = Path(__file__).resolve().parents[1]
OPS = Path('operations/clinical-reconsideration/20261121')
OUTPUT = Path('reports/clinical-reconsideration/20261121/generated')
SCHEMA = Path('schemas/clinical-reconsideration.schema.json')
TREE = Path('config/garden-trees/clinical-reconsideration.json')
JOURNAL, REFERENCES = OPS / 'journal.json', OPS / 'references.json'
require, Error, read = shared.require, shared.ContinuityError, care.read
ASSESSMENT_KINDS = {
    'second_review': 'opinion', 'clinical_error': 'clinical_error_review',
    'harm_causation': 'causation_review', 'correction_authored': 'correction_authored',
    'correction_dispatched': 'correction_dispatch', 'correction_received': 'correction_receipt',
    'downstream_change': 'downstream_change', 'clinical_benefit': 'benefit_observation',
}
OBSERVATIONS = {
    'opinion': {'diagnostic_evaluation'}, 'patient_report': {'need_recorded'},
    'primary_record': {'need_recorded', 'prerequisite_performed'},
    'clinical_error_review': {'diagnostic_evaluation'}, 'causation_review': {'diagnostic_evaluation'},
    'independence_record': {'diagnostic_evaluation'}, 'correction_authored': {'route_corrected'},
    'correction_dispatch': {'referral_dispatched'}, 'correction_receipt': {'referral_received'},
    'downstream_change': {'treatment_selected'}, 'benefit_observation': {'clinical_benefit'},
    'policy': {'formal_protection'}, 'access_record': {'need_recorded', 'referral_dispatched',
        'referral_received', 'medical_authorization', 'appointment_booked',
        'appointment_attended', 'diagnostic_evaluation'},
}


def combined_schema(root=ROOT, lens_schema=None):
    """Compose, never replace or mutate the historically pinned care schema."""
    schema = copy.deepcopy(read(root, care.SCHEMA))
    lens_schema = read(root, SCHEMA) if lens_schema is None else lens_schema
    schema['$id'] = lens_schema['$id'] + '?sha256=' + cycle.digest(lens_schema)
    schema['properties']['reconsideration'] = lens_schema['properties']['assessment']
    schema['required'].append('reconsideration')
    return schema


def validate_lens(pathway, resolved, lens_schema):
    lens = pathway['reconsideration']
    shared.shape(lens, lens_schema['properties']['assessment'])
    events = {ref: resolved[ref]['record'] for ref in pathway['event_refs']}
    details = {}
    sources = {x['record']['source_id']: x['record'] for x in resolved.values()
               if x['binding']['kind'] == 'source'}
    for ref, event in events.items():
        detail = event.get('reconsideration')
        shared.shape(detail, lens_schema['properties']['record'])
        kind = detail['kind']
        require(event['observation_type'] in OBSERVATIONS[kind], 'Record kind and care milestone differ')
        require(all(kind in sources[sid].get('permitted_reconsideration_kinds', [])
                    for sid in event['source_ids']), 'Record kind exceeds its source scope')
        if kind != 'access_record':
            require(event['result'] in {'observed', 'contested'}, 'A substantive record needs an explicit result')
        details[ref] = detail

    def refs(values, description, kind=None):
        care.unique(values, description)
        require(all(ref in events for ref in values), description + ' outside case scope')
        if kind:
            require(all(details[ref]['kind'] == kind for ref in values), description + ' needs its own evidence kind')

    def earlier(values, target, description):
        refs(values, description)
        require(all(events[ref]['event_date'] <= events[target]['event_date'] for ref in values),
                description + ' uses future evidence')
        require(target not in values, description + ' cannot cite itself')

    initial = lens['initial_opinion_ref']
    refs([initial], 'Initial opinion', 'opinion')
    require(details[initial]['review_kind'] == 'initial', 'Initial opinion cannot be replaced by a later review')
    refs(lens['opinion_refs'], 'Opinion reference', 'opinion')
    require(initial in lens['opinion_refs'], 'Retain the initial opinion')
    refs(lens['reported_harm_refs'], 'Reported harm', 'patient_report')
    require(set(lens['opinion_refs']) == {r for r, d in details.items() if d['kind'] == 'opinion'},
            'Expose every opinion in the case')
    require(set(lens['reported_harm_refs']) == {r for r, d in details.items() if d['kind'] == 'patient_report'},
            'Expose every attributed harm report')
    for ref, detail in details.items():
        kind = detail['kind']
        if kind == 'patient_report':
            earlier([detail['alleged_origin_ref']], ref, 'Reported relationship')
        elif kind == 'opinion':
            earlier(detail['evidence_considered'], ref, 'Opinion basis')
            require(bool(detail['evidence_considered']), 'Opinion must retain its stated evidence basis')
            if detail['review_kind'] == 'initial':
                require(ref == initial and detail['prior_opinion_ref'] is None
                        and detail['conclusion'] in {'provisional', 'definitive', 'unspecified'},
                        'Invalid initial opinion relationship')
            else:
                require(detail['prior_opinion_ref'] == initial, 'Reconsideration must retain its original opinion')
                earlier([initial], ref, 'Prior opinion')
                require(detail['conclusion'] in {'agrees', 'revises', 'inconclusive'}, 'Invalid review conclusion')
        elif kind in {'clinical_error_review', 'causation_review'}:
            require(detail['target_opinion_ref'] in lens['opinion_refs'], 'Review target must be a retained opinion')
            earlier([detail['target_opinion_ref']] + detail['basis_refs'], ref, 'Error/causation review basis')
            require(bool(detail['basis_refs']), 'Error/causation needs a scoped review basis')
            if kind == 'causation_review':
                refs([detail['harm_report_ref']], 'Causal claim harm target', 'patient_report')
                earlier([detail['harm_report_ref']], ref, 'Causal claim harm target')
                require(events[detail['target_opinion_ref']]['event_date'] <=
                        events[detail['harm_report_ref']]['event_date'],
                        'Causal target cannot postdate the report of existing harm')
        elif kind == 'independence_record':
            refs([detail['opinion_ref']], 'Independence target', 'opinion')
        elif kind == 'correction_authored':
            earlier([detail['target_record_ref']], ref, 'Correction target')
        elif kind in {'correction_dispatch', 'correction_receipt', 'downstream_change'}:
            refs([detail['correction_ref']], 'Correction relay', 'correction_authored')
            earlier([detail['correction_ref']], ref, 'Correction relay')
        elif kind == 'benefit_observation':
            earlier(detail['basis_refs'], ref, 'Benefit basis')
            require(bool(detail['basis_refs']) and event_effect(events[ref]),
                    'Benefit needs its own observed usable result')
    independence = {item['opinion_ref']: item for item in lens['opinion_independence']}
    require(len(independence) == len(lens['opinion_independence'])
            and set(independence) == set(lens['opinion_refs']),
            'Independence assessments must match each retained opinion exactly once')
    for opinion, assessment in independence.items():
        evidence = assessment['evidence_refs']
        refs(evidence, 'Independence basis', 'independence_record')
        applicable = {r for r, d in details.items()
                      if d['kind'] == 'independence_record' and d['opinion_ref'] == opinion}
        require(set(evidence) == applicable, 'Independence basis must expose all scoped records')
        require(all(details[r]['reviewer_role'] == details[opinion]['author_role'] for r in evidence),
                'Independence basis must identify the actual reviewer role')
        if assessment['status'] == 'unknown':
            continue
        require(bool(evidence), 'Independence basis is missing')
        conclusions = {details[r]['conclusion'] for r in evidence}
        results = {events[r]['result'] for r in evidence}
        if assessment['status'] == 'documented':
            require(conclusions == {'affirmed'} and results == {'observed'},
                    'An affirmative independence basis is required; different clinician or date is insufficient')
        else:
            require('contested' in results or 'contested' in conclusions or
                    {'affirmed', 'rejected'} <= conclusions,
                    'Contested independence basis needs explicit contrary evidence')

    for name, assessment in lens['assessments'].items():
        evidence = assessment['evidence_refs']
        refs(evidence, name, ASSESSMENT_KINDS[name])
        if name == 'second_review':
            require(all(details[r]['review_kind'] == 'reconsideration' for r in evidence),
                    'An initial opinion is not a second review')
        applicable = {r for r, d in details.items() if d['kind'] == ASSESSMENT_KINDS[name]
                      and (name != 'second_review' or d['review_kind'] == 'reconsideration')}
        require(set(evidence) == applicable,
                name + ' must expose all scoped records, including contrary evidence')
        if assessment['status'] == 'unknown':
            continue
        require(bool(evidence), name + ' cannot be established by missing evidence')
        results = {events[r]['result'] for r in evidence}
        require(results <= {'observed', 'contested'}, 'Invalid assessment result')
        if assessment['status'] == 'contested':
            conclusions = {details[r].get('conclusion') for r in evidence}
            require('contested' in results or
                    (name in {'clinical_error', 'harm_causation'} and
                     ('contested' in conclusions or {'affirmed', 'rejected'} <= conclusions)),
                    'Contested assessment needs explicit contrary evidence')
        else:
            require(results == {'observed'}, 'Contested records cannot become a documented conclusion')
            if name not in {'clinical_error', 'harm_causation'}:
                require(all(any(s['status'] == 'completed' and r in s['event_refs']
                                for s in pathway['stages']) for r in evidence),
                        'Documented reconsideration milestone needs its completed same-event care stage')
            if name in {'clinical_error', 'harm_causation'}:
                require(all(details[r]['conclusion'] == 'affirmed' for r in evidence),
                        'Review existence or an inconclusive/rejected proposition is not an affirmed finding')
            if name in {'correction_dispatched', 'correction_received'}:
                require(all(details[r]['recipient_role'] == lens['correction_recipient_role']
                            and details[r]['correction_ref'] in lens['assessments']['correction_authored']['evidence_refs']
                            for r in evidence), 'Correction receipt/dispatch needs the intended recipient and specific addendum')
            if name == 'second_review':
                require(all(any(details[b]['kind'] == 'primary_record'
                                for b in details[r]['evidence_considered']) for r in evidence),
                        'Repeated opinions alone do not establish reconsideration of primary evidence')
    return details


def event_effect(event):
    return event['usable_effect'] is True and event['result'] == 'observed'


def replay(root=ROOT, *, journal=None, manifest=None, lens_schema=None):
    journal = read(root, JOURNAL) if journal is None else journal
    manifest = read(root, REFERENCES) if manifest is None else manifest
    lens_schema = read(root, SCHEMA) if lens_schema is None else lens_schema
    schema = combined_schema(root, lens_schema)
    state, resolved = care.replay(root, journal=journal, manifest=manifest, schema=schema)
    prior = {}
    for entry in journal['entries']:
        pathway = entry['pathway']
        validate_lens(pathway, resolved, lens_schema)
        lens, pid = pathway['reconsideration'], pathway['pathway_id']
        if pid in prior:
            old = prior[pid]
            require(lens['initial_opinion_ref'] == old['initial_opinion_ref'], 'Retain initial opinion identity')
            require(lens['correction_recipient_role'] == old['correction_recipient_role'],
                    'Changed correction recipient requires a new pathway scope')
            for key in ('opinion_refs', 'reported_harm_refs'):
                require(set(old[key]) <= set(lens[key]), 'Retain earlier opinions and harm reports')
            old_independence = {a['opinion_ref']: a for a in old['opinion_independence']}
            for assessment in lens['opinion_independence']:
                previous = old_independence.get(assessment['opinion_ref'])
                if previous:
                    require(set(previous['evidence_refs']) <= set(assessment['evidence_refs']),
                            'Retain earlier independence evidence')
                    if assessment['status'] != previous['status']:
                        require(set(assessment['evidence_refs']) - set(previous['evidence_refs']),
                                'Changed independence status needs new scoped evidence')
            for key, assessment in lens['assessments'].items():
                previous = old['assessments'][key]
                require(set(previous['evidence_refs']) <= set(assessment['evidence_refs']),
                        'Retain earlier assessment evidence')
                if previous['status'] != assessment['status']:
                    require(set(assessment['evidence_refs']) - set(previous['evidence_refs']),
                            'Changed reconsideration status needs new scoped evidence')
        prior[pid] = copy.deepcopy(lens)
    state['version'] = 'clinical-reconsideration-state-1'
    state['reconsideration_history'] = [
        {'sequence': e['sequence'], 'recorded_at': e['recorded_at'],
         'pathway_id': e['pathway']['pathway_id'], 'assessment': e['pathway']['reconsideration']}
        for e in journal['entries']]
    return state, resolved


def markdown(state, resolved):
    lines = ['# Clinical Reconsideration and Second Opinions', '',
             '**FICTIONAL DEMONSTRATION. These are invented records, not a patient case or provider finding.**', '',
             'Reported psychological harm is retained as an attributed experience. Clinical error, causal responsibility, independent review and benefit require separate evidence.', '']
    for pid, pathway in state['pathways'].items():
        lens = pathway['reconsideration']
        first = next(h['stages'] for h in state['history'] if h['pathway_id'] == pid)
        lines += ['## Care and correction path', '', 'Completed means the named step has a record; a recorded harm report is not resolved distress, and policy text is not operational access.', '', '| Milestone | First revision | Latest revision | Evidence |',
                  '| --- | --- | --- | --- |']
        lines += ['| ' + ' | '.join([s['claim'], first.get(s['stage_id'], 'not yet assessed'),
                    s['status'], ', '.join(s['event_refs']) or 'none']) + ' |' for s in pathway['stages']]
        lines += ['', '## Separate judgments', '', '| Judgment | Status | Scope and limitation |', '| --- | --- | --- |']
        lines += ['| ' + ' | '.join([k.replace('_', ' '), a['status'], a['scope']]) + ' |'
                  for k, a in lens['assessments'].items()]
        lines += ['', '## Reports and opinions retained', '']
        for ref in lens['reported_harm_refs']:
            d = resolved[ref]['record']['reconsideration']
            lines.append('- ' + ref + ': ' + d['attribution'] + ' reports: ' + d['statement'] +
                         ' Alleged relationship is attributed; causation is not established by this report.')
        independence = {a['opinion_ref']: a for a in lens['opinion_independence']}
        for ref in lens['opinion_refs']:
            event = resolved[ref]['record']; d = event['reconsideration']
            lines.append('- ' + ref + ' (' + event['event_date'] + '): ' + d['author_role'] + '; ' +
                         d['conclusion'] + '. ' + d['reasoning'] + ' Evidence considered: ' +
                         ', '.join(d['evidence_considered']) + '. Independence: ' + independence[ref]['status'] +
                         '; ' + independence[ref]['limitation'])
        lines += ['', '**Source families:** ' + ', '.join(state['source_families'][pid]) +
                  '. Repeated or copied records do not create independent corroboration.', '',
                  '## Contrary evidence, ordinary explanations and unknowns', '']
        lines += ['- ' + s for s in pathway['contrary_evidence'] + pathway['ordinary_explanations'] + pathway['unknowns']]
        lines += ['', '**One bounded next test:** ' + pathway['next_test']['question'], '',
                  pathway['next_test']['stop_condition'], '',
                  'This program validates the supplied record relationships; it does not diagnose, adjudicate negligence, decide consent, or verify the truth of a source.', '']
    return '\n'.join(lines)


def scenario(root, state, resolved):
    require(len(state['pathways']) == 1, 'The saved pass is bounded to one pathway')
    pathway = next(iter(state['pathways'].values()))
    core = (SCHEMA, care.SCHEMA, JOURNAL, REFERENCES, OPS / 'records.json', TREE,
            Path('config/garden-traversal.json'), Path('operations/continuity/references.json'))
    pins = {str(p): hashlib.sha256((Path(root) / p).read_bytes()).hexdigest() for p in core}
    source_ids = {sid for ref in pathway['event_refs'] for sid in resolved[ref]['record']['source_ids']}
    refs = sorted(r for r, item in resolved.items() if item['binding']['kind'] == 'source'
                  and item['record']['source_id'] in source_ids)
    actor = {'name': 'Work Aiden / reconsideration_runtime', 'runtime': 'Supplied fictional demonstration; offline replay',
             'model': 'No provider/model dispatch'}
    arrival = {'id': 'RECONSIDERATION-FICTIONAL-INTAKE', 'from': str(JOURNAL),
        'to': 'CLINICAL-RECONSIDERATION:ROOT-0001', 'payload': {'kind': 'synthetic_demonstration', 'input_sha256': pins}}
    outputs = [
        ('ROOT', {'name': pathway['title']}),
        ('ARRIVAL', {'arrival': arrival, 'language_glance': {'languages': ['English'], 'basis': 'participant_supplied',
            'issuing_office': 'Fictional fixture author', 'surface_kind': 'mixed', 'source_refs': refs,
            'note': 'Invented records; no private health records or empirical provider finding.'}}),
        ('EPIST', {'prompt': pathway['clinical_question'], 'evidence_cutoff': pathway['evidence_cutoff'],
                   'starting_state': 'Reported harm remains visible; error and causation are not presumed.'}),
        ('FUNC', {'task': 'Separate access, actual reconsideration, correction relay and benefit.',
                  'function': 'Apply a typed lens to the existing care history.', 'pathways': state['pathways'],
                  'assessment_history': state['reconsideration_history']}),
        ('MIRROR', {'comparisons': [{'explanation': x, 'queries': [], 'answers': []} for x in pathway['ordinary_explanations']],
            'contrary_evidence': pathway['contrary_evidence'], 'information_lineage': {'parent_answer_visible': True,
             'source_refs': refs, 'parent_output_refs': [str(JOURNAL)], 'criteria_refs': [str(SCHEMA), str(care.SCHEMA)],
             'api_record_refs': [], 'test_origin': 'separately_specified'}}),
        ('CROSS', {'inherited': [{'ref': r, 'status': 'One fictional family; no independent corroboration'} for r in refs],
            'independent': [], 'bridge': [{'question': pathway['next_test']['question'], 'status': 'proposed_only'}]}),
        ('RESID', {'summary': ' '.join(pathway['unknowns']), 'next_test': pathway['next_test'],
            'predicates': {'consequential': True, 'distinct_functions': False, 'language_exception': None}}),
        ('MEAN', {'summary': 'A reasoned second opinion can agree. Record correction and dispatch do not establish receipt, clinical error, causal responsibility or benefit.'}),
        ('EXIT', {'kind': 'question', 'summary': pathway['next_test']['question']}),
        ('RETURN', {'new_arrival': None, 'reason': pathway['next_test']['stop_condition']}),
    ]
    return {'schema_version': 'garden-scenario-1', 'recorded_at': '2026-11-21T20:00:00Z',
        'recorded_at_meaning': 'Fixed supplied replay timestamp, not a real patient event.',
        'record_base_url': 'https://github.com/Jaradyne/Dis-Unity/blob/main/' + str(OUTPUT / 'garden') + '/',
        'question_snapshot': {'questions': {'Q-CLINICAL-RECONSIDERATION': {'epoch': 1, 'status': 'staged_question_not_live_registration'}}},
        'start': {'run_id': 'CLINICAL-RECONSIDERATION-FICTIONAL-20261121', 'question_id': 'Q-CLINICAL-RECONSIDERATION',
            'epoch': 1, 'actor': actor, 'tree': 'CLINICAL-RECONSIDERATION', 'focus': pathway['clinical_question'],
            'status': 'Supplied fictional demonstration; no live registry admission', 'arrival': arrival,
            'sources': [{'ref': r, 'lineage_id': safeguards.lineage(r, resolved), 'kind': 'design_input',
                         'binding': resolved[r]['binding']} for r in refs],
            'budget': {'max_steps': 10, 'max_branches': 1, 'max_events': 10, 'max_fanout': 0, 'model_calls': 0}},
        'commands': [{'event_id': 'RECONSIDERATION-STEP-' + str(i + 1), 'expected_revision': i,
                      'actor': actor, 'branch_id': 'B0', 'kind': 'step', 'node': node, 'output': output}
                     for i, (node, output) in enumerate(outputs)]}


def build(root=ROOT, *, write=False):
    root = Path(root)
    state, resolved = replay(root)
    supplied = scenario(root, state, resolved)
    files = {OPS / 'scenario.json': cycle.encoded(supplied),
             OUTPUT / 'RECONSIDERATION.json': cycle.encoded(state),
             OUTPUT / 'RECONSIDERATION.md': markdown(state, resolved).encode()}
    if write:
        for path, content in files.items():
            cycle.write_bytes(root / path, content, replace=True)
        garden_tree.build(root, supplied, root / OUTPUT / 'garden', tree_extension=read(root, TREE))
    for path, content in files.items():
        require((root / path).read_bytes() == content, 'Saved replay drift: ' + str(path))
    saved = root / OUTPUT / 'garden'
    paths = {p.relative_to(saved) for p in saved.rglob('*') if p.is_file()}
    with tempfile.TemporaryDirectory() as temporary:
        for name in ('one', 'two'):
            target = Path(temporary) / name
            document = garden_tree.build(root, supplied, target, tree_extension=read(root, TREE))
            require(garden.replay(copy.deepcopy(document)) == document, 'Garden replay differs')
            require(paths == {p.relative_to(target) for p in target.rglob('*') if p.is_file()}, 'Saved output set differs')
            require(all((target / p).read_bytes() == (saved / p).read_bytes() for p in paths), 'Garden output bytes differ')
    require(document['state']['used'] == {'steps': 10, 'branches': 1, 'model_calls': 0}
            and document['state']['branches']['B0']['status'] == 'resting', 'Unexpected execution')
    return {'status': 'passed', 'pathways': 1, 'revisions': len(state['history']), 'steps': 10,
            'branches': 1, 'provider_calls': 0, 'mode': 'synthetic_demonstration',
            'state_sha256': document['state_sha256'], 'canonical_admission': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['validate', 'replay', 'build', 'check'])
    action = parser.parse_args().action
    if action in {'build', 'check'}:
        result = build(write=action == 'build')
    else:
        state, _ = replay()
        result = state if action == 'replay' else {'status': 'valid', 'revisions': state['revisions']}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
