#!/usr/bin/env python3
"""Replay one public Campus Motel packet through existing safeguards/relays/Garden."""
from pathlib import Path
import argparse
import hashlib
import sys

import continuity as shared
import cycle
import garden_runtime as garden
import relays
import safeguards

ROOT = Path(__file__).resolve().parents[1]
OPS = Path('operations/shelter-accountability/campus-motel')
REPORT = Path('reports/shelter-accountability/campus-motel')
OUTPUT = REPORT/'generated'
REQUIRED = {str(OPS/n) for n in ('case.json', 'safeguard-journal.json',
    'safeguard-references.json', 'relay-journal.json', 'relay-references.json')} | {
    str(REPORT/'sources.json'), str(REPORT/'events.json'), 'config/garden-traversal.json'}
require = shared.require


def replay(root=ROOT):
    root = Path(root)
    read = lambda p: shared.strict_json(root/p)
    pins = read(OPS/'inputs.json')
    require(set(pins) == {'version', 'sha256'} and pins['version'] == 'campus-inputs-1', 'Invalid pins')
    require(REQUIRED <= set(pins['sha256']), 'Missing required input pin')
    for path, sha in pins['sha256'].items():
        require(hashlib.sha256(shared.local_path(root, path).read_bytes()).hexdigest() == sha,
                'Pinned input changed: '+path)
    meta = read(OPS/'case.json')
    require(meta['version'] == 'campus-case-1' and meta['case_id'] == 'CAMPUS-MOTEL-PACKET'
            and meta['safeguard_id'] == 'SG-CAMPUS-NOTICE' and meta['tree'] == 'HOMELESSNESS'
            and meta['record_class'] == 'historical_public_packet_incomplete'
            and meta['current_executed_agreement'] == 'not_verified', 'Unexpected case scope')
    sg, sr = safeguards.replay(root, journal=read(OPS/'safeguard-journal.json'),
                                manifest=read(OPS/'safeguard-references.json'))
    rl, rr = relays.replay(root, journal=read(OPS/'relay-journal.json'),
                            manifest=read(OPS/'relay-references.json'))
    require(sr == rr, 'Safeguard and relay lineage disagree')
    require(set(sg['safeguards']) == {meta['safeguard_id']} and
            set(rl['cases']) == {meta['case_id']}, 'Keep one case')
    s, c = sg['safeguards'][meta['safeguard_id']], rl['cases'][meta['case_id']]
    require(s['scope'] == c['scope'] == meta['scope'] and
            s['evidence_cutoff'] == c['evidence_cutoff'] == meta['evidence_cutoff'], 'Scope/cutoff mismatch')
    require(set(s['event_refs']) == set(c['event_refs']) and
            s['next_test']['question'] == c['next_test'], 'Case lineage/next test mismatch')
    stamp = relays.bounds(meta['recorded_at'])[0]
    require('T' in meta['recorded_at'] and all(relays.bounds(h['recorded_at'])[0] <= stamp
            for state in (sg, rl) for h in state['history']), 'Projection predates review')
    # Verify retained materials as well as record-level reference hashes.
    for source in read(REPORT/'sources.json')['sources']:
        for material in source['materials']:
            path = (REPORT/material['body']).as_posix()
            local = shared.local_path(root, path)
            key = local.relative_to(root.resolve()).as_posix()
            require(key in pins['sha256'] and pins['sha256'][key] == material['sha256'],
                    'Source material missing/mismatched pin')
    return {'meta':meta, 'input_pins':pins, 'safeguards':sg, 'relays':rl}, sr


def garden_pass(root, state, resolved):
    m = state['meta']
    s = state['safeguards']['safeguards'][m['safeguard_id']]
    c = state['relays']['cases'][m['case_id']]
    refs = sorted(set(safeguards.source_refs(s)) | set(relays.source_refs(c)))
    sources = [{'ref':r, 'lineage_id':safeguards.lineage(r,resolved), 'kind':'public_source',
                'binding':resolved[r]['binding'], 'access_limit':resolved[r]['record'].get('limitations','See source')}
               for r in refs]
    actor = {'name':'Work Aiden', 'runtime':'deterministic supplied Campus packet projection', 'model':'none invoked'}
    arrival = {'id':'CAMPUS-PACKET-ARRIVAL', 'from':str(OPS), 'to':'HOMELESSNESS:ROOT-0001',
               'payload':{'case_id':m['case_id'], 'input_pins_sha256':cycle.digest(state['input_pins']),
                          'classification':m['record_class'], 'current_executed_agreement':m['current_executed_agreement']}}
    start = {'run_id':'CAMPUS-PACKET-GARDEN', 'question_id':m['question_id'], 'epoch':m['question_epoch'],
             'actor':actor, 'tree':m['tree'], 'focus':m['scope'], 'arrival':arrival, 'sources':sources,
             'budget':{'max_steps':10,'max_branches':1,'max_events':10,'max_fanout':0,'model_calls':0},
             'status':'case-local supplied review; no shared Question registration or canonical admission'}
    nodes = [
        ('ROOT', {'name':s['title']}),
        ('ARRIVAL', {'arrival':arrival, 'language_glance':{'languages':['English'], 'basis':'participant_supplied',
            'issuing_office':'City of Berkeley; inherited legal sources separately identified',
            'surface_kind':'summary', 'source_refs':refs,
            'note':'English public records read; no resident-language delivery or translated notice observed.'}}),
        ('EPIST', {'prompt':m['scope'], 'starting_state':m['record_class'], 'dimensions':safeguards.dimensions(s)}),
        ('FUNC', {'task':m['scope'], 'function':'Keep authorization, execution, duties and protection distinct.',
                  'safeguard':s, 'relays':c['relays']}),
        ('MIRROR', {'comparisons':[{'explanation':x['claim'], 'queries':[], 'answers':[{'evidence_ids':x['evidence_ids']}]}
                                   for x in s['ordinary_explanations']], 'contrary_evidence':s['contrary_evidence'],
                    'information_lineage':{'parent_answer_visible':True, 'source_refs':refs,
                        'parent_output_refs':[str(OPS/'safeguard-journal.json'),str(OPS/'relay-journal.json')],
                        'criteria_refs':[str(safeguards.SCHEMA),str(relays.SCHEMA)],
                        'api_record_refs':['API-CAMPUS-LEASE-20261021-0001'], 'test_origin':'inherited'}}),
        ('CROSS', {'inherited':[{'ref':r,'status':'Source-linked public material; reuse is not independent corroboration.'} for r in refs],
                   'independent':[], 'bridge':[{'question':c['next_test'],'status':'proposed only'}]}),
        ('RESID', {'summary':'; '.join(c['unknowns']), 'next_test':s['next_test'],
                   'predicates':{'consequential':True,'distinct_functions':False,'language_exception':None}}),
        ('MEAN', {'summary':'Public packet incomplete; current execution, notice practice and remedy effectiveness unknown.',
                  'dimensions':safeguards.dimensions(s)}),
        ('EXIT', {'kind':'question','summary':c['next_test']}),
        ('RETURN', {'new_arrival':None,'reason':m['stop_condition']})]
    doc = garden.new_document(garden.load_config(root),start,{'questions':{m['question_id']:{'epoch':m['question_epoch']}}})
    for i,(node,output) in enumerate(nodes):
        doc = garden.apply_event(doc,{'event_id':'CAMPUS-STEP-'+str(i+1),'expected_revision':i,'actor':actor,
            'branch_id':'B0','kind':'step','node':node,'output':output},m['recorded_at'])
    doc = garden.replay(doc)
    require(doc['state']['used'] == {'steps':10,'branches':1,'model_calls':0}
            and doc['state']['branches']['B0']['status'] == 'resting' and not doc['state']['route_decisions'],
            'Unexpected execution/routing')
    return doc


def markdown(state, resolved):
    m = state['meta']; s = state['safeguards']['safeguards'][m['safeguard_id']]
    c = state['relays']['cases'][m['case_id']]
    esc = lambda x: str(x).replace('|','\\|').replace('\n',' ')
    lines = ['# Campus Motel: public duties and the missing executed packet', '',
        '**Result: historical public packet incomplete. Current executed operating agreement NOT VERIFIED.**', '',
        'Evidence cutoff: '+m['evidence_cutoff']+' UTC. Older records are late discoveries, not new resident incidents.', '',
        'This reads one program’s 2023 authorization/lease packet with limited identity and currentness checks. '
        'It does not establish a current seven-day rule, unlawful removal, fraud, actual closure or a successful remedy.', '',
        '## What the records establish', '', '| Record | Classification and finding | Source / locator |', '| --- | --- | --- |']
    for e in s['evidence']:
        if e['evidence_id'].startswith('CM-'):
            lines.append('| '+e['evidence_id']+' | '+esc(e['kind']+': '+e['claim'])+' | '+
                '; '.join(x['source_ref']+' — '+esc(x['locator']) for x in e['citations'])+' |')
    lines += ['', 'The property agreement, Insight operating contract and resident agreement are distinct instruments. '
        'Blank signature/date fields and the property-name anomaly prevent treating the posted lease as the authenticated final version. '
        'Item07 p.5 proposes that signed contracts/amendments will be filed with the City Clerk; their existence and current availability were not verified. '
        'The records portal exposed instructions but no searchable results in the text tool; the archive was not exhaustively searched.', '',
        '## Safeguard reality check', '', '| Dimension | Status | Assessment |', '| --- | --- | --- |']
    for name,a in [('Formal framework',s['formal']), *[('Operational '+k,v) for k,v in s['operational'].items()],
                   ('Observed effectiveness',s['effectiveness']),('Documented failure',s['failure'])]:
        lines.append('| '+name+' | '+a['status'].upper()+' | '+esc(a['claim'])+' |')
    lines += ['', 'The existing shelter-law baseline is referenced, not rewritten or refreshed. '
        'Its statutory scope, exceptions, preserved rights and official-text access limits still apply. '
        'No 2026 code version is retroactively treated as the law governing an alleged 2023 event.', '',
        '## Where knowledge stops', '', '| Relay | Conditional expectation | Origin / dispatch / receipt / action / outcome / verification |', '| --- | --- | --- |']
    for r in c['relays']:
        lines.append('| '+r['relay_id']+' | '+esc(r['from_actor']+' → '+r['to_actor']+': '+r['payload'])+' | '+
            ' / '.join(r['stages'][k]['status'].upper() for k in ('origin','dispatch','arrival','action','outcome','verification'))+' |')
    lines += ['', 'No dated resident trigger is supplied, so neither a calendar deadline nor a deadline violation is computed. '
        'Proposed meals, transport, housing navigation and partner services are potential supports; usable capacity and successful substitution remain unverified. '
        'A referral or readmission direction would still need evidence of actual acceptance and sustained access.', '',
        '## Contrary evidence and alternatives', '']+['- '+x['claim'] for x in s['contrary_evidence']+s['ordinary_explanations']]
    lines += ['', '## Source lineage', '', '| Source | Date and access limit |', '| --- | --- |']
    for ref in ['S-CM01','S-CM02','S-CM03','S-CM04','S-CM05']:
        v=resolved[ref]['record']
        lines.append('| ['+ref+': '+esc(v['title'])+']('+v['url']+') | '+v['publication_date']+'; '+esc(v['limitations'])+' |')
    lines += ['', 'CM01–03 share one City transaction family; wrapper republication and source reuse add no independent corroboration. '
        'CM04’s March28 date survives its December wrapper. CM05 is an unverified index lead, not a finding. '
        'The original lease HTTP response and separate web-tool captures retain their different receipt types. '
        'Hashes detect changed material, not truth or authorship.', '',
        '## Residual and one next question', '', '**'+c['next_test']+'**', '',
        'A current executed packet could resolve duties and the text tension. Actual delivery, grievance decisions and verified readmission would still be needed to assess practice or protection.', '',
        m['stop_condition'], '',
        'Offline replay: `python scripts/campus_motel.py check`. [Sources](../sources.json) · [source review](../SOURCE_REVIEW.md) · [saved Garden pass](GARDEN.json).', '']
    return '\n'.join(lines).encode()


def outputs(root=ROOT):
    state, resolved = replay(root)
    return {'STATE.json':cycle.encoded(state), 'GARDEN.json':cycle.encoded(garden_pass(root,state,resolved)),
            'CAMPUS.md':markdown(state,resolved)}


def build(root=ROOT, check=False):
    for name,data in outputs(root).items():
        path = Path(root)/OUTPUT/name
        if check:
            require(path.is_file() and path.read_bytes() == data, 'Saved output differs: '+name)
        else:
            path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['build','check']); args=p.parse_args()
    try:
        build(check=args.command=='check')
    except (shared.ContinuityError,cycle.CycleError,ValueError,KeyError,TypeError,OSError) as exc:
        print('INVALID: '+str(exc),file=sys.stderr); return 1
    print('PASS: one Campus packet; shared safeguard/relay validation; 10 Garden nodes; 0 calls; three outputs')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
