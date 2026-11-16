"""Retained public receipts and a clearly labeled simulated repeat."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('eia_followup', ROOT / 'reports/followups/20261113/verify_packet.py')
eia = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eia)


class EiaFollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = eia.reconstruct(ROOT)

    def test_saved_replay(self):
        for name, record in self.result.items():
            self.assertEqual((ROOT / eia.CASE / name).read_bytes(), eia.encode(record))

    def test_repeat_does_not_queue_work_or_claim_independence(self):
        result = self.result['arrival-output.json']
        self.assertEqual([r['decision'] for r in result['observations']],
                         ['first_observation', 'unchanged', 'changed_version'])
        self.assertEqual(len(result['review_queue']), 2)
        self.assertTrue(all(r['status'] == 'awaiting_review' for r in result['review_queue']))
        self.assertEqual(result['automatic_findings'], [])
        self.assertEqual(result['independent_source_families'], ['EIA'])

    def test_return_to_old_version_does_not_duplicate_work(self):
        items = deepcopy(self.result['arrival-output.json']['observations'])
        old = deepcopy(items[0]); old['observation_id'] = 'SIMULATED-RETURN-TO-OLD'
        old['source_observed_at'] = items[-1]['source_observed_at']
        # A unit-test synthetic input, never added to the recorded observation journal.
        items.append(old)
        result = eia.detect(items)
        self.assertEqual(result['observations'][-1]['decision'], 'previously_seen_version')
        self.assertEqual(len(result['review_queue']), 2)

    def test_changed_bytes_cannot_be_labeled_unchanged_fixture(self):
        items = deepcopy(self.result['arrival-output.json']['observations'])
        items[1]['body_sha256'] = '0' * 64
        with self.assertRaises(eia.shared.ContinuityError):
            eia.detect(items)

    def test_wrong_identity_and_reversed_receipt_time_rejected(self):
        for field, value in [('source_family', 'OTHER'), ('url', 'https://example.com'),
                             ('source_observed_at', '2000-01-01T00:00:00Z')]:
            items = deepcopy(self.result['arrival-output.json']['observations'])
            items[-1][field] = value
            with self.assertRaises(eia.shared.ContinuityError):
                eia.detect(items)

    def test_receipt_tampering_and_incompleteness_rejected(self):
        packet = eia.shared.strict_json(ROOT / eia.CASE / 'packet.json')
        original = eia.shared.strict_json(ROOT / packet['current']['receipt']['path'])
        for mode in ('bytes', 'incomplete'):
            record = deepcopy(original)
            if mode == 'bytes':
                record['response']['body']['content'] = 'aW52YWxpZA=='
            else:
                record['response']['body']['complete'] = False
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'receipt.json'; raw = eia.encode(record); path.write_bytes(raw)
                binding = {'path':'receipt.json', 'sha256':eia.arrival.sha(raw)}
                with self.assertRaises(eia.shared.ContinuityError):
                    eia.receipt(Path(tmp), binding, eia.FORECAST_URL)

    def test_monthly_and_annual_remain_distinct(self):
        data = self.result['diesel-data.json']
        rows = data['monthly_forecast']['rows']
        self.assertEqual([r['month'] for r in rows], ['2026-11', '2026-12', '2027-01'])
        self.assertAlmostEqual(rows[-1]['current_usd_per_us_gallon'], 5.549171)
        self.assertEqual(data['annual_forecast']['current'], 5.03)
        self.assertEqual(data['weekly_actual']['observation_date'], '2026-11-09')


if __name__ == '__main__':
    unittest.main()
