import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import continuity as ledger
import cycle
import garden_runtime as garden

ROOT = Path(__file__).resolve().parents[1]


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.journal = ledger.strict_json(ROOT / ledger.JOURNAL)
        self.catalog = ledger.strict_json(ROOT / ledger.REFERENCES)
        self.schema = ledger.strict_json(ROOT / ledger.SCHEMA)
        self.state, self.resolved = ledger.replay(ROOT)

    def relation(self, rid='REL-ORA-CAREER'):
        return copy.deepcopy(self.state['relationships'][rid])

    def append(self, relation, revision=1):
        journal = copy.deepcopy(self.journal)
        journal['entries'].append(ledger.make_entry(
            relation, sequence=len(journal['entries']) + 1,
            recorded_at=journal['entries'][-1]['recorded_at'], actor='test reviewer',
            reason='Synthetic revision test; never saved as evidence',
            expected_revision=revision, previous=journal['entries'][-1]['entry_sha256']))
        return journal

    def validate(self, relation):
        ledger.validate_relation(relation, self.schema, self.resolved)

    def test_three_cases_reconstruct_with_original_shared_records(self):
        self.assertEqual(self.state['revisions'], {
            'REL-CEM-ARMY-ICE': 1, 'REL-AFCB-REPORTING': 1, 'REL-ORA-CAREER': 1})
        self.assertEqual(self.relation('REL-CEM-ARMY-ICE')['epistemic_status'], 'documented')
        self.assertEqual(self.relation('REL-AFCB-REPORTING')['epistemic_status'], 'documented')
        self.assertEqual(self.relation()['epistemic_status'], 'hypothesized')
        self.assertIsNone(self.relation()['to_event'])
        self.assertEqual(self.resolved['E-CEM-AWARD']['binding']['record_id'], 'CEM04')
        self.assertEqual(self.resolved['E-ORA']['binding']['record_id'], 'MC21')
        self.assertEqual(self.resolved['S-ORA']['binding']['record_id'], 'O01')
        self.assertNotIn('record', self.catalog['references']['S-ORA'])
        self.assertIn('facsimile', ' '.join(self.relation('REL-AFCB-REPORTING')['limitations']))

    def test_deterministic_generated_outputs_and_saved_garden_replay(self):
        self.assertEqual(ledger.build(ROOT, check=True), 5)
        self.assertEqual(ledger.outputs(ROOT), ledger.outputs(ROOT))
        for path in (ROOT / ledger.OUTPUT / 'garden').glob('*.json'):
            document = ledger.strict_json(path)
            with self.subTest(path=path.name):
                self.assertEqual(garden.replay(document), document)
                self.assertEqual(len(document['events']), 10)
                commands = [e['command'] for e in document['events']]
                self.assertEqual([c['node'] for c in commands], garden.NODES)
                self.assertEqual(set(document['state']['branches']), {'B0'})
                self.assertEqual(document['state']['branches']['B0']['status'], 'resting')
                cross = next(c['output'] for c in commands if c['node'] == 'CROSS')
                self.assertEqual(cross['independent'], [])
                self.assertEqual({s['ref'] for s in cross['inherited']},
                                 set(ledger.source_keys(self.relation(path.stem))))

    def test_schema_rejects_extra_fields_bad_types_and_unbounded_test(self):
        mutations = [('surprise', True), ('from_event', 123), ('epistemic_status', 'proven')]
        for key, value in mutations:
            relation = self.relation()
            relation[key] = value
            with self.subTest(key=key), self.assertRaises(ledger.ContinuityError):
                self.validate(relation)
        for key, value in [('max_records', 2), ('max_records', True), ('status', 'scheduled')]:
            relation = self.relation()
            relation['next_test'][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ledger.ContinuityError):
                self.validate(relation)
        with self.assertRaisesRegex(ledger.ContinuityError, 'unsupported schema'):
            ledger.shape('value', {'type': 'string', 'unimplementedConstraint': True})

    def test_missing_wrong_kind_and_changed_source_records_are_rejected(self):
        for key in ['E-NOT-OBSERVED', 'S-ORA']:
            relation = self.relation()
            relation['from_event'] = key
            with self.subTest(key=key), self.assertRaisesRegex(ledger.ContinuityError, 'Missing/wrong-kind'):
                self.validate(relation)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            catalog = copy.deepcopy(self.catalog)
            for binding in catalog['references'].values():
                path = root / binding['path']
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT / binding['path']).read_bytes())
            path = root / catalog['references']['S-ORA']['path']
            content = ledger.strict_json(path)
            next(s for s in content['sources'] if s['source_id'] == 'O01')['title'] = 'Changed title'
            path.write_bytes(cycle.encoded(content))
            with self.assertRaisesRegex(ledger.ContinuityError, 'pinned record changed'):
                ledger.resolve(root, catalog)

    def test_source_aliases_preserve_shared_lineage_and_manifest_is_pinned(self):
        catalog = copy.deepcopy(self.catalog)
        catalog['references']['S-ORA-ALIAS'] = copy.deepcopy(catalog['references']['S-ORA'])
        resolved = ledger.resolve(ROOT, catalog)
        self.assertEqual(resolved['S-ORA']['record'], resolved['S-ORA-ALIAS']['record'])
        relation = self.relation()
        relation['supporting_evidence'].append({**relation['supporting_evidence'][0], 'source_ref': 'S-ORA-ALIAS'})
        doc = ledger.garden_pass(ROOT, relation, resolved, self.journal['entries'][0]['recorded_at'])
        cross = next(e['command']['output'] for e in doc['events'] if e['command']['node'] == 'CROSS')
        self.assertEqual(cross['independent'], [])
        with self.assertRaisesRegex(ledger.ContinuityError, 'Reference manifest mismatch'):
            ledger.replay(ROOT, catalog=catalog)
        with self.assertRaisesRegex(ledger.ContinuityError, 'Schema snapshot mismatch'):
            ledger.replay(ROOT, schema={**self.schema, 'title': 'Changed contract'})

    def test_context_or_time_alone_cannot_establish_a_relationship(self):
        for basis in ['context', 'temporal_only']:
            relation = self.relation('REL-CEM-ARMY-ICE')
            for support in relation['supporting_evidence']:
                support['basis'] = basis
            with self.subTest(basis=basis), self.assertRaisesRegex(ledger.ContinuityError, 'direct-record'):
                self.validate(relation)
        relation = self.relation('REL-CEM-ARMY-ICE')
        relation['epistemic_status'] = 'hypothesized'
        self.validate(relation)
        self.assertEqual(ledger.chronological(relation, self.resolved)['lag_days'], 75)
        self.assertEqual(relation['epistemic_status'], 'hypothesized')

    def test_missing_target_cannot_be_documented_but_can_be_retired(self):
        for status in ['documented', 'partly_documented']:
            relation = self.relation()
            relation['epistemic_status'] = status
            relation['supporting_evidence'][0]['basis'] = 'direct_record'
            with self.subTest(status=status), self.assertRaisesRegex(ledger.ContinuityError, 'Unobserved endpoint'):
                self.validate(relation)
        for status in ['contested', 'refuted', 'unknown']:
            relation = self.relation()
            relation['epistemic_status'] = status
            relation['counterevidence'][0]['statement'] = 'Synthetic changed assessment for transition test'
            state, _ = ledger.replay(ROOT, journal=self.append(relation))
            self.assertIsNone(state['relationships']['REL-ORA-CAREER']['to_event'])
            self.assertEqual(state['relationships']['REL-ORA-CAREER']['epistemic_status'], status)

    def test_date_precision_does_not_invent_order_or_causation(self):
        relation = self.relation('REL-CEM-ARMY-ICE')
        relation['time_scope'].update(start='2026-09-30', end='2026-09')
        self.validate(relation)
        relation['time_scope'].update(start='2026-10-01', end='2026-09')
        with self.assertRaisesRegex(ledger.ContinuityError, 'Definitely reversed'):
            self.validate(relation)
        relation = self.relation('REL-CEM-ARMY-ICE')
        relation.update(from_event='E-ICE-OPEN', to_event='E-ICE-HANDOFF')
        comparison = ledger.chronological(relation, self.resolved)
        self.assertEqual(comparison['order'], 'unresolved_or_imprecise')
        self.assertIsNone(comparison['lag_days'])
        relation['relationship_type'] = 'precedes'
        with self.assertRaisesRegex(ledger.ContinuityError, 'ordered day dates'):
            self.validate(relation)
        relation.update(from_event='E-CEM-HANDOFF', to_event='E-CEM-AWARD')
        self.assertEqual(ledger.chronological(relation, self.resolved)['order'], 'follows')
        with self.assertRaisesRegex(ledger.ContinuityError, 'ordered day dates'):
            self.validate(relation)
        for bad in ['2026-02-30', '2026-13', '', 'soon']:
            with self.subTest(bad=bad), self.assertRaises(ledger.ContinuityError):
                ledger.date_value(bad)

    def test_journal_tampering_reordering_and_stale_revision_fail(self):
        journal = copy.deepcopy(self.journal)
        journal['entries'][0]['relationship']['claim'] = 'Altered history'
        with self.assertRaisesRegex(ledger.ContinuityError, 'Entry modified'):
            ledger.replay(ROOT, journal=journal)
        journal = copy.deepcopy(self.journal)
        journal['entries'][0], journal['entries'][1] = journal['entries'][1], journal['entries'][0]
        with self.assertRaisesRegex(ledger.ContinuityError, 'sequence mismatch'):
            ledger.replay(ROOT, journal=journal)
        with self.assertRaisesRegex(ledger.ContinuityError, 'Stale relationship revision'):
            ledger.replay(ROOT, journal=self.append(self.relation(), revision=0))

    def test_appended_revision_preserves_history_without_endpoint_rewiring(self):
        relation = self.relation()
        relation['limitations'].append('Synthetic review note')
        journal = self.append(relation)
        state, _ = ledger.replay(ROOT, journal=journal)
        self.assertEqual(journal['entries'][:3], self.journal['entries'])
        self.assertEqual(state['history'][:3], self.state['history'])
        self.assertEqual(state['revisions']['REL-ORA-CAREER'], 2)
        relation['to_event'] = 'E-ASSESSMENT-GUIDE'
        relation['unobserved_target'] = None
        with self.assertRaisesRegex(ledger.ContinuityError, 'new relationship ID'):
            ledger.replay(ROOT, journal=self.append(relation))

    def test_status_revision_requires_changed_evidence_assessment(self):
        relation = self.relation('REL-CEM-ARMY-ICE')
        relation['epistemic_status'] = 'contested'
        with self.assertRaisesRegex(ledger.ContinuityError, 'changed evidence assessment'):
            ledger.replay(ROOT, journal=self.append(relation))
        relation['counterevidence'][0]['statement'] = 'Synthetic revised counterevidence assessment'
        state, _ = ledger.replay(ROOT, journal=self.append(relation))
        self.assertEqual(state['relationships']['REL-CEM-ARMY-ICE']['epistemic_status'], 'contested')

    def test_repository_escape_and_ambiguous_json_are_rejected(self):
        for path in ['../outside.json', '/tmp/outside.json']:
            with self.subTest(path=path), self.assertRaises(ledger.ContinuityError):
                ledger.local_path(ROOT, path)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'bad.json'
            for content in ['{"a":1,"a":2}', '{"a":NaN}']:
                path.write_text(content)
                with self.subTest(content=content), self.assertRaises(ledger.ContinuityError):
                    ledger.strict_json(path)


if __name__ == '__main__':
    unittest.main()
