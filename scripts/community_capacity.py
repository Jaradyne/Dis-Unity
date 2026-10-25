#!/usr/bin/env python3
"""Replay a bounded community-capacity case using existing safeguard/relay/Garden contracts.

No network, model dispatch, Governor decision or canonical evidence admission.
The supplemental tree is available here; the global dispatcher is unchanged.
"""
from copy import deepcopy
from decimal import Decimal
import argparse
import hashlib
from pathlib import Path
import re
import sys

import continuity as shared
import cycle
import garden_runtime as garden
import governor_inbox
import meaning_boss
import relays
import safeguards

ROOT = Path(__file__).resolve().parents[1]
CASE = Path('operations/community-capacity/richmond')
REPORT = Path('reports/shelter-accountability/richmond-operations-20261024')
OUTPUT = REPORT/'generated'
TREE = Path('config/community-capacity-tree.json')
require = shared.require


def tree_config(root=ROOT, extension=None):
    config = garden.load_config(root)
    ext = shared.strict_json(Path(root)/TREE) if extension is None else extension
    require(set(ext) == {'version','base_sha256','tree_id','definition','context_trees'}, 'Invalid tree extension')
    require(ext['version'] == 'garden-tree-extension-1', 'Unknown extension version')
    require(hashlib.sha256((Path(root)/'config/garden-traversal.json').read_bytes()).hexdigest()
            == ext['base_sha256'], 'Tree base pin changed')
    require(ext['tree_id'] not in config['trees'], 'Tree extension cannot replace a tree')
    require(re.fullmatch(r'[A-Z][A-Z0-9-]*',ext['tree_id']) is not None, 'Invalid tree ID')
    d = ext['definition']
    require(set(d) == {'name','node_template','status'} and d['node_template'] == 'INIT'
            and d['status'] == 'traversable_with_supplied_content' and d['name'], 'Invalid tree definition')
    require(set(ext['context_trees']) <= set(config['trees']), 'Unknown context tree')
    config['trees'][ext['tree_id']] = deepcopy(d)
    return config


def validate_costs(costs, resolved):
    """Keep amount, instrument, period and document status together; never annualize."""
    require(isinstance(costs,list) and costs, 'Cost observations required')
    ids = set()
    fields = {'id','amount_usd','status','period','scope','source_refs','locator','limits','as_of'}
    for cost in costs:
        require(set(cost) == fields and cost['id'] not in ids, 'Invalid/duplicate cost record')
        ids.add(cost['id'])
        require(isinstance(cost['amount_usd'],str) and
                re.fullmatch(r'(0|[1-9][0-9]*)(\.[0-9]{1,2})?',cost['amount_usd']) is not None,
                'Use a nonnegative USD decimal string')
        require(cost['status'] in {'reported_unverified','historical_budget','proposed_grant',
                'documented_quote','executed_award','observed_payment'}, 'Unknown cost status')
        require(all(isinstance(cost[k],str) and cost[k].strip() for k in ('period','scope','locator','limits')),
                'Cost needs period, scope, locator and limits')
        shared.date_value(cost['as_of'])
        require(isinstance(cost['source_refs'],list) and
                all(r in resolved and resolved[r]['binding']['kind']=='source' for r in cost['source_refs']),
                'Unknown cost source')
        if cost['status'] != 'reported_unverified':
            require(cost['source_refs'], 'Documented cost needs a source')
        required_class = {'documented_quote':'priced_proposal', 'executed_award':'executed_agreement',
                          'observed_payment':'payment_record'}.get(cost['status'])
        if required_class:
            require(any(resolved[r]['record'].get('record_class') == required_class for r in cost['source_refs']),
                    'Cost status needs the matching instrument class')


def replay(root=ROOT):
    root = Path(root)
    read = lambda p: shared.strict_json(root/p)
    pins = read(CASE/'inputs.json')
    require(set(pins)=={'version','sha256'} and pins['version']=='community-capacity-inputs-1','Invalid input pins')
    required = {str(CASE/n) for n in ('case.json','references.json','safeguard-references.json',
                'relay-references.json','safeguard-journal.json','relay-journal.json','meaning-question-snapshot.json')} | {
                str(REPORT/'sources.json'),str(REPORT/'events.json'),str(TREE),'config/garden-traversal.json'}
    require(required <= set(pins['sha256']), 'Missing case input pin')
    for path, sha in pins['sha256'].items():
        require(hashlib.sha256(shared.local_path(root,path).read_bytes()).hexdigest()==sha, 'Pinned input changed: '+path)
    m=read(CASE/'case.json')
    require(m['version']=='community-capacity-case-1' and m['tree']==read(TREE)['tree_id'],'Invalid case/tree')
    sg,sr=safeguards.replay(root,journal=read(CASE/'safeguard-journal.json'),manifest=read(CASE/'safeguard-references.json'))
    rl,rr=relays.replay(root,journal=read(CASE/'relay-journal.json'),manifest=read(CASE/'relay-references.json'))
    require(sr==rr,'Shared source lineage differs')
    require(set(sg['safeguards'])=={m['safeguard_id']} and set(rl['cases'])=={m['case_id']},'One bounded case required')
    s,c=sg['safeguards'][m['safeguard_id']],rl['cases'][m['case_id']]
    require(s['scope']==c['scope']==m['scope'] and s['evidence_cutoff']==c['evidence_cutoff']==m['evidence_cutoff'],
            'Case scope/cutoff differs')
    require(s['next_test']['question']==c['next_test']==m['next_test'],'Next test differs')
    require('T' in m['recorded_at'] and all(relays.bounds(h['recorded_at'])[0] <= relays.bounds(m['recorded_at'])[0]
            for state in (sg,rl) for h in state['history']), 'Projection predates assessment')
    validate_costs(m['costs'],sr)
    eids={e['evidence_id'] for e in s['evidence']}
    for gate in m['gates']:
        require(set(gate)=={'gate','controller','requirement','current_status','evidence_ids','alternative'},'Invalid gate')
        require(gate['current_status'] in {'unknown','documented_historical_requirement'},'Gate is not current operating proof')
        require(set(gate['evidence_ids']) <= eids,'Unknown gate evidence')
    for source in read(REPORT/'sources.json')['sources']:
        for material in source.get('materials',[]):
            require(pins['sha256'].get(material['path'])==material['sha256'],'Unpinned source material')
    snapshot=read(CASE/'meaning-question-snapshot.json')
    require(snapshot['version']=='meaning-question-snapshot-1' and
            set(snapshot['registry']['questions'])=={meaning_boss.QUESTION},'Invalid historical Meaning registry')
    # A saved encounter keeps the epoch observed at preparation. Advancing a live
    # Question later must not invalidate this historical case or close the newer epoch.
    meaning_boss.validate_packet(read(m['meaning_packet']),snapshot['registry'])
    governor_inbox.validate(root,root/m['governor_input'])
    return {'meta':m,'input_pins':pins,'safeguards':sg,'relays':rl},sr


def garden_pass(root,state,resolved):
    m=state['meta']; s=state['safeguards']['safeguards'][m['safeguard_id']]
    c=state['relays']['cases'][m['case_id']]
    refs=sorted(set(safeguards.source_refs(s))|set(relays.source_refs(c)))
    sources=[{'ref':r,'lineage_id':safeguards.lineage(r,resolved),'kind':'public_source',
              'binding':resolved[r]['binding'],'access_limit':resolved[r]['record']['limitations']} for r in refs]
    actor={'name':'Work Aiden','runtime':'deterministic projection of reviewed supplied material','model':'none invoked'}
    arrival={'id':m['case_id']+'-ARRIVAL','from':str(CASE),'to':m['tree']+':ROOT-0001',
             'payload':{'case_id':m['case_id'],'inputs_sha256':cycle.digest(state['input_pins'])}}
    start={'run_id':m['case_id']+'-GARDEN','question_id':m['question_id'],'epoch':m['question_epoch'],
           'actor':actor,'tree':m['tree'],'focus':m['scope'],'arrival':arrival,'sources':sources,
           'budget':{'max_steps':10,'max_branches':1,'max_events':10,'max_fanout':0,'model_calls':0},
           'status':'supplied case review; shared registration is separately recorded on week-one-state'}
    nodes=[
        ('ROOT',{'name':m['title']}),
        ('ARRIVAL',{'arrival':arrival,'language_glance':{'languages':['English'],'basis':'participant_supplied',
            'issuing_office':'Richmond public records and separately attributed public summaries','surface_kind':'mixed',
            'source_refs':refs,'note':'No resident communication or current operator delivery observed.'}}),
        ('EPIST',{'prompt':m['question'],'starting_state':'Historical documents plus an unverified current cost-barrier lead.',
            'dimensions':safeguards.dimensions(s)}),
        ('FUNC',{'task':m['scope'],'function':'Trace community-created capacity through controlled gates to usable shelter.',
            'gates':m['gates'],'cost_observations':m['costs'],
            'relay_journal_ref':str(CASE/'relay-journal.json'),
            'relays':[{**{k:r[k] for k in ('relay_id','kind','from_actor','to_actor','payload','stages')},
                       'evidence_ids':[e['evidence_id'] for e in r['evidence']]} for r in c['relays']]}),
        ('MIRROR',{'comparisons':[{'explanation':x['claim'],'queries':[],'answers':[{'evidence_ids':x['evidence_ids']}]} for x in s['ordinary_explanations']],
            'contrary_evidence':s['contrary_evidence'],'information_lineage':{'parent_answer_visible':True,'source_refs':refs,
            'parent_output_refs':[str(CASE/'safeguard-journal.json'),str(CASE/'relay-journal.json')],
            'criteria_refs':[str(safeguards.SCHEMA),str(relays.SCHEMA)],'api_record_refs':m['api_record_refs'],'test_origin':'inherited'}}),
        ('CROSS',{'inherited':[{'ref':r,'status':'Retained source; reuse is not independent corroboration.'} for r in refs],
            'independent':[],'bridge':[{'question':m['next_test'],'status':'proposed; no request sent'}]}),
        ('RESID',{'summary':' '.join(c['unknowns']),'next_test':s['next_test'],
            'predicates':{'consequential':True,'distinct_functions':False,'language_exception':None}}),
        ('MEAN',{'summary':m['meaning'],'dimensions':safeguards.dimensions(s)}),
        ('EXIT',{'kind':'question','summary':m['next_test']}),
        ('RETURN',{'new_arrival':None,'reason':m['stop_condition']})]
    doc=garden.new_document(tree_config(root),start,{'questions':{m['question_id']:{'epoch':m['question_epoch']}}})
    for i,(node,out) in enumerate(nodes):
        doc=garden.apply_event(doc,{'event_id':m['case_id']+'-STEP-'+str(i+1),'expected_revision':i,
            'actor':actor,'branch_id':'B0','kind':'step','node':node,'output':out},m['recorded_at'])
    doc=garden.replay(doc)
    require(doc['state']['used']=={'steps':10,'branches':1,'model_calls':0}
            and doc['state']['branches']['B0']['status']=='resting','Unexpected Garden execution')
    return doc


def markdown(state,resolved):
    m=state['meta'];s=state['safeguards']['safeguards'][m['safeguard_id']]
    c=state['relays']['cases'][m['case_id']]
    esc=lambda v:str(v).replace('|','\\|').replace('\n',' ')
    lines=['# '+m['title'],'','**'+m['question']+'**','',m['meaning'],'',
        'Evidence cutoff: '+m['evidence_cutoff']+'. Historical requirements are dated; current replacement price and usable capacity remain unverified.','',
        '| Gate | Who controls it in the inspected records | Requirement / limit | Community alternative to test |',
        '| --- | --- | --- | --- |']
    for g in m['gates']:
        lines.append('| '+' | '.join(esc(g[k]) for k in ('gate','controller','requirement','alternative'))+' |')
    lines+=['','## Money: keep scope and period attached','','| Amount | Record status | Period / scope | Source and limit |','| --- | --- | --- | --- |']
    for x in m['costs']:
        lines.append('| $'+format(Decimal(x['amount_usd']),',.2f')+' | '+x['status']+' | '+esc(x['period']+'; '+x['scope'])+' | '+esc(', '.join(x['source_refs'])+' '+x['locator']+'; '+x['limits'])+' |')
    lines+=['','No figure is converted into manager salary, profit, payment, annual cost or cost per occupied bed. The records do not provide a verified current denominator.','',
        '## Safeguards in reality','','| Dimension | Status | Assessment |','| --- | --- | --- |']
    for label,a in [('Formal',s['formal']),*[(k,v) for k,v in s['operational'].items()],('Effectiveness',s['effectiveness']),('Failure',s['failure'])]:
        lines.append('| '+label+' | '+a['status']+' | '+esc(a['claim'])+' |')
    lines+=['','## Contrary evidence and ordinary explanations','']+['- '+x['claim'] for x in s['contrary_evidence']+s['ordinary_explanations']]
    lines+=['','## Where knowledge stops','']+['- '+x for x in c['unknowns']]
    lines+=['','**One next question:** '+m['next_test'],'','## Retained sources','','| Source | Date / limits |','| --- | --- |']
    for ref in sorted(safeguards.source_refs(s)):
        r=resolved[ref]['record']
        lines.append('| ['+ref+': '+esc(r['title'])+']('+r['url']+') | '+str(r['publication_date'])+'; '+esc(r['limitations'])+' |')
    lines+=['','The ten-node Garden pass uses the reviewed supplemental COMMUNITY-CAPACITY tree. The base dispatcher and prior cases are unchanged. The Meaning Tower packet is available to play; no user play is invented. The advisory Governor input requires an actual response before it can be called reviewed.','',
        'Offline replay: `python scripts/community_capacity.py check`. This checks retained bytes and supplied assessments, not source truth or current conditions.','']
    return '\n'.join(lines).encode()


def outputs(root=ROOT):
    state,resolved=replay(root)
    return {'STATE.json':cycle.encoded(state),'GARDEN.json':cycle.encoded(garden_pass(root,state,resolved)),
            'COMMUNITY_CAPACITY.md':markdown(state,resolved)}


def build(root=ROOT,check=False):
    for name,data in outputs(root).items():
        path=Path(root)/OUTPUT/name
        if check:
            require(path.is_file() and path.read_bytes()==data,'Saved output differs: '+name)
        else:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['build','check'])
    try:
        build(check=p.parse_args().command=='check')
    except (ValueError,cycle.CycleError,KeyError,TypeError,OSError) as exc:
        print('INVALID: '+str(exc),file=sys.stderr);sys.exit(1)
    print('PASS: one community-capacity case; shared safeguard/relay history; 10 Garden nodes; zero model calls')
