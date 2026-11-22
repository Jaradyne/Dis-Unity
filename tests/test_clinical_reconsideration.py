"""Meaningful boundary tests for supplied clinical reconsideration, never diagnosis."""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import clinical_reconsideration as cr
import cycle
import patient_care as care

ROOT = Path(__file__).resolve().parents[1]


class ClinicalReconsiderationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.journal = cr.read(ROOT, cr.JOURNAL)
        cls.schema = cr.read(ROOT, cr.SCHEMA)
        cls.state, cls.resolved = cr.replay(ROOT)

    def case(self, n=-1):
        return copy.deepcopy(self.journal['entries'][n]['pathway'])

    def validate(self, case, resolved=None):
        resolved = self.resolved if resolved is None else resolved
        care.validate(case, cr.combined_schema(ROOT), resolved)
        return cr.validate_lens(case, resolved, self.schema)

    def assessment(self, case, name):
        return case['reconsideration']['assessments'][name]

    def independence(self, case, opinion='RC-OPINION-B'):
        return next(a for a in case['reconsideration']['opinion_independence']
                    if a['opinion_ref'] == opinion)

    def record(self, case, resolved, ref, detail, observation='diagnostic_evaluation'):
        """An explicitly supplied new fictional record with its own scoped source."""
        event = copy.deepcopy(resolved['RC-OPINION-B']['record'])
        sid = 'SYNTHETIC-' + ref
        event.update(event_id='FICTIONAL-' + ref, event_date='2026-11-13',
                     reconsideration=detail, source_ids=[sid], observation_type=observation)
        source = copy.deepcopy(resolved['S-RC-OPINION-B']['record'])
        source.update(source_id=sid, publication_date='2026-11-13', asserted_event_ids=[event['event_id']],
                      permitted_observation_types=[observation], permitted_reconsideration_kinds=[detail['kind']])
        resolved[ref] = {'binding': {'kind': 'event'}, 'record': event}
        resolved['S-' + ref] = {'binding': {'kind': 'source'}, 'record': source}
        case['event_refs'].append(ref)

    def test_fixture_retains_report_refusal_unknowns_and_later_agreement(self):
        first, last = self.case(0), self.case()
        for case in (first, last):
            self.assertEqual(case['reconsideration']['reported_harm_refs'], ['RC-REPORT'])
            stages = {s['stage_id']: s for s in case['stages']}
            self.assertEqual(stages['REVIEW-A']['status'], 'failed')
            self.assertEqual(stages['BENEFIT']['status'], 'unknown')
        self.assertEqual(next(s for s in first['stages'] if s['stage_id'] == 'RECEIPT-B')['status'], 'unknown')
        self.assertEqual(self.assessment(first, 'second_review')['status'], 'unknown')
        self.assertEqual(self.assessment(last, 'second_review')['status'], 'documented')
        opinion = self.resolved['RC-OPINION-B']['record']['reconsideration']
        self.assertEqual(opinion['conclusion'], 'agrees')
        self.assertEqual(self.independence(last)['status'], 'unknown')
        for name in ('clinical_error', 'harm_causation', 'correction_received', 'downstream_change', 'clinical_benefit'):
            self.assertEqual(self.assessment(last, name)['status'], 'unknown')

    def test_missing_evidence_is_neither_failure_nor_conclusion(self):
        for status in ('documented', 'contested'):
            case = self.case()
            self.assessment(case, 'clinical_benefit')['status'] = status
            with self.subTest(status=status), self.assertRaisesRegex(cr.Error, 'missing evidence'):
                self.validate(case)
        case = self.case(0)
        next(s for s in case['stages'] if s['stage_id'] == 'RECEIPT-B')['status'] = 'failed'
        with self.assertRaisesRegex(cr.Error, 'absence is UNKNOWN'):
            self.validate(case)

    def test_initial_opinion_certainty_does_not_establish_accuracy(self):
        for conclusion in ('provisional', 'definitive', 'unspecified'):
            resolved = copy.deepcopy(self.resolved)
            resolved['RC-INITIAL']['record']['reconsideration']['conclusion'] = conclusion
            with self.subTest(conclusion=conclusion):
                self.validate(self.case(), resolved)
                self.assertEqual(self.assessment(self.case(), 'clinical_error')['status'], 'unknown')

    def test_policy_booking_and_approval_are_not_reconsideration(self):
        for ref in ('RC-POLICY', 'RC-BOOK-B', 'RC-AUTH-B', 'RC-ATTEND-B', 'RC-INITIAL'):
            case = self.case()
            self.assessment(case, 'second_review')['evidence_refs'] = [ref]
            with self.subTest(ref=ref), self.assertRaises(cr.Error):
                self.validate(case)

    def test_patient_report_disagreement_and_addendum_do_not_prove_error_or_cause(self):
        for name in ('clinical_error', 'harm_causation'):
            for ref in ('RC-REPORT', 'RC-OPINION-B', 'RC-CORRECTION'):
                case = self.case()
                self.assessment(case, name).update(status='documented', evidence_refs=[ref])
                with self.subTest(name=name, ref=ref), self.assertRaisesRegex(cr.Error, 'own evidence kind'):
                    self.validate(case)
        resolved = copy.deepcopy(self.resolved)
        resolved['RC-OPINION-B']['record']['reconsideration']['conclusion'] = 'revises'
        self.validate(self.case(), resolved)
        self.assertEqual(self.assessment(self.case(), 'clinical_error')['status'], 'unknown')

    def test_dedicated_review_must_affirm_the_actual_proposition(self):
        for name, kind in [('clinical_error', 'clinical_error_review'), ('harm_causation', 'causation_review')]:
            for conclusion in ('affirmed', 'rejected', 'inconclusive', 'contested'):
                case, resolved = self.case(), copy.deepcopy(self.resolved)
                detail = {'kind': kind, 'target_opinion_ref': 'RC-INITIAL', 'reviewing_role': 'Fictional scoped reviewer',
                          'basis_refs': ['RC-PRIMARY', 'RC-NEW-PRIMARY'], 'scope': 'One explicitly stated proposition.',
                          'conclusion': conclusion}
                if name == 'clinical_error':
                    detail['finding'] = 'Supplied finding concerning one aspect of the initial assessment.'
                else:
                    detail.update(reasoning='Supplied scoped causal reasoning.', harm_report_ref='RC-REPORT')
                self.record(case, resolved, 'RC-REVIEW-PROPOSITION', detail)
                self.assessment(case, name).update(status='documented', evidence_refs=['RC-REVIEW-PROPOSITION'])
                with self.subTest(name=name, conclusion=conclusion):
                    if conclusion == 'affirmed':
                        self.validate(case, resolved)
                    else:
                        with self.assertRaisesRegex(cr.Error, 'not an affirmed finding'):
                            self.validate(case, resolved)

    def test_reviewer_change_is_not_independence(self):
        for refs in ([], ['RC-INITIAL'], ['RC-NEW-PRIMARY']):
            case = self.case()
            independence = self.independence(case)
            independence.update(status='documented', evidence_refs=refs)
            with self.subTest(refs=refs), self.assertRaisesRegex(cr.Error, '[Ii]ndependence basis'):
                self.validate(case)

    def test_repeat_of_prior_opinion_alone_is_not_primary_reconsideration(self):
        resolved = copy.deepcopy(self.resolved)
        resolved['RC-OPINION-B']['record']['reconsideration']['evidence_considered'] = ['RC-INITIAL']
        with self.assertRaisesRegex(cr.Error, 'Repeated opinions alone'):
            self.validate(self.case(), resolved)

    def test_opinion_basis_cannot_come_from_future_or_self(self):
        for refs in (['RC-CORRECTION'], ['RC-OPINION-B']):
            resolved = copy.deepcopy(self.resolved)
            resolved['RC-OPINION-B']['record']['reconsideration']['evidence_considered'] = refs
            with self.subTest(refs=refs), self.assertRaises(cr.Error):
                self.validate(self.case(), resolved)

    def test_correction_authorship_dispatch_receipt_action_and_benefit_are_separate(self):
        for name, ref in [('correction_dispatched','RC-CORRECTION'), ('correction_received','RC-CORRECTION-SENT'),
                          ('downstream_change','RC-CORRECTION-SENT'), ('clinical_benefit','RC-CORRECTION')]:
            case = self.case()
            self.assessment(case, name).update(status='documented', evidence_refs=[ref])
            with self.subTest(name=name), self.assertRaisesRegex(cr.Error, 'own evidence kind'):
                self.validate(case)

    def test_receipt_must_identify_the_intended_recipient_and_addendum(self):
        for recipient, expected in [('Fictional continuing-care team', True), ('Someone else', False)]:
            case, resolved = self.case(), copy.deepcopy(self.resolved)
            self.record(case, resolved, 'RC-RECEIVED', {'kind':'correction_receipt',
                'correction_ref':'RC-CORRECTION', 'recipient_role':recipient}, 'referral_received')
            stage = next(s for s in case['stages'] if s['stage_id'] == 'CORRECTION-RECEIVED')
            stage.update(status='completed', event_refs=['RC-RECEIVED'])
            resolved['RC-RECEIVED']['record']['service_type'] = stage['service_type']
            self.assessment(case, 'correction_received').update(status='documented', evidence_refs=['RC-RECEIVED'])
            with self.subTest(recipient=recipient):
                if expected:
                    self.validate(case, resolved)
                else:
                    with self.assertRaisesRegex(cr.Error, 'intended recipient'):
                        self.validate(case, resolved)

    def test_independence_requires_an_affirmative_scoped_disposition(self):
        for conclusion in ('affirmed', 'rejected', 'inconclusive', 'contested'):
            case, resolved = self.case(), copy.deepcopy(self.resolved)
            self.record(case, resolved, 'RC-INDEPENDENCE', {
                'kind':'independence_record', 'opinion_ref':'RC-OPINION-B',
                'reviewer_role':'Fictional clinician B', 'relationship_disclosure':'A separately supplied relationship review.',
                'scope':'Organizational relationship only; prior opinion was visible.', 'conclusion':conclusion})
            self.independence(case).update(
                status='documented', evidence_refs=['RC-INDEPENDENCE'])
            with self.subTest(conclusion=conclusion):
                if conclusion == 'affirmed':
                    self.validate(case, resolved)
                else:
                    with self.assertRaisesRegex(cr.Error, 'independence basis'):
                        self.validate(case, resolved)

    def test_later_independence_conflict_preserves_the_opinion_and_prior_revision(self):
        case, resolved = self.case(), copy.deepcopy(self.resolved)
        journal = copy.deepcopy(self.journal)
        prior_opinion = copy.deepcopy(resolved['RC-OPINION-B']['record'])
        for sequence, conclusion, day in [(3, 'affirmed', '2026-11-13'),
                                          (4, 'rejected', '2026-11-14')]:
            ref = 'RC-INDEPENDENCE-' + conclusion
            self.record(case, resolved, ref, {'kind':'independence_record',
                'opinion_ref':'RC-OPINION-B', 'reviewer_role':'Fictional clinician B',
                'relationship_disclosure':'An attributed relationship review.',
                'scope':'Organizational relationship only.', 'conclusion':conclusion})
            resolved[ref]['record']['event_date'] = day
            case['evidence_cutoff'] = day
            independence = self.independence(case)
            if conclusion == 'rejected':
                with self.assertRaisesRegex(cr.Error, 'all scoped records'):
                    self.validate(case, resolved)
            independence['evidence_refs'].append(ref)
            if conclusion == 'rejected':
                with self.assertRaisesRegex(cr.Error, 'affirmative independence basis'):
                    self.validate(case, resolved)
            independence['status'] = 'documented' if conclusion == 'affirmed' else 'contested'
            self.validate(case, resolved)
            journal['entries'].append(care.make_entry(case, sequence=sequence,
                recorded_at='2026-11-22T18:0' + str(sequence) + ':00Z',
                actor='Negative/positive fictional history test', reason='New scoped disclosure.',
                expected_revision=sequence - 1, previous=journal['entries'][-1]['entry_sha256']))
        # Resolver injection isolates journal behavior; real pinned bindings are checked separately.
        with patch.object(care.sg, 'resolve', return_value=resolved):
            state, _ = cr.replay(ROOT, journal=journal)
        assessments = [self.independence(e['pathway'])['status'] for e in journal['entries'][1:]]
        self.assertEqual(assessments, ['unknown', 'documented', 'contested'])
        self.assertEqual(journal['entries'][:2], self.journal['entries'])
        self.assertEqual(resolved['RC-OPINION-B']['record'], prior_opinion)
        self.assertEqual(state['revisions']['PC-RECONSIDERATION-FICTIONAL-ONE'], 4)

    def test_lens_cannot_promote_an_uncompleted_care_stage(self):
        for stage_id, judgment in [('REVIEW-B','second_review'),
                                   ('CORRECTION','correction_authored'),
                                   ('CORRECTION-SENT','correction_dispatched')]:
            case = self.case()
            next(s for s in case['stages'] if s['stage_id'] == stage_id)['status'] = 'unknown'
            self.assertEqual(self.assessment(case, judgment)['status'], 'documented')
            with self.subTest(stage=stage_id), self.assertRaisesRegex(cr.Error, 'same-event care stage'):
                self.validate(case)

    def test_contrary_reviews_cannot_be_omitted_or_silently_promoted(self):
        case, resolved = self.case(), copy.deepcopy(self.resolved)
        for conclusion in ('affirmed', 'rejected'):
            self.record(case, resolved, 'RC-ERROR-' + conclusion, {
                'kind':'clinical_error_review', 'target_opinion_ref':'RC-INITIAL',
                'reviewing_role':'Fictional scoped reviewer', 'basis_refs':['RC-PRIMARY'],
                'finding':'An attributed conclusion about the same proposition.',
                'scope':'One initial opinion proposition.', 'conclusion':conclusion})
        judgment = self.assessment(case, 'clinical_error')
        judgment.update(status='documented', evidence_refs=['RC-ERROR-affirmed'])
        with self.assertRaisesRegex(cr.Error, 'all scoped records'):
            self.validate(case, resolved)
        judgment['evidence_refs'].append('RC-ERROR-rejected')
        with self.assertRaisesRegex(cr.Error, 'not an affirmed finding'):
            self.validate(case, resolved)
        judgment['status'] = 'contested'
        self.validate(case, resolved)
        judgment['status'] = 'unknown'
        self.validate(case, resolved)

    def test_causation_needs_the_actual_report_and_possible_event_order(self):
        for target, report in [('RC-INITIAL','MISSING'), ('RC-INITIAL','RC-POLICY'),
                              ('RC-OPINION-B','RC-REPORT')]:
            case, resolved = self.case(), copy.deepcopy(self.resolved)
            self.record(case, resolved, 'RC-CAUSE', {
                'kind':'causation_review', 'target_opinion_ref':target,
                'harm_report_ref':report, 'reviewing_role':'Fictional reviewer',
                'basis_refs':['RC-PRIMARY'], 'reasoning':'A supplied causal assertion.',
                'scope':'Reported existing burden.', 'conclusion':'affirmed'})
            self.assessment(case, 'harm_causation').update(status='documented', evidence_refs=['RC-CAUSE'])
            with self.subTest(target=target, report=report), self.assertRaises(cr.Error):
                self.validate(case, resolved)

    def test_source_scope_cannot_be_relabelled_to_bypass_a_boundary(self):
        resolved = copy.deepcopy(self.resolved)
        resolved['RC-CORRECTION']['record']['reconsideration'] = {
            'kind':'clinical_error_review', 'target_opinion_ref':'RC-INITIAL',
            'reviewing_role':'Invented role', 'basis_refs':['RC-PRIMARY'], 'finding':'Assertion',
            'scope':'One assertion', 'conclusion':'affirmed'}
        resolved['RC-CORRECTION']['record']['observation_type'] = 'diagnostic_evaluation'
        with self.assertRaisesRegex(cr.Error, 'source record or lineage'):
            self.validate(self.case(), resolved)

    def test_report_cannot_disappear_and_reuse_does_not_add_corroboration(self):
        case = self.case()
        case['reconsideration']['reported_harm_refs'] = []
        with self.assertRaisesRegex(cr.Error, 'Expose every attributed harm report'):
            self.validate(case)
        self.assertEqual(self.state['source_families'],
            {'PC-RECONSIDERATION-FICTIONAL-ONE':['FICTIONAL-RECONSIDERATION-ONE']})

    def test_record_schema_and_history_are_pinned(self):
        schema = copy.deepcopy(self.schema)
        schema['properties']['record']['anyOf'][0]['properties']['description']['minLength'] = 2
        with self.assertRaisesRegex(cr.Error, 'Schema snapshot changed'):
            cr.replay(ROOT, lens_schema=schema)
        journal = copy.deepcopy(self.journal)
        journal['entries'][0]['pathway']['reconsideration']['reported_harm_refs'] = []
        with self.assertRaisesRegex(cr.Error, 'Entry modified'):
            cr.replay(ROOT, journal=journal)

    def test_status_revision_needs_new_scoped_evidence(self):
        journal = copy.deepcopy(self.journal)
        case = self.case()
        self.assessment(case, 'second_review')['status'] = 'unknown'
        journal['entries'].append(care.make_entry(case, sequence=3, recorded_at='2026-11-21T18:02:00Z',
            actor='Negative fixture', reason='Attempt downgrade without new evidence', expected_revision=2,
            previous=journal['entries'][-1]['entry_sha256']))
        with self.assertRaisesRegex(cr.Error, 'new scoped evidence'):
            cr.replay(ROOT, journal=journal)

    def test_projection_preserves_harm_and_distinguishes_completed_report(self):
        rendered = cr.markdown(self.state, self.resolved)
        self.assertIn('Report of psychological burden recorded', rendered)
        self.assertIn('distress and loss of trust', rendered)
        self.assertIn('a recorded harm report is not resolved distress', rendered)
        self.assertIn('clinical error | unknown', rendered)

    def test_saved_replay_is_deterministic(self):
        result = cr.build(ROOT)
        self.assertEqual(result['status'], 'passed')
        self.assertEqual((result['revisions'], result['steps'], result['provider_calls']), (2,10,0))
        self.assertFalse(result['canonical_admission'])


if __name__ == '__main__':
    unittest.main()
