import copy
import csv
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import cycle
import garden_example
import garden_runtime as garden

ROOT = Path(__file__).resolve().parents[1]


class TraversalTests(unittest.TestCase):
    def setUp(self):
        self.config = garden.load_config(ROOT)
        self.scenario = cycle.read_json(ROOT / 'examples/garden-traversal/q18-scenario.json')
        self.packet = copy.deepcopy(self.scenario['start'])
        self.registry = self.scenario['question_snapshot']
        self.document = garden.new_document(self.config, self.packet, self.registry)
        self.outputs = {c['node']:copy.deepcopy(c['output']) for c in self.scenario['commands']
                        if c['kind'] == 'step' and c['branch_id'] == 'B0'}

    def command(self, kind, branch='B0', **fields):
        return {'event_id':f"TEST-{self.document['state']['revision']}",
                'expected_revision':self.document['state']['revision'], 'actor':self.packet['actor'],
                'branch_id':branch, 'kind':kind, **fields}

    def apply(self, kind, branch='B0', **fields):
        self.document = garden.apply_event(self.document, self.command(kind, branch, **fields), 'fixture')
        return self.document['state']

    def advance(self, stop='RESID', branch='B0'):
        while True:
            stage = garden.node(self.document['state']['branches'][branch])
            output = copy.deepcopy(self.outputs[stage])
            if stage == 'ARRIVAL':
                output['arrival'] = garden.current(self.document['state']['branches'][branch])['arrival']
            self.apply('step', branch, node=stage, output=output)
            if stage == stop:
                break

    def route(self, action='CLONE', targets=('PRODUCTION',), rule='DOMAIN-BRANCH'):
        return self.apply('route', rule_id=rule, action=action,
                          targets=[{'tree':t,'focus':f'Inspect {t}','reason':'Distinct question'} for t in targets],
                          review={'actor':self.packet['actor'],'reference':'test review','decision':'approved'})

    def new_arrival(self, number=2):
        arrival = copy.deepcopy(garden.current(self.document['state']['branches']['B0'])['arrival'])
        arrival.update(id=f'NEW-{number}', payload={'kind':'supplied_fixture','revision':number})
        return arrival

    def test_replay_pause_resume_and_idempotent_retry(self):
        self.advance('MIRROR')
        self.apply('rest', reason='Supplied output is pending')
        saved = copy.deepcopy(self.document)
        self.assertEqual(garden.replay(saved), saved)
        self.apply('resume', reason='Output is now supplied')
        command = self.command('step', node='CROSS', output=self.outputs['CROSS'])
        self.document = garden.apply_event(self.document, command, 'fixture')
        self.assertEqual(garden.apply_event(self.document, command), self.document)
        self.assertEqual(len(self.document['events']), 8)
        self.assertEqual(saved['state']['branches']['B0']['status'], 'resting')
        self.assertEqual(garden.replay(self.document), self.document)

    def test_stale_writer_and_changed_event_id_cannot_overwrite_history(self):
        command = self.command('step', node='ROOT', output=self.outputs['ROOT'])
        self.document = garden.apply_event(self.document, command, 'fixture')
        with self.assertRaisesRegex(cycle.CycleError, 'Stale revision'):
            garden.apply_event(self.document, {**command, 'event_id':'OTHER'})
        with self.assertRaisesRegex(cycle.CycleError, 'cannot replace'):
            garden.apply_event(self.document, {**command, 'output':{'name':'Rewritten'}})

    def test_replay_detects_changed_material_state_and_config(self):
        self.advance('CROSS')
        for mutation in ('state','command','config'):
            changed = copy.deepcopy(self.document)
            if mutation == 'state': changed['state']['branches']['B0']['focus'] = 'Changed'
            elif mutation == 'command': changed['events'][0]['command']['output']['name'] = 'Changed'
            else: changed['initial']['config']['model_execution'] = True
            with self.subTest(mutation=mutation), self.assertRaises(cycle.CycleError):
                garden.replay(changed)

    def test_node_order_and_contracts_are_enforced_without_partial_write(self):
        original = copy.deepcopy(self.document)
        with self.assertRaisesRegex(cycle.CycleError, 'current node'):
            self.apply('step', node='EXIT', output=self.outputs['EXIT'])
        self.assertEqual(original, self.document)
        for stage in garden.NODES:
            before = copy.deepcopy(self.document)
            with self.subTest(stage=stage), self.assertRaises(cycle.CycleError):
                self.apply('step', node=stage, output={})
            self.assertEqual(before, self.document)
            self.apply('step', node=stage, output=self.outputs[stage])

    def test_clone_preserves_parent_question_and_actual_information_lineage(self):
        self.advance()
        parent = copy.deepcopy(self.document['state']['branches']['B0'])
        state = self.route()
        child = state['branches']['B1']
        self.assertEqual(state['branches']['B0'], parent)
        self.assertEqual((child['question_id'], child['epoch']), (parent['question_id'], parent['epoch']))
        self.assertEqual(child['lineage']['source_refs'], parent['lineage']['source_refs'])
        self.assertFalse(child['lineage']['independent_evidence'])
        self.assertEqual(child['lineage']['originating_residual'], self.outputs['RESID'])
        self.assertEqual(garden.current(child)['arrival']['origin'], self.packet['arrival'])
        self.assertEqual(garden.current(child)['arrival']['parent_arrival_id'], self.packet['arrival']['id'])
        self.assertEqual(garden.node(child), 'ROOT')
        self.assertEqual(state['used']['model_calls'], 0)
        self.assertEqual(garden.replay(self.document), self.document)

    def test_move_relocates_same_branch_and_retains_prior_visit(self):
        self.advance()
        state = self.route(action='MOVE')
        branch = state['branches']['B0']
        self.assertEqual(state['used']['branches'], 1)
        self.assertEqual(len(branch['visits']), 2)
        self.assertEqual(branch['visits'][0]['status'], 'moved')
        self.assertEqual(garden.current(branch)['tree'], 'PRODUCTION')
        self.assertEqual(garden.node(branch), 'ROOT')

    def test_fanout_is_bounded_and_all_or_nothing(self):
        self.packet['budget'] = {'max_branches':2}
        self.document = garden.new_document(self.config, self.packet, self.registry)
        self.advance()
        state = self.route('FANOUT', ('PRODUCTION','ECONOMICS'))
        self.assertEqual(list(state['branches']), ['B0'])
        self.assertEqual(state['route_decisions'][-1]['status'], 'rest_budget')
        with self.assertRaises(cycle.CycleError): self.apply('resume', reason='Try again')
        with self.assertRaises(cycle.CycleError): self.apply('rest', reason='Replace budget brake')
        with self.assertRaises(cycle.CycleError): self.apply('arrive', new_arrival=self.new_arrival(), reason='New')

    def test_fanout_creates_distinct_siblings_without_mutating_parent(self):
        self.advance()
        parent = copy.deepcopy(self.document['state']['branches']['B0'])
        state = self.route('FANOUT', ('PRODUCTION','ECONOMICS'))
        self.assertEqual(state['branches']['B0'], parent)
        self.assertEqual([state['branches'][b]['parent_branch'] for b in ('B1','B2')], ['B0','B0'])
        self.assertEqual(state['used']['branches'], 3)
        self.assertEqual(garden.replay(self.document), self.document)

    def test_unknown_and_false_conditions_do_not_spawn_children(self):
        for value, status in ((None,'unknown'), (False,'condition_false')):
            self.document = garden.new_document(self.config, self.packet, self.registry)
            self.outputs['RESID']['predicates']['distinct_functions'] = value
            self.advance()
            state = self.route()
            self.assertEqual(list(state['branches']), ['B0'])
            self.assertEqual(state['route_decisions'][-1]['status'], status)
            self.assertEqual(state['branches']['B0']['status'], 'ready')

    def test_rephrasing_or_changing_clone_to_fanout_cannot_duplicate_route(self):
        self.advance()
        self.route()
        state = self.route('FANOUT', ('ECONOMICS','PRODUCTION'))
        self.assertEqual(list(state['branches']), ['B0','B1'])
        self.assertEqual(state['route_decisions'][-1]['status'], 'rest_loop')
        with self.assertRaises(cycle.CycleError): self.apply('resume', reason='Bypass loop')
        with self.assertRaises(cycle.CycleError): self.apply('rest', reason='Replace loop brake')

    def test_child_cannot_route_same_payload_back_into_parent_tree(self):
        self.advance()
        self.route(action='MOVE')
        self.advance()
        state = self.route(action='MOVE', targets=('INIT',))
        self.assertEqual(state['route_decisions'][-1]['status'], 'rest_loop')
        self.assertEqual(len(state['branches']['B0']['visits']), 2)

    def test_completed_branch_reenters_only_on_new_material(self):
        self.advance('RETURN')
        with self.assertRaises(cycle.CycleError): self.apply('resume', reason='Repeat old work')
        with self.assertRaises(cycle.CycleError): self.apply('rest', reason='Replace completion')
        unchanged = {**self.packet['arrival'], 'id':'ANOTHER-ID'}
        state = self.apply('arrive', new_arrival=unchanged, reason='Same payload')
        self.assertEqual(len(state['branches']['B0']['visits']), 1)
        new = self.new_arrival()
        state = self.apply('arrive', new_arrival=new, reason='New supplied material')
        branch = state['branches']['B0']
        self.assertEqual((branch['status'], garden.node(branch)), ('ready','ROOT'))
        self.assertEqual(garden.current(branch)['arrival']['origin'], self.packet['arrival'])
        self.advance('RETURN')
        state = self.apply('arrive', new_arrival={**self.packet['arrival'], 'id':'OLD-PAYLOAD'}, reason='Older payload under new ID')
        self.assertEqual(state['branches']['B0']['rest']['kind'], 'loop')

    def test_return_can_carry_new_arrival_immediately(self):
        self.advance('EXIT')
        state = self.apply('step', node='RETURN', output={'reason':'New observation', 'new_arrival':self.new_arrival()})
        self.assertEqual(len(state['branches']['B0']['visits']), 2)
        self.assertEqual(garden.node(state['branches']['B0']), 'ROOT')

    def test_step_budget_does_not_admit_unused_cross_material(self):
        self.packet['budget'] = {'max_steps':5}
        self.document = garden.new_document(self.config, self.packet, self.registry)
        self.advance('MIRROR')
        output = {**self.outputs['CROSS'], 'source_additions':[{'ref':'new','lineage_id':'NEW','kind':'public_source'}]}
        state = self.apply('step', node='CROSS', output=output)
        self.assertNotIn('new', state['sources'])
        self.assertEqual(state['used']['steps'], 5)
        self.assertEqual(state['branches']['B0']['rest']['kind'], 'budget')

    def test_inherited_source_alias_or_model_output_is_not_independent_evidence(self):
        self.advance('MIRROR')
        for source in (
            {'ref':'alias','kind':'public_source','lineage_id':'Q18-STAGED-20260925','independence_basis':'Different URL'},
            {'ref':'model','kind':'model_output','lineage_id':'OTHER','independence_basis':'Different model'},
        ):
            output = {**self.outputs['CROSS'], 'source_additions':[source], 'independent':[source['ref']]}
            with self.subTest(source=source), self.assertRaises(cycle.CycleError):
                self.apply('step', node='CROSS', output=output)

    def test_new_source_and_bridge_refs_survive_clone_as_inherited(self):
        self.advance('MIRROR')
        source = {'ref':'fixture-observation','lineage_id':'DISTINCT','kind':'public_source','independence_basis':'Separate observed event; test fixture'}
        bridge_source = {'ref':'fixture-bridge','lineage_id':'BRIDGE','kind':'context'}
        output = {**self.outputs['CROSS'], 'source_additions':[source,bridge_source], 'independent':[source['ref']],
                  'bridge':[{'question':'Does the test connect these observations?', 'status':'supplied fixture', 'source_refs':[bridge_source['ref']]}]}
        self.apply('step', node='CROSS', output=output)
        self.advance()
        state = self.route()
        self.assertIn(source['ref'], state['branches']['B1']['lineage']['source_refs'])
        self.assertIn(bridge_source['ref'], state['branches']['B1']['lineage']['source_refs'])
        self.advance('MIRROR', branch='B1')
        with self.assertRaisesRegex(cycle.CycleError, 'not independent'):
            self.apply('step', branch='B1', node='CROSS', output={**self.outputs['CROSS'], 'independent':[source['ref']]})

    def test_missing_language_metadata_stays_unknown_and_deeper_route_needs_residual(self):
        self.advance('ROOT')
        incorrect = copy.deepcopy(self.outputs['ARRIVAL'])
        incorrect['language_glance']['languages'] = ['en']
        with self.assertRaisesRegex(cycle.CycleError, 'Unknown language'):
            self.apply('step', node='ARRIVAL', output=incorrect)
        self.advance()
        state = self.route(targets=('LANGUAGE',), rule='LANGUAGE-EXCEPTION')
        self.assertEqual(state['route_decisions'][-1]['status'], 'unknown')
        self.assertEqual(state['used']['branches'], 1)

    def test_morphology_and_proposed_power_cannot_supply_route_authority(self):
        self.advance()
        with self.assertRaisesRegex(cycle.CycleError, 'reviewed configuration'):
            self.route(rule='PECULIARITY_SENSE')
        with self.assertRaises(cycle.CycleError):
            self.apply('route', rule_id='DOMAIN-BRANCH', action='CLONE',
                       targets=[{'tree':'PRODUCTION','focus':'Inspect','reason':'Curiosity'}], power='CURIOSITY')

    def test_example_is_reproducible_and_csv_has_correct_status_and_lineage(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            document = garden_example.build(ROOT, self.scenario, output)
            first = {str(p.relative_to(output)):p.read_bytes() for p in output.rglob('*') if p.is_file()}
            garden_example.build(ROOT, self.scenario, output)
            self.assertEqual(first, {str(p.relative_to(output)):p.read_bytes() for p in output.rglob('*') if p.is_file()})
            with (output / garden.THRESHOLD / 'branches.csv').open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual([(r['branch_id'],r['status']) for r in rows], [('B0','resting'),('B1','ready'),('B2','ready')])
            self.assertEqual([r['parent_branch'] for r in rows], ['', 'B0', 'B0'])
            self.assertTrue(all(r['model_calls'] == '0' for r in rows))
            self.assertEqual(garden.replay(document), document)


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for path in [cycle.CANONICAL, 'config/garden.json', 'config/garden-traversal.json']:
            dest = self.root / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, dest)
        self.scenario = cycle.read_json(ROOT / 'examples/garden-traversal/q18-scenario.json')
        cycle.write_json(self.root / 'operations/questions.json', self.scenario['question_snapshot'])

    def test_retry_repairs_projection_after_checkpoint_was_saved(self):
        packet = self.scenario['start']
        garden.start(self.root, packet)
        command = self.scenario['commands'][0]
        with patch.object(garden, 'project', side_effect=OSError('Interrupted projection')):
            with self.assertRaises(OSError): garden.submit(self.root, packet['run_id'], command)
        saved = cycle.read_json(garden.path_for(self.root, packet['run_id']))
        self.assertEqual(saved['state']['revision'], 1)
        restored = garden.submit(self.root, packet['run_id'], command)
        self.assertEqual(restored, saved)
        self.assertTrue((self.root / garden.THRESHOLD / 'branches.csv').exists())
        self.assertEqual((self.root / cycle.CANONICAL).read_bytes(), (ROOT / cycle.CANONICAL).read_bytes())

    def test_live_epoch_change_preserves_old_run_and_blocks_stale_continuation(self):
        packet = self.scenario['start']
        document = garden.start(self.root, packet)
        registry = copy.deepcopy(self.scenario['question_snapshot'])
        registry['questions'][packet['question_id']]['epoch'] += 1
        cycle.write_json(self.root / 'operations/questions.json', registry, replace=True)
        with self.assertRaisesRegex(cycle.CycleError, 'epoch changed'):
            garden.submit(self.root, packet['run_id'], self.scenario['commands'][0])
        self.assertEqual(garden.replay(cycle.read_json(garden.path_for(self.root, packet['run_id']))), document)

    def test_start_id_cannot_overwrite_and_csv_is_formula_safe(self):
        packet = copy.deepcopy(self.scenario['start'])
        packet['focus'] = '=FORMULA()'
        garden.start(self.root, packet)
        with self.assertRaisesRegex(cycle.CycleError, 'another start packet'):
            garden.start(self.root, {**packet, 'focus':'Changed'})
        with (self.root / garden.THRESHOLD / 'branches.csv').open() as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row['focus'], "'=FORMULA()")


if __name__ == '__main__':
    unittest.main()
