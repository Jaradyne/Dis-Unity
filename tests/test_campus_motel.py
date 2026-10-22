"""Evidence-boundary regressions for the saved Campus public packet."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import campus_motel as campus
import continuity as shared
import relays
import safeguards


class CampusPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state,cls.refs=campus.replay()
        cls.sg=cls.state['safeguards']['safeguards']['SG-CAMPUS-NOTICE']
        cls.case=cls.state['relays']['cases']['CAMPUS-MOTEL-PACKET']
        cls.sg_schema=shared.strict_json(campus.ROOT/safeguards.SCHEMA)
        cls.relay_schema=shared.strict_json(campus.ROOT/relays.SCHEMA)

    def test_saved_replay_is_offline_and_leaves_original_baseline_separate(self):
        with patch('socket.create_connection',side_effect=AssertionError('Network during replay')):
            campus.build(check=True)
        self.assertEqual(self.state['meta']['current_executed_agreement'],'not_verified')
        self.assertEqual(self.refs['S-SC02']['binding']['path'],'reports/shelter-accountability/sources.json')
        self.assertEqual(self.refs['S-CM01']['record']['source_lineage'],self.refs['S-CM03']['record']['source_lineage'])

    def test_authorization_and_operator_identity_cannot_prove_working_procedures(self):
        for part in ('people','procedures','authority'):
            sg=copy.deepcopy(self.sg)
            sg['operational'][part].update(status='observed',evidence_ids=['CM-AUTHORITY','CM-IDENTITY'])
            with self.subTest(part=part),self.assertRaisesRegex(shared.ContinuityError,'observed implementation'):
                safeguards.validate(sg,self.sg_schema,self.refs)

    def test_proposed_removal_text_is_not_a_noncompliance_observation(self):
        sg=copy.deepcopy(self.sg)
        sg['failure'].update(status='documented',evidence_ids=['CM-REMOVAL-TEXT'])
        with self.assertRaisesRegex(shared.ContinuityError,'observed noncompliance'):
            safeguards.validate(sg,self.sg_schema,self.refs)

    def test_proposed_services_do_not_prove_effectiveness(self):
        sg=copy.deepcopy(self.sg)
        sg['effectiveness'].update(status='observed',evidence_ids=['CM-SERVICES'])
        with self.assertRaisesRegex(shared.ContinuityError,'dated harm/action/result'):
            safeguards.validate(sg,self.sg_schema,self.refs)

    def test_notice_requirement_cannot_become_notice_receipt(self):
        case=copy.deepcopy(self.case)
        case['relays'][0]['stages']['arrival'].update(status='received',evidence_ids=['CA-NOTICE'])
        with self.assertRaisesRegex(shared.ContinuityError,'stage-specific evidence'):
            relays.validate(case,self.relay_schema,self.refs)

    def test_budget_index_cannot_become_verified_service_failure(self):
        case=copy.deepcopy(self.case)
        r=case['relays'][0]
        r['stages']['outcome'].update(status='failed',evidence_ids=['CM-CURRENTNESS'])
        r['stages']['verification'].update(status='source_supported',evidence_ids=['CM-CURRENTNESS'],method='Search snippet')
        with self.assertRaisesRegex(shared.ContinuityError,'stage-specific evidence'):
            relays.validate(case,self.relay_schema,self.refs)

    def test_changed_raw_receipt_is_detected_before_interpretation(self):
        pins=self.state['input_pins']
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for path in [*pins['sha256'],str(campus.OPS/'inputs.json')]:
                target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(campus.ROOT/path,target)
            raw=next(p for p in pins['sha256'] if p.endswith('/lease-response.json'))
            with (root/raw).open('ab') as f: f.write(b' ')
            with self.assertRaisesRegex(shared.ContinuityError,'Pinned input changed'):
                campus.replay(root)


if __name__=='__main__':
    unittest.main()
