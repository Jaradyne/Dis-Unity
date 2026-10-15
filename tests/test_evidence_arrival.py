import copy
import io
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import continuity as shared
import cycle
import evidence_arrival as a
import garden_runtime as garden
import safeguards

ROOT = Path(__file__).resolve().parents[1]


class EvidenceArrivalTests(unittest.TestCase):
    def setUp(self):
        self.source=a.source_record(ROOT)
        self.live=shared.strict_json(ROOT/a.CASE/'observations.json')
        self.fixtures=shared.strict_json(ROOT/a.CASE/'fixtures/observations.json')
        self.raw=a.pinned(ROOT,self.live['observations'][0]['receipt'])

    def sealed(self, ledger):
        previous=shared.ZERO
        for n,e in enumerate(ledger['observations'],1):
            e.update(sequence=n,previous_sha256=previous)
            e['entry_sha256']=cycle.digest({k:v for k,v in e.items() if k!='entry_sha256'})
            previous=e['entry_sha256']
        return ledger

    def test_live_first_version_preserves_raw_identity_dates_and_pending_review(self):
        state=a.replay(ROOT)
        self.assertEqual(state['observations'][0]['classification'],'new')
        self.assertEqual(len(state['handoffs']),1)
        h=state['handoffs'][0]
        self.assertEqual(h['status'],'awaiting_review')
        self.assertEqual(h['source_family'],self.source['source_family'])
        self.assertEqual(h['lineage_id'],'GAO-26-108886')
        self.assertEqual(h['temporal_validity']['retrieved_at'],self.raw['finished_at'])
        self.assertEqual(h['temporal_validity']['published_at'],'2026-06-09')
        self.assertIsNone(h['temporal_validity']['updated_at'])
        self.assertEqual(state['observations'][0]['raw_body_sha256'],self.raw['response']['body']['saved_sha256'])
        self.assertEqual(state['model_calls'],0)
        self.assertEqual(state['dispatches'],0)

    def test_repeat_conditional_changed_contradictory_and_incomplete_are_separate(self):
        state=a.replay(ROOT,self.fixtures)
        self.assertEqual([o['classification'] for o in state['observations']],
                         ['new','unchanged','unchanged','changed','changed','unobservable'])
        self.assertEqual(len(state['handoffs']),3)
        self.assertTrue(all(h['status']=='awaiting_review' for h in state['handoffs']))
        self.assertTrue(all(h['lane']=='simulation' for h in state['handoffs']))
        self.assertIn('Closed - Implemented',state['observations'][3]['text'])
        self.assertIn('agency disputes',state['observations'][4]['text'])
        self.assertEqual(state['last_observed_content_sha256'],state['observations'][4]['content_sha256'])
        repeat=a.pinned(ROOT,self.fixtures['observations'][1]['receipt'])
        self.assertIsNone(repeat['exchange']['response']['body'])
        self.assertEqual(repeat['body_from'],self.live['observations'][0]['receipt'])

    def test_replay_cannot_fetch_or_mutate_assessment(self):
        paths=[ROOT/safeguards.JOURNAL,ROOT/shared.JOURNAL,ROOT/'operations/questions.json']
        before=[p.read_bytes() for p in paths]
        with patch.object(urllib.request.OpenerDirector,'open',side_effect=AssertionError('No network in replay')):
            self.assertEqual(a.outputs(ROOT),a.outputs(ROOT))
            a.run('check',ROOT)
        self.assertEqual(before,[p.read_bytes() for p in paths])

    def test_corrupt_raw_body_wrong_endpoint_or_method_rejected(self):
        for mutation in ('body','url','method'):
            raw=copy.deepcopy(self.raw)
            if mutation=='body':raw['response']['body']['content']+='tampered'
            elif mutation=='url':raw['request']['url']='https://example.org/'
            else:raw['request']['method']='POST'
            with self.subTest(mutation=mutation),self.assertRaises(shared.ContinuityError):a.normalize(raw,self.source)

    def test_error_redirect_missing_main_and_partial_never_replace_good_version(self):
        for code in (301,403,429,500):
            raw=copy.deepcopy(self.raw);raw['response']['http_status']=code;raw['state']='http_error'
            self.assertEqual(a.normalize(raw,self.source)['outcome'],'unobservable')
        for body in (b'<html>login required</html>',b'<main>Unrelated official page</main>'):
            raw=copy.deepcopy(self.raw);raw['response']['body'].update(content=body.decode(),saved_sha256=a.sha(body))
            self.assertEqual(a.normalize(raw,self.source)['outcome'],'unobservable')
        raw=copy.deepcopy(self.raw);raw['response']['body']['complete']=False
        self.assertEqual(a.normalize(raw,self.source)['outcome'],'unobservable')

    def test_orphan_304_is_not_a_success(self):
        ledger=copy.deepcopy(self.fixtures);ledger['observations']=[ledger['observations'][2]]
        with self.assertRaisesRegex(shared.ContinuityError,'matching prior validator'):
            a.replay(ROOT,self.sealed(ledger))

    def test_chain_pin_duplicate_and_order_drift_rejected(self):
        for mutation in ('chain','file','duplicate','order','registry','escape'):
            ledger=copy.deepcopy(self.fixtures)
            if mutation=='chain':ledger['observations'][1]['previous_sha256']='0'*64
            elif mutation=='file':ledger['observations'][0]['receipt']['sha256']='0'*64;self.sealed(ledger)
            elif mutation=='duplicate':ledger['observations'][1]['observation_id']=ledger['observations'][0]['observation_id'];self.sealed(ledger)
            elif mutation=='order':ledger['observations'][1],ledger['observations'][3]=ledger['observations'][3],ledger['observations'][1];self.sealed(ledger)
            elif mutation=='registry':ledger['source_sha256']='0'*64
            else:ledger['observations'][0]['receipt']['path']='../escape.json';self.sealed(ledger)
            with self.subTest(mutation=mutation),self.assertRaises(shared.ContinuityError):a.replay(ROOT,ledger)

    def test_fixture_cannot_be_relabelled_as_live_or_reviewed_empirically(self):
        ledger=copy.deepcopy(self.fixtures);ledger['lane']='live';ledger['observations']=[ledger['observations'][3]]
        with self.assertRaisesRegex(shared.ContinuityError,'fixed captured exchange'):
            a.replay(ROOT,self.sealed(ledger))
        with self.assertRaisesRegex(shared.ContinuityError,'Simulation cannot revise'):
            a.reviewed(ROOT,a.replay(ROOT,self.fixtures))

    def test_review_binds_receipt_queue_lineage_time_and_immutable_prefix(self):
        live=a.replay(ROOT)
        result,state,resolved=a.reviewed(ROOT,live)
        self.assertEqual(result['safeguard_dimensions']['effectiveness'],'unknown')
        self.assertEqual(result['safeguard_dimensions']['failure'],'documented')
        self.assertEqual(result['review']['continuity']['disposition'],'unchanged')
        self.assertEqual(state['revisions']['SG-CEM-INSPECTIONS'],3)
        self.assertEqual(safeguards.lineage('S-CEM-ARRIVAL-20261014',resolved),safeguards.lineage('S-GAO-CEM',resolved))
        for field,value in [('intake_sha256','0'*64),('handoff_id','MISSING'),('reviewed_at','2026-01-01T00:00:00Z'),
                            ('base_entries_sha256','0'*64),('revision_entry_sha256','0'*64),
                            ('classification','effectiveness_observation'),('reviewer','camp_review')]:
            review=copy.deepcopy(result['review']);review[field]=value
            with self.subTest(field=field),self.assertRaises(shared.ContinuityError):a.reviewed(ROOT,live,review)

    def test_receipt_queue_alone_cannot_supply_a_review(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);shutil.copytree(ROOT/'schemas',root/'schemas')
            with self.assertRaises(FileNotFoundError):a.reviewed(root,a.replay(ROOT))

    def test_staging_is_idempotent_and_does_not_apply_review(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(a,'source_record',return_value=self.source):
            root=Path(temp)
            shutil.copytree(ROOT/a.CASE/'live',root/a.CASE/'live')
            first=a.stage(root)
            saved=(root/a.CASE/'observations.json').read_bytes()
            self.assertEqual(a.stage(root),first)
            self.assertEqual(saved,(root/a.CASE/'observations.json').read_bytes())
            self.assertEqual(first['handoffs'][0]['status'],'awaiting_review')
            self.assertFalse((root/safeguards.JOURNAL).exists())

    def test_raw_form_synthetic_substitute_and_capture_identity_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(a,'source_record',return_value=self.source):
            root=Path(temp)
            shutil.copytree(ROOT/a.CASE,root/a.CASE)
            substitute=a.CASE/'fixtures/raw-substitute.json'
            (root/substitute).write_bytes(cycle.encoded(self.raw))
            ledger=copy.deepcopy(self.live)
            ledger['observations'][0]['receipt']={'path':str(substitute),'sha256':a.sha((root/substitute).read_bytes())}
            with self.assertRaisesRegex(shared.ContinuityError,'fixed captured exchange'):
                a.replay(root,self.sealed(ledger))
            for field,value in [('run_id','SIMULATED'),('record_id','SIMULATED'),('started_at','2026-01-01T00:00:00Z')]:
                raw=copy.deepcopy(self.raw);raw[field]=value
                (root/a.LIVE_RECEIPT).write_bytes(cycle.encoded(raw))
                ledger=copy.deepcopy(self.live);ledger['observations'][0]['receipt']['sha256']=a.sha((root/a.LIVE_RECEIPT).read_bytes())
                with self.subTest(field=field),self.assertRaisesRegex(shared.ContinuityError,'authorized attempt'):
                    a.replay(root,self.sealed(ledger))

    def test_garden_replay_has_ten_nodes_and_rests(self):
        live=a.replay(ROOT);decision,_,_=a.reviewed(ROOT,live)
        doc=a.garden_pass(ROOT,live,decision)
        self.assertEqual(garden.replay(doc),doc)
        self.assertEqual([e['command']['node'] for e in doc['events']],garden.NODES)
        self.assertEqual(doc['state']['branches']['B0']['status'],'resting')
        self.assertEqual(set(doc['state']['branches']),{'B0'})
        self.assertEqual(doc['initial']['packet']['question_id'],'Q-CEM-TB-CORRECTION')
        self.assertEqual(doc['initial']['packet']['budget']['model_calls'],0)

    def test_capture_is_once_only_and_retains_refusal_without_retry(self):
        class Refusing:
            def __init__(self):self.calls=0
            def open(self,request,timeout):
                self.calls+=1
                raise urllib.error.HTTPError(request.full_url,403,'Fixture refusal',{},io.BytesIO(b'No access'))
        with tempfile.TemporaryDirectory() as temp,patch.object(a,'source_record',return_value=self.source):
            opener=Refusing();root=Path(temp)
            path=a.capture(root,opener)
            self.assertEqual(opener.calls,1)
            record=shared.strict_json(path)
            self.assertEqual(record['response']['http_status'],403)
            self.assertEqual(record['response']['body']['content'],'No access')
            with self.assertRaises(FileExistsError):a.capture(root,opener)
            self.assertEqual(opener.calls,1)


if __name__=='__main__':unittest.main()
