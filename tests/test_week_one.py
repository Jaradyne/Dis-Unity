from copy import deepcopy
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import cycle
import free_provider as fp
import questions
import reflections
import week_one as w

REPO = Path(__file__).resolve().parents[1]


def source(url, accept):
    if 'weather.gov' in url:
        return b'{"features":[],"updated":"2026-09-24T08:00:00Z"}'
    return b'<rss><channel><item><title>Fuel update</title><link>https://www.eia.gov/x</link><pubDate>2026-09-23</pubDate></item></channel></rss>'


def valid_result(request, sources):
    sid = sources['items'][0]['source_id']
    return {'answer': {'summary': 'Delivery capacity is unknown.', 'evidence_refs': [sid], 'counterevidence': ['A price update does not measure missed deliveries.'], 'limitations': ['No delivery observation']},
            'claims': [{'kind': 'FACT', 'text': 'An update appears in the supplied feed.', 'evidence_refs': [sid]}],
            'conditional_link': {**{k: 'conditional / unknown' for k in ['initiating_stress', 'dependent_system', 'mechanism', 'time_horizon', 'uncertainty', 'confirm', 'falsify']},
                                 **{k: [] for k in ['evidence_refs', 'buffering_mechanisms', 'threshold_conditions', 'substitutes']}},
            'resilience': {k: 'Option to verify' for k in ['reserve', 'release', 'substitution', 'growth', 'conversion', 'lifeboat', 'outside_support', 'commons']},
            'caretaker': {k: 'unknown' for k in ['actor', 'authority', 'trigger', 'cash_available_now', 'service_capacity', 'access', 'response_time', 'dependencies', 'backup', 'proof_status', 'tomorrow_test']},
            'sample': {**{k: 'An illustrative sample' for k in ['title', 'original', 'english_pivot', 'why_curious', 'control']}, 'question_refs': ['Q-TEST']},
            'governor': {'reflection_ids': request['reflection_ids'][:1], 'summary': 'Check actual service before reserve claims.', 'followups': [], 'self_reflection': 'Check the denominator.'},
            'reflection': {'summary': 'Service data is the missing observation.', 'observations': [], 'uncertainties': []}}


class ProviderTests(unittest.TestCase):
    def catalog(self):
        return {'data': {'id': fp.MODEL, 'endpoints': [{'model_id': fp.MODEL, 'provider_name': 'Nvidia', 'tag': 'nvidia', 'status': 0, 'pricing': {'prompt': '0', 'completion': '0', 'discount': 0}}]}}

    def test_price_identity_and_inference_key_preflight(self):
        fp.verify_catalog(self.catalog())
        for field, value in [('model_id', 'unapproved'), ('provider_name', 'Groq'), ('pricing', {'prompt': '0', 'completion': '0.001'})]:
            obj = self.catalog(); obj['data']['endpoints'][0][field] = value
            with self.assertRaises(fp.ProviderFailure): fp.verify_catalog(obj)
        obj = self.catalog(); obj['data']['id'] = 'wrong'
        with self.assertRaises(fp.ProviderFailure): fp.verify_catalog(obj)
        fp.verify_inference_key({'data': {'is_management_key': False}})
        for obj in [{'data': {'is_management_key': True}}, {'data': None}, {}]:
            with self.assertRaises(fp.ProviderFailure): fp.verify_inference_key(obj)

    def test_receipt_binds_generation_and_cost(self):
        response = {'id': 'gen-one'}
        audit = {'data': {'id': 'gen-one', 'model': fp.MODEL, 'provider_name': 'Nvidia', 'total_cost': 0, 'is_byok': False}}
        fp.verify_receipt(response, audit)
        for field, value in [('id', 'gen-other'), ('total_cost', 0.01), ('provider_name', 'Groq'), ('is_byok', True), ('model', 'wrong')]:
            altered = deepcopy(audit); altered['data'][field] = value
            with self.assertRaises(fp.ProviderFailure): fp.verify_receipt(response, altered)

    def test_no_inference_when_key_preflight_fails(self):
        posts = []
        def transport(url, **kwargs):
            if url == fp.CATALOG: return self.catalog()
            if url.endswith('/api/v1/key'):
                raise fp.ProviderFailure('auth_or_configuration_error', 'Forbidden', brake=True)
            posts.append(url); return {}
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-fixture'}):
            with self.assertRaises(fp.ProviderFailure): fp.call(fp.payload('public prompt'), transport)
        self.assertEqual(posts, [])

    def test_response_checkpoint_precedes_audit_failure(self):
        saved = []
        def transport(url, **kwargs):
            if url == fp.CATALOG: return self.catalog()
            if url.endswith('/api/v1/key'): return {'data': {'is_management_key': False}}
            if url == fp.ENDPOINT: return {'id': 'gen-one', 'choices': [{'finish_reason': 'stop', 'message': {'content': '{}', 'reasoning': 'must not retain'}}]}
            self.assertEqual(saved[0]['id'], 'gen-one')
            self.assertNotIn('reasoning', saved[0]['choices'][0]['message'])
            raise fp.ProviderFailure('model_unavailable', 'Audit not ready')
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-fixture'}):
            with self.assertRaises(fp.ProviderFailure) as error: fp.call(fp.payload('public prompt'), transport, saved.append)
        self.assertEqual(error.exception.category, 'audit_pending')


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / cycle.CANONICAL).write_text('{"meta":{}}')
        (self.root / 'CULTURE.md').write_text('Care, evidence and reflection.')
        (self.root / 'config').mkdir()
        shutil.copy2(REPO / 'config/sensors.json', self.root / 'config/sensors.json')
        w.write(self.root, Path('config/week-one.json'), {'enabled': True, 'starts_at': '2026-09-24T00:00:00Z', 'ends_at': '2026-10-01T00:00:00Z', 'max_provider_posts_per_utc_day': 4, 'questions': ['Q-TEST']})
        questions.ask(self.root, 'Are essential deliveries affected?', 'test', qid='Q-TEST')
        reflections.post(self.root, {'actor': 'test', 'level': 'worker', 'summary': 'Check actual service.'})
        self.env = patch.dict(os.environ, {'GITHUB_SHA': 'test-commit', 'WEEK_ONE_PERSIST': '0'}); self.env.start(); self.addCleanup(self.env.stop)

    def prepare(self, rid='test-one', now='2026-09-24T08:05:00Z'):
        return w.prepare(self.root, rid, now=now, fetcher=source)

    def save_result(self, rid='test-one'):
        req = w.read(self.root, w.run_path(rid, 'request.json'))
        value = valid_result(req, w.read(self.root, w.run_path(rid, 'sources.json')))
        rec = w.manifest(self.root)['runs'][rid]
        w.write(self.root, w.run_path(rid, 'outcome.json'), {'category': 'partial_answer', 'finished_at': '2026-09-24T08:10:00Z', 'output': {'result': value, 'receipt': {'fixture': True}}})
        return value, req, rec

    def test_recovery_projects_once_and_slot_deduplicates(self):
        self.assertEqual(self.prepare()['status'], 'prepared')
        value, req, rec = self.save_result()
        self.assertEqual(self.prepare('recovery')['status'], 'slot_already_completed')
        w.finalize(self.root, 'test-one')
        q = questions.question(questions.load(self.root), 'Q-TEST')
        self.assertEqual(len(q['answers']), 1)
        self.assertEqual(q['status'], 'open')
        self.assertEqual(len(reflections.load(self.root)['decisions']), 1)

    def test_interrupt_links_saved_generation_without_new_post(self):
        self.prepare()
        w.write(self.root, w.run_path('test-one', 'provider-response.json'), {'id': 'gen-saved'})
        self.assertEqual(self.prepare('recovery')['status'], 'prepared')
        rec = w.manifest(self.root)['runs']['recovery']
        self.assertEqual(rec['post_reserved'], 0)
        self.assertEqual(rec['recovery_from'], 'test-one')
        req = w.read(self.root, w.run_path('recovery', 'request.json'))
        self.assertIn('recovery_from', req)
        self.assertEqual(w.read(self.root, w.run_path('recovery', 'provider-response.json'))['id'], 'gen-saved')
        self.assertEqual(self.prepare('third')['status'], 'slot_attempt_limit')

    def test_audit_pending_recovers_without_regeneration(self):
        self.prepare()
        w.write(self.root, w.run_path('test-one', 'provider-response.json'), {'id': 'gen-saved'})
        w.write(self.root, w.run_path('test-one', 'outcome.json'), {'category': 'audit_pending', 'finished_at': '2026-09-24T08:10:00Z', 'cooldown_hours': 12})
        w.finalize(self.root, 'test-one')
        self.assertEqual(self.prepare('later', '2026-09-25T08:11:00Z')['status'], 'prepared')
        self.assertEqual(w.manifest(self.root)['runs']['later']['post_reserved'], 0)

    def test_operator_recovery_counts_provider_reservations_not_scout_wakes(self):
        self.assertEqual(self.prepare('first')['status'], 'prepared')
        state = w.manifest(self.root)
        state['runs']['first']['status'] = 'complete'
        state['runs']['first']['result'] = 'auth_or_configuration_error'
        state['runs']['first']['post_reserved'] = 1
        state['runs']['second'] = {
            'run_id': 'second', 'started_at': '2026-09-24T08:06:00+00:00',
            'slot': '20260924-AM', 'status': 'deferred',
            'result': 'operator_review_required', 'post_reserved': 0
        }
        w.write(self.root, w.BASE / 'run-manifest.json', state)
        result = self.prepare('recovery', now='2026-09-24T08:07:00Z')
        self.assertEqual(result['status'], 'prepared')
        self.assertEqual(w.manifest(self.root)['runs']['recovery']['post_reserved'], 1)
        self.assertEqual(self.prepare('fourth', now='2026-09-24T08:08:00Z')['status'], 'slot_attempt_limit')

    def test_thought_partner_mailbox_is_idempotent_and_answer_stays_staged(self):
        packet = {'question_id': 'Q-TEST', 'answer': {'summary': 'An unadmitted thought'},
                  'reflection': {'summary': 'A meaningful shared note', 'source_refs': []}}
        w.write(self.root, Path('handoffs/week_one_governor/2026-09-24.json'), packet)
        first = w.ingest_thought_partners(self.root)
        second = w.ingest_thought_partners(self.root)
        self.assertEqual(first, second)
        self.assertEqual(len(questions.question(questions.load(self.root), 'Q-TEST')['answers']), 0)
        self.assertEqual(len(reflections.load(self.root)['entries']), 2)

    def test_end_date_stops_all_reads_and_writes_digest(self):
        with patch.object(w, 'gather') as gather:
            result = self.prepare(now='2026-10-01T00:00:00Z')
        self.assertEqual(result['status'], 'window_complete'); gather.assert_not_called()
        self.assertTrue((self.root / w.BASE / 'WEEK_ONE_DIGEST.md').exists())
        self.assertEqual(w.gate(w.catalog(self.root), w.manifest(self.root), w.clock('2026-09-25T00:00:00Z')), 'window_complete')

    def test_budget_cooldown_and_source_reference_validation(self):
        cfg = w.catalog(self.root); state = w.manifest(self.root)
        state['cooldown_until'] = '2026-09-25T00:00:00Z'
        self.assertEqual(w.gate(cfg, state, w.clock('2026-09-24T08:00:00Z')), 'cooldown')
        self.prepare(); value, req, rec = self.save_result()
        sources = w.read(self.root, w.run_path('test-one', 'sources.json'))
        ids = {x['source_id'] for x in sources['items']}
        w.validate_answer(value, ids, set(req['reflection_ids']), 'Q-TEST')
        value['claims'][0]['evidence_refs'] = ['invented']
        with self.assertRaises(ValueError): w.validate_answer(value, ids, set(req['reflection_ids']), 'Q-TEST')


if __name__ == '__main__': unittest.main()
