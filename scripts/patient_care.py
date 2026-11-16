#!/usr/bin/env python3
"""Typed care milestones over shared records; offline supplied replay, no diagnosis.

Checks establish consistency with reviewed records, never their empirical truth.
A new record may change a later assessment; previous journal entries are retained.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import continuity as shared
import cycle
import garden_runtime as garden
import garden_tree
import safeguards as sg

ROOT = Path(__file__).resolve().parents[1]
OPS = Path('operations/medical-access/20261113')
SCHEMA = Path('schemas/patient-care.schema.json')
JOURNAL, REFERENCES = OPS / 'journal.json', OPS / 'references.json'
TREE = Path('config/garden-trees/medical-access.json')
OUTPUT = Path('reports/medical-access/20261113/generated')
require, Error = shared.require, shared.ContinuityError


def read(root, path):
    return shared.strict_json(Path(root) / path)


def unique(values, description):
    require(len(set(values)) == len(values), 'Duplicate ' + description)


def validate(pathway, schema, resolved):
    shared.shape(pathway, schema)
    cutoff = shared.day(pathway['evidence_cutoff'])
    require(cutoff is not None, 'Evidence cutoff requires a day date')
    unique(pathway['event_refs'], 'pathway event')
    sources = {}
    for alias, item in resolved.items():
        if item['binding']['kind'] == 'source':
            sid = item['record']['source_id']
            require(sid not in sources or sources[sid] == item['record'], 'Ambiguous source ID')
            sources[sid] = item['record']
    events = {}
    for ref in pathway['event_refs']:
        require(ref in resolved and resolved[ref]['binding']['kind'] == 'event', 'Unknown event reference')
        event = resolved[ref]['record']
        require(event.get('record_mode') == pathway['record_mode'], 'Synthetic/public mode mismatch')
        date = shared.day(event.get('event_date'))
        require(date is not None and date <= cutoff, 'Event date absent or after cutoff')
        require(event.get('result') in {'observed', 'not_performed', 'pending', 'contested'}, 'Unknown event result')
        require(isinstance(event.get('usable_effect'), bool), 'Effect flag must be explicit')
        if event['usable_effect']:
            require(event['result'] == 'observed' and event['observation_type'] in {
                'route_corrected', 'accommodation_implemented', 'clinical_benefit', 'remedy_realized'},
                'A policy, request or booking cannot establish a patient-usable effect')
        ids = event.get('source_ids', [])
        require(isinstance(ids, list) and ids, 'Event requires source lineage')
        unique(ids, 'event source')
        for sid in ids:
            require(sid in sources, 'Event source missing')
            source = sources[sid]
            allowed = source.get('permitted_observation_types', [])
            require(event['observation_type'] in allowed and event['event_id'] in source.get('asserted_event_ids', []),
                    'Event type exceeds its source record or lineage')
            require(shared.day(source.get('publication_date')) is not None
                    and shared.day(source['publication_date']) <= cutoff, 'Source publication after cutoff or absent')
            if pathway['record_mode'] == 'synthetic_demonstration':
                require(source.get('source_kind') == 'synthetic_record', 'Fictional pathway needs fictional sources')
            else:
                require(source.get('source_kind') in {'public_action_record', 'formal_policy'}, 'Invalid public source kind')
                if source['source_kind'] == 'formal_policy':
                    require(set(allowed) <= {'formal_protection'}, 'Formal policy cannot establish action or effect')
        if event['observation_type'] == 'coordinator_authorized':
            require(event.get('scope') == 'scheduling_and_record_routing_only', 'Coordinator scope must remain explicit')
        if event['observation_type'] == 'treatment_consent':
            require(event.get('scope') == 'treatment_decision', 'Treatment consent needs separate scope')
        events[ref] = event

    ids = []
    for stage in pathway['stages']:
        ids.append(stage['stage_id'])
        refs = stage['event_refs']
        unique(refs, 'stage event')
        require(all(ref in events for ref in refs), 'Stage event outside pathway scope')
        matching = [events[ref] for ref in refs]
        require(all(event['observation_type'] == stage['observation_type']
                    and event['service_type'] == stage['service_type'] for event in matching),
                'Stage needs its own observation and service type; adjacent milestones do not substitute')
        results = {event['result'] for event in matching}
        required = {'completed': {'observed'}, 'failed': {'not_performed'},
                    'pending': {'pending'}, 'contested': {'contested'}}
        if stage['status'] != 'unknown':
            require(bool(results & required[stage['status']]) or
                    (stage['status'] == 'contested' and {'observed', 'not_performed'} <= results),
                    'Status needs explicit matching evidence; absence is UNKNOWN')
        if stage['status'] in {'completed', 'failed'}:
            require('contested' not in results and not {'observed', 'not_performed'} <= results,
                    'Conflicting results require contested assessment')
        for ref in stage['claimed_policy_refs']:
            require(ref in resolved and resolved[ref]['binding']['kind'] == 'source'
                    and 'formal_protection' in resolved[ref]['record'].get('permitted_observation_types', [])
                    and any(resolved[ref]['record']['source_id'] in event['source_ids']
                            and event['observation_type'] == 'formal_protection' for event in events.values()),
                    'Claimed policy needs a scoped formal record')
        cost = stage['patient_cost']
        unique(cost['event_refs'], 'cost event')
        require(all(ref in events for ref in cost['event_refs']), 'Cost event outside pathway scope')
        if cost['type'] in {'unknown', 'not_stated'}:
            require(cost['amount'] is None and cost['currency'] is None, 'Unknown cost cannot supply amount/currency')
        else:
            expected = {key: cost[key] for key in ('type', 'amount', 'currency')}
            require(bool(cost['event_refs']) and all(events[ref]['cost'] == expected
                    and events[ref]['service_type'] == stage['service_type']
                    and events[ref]['result'] == 'observed' for ref in cost['event_refs']),
                    'Cost/coverage needs same-service evidence; optional fee does not govern other care')
        effect = stage['patient_usable_effect']
        unique(effect['event_refs'], 'effect event')
        require(all(ref in refs for ref in effect['event_refs']), 'Effect needs stage-specific evidence')
        if effect['status'] == 'observed':
            require(stage['status'] == 'completed' and bool(effect['event_refs'])
                    and all(events[ref]['usable_effect'] for ref in effect['event_refs']),
                    'Patient-usable effect needs a separate supported observation')
    unique(ids, 'stage ID')
    return events


def make_entry(pathway, *, sequence, recorded_at, actor, reason, expected_revision, previous):
    entry = {'sequence': sequence, 'recorded_at': recorded_at, 'actor': actor, 'reason': reason,
             'expected_revision': expected_revision, 'previous_entry_sha256': previous,
             'pathway': copy.deepcopy(pathway)}
    return {**entry, 'entry_sha256': cycle.digest(entry)}


def replay(root=ROOT, *, journal=None, manifest=None, schema=None):
    journal = read(root, JOURNAL) if journal is None else journal
    manifest = read(root, REFERENCES) if manifest is None else manifest
    schema = read(root, SCHEMA) if schema is None else schema
    require(set(journal) == {'version', 'schema_sha256', 'references_sha256', 'entries'}
            and journal['version'] == 'patient-care-journal-1', 'Invalid pathway journal')
    require(journal['schema_sha256'] == cycle.digest(schema), 'Schema snapshot changed')
    require(journal['references_sha256'] == cycle.digest(manifest), 'References snapshot changed')
    resolved = sg.resolve(root, manifest)
    require(isinstance(journal['entries'], list) and journal['entries'], 'Journal needs entries')
    latest, revisions, history = {}, {}, []
    previous, prior_time = shared.ZERO, None
    for sequence, entry in enumerate(journal['entries'], 1):
        require(set(entry) == {'sequence', 'recorded_at', 'actor', 'reason', 'expected_revision',
                              'previous_entry_sha256', 'pathway', 'entry_sha256'}, 'Invalid journal entry')
        require(type(entry['sequence']) is int and entry['sequence'] == sequence, 'Sequence mismatch')
        require(entry['previous_entry_sha256'] == previous, 'Broken history chain')
        require(entry['entry_sha256'] == cycle.digest({k: v for k, v in entry.items() if k != 'entry_sha256'}), 'Entry modified')
        require(all(isinstance(entry[k], str) and entry[k].strip() for k in ('recorded_at', 'actor', 'reason')), 'Entry needs attribution/date/reason')
        try:
            stamp = datetime.fromisoformat(entry['recorded_at'].replace('Z', '+00:00'))
        except ValueError as exc:
            raise Error('Invalid journal timestamp') from exc
        require(stamp.tzinfo is not None and (prior_time is None or stamp >= prior_time), 'Journal chronology reversed or timezone absent')
        record = entry['pathway']
        validate(record, schema, resolved)
        require(stamp.date() >= shared.day(record['evidence_cutoff']), 'Assessment predates its cutoff')
        pid = record['pathway_id']
        require(type(entry['expected_revision']) is int and entry['expected_revision'] == revisions.get(pid, 0), 'Stale pathway revision')
        old = latest.get(pid)
        if old:
            require(all(old[k] == record[k] for k in ('record_mode', 'clinical_question')), 'Changed pathway scope requires a new ID')
            require(record['evidence_cutoff'] >= old['evidence_cutoff'], 'Cutoff cannot move backwards')
            require(set(old['event_refs']) <= set(record['event_refs']), 'Retain earlier event references')
            require(all(item in record['contrary_evidence'] for item in old['contrary_evidence']), 'Retain contrary evidence')
            new_stages = {s['stage_id']: s for s in record['stages']}
            for stage in old['stages']:
                require(stage['stage_id'] in new_stages, 'Retain earlier stage identities')
                new = new_stages[stage['stage_id']]
                require(all(new[k] == stage[k] for k in ('observation_type', 'service_type', 'phase')), 'Changed stage meaning requires a new stage ID')
                if any(new[k] != stage[k] for k in ('status', 'patient_cost', 'patient_usable_effect')):
                    require(set(new['event_refs']) - set(stage['event_refs']) or
                            record['contrary_evidence'] != old['contrary_evidence'], 'Changed assessment needs new evidence or explicit counterassessment')
        latest[pid] = copy.deepcopy(record)
        revisions[pid] = revisions.get(pid, 0) + 1
        history.append({'sequence': sequence, 'pathway_id': pid, 'revision': revisions[pid],
                        'recorded_at': entry['recorded_at'], 'actor': entry['actor'], 'reason': entry['reason'],
                        'evidence_cutoff': record['evidence_cutoff'], 'entry_sha256': entry['entry_sha256'],
                        'stages': {s['stage_id']: s['status'] for s in record['stages']}})
        previous, prior_time = entry['entry_sha256'], stamp
    families = {}
    for pid, record in latest.items():
        source_ids = {sid for ref in record['event_refs'] for sid in resolved[ref]['record']['source_ids']}
        families[pid] = sorted({sg.lineage(ref, resolved) for ref, item in resolved.items()
                               if item['binding']['kind'] == 'source' and item['record']['source_id'] in source_ids})
    return {'version': 'patient-care-state-1', 'status': 'supplied assessment; no canonical admission',
            'pathways': latest, 'revisions': revisions, 'history': history,
            'source_families': families, 'history_head': previous}, resolved


def markdown(state):
    lines = ['# Patient Care Continuity', '', '**FICTIONAL DEMONSTRATION. No patient or provider outcome is established.**', '',
             'A booked appointment is an administrative milestone. Attendance, clinical assessment, treatment and benefit require their own records.', '']
    for pid, record in state['pathways'].items():
        lines += ['## ' + record['title'], '', record['clinical_question'], '',
                  '| Milestone | Initial revision | Latest revision | Service | Evidence |',
                  '| --- | --- | --- | --- | --- |']
        first = next(h['stages'] for h in state['history'] if h['pathway_id'] == pid)
        for stage in record['stages']:
            lines.append('| ' + ' | '.join([stage['observation_type'].replace('_', ' '),
                first.get(stage['stage_id'], 'not yet assessed'), stage['status'], stage['service_type'],
                ', '.join(stage['event_refs']) or 'none']) + ' |')
        lines += ['', 'Event dates and source bindings are retained in the [shared records](../../../../operations/medical-access/20261113/records.json) and '
                  '[append-only journal](../../../../operations/medical-access/20261113/journal.json).', '',
                  '**Source families:** ' + ', '.join(state['source_families'][pid]) + '. Reuse is not independent corroboration.', '',
                  '## What remains unknown', ''] + ['- ' + x for x in record['unknowns']]
        lines += ['', '## Ordinary explanations and contrary evidence', ''] + ['- ' + x for x in record['ordinary_explanations'] + record['contrary_evidence']]
        lines += ['', '**One proposed next test:** ' + record['next_test']['question'], '',
                  record['next_test']['stop_condition'], '',
                  'Clinical uncertainty is distinct from documented access failure. These supplied records do not decide causation, negligence, coverage for other services or treatment consent.', '']
    return '\n'.join(lines)


def scenario(root, state, resolved):
    require(len(state['pathways']) == 1, 'This saved pass is bounded to one pathway')
    record = next(iter(state['pathways'].values()))
    core = (SCHEMA, JOURNAL, REFERENCES, OPS / 'records.json', TREE,
            Path('config/garden-traversal.json'), Path('operations/continuity/references.json'))
    pins = {str(p): hashlib.sha256((Path(root) / p).read_bytes()).hexdigest() for p in core}
    source_ids = {sid for ref in record['event_refs'] for sid in resolved[ref]['record']['source_ids']}
    refs = sorted(ref for ref, item in resolved.items() if item['binding']['kind'] == 'source' and item['record']['source_id'] in source_ids)
    actor = {'name': 'Work Aiden', 'runtime': 'Supplied fictional demonstration; offline replay',
             'model': 'No provider/model dispatch'}
    arrival = {'id': 'MEDICAL-FICTIONAL-INTAKE', 'from': str(JOURNAL), 'to': 'MEDICAL-ACCESS:ROOT-0001',
               'payload': {'kind': 'synthetic_demonstration', 'pathway_id': record['pathway_id'], 'input_sha256': pins}}
    outputs = [
        ('ROOT', {'name': record['title']}),
        ('ARRIVAL', {'arrival': arrival, 'language_glance': {'languages': ['English'], 'basis': 'participant_supplied',
            'issuing_office': 'Fictional fixture author', 'surface_kind': 'mixed', 'source_refs': refs,
            'note': 'Fictional records, not medical records or empirical policy observations.'}}),
        ('EPIST', {'prompt': record['clinical_question'], 'evidence_cutoff': record['evidence_cutoff'],
                   'starting_state': 'No clinical outcome is presumed.'}),
        ('FUNC', {'task': 'Separate administrative milestones, clinical action and benefit.',
                  'function': 'Project typed assessments over retained shared records without inferring clinical causation.',
                  'pathways': state['pathways'], 'assessment_history': state['history']}),
        ('MIRROR', {'comparisons': [{'explanation': x, 'queries': [], 'answers': []} for x in record['ordinary_explanations']],
                    'contrary_evidence': record['contrary_evidence'], 'information_lineage': {
                        'parent_answer_visible': True, 'source_refs': refs, 'parent_output_refs': [str(JOURNAL)],
                        'criteria_refs': [str(SCHEMA)], 'api_record_refs': [], 'test_origin': 'separately_specified'}}),
        ('CROSS', {'inherited': [{'ref': r, 'status': 'One fictional source family; no independent corroboration'} for r in refs],
                   'independent': [], 'bridge': [{'question': record['next_test']['question'], 'status': 'proposed_only'}]}),
        ('RESID', {'summary': ' '.join(record['unknowns']), 'next_test': record['next_test'],
                   'predicates': {'consequential': True, 'distinct_functions': False, 'language_exception': None}}),
        ('MEAN', {'summary': 'Preserve a working administrative correction without inventing usable clinical care or harm.'}),
        ('EXIT', {'kind': 'question', 'summary': record['next_test']['question']}),
        ('RETURN', {'new_arrival': None, 'reason': record['next_test']['stop_condition']}),
    ]
    return {'schema_version': 'garden-scenario-1', 'recorded_at': '2026-11-15T20:00:00Z',
            'recorded_at_meaning': 'Fixed supplied replay timestamp; not a real patient event or live observation.',
            'record_base_url': 'https://github.com/Jaradyne/Dis-Unity/blob/main/' + str(OUTPUT / 'garden') + '/',
            'question_snapshot': {'questions': {'Q-MEDICAL-CARE-CONTINUITY': {'epoch': 1, 'status': 'staged_question_not_live_registration'}}},
            'start': {'run_id': 'MEDICAL-ACCESS-FICTIONAL-20261115', 'question_id': 'Q-MEDICAL-CARE-CONTINUITY', 'epoch': 1,
                'actor': actor, 'tree': 'MEDICAL-ACCESS', 'focus': record['clinical_question'],
                'status': 'Supplied fictional demonstration; no live registry admission', 'arrival': arrival,
                'sources': [{'ref': ref, 'lineage_id': sg.lineage(ref, resolved), 'kind': 'design_input',
                             'binding': resolved[ref]['binding']} for ref in refs],
                'budget': {'max_steps': 10, 'max_branches': 1, 'max_events': 10, 'max_fanout': 0, 'model_calls': 0}},
            'commands': [{'event_id': 'MEDICAL-STEP-' + str(i + 1), 'expected_revision': i, 'actor': actor,
                          'branch_id': 'B0', 'kind': 'step', 'node': node, 'output': output}
                         for i, (node, output) in enumerate(outputs)]}


def build(root=ROOT, *, write=False):
    root = Path(root)
    state, resolved = replay(root)
    supplied = scenario(root, state, resolved)
    inputs = {'version': 'patient-care-inputs-1', 'sha256': supplied['start']['arrival']['payload']['input_sha256'],
              'scenario_sha256': hashlib.sha256(cycle.encoded(supplied)).hexdigest()}
    files = {OPS / 'scenario.json': cycle.encoded(supplied), OPS / 'inputs.json': cycle.encoded(inputs),
             OUTPUT / 'PATIENT_CARE.json': cycle.encoded(state), OUTPUT / 'PATIENT_CARE.md': markdown(state).encode()}
    if write:
        for path, content in files.items():
            cycle.write_bytes(root / path, content, replace=True)
        garden_tree.build(root, supplied, root / OUTPUT / 'garden', tree_extension=read(root, TREE))
    for path, content in files.items():
        require((root / path).read_bytes() == content, 'Saved replay drift: ' + str(path))
    saved = root / OUTPUT / 'garden'
    paths = {p.relative_to(saved) for p in saved.rglob('*') if p.is_file()}
    with tempfile.TemporaryDirectory() as temporary:
        documents = []
        for name in ('one', 'two'):
            folder = Path(temporary) / name
            document = garden_tree.build(root, supplied, folder, tree_extension=read(root, TREE))
            documents.append(document)
            require(garden.replay(copy.deepcopy(document)) == document, 'Garden replay differs')
            require(paths == {p.relative_to(folder) for p in folder.rglob('*') if p.is_file()}, 'Saved output set differs')
            require(all((folder / p).read_bytes() == (saved / p).read_bytes() for p in paths), 'Garden output bytes differ')
        require(documents[0] == documents[1], 'Repeated replay differs')
    document = documents[0]
    require(document['state']['used'] == {'steps': 10, 'branches': 1, 'model_calls': 0}
            and document['state']['branches']['B0']['status'] == 'resting', 'Unexpected execution')
    return {'status': 'passed', 'pathways': 1, 'revisions': len(state['history']), 'steps': 10,
            'branches': 1, 'provider_calls': 0, 'mode': 'synthetic_demonstration',
            'state_sha256': document['state_sha256'], 'canonical_admission': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['validate', 'replay', 'build', 'check'])
    args = parser.parse_args()
    if args.action in {'build', 'check'}:
        result = build(write=args.action == 'build')
    else:
        state, _ = replay()
        result = state if args.action == 'replay' else {'status': 'valid', 'revisions': state['revisions']}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
