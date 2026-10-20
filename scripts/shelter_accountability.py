#!/usr/bin/env python3
"""Replay one shelter-law baseline and fictional notice triage; no collection.

The existing Safeguard, Relay and Garden reducers own evidence validation/history.
This wing only composes them and screens explicitly fictional notice inputs.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

import continuity as shared
import cycle
import garden_runtime as garden
import relays
import safeguards

ROOT = Path(__file__).resolve().parents[1]
OPERATIONS = Path('operations/shelter-accountability')
SCHEMA = Path('schemas/shelter-notice-rehearsal.schema.json')
FIXTURES = Path('examples/shelter-accountability/notice-rehearsals.json')
OUTPUT = Path('reports/shelter-accountability/generated')
PINNED = {str(p) for p in (SCHEMA, FIXTURES, OPERATIONS/'wing.json',
    OPERATIONS/'safeguard-journal.json', OPERATIONS/'safeguard-references.json',
    OPERATIONS/'relay-journal.json', OPERATIONS/'relay-references.json',
    Path('reports/shelter-accountability/sources.json'),
    Path('reports/shelter-accountability/events.json'), Path('config/garden-traversal.json'))}
require = shared.require
Error = shared.ContinuityError


def notice_screen(packet, schema=None):
    """Calendar triage of a fictional packet, never a legal determination."""
    shared.shape(packet, shared.strict_json(ROOT/SCHEMA) if schema is None else schema)
    require(packet['case_id'].startswith('SIM-') and
            all(r.startswith('FICT-') for r in packet['record_refs']),
            'Use explicitly fictional case and record identifiers')
    dates = [packet['notice'][k] for k in ('delivered_on', 'proposed_exit_on')]
    require(all(d is None or shared.day(d) is not None for d in dates), 'Invalid notice day date')
    start, end = [shared.day(d) for d in dates]
    require(not (start and end) or end >= start, 'Proposed exit precedes notice delivery')
    days = (end-start).days if start and end else None
    flags = []
    version = shared.day(packet['legal_version'])
    if version is None or any(d and d < version for d in (start, end)):
        flags.append('legal_version_review_required')
    scope = set(packet['scope'].values())
    if 'excluded' in scope:
        flags.append('other_framework_review_required')
    elif 'unknown' in scope:
        flags.append('coverage_unknown')
    if packet['permanent_conversion'] != 'no':
        flags.append('conversion_review_required')
    if days is None or packet['notice']['service_basis'] == 'unknown':
        flags.append('date_unknown')
    exceptions = [packet['exceptions'][k] for k in ('direct_threat', 'self_exit', 'short_extension')]
    if 'asserted' in exceptions:
        flags.append('exception_evidence_review_required')
    elif 'unknown' in exceptions:
        flags.append('exception_unknown')
    # This is a flag for review, not a decision about legal time computation.
    status = flags[0] if flags else ('short_interval_review_required' if days < 30 else 'no_interval_flag')
    if days is not None and days < 30:
        flags.append('calendar_interval_under_30_days')
    if packet['exceptions']['exigent_paperwork'] != 'not_asserted':
        flags.append('exigent_paperwork_review_does_not_waive_notice')
    gaps = sorted(k for k,v in packet['content'].items() if v == 'absent')
    unknowns = sorted(k for k,v in packet['content'].items() if v == 'unknown')
    if gaps:
        flags.append('notice_content_review_required')
    if unknowns:
        flags.append('notice_content_unknown')
    return {'case_id': packet['case_id'], 'mode': 'simulated', 'status': status,
        'calendar_interval_days': days, 'review_flags': flags,
        'content_gaps': gaps, 'content_unknowns': unknowns, 'record_refs': list(packet['record_refs']),
        'legal_finding': 'not_determined', 'fraud_finding': 'not_assessed', 'protective_outcome': 'unknown',
        'limits': 'Fictional triage only. Calendar subtraction is not a legal service/counting decision. '
                  'Scope fields do not establish all non-tenancy conditions, including Housing First. '
                  'No interval flag does not mean compliance, a valid exception, non-tenancy or protection. '
                  'Other rights and the applicable legal version require separate review.'}


def review_time(value):
    require(isinstance(value,str) and 'T' in value, 'Review needs an exact aware timestamp')
    return relays.bounds(value)[0]


def replay(root=ROOT):
    root = Path(root)
    pins = shared.strict_json(root/OPERATIONS/'inputs.json')
    require(set(pins) == {'version', 'sha256'} and pins['version'] == 'shelter-inputs-1' and
            set(pins['sha256']) == PINNED, 'Invalid shelter input pins')
    for path, expected in pins['sha256'].items():
        require(hashlib.sha256(shared.local_path(root,path).read_bytes()).hexdigest() == expected,
                'Pinned shelter input changed: '+path)
    wing = shared.strict_json(root/OPERATIONS/'wing.json')
    require(wing['version'] == 'shelter-wing-1' and wing['tree'] == 'HOMELESSNESS' and
            wing['status'] == 'supplied_baseline_no_collectors', 'Unexpected wing scope or activation')
    require(shared.day(wing['evidence_cutoff']) is not None, 'Invalid wing cutoff')
    require(relays.bounds(wing['evidence_cutoff'])[0] <= review_time(wing['recorded_at']),
            'Wing review precedes evidence cutoff')
    sg, sg_refs = safeguards.replay(root,
        journal=shared.strict_json(root/OPERATIONS/'safeguard-journal.json'),
        manifest=shared.strict_json(root/OPERATIONS/'safeguard-references.json'))
    relay, resolved = relays.replay(root,
        journal=shared.strict_json(root/OPERATIONS/'relay-journal.json'),
        manifest=shared.strict_json(root/OPERATIONS/'relay-references.json'))
    require(all(resolved[k] == v for k,v in sg_refs.items()), 'Shared shelter reference differs')
    require(set(sg['safeguards']) == {'SG-CA-SHELTER-NOTICE'} and
            set(relay['cases']) == {'CA-SHELTER-BASELINE'}, 'Keep this pass to one baseline')
    require(all(r['evidence_cutoff'] == wing['evidence_cutoff'] for r in
                [*sg['safeguards'].values(), *relay['cases'].values()]), 'Wing cutoff mismatch')
    fixtures = shared.strict_json(root/FIXTURES)
    require(set(fixtures) == {'version', 'mode', 'cases'} and
            fixtures['version'] == 'shelter-rehearsals-1' and fixtures['mode'] == 'simulated',
            'Fictional rehearsal envelope required')
    schema = shared.strict_json(root/SCHEMA)
    rehearsals = [notice_screen(c, schema) for c in fixtures['cases']]
    require(rehearsals and len({c['case_id'] for c in rehearsals}) == len(rehearsals),
            'Rehearsals need unique case identifiers')
    return {'version': 'shelter-state-1', 'wing': wing, 'input_pins': pins,
            'safeguards': sg, 'relays': relay, 'rehearsals': rehearsals}, resolved


def garden_pass(root, state, resolved):
    wing = state['wing']
    sg = state['safeguards']['safeguards']['SG-CA-SHELTER-NOTICE']
    case = state['relays']['cases']['CA-SHELTER-BASELINE']
    refs = sorted(k for k,v in resolved.items() if v['binding']['kind'] == 'source' and
                  v['binding']['path'] == 'reports/shelter-accountability/sources.json')
    sources = [{'ref': r, 'lineage_id': safeguards.lineage(r,resolved), 'kind': 'public_source',
                'binding': resolved[r]['binding'], 'access_limit': resolved[r]['record']['limitations']} for r in refs]
    actor = {'name': 'Work Aiden', 'runtime': 'deterministic supplied shelter projection', 'model': 'none invoked'}
    arrival = {'id': 'CA-SHELTER-ARRIVAL', 'from': str(OPERATIONS), 'to': 'HOMELESSNESS:ROOT-0001',
        'payload': {'wing_id': wing['wing_id'], 'input_pins_sha256': cycle.digest(state['input_pins']),
                    'safeguard_journal_sha256': state['safeguards']['journal_sha256'],
                    'relay_journal_sha256': state['relays']['journal_sha256'],
                    'scope': 'Formal baseline only; fictional notice rehearsals are separate, not practice evidence.'}}
    qid = wing['first_question_id']
    start = {'run_id': 'CA-SHELTER-BASELINE-GARDEN', 'question_id': qid, 'epoch': 1, 'actor': actor,
        'tree': wing['tree'], 'focus': wing['root_question'], 'arrival': arrival, 'sources': sources,
        'budget': {'max_steps':10, 'max_branches':1, 'max_events':10, 'max_fanout':0, 'model_calls':0},
        'status': 'case-local supplied legal baseline; no shared Question registration or practice finding'}
    nodes = [
        ('ROOT', {'name': wing['name']}),
        ('ARRIVAL', {'arrival': arrival, 'language_glance': {'languages': [], 'basis': 'unknown',
            'issuing_office': 'See shared legal sources and access limits', 'surface_kind': 'summary',
            'source_refs': refs, 'note': 'Supplied interpretation; no resident notice or accessible-language delivery observed.'}}),
        ('EPIST', {'prompt': wing['root_question'], 'starting_state': sg['scope'],
                   'dimensions': safeguards.dimensions(sg), 'legal_version': wing['legal_version']}),
        ('FUNC', {'task': 'Trace protection, responsibility and remedy separately.', 'function': sg['scope'],
                  'safeguard': sg, 'relays': case['relays'], 'wing_functions': wing['functions']}),
        ('MIRROR', {'comparisons': [{'explanation': i['claim'], 'queries': [],
                                   'answers': [{'evidence_ids': i['evidence_ids']}]} for i in sg['ordinary_explanations']],
                    'contrary_evidence': sg['contrary_evidence'],
                    'information_lineage': {'parent_answer_visible': True, 'source_refs': refs,
                        'parent_output_refs': [str(OPERATIONS/'safeguard-journal.json'), str(OPERATIONS/'relay-journal.json')],
                        'criteria_refs': [str(safeguards.SCHEMA), str(relays.SCHEMA)],
                        'api_record_refs': [], 'test_origin': 'inherited'}}),
        ('CROSS', {'inherited': [{'ref': r, 'status': 'Retained legal material; mirrored renditions share lineage.'} for r in refs],
                   'independent': [], 'bridge': [{'question': wing['next_test'], 'status': 'proposed only'}]}),
        ('RESID', {'summary': '; '.join(sg['residuals']),
                   'predicates': {'consequential': True, 'distinct_functions': False, 'language_exception': None}}),
        ('MEAN', {'summary': 'Formal safeguards documented with scope/access limits; actual enforcement and protection unknown.',
                  'dimensions': safeguards.dimensions(sg)}),
        ('EXIT', {'kind': 'question', 'summary': wing['next_test']}),
        ('RETURN', {'new_arrival': None, 'reason': wing['stop_condition']})]
    document = garden.new_document(garden.load_config(root), start, {'questions': {qid: {'epoch':1}}})
    stamp = max([wing['recorded_at']] + [h['recorded_at'] for k in ('safeguards','relays') for h in state[k]['history']],
                key=review_time)
    for i, (node, output) in enumerate(nodes):
        document = garden.apply_event(document, {'event_id': 'CA-SHELTER-STEP-'+str(i+1), 'expected_revision': i,
            'actor': actor, 'branch_id': 'B0', 'kind': 'step', 'node': node, 'output': output}, stamp)
    return garden.replay(document)


def markdown(state, resolved):
    wing = state['wing']
    sg = state['safeguards']['safeguards']['SG-CA-SHELTER-NOTICE']
    case = state['relays']['cases']['CA-SHELTER-BASELINE']
    esc = lambda value: str(value).replace('|', '\\|').replace('\n', ' ')
    label = lambda value: value.replace('_', ' ')
    lines = ['# '+wing['name'], '', '**One formal baseline; no particular shelter violation or financial misconduct established.**', '',
        'Evidence read: '+wing['evidence_cutoff']+' UTC. Older legal material first found in this pass is late discovery, not a new shelter event.', '',
        wing['root_question'], '', '## Protection and practice', '',
        '| Claim | Status | What is established |', '| --- | --- | --- |']
    assessments = [('Formal safeguard', sg['formal'])] + [('Operational '+k,v) for k,v in sg['operational'].items()] + [
        ('Observed effectiveness', sg['effectiveness']), ('Failure', sg['failure'])]
    for name, a in assessments:
        lines.append('| '+name+' | '+a['status'].upper()+' | '+esc(a['claim'])+' |')
    lines += ['', '## Where responsibility goes', '',
        'These are required flows, not observed incidents. Acknowledgment, decision, implementation and restored service require separate records.', '',
        '| Relay / responsible roles | Expected transfer | Dispatch / arrival / action / outcome / verification |',
        '| --- | --- | --- |']
    for r in case['relays']:
        lines.append('| '+esc(r['relay_id']+': '+r['from_actor']+' → '+r['to_actor'])+' | '+esc(r['payload']+'. '+r['stages']['expected_transfer']['claim'])+' | '+
            ' / '.join(r['stages'][s]['status'].upper() for s in ('dispatch','arrival','action','outcome','verification'))+' |')
    lines += ['', 'A referral is not verified intake; an instruction to readmit is not verified shelter access. No absolute deadline or missed deadline is asserted without an actual dated event.', '',
        '## Wing questions', '', '| Function | Question | Evidence needed |', '| --- | --- | --- |']
    for f in wing['functions']:
        lines.append('| '+f['id']+' | '+esc(f['question'])+' | '+esc('; '.join(f['evidence_needed']))+' |')
    lines += ['', '## Scope and exceptions', '',
        'The retained Civil Code §§1954.08–1954.091 text defines publicly funded/overseen programs, including other shelter sites as well as hotels/motels. '
        'Section 1954.09 conditions its stated non-tenancy treatment on all requirements, including Housing First; a funding/occupancy screen alone cannot establish that treatment. Existing rights remain preserved.', '',
        'Within that framework, ordinary written notice is at least 30 days before proposed termination, with reasons, accommodation and grievance information. '
        'Qualifying direct threat, statutory self-exit and amendment of an already-noticed short extension require their own evidence. '
        'An exigent situation can affect when termination paperwork is practicable; it does not itself authorize every shortened notice. '
        'The specified fallback is availability within 24 hours of the participant’s request. Conversion provisions require separate interpretation.', '',
        'The public administrator establishes the grievance process. Documented exit/intake efforts are required; a replacement bed is not guaranteed. '
        'The inspected text does not supply a universal automatic stay pending appeal. The 2026 version note is not the origin of 30-day protections; the official 2024 analysis already describes the rule.', '',
        '## Fictional boundary rehearsals', '',
        'Every row below is SIMULATED. These are software checks with invented records, not resident cases, a legal compliance checker or evidence of statewide practice.', '',
        '| Fictional input | Calendar days | Triage | Additional review flags |', '| --- | --- | --- | --- |']
    for r in state['rehearsals']:
        lines.append('| '+r['case_id']+' | '+str(r['calendar_interval_days'] if r['calendar_interval_days'] is not None else 'UNKNOWN')+' | '+
            label(r['status'])+' | '+esc('; '.join(label(f) for f in r['review_flags']))+' |')
    lines += ['', 'All rehearsals retain legal finding NOT DETERMINED, fraud NOT ASSESSED and protective outcome UNKNOWN. A 30-day interval alone does not prove compliance or protection.', '',
        '## Shared source lineage', '', '| Source / lineage | Retained source and access |', '| --- | --- |']
    for alias, item in sorted(resolved.items()):
        if item['binding']['kind'] != 'source' or item['binding']['path'] != 'reports/shelter-accountability/sources.json':
            continue
        s = item['record']
        lines.append('| '+alias+' / '+esc(safeguards.lineage(alias,resolved))+' | ['+esc(s['title'])+']('+s['url']+'). '+esc(s['limitations'])+' |')
    lines += ['', 'Mirror renditions and reused legal text are not independent empirical corroboration. Retained tool responses include their access limits; they are not raw origin-server HTTP receipts.', '',
        '## Residuals and one next test', '']+['- '+u for u in sg['residuals']]
    lines += ['', '**Proposed next test:** '+wing['next_test'], '',
        'No collector, provider call, recurring task, Bee, Governor action, complaint, FOIA submission or canonical evidence admission is activated.', '',
        'Reproduce offline: `python scripts/shelter_accountability.py check`. '
        'See [sources](../sources.json), [legal review](../LEGAL_REVIEW.md), '
        '[input pins](../../../operations/shelter-accountability/inputs.json), '
        '[Safeguard history](../../../operations/shelter-accountability/safeguard-journal.json), '
        '[Relay history](../../../operations/shelter-accountability/relay-journal.json) and [saved Garden pass](GARDEN.json).', '']
    return '\n'.join(lines)


def outputs(root=ROOT):
    state, resolved = replay(root)
    return {'STATE.json': cycle.encoded(state), 'GARDEN.json': cycle.encoded(garden_pass(root,state,resolved)),
            'NOTICE_REHEARSALS.json': cycle.encoded({'mode':'simulated', 'results':state['rehearsals']}),
            'SHELTER.md': markdown(state,resolved).encode()}


def build(root=ROOT, check=False):
    generated = outputs(root)
    for name, data in generated.items():
        path = Path(root)/OUTPUT/name
        if check:
            require(path.is_file() and path.read_bytes() == data, 'Saved shelter output differs: '+name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    return len(generated)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate','replay','build','check'])
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        if args.command in {'build','check'}:
            print(f'PASS: {build(args.root, args.command == "check")} shelter outputs; no collection/dispatch')
        else:
            state, _ = replay(args.root)
            print(f"PASS: one shelter baseline; {len(state['rehearsals'])} fictional rehearsals; {cycle.digest(state)}")
    except (Error, cycle.CycleError, ValueError, KeyError, TypeError, OSError) as exc:
        print('INVALID: '+str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
