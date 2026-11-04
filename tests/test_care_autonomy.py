"""Bounded care/autonomy review: authority, practice and outcome stay separate."""
import copy
import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import continuity as shared
import cycle
import garden_runtime as garden
import garden_tree
import safeguards as sg

spec = importlib.util.spec_from_file_location('care_autonomy_packet',
    ROOT / 'reports/care-autonomy/20261104/verify_packet.py')
packet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packet)


class CareAutonomyTests(unittest.TestCase):
    def setUp(self):
        self.state, self.resolved = packet.load_review(ROOT)
        self.schema = shared.strict_json(ROOT / sg.SCHEMA)
        self.journal = shared.strict_json(ROOT / packet.JOURNAL)
        self.manifest = shared.strict_json(ROOT / packet.MANIFEST)

    def record(self, sid='SG-CARE-ELIGIBILITY'):
        return copy.deepcopy(self.state['safeguards'][sid])

    def validate(self, record):
        packet.validate_evidence_classes(record, self.schema, self.resolved)

    def test_supplied_baseline_replays_offline_without_diagnosing_people(self):
        with patch('socket.create_connection', side_effect=AssertionError('No network in replay')):
            result = packet.build(ROOT)
        self.assertEqual(result['safeguards'], 3)
        self.assertEqual((result['steps'], result['branches'], result['provider_calls']), (10, 1, 0))
        self.assertFalse(result['individual_eligibility_decision'])
        for record in self.state['safeguards'].values():
            self.assertEqual(record['effectiveness']['status'], 'unknown')
            self.assertEqual(record['failure']['status'], 'unknown')

    def test_campaign_statement_cannot_be_relabelled_formal_authority(self):
        record = self.record()
        item = next(e for e in record['evidence'] if any(
            self.resolved[c['source_ref']]['record']['source_kind'] == 'campaign_statement'
            for c in e['citations']))
        item['kind'] = 'formal_text'
        record['formal']['evidence_ids'] = [item['evidence_id']]
        with self.assertRaisesRegex(shared.ContinuityError, 'reviewed source class'):
            self.validate(record)

    def test_formal_rule_does_not_establish_staffing_enforcement_or_protection(self):
        for component in ('people', 'procedures', 'authority', 'effectiveness'):
            record = self.record()
            formal_id = next(e['evidence_id'] for e in record['evidence'] if e['kind'] == 'formal_text')
            if component == 'effectiveness':
                target = record['effectiveness']
            else:
                target = record['operational'][component]
            target.update(status='observed', evidence_ids=[formal_id])
            with self.subTest(component=component), self.assertRaises(shared.ContinuityError):
                self.validate(record)

    def test_announced_services_cannot_be_relabelled_as_completed_benefit(self):
        record = self.record('SG-CARE-USABLE-SERVICES')
        item = record['evidence'][0]
        item.update(kind='effectiveness_observation',
            period={'start': '2026-11-04', 'end': '2026-11-04', 'note': 'Synthetic attempted promotion'},
            effect={'kind': 'remedied', 'harm': 'Synthetic lack of access',
                    'action': 'An announcement', 'result': 'Claimed delivery',
                    'scope': 'Negative fixture only'})
        record['effectiveness'].update(status='observed', evidence_ids=[item['evidence_id']])
        with self.assertRaisesRegex(shared.ContinuityError, 'reviewed source class'):
            self.validate(record)

    def test_unknown_effectiveness_is_not_documented_failure(self):
        record = self.record()
        record['failure'].update(status='documented', evidence_ids=record['formal']['evidence_ids'])
        with self.assertRaisesRegex(shared.ContinuityError, 'observed noncompliance'):
            self.validate(record)

    def test_refusal_fields_cannot_turn_the_baseline_into_an_eligibility_decision(self):
        case = shared.strict_json(ROOT / packet.CASE)
        case['eligibility_decision'] = 'eligible_because_refused'
        with self.assertRaisesRegex(shared.ContinuityError, 'No automated eligibility'):
            packet.make_scenario(ROOT, case, self.state, self.resolved)

    def test_source_pin_drift_and_unrelated_event_are_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        next(iter(manifest['references'].values()))['sha256'] = '0' * 64
        with self.assertRaises(shared.ContinuityError):
            packet.load_review(ROOT, manifest=manifest)
        record = self.record()
        item = record['evidence'][0]
        bad = copy.deepcopy(self.resolved)
        bad[item['event_refs'][0]]['record']['source_ids'] = ['UNRELATED-SOURCE']
        with self.assertRaisesRegex(shared.ContinuityError, 'different lineage'):
            packet.validate_evidence_classes(record, self.schema, bad)

    def test_supplement_does_not_change_existing_routing_or_limits(self):
        base = garden.load_config(ROOT)
        extended = garden_tree.load(ROOT, shared.strict_json(ROOT / packet.TREE))
        self.assertEqual(set(extended['trees']) - set(base['trees']), {'CARE-AUTONOMY'})
        del extended['trees']['CARE-AUTONOMY']
        self.assertEqual(extended, base)

    def test_later_scoped_outcome_can_be_appended_without_rewriting_history(self):
        """All new records here are explicitly fictional and stay inside a temp tree."""
        record = self.record()
        event_ref, source_ref = 'E-SYNTHETIC-CARE-OUTCOME', 'S-SYNTHETIC-CARE-OUTCOME'
        source = {'source_id': 'SYNTHETIC-CARE-OUTCOME', 'source_family': 'SYNTHETIC-TEST-ONLY',
                  'source_kind': 'outcome_record', 'permitted_evidence_kinds': ['effectiveness_observation']}
        event = {'event_id': 'SYNTHETIC-CARE-OUTCOME', 'source_ids': [source['source_id']],
                 'event_date': '2026-11-04', 'scope': 'Fictional boundary test only'}
        record['event_refs'].append(event_ref)
        record['evidence'].append({'evidence_id': 'SYNTHETIC-CARE-REMEDY',
            'kind': 'effectiveness_observation', 'claim': 'Fictional reviewed remedy',
            'period': {'start': '2026-11-04', 'end': '2026-11-04', 'note': 'Fictional event date'},
            'citations': [{'source_ref': source_ref, 'locator': 'Fictional observation'}],
            'event_refs': [event_ref], 'limits': 'Synthetic test; not real protection',
            'effect': {'kind': 'remedied', 'harm': 'Fictional unsupported referral',
                       'action': 'Fictional independent review and accessible alternative',
                       'result': 'Fictional referral corrected and alternative used',
                       'scope': 'One fictional event'}})
        record['effectiveness'].update(status='observed', claim='Fictional bounded result',
                                       evidence_ids=['SYNTHETIC-CARE-REMEDY'])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base_path = self.manifest['base']['path']
            base = shared.strict_json(ROOT / base_path)
            paths = {base_path, str(sg.SCHEMA)} | {
                binding['path'] for binding in [*base['references'].values(),
                                               *self.manifest['references'].values()]}
            for path in paths:
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, root / path)
            fixture_path = 'fixtures/synthetic-care.json'
            cycle.write_json(root / fixture_path, {'sources': [source], 'events': [event]})
            manifest = copy.deepcopy(self.manifest)
            for alias, kind, item, field, collection in (
                    (source_ref, 'source', source, 'source_id', 'sources'),
                    (event_ref, 'event', event, 'event_id', 'events')):
                manifest['references'][alias] = {'kind': kind, 'path': fixture_path,
                    'collection': collection, 'id_field': field, 'record_id': item[field],
                    'sha256': cycle.digest(item)}
            journal = copy.deepcopy(self.journal)
            journal['references_sha256'] = cycle.digest(manifest)
            journal['entries'].append(sg.make_entry(record, sequence=len(journal['entries']) + 1,
                recorded_at=journal['entries'][-1]['recorded_at'], actor='synthetic test reviewer',
                reason='Fictional later evidence tests revision support',
                expected_revision=self.state['revisions'][record['safeguard_id']],
                previous=journal['entries'][-1]['entry_sha256']))
            state, _ = packet.load_review(root, journal=journal, manifest=manifest)
            self.assertEqual(state['history'][:-1], self.state['history'])
            revised = state['safeguards'][record['safeguard_id']]
            self.assertEqual(revised['effectiveness']['status'], 'observed')
            self.assertEqual(revised['evidence'][:-1], self.record()['evidence'])


if __name__ == '__main__':
    unittest.main()
