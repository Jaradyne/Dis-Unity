"""Semantic boundary tests for supplied relay records; no collection or dispatch."""
import copy
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import continuity as shared
import cycle
import garden_runtime as garden
import relays

ROOT = Path(__file__).resolve().parents[1]


class RelayTimeTests(unittest.TestCase):
    def test_timezone_equivalence_and_month_precision_are_preserved(self):
        self.assertEqual(relays.bounds('2026-10-15T16:00:00Z'),
                         relays.bounds('2026-10-15T09:00:00-07:00'))
        lo, hi = relays.bounds('2026-02')
        self.assertEqual(lo.isoformat(), '2026-02-01T00:00:00+00:00')
        self.assertEqual(hi.isoformat(), '2026-02-28T23:59:59.999999+00:00')
        self.assertIsNone(relays.bounds(None))
        for invalid in ('2026-10-15T09:00:00', '2026-02-29', '2026-13', '2026-01-01T25:00:00Z'):
            with self.subTest(invalid=invalid), self.assertRaises(relays.Error):
                relays.bounds(invalid)

    def test_period_rejects_definitely_future_or_reversed_observation(self):
        cutoff = datetime(2026, 10, 15, 12, tzinfo=timezone.utc)
        relays.period({'start': '2026-10', 'end': '2026-10', 'note': 'Month precision'}, cutoff)
        for start, end in [('2026-10-15T12:00:01Z', '2026-10-15T12:00:01Z'),
                           ('2026-11', '2026-11'), ('2026-03-01', '2026-02')]:
            with self.subTest(start=start), self.assertRaises(relays.Error):
                relays.period({'start': start, 'end': end, 'note': 'Invalid synthetic period'}, cutoff)

    def test_deadline_comparison_never_invents_a_deadline_or_false_precision(self):
        relay = {'deadline': None, 'stages': {'arrival': {
            'status': 'received', 'time': {'start': '2026-10-15T09:00:00-07:00',
                                          'end': '2026-10-15T09:00:00-07:00', 'note': 'Fixture'}}}}
        self.assertEqual(relays.timing(relay), {'status': 'no_documented_deadline', 'lag_seconds': None})
        relay['deadline'] = {'at': '2026-10-15T15:00:00Z', 'stage': 'arrival'}
        self.assertEqual(relays.timing(relay), {'status': 'missed', 'lag_seconds': 3600})
        relay['deadline']['at'] = '2026-10-15T16:00:00Z'
        self.assertEqual(relays.timing(relay), {'status': 'met', 'lag_seconds': 0})
        relay['stages']['arrival']['time'].update(start='2026-10', end='2026-10')
        self.assertEqual(relays.timing(relay), {'status': 'unknown', 'lag_seconds': None})
        relay['stages']['arrival']['time'].update(start='2026-11', end='2026-11')
        self.assertEqual(relays.timing(relay), {'status': 'missed', 'lag_seconds': None})
        relay['stages']['arrival']['status'] = 'acknowledged'
        self.assertEqual(relays.timing(relay), {'status': 'unknown', 'lag_seconds': None})


class RelayCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.journal = shared.strict_json(ROOT/relays.JOURNAL)
        cls.schema = shared.strict_json(ROOT/relays.SCHEMA)
        cls.manifest = shared.strict_json(ROOT/relays.REFERENCES)
        cls.state, cls.resolved = relays.replay(ROOT)

    def case(self, cid='DIESEL-RELAYS', first=False):
        if first:
            return copy.deepcopy(next(e['case'] for e in self.journal['entries'] if e['case']['case_id'] == cid))
        return copy.deepcopy(self.state['cases'][cid])

    @staticmethod
    def relay(case, rid):
        return next(r for r in case['relays'] if r['relay_id'] == rid)

    @staticmethod
    def evidence(relay, eid):
        return next(e for e in relay['evidence'] if e['evidence_id'] == eid)

    def validate(self, case):
        return relays.validate(case, self.schema, self.resolved)

    def append(self, case, revision=None, recorded_at=None):
        journal = copy.deepcopy(self.journal)
        journal['entries'].append(relays.make_entry(case, sequence=len(journal['entries'])+1,
            recorded_at=recorded_at or journal['entries'][-1]['recorded_at'], actor='test reviewer',
            reason='Synthetic boundary test only; no empirical admission',
            expected_revision=self.state['revisions'][case['case_id']] if revision is None else revision,
            previous=journal['entries'][-1]['entry_sha256']))
        return journal

    def single(self, case, recorded_at):
        journal = copy.deepcopy(self.journal)
        journal['entries'] = [relays.make_entry(case, sequence=1, recorded_at=recorded_at,
            actor='test reviewer', reason='Synthetic chronological boundary', expected_revision=0,
            previous=shared.ZERO)]
        return journal

    def test_two_cases_keep_empirical_unknowns_and_simulated_recovery_separate(self):
        self.assertEqual(set(self.state['cases']), {'CEM-RELAYS', 'DIESEL-RELAYS'})
        self.assertEqual(self.state['revisions'], {'CEM-RELAYS': 1, 'DIESEL-RELAYS': 2})
        camp, diesel = self.case('CEM-RELAYS'), self.case()
        self.assertEqual(camp['mode'], 'empirical')
        self.assertEqual(diesel['mode'], 'simulated')
        tb = self.relay(camp, 'CEM-TB-NOTICE')
        self.assertEqual(tb['stages']['expected_transfer']['status'], 'inferred_expectation')
        self.assertTrue(all(tb['stages'][s]['status'] == 'unknown' for s in
                            ('dispatch', 'arrival', 'action', 'outcome', 'verification')))
        self.assertTrue(all(v['status'] == 'no_documented_deadline'
                            for v in self.state['timing']['CEM-RELAYS'].values()))
        primary = self.relay(diesel, 'DIESEL-PRIMARY')
        self.assertEqual(primary['issues'][0]['mechanism'], 'physical_resource')
        self.assertEqual(primary['stages']['arrival']['status'], 'unknown')
        self.assertTrue(all(s['status'] == 'proposed' for s in self.case(first=True)['supports']))
        self.assertTrue(all(s['status'] == 'verified' for s in diesel['supports']))
        self.assertEqual(self.state['timing']['DIESEL-RELAYS']['DIESEL-RESUPPLY'],
                         {'status': 'missed', 'lag_seconds': 1800})

    def test_announcements_and_commitments_are_not_actual_dispatch(self):
        for eid in ('R-ALLOCATION', 'R-COMMIT'):
            case = self.case(first=True)
            relay = self.relay(case, 'DIESEL-RESUPPLY')
            relay['stages']['dispatch'].update(status='performed', evidence_ids=[eid])
            with self.subTest(eid=eid), self.assertRaisesRegex(relays.Error, 'stage-specific'):
                self.validate(case)

    def test_acknowledgment_is_neither_physical_arrival_nor_action(self):
        for stage, status in [('arrival', 'received'), ('action', 'performed')]:
            case = self.case()
            relay = self.relay(case, 'DIESEL-PRIMARY')
            self.evidence(relay, 'P-ACK')['stages'].append(stage)
            relay['stages'][stage].update(status=status, evidence_ids=['P-ACK'])
            with self.subTest(stage=stage), self.assertRaisesRegex(relays.Error, 'stage-specific'):
                self.validate(case)

    def test_delivery_is_not_a_protective_or_service_outcome(self):
        case = self.case()
        relay = self.relay(case, 'DIESEL-RESUPPLY')
        self.evidence(relay, 'R-RECEIPT')['stages'] += ['outcome', 'verification']
        for stage in ('outcome', 'verification'):
            relay['stages'][stage]['evidence_ids'] = ['R-RECEIPT']
        with self.assertRaisesRegex(relays.Error, 'stage-specific'):
            self.validate(case)

    def test_missing_evidence_does_not_become_an_omission_or_nonresponse(self):
        case = self.case(first=True)
        relay = self.relay(case, 'DIESEL-PRIMARY')
        self.evidence(relay, 'P-ACK')['stages'].append('arrival')
        relay['stages']['arrival'].update(status='not_received', evidence_ids=['P-ACK'])
        with self.assertRaisesRegex(relays.Error, 'stage-specific'):
            self.validate(case)
        case = self.case(first=True)
        relay = self.relay(case, 'DIESEL-RESUPPLY')
        self.evidence(relay, 'R-ALLOCATION')['stages'].append('action')
        relay['issues'].append({'kind': 'non_response', 'stage': 'action', 'mechanism': 'unknown',
            'claim': 'Synthetic unsupported silence inference', 'evidence_ids': ['R-ALLOCATION']})
        with self.assertRaisesRegex(relays.Error, 'specific failure evidence'):
            self.validate(case)

    def test_evidence_polarity_cannot_invert_action_failure_or_recovery(self):
        for rid, eid, result in [('DIESEL-PRIMARY', 'P-NODISPATCH', 'positive'),
                                 ('DIESEL-RESUPPLY', 'R-DISPATCH', 'negative'),
                                 ('DIESEL-RESUPPLY', 'R-SERVICE', 'negative'),
                                 ('DIESEL-BATTERY', 'B-SERVICE', 'context')]:
            case = self.case()
            relay = self.relay(case, rid)
            self.evidence(relay, eid)['result'] = result
            if eid == 'R-DISPATCH':
                # Isolate the changed record: the fixture also has a separate
                # positive movement observation that can support dispatch.
                relay['stages']['dispatch']['evidence_ids'] = [eid]
            with self.subTest(eid=eid), self.assertRaisesRegex(relays.Error, 'stage-specific'):
                self.validate(case)
        case = self.case()
        self.relay(case, 'DIESEL-RESUPPLY')['stages']['outcome']['status'] = 'failed'
        with self.assertRaisesRegex(relays.Error, 'stage-specific'):
            self.validate(case)

    def test_verification_needs_method_and_same_scoped_outcome_evidence(self):
        for mutation in ('method', 'wrong_outcome', 'unknown_outcome'):
            case = self.case()
            relay = self.relay(case, 'DIESEL-RESUPPLY')
            if mutation == 'method':
                relay['stages']['verification']['method'] = None
            elif mutation == 'wrong_outcome':
                alternate = copy.deepcopy(self.evidence(relay, 'R-SERVICE'))
                alternate['evidence_id'] = 'UNRELATED-OUTCOME'
                alternate['claim'] = 'Different test scope, not the assessed result'
                relay['evidence'].append(alternate)
                relay['stages']['verification']['evidence_ids'] = ['UNRELATED-OUTCOME']
            else:
                relay['stages']['outcome']['status'] = 'unknown'
            with self.subTest(mutation=mutation), self.assertRaises(relays.Error):
                self.validate(case)

    def test_capacity_shortage_is_not_relabelled_as_communication_failure(self):
        case = self.case()
        self.relay(case, 'DIESEL-PRIMARY')['issues'][0]['mechanism'] = 'communication'
        with self.assertRaisesRegex(relays.Error, 'Physical resource shortfall'):
            self.validate(case)
        case = self.case()
        primary = self.relay(case, 'DIESEL-PRIMARY')
        primary['issues'][0].update(kind='non_transmission', mechanism='communication')
        with self.assertRaisesRegex(relays.Error, 'specific failure evidence'):
            self.validate(case)
        case = self.case()
        self.evidence(self.relay(case, 'DIESEL-PRIMARY'), 'P-STOCK')['result'] = 'positive'
        with self.assertRaisesRegex(relays.Error, 'specific failure evidence'):
            self.validate(case)

    def test_capacity_basis_preserves_announcement_commitment_and_measurement(self):
        for wrong in ('observed', 'committed', 'required'):
            case = self.case()
            self.relay(case, 'DIESEL-RESUPPLY')['capacities'][0]['basis'] = wrong
            with self.subTest(basis=wrong), self.assertRaisesRegex(relays.Error, 'matching evidence class'):
                self.validate(case)
        case = self.case()
        self.relay(case, 'DIESEL-BATTERY')['capacities'][0]['value'] = '-1'
        with self.assertRaises(relays.Error):
            self.validate(case)

    def test_deadline_requires_positive_applicable_obligation(self):
        for mutation in ('announcement', 'negative', 'wrong_stage'):
            case = self.case()
            relay = self.relay(case, 'DIESEL-RESUPPLY')
            item = copy.deepcopy(self.evidence(relay, 'R-COMMIT'))
            item['evidence_id'] = 'TEST-DEADLINE'
            if mutation == 'announcement': item['kind'] = 'announcement'
            elif mutation == 'negative': item['result'] = 'negative'
            else: item['stages'] = ['dispatch']
            relay['evidence'].append(item)
            relay['deadline']['evidence_ids'] = ['TEST-DEADLINE']
            with self.subTest(mutation=mutation), self.assertRaisesRegex(relays.Error, 'Deadline needs'):
                self.validate(case)

    def test_cutoff_rejects_later_evidence_and_later_action_without_hiding_unknown_time(self):
        for target in ('evidence', 'stage'):
            case = self.case(first=True)
            relay = self.relay(case, 'DIESEL-RESUPPLY')
            period = relay['evidence'][0]['observed'] if target == 'evidence' else relay['stages']['dispatch']['time']
            period.update(start='2026-10-01T08:20:01Z', end='2026-10-01T08:20:01Z')
            with self.subTest(target=target), self.assertRaisesRegex(relays.Error, 'after cutoff'):
                self.validate(case)
        case = self.case(first=True)
        case['evidence_cutoff'] = '2026-10'
        with self.assertRaisesRegex(relays.Error, 'Cutoff needs'):
            self.validate(case)

    def test_review_cannot_predate_evidence_or_use_naive_clock_time(self):
        for stamp in ('2026-09-30T12:00:00Z', '2026-10-16T05:06:03'):
            with self.subTest(stamp=stamp), self.assertRaises(relays.Error):
                relays.replay(ROOT, journal=self.single(self.case(first=True), stamp))
        case = self.case(first=True)
        case['evidence_cutoff'] = '2026-10-01'
        with self.assertRaisesRegex(relays.Error, 'after cutoff'):
            relays.replay(ROOT, journal=self.single(case, '2026-10-01T08:00:00Z'))

    def test_review_instant_limits_stage_and_capacity_times_inside_a_day_cutoff(self):
        for target in ('stage', 'capacity'):
            case = self.case()
            case['evidence_cutoff'] = '2026-10-16'
            if target == 'stage':
                period = self.relay(case, 'DIESEL-RESUPPLY')['stages']['arrival']['time']
            else:
                period = self.relay(case, 'DIESEL-BATTERY')['capacities'][0]['time']
            period.update(start='2026-10-16T12:00:00Z', end='2026-10-16T12:00:00Z')
            with self.subTest(target=target), self.assertRaisesRegex(relays.Error, 'after cutoff'):
                relays.replay(ROOT, journal=self.single(case, '2026-10-16T05:06:03Z'))

    def test_empirical_and_simulated_sources_or_events_cannot_cross(self):
        for cid, wrong_source in [('CEM-RELAYS', 'S-SIM-DIESEL'), ('DIESEL-RELAYS', 'S-GAO-CEM')]:
            case = self.case(cid)
            case['relays'][0]['evidence'][0]['citations'][0]['source_ref'] = wrong_source
            with self.subTest(case=cid), self.assertRaisesRegex(relays.Error, 'source crossing'):
                self.validate(case)
        case = self.case()
        case['event_refs'].append('E-CEM13')
        with self.assertRaisesRegex(relays.Error, 'event crossing'):
            self.validate(case)
        case = self.case('CEM-RELAYS')
        case['relays'][0]['evidence'][0]['citations'][0]['source_ref'] = 'D-GAO-CEM'
        with self.assertRaisesRegex(relays.Error, 'Unknown source'):
            self.validate(case)

    def test_alias_hash_parent_and_path_tampering_fail(self):
        for mutation in ('base_hash', 'source_hash', 'artifact_hash', 'shadow', 'bad_alias',
                         'parent', 'base_escape', 'source_escape', 'document_escape'):
            manifest = copy.deepcopy(self.manifest)
            if mutation == 'base_hash': manifest['base']['sha256'] = shared.ZERO
            elif mutation == 'source_hash': manifest['references']['S-SIM-DIESEL']['sha256'] = shared.ZERO
            elif mutation == 'artifact_hash': manifest['documents']['D-GAO-CEM']['sha256'] = shared.ZERO
            elif mutation == 'shadow': manifest['references']['S-GAO-CEM'] = manifest['references']['S-SIM-DIESEL']
            elif mutation == 'bad_alias': manifest['documents']['invalid alias'] = manifest['documents']['D-GAO-CEM']
            elif mutation == 'parent': manifest['documents']['D-GAO-CEM']['parent_source_ref'] = 'S-ORA'
            elif mutation == 'base_escape': manifest['base']['path'] = '../outside.json'
            elif mutation == 'source_escape': manifest['references']['S-SIM-DIESEL']['path'] = '../outside.json'
            else: manifest['documents']['D-GAO-CEM']['path'] = '../outside.pdf'
            with self.subTest(mutation=mutation), self.assertRaises(relays.Error):
                relays.resolve(ROOT, manifest)

    def test_journal_mutation_reordering_stale_writer_and_schema_drift_fail(self):
        journal = copy.deepcopy(self.journal)
        journal['entries'][0]['case']['title'] = 'Rewritten history'
        with self.assertRaisesRegex(relays.Error, 'Entry modified'):
            relays.replay(ROOT, journal=journal)
        journal = copy.deepcopy(self.journal)
        journal['entries'][0], journal['entries'][1] = journal['entries'][1], journal['entries'][0]
        with self.assertRaisesRegex(relays.Error, 'Sequence mismatch'):
            relays.replay(ROOT, journal=journal)
        with self.assertRaisesRegex(relays.Error, 'Stale case revision'):
            relays.replay(ROOT, journal=self.append(self.case(), revision=0))
        with self.assertRaisesRegex(relays.Error, 'snapshot mismatch'):
            relays.replay(ROOT, schema={**self.schema, 'title': 'Different contract'})

    def test_revision_cannot_erase_evidence_context_identity_or_support_edges(self):
        for mutation in ('evidence', 'contrary_evidence', 'ordinary_explanations', 'issues',
                         'capacities', 'scope', 'relay_identity', 'design_refs', 'supports'):
            case = self.case()
            relay = self.relay(case, 'DIESEL-PRIMARY')
            if mutation in ('evidence', 'contrary_evidence', 'ordinary_explanations', 'issues', 'capacities'):
                relay[mutation][0]['claim' if mutation not in ('capacities',) else 'limits'] = 'Replaced historical content'
            elif mutation == 'scope': case['scope'] = 'A different case scope'
            elif mutation == 'relay_identity': relay['from_actor'] = 'A different sender'
            elif mutation == 'design_refs': case['design_refs'] = []
            else: case['supports'] = []
            with self.subTest(mutation=mutation), self.assertRaises(relays.Error):
                relays.replay(ROOT, journal=self.append(case))
        case = self.case()
        self.relay(case, 'DIESEL-RESUPPLY')['stages']['arrival']['claim'] = 'Unexplained assessment rewrite'
        with self.assertRaisesRegex(relays.Error, 'new evidence or counterassessment'):
            relays.replay(ROOT, journal=self.append(case))

    def test_reviewed_revision_keeps_old_unknowns_failures_and_evidence_inspectable(self):
        first, latest = self.case(first=True), self.case()
        original, later = self.state['history'][1], self.state['history'][2]
        self.assertEqual(original['unknowns'], first['unknowns'])
        self.assertEqual(later['unknowns'], latest['unknowns'])
        self.assertNotEqual(original['unknowns'], later['unknowns'])
        self.assertEqual(original['supports'], first['supports'])
        self.assertEqual(later['supports'], latest['supports'])
        for old in first['relays']:
            new = self.relay(latest, old['relay_id'])
            self.assertEqual(new['evidence'][:len(old['evidence'])], old['evidence'])
            self.assertEqual(new['issues'][:len(old['issues'])], old['issues'])
        case = self.case()
        case['unknowns'] = ['A reviewed residual expressed more narrowly; old residual stays in history.']
        state, _ = relays.replay(ROOT, journal=self.append(case))
        self.assertEqual(state['history'][:-1], self.state['history'])
        self.assertEqual(state['history'][-1]['unknowns'], case['unknowns'])

    def test_chronology_does_not_prove_causation_or_generalize_a_case(self):
        case = self.case()
        relay = self.relay(case, 'DIESEL-RESUPPLY')
        relay['causal_assessment'].update(status='supported', evidence_ids=['R-DISPATCH', 'R-RECEIPT'])
        with self.assertRaisesRegex(relays.Error, 'Sequence is not causation'):
            self.validate(case)
        item = copy.deepcopy(self.evidence(relay, 'R-SERVICE'))
        item.update(evidence_id='TEST-CAUSAL', kind='causal_analysis', result='negative')
        relay['evidence'].append(item)
        relay['causal_assessment']['evidence_ids'] = ['TEST-CAUSAL']
        with self.assertRaisesRegex(relays.Error, 'Sequence is not causation'):
            self.validate(case)
        case = self.case()
        case['generalization'] = 'systemic_pattern'
        with self.assertRaises(relays.Error):
            self.validate(case)

    def test_working_buffer_needs_observed_action_or_verified_outcome(self):
        for status in ('used', 'verified'):
            case = self.case(first=True)
            case['supports'][1]['status'] = status
            with self.subTest(status=status), self.assertRaisesRegex(relays.Error, 'buffer needs'):
                self.validate(case)
        case = self.case()
        self.relay(case, 'DIESEL-BATTERY')['stages']['verification']['status'] = 'contested'
        with self.assertRaisesRegex(relays.Error, 'Working buffer needs'):
            self.validate(case)

    def test_same_schema_accepts_renamed_domain_without_name_based_rules(self):
        case = self.case()
        case.update(case_id='RELAYS-EXERCISE', title='Domain-neutral relay exercise')
        mapping = {r['relay_id']: 'TRANSFER-'+str(i) for i, r in enumerate(case['relays'], 1)}
        for relay in case['relays']:
            relay['relay_id'] = mapping[relay['relay_id']]
            relay['from_actor'], relay['to_actor'] = 'Role A', 'Role B'
        for support in case['supports']:
            for field in ('relay_id', 'supports_relay'):
                support[field] = mapping[support[field]]
        self.validate(case)
        with self.assertRaises(relays.Error):
            self.validate({**case, 'facility_risk_score': 100})

    def test_saved_outputs_replay_deterministically_without_independent_evidence_or_dispatch(self):
        first, second = relays.outputs(ROOT), relays.outputs(ROOT)
        self.assertEqual(first, second)
        self.assertEqual(relays.build(ROOT, check=True), 4)
        for cid in self.state['cases']:
            document = shared.strict_json(ROOT/relays.OUTPUT/'garden'/f'{cid}.json')
            with self.subTest(case=cid):
                self.assertEqual(garden.replay(document), document)
                commands = [event['command'] for event in document['events']]
                self.assertEqual([c['node'] for c in commands], garden.NODES)
                self.assertEqual(set(document['state']['branches']), {'B0'})
                self.assertEqual(document['state']['branches']['B0']['status'], 'resting')
                self.assertEqual(document['initial']['packet']['budget']['model_calls'], 0)
                cross = next(c['output'] for c in commands if c['node'] == 'CROSS')
                self.assertEqual(cross['independent'], [])
                self.assertEqual(document['initial']['packet']['budget']['max_fanout'], 0)


if __name__ == '__main__':
    unittest.main()
