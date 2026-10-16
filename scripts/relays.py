#!/usr/bin/env python3
"""Validate supplied relay assessments and replay them through Garden; offline only."""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, time, timezone
from decimal import Decimal
import hashlib
from pathlib import Path
import sys

import continuity as shared
import cycle
import garden_runtime as garden
import safeguards

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = Path('schemas/relay-case.schema.json')
REFERENCES = Path('operations/relays/references.json')
JOURNAL = Path('operations/relays/journal.json')
OUTPUT = Path('reports/relays/generated')
STAGES = ('origin', 'expected_transfer', 'dispatch', 'arrival', 'action', 'outcome', 'verification')
require, Error = shared.require, shared.ContinuityError
RULES = {
    'origin': {'observed': {'trigger_observation'}},
    'expected_transfer': {'documented': {'requirement'}, 'committed': {'commitment'},
                          'announced': {'announcement'}, 'inferred_expectation': {'omission_observation'}},
    'dispatch': {'announced': {'announcement'}, 'committed': {'commitment'},
                 'performed': {'dispatch_observation'}, 'not_performed': {'omission_observation'}},
    'arrival': {'acknowledged': {'acknowledgment'}, 'received': {'arrival_observation'},
                'partial': {'arrival_observation'}, 'not_received': {'omission_observation'}},
    'action': {'performed': {'action_observation'}, 'partial': {'action_observation'},
               'not_performed': {'omission_observation'}},
    'outcome': {s: {'outcome_observation'} for s in ('continued', 'recovered', 'failed', 'partial')},
    'verification': {s: {'outcome_observation'} for s in ('source_supported', 'contested')},
}


def compiled_schema(schema):
    """Expand only local acyclic $defs, then use the existing strict shape validator."""
    definitions = schema.get('$defs', {})
    def expand(value, stack=()):
        if isinstance(value, list):
            return [expand(v, stack) for v in value]
        if not isinstance(value, dict):
            return value
        if '$ref' in value:
            ref = value['$ref']
            require(set(value) == {'$ref'} and isinstance(ref, str) and ref.startswith('#/$defs/'), 'Only local schema refs')
            key = ref[len('#/$defs/'):]
            require(key in definitions and key not in stack, 'Missing or recursive schema ref')
            return expand(definitions[key], (*stack, key))
        return {k: expand(v, stack) for k, v in value.items() if k != '$defs'}
    return expand(schema)


def bounds(value):
    """Preserve month/day uncertainty; exact instants require a timezone."""
    if value is None:
        return None
    require(isinstance(value, str), 'Time must be ISO text or null')
    if 'T' in value:
        try:
            stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError as exc:
            raise Error('Invalid timestamp') from exc
        require(stamp.tzinfo is not None, 'Timestamp needs timezone')
        stamp = stamp.astimezone(timezone.utc)
        return stamp, stamp
    lo, hi = shared.date_bounds(value)
    return datetime.combine(lo, time.min, timezone.utc), datetime.combine(hi, time.max, timezone.utc)


def period(value, cutoff):
    lo, hi = bounds(value['start']), bounds(value['end'])
    require(not (lo and hi) or lo[0] <= hi[1], 'Definitely reversed period')
    require(all(not b or b[0] <= cutoff for b in (lo, hi)), 'Observation after cutoff')


def resolve(root, manifest):
    require(set(manifest) == {'version', 'base', 'references', 'documents'} and
            manifest['version'] == 'relay-references-1', 'Invalid relay references')
    base = manifest['base']
    require(set(base) == {'path', 'sha256'}, 'Invalid reference base')
    inherited = shared.strict_json(shared.local_path(root, base['path']))
    require(cycle.digest(inherited) == base['sha256'], 'Shared reference base changed')
    resolved = safeguards.resolve(root, inherited)
    extras = shared.resolve(root, {'version': 'continuity-references-1', 'references': manifest['references']})
    require(not set(extras) & set(resolved), 'Cannot shadow shared aliases')
    resolved.update(extras)
    require(isinstance(manifest['documents'], dict), 'Documents must be keyed objects')
    for key, binding in manifest['documents'].items():
        require(shared.re.fullmatch(r'[A-Z][A-Z0-9-]*', key) is not None, 'Invalid document alias')
        require(key not in resolved and set(binding) == {'path', 'sha256', 'kind', 'parent_source_ref'}, 'Invalid document alias')
        require(binding['kind'] in {'design', 'artifact'}, 'Invalid document kind')
        path = shared.local_path(root, binding['path'])
        require(hashlib.sha256(path.read_bytes()).hexdigest() == binding['sha256'], 'Pinned document changed')
        parent = binding['parent_source_ref']
        if binding['kind'] == 'artifact':
            require(parent in resolved and resolved[parent]['binding']['kind'] == 'source', 'Artifact needs source parent')
            source = resolved[parent]
            catalog_path = shared.local_path(root, source['binding']['path'])
            require(any(m['sha256'] == binding['sha256'] and
                        (catalog_path.parent / m['body']).resolve() == path
                        for m in source['record'].get('materials', [])), 'Artifact/source binding mismatch')
        else:
            require(parent is None, 'Design is not an empirical source')
        resolved[key] = {'binding': binding, 'record': {'source_family': 'design-input' if parent is None else safeguards.lineage(parent, resolved)}}
    return resolved


def cited(ids, evidence, label):
    require(len(set(ids)) == len(ids) and all(e in evidence for e in ids), 'Invalid evidence refs: '+label)
    return [evidence[e] for e in ids]


def timing(relay):
    deadline = relay['deadline']
    if deadline is None:
        return {'status': 'no_documented_deadline', 'lag_seconds': None}
    stage = relay['stages'][deadline['stage']]
    if stage['status'] not in {'received', 'performed'}:
        return {'status': 'unknown', 'lag_seconds': None}
    lo, hi = bounds(stage['time']['start']), bounds(stage['time']['end'])
    due = bounds(deadline['at'])
    if not lo or not hi:
        return {'status': 'unknown', 'lag_seconds': None}
    state = 'missed' if lo[0] > due[1] else 'met' if hi[1] <= due[0] else 'unknown'
    exact = lo[0] == lo[1] == hi[0] == hi[1] and due[0] == due[1]
    return {'status': state, 'lag_seconds': int((lo[0]-due[0]).total_seconds()) if exact else None}


def validate(case, schema, resolved):
    shared.shape(case, compiled_schema(schema), 'relay_case')
    cutoff = bounds(case['evidence_cutoff'])
    require(cutoff is not None and len(case['evidence_cutoff']) != 7, 'Cutoff needs day or instant')
    for ref in case['event_refs']:
        require(ref in resolved and resolved[ref]['binding']['kind'] == 'event', 'Unknown event')
        require((resolved[ref]['record'].get('mode') == 'simulated') == (case['mode'] == 'simulated'),
                'Empirical/simulation event crossing')
    for ref in case['design_refs']:
        require(ref in resolved and resolved[ref]['binding']['kind'] == 'design', 'Unknown design reference')
    relays = {}
    for relay in case['relays']:
        rid = relay['relay_id']
        require(rid not in relays, 'Duplicate relay')
        relays[rid] = relay
        evidence = {}
        for item in relay['evidence']:
            eid = item['evidence_id']
            require(eid not in evidence, 'Duplicate evidence ID')
            evidence[eid] = item
            period(item['observed'], cutoff[1])
            require(item['observed']['start'] or item['observed']['end'], 'Evidence observation date required')
            require(all(r in case['event_refs'] for r in item['event_refs']), 'Evidence event outside case scope')
            for citation in item['citations']:
                ref = citation['source_ref']
                require(ref in resolved and resolved[ref]['binding']['kind'] == 'source', 'Unknown source')
                simulated = resolved[ref]['record'].get('mode') == 'simulated'
                require(simulated == (case['mode'] == 'simulated'), 'Empirical/simulation source crossing')
        for stage_name in STAGES:
            assessment = relay['stages'][stage_name]
            period(assessment['time'], cutoff[1])
            items = cited(assessment['evidence_ids'], evidence, stage_name)
            status = assessment['status']
            require(status == 'unknown' or status in RULES[stage_name], 'Invalid stage/status combination')
            if status != 'unknown':
                negative = status in {'not_performed', 'not_received', 'failed', 'inferred_expectation'}
                polarity = {'positive', 'negative'} if status in {'partial', 'source_supported', 'contested'} else {'negative' if negative else 'positive'}
                require(any(e['kind'] in RULES[stage_name][status] and stage_name in e['stages'] and e['result'] in polarity for e in items),
                        stage_name+' needs stage-specific evidence; no automatic promotion')
            if stage_name == 'verification' and status != 'unknown':
                require(bool(assessment['method']), 'Verification method required')
                require(relay['stages']['outcome']['status'] != 'unknown', 'Cannot verify unknown outcome')
                outcome = relay['stages']['outcome']
                result = {'positive', 'negative'} if outcome['status'] == 'partial' else {'negative' if outcome['status'] == 'failed' else 'positive'}
                require(any(e['evidence_id'] in outcome['evidence_ids'] and e['kind'] == 'outcome_observation'
                            and {'outcome', 'verification'} <= set(e['stages']) and e['result'] in result for e in items),
                        'Verification must address the same outcome evidence')
        if relay['stages']['outcome']['status'] != 'unknown':
            require(relay['stages']['verification']['status'] != 'unknown', 'Outcome needs explicit verification assessment')
        deadline = relay['deadline']
        if deadline:
            require(bounds(deadline['at']) is not None, 'Deadline date required')
            items = cited(deadline['evidence_ids'], evidence, 'deadline')
            require(any(e['kind'] in {'requirement', 'commitment'} and deadline['stage'] in e['stages'] and e['result'] == 'positive' for e in items), 'Deadline needs applicable obligation/commitment, not announcement')
        for capacity in relay['capacities']:
            period(capacity['time'], cutoff[1])
            items = cited(capacity['evidence_ids'], evidence, 'capacity')
            if capacity['value'] is not None:
                require(Decimal(capacity['value']).is_finite() and Decimal(capacity['value']) >= 0, 'Invalid capacity')
                needed = {dict(observed='capacity_observation', required='requirement', committed='commitment', announced='announcement')[capacity['basis']]}
                require(any(e['kind'] in needed for e in items), 'Capacity needs matching evidence class')
        for issue in relay['issues']:
            items = cited(issue['evidence_ids'], evidence, 'issue')
            needed = {'capacity_observation'} if issue['kind'] == 'capacity_shortfall' else {'outcome_observation'} if issue['kind'] == 'outcome_failure' else {'timing_observation'} if issue['kind'] == 'delay' else {'omission_observation', 'arrival_observation', 'dispatch_observation'} if issue['kind'] in {'misdirection', 'degradation'} else {'omission_observation'}
            require(any(e['kind'] in needed and issue['stage'] in e['stages'] and e['result'] == 'negative' for e in items), 'Issue needs specific failure evidence; missing evidence is not failure')
            if issue['kind'] == 'capacity_shortfall' and relay['kind'] == 'physical':
                require(issue['mechanism'] == 'physical_resource', 'Physical resource shortfall is not communication failure')
            if issue['kind'] == 'non_transmission':
                require(issue['stage'] == 'dispatch' and relay['stages']['dispatch']['status'] == 'not_performed', 'Non-transmission needs documented dispatch omission')
        for group in ('contrary_evidence', 'ordinary_explanations'):
            for claim in relay[group]:
                cited(claim['evidence_ids'], evidence, group)
        causal = relay['causal_assessment']
        items = cited(causal['evidence_ids'], evidence, 'causation')
        if causal['status'] == 'supported':
            require(any(e['kind'] == 'causal_analysis' and e['result'] == 'positive' for e in items), 'Sequence is not causation')
    support_keys = set()
    for support in case['supports']:
        key = (support['kind'], support['relay_id'], support['supports_relay'])
        require(key not in support_keys, 'Duplicate support link')
        support_keys.add(key)
        require(support['relay_id'] in relays and support['supports_relay'] in relays and
                support['relay_id'] != support['supports_relay'], 'Invalid support link')
        donor = relays[support['relay_id']]['stages']
        if support['status'] == 'used':
            require(donor['action']['status'] == 'performed', 'Used buffer needs action evidence')
        if support['status'] == 'verified':
            require(donor['outcome']['status'] in {'continued', 'recovered'} and
                    donor['verification']['status'] == 'source_supported', 'Working buffer needs verified outcome')


def make_entry(case, *, sequence, recorded_at, actor, reason, expected_revision, previous):
    item = {'sequence': sequence, 'recorded_at': recorded_at, 'actor': actor, 'reason': reason,
            'expected_revision': expected_revision, 'previous_entry_sha256': previous, 'case': copy.deepcopy(case)}
    return {**item, 'entry_sha256': cycle.digest(item)}


def replay(root=ROOT, journal=None, manifest=None, schema=None):
    root = Path(root)
    journal = shared.strict_json(root/JOURNAL) if journal is None else journal
    manifest = shared.strict_json(root/REFERENCES) if manifest is None else manifest
    schema = shared.strict_json(root/SCHEMA) if schema is None else schema
    require(set(journal) == {'version', 'schema_sha256', 'references_sha256', 'entries'} and journal['version'] == 'relay-journal-1', 'Invalid journal')
    require(journal['schema_sha256'] == cycle.digest(schema) and journal['references_sha256'] == cycle.digest(manifest), 'Schema/reference snapshot mismatch')
    resolved = resolve(root, manifest)
    require(isinstance(journal['entries'], list) and journal['entries'], 'Journal needs entries')
    latest, revisions, history = {}, {}, []
    previous, prior_time = shared.ZERO, None
    for number, entry in enumerate(journal['entries'], 1):
        require(set(entry) == {'sequence', 'recorded_at', 'actor', 'reason', 'expected_revision', 'previous_entry_sha256', 'case', 'entry_sha256'}, 'Invalid entry')
        require(type(entry['sequence']) is int and entry['sequence'] == number, 'Sequence mismatch')
        require(entry['previous_entry_sha256'] == previous, 'Broken history chain')
        require(entry['entry_sha256'] == cycle.digest({k:v for k,v in entry.items() if k != 'entry_sha256'}), 'Entry modified')
        require(all(isinstance(entry[k], str) and entry[k].strip() for k in ('actor', 'reason', 'recorded_at')), 'Review attribution/reason/date required')
        require('T' in entry['recorded_at'], 'Recording needs exact aware timestamp')
        stamp = bounds(entry['recorded_at'])[0]
        require(prior_time is None or stamp >= prior_time, 'Recording time reversal')
        case = entry['case']
        validate(case, schema, resolved)
        require(bounds(case['evidence_cutoff'])[0] <= stamp, 'Review precedes evidence cutoff')
        for relay in case['relays']:
            for evidence in relay['evidence']:
                period(evidence['observed'], stamp)
            for assessment in relay['stages'].values():
                period(assessment['time'], stamp)
            for capacity in relay['capacities']:
                period(capacity['time'], stamp)
        cid = case['case_id']
        require(type(entry['expected_revision']) is int and entry['expected_revision'] == revisions.get(cid, 0), 'Stale case revision')
        old = latest.get(cid)
        if old:
            require(all(case[k] == old[k] for k in ('mode', 'scope')), 'Case mode/scope cannot change')
            require(bounds(case['evidence_cutoff'])[0] >= bounds(old['evidence_cutoff'])[0], 'Cutoff moved backwards')
            require(set(old['event_refs']) <= set(case['event_refs']), 'Historical events removed')
            require(set(old['design_refs']) <= set(case['design_refs']), 'Historical design references removed')
            support_key = lambda s: (s['kind'], s['relay_id'], s['supports_relay'])
            require({support_key(s) for s in old['supports']} <= {support_key(s) for s in case['supports']}, 'Historical support link removed')
            new_relays = {r['relay_id']: r for r in case['relays']}
            for before in old['relays']:
                after = new_relays.get(before['relay_id'])
                require(after is not None, 'Historical relay removed')
                require(all(before[k] == after[k] for k in ('kind', 'from_actor', 'to_actor', 'payload', 'essential_function', 'scope')), 'Relay identity changed')
                for group in ('evidence', 'contrary_evidence', 'ordinary_explanations', 'issues', 'capacities'):
                    require(after[group][:len(before[group])] == before[group], 'Retain historical '+group+'; append a correction')
                if any(after[k] != before[k] for k in ('stages', 'deadline', 'causal_assessment')):
                    require(after['evidence'] != before['evidence'] or after['contrary_evidence'] != before['contrary_evidence'], 'Assessment revision needs new evidence or counterassessment')
        latest[cid] = copy.deepcopy(case)
        revisions[cid] = revisions.get(cid, 0)+1
        history.append({'sequence': number, 'case_id': cid, 'revision': revisions[cid], 'recorded_at': entry['recorded_at'],
                        'actor': entry['actor'], 'reason': entry['reason'], 'entry_sha256': entry['entry_sha256'],
                        'stages': {r['relay_id']: {k:v['status'] for k,v in r['stages'].items()} for r in case['relays']},
                        'supports': copy.deepcopy(case['supports']), 'unknowns': copy.deepcopy(case['unknowns'])})
        previous, prior_time = entry['entry_sha256'], stamp
    state = {'version': 'relay-state-1', 'status': 'supplied assessments; no canonical admission or automatic causation/pattern finding',
             'journal_sha256': cycle.digest(journal), 'cases': latest, 'revisions': revisions, 'history': history,
             'timing': {cid: {r['relay_id']: timing(r) for r in c['relays']} for cid,c in latest.items()}}
    return state, resolved


def source_refs(case):
    return sorted({c['source_ref'] for r in case['relays'] for e in r['evidence'] for c in e['citations']})


def garden_pass(root, case, resolved, recorded_at):
    cid, qid = case['case_id'], 'Q-'+case['case_id']
    actor = {'name': 'Work Aiden', 'runtime': 'deterministic supplied relay projection', 'model': 'none invoked'}
    refs = source_refs(case)
    sources = [{'ref': ref, 'lineage_id': safeguards.lineage(ref, resolved),
                'kind': 'design_input' if case['mode'] == 'simulated' else 'public_source',
                'mode': case['mode'], 'binding': resolved[ref]['binding'],
                'access_limit': resolved[ref]['record'].get('limitations', 'See retained source record')} for ref in refs]
    arrival = {'id': cid+'-ARRIVAL', 'from': str(JOURNAL), 'to': 'INIT:ROOT-0001',
               'payload': {'case_id': cid, 'case_sha256': cycle.digest(case), 'mode': case['mode']}}
    start = {'run_id': cid+'-GARDEN', 'question_id': qid, 'epoch': 1, 'actor': actor, 'tree': 'INIT',
             'focus': case['scope'], 'arrival': arrival, 'sources': sources,
             'budget': {'max_steps':10, 'max_branches':1, 'max_events':10, 'max_fanout':0, 'model_calls':0},
             'status': case['mode']+' case-local supplied relay review; no shared registration'}
    outputs = [
        ('ROOT', {'name': case['mode'].upper()+': '+case['title']}),
        ('ARRIVAL', {'arrival': arrival, 'language_glance': {'languages': [], 'basis': 'unknown',
            'issuing_office': 'See inherited source records', 'surface_kind': 'summary', 'source_refs': refs,
            'note': 'Supplied review or fictional fixture; no new source/language observation.'}}),
        ('EPIST', {'prompt': case['scope'], 'starting_state': 'Separate origin, obligation, dispatch, receipt, action, outcome and verification.',
                   'mode': case['mode'], 'evidence_cutoff': case['evidence_cutoff']}),
        ('FUNC', {'task': 'Trace each relay without promoting one stage into the next.', 'function': case['scope'], 'relays': case['relays'], 'supports': case['supports']}),
        ('MIRROR', {'comparisons': [{'explanation': x['claim'], 'queries': [], 'answers': [{'evidence_ids': x['evidence_ids']}]} for r in case['relays'] for x in r['ordinary_explanations']],
                    'contrary_evidence': {r['relay_id']:r['contrary_evidence'] for r in case['relays']},
                    'information_lineage': {'parent_answer_visible': True, 'source_refs': refs,
                        'parent_output_refs': [str(JOURNAL)], 'criteria_refs': [str(SCHEMA)], 'api_record_refs': [], 'test_origin': 'inherited'}}),
        ('CROSS', {'inherited': [{'ref': r, 'status': case['mode']+' inherited material; no independent corroboration'} for r in refs],
                   'independent': [], 'bridge': [{'question': case['next_test'], 'status': 'proposed only'}]}),
        ('RESID', {'summary': '; '.join(case['unknowns']), 'predicates': {'consequential': True, 'distinct_functions': False, 'language_exception': None}}),
        ('MEAN', {'summary': case['title'], 'mode': case['mode'], 'stages': {r['relay_id']: {k:v['status'] for k,v in r['stages'].items()} for r in case['relays']}}),
        ('EXIT', {'kind': 'question', 'summary': case['next_test']}),
        ('RETURN', {'new_arrival': None, 'reason': 'Bounded demonstration complete; rest until separately reviewed evidence.'})]
    document = garden.new_document(garden.load_config(root), start, {'questions': {qid: {'epoch': 1}}})
    for i, (node, output) in enumerate(outputs):
        document = garden.apply_event(document, {'event_id': cid+'-STEP-'+str(i+1), 'expected_revision': i,
            'actor': actor, 'branch_id': 'B0', 'kind': 'step', 'node': node, 'output': output}, recorded_at)
    return garden.replay(document)


def markdown(state, resolved):
    def esc(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    def label(value):
        return value.replace('_', ' ').upper() if value == 'unknown' else value.replace('_', ' ')
    def dates(p):
        if p['start'] == p['end']:
            span = p['start'] or 'UNKNOWN'
        else:
            span = (p['start'] or 'UNKNOWN')+' → '+(p['end'] or 'UNKNOWN')
        return span+'; '+p['note']
    def refs(ids):
        return ', '.join(ids) or 'none asserted'
    def claims(title, items):
        if not items:
            return [title+': none supplied.', '']
        return [title+':', '']+['- '+i['claim']+' ['+refs(i['evidence_ids'])+']' for i in items]+['']
    lines = ['# Relay Continuity', '',
             'Supplied assessments, with empirical and fictional cases kept separate. UNKNOWN means knowledge stops; it does not declare a broken relay. No causal or systemic-pattern inference is generated.', '',
             '## At a glance', '',
             '| Case / relay | Supplied stage assessments | Documented issue | Knowledge stops |',
             '| --- | --- | --- | --- |']
    for cid, case in sorted(state['cases'].items()):
        for r in case['relays']:
            known = '; '.join(label(k)+': '+label(r['stages'][k]['status']) for k in STAGES if r['stages'][k]['status'] != 'unknown')
            issues = '; '.join(i['claim'] for i in r['issues']) or 'No failure finding supplied.'
            unknown = ', '.join(label(k) for k in STAGES if r['stages'][k]['status'] == 'unknown') or 'Beyond the stated observation window.'
            lines.append('| '+esc(case['mode'].upper()+' / '+r['relay_id'])+' | '+esc(known)+' | '+esc(issues)+' | '+esc(unknown)+' |')
    lines += ['', '“Source supported” describes the declared outcome and method below. It does not mean independent corroboration, broad safety, or real-world effectiveness of a simulated case.', '',
              '## Assessment history', '', 'Stage order: origin → expected transfer → dispatch → arrival → action → outcome → verification.', '',
              '| Case / revision | Recorded / reviewer | Reason |', '| --- | --- | --- |']
    for h in state['history']:
        lines.append('| '+h['case_id']+' / '+str(h['revision'])+' | '+esc(h['recorded_at']+'; '+h['actor'])+' | '+esc(h['reason'])+' |')
    for h in state['history']:
        lines += ['', 'Revision '+h['case_id']+'/'+str(h['revision'])+':', '']
        for rid, stages in h['stages'].items():
            lines.append('- '+rid+': '+' → '.join(label(stages[s]) for s in STAGES)+'.')
        for support in h['supports']:
            lines.append('- '+label(support['kind'])+' '+support['relay_id']+' → '+support['supports_relay']+': '+support['status']+'.')
        lines += ['- Residual then: '+u for u in h['unknowns']]
    for cid, case in sorted(state['cases'].items()):
        lines += ['', '## '+case['mode'].upper()+' — '+case['title'], '', case['scope'], '',
                  'Evidence cutoff: '+case['evidence_cutoff']+'. Current reviewed revision: '+str(state['revisions'][cid])+'.', '',
                  'Source families: '+', '.join(sorted({safeguards.lineage(ref, resolved) for ref in source_refs(case)}))+'. Reuse does not add corroboration.', '']
        for r in case['relays']:
            lines += ['### '+r['relay_id']+' · '+r['kind'], '',
                      r['payload']+'. '+r['essential_function'], '',
                      'From: '+r['from_actor']+'. To: '+r['to_actor']+'.', '', 'Scope: '+r['scope'], '',
                      '| Stage / status | Assessment / evidence | Occurrence or report time |', '| --- | --- | --- |']
            for stage_name in STAGES:
                a = r['stages'][stage_name]
                lines.append('| '+label(stage_name)+' / '+label(a['status'])+' | '+esc(a['claim']+' ['+refs(a['evidence_ids'])+']')+' | '+esc(dates(a['time']))+' |')
            method = r['stages']['verification']['method'] or 'Outcome verification not established.'
            lines += ['', 'Verification method: '+method, '']
            due, comparison = r['deadline'], timing(r)
            if due:
                lag = '' if comparison['lag_seconds'] is None else '; signed lag '+str(comparison['lag_seconds'])+' seconds'
                lines += ['Deadline: '+due['at']+' for '+due['stage']+'. '+due['claim']+' ['+refs(due['evidence_ids'])+']. Date comparison: '+comparison['status']+lag+'. This comparison does not establish cause.', '']
            else:
                lines += ['Deadline: not established; no deadline violation or exact lag is inferred.', '']
            if r['issues']:
                lines += ['Recorded issues (retained when later evidence changes an assessment):', '']
                for i in r['issues']:
                    lines.append('- '+label(i['kind'])+' at '+label(i['stage'])+'; mechanism '+label(i['mechanism'])+': '+i['claim']+' ['+refs(i['evidence_ids'])+']')
                lines.append('')
            if r['capacities']:
                lines += ['| Resource / basis | Quantity / time | Scope / evidence |', '| --- | --- | --- |']
                for c in r['capacities']:
                    lines.append('| '+esc(c['resource']+' / '+c['basis'])+' | '+esc((c['value'] or 'UNKNOWN')+' '+c['unit']+'; '+dates(c['time']))+' | '+esc(c['limits']+' ['+refs(c['evidence_ids'])+']')+' |')
                lines += ['', 'Units and scopes are retained separately; no automatic conversion or reserve-to-outcome inference.', '']
            else:
                lines += ['Quantified capacities: not supplied.', '']
            causal = r['causal_assessment']
            lines += ['Causation — '+label(causal['status'])+': '+causal['claim']+' ['+refs(causal['evidence_ids'])+']', '']
            lines += claims('Contrary evidence', r['contrary_evidence'])+claims('Ordinary explanations / alternatives', r['ordinary_explanations'])
            lines += ['| Evidence / class / result | Observation period | Claim / locator / limits |', '| --- | --- | --- |']
            for e in r['evidence']:
                citations = '; '.join(c['source_ref']+' '+c['locator'] for c in e['citations'])
                lines.append('| '+e['evidence_id']+' / '+label(e['kind'])+' / '+e['result']+' | '+esc(dates(e['observed']))+' | '+esc(e['claim']+' '+citations+'. '+e['limits'])+' |')
            lines.append('')
        lines += ['### Buffers, alternatives and residuals', '']
        if not case['supports']:
            lines += ['No verified buffer/substitution is supplied for this bounded case.', '']
        for support in case['supports']:
            lines += ['- '+support['kind']+' '+support['relay_id']+' → '+support['supports_relay']+' / '+support['status']+': '+support['claim']]
        lines += ['', 'Current unknowns:', '']+['- '+u for u in case['unknowns']]
        lines += ['', 'One proposed next test: '+case['next_test'], '', '### Shared reference lineage', '',
                  '| Source | Publication / retrieval / authorship | Shared record / hash |', '| --- | --- | --- |']
        for ref in source_refs(case):
            item = resolved[ref]
            rec, binding = item['record'], item['binding']
            chronology = '; '.join(k+': '+str(rec[k]) for k in ('publication_date','retrieved_date_utc','authored_at') if k in rec)
            path = binding['path']
            lines.append('| '+esc(ref+': '+rec.get('title', ref))+' | '+esc(chronology or 'See shared record.')+' | ['+path+'](../../../'+path+'); '+binding['sha256']+' |')
        lines += ['', 'Access and source limits:', '']
        for ref in source_refs(case):
            lines.append('- '+ref+': '+resolved[ref]['record'].get('limitations', 'See shared record.'))
        if case['event_refs']:
            lines += ['', '| Event selector | Historical date / publication / case reading | Shared record |', '| --- | --- | --- |']
            for ref in case['event_refs']:
                item = resolved[ref]
                rec = item['record']
                dates_ = '; '.join(k+': '+str(rec[k]) for k in ('event_date','publication_date','case_read_date') if k in rec)
                path = item['binding']['path']
                lines.append('| '+ref+' / '+item['binding']['record_id']+' | '+esc(dates_)+' | ['+path+'](../../../'+path+') |')
        if case['design_refs']:
            lines += ['', 'Design inputs (not empirical evidence):', '']
            for ref in case['design_refs']:
                path = resolved[ref]['binding']['path']
                lines.append('- '+ref+': ['+path+'](../../../'+path+').')
    lines += ['', 'Reference selectors and raw document pins: [references.json](../../../operations/relays/references.json). Full immutable review entries: [journal.json](../../../operations/relays/journal.json). Git retains the exact schema, code and Garden configuration for this review.', '']
    return '\n'.join(lines)


def outputs(root=ROOT):
    state, resolved = replay(root)
    journal = shared.strict_json(Path(root)/JOURNAL)
    result = {'relays.json': cycle.encoded(state), 'RELAYS.md': markdown(state, resolved).encode()}
    for cid, case in sorted(state['cases'].items()):
        stamp = next(e['recorded_at'] for e in reversed(journal['entries']) if e['case']['case_id'] == cid)
        result['garden/'+cid+'.json'] = cycle.encoded(garden_pass(root, case, resolved, stamp))
    return result


def build(root=ROOT, check=False):
    generated = outputs(root)
    for name, data in generated.items():
        path = Path(root)/OUTPUT/name
        if check:
            require(path.is_file() and path.read_bytes() == data, 'Saved relay output differs: '+name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    return len(generated)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate', 'replay', 'build', 'check'])
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        if args.command in {'build', 'check'}:
            print(f'PASS: {build(args.root, args.command == "check")} relay outputs; no collection/dispatch')
        else:
            state, _ = replay(args.root)
            print(f"PASS: {len(state['cases'])} cases; {len(state['history'])} revisions; {cycle.digest(state)}")
    except (Error, cycle.CycleError, ValueError, KeyError, TypeError, OSError) as exc:
        print('INVALID: '+str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
