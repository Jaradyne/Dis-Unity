"""Public incident scope, attribution and supplemental-tree regression checks."""
import copy
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import continuity as shared
import garden_runtime as garden
import garden_tree

spec = importlib.util.spec_from_file_location('information_integrity_packet',
    ROOT / 'reports/information-integrity/20261028/verify_packet.py')
packet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packet)


class InformationIntegrityTests(unittest.TestCase):
    def test_public_case_replays_offline_and_preserves_attribution_limits(self):
        with patch('socket.create_connection', side_effect=AssertionError('No network in replay')):
            result = packet.verify()
        self.assertEqual(result['case_status'], 'historical_source_reported')
        case = shared.strict_json(ROOT / packet.CASE)
        self.assertEqual(case['observations']['messages']['status'], 'source_reported')
        self.assertEqual(case['observations']['source_attribution']['status'], 'source_assessed')
        for axis in ('automation', 'coordination', 'operator_or_sponsor',
                     'audience_exposure', 'protective_result'):
            self.assertEqual(case['observations'][axis]['status'], 'unknown')

    def test_other_incidents_or_attribution_cannot_establish_automation_or_remedy(self):
        sources = shared.strict_json(ROOT / packet.PACKET / 'sources.json')
        for axis, ref in [('automation', 'II-DOJ-2024'),
                          ('automation', 'II-CSIS-2018'),
                          ('protective_result', 'II-ISD-2025')]:
            case = shared.strict_json(ROOT / packet.CASE)
            case['observations'][axis].update(status='source_reported', source_refs=[ref])
            with self.subTest(axis=axis, ref=ref), self.assertRaisesRegex(shared.ContinuityError, 'Background'):
                packet.validate_case(case, sources)

    def test_synthetic_context_cannot_be_promoted_to_public_evidence(self):
        case = shared.strict_json(ROOT / packet.CASE)
        sources = shared.strict_json(ROOT / packet.PACKET / 'sources.json')
        sources['sources'].append({'id': 'SYNTHETIC-CONTEXT', 'kind': 'context',
            'scopes': [case['case_id']], 'supports': ['messages']})
        case['observations']['messages']['source_refs'] = ['SYNTHETIC-CONTEXT']
        with self.assertRaisesRegex(shared.ContinuityError, 'difference between'):
            packet.validate_case(case, sources)

    def test_supplement_preserves_dispatch_limits_and_existing_trees(self):
        ext = shared.strict_json(ROOT / packet.TREE)
        base = garden.load_config(ROOT)
        extended = garden_tree.load(ROOT, ext)
        self.assertEqual(set(extended['trees']) - set(base['trees']), {'INFORMATION-INTEGRITY'})
        del extended['trees']['INFORMATION-INTEGRITY']
        self.assertEqual(base, extended)
        for change in ({'tree_id': 'LANGUAGE'}, {'rules': []}, {'base_sha256': '0' * 64}):
            bad = copy.deepcopy(ext)
            bad.update(change)
            with self.subTest(change=change), self.assertRaises(shared.ContinuityError):
                garden_tree.load(ROOT, bad)
