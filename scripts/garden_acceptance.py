#!/usr/bin/env python3
"""One real Q18 operation run; idempotent, window/budget gated, no new provider firsts."""
import argparse
import copy
from pathlib import Path

import cycle
import garden_runtime as garden
import garden_operations as ops
import week_one

RUN = 'Q18-NERVOUS-SYSTEM-20260929'
COG = 'Q18-BOUNDED-COGNITION-20260929'
INVENTORY = 'Q18-LINEAGE-20260929'


def step(root, node, output):
    doc = garden.replay(cycle.read_json(garden.path_for(root,RUN)))
    eid = 'Q18-LIVE-'+node
    old = next((e for e in doc['events'] if e['command']['event_id']==eid),None)
    garden.submit(root,RUN,old['command'] if old else ops.command(doc,'B0',eid,'step',node=node,output=output))


def build(root):
    root=Path(root)
    existing=ops.read(root,ops.THRESHOLD/'Q18-acceptance.json')
    if existing:
        document=garden.replay(cycle.read_json(garden.path_for(root,RUN)))
        initial=document['initial']
        checkpoint=garden.new_document(initial['config'],initial['packet'],initial['registry'])
        for event in document['events'][:existing['event_count']]:
            checkpoint=garden.apply_event(checkpoint,event['command'],event['recorded_at'])
        garden.require(checkpoint['state_sha256'] == existing['state_sha256'], 'Acceptance checkpoint changed')
        ops.project(root)
        return existing
    q=ops.read(root,'operations/questions.json')['questions']['Q-RESEARCH-Q18']
    inherited=ops.read(root,'handoffs/week_one_governor/2026-09-25.json')
    sources=[{'ref':'handoffs/week_one_governor/2026-09-25.json','lineage_id':'Q18-STAGED-20260925',
              'kind':'context','status':'Attributed historical provisional packet; not newly verified'}]
    sources += [{'ref':s['source_id'],'lineage_id':'CCS-'+s['url'].split('id=')[-1], 'kind':'context',
                 'languages':['zh'],'publication_metadata_basis':'inherited packet; not language detection',
                 'inherited_source_metadata':s} for s in inherited['source_ledger']]
    packet={'run_id':RUN,'question_id':q['question_id'],'epoch':q['epoch'],'actor':ops.ACTOR,'tree':'INIT',
            'operations':True,'focus':q['question'],
            'arrival':{'id':'Q18-NERVES-ARRIVAL-1','from':'examples/garden-traversal/worked/operations/garden/runs/Q18-SUPPLIED-TRAVERSAL-20260928.json',
                       'to':'INIT:ROOT-0001','payload':{'kind':'linked_operational_followup','question':q['question'],
                       'old_example_is_unchanged':True,'source_packet':'handoffs/week_one_governor/2026-09-25.json'}},'sources':sources}
    doc=garden.start(root,packet)
    step(root,'ROOT',{'name':'Q18: delivered hardware to dependable freight'})
    step(root,'ARRIVAL',{'arrival':packet['arrival'],'language_glance':{'languages':['zh'],'issuing_office':'China Classification Society',
        'basis':'participant_supplied','surface_kind':'summary','source_refs':[s['ref'] for s in sources],
        'note':'Chinese publication metadata inherited from the saved packet; English summary exposed.'}})
    step(root,'EPIST',{'prompt':q['question'],'starting_state':'UNKNOWN: staged delivery findings lack a validated loaded-voyage series.'})
    step(root,'FUNC',{'task':'Inspect the delivery-to-service inference and seek one bounded source return.',
                      'function':'Dependable freight substituting a diesel function; no empirical admission.'})
    common={'branch_id':'B0','reason':'Q18 has no admitted answer; inherited delivery claims need an operating-evidence test.',
            'task':'Specify one ordinary control and one narrow test distinguishing vessel delivery from dependable freight service.',
            'role':'crosscheck','stop_condition':'One structured return, or explicit defer/UNKNOWN; no inference retry.',
            'context':{'inherited_summary':inherited['answer']['summary'],'inherited_tests':inherited['answer']['tests']}}
    ops.prepare(root,RUN,{**common,'operation_id':COG,'method':'cognition','permissions':{'model':True,'public_http':False},
                          'budget':{'model_posts':1,'source_gets':0}})
    cognition=ops.execute(root,COG)
    birth={'why_parent_cannot_answer':'Inherited construction/delivery reporting supplies no validated voyage-performance series.',
           'question':'Does the saved CCS Ningyuan Dianpeng delivery surface supply a dated completed-freight record?',
           'tree':'PRODUCTION','role':'collector','need':'q18-ccs-delivery',
           'budget':{'operations':1,'model_posts':0,'source_gets':1},
           'stop_condition':'One public GET; retain full response and return UNKNOWN unless separately reviewed operating measures exist.'}
    ops.prepare(root,RUN,{**common,'operation_id':INVENTORY,'method':'lineage_inventory',
                          'permissions':{'model':False,'public_http':False},'budget':{'model_posts':0,'source_gets':0},'on_unknown_birth':birth})
    inventory=ops.execute(root,INVENTORY)
    outcome=cognition['outcome']; refs=[s['ref'] for s in sources]
    step(root,'MIRROR',{'comparisons':[{'explanation':outcome['summary'],'queries':[{'text':common['task'],'status':outcome['status']}],
                                      'answers':[{'operation_id':COG,'status':outcome['status'],'independent_evidence':False}]}],
        'information_lineage':{'parent_answer_visible':True,'source_refs':refs,'parent_output_refs':['examples/garden/q18-pass.json'],
            'criteria_refs':['handoffs/chat_aiden/2026-09-29_nervous-system-work-request/WORK_AIDEN_PRIMARY.md'],
            'api_record_refs':outcome.get('api_records',[]),'test_origin':'inherited'}})
    step(root,'CROSS',{'inherited':refs,'independent':[], 'bridge':[{'question':common['task'],
        'status':'Attributed operation return; no independent operating evidence admitted','source_refs':refs}]})
    step(root,'RESID',{'summary':'Operating reliability remains unknown; a bounded child may inspect one inherited public surface.',
                       'predicates':{'consequential':True,'distinct_functions':True,'language_exception':None}})
    child=ops.spawn(root,INVENTORY)
    step(root,'MEAN',{'summary':'Preserve the engineering milestone while keeping usable freight service unproven.'})
    step(root,'EXIT',{'kind':'question','summary':'UNKNOWN retained for Chat Aiden and Digest Aiden with complete operation materials.'})
    step(root,'RETURN',{'reason':'Bounded acceptance run complete; no new material warrants another pass.'})
    document=garden.replay(cycle.read_json(garden.path_for(root,RUN)))
    report={'schema_version':'garden-acceptance-1','run_id':RUN,'question_id':q['question_id'],'epoch':q['epoch'],
            'state_sha256':document['state_sha256'],'event_count':len(document['events']),
            'replay':'identical','cognition_status':outcome['status'],
            'cognition_executor':cognition['selected'],'provider_receipt':outcome.get('provider_receipt'),
            'provider_posts':outcome.get('provider_posts',0),'inventory_status':inventory['outcome']['status'],
            'child_status':(child or {}).get('outcome',{}).get('status',(child or {}).get('status')),
            'source_gets':sum(r.get('source_reserved',0) for r in ops.records(root) if r['request']['anchor']['run_id']==RUN),
            'empirical_result':'UNKNOWN; no validated loaded-service/uptime series admitted.',
            'supplied_parts':['Q18 framing','MIRROR/CROSS/RESID interpretation and conservative continuation policy'],
            'automatic_parts':['contextual candidates','recorded operation execution/return','bounded child Collector','digestion projection','replay'],
            'finished_at':cycle.now()}
    ops.write(root,ops.THRESHOLD/'Q18-acceptance.json',report)
    ops.project(root)
    week_one.durable(root)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=p.parse_args()
    import json
    print(json.dumps(build(args.root),indent=2))
