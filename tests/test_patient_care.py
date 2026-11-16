"""Reject evidence promotion at care-pathway boundaries, using fictional records."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import continuity as shared
import cycle
import patient_care as pc

ROOT = Path(__file__).resolve().parents[1]


class PatientCareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.journal = pc.read(ROOT, pc.JOURNAL)
        cls.manifest = pc.read(ROOT, pc.REFERENCES)
        cls.schema = pc.read(ROOT, pc.SCHEMA)
        cls.state, cls.resolved = pc.replay(ROOT)

    def case(self, revision=-1):
        return copy.deepcopy(self.journal['entries'][revision]['pathway'])

    def stage(self, case, kind):
        return next(s for s in case['stages'] if s['observation_type'] == kind)

    def validate(self, case, resolved=None):
        return pc.validate(case, self.schema, self.resolved if resolved is None else resolved)

    def test_fixture_preserves_initial_unknowns_and_later_administrative_success(self):
        self.assertEqual(self.state['revisions'], {'PC-FICTIONAL-ONE': 2})
        initial, latest = self.case(0), self.case()
        for kind in ('medical_authorization', 'prerequisite_performed', 'route_corrected', 'appointment_booked', 'coordinator_authorized'):
            self.assertEqual(self.stage(initial, kind)['status'], 'unknown')
            self.assertEqual(self.stage(latest, kind)['status'], 'completed')
        for kind in ('accommodation_implemented', 'treatment_consent', 'appointment_attended',
                     'diagnostic_evaluation', 'treatment_selected', 'clinical_benefit', 'remedy_realized'):
            self.assertEqual(self.stage(latest, kind)['status'], 'unknown')
        self.assertTrue(set(initial['event_refs']) < set(latest['event_refs']))
        self.assertEqual(self.stage(initial, 'medical_authorization')['patient_cost']['type'], 'unknown')
        self.assertEqual(self.stage(latest, 'medical_authorization')['patient_cost']['type'], 'authorized_coverage')
        self.assertEqual(self.stage(latest, 'route_corrected')['patient_usable_effect']['status'], 'observed')
        self.assertTrue(all(s['patient_usable_effect']['status'] == 'unknown'
                            for s in latest['stages'] if s['observation_type'] != 'route_corrected'))

    def test_adjacent_milestones_do_not_establish_the_requested_action(self):
        substitutions = [
            ('referral_received', 'E-DISPATCH'),
            ('triage_completed', 'E-RECEIPT'),
            ('diagnostic_evaluation', 'E-TEST-REQUEST'),
            ('diagnostic_evaluation', 'E-TEST-DONE'),
            ('diagnostic_evaluation', 'E-MANAGEMENT'),
            ('accommodation_implemented', 'E-WRITING-REQUEST'),
            ('treatment_consent', 'E-COORDINATOR-OK'),
            ('remedy_realized', 'E-POLICY'),
            ('appointment_attended', 'E-BOOKING'),
            ('clinical_benefit', 'E-BOOKING'),
        ]
        for kind, ref in substitutions:
            with self.subTest(kind=kind, ref=ref):
                case = self.case()
                self.stage(case, kind).update(status='completed', event_refs=[ref])
                with self.assertRaisesRegex(pc.Error, 'observation and service type'):
                    self.validate(case)

    def test_optional_management_fee_does_not_determine_medical_coverage(self):
        case = self.case()
        self.stage(case, 'medical_authorization')['patient_cost'] = {
            'type': 'self_pay', 'amount': None, 'currency': None, 'event_refs': ['E-MANAGEMENT']}
        with self.assertRaisesRegex(pc.Error, 'same-service evidence'):
            self.validate(case)

    def test_missing_outcome_is_unknown_not_failure_or_success(self):
        for status in ('completed', 'failed', 'pending', 'contested'):
            case = self.case()
            self.stage(case, 'clinical_benefit')['status'] = status
            with self.subTest(status=status), self.assertRaisesRegex(pc.Error, 'absence is UNKNOWN'):
                self.validate(case)

    def test_booking_does_not_establish_usable_clinical_effect(self):
        case = self.case()
        self.stage(case, 'appointment_booked')['patient_usable_effect'].update(
            status='observed', event_refs=['E-BOOKING'])
        with self.assertRaisesRegex(pc.Error, 'separate supported observation'):
            self.validate(case)

    def test_relabeling_policy_or_booking_effect_flag_is_insufficient(self):
        for ref in ('E-POLICY', 'E-BOOKING', 'E-WRITING-REQUEST'):
            resolved = copy.deepcopy(self.resolved)
            resolved[ref]['record']['usable_effect'] = True
            with self.subTest(ref=ref), self.assertRaisesRegex(pc.Error, 'cannot establish a patient-usable effect'):
                self.validate(self.case(), resolved)

    def test_shared_source_reuse_never_becomes_independent_corroboration(self):
        self.assertEqual(len(self.case()['event_refs']), 14)
        self.assertEqual(self.state['source_families'], {'PC-FICTIONAL-ONE': ['FICTIONAL-PATHWAY-ONE']})
        case = self.case()
        case['independent_corroboration_count'] = 14
        with self.assertRaisesRegex(pc.Error, 'unexpected fields'):
            self.validate(case)
        case = self.case()
        self.stage(case, 'referral_received')['event_refs'] *= 2
        with self.assertRaisesRegex(pc.Error, 'Duplicate stage event'):
            self.validate(case)

    def test_relabeling_event_cannot_override_pinned_source_type(self):
        case, resolved = self.case(), copy.deepcopy(self.resolved)
        resolved['E-MANAGEMENT']['record']['observation_type'] = 'diagnostic_evaluation'
        with self.assertRaisesRegex(pc.Error, 'exceeds its source record'):
            self.validate(case, resolved)

    def test_formal_source_cannot_be_reclassified_as_observed_care(self):
        case, resolved = self.case(), copy.deepcopy(self.resolved)
        case['record_mode'] = 'reviewed_public_record'
        for item in resolved.values():
            record = item['record']
            if record.get('record_mode') == 'synthetic_demonstration':
                record['record_mode'] = 'reviewed_public_record'
            if record.get('source_kind') == 'synthetic_record':
                record['source_kind'] = 'public_action_record'
        resolved['S-BOOKING']['record']['source_kind'] = 'formal_policy'
        with self.assertRaisesRegex(pc.Error, 'Formal policy cannot establish action'):
            self.validate(case, resolved)

    def test_future_event_or_source_cannot_support_an_earlier_assessment(self):
        case = self.case(0)
        case['event_refs'].append('E-BOOKING')
        with self.assertRaisesRegex(pc.Error, 'after cutoff'):
            self.validate(case)
        resolved = copy.deepcopy(self.resolved)
        resolved['S-RECEIPT']['record']['publication_date'] = '2026-12-01'
        with self.assertRaisesRegex(pc.Error, 'publication after cutoff'):
            self.validate(self.case(), resolved)

    def test_contradiction_requires_contested_status(self):
        case, resolved = self.case(), copy.deepcopy(self.resolved)
        extra = copy.deepcopy(resolved['E-BOOKING'])
        extra['record']['result'] = 'not_performed'
        resolved['E-CONTRARY-BOOKING'] = extra
        case['event_refs'].append('E-CONTRARY-BOOKING')
        stage = self.stage(case, 'appointment_booked')
        stage['event_refs'].append('E-CONTRARY-BOOKING')
        for status in ('completed', 'failed'):
            stage['status'] = status
            with self.subTest(status=status), self.assertRaisesRegex(pc.Error, 'Conflicting results'):
                self.validate(case, resolved)
        stage['status'] = 'contested'
        self.validate(case, resolved)
        extra['record']['result'] = 'contested'
        self.validate(case, resolved)

    def test_explicit_nonperformance_can_be_recorded_without_inferring_harm(self):
        case, resolved = self.case(), copy.deepcopy(self.resolved)
        resolved['E-BOOKING']['record']['result'] = 'not_performed'
        self.stage(case, 'appointment_booked')['status'] = 'failed'
        self.validate(case, resolved)
        self.assertEqual(self.stage(case, 'clinical_benefit')['status'], 'unknown')

    def test_journal_cannot_be_silently_edited_or_reordered(self):
        changed = copy.deepcopy(self.journal)
        changed['entries'][0]['pathway']['title'] = 'Rewritten history'
        with self.assertRaisesRegex(pc.Error, 'Entry modified'):
            pc.replay(ROOT, journal=changed)
        changed = copy.deepcopy(self.journal)
        changed['entries'].reverse()
        with self.assertRaisesRegex(pc.Error, 'Sequence mismatch'):
            pc.replay(ROOT, journal=changed)

    def test_later_revision_must_retain_events_and_stage_identity(self):
        for mutation in ('remove_event', 'change_stage'):
            case = self.case()
            if mutation == 'remove_event':
                case['event_refs'].remove('E-DISPATCH')
                case['stages'] = [s for s in case['stages'] if s['observation_type'] != 'referral_dispatched']
            else:
                self.stage(case, 'clinical_benefit')['service_type'] = 'education_management'
            journal = copy.deepcopy(self.journal)
            journal['entries'].append(pc.make_entry(case, sequence=3, recorded_at='2026-11-15T20:00:00Z',
                actor='test fixture', reason='Negative history test', expected_revision=2,
                previous=journal['entries'][-1]['entry_sha256']))
            with self.subTest(mutation=mutation), self.assertRaisesRegex(pc.Error, 'Retain earlier|Changed stage meaning'):
                pc.replay(ROOT, journal=journal)

    def test_source_record_pin_rejects_changed_binding(self):
        manifest = copy.deepcopy(self.manifest)
        manifest['references']['E-BOOKING']['sha256'] = '0' * 64
        journal = copy.deepcopy(self.journal)
        journal['references_sha256'] = cycle.digest(manifest)
        with self.assertRaisesRegex(pc.Error, 'pinned record changed'):
            pc.replay(ROOT, journal=journal, manifest=manifest)

    def test_saved_pass_reconstructs_without_network_or_provider(self):
        result = pc.build(ROOT)
        self.assertEqual(result['steps'], 10)
        self.assertEqual(result['revisions'], 2)
        self.assertEqual(result['provider_calls'], 0)
        self.assertFalse(result['canonical_admission'])


if __name__ == '__main__':
    unittest.main()
