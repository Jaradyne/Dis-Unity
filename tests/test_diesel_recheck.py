"""Evidence-boundary checks for the retained supervised diesel pass."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'reports/diesel/20261102/verify.py'
SPEC = importlib.util.spec_from_file_location('diesel_recheck', PATH)
case = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(case)


class DieselRecheck(unittest.TestCase):
    def test_exact_receipts_and_actual_event_replay(self):
        self.assertEqual(case.verify()['status'], 'passed')

    def test_gasoline_cannot_substitute_for_diesel(self):
        html = case.receipts()['EIA-DIESEL-PRICES']
        with self.assertRaisesRegex(ValueError, 'diesel table'):
            case.extract(html.replace('U.S. On-Highway Diesel Fuel Prices', 'U.S. Regular Gasoline Prices'))

    def test_shifted_change_column_needs_review(self):
        html = case.receipts()['EIA-DIESEL-PRICES']
        with self.assertRaisesRegex(ValueError, 'columns shifted'):
            case.extract(html.replace('week ago', 'month ago'))

    def test_price_and_change_disagreement_is_rejected(self):
        html = case.receipts()['EIA-DIESEL-PRICES']
        with self.assertRaisesRegex(ValueError, 'Weekly change'):
            case.extract(html.replace('<td>6.352</td>', '<td>9.352</td>'))

    def test_two_eia_surfaces_cannot_be_independent_corroboration(self):
        data = json.loads((PATH.parent / 'garden-events.json').read_text())
        run = case.garden.new_document(case.garden.load_config(ROOT), data['start'], data['question_snapshot'])
        for event in data['events']:
            command = copy.deepcopy(event['command'])
            if command['node'] == 'CROSS':
                command['output']['independent'] = [{'ref': 'EIA-DIESEL-PRICES'}]
                with self.assertRaises(case.cycle.CycleError):
                    case.garden.apply_event(run, command, event['recorded_at'])
                return
            run = case.garden.apply_event(run, command, event['recorded_at'])
        self.fail('No CROSS node was inspected')

    def assert_binding_rejected(self, change, message):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'case'
            shutil.copytree(PATH.parent, folder)
            data = json.loads((folder / 'garden-events.json').read_text())
            change(data)
            (folder / 'garden-events.json').write_text(json.dumps(data))
            with patch.object(case, 'HERE', folder), self.assertRaisesRegex(ValueError, message):
                case.verify()

    def test_arrival_must_bind_actual_price_file(self):
        self.assert_binding_rejected(
            lambda d: d['start']['arrival']['payload'].update(price_file_sha256='0' * 64),
            'arrival price hash')

    def test_arrival_must_bind_actual_receipt_index(self):
        self.assert_binding_rejected(
            lambda d: d['start']['arrival']['payload'].update(receipt_index_sha256='0' * 64),
            'arrival receipt-index hash')

    def test_garden_observations_must_match_extraction(self):
        def change(data):
            event = next(e for e in data['events'] if e['command'].get('node') == 'FUNC')
            event['command']['output']['observations']['rows'][0]['change_from_week'] = '9.999'
        self.assert_binding_rejected(change, 'FUNC observations differ')
