from pathlib import Path
import copy
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import cycle
import governor
import meaning_boss

ROOT = Path(__file__).resolve().parents[1]


class GovernorBossTests(unittest.TestCase):
    def test_real_packet_reaches_governor_without_power_or_evidence_mutation(self):
        packet = cycle.read_json(ROOT / 'examples/meaning-tower/parallax-trucks-2026-09-25.json')
        original = copy.deepcopy(packet)
        result = {'schema_version': meaning_boss.RESULT_VERSION, 'packet_id': packet['packet_id'],
                  'packet_sha256': cycle.digest(packet), 'play_id': 'TEST-GOVERNOR-1',
                  'actor': {'name': 'Automated verifier, not Jared', 'runtime': 'unittest'},
                  'completed_at': '2026-09-25T22:00:00Z', 'completion_status': 'completed',
                  'choices': [{'round_id': r['id'], 'preserved_id': r['pieces'][0]['id'],
                               'held_ms': 1900, 'input_method': 'keyboard'} for r in packet['rounds']],
                  'power_decision': 'pending_review', 'evidence_changed': False}
        review = governor.prepare(ROOT, boss_packet=packet, boss_result=result)
        self.assertEqual(review['inputs']['boss_encounter']['applied_powers'], [])
        self.assertFalse(review['inputs']['boss_encounter']['evidence_changed'])
        self.assertEqual(review['inputs']['voice']['mode'], 'tamarian_with_plain_gloss')
        self.assertIn('daily_scroll', review['inputs'])
        self.assertEqual(packet, original)
        with self.assertRaises(cycle.CycleError):
            governor.prepare(ROOT, boss_packet=packet)


if __name__ == '__main__':
    unittest.main()
