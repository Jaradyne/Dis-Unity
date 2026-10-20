"""Bounded shelter-wing checks; fictional screens never establish legal findings."""
import copy
from datetime import datetime, timedelta, timezone
import json
import shutil
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import continuity as shared
import garden_runtime as garden
import relays
import safeguards
import shelter_accountability as shelter

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('operations/shelter-accountability')
REHEARSALS = Path('examples/shelter-accountability/notice-rehearsals.json')
NOTICE_SCHEMA = Path('schemas/shelter-notice-rehearsal.schema.json')


class NoticeScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = shared.strict_json(ROOT/REHEARSALS)
        cls.schema = shared.strict_json(ROOT/NOTICE_SCHEMA)

    def packet(self, case_id='SIM-SEVEN-DAY'):
        return copy.deepcopy(next(p for p in self.fixtures['cases'] if p['case_id'] == case_id))

    def screen(self, packet):
        result = shelter.notice_screen(packet, schema=self.schema)
        self.assertEqual(result['mode'], 'simulated')
        self.assertEqual(result['legal_finding'], 'not_determined')
        self.assertEqual(result['fraud_finding'], 'not_assessed')
        self.assertEqual(result['protective_outcome'], 'unknown')
        return result

    def test_short_and_thirty_day_intervals_are_triage_not_legal_or_safety_findings(self):
        short = self.screen(self.packet())
        full = self.screen(self.packet('SIM-THIRTY-DAY'))
        self.assertEqual((short['calendar_interval_days'], short['status']), (7, 'short_interval_review_required'))
        self.assertEqual((full['calendar_interval_days'], full['status']), (30, 'no_interval_flag'))
        for result in (short, full):
            self.assertTrue(result['limits'])
            self.assertNotIn(result['status'], ('lawful', 'unlawful', 'compliant', 'protected'))

    def test_each_unknown_or_excluded_scope_element_blocks_standard_interval_conclusion(self):
        for field in self.packet()['scope']:
            for value, status in [('unknown', 'coverage_unknown'), ('excluded', 'other_framework_review_required')]:
                packet = self.packet()
                packet['scope'][field] = value
                with self.subTest(field=field, value=value):
                    self.assertEqual(self.screen(packet)['status'], status)

    def test_asserted_exceptions_require_evidence_and_unknowns_stay_unknown(self):
        for field in ('direct_threat', 'self_exit', 'short_extension'):
            for value, status in [('asserted', 'exception_evidence_review_required'), ('unknown', 'exception_unknown')]:
                packet = self.packet()
                packet['exceptions'][field] = value
                with self.subTest(field=field, value=value):
                    self.assertEqual(self.screen(packet)['status'], status)

    def test_exigent_paperwork_never_waives_the_notice_interval_screen(self):
        for value in ('asserted', 'unknown'):
            packet = self.packet()
            packet['exceptions']['exigent_paperwork'] = value
            with self.subTest(value=value):
                result = self.screen(packet)
                self.assertEqual(result['status'], 'short_interval_review_required')
                self.assertTrue(result['review_flags'])

    def test_conversion_and_legal_version_need_review_even_if_interval_is_thirty_days(self):
        for value in ('yes', 'unknown'):
            packet = self.packet('SIM-THIRTY-DAY')
            packet['permanent_conversion'] = value
            with self.subTest(conversion=value):
                self.assertEqual(self.screen(packet)['status'], 'conversion_review_required')
        packet = self.packet('SIM-THIRTY-DAY')
        packet['legal_version'] = 'unknown'
        self.assertEqual(self.screen(packet)['status'], 'legal_version_review_required')
        packet = self.packet()
        packet['notice'].update(delivered_on='2025-12-01', proposed_exit_on='2026-01-15')
        self.assertEqual(self.screen(packet)['status'], 'legal_version_review_required')

    def test_missing_service_or_dates_do_not_become_observed_service(self):
        for missing in ('delivered_on', 'proposed_exit_on', 'service_basis'):
            packet = self.packet()
            packet['notice'][missing] = 'unknown' if missing == 'service_basis' else None
            with self.subTest(missing=missing):
                result = self.screen(packet)
                self.assertEqual(result['status'], 'date_unknown')

    def test_invalid_reversed_or_falsely_precise_dates_fail(self):
        for delivered, exit_on in [('2026-02-29', '2026-03-30'), ('2026-10-02', '2026-10-01'),
                                   ('2026-10', '2026-10-31'), ('2026-10-01T09:00:00Z', '2026-10-31')]:
            packet = self.packet()
            packet['notice'].update(delivered_on=delivered, proposed_exit_on=exit_on)
            with self.subTest(delivered=delivered), self.assertRaises((shared.ContinuityError, ValueError)):
                self.screen(packet)

    def test_calendar_boundaries_are_explicit_and_not_a_statutory_clock_decision(self):
        for exit_on, days, status in [('2026-10-01', 0, 'short_interval_review_required'),
                                      ('2026-10-30', 29, 'short_interval_review_required'),
                                      ('2026-10-31', 30, 'no_interval_flag')]:
            packet = self.packet()
            packet['notice']['proposed_exit_on'] = exit_on
            with self.subTest(days=days):
                result = self.screen(packet)
                self.assertEqual((result['calendar_interval_days'], result['status']), (days, status))

    def test_content_gaps_and_unknowns_survive_a_long_notice_interval(self):
        packet = self.packet('SIM-THIRTY-DAY')
        packet['content']['grievance_information'] = 'absent'
        packet['content']['accommodation_information'] = 'unknown'
        result = self.screen(packet)
        self.assertEqual(result['status'], 'no_interval_flag')
        self.assertIn('grievance_information', result['content_gaps'])
        self.assertIn('accommodation_information', result['content_unknowns'])
        self.assertNotIn('accommodation_information', result['content_gaps'])
        self.assertNotIn('plain_language_reasons', result['content_gaps'])
        self.assertTrue(result['review_flags'])

    def test_schema_rejects_empirical_relabelling_untyped_assumptions_and_unrequested_details(self):
        for mutation in ('mode', 'scope_boolean', 'unknown_field', 'missing_refs', 'missing_scope', 'case_identity', 'record_identity'):
            packet = self.packet()
            if mutation == 'mode': packet['mode'] = 'empirical'
            elif mutation == 'scope_boolean': packet['scope']['public_funding'] = True
            elif mutation == 'unknown_field': packet['resident_name'] = 'Synthetic extra field'
            elif mutation == 'missing_refs': packet['record_refs'] = []
            elif mutation == 'missing_scope': del packet['scope']['public_oversight']
            elif mutation == 'case_identity': packet['case_id'] = 'REAL-NOTICE'
            else: packet['record_refs'] = ['ACTUAL-NOTICE']
            with self.subTest(mutation=mutation), self.assertRaises(shared.ContinuityError):
                self.screen(packet)

    def test_replay_is_deterministic_and_does_not_mutate_supplied_fixture(self):
        packet = self.packet()
        before = copy.deepcopy(packet)
        first, second = self.screen(packet), self.screen(packet)
        self.assertEqual(first, second)
        self.assertEqual(packet, before)
        self.assertEqual(first['record_refs'], packet['record_refs'])
        for packet in self.fixtures['cases']:
            with self.subTest(case_id=packet['case_id']):
                self.screen(copy.deepcopy(packet))


    def test_result_edits_cannot_mutate_original_fixture_record_refs(self):
        packet = self.packet()
        before = copy.deepcopy(packet)
        result = self.screen(packet)
        result['record_refs'].append('FICT-RESULT-ONLY')
        self.assertEqual(packet, before)


class ShelterWingTests(unittest.TestCase):
    def test_formal_baseline_remains_separate_from_practice_failure_and_protection(self):
        journal = shared.strict_json(ROOT/BASE/'safeguard-journal.json')
        manifest = shared.strict_json(ROOT/BASE/'safeguard-references.json')
        state, resolved = safeguards.replay(ROOT, journal=journal, manifest=manifest)
        self.assertEqual(len(state['safeguards']), 1)
        record = next(iter(state['safeguards'].values()))
        self.assertEqual(record['formal']['status'], 'documented')
        self.assertTrue(all(x['status'] == 'unknown' for x in record['operational'].values()))
        self.assertEqual(record['effectiveness']['status'], 'unknown')
        self.assertEqual(record['failure']['status'], 'unknown')
        for dimension, status in [('effectiveness', 'observed'), ('failure', 'documented')]:
            bad = copy.deepcopy(record)
            bad[dimension].update(status=status, evidence_ids=['CA-NOTICE'])
            with self.subTest(dimension=dimension), self.assertRaises(shared.ContinuityError):
                safeguards.validate(bad, shared.strict_json(ROOT/safeguards.SCHEMA), resolved)

    def test_documented_relay_duties_do_not_establish_real_notice_or_remedy(self):
        journal = shared.strict_json(ROOT/BASE/'relay-journal.json')
        manifest = shared.strict_json(ROOT/BASE/'relay-references.json')
        state, resolved = relays.replay(ROOT, journal=journal, manifest=manifest)
        case = next(iter(state['cases'].values()))
        self.assertEqual(case['mode'], 'empirical')
        for relay in case['relays']:
            self.assertEqual(relay['stages']['expected_transfer']['status'], 'documented')
            self.assertTrue(all(relay['stages'][s]['status'] == 'unknown' for s in
                                ('origin', 'dispatch', 'arrival', 'action', 'outcome', 'verification')))
        bad = copy.deepcopy(case)
        bad['relays'][0]['stages']['dispatch'].update(status='performed', evidence_ids=['CA-NOTICE'])
        with self.assertRaises(shared.ContinuityError):
            relays.validate(bad, shared.strict_json(ROOT/relays.SCHEMA), resolved)

    def test_shared_source_snapshot_and_artifact_tampering_are_rejected(self):
        for mutation in ('record', 'base', 'artifact', 'escape'):
            manifest = shared.strict_json(ROOT/BASE/'relay-references.json')
            if mutation == 'base': manifest['base']['sha256'] = '0'*64
            elif mutation == 'artifact': manifest['documents']['D-SC01']['sha256'] = '0'*64
            elif mutation == 'escape': manifest['documents']['D-SC01']['path'] = '../outside.json'
            else:
                manifest = shared.strict_json(ROOT/BASE/'safeguard-references.json')
                manifest['references']['S-SC01']['sha256'] = '0'*64
            with self.subTest(mutation=mutation), self.assertRaises(shared.ContinuityError):
                if mutation == 'record': safeguards.resolve(ROOT, manifest)
                else: relays.resolve(ROOT, manifest)

    def test_wing_reuses_homelessness_tree_without_mutating_shared_module_routes(self):
        before = (safeguards.JOURNAL, safeguards.REFERENCES, relays.JOURNAL, relays.REFERENCES)
        state, _ = shelter.replay(ROOT)
        self.assertEqual(state['wing']['tree'], 'HOMELESSNESS')
        self.assertEqual(state['wing']['legal_version']['current_official_text_verified'], False)
        self.assertEqual(before, (safeguards.JOURNAL, safeguards.REFERENCES, relays.JOURNAL, relays.REFERENCES))

    def test_pinned_input_drift_fails_before_reassessing_a_changed_wing(self):
        pins = shared.strict_json(ROOT/BASE/'inputs.json')
        with tempfile.TemporaryDirectory() as folder:
            temp = Path(folder)
            for relative in [str(BASE/'inputs.json'), *pins['sha256']]:
                destination = temp/relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/relative, destination)
            wing_path = temp/BASE/'wing.json'
            wing = shared.strict_json(wing_path)
            wing['legal_version']['current_official_text_verified'] = True
            wing_path.write_text(json.dumps(wing))
            with self.assertRaisesRegex(shared.ContinuityError, 'Pinned shelter input changed'):
                shelter.replay(temp)

    def test_garden_uses_latest_review_instant_across_timezones(self):
        state, resolved = shelter.replay(ROOT)
        stamps = [state['wing']['recorded_at']] + [h['recorded_at']
            for key in ('safeguards', 'relays') for h in state[key]['history']]
        latest = max(datetime.fromisoformat(s.replace('Z', '+00:00')) for s in stamps)
        later = latest.astimezone(timezone.utc) + timedelta(hours=1)
        state['wing']['recorded_at'] = later.astimezone(timezone(timedelta(hours=-12))).isoformat()
        document = shelter.garden_pass(ROOT, state, resolved)
        selected = datetime.fromisoformat(document['events'][0]['recorded_at'].replace('Z', '+00:00'))
        self.assertEqual(selected.astimezone(timezone.utc), later)
        for invalid in ('2026-10-20', '2026-10-20T06:30:00'):
            state['wing']['recorded_at'] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(shared.ContinuityError):
                shelter.garden_pass(ROOT, state, resolved)

    def test_one_saved_garden_pass_replays_with_fictional_screening_kept_separate(self):
        first, second = shelter.outputs(ROOT), shelter.outputs(ROOT)
        self.assertEqual(first, second)
        self.assertEqual(shelter.build(ROOT, check=True), len(first))
        passes = []
        for blob in first.values():
            try: document = json.loads(blob)
            except (ValueError, UnicodeDecodeError): continue
            if isinstance(document, dict) and 'initial' in document and 'events' in document:
                passes.append(document)
        self.assertEqual(len(passes), 1)
        doc = passes[0]
        self.assertEqual(garden.replay(doc), doc)
        self.assertEqual(doc['initial']['packet']['tree'], 'HOMELESSNESS')
        self.assertEqual(doc['initial']['packet']['budget']['model_calls'], 0)
        self.assertEqual(doc['initial']['packet']['budget']['max_fanout'], 0)
        self.assertEqual(set(doc['state']['branches']), {'B0'})
        self.assertEqual(doc['state']['branches']['B0']['status'], 'resting')
        commands = [e['command'] for e in doc['events']]
        self.assertEqual([c['node'] for c in commands], garden.NODES)
        self.assertEqual(next(c['output'] for c in commands if c['node'] == 'CROSS')['independent'], [])


if __name__ == '__main__':
    unittest.main()
