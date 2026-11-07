"""Keep the completed cross-wing cycle reconstructible in ordinary CI."""
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'all_garden_cycle', ROOT / 'reports/all-garden/20261104/replay.py')
PACKET = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKET)


class AllGardenCycleTests(unittest.TestCase):
    def test_all_registered_trees_and_saved_records_reconstruct(self):
        result = PACKET.verify()
        self.assertEqual(result, {
            'status': 'passed', 'lanes': 14, 'trees': 10, 'steps': 140,
            'repository_model_calls': 0, 'reconstructions': 2,
            'canonical_admission': False,
        })
