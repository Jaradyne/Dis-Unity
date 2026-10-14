#!/usr/bin/env python3
"""Replay separate safeguard claims over shared records; no collection or dispatch."""
from __future__ import annotations

import argparse
import copy
from datetime import datetime
from pathlib import Path
import sys

import continuity as shared
import cycle
import garden_runtime as garden

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = Path('schemas/safeguard.schema.json')
REFERENCES = Path('operations/safeguards/references.json')
JOURNAL = Path('operations/safeguards/journal.json')
OUTPUT = Path('reports/safeguards/generated')
require = shared.require
Error = shared.ContinuityError
EMPIRICAL = {'implementation_observation', 'effectiveness_observation', 'noncompliance_observation'}


def resolve(root, manifest):
    require(set(manifest) == {'version', 'base', 'references', 'snapshots'}
            and manifest['version'] == 'safeguard-references-1', 'Invalid safeguard manifest')
    base = manifest['base']
    require(set(base) == {'path', 'sha256'}, 'Invalid shared reference base')
    catalog = shared.strict_json(shared.local_path(root, base['path']))
    require(cycle.digest(catalog) == base['sha256'], 'Shared reference base changed')
    require(isinstance(manifest['references'], dict) and isinstance(manifest['snapshots'], dict), 'Invalid references')
    require(not set(catalog['references']) & set(manifest['references']), 'Cannot shadow shared references')
    resolved = shared.resolve(root, {**catalog, 'references':{**catalog['references'], **manifest['references']}})
    for alias, binding in manifest['snapshots'].items():
        shared.shape(alias, {'type':'string', 'pattern':'^[A-Z][A-Z0-9-]*$'})
        require(alias not in resolved and set(binding) == {'path', 'sha256', 'parent_source_ref'}, 'Invalid snapshot binding')
        parent = binding['parent_source_ref']
        require(parent in resolved and resolved[parent]['binding']['kind'] == 'source', 'Unknown snapshot source')
        record = shared.strict_json(shared.local_path(root, binding['path']))
        require(cycle.digest(record) == binding['sha256'], 'Pinned source snapshot changed')
        require(record.get('source_id') and record.get('lineage_id'), 'Snapshot lacks source lineage')
        parent_record = resolved[parent]['record']
        require(record.get('parent_source_id') == parent_record.get('source_id')
                and isinstance(record.get('url'), str) and record['url']
                and record['url'] == parent_record.get('url'), 'Snapshot parent source identity mismatch')
        resolved[alias] = {'binding':{**binding, 'kind':'source', 'record_id':record['source_id']}, 'record':record}
    return resolved


def lineage(ref, resolved):
    item = resolved[ref]
    if 'parent_source_ref' in item['binding']:
        return lineage(item['binding']['parent_source_ref'], resolved)
    return item['record'].get('source_family') or item['record']['source_lineage']


def dimensions(record):
    return {'formal':record['formal']['status'],
            'operational':{k:v['status'] for k,v in record['operational'].items()},
            'effectiveness':record['effectiveness']['status'], 'failure':record['failure']['status']}


def validate(record, schema, resolved):
    shared.shape(record, schema)
    cutoff = shared.day(record['evidence_cutoff'])
    require(cutoff is not None, 'Evidence cutoff needs a day date')

    def known(ref, kind):
        require(ref in resolved and resolved[ref]['binding']['kind'] == kind, 'Missing/wrong-kind reference: '+ref)

    for ref in record['event_refs']:
        known(ref, 'event')
    evidence = {}
    for item in record['evidence']:
        eid = item['evidence_id']
        require(eid not in evidence, 'Duplicate evidence ID')
        evidence[eid] = item
        for citation in item['citations']:
            known(citation['source_ref'], 'source')
        for ref in item['event_refs']:
            known(ref, 'event')
            require(ref in record['event_refs'], 'Evidence event missing from case scope')
        start, end = (shared.date_bounds(item['period'][k]) for k in ('start', 'end'))
        require(not (start and end) or start[0] <= end[1], 'Definitely reversed evidence interval')
        require(all(not b or b[0] <= cutoff for b in (start, end)), 'Observation lies after evidence cutoff')
        if item['kind'] in EMPIRICAL:
            require(start or end, 'Empirical observation needs a dated period')
        if item['kind'] == 'effectiveness_observation':
            require(item['effect'] is not None, 'Effectiveness needs named harm, action, result and scope')
        else:
            require(item['effect'] is None, 'Only effectiveness observations may carry a proven-effect claim')

    def cited(assessment):
        require(len(set(assessment['evidence_ids'])) == len(assessment['evidence_ids']), 'Duplicate evidence citation')
        require(all(e in evidence for e in assessment['evidence_ids']), 'Unknown evidence ID')
        return {evidence[e]['kind'] for e in assessment['evidence_ids']}

    formal_kinds = cited(record['formal'])
    if record['formal']['status'] != 'unknown':
        require('formal_text' in formal_kinds, 'Formal status needs a formal-text record')
    for part, assessment in record['operational'].items():
        kinds = cited(assessment)
        if assessment['status'] != 'unknown':
            require(bool(kinds & {'implementation_observation', 'noncompliance_observation'}),
                    'Operational '+part+' needs observed implementation/noncompliance; policy alone is insufficient')
    kinds = cited(record['effectiveness'])
    if record['effectiveness']['status'] == 'observed':
        require('effectiveness_observation' in kinds,
                'Observed effectiveness needs a dated harm/action/result record; existence, activity, responses and ratings do not suffice')
    kinds = cited(record['failure'])
    if record['failure']['status'] == 'documented':
        require('noncompliance_observation' in kinds, 'Documented failure needs observed noncompliance; Open/unknown is insufficient')
    elif record['failure']['status'] == 'reported':
        require(bool(kinds & {'reported_concern', 'noncompliance_observation'}), 'Reported failure needs an attributed report')
    for group in ('contrary_evidence', 'ordinary_explanations'):
        for item in record[group]:
            cited(item)


def make_entry(safeguard, *, sequence, recorded_at, actor, reason, expected_revision, previous):
    entry = {'sequence':sequence, 'recorded_at':recorded_at, 'actor':actor, 'reason':reason,
             'expected_revision':expected_revision, 'previous_entry_sha256':previous,
             'safeguard':copy.deepcopy(safeguard)}
    return {**entry, 'entry_sha256':cycle.digest(entry)}


def replay(root=ROOT, journal=None, manifest=None, schema=None):
    root = Path(root)
    journal = shared.strict_json(root/JOURNAL) if journal is None else journal
    manifest = shared.strict_json(root/REFERENCES) if manifest is None else manifest
    schema = shared.strict_json(root/SCHEMA) if schema is None else schema
    require(set(journal) == {'version', 'schema_sha256', 'references_sha256', 'entries'}
            and journal['version'] == 'safeguard-journal-1', 'Invalid journal')
    require(journal['schema_sha256'] == cycle.digest(schema), 'Schema snapshot mismatch')
    require(journal['references_sha256'] == cycle.digest(manifest), 'Reference manifest mismatch')
    resolved = resolve(root, manifest)
    require(isinstance(journal['entries'], list) and journal['entries'], 'Journal needs entries')
    latest, revisions, history = {}, {}, []
    previous, prior_time = shared.ZERO, None
    for number, entry in enumerate(journal['entries'], 1):
        require(set(entry) == {'sequence','recorded_at','actor','reason','expected_revision','previous_entry_sha256','safeguard','entry_sha256'}, 'Invalid entry')
        require(type(entry['sequence']) is int and entry['sequence'] == number, 'Journal sequence mismatch')
        require(entry['previous_entry_sha256'] == previous, 'Broken history chain')
        require(entry['entry_sha256'] == cycle.digest({k:v for k,v in entry.items() if k != 'entry_sha256'}), 'Entry modified')
        require(all(isinstance(entry[k], str) and entry[k].strip() for k in ('actor','reason','recorded_at')), 'Attribution, reason and date required')
        stamp = datetime.fromisoformat(entry['recorded_at'].replace('Z','+00:00'))
        require(stamp.tzinfo is not None and (prior_time is None or stamp >= prior_time), 'Timestamps must be aware and nondecreasing')
        record = entry['safeguard']
        validate(record, schema, resolved)
        sid = record['safeguard_id']
        require(type(entry['expected_revision']) is int and entry['expected_revision'] == revisions.get(sid, 0), 'Stale safeguard revision')
        old = latest.get(sid)
        if old:
            require(record['scope'] == old['scope'], 'Changed scope requires a new safeguard ID')
            require(record['evidence_cutoff'] >= old['evidence_cutoff'], 'Evidence cutoff cannot move backwards')
            new_items = {e['evidence_id']:e for e in record['evidence']}
            require(all(new_items.get(e['evidence_id']) == e for e in old['evidence']), 'Retain earlier evidence unchanged; append a correction or challenge')
            require(all(item in record['contrary_evidence'] for item in old['contrary_evidence']),
                    'Retain earlier contrary assessments; append a correction or challenge')
            if dimensions(old) != dimensions(record):
                require(old['evidence'] != record['evidence'] or old['contrary_evidence'] != record['contrary_evidence'],
                        'Status revision requires changed evidence or explicit counterassessment')
        latest[sid] = copy.deepcopy(record)
        revisions[sid] = revisions.get(sid, 0) + 1
        history.append({'sequence':number, 'safeguard_id':sid, 'revision':revisions[sid],
                        'recorded_at':entry['recorded_at'], 'actor':entry['actor'], 'reason':entry['reason'],
                        'dimensions':dimensions(record), 'entry_sha256':entry['entry_sha256']})
        previous, prior_time = entry['entry_sha256'], stamp
    return {'version':'safeguard-state-1', 'status':'supplied review; no canonical admission',
            'journal_sha256':cycle.digest(journal), 'safeguards':latest, 'revisions':revisions,
            'history':history}, resolved


def source_refs(record):
    return sorted({c['source_ref'] for e in record['evidence'] for c in e['citations']})


def garden_pass(root, record, resolved, recorded_at):
    sid, qid = record['safeguard_id'], 'Q-'+record['safeguard_id']
    actor = {'name':'Work Aiden', 'runtime':'deterministic supplied safeguard projection', 'model':'none invoked'}
    refs = source_refs(record)
    sources = [{'ref':ref, 'lineage_id':lineage(ref,resolved), 'kind':'public_source',
                'binding':resolved[ref]['binding'], 'access_limit':resolved[ref]['record'].get('limitations',resolved[ref]['record'].get('access'))} for ref in refs]
    arrival = {'id':sid+'-ARRIVAL', 'from':str(JOURNAL), 'to':'INIT:ROOT-0001',
               'payload':{'safeguard_id':sid, 'safeguard_sha256':cycle.digest(record)}}
    start = {'run_id':sid+'-GARDEN', 'question_id':qid, 'epoch':1, 'actor':actor, 'tree':'INIT',
             'focus':record['scope'], 'arrival':arrival, 'sources':sources,
             'budget':{'max_steps':10,'max_branches':1,'max_events':10,'max_fanout':0,'model_calls':0},
             'status':'case-local supplied review; no shared Question registration'}
    outputs = [
        ('ROOT', {'name':record['title']}),
        ('ARRIVAL', {'arrival':arrival, 'language_glance':{'languages':[], 'basis':'unknown',
            'issuing_office':'See shared source records', 'surface_kind':'summary', 'source_refs':refs,
            'note':'Supplied metadata; no fresh source-language observation.'}}),
        ('EPIST', {'prompt':'Which safeguard claims are supported?', 'starting_state':'Separate formal, operational, effectiveness and failure claims; see dimensions.', 'dimensions':dimensions(record),
                   'cutoff':record['evidence_cutoff'], 'rule':'Formal existence never promotes operation or effectiveness.'}),
        ('FUNC', {'task':record['scope'], 'function':'Keep each safeguard claim within its cited evidence class and scope.', 'formal':record['formal'], 'operational':record['operational'],
                  'effectiveness':record['effectiveness'], 'failure':record['failure'], 'evidence':record['evidence']}),
        ('MIRROR', {'comparisons':[{'explanation':i['claim'],'queries':[], 'answers':[{'evidence_ids':i['evidence_ids']}]} for i in record['ordinary_explanations']],
                    'contrary_evidence':record['contrary_evidence'], 'information_lineage':{
                        'parent_answer_visible':True, 'source_refs':refs, 'parent_output_refs':[str(JOURNAL)],
                        'criteria_refs':[str(SCHEMA)], 'api_record_refs':[], 'test_origin':'inherited'}}),
        ('CROSS', {'inherited':[{'ref':ref,'status':'shared archive; inherited, not independent corroboration'} for ref in refs],
                   'independent':[], 'bridge':[{'question':record['next_test']['question'],'status':'proposed only'}]}),
        ('RESID', {'summary':' '.join(record['residuals']), 'next_test':record['next_test'],
                   'predicates':{'consequential':True,'distinct_functions':False,'language_exception':None}}),
        ('MEAN', {'summary':record['effectiveness']['claim'], 'dimensions':dimensions(record)}),
        ('EXIT', {'kind':'question','summary':record['next_test']['question']}),
        ('RETURN', {'new_arrival':None,'reason':record['rest_until']})]
    document = garden.new_document(garden.load_config(root),start,{'questions':{qid:{'epoch':1}}})
    for number, (node, output) in enumerate(outputs):
        command = {'event_id':sid+'-STEP-'+str(number+1),'expected_revision':number,'actor':actor,
                   'branch_id':'B0','kind':'step','node':node,'output':output}
        document = garden.apply_event(document,command,recorded_at)
    return garden.replay(document)


def markdown(state, resolved):
    def display(v):
        return 'unknown' if v is None else str(v).replace('|','\\|').replace('\n',' ')
    def link(ref):
        b = resolved[ref]['binding']
        return '['+b['record_id']+'](../../../'+b['path']+')'
    lines = ['# Safeguard Reality Check', '',
             'Separate supplied claims, not a protection score. Formal text and agency promises are not empirical protection. '
             'Unknown effectiveness is not proof of failure. Replay checks consistency, not truth.', '',
             '| Case | Formal | Operational: people / procedures / authority | Observed effectiveness | Failure |',
             '| --- | --- | --- | --- | --- |']
    for _, record in sorted(state['safeguards'].items()):
        lines.append('| '+' | '.join([record['title'],record['formal']['status'],
            ' / '.join(record['operational'][k]['status'] for k in ('people','procedures','authority')),
            record['effectiveness']['status'],record['failure']['status']])+' |')
    for sid, record in sorted(state['safeguards'].items()):
        lines += ['', '## '+record['title'], '', record['scope'], '',
                  'Evidence cutoff: '+record['evidence_cutoff']+'. Assessment revision: '+str(state['revisions'][sid])+'.', '']
        assessments = [('Formal',record['formal']), *[(k.capitalize(),v) for k,v in record['operational'].items()],
                       ('Observed effectiveness',record['effectiveness']),('Failure',record['failure'])]
        for label, item in assessments:
            lines.append('- **'+label+' — '+item['status']+':** '+item['claim']+' ['+', '.join(item['evidence_ids'])+']')
        for label, key in [('Contrary evidence and formal constraints','contrary_evidence'),('Ordinary explanations','ordinary_explanations')]:
            lines += ['', '**'+label+':**', '']
            for item in record[key]:
                kinds = sorted({e['kind'] for e in record['evidence'] if e['evidence_id'] in item['evidence_ids']})
                lines.append('- '+item['claim']+' ['+', '.join(item['evidence_ids'])+'; '+', '.join(kinds)+']')
        lines += ['', '**Retained evidence (classifications are supplied judgments):**', '']
        for item in record['evidence']:
            lines.append('- **'+item['evidence_id']+' · '+item['kind']+'** · '+display(item['period']['start'])+' → '+display(item['period']['end'])+': '+item['claim'])
            lines.append('  '+item['period']['note']+' '+item['limits'])
            lines.append('  Sources: '+'; '.join(link(c['source_ref'])+' · '+c['locator'] for c in item['citations'])+'.')
            if item['effect']:
                lines.append('  Effect: '+'; '.join(k+': '+v for k,v in item['effect'].items()))
        lines += ['', '**Unknowns and limits:**', '', *['- '+x for x in record['residuals']], '',
                  '**One proposed next test:** '+record['next_test']['question'], '',
                  'Required record: '+record['next_test']['required_record'],
                  'Supports: '+record['next_test']['supports_if'], 'Weakens: '+record['next_test']['weakens_if'],
                  'Stop: '+record['next_test']['stop_condition'], '', '**Rest:** '+record['rest_until'], '',
                  '**Shared event dates and qualifications:**', '']
        for ref in record['event_refs']:
            data = resolved[ref]['record']
            parts = {k:v for k,v in data.items() if 'date' in k or k in ('date_precision','uncertainty','limits','implementation_status','discovery_status')}
            lines.append('- '+link(ref)+': '+'; '.join(k.replace('_',' ')+': '+display(v) for k,v in parts.items()))
    lines += ['', '## Source lineage and access', '']
    for ref in sorted({r for record in state['safeguards'].values() for r in source_refs(record)}):
        item = resolved[ref]['record']
        lines.append('- '+link(ref)+' ('+ref+'): '+lineage(ref,resolved)+'. Publication '+display(item.get('publication_date'))
                     +'; catalog retrieval '+display(item.get('retrieved_date_utc'))+'; snapshot observation '+display(item.get('observed_date'))+'.')
        lines.append('  '+str(item.get('access_level',item.get('access','See shared record')))+'. '+str(item.get('limitations',item.get('interpretation',''))))
    lines += ['', '## Dated assessment revisions', '']
    for entry in state['history']:
        lines.append('- '+entry['recorded_at']+' · '+entry['actor']+' · '+entry['safeguard_id']+' revision '+str(entry['revision'])+': '+entry['reason'])
    return '\n'.join(lines)+'\n'


def outputs(root=ROOT):
    state, resolved = replay(root)
    journal = shared.strict_json(Path(root)/JOURNAL)
    result = {'safeguards.json':cycle.encoded(state), 'SAFEGUARDS.md':markdown(state,resolved).encode()}
    for sid, record in sorted(state['safeguards'].items()):
        stamp = next(e['recorded_at'] for e in reversed(journal['entries']) if e['safeguard']['safeguard_id'] == sid)
        result['garden/'+sid+'.json'] = cycle.encoded(garden_pass(root,record,resolved,stamp))
    return result


def build(root=ROOT, check=False):
    generated, dest = outputs(root), Path(root)/OUTPUT
    if check:
        actual = {p.relative_to(dest).as_posix():p.read_bytes() for p in dest.rglob('*') if p.is_file()}
        require(actual == generated, 'Generated safeguard projections differ')
    else:
        for name, data in generated.items():
            path = dest/name
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
            count = build(args.root, args.command == 'check')
            print(f'PASS: {count} deterministic outputs; {count-2} resting Garden passes; no dispatch')
        else:
            state,_ = replay(args.root)
            print(f"PASS: {len(state['safeguards'])} safeguards; {len(state['history'])} entries; {cycle.digest(state)}")
    except (Error, cycle.CycleError, ValueError, KeyError, TypeError, OSError) as exc:
        print('INVALID: '+str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
