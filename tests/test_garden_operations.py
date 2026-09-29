import copy
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import api_records
import cycle
import free_provider as fp
import garden_acceptance as acceptance
import garden_operations as ops
import garden_runtime as garden
import week_one

NOW='2026-09-29T10:00:00+00:00'


class Response(io.BytesIO):
    status=200
    headers={'Content-Type':'application/json'}


class OperationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        for path in [cycle.CANONICAL,'config/garden.json','config/garden-traversal.json','config/garden-operations.json',
                     'config/week-one.json','operations/questions.json','handoffs/week_one_governor/2026-09-25.json']:
            dest=self.root/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,dest)
        self.time=patch.object(cycle,'now',return_value=NOW);self.time.start();self.addCleanup(self.time.stop)
        self.env=patch.dict(os.environ,{'OPENROUTER_API_KEY':'fixture-key-never-publish','WEEK_ONE_PERSIST':'0'})
        self.env.start();self.addCleanup(self.env.stop)
        self.scenario=cycle.read_json(ROOT/'examples/garden-traversal/q18-scenario.json')
        self.packet={**self.scenario['start'],'run_id':'OPS-TEST','operations':True}
        garden.start(self.root,self.packet)
        self.spec={'operation_id':'OP-1','branch_id':'B0','reason':'Test a consequential source gap',
                   'task':'Find the missing operating denominator','role':'crosscheck','method':'lineage_inventory',
                   'permissions':{'model':False,'public_http':False},'budget':{'model_posts':0,'source_gets':0},
                   'stop_condition':'One bounded return','context':{'note':'Exact supplied context'}}
        self.calls=[]

    def load(self): return cycle.read_json(garden.path_for(self.root,'OPS-TEST'))

    def model(self):
        self.spec.update(method='cognition',permissions={'model':True,'public_http':False},budget={'model_posts':1,'source_gets':0})

    def prepare(self): return ops.prepare(self.root,'OPS-TEST',self.spec,now=NOW)

    def response(self, value=None, cost=0):
        if value is None:
            req=ops.read(self.root,ops.path_for(self.spec['operation_id']))['request']
            value=ops.deterministic(req)
        return {'id':'gen-fixture','model':fp.MODEL,'usage':{'cost':cost,'is_byok':False,'prompt_tokens':12,'completion_tokens':20},
                'openrouter_metadata':{'endpoints':{'available':[{'selected':True,'provider':'Nvidia'}]}},
                'choices':[{'finish_reason':'stop','message':{'content':json.dumps(value)}}]}

    def transport(self, result=None, crash=False):
        test=self
        class Opener:
            def open(self,request,timeout):
                test.calls.append((request.get_method(),request.full_url))
                if request.full_url == fp.CATALOG:
                    value={'data':{'id':fp.MODEL,'endpoints':[{'model_id':fp.MODEL,'provider_name':'Nvidia','tag':'nvidia',
                        'status':0,'pricing':{'prompt':'0','completion':'0'},'supported_parameters':[]}]}}
                elif request.full_url.endswith('/key'):
                    value={'data':{'is_management_key':False}}
                elif request.full_url==fp.ENDPOINT:
                    if crash: raise KeyboardInterrupt('Power loss during inference')
                    value=result or test.response()
                else:
                    return Response(b'<html>Delivery milestone; no verified voyage series.</html>')
                return Response(json.dumps(value).encode())
        return patch('urllib.request.build_opener',return_value=Opener())

    def test_any_node_needs_reason_and_exact_context(self):
        for stage in garden.NODES:
            with self.subTest(stage=stage):
                spec={**self.spec,'operation_id':'OP-'+stage,'reason':''}
                with self.assertRaisesRegex(cycle.CycleError,'reason'): ops.prepare(self.root,'OPS-TEST',spec)
                spec['reason']='Inspect '+stage
                record=ops.prepare(self.root,'OPS-TEST',spec)
                self.assertEqual(record['request']['anchor']['node'],stage)
                self.assertEqual(record['request']['exposed_context']['task_context'],self.spec['context'])
                ops.execute(self.root,spec['operation_id'])
                output=next(c['output'] for c in self.scenario['commands'] if c.get('node')==stage)
                doc=self.load()
                garden.submit(self.root,'OPS-TEST',ops.command(doc,'B0','STEP-'+stage,'step',node=stage,output=output))
                # Separate test config grants ten operation attachments, no model capacity.
                if stage=='ROOT':
                    cfg=ops.policy(self.root);cfg['limits']['max_operations']=16
                    ops.write(self.root,'config/garden-operations.json',cfg)
                    # New linked run for remaining stages uses one consistent snapshot.
                    self.patch_limit_for_fixture(cfg)
        self.assertEqual(garden.replay(self.load()),self.load())

    def patch_limit_for_fixture(self,cfg):
        # Rebuild this fixture using the same commands under the larger starting budget.
        old=self.load(); config=old['initial']['config'];config['operations']=cfg
        doc=garden.new_document(config,old['initial']['packet'],old['initial']['registry'])
        for event in old['events']: doc=garden.apply_event(doc,event['command'],event['recorded_at'])
        garden.save(self.root,doc)

    def test_contextual_role_language_history_and_first_use(self):
        self.model();record=self.prepare()
        rows=record['candidates'];states={c['id']:c['state'] for c in rows}
        self.assertEqual(record['selected'],'or-nvidia')
        self.assertEqual(states['gemini'],'requires_first_use_approval')
        request=copy.deepcopy(record['request']);request['anchor']['tree']='LANGUAGE';request['role']='parallax'
        request['exposed_context']['sources'][0]['languages']=['sw']
        rows,_=ops.candidates(self.root,request)
        nvidia=next(c for c in rows if c['id']=='or-nvidia')
        self.assertIn('contextual role parallax',nvidia['reasons'][0]);self.assertIn('sw',nvidia['reasons'][2])
        self.assertEqual(nvidia['language_fit'],'unverified')
        request.update(peculiar=True)
        rows,selected=ops.candidates(self.root,request);self.assertIsNone(selected)
        self.assertEqual(next(c['state'] for c in rows if c['id']=='or-nvidia'),'requires_first_use_approval')

    def test_cooldown_no_eligible_returns_to_chat_and_digest(self):
        self.model();state=week_one.manifest(self.root);state['cooldown_until']='2026-09-30T00:00:00+00:00'
        state['cooldown_category']='audit_pending'
        ops.write(self.root,week_one.BASE/'run-manifest.json',state)
        self.prepare();result=ops.execute(self.root,'OP-1')
        self.assertEqual(result['outcome']['status'],'deferred')
        self.assertEqual(self.load()['state']['operation_requests']['OP-1']['status'],'returned')
        queue=ops.read(self.root,ops.THRESHOLD/'unresolved.json')
        self.assertEqual(queue['capacity_mode'],'luna')
        self.assertEqual(queue['items'][0]['recipients'],['Chat Aiden','Digest Aiden'])
        handoff=ops.read(self.root,Path(queue['items'][0]['handoff']['path']))
        self.assertEqual(handoff['schema_version'],'bee-handoff-1')
        self.assertEqual(handoff['return_path']['on_failure'],['Chat Aiden','Digest Aiden'])
        capacity=ops.read(self.root,ops.THRESHOLD/'capacity.json')
        self.assertEqual(capacity['mode'],'luna')
        self.assertEqual(capacity['bandwidth_wait_category'],'audit_pending')
        api=ops.read(self.root,api_records.THRESHOLD/'runs'/(ops.api_id('OP-1')+'.json'))
        self.assertEqual(api['coverage'],'no_http_exchange')

    def test_non_bandwidth_failure_does_not_create_global_wait(self):
        self.model();self.prepare()
        with patch.object(fp,'call',side_effect=fp.ProviderFailure('model_unavailable','route missing',cooldown_hours=12)):
            result=ops.execute(self.root,'OP-1')
        self.assertEqual(result['outcome']['category'],'model_unavailable')
        state=week_one.manifest(self.root)
        self.assertIsNone(state.get('cooldown_until'))
        self.assertIsNone(week_one.bandwidth_wait_category(state))

    def test_approved_model_full_record_and_shared_budget(self):
        self.model();self.prepare()
        with self.transport(): result=ops.execute(self.root,'OP-1')
        self.assertEqual(result['outcome']['provider_receipt']['total_cost'],0)
        self.assertEqual(result['outcome']['provider_posts'],1)
        self.assertEqual(len(result['outcome']['api_records']),3)
        req=ops.read(self.root,week_one.run_path(ops.api_id('OP-1'),'request.json'))
        fp.validate_payload(req['settings'])
        self.assertFalse(req['settings']['provider']['allow_fallbacks']);self.assertEqual(req['settings']['provider']['ignore'],['groq'])
        text=''.join(p.read_text() for p in self.root.rglob('*.json'))
        self.assertNotIn('fixture-key-never-publish',text)
        before=self.calls[:];ops.execute(self.root,'OP-1');self.assertEqual(before,self.calls)
        manifest=week_one.manifest(self.root);reservation=manifest['garden_operations']['OP-1']
        self.assertEqual((reservation['post_reserved'],reservation['status']),(1,'complete'))
        self.assertEqual(self.load()['state']['used']['model_calls'],1)
        self.assertEqual(garden.replay(self.load()),self.load())

    def test_paid_or_groq_route_never_selected(self):
        self.model();record=self.prepare()
        cfg=ops.policy(self.root)
        for denied in ({'upstream':'groq'},{'paid':True}):
            bad=copy.deepcopy(cfg);bad['executors'][2].update(denied)
            ops.write(self.root,'config/garden-operations.json',bad)
            rows,selected=ops.candidates(self.root,record['request']);self.assertIsNone(selected)
            self.assertEqual(next(c['state'] for c in rows if c['id']=='or-nvidia'),'prohibited')

    def test_positive_cost_closes_shared_window(self):
        self.model();self.prepare()
        with self.transport(self.response(cost=.02)): result=ops.execute(self.root,'OP-1')
        self.assertEqual(result['outcome']['category'],'spend_detected')
        self.assertTrue(week_one.manifest(self.root)['closed'])
        self.assertEqual(ops.provider_gate(self.root),'window_complete')

    def test_worker_cannot_promote_output_or_rewrite_authority(self):
        self.model();record=self.prepare();value=ops.deterministic(record['request'])
        value['independent']=['model-output'];value['permissions']={'paid':True}
        with self.transport(self.response(value)): result=ops.execute(self.root,'OP-1')
        self.assertEqual(result['outcome']['validation']['status'],'not_admitted')
        self.assertEqual(result['outcome']['provider_receipt']['total_cost'],0)
        self.assertNotIn('output',result['outcome'])
        self.assertEqual(self.load()['state']['sources'],{s['ref']:s for s in self.packet['sources']})

    def test_blinding_omits_parent_history_and_rejects_uncontrolled_context(self):
        self.spec['independence']={'blind_parent':True,'distinct_executor':True}
        with self.assertRaisesRegex(cycle.CycleError,'Blind requests'):self.prepare()
        self.spec['context']={};record=self.prepare()
        self.assertNotIn('prior_node_outputs',record['request']['exposed_context'])
        self.assertFalse(record['request']['information_lineage']['parent_answer_visible'])
        self.assertNotIn('inherited_branch_lineage',record['prompt'])

    def test_pending_operation_holds_exact_node_and_return_is_idempotent(self):
        record=self.prepare();doc=self.load()
        with self.assertRaisesRegex(cycle.CycleError,'pending operation'):
            garden.submit(self.root,'OPS-TEST',ops.command(doc,'B0','MOVE-EARLY','step',node='ROOT',output={'name':'No'}))
        result=ops.execute(self.root,'OP-1');before=self.load()
        self.assertEqual(ops.execute(self.root,'OP-1'),result);self.assertEqual(before,self.load())
        with self.assertRaisesRegex(cycle.CycleError,'cannot replace'):
            ops.prepare(self.root,'OPS-TEST',{**self.spec,'task':'Change history'})

    def test_interrupted_provider_never_reposts_and_saved_generation_recovers(self):
        self.model();self.prepare()
        with self.transport(crash=True),self.assertRaises(KeyboardInterrupt):ops.execute(self.root,'OP-1')
        self.assertEqual(week_one.gate(week_one.catalog(self.root),week_one.manifest(self.root),week_one.clock()),'garden_operation_pending')
        response=self.response()
        ops.write(self.root,week_one.run_path(ops.api_id('OP-1'),'provider-response.json'),response)
        with patch.object(fp,'call',side_effect=AssertionError('No replacement inference')):
            result=ops.execute(self.root,'OP-1',recover=True)
        self.assertEqual(result['outcome']['status'],'unknown')
        self.assertEqual(sum(method=='POST' for method,url in self.calls),1)

    def test_recover_command_cannot_start_a_prepared_inference(self):
        self.model();self.prepare()
        with patch.object(fp,'call',side_effect=AssertionError('Recovery cannot initiate inference')):
            with self.assertRaisesRegex(cycle.CycleError,'no new inference'):
                ops.execute(self.root,'OP-1',recover=True)

    def test_interrupted_without_generation_preserves_uncertainty_and_brake(self):
        self.model();self.prepare()
        with self.transport(crash=True),self.assertRaises(KeyboardInterrupt):ops.execute(self.root,'OP-1')
        with patch.object(fp,'call',side_effect=AssertionError('No second POST')):
            result=ops.execute(self.root,'OP-1',recover=True)
        self.assertEqual(result['outcome']['status'],'error')
        self.assertEqual(week_one.manifest(self.root)['garden_operations']['OP-1']['status'],'uncertain')
        self.assertIsNotNone(week_one.manifest(self.root)['brake'])

    def test_return_recovers_after_outcome_saved_before_garden_commit(self):
        self.prepare()
        with patch.object(garden,'save',side_effect=OSError('Interrupted return write')):
            with self.assertRaises(OSError):ops.execute(self.root,'OP-1')
        result=ops.execute(self.root,'OP-1',recover=True)
        self.assertEqual(result['phase'],'returned')
        self.assertEqual(len([e for e in self.load()['events'] if e['command']['kind']=='operation_return']),1)

    def test_restart_repairs_shared_reservation_after_garden_return(self):
        self.model();self.prepare()
        original=week_one.write
        def interrupted(root,path,value):
            if path == week_one.BASE/'run-manifest.json' and value.get('garden_operations',{}).get('OP-1',{}).get('status') == 'complete':
                raise OSError('Power loss before shared reservation save')
            return original(root,path,value)
        with self.transport(),patch.object(week_one,'write',side_effect=interrupted),self.assertRaises(OSError):
            ops.execute(self.root,'OP-1')
        self.assertEqual(ops.read(self.root,ops.path_for('OP-1'))['phase'],'returned')
        self.assertEqual(week_one.manifest(self.root)['garden_operations']['OP-1']['status'],'executing')
        with patch.object(fp,'call',side_effect=AssertionError('No second inference')):
            result=ops.execute(self.root,'OP-1')
        self.assertTrue(result['finalized'])
        self.assertEqual(week_one.manifest(self.root)['garden_operations']['OP-1']['status'],'complete')
        self.assertEqual(len([e for e in self.load()['events'] if e['command']['kind']=='operation_return']),1)

    def test_missing_receipt_recovery_is_get_only_and_keeps_original_return(self):
        self.model();self.prepare()
        response=self.response();response['usage'].pop('cost')
        def pending(payload,checkpoint,**kwargs):
            checkpoint(response)
            raise fp.ProviderFailure('audit_pending','Saved generation needs receipt',cooldown_hours=1)
        with patch.object(fp,'call',side_effect=pending):first=ops.execute(self.root,'OP-1')
        original_return=copy.deepcopy(self.load()['state']['operation_requests']['OP-1']['result'])
        state=week_one.manifest(self.root);state['cooldown_until']=None
        ops.write(self.root,week_one.BASE/'run-manifest.json',state)
        result={'result':ops.deterministic(first['request']),'receipt':{'id':'gen-fixture','total_cost':0,'provider_name':'Nvidia'}}
        with patch.object(fp,'call',side_effect=AssertionError('No replacement POST')),patch.object(fp,'complete',return_value=result) as recover:
            recovered=ops.execute(self.root,'OP-1',recover=True)
        recover.assert_called_once()
        self.assertEqual(recovered['outcome'],first['outcome'])
        self.assertEqual(self.load()['state']['operation_requests']['OP-1']['result'],original_return)
        self.assertEqual(len(self.load()['state']['operation_requests']['OP-1']['audits']),1)
        self.assertEqual(week_one.manifest(self.root)['garden_operations']['OP-1']['status'],'complete')

    def birth(self):
        return {'why_parent_cannot_answer':'Missing operating data','question':'One loaded-service record?',
                'tree':'PRODUCTION','role':'collector','need':'q18-ccs-delivery',
                'budget':{'operations':1,'model_posts':0,'source_gets':1},'stop_condition':'One GET then return'}

    def test_child_executes_returns_and_cannot_duplicate_or_recurse(self):
        self.spec['on_unknown_birth']=self.birth();self.prepare();ops.execute(self.root,'OP-1')
        with self.transport(): child=ops.spawn(self.root,'OP-1')
        self.assertEqual(child['outcome']['status'],'unknown')
        self.assertEqual(self.load()['state']['branches']['B1']['status'],'resting')
        before=self.calls[:];ops.spawn(self.root,'OP-1');self.assertEqual(self.calls,before)
        doc=self.load();event=ops.command(doc,'B0','DUPLICATE-BIRTH','birth',birth=self.birth())
        doc=garden.submit(self.root,'OPS-TEST',event);self.assertEqual(doc['events'][-1]['decision']['reason'],'duplicate')
        # Depth check uses a ready child fixture, preserving the pure reducer's branch budget.
        document=copy.deepcopy(doc);document['state']['branches']['B1']['status']='ready'
        decision=garden.operation_event(document['state'],document['state']['branches']['B1'],
            {'kind':'birth','event_id':'DEEP','birth':{**self.birth(),'question':'Deeper question'}},document['initial']['config'])
        self.assertEqual(decision['reason'],'depth_budget')
        self.assertEqual(garden.replay(self.load()),self.load())

    def test_no_child_capacity_records_both_recipients(self):
        cfg=ops.policy(self.root);cfg['limits']['max_child_work']=0
        ops.write(self.root,'config/garden-operations.json',cfg);self.patch_limit_for_fixture(cfg)
        self.spec['on_unknown_birth']=self.birth();self.prepare();ops.execute(self.root,'OP-1')
        result=ops.spawn(self.root,'OP-1');self.assertEqual(result['reason'],'child_budget')
        self.assertEqual(result['recipients'],['Chat Aiden','Digest Aiden'])

    def test_child_return_targets_original_visit_after_parent_reentry(self):
        doc=self.load()
        garden.submit(self.root,'OPS-TEST',ops.command(doc,'B0','BIRTH-1','birth',birth=self.birth()))
        spec={**self.spec,'operation_id':'CHILD-1','branch_id':'B1','method':'public_source','role':'collector',
              'source_key':'q18-ccs-delivery','permissions':{'model':False,'public_http':True},'budget':{'model_posts':0,'source_gets':1}}
        ops.prepare(self.root,'OPS-TEST',spec)
        with self.transport():ops.execute(self.root,'CHILD-1')
        for stage in garden.NODES:
            output=next(c['output'] for c in self.scenario['commands'] if c.get('node')==stage)
            garden.submit(self.root,'OPS-TEST',ops.command(self.load(),'B0','ADVANCE-'+stage,'step',node=stage,output=output))
        arrival=copy.deepcopy(self.packet['arrival']);arrival.update(id='NEW-ARRIVAL',payload={'new_material':'A later distinct packet'})
        garden.submit(self.root,'OPS-TEST',ops.command(self.load(),'B0','REENTER','arrive',new_arrival=arrival,reason='New material'))
        garden.submit(self.root,'OPS-TEST',ops.command(self.load(),'B0','CHILD-BACK','child_return',child_branch='B1',operation_id='CHILD-1'))
        visits=self.load()['state']['branches']['B0']['visits']
        self.assertEqual(len(visits),2);self.assertEqual(len(visits[0]['child_returns']),1)
        self.assertNotIn('child_returns',visits[1])
        self.assertEqual(garden.replay(self.load()),self.load())

    def test_child_cannot_expand_its_budget_or_strand_its_return(self):
        doc=self.load();config=doc['initial']['config'];config['limits']['max_events']=5
        garden.save(self.root,garden.new_document(config,doc['initial']['packet'],doc['initial']['registry']))
        garden.submit(self.root,'OPS-TEST',ops.command(self.load(),'B0','BIRTH-1','birth',birth=self.birth()))
        garden.submit(self.root,'OPS-TEST',ops.command(self.load(),'B0','STEP-ROOT','step',node='ROOT',output={'name':'Parent may continue'}))
        output=next(c['output'] for c in self.scenario['commands'] if c.get('node')=='ARRIVAL')
        with self.assertRaisesRegex(cycle.CycleError,'capacity'):
            garden.submit(self.root,'OPS-TEST',ops.command(self.load(),'B0','TOO-FAR','step',node='ARRIVAL',output=output))
        self.model()
        with self.assertRaisesRegex(cycle.CycleError,'source-only'):
            ops.prepare(self.root,'OPS-TEST',{**self.spec,'branch_id':'B1'})
        child={**self.spec,'branch_id':'B1','method':'public_source','source_key':'q18-ccs-delivery','role':'collector',
               'permissions':{'model':False,'public_http':True},'budget':{'model_posts':0,'source_gets':1}}
        ops.prepare(self.root,'OPS-TEST',child)
        with self.transport():ops.execute(self.root,'OP-1')
        garden.submit(self.root,'OPS-TEST',ops.command(self.load(),'B0','CHILD-BACK','child_return',child_branch='B1',operation_id='OP-1'))
        self.assertEqual(self.load()['state']['revision'],5)
        self.assertEqual(garden.replay(self.load()),self.load())

    def test_full_digest_hashes_and_formula_safe_projection(self):
        self.spec['task']='=SUM(1,2)';self.prepare();ops.execute(self.root,'OP-1')
        record=ops.read(self.root,ops.path_for('OP-1'));record['outcome']['summary']='=FORMULA()'
        ops.write(self.root,ops.path_for('OP-1'),record);ops.project(self.root)
        with (self.root/ops.THRESHOLD/'operations.csv').open() as f:
            self.assertEqual(next(csv.DictReader(f))['summary'],"'=FORMULA()")
        packet=ops.read(self.root,ops.THRESHOLD/'OP-1.json')
        for material in packet['materials']:
            self.assertEqual(material['sha256'],hashlib.sha256((self.root/material['path']).read_bytes()).hexdigest())

    def test_shared_daily_and_slot_limits_include_garden(self):
        state=week_one.manifest(self.root);state['garden_operations']={str(i):{'started_at':NOW,'slot':'20260929-AM',
            'post_reserved':1,'status':'complete'} for i in range(4)}
        ops.write(self.root,week_one.BASE/'run-manifest.json',state)
        self.assertEqual(ops.provider_gate(self.root),'daily_budget')
        state['garden_operations'].pop('3');state['garden_operations'].pop('2')
        ops.write(self.root,week_one.BASE/'run-manifest.json',state)
        self.assertEqual(ops.provider_gate(self.root),'slot_attempt_limit')

    def test_lower_start_budget_prevents_a_model_reservation(self):
        self.model()
        packet={**self.packet,'run_id':'NO-MODELS','budget':{'model_calls':0}}
        garden.start(self.root,packet)
        record=ops.prepare(self.root,'NO-MODELS',self.spec)
        self.assertIsNone(record['selected'])
        with patch.object(fp,'call',side_effect=AssertionError('No inference in a zero-model run')):
            result=ops.execute(self.root,'OP-1')
        self.assertEqual(result['outcome']['provider_posts'],0)
        self.assertEqual(result['outcome']['status'],'deferred')

    def test_q18_acceptance_runs_and_replays_without_modifying_old_example(self):
        before=hashlib.sha256((ROOT/'examples/garden-traversal/q18-scenario.json').read_bytes()).hexdigest()
        with self.transport(): report=acceptance.build(self.root)
        self.assertEqual(report['replay'],'identical');self.assertEqual(report['provider_posts'],1)
        self.assertEqual(report['child_status'],'unknown');self.assertEqual(report['source_gets'],1)
        oldcalls=self.calls[:]
        with self.transport(),patch.object(cycle,'now',return_value='2026-09-30T10:00:00+00:00'):
            again=acceptance.build(self.root)
        self.assertEqual(self.calls,oldcalls);self.assertEqual(again,report)
        self.assertEqual(before,hashlib.sha256((ROOT/'examples/garden-traversal/q18-scenario.json').read_bytes()).hexdigest())


if __name__=='__main__': unittest.main()
