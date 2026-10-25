"""Evidence-boundary tests for community capacity, funding custody and supplied replay."""
import copy
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import community_capacity as capacity
import continuity as shared
import cycle
import garden_runtime as garden
import governor_inbox
import reflections
import safeguards
import relays


class CommunityCapacityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state,cls.refs=capacity.replay()
        cls.sg=cls.state['safeguards']['safeguards']['SG-RICHMOND-OPERATING-GATES']
        cls.case=cls.state['relays']['cases']['RICHMOND-COMMUNITY-CAPACITY']

    def test_replay_is_offline_deterministic_and_rests(self):
        with patch('socket.create_connection',side_effect=AssertionError('Network during replay')):
            capacity.build(check=True)
            self.assertEqual(capacity.outputs(),capacity.outputs())
        doc=capacity.garden_pass(capacity.ROOT,self.state,self.refs)
        self.assertEqual(doc['state']['used'],{'steps':10,'branches':1,'model_calls':0})
        self.assertEqual(doc['state']['branches']['B0']['status'],'resting')

    def test_extension_cannot_replace_trees_or_change_base_rules(self):
        ext=shared.strict_json(capacity.ROOT/capacity.TREE)
        for change in (lambda d:d.update(tree_id='HOMELESSNESS'),lambda d:d.update(rules=[]),
                       lambda d:d.update(base_sha256='0'*64)):
            bad=copy.deepcopy(ext);change(bad)
            with self.assertRaises(shared.ContinuityError):capacity.tree_config(extension=bad)
        base=garden.load_config(capacity.ROOT);new=capacity.tree_config()
        for key in ('limits','rules','grammar','node_contracts','model_execution'):
            self.assertEqual(base[key],new[key])

    def test_historical_meaning_replay_does_not_follow_a_later_live_epoch(self):
        original=shared.strict_json
        def later_registry(path):
            value=original(path)
            if Path(path)==capacity.ROOT/'operations/questions.json':
                value['questions']['Q-MEANING-TRANSLATION-BOSS']['epoch']+=1
            return value
        with patch.object(shared,'strict_json',side_effect=later_registry):
            capacity.build(check=True)
        snapshot=original(capacity.ROOT/capacity.CASE/'meaning-question-snapshot.json')
        self.assertEqual(snapshot['registry']['questions']['Q-MEANING-TRANSLATION-BOSS']['epoch'],1)

    def test_draft_and_reported_cost_cannot_be_payment_or_executed_award(self):
        for index in (0,1,4):
            costs=copy.deepcopy(self.state['meta']['costs'])
            costs[index]['status']='observed_payment'
            with self.assertRaises(shared.ContinuityError):capacity.validate_costs(costs,self.refs)
        costs=copy.deepcopy(self.state['meta']['costs']);costs[1]['status']='executed_award'
        with self.assertRaisesRegex(shared.ContinuityError,'matching instrument'):
            capacity.validate_costs(costs,self.refs)

    def test_formal_requirements_and_old_operator_cannot_prove_effective_care(self):
        schema=shared.strict_json(capacity.ROOT/safeguards.SCHEMA)
        for key in ('people','procedures','authority'):
            s=copy.deepcopy(self.sg)
            s['operational'][key].update(status='observed',evidence_ids=['RT-PROVIDER-GATE','RT-SERVICES'])
            with self.subTest(key=key),self.assertRaisesRegex(shared.ContinuityError,'observed implementation'):
                safeguards.validate(s,schema,self.refs)
        s=copy.deepcopy(self.sg);s['effectiveness'].update(status='observed',evidence_ids=['RT-CITY-CONTROL'])
        with self.assertRaisesRegex(shared.ContinuityError,'dated harm/action/result'):
            safeguards.validate(s,schema,self.refs)

    def test_grant_requirement_is_not_received_money_or_delivered_shelter(self):
        schema=shared.strict_json(capacity.ROOT/relays.SCHEMA)
        for index,stage,status in ((0,'arrival','received'),(2,'outcome','continued')):
            c=copy.deepcopy(self.case)
            c['relays'][index]['stages'][stage].update(status=status,evidence_ids=['RT-GRANT-CUSTODY'])
            with self.subTest(stage=stage),self.assertRaisesRegex(shared.ContinuityError,'stage-specific evidence'):
                relays.validate(c,schema,self.refs)

    def test_reused_material_is_not_independent_corroboration(self):
        saved=capacity.garden_pass(capacity.ROOT,self.state,self.refs)
        initial=copy.deepcopy(saved['initial']);source=initial['packet']['sources'][0]
        source['independence_basis']='Another reader looked at it'
        doc=garden.new_document(initial['config'],initial['packet'],initial['registry'])
        # Recreate the first five nodes, then falsely promote an inherited source at CROSS.
        for event in saved['events'][:5]:
            doc=garden.apply_event(doc,event['command'],event['recorded_at'])
        command=copy.deepcopy(saved['events'][5]['command'])
        command['output']['independent']=[{'ref':source['ref']}]
        with self.assertRaisesRegex(cycle.CycleError,'not independent'):
            garden.apply_event(doc,command,saved['events'][5]['recorded_at'])

    def test_changed_retained_receipt_is_rejected_before_interpretation(self):
        pins=self.state['input_pins']
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for path in [*pins['sha256'],str(capacity.CASE/'inputs.json')]:
                target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(capacity.ROOT/path,target)
            source=next(p for p in pins['sha256'] if p.endswith('/api/0003.json'))
            with (root/source).open('ab') as f:f.write(b' ')
            with self.assertRaisesRegex(shared.ContinuityError,'Pinned input changed'):
                capacity.replay(root)

    def test_governor_import_is_idempotent_pending_and_has_no_decision(self):
        feed=self.state['meta']['governor_input']
        envelope=shared.strict_json(capacity.ROOT/feed)
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for path in [feed,*envelope['context_refs'],'operations/reflections/mailbox.json','Resilience_Cascade_STATE.json']:
                target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(capacity.ROOT/path,target)
            before=reflections.load(root)['decisions']
            one=governor_inbox.ingest(root);two=governor_inbox.ingest(root)
            self.assertFalse(one['errors']);self.assertFalse(two['errors'])
            a,b=one['entries'][0],two['entries'][0]
            self.assertEqual(a['reflection_id'],b['reflection_id'])
            self.assertEqual(b['status'],'pending');self.assertEqual(b['responses'],[])
            self.assertEqual(before,reflections.load(root)['decisions'])


if __name__=='__main__':unittest.main()
