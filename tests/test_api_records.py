from pathlib import Path
import csv
import io
import json
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import api_records as ar
import cycle
import free_provider as fp
import scout


class Response(io.BytesIO):
    def __init__(self, body, status=200, headers=None):
        super().__init__(body)
        self.status = status
        self.headers = headers or {'Content-Type': 'application/json', 'X-Request-Id': 'request-one'}


class APIRecordsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def records(self, rid='recording'):
        return [cycle.read_json(p) for p in sorted((self.root / ar.RUNS / rid / 'api').glob('*.json'))]

    def rows(self):
        with (self.root / ar.THRESHOLD / 'interactions.csv').open() as file:
            return list(csv.DictReader(file))

    def test_full_body_survives_projection_and_credentials_do_not(self):
        raw = json.dumps({'id': 'gen-visible', 'unknown_future_field': {'value': [1, 2]},
                          'choices': [{'message': {'content': 'visible answer', 'reasoning': 'provider-returned field'}}],
                          'echo': 'fixture-api-credential', 'usage': {'cost': 0, 'prompt_tokens': 2}}).encode()
        request = urllib.request.Request(fp.ENDPOINT, data=b'{ "prompt": "public prompt" }',
                                         headers={'Authorization': 'Bearer fixture-api-credential'})
        with ar.recording(self.root, 'recording'), patch('urllib.request.OpenerDirector.open') as opened:
            opened.return_value = Response(raw, headers={'X-Diagnostic': 'unfiltered detail', 'Set-Cookie': 'session=private'})
            data, status = ar.http(request, opener=urllib.request.build_opener(), timeout=1, max_bytes=10000)
        self.assertEqual(data, raw)  # Recorder never changes the bytes consumed by the adapter.
        record = self.records()[0]
        self.assertEqual(record['request']['body']['content'], '{ "prompt": "public prompt" }')
        stored = json.loads(record['response']['body']['content'])
        self.assertEqual(stored['unknown_future_field'], {'value': [1, 2]})
        self.assertEqual(stored['choices'][0]['message']['reasoning'], 'provider-returned field')
        self.assertIn(['X-Diagnostic', 'unfiltered detail'], record['response']['headers'])
        all_saved = '\n'.join(p.read_text() for p in self.root.rglob('*') if p.is_file())
        self.assertNotIn('fixture-api-credential', all_saved)
        self.assertNotIn('session=private', all_saved)
        self.assertTrue(record['response']['body']['complete'])
        self.assertEqual(self.rows()[0]['cost_usd'], '0')
        self.assertTrue(self.rows()[0]['full_record'].endswith('/api/0001.json'))

    def test_every_provider_preflight_and_failed_post_is_recorded_without_retry(self):
        calls = []
        def opened(request, **kwargs):
            calls.append(request.get_method())
            if request.full_url == fp.CATALOG:
                body = {'data': {'id': fp.MODEL, 'endpoints': [{'model_id': fp.MODEL, 'provider_name': 'Nvidia',
                        'tag': 'nvidia', 'status': 0, 'pricing': {'prompt': '0', 'completion': '0'}}]}}
            elif request.full_url.endswith('/key'):
                body = {'data': {'is_management_key': False, 'limit': .01, 'usage': 0}}
            else:
                body = {'id': 'gen-failed', 'error': {'code': 502, 'message': 'Full original diagnostic',
                        'metadata': {'unrecognized_future_field': ['retain', 'all'], 'error_type': 'provider_unavailable'}}}
            return Response(json.dumps(body).encode())
        with ar.recording(self.root, 'recording'), patch.dict('os.environ', {'OPENROUTER_API_KEY': 'fixture-secret'}), \
                patch('urllib.request.OpenerDirector.open', side_effect=opened):
            with self.assertRaises(fp.ProviderFailure) as error:
                fp.call(fp.payload('public prompt'))
        self.assertEqual(error.exception.category, 'transient_capacity')
        self.assertEqual(calls, ['GET', 'GET', 'POST'])
        records = self.records()
        self.assertEqual(len(records), 3)
        saved = json.loads(records[2]['response']['body']['content'])
        self.assertEqual(saved['error']['message'], 'Full original diagnostic')
        self.assertEqual(saved['error']['metadata']['unrecognized_future_field'], ['retain', 'all'])
        self.assertEqual([r['generation_id'] for r in self.rows()], ['', '', 'gen-failed'])

    def test_http_error_non_json_and_timeout_preserve_available_material(self):
        bodies = [b'<html>Full error body</html>', b'not valid JSON at all']
        with ar.recording(self.root, 'recording'), patch('urllib.request.OpenerDirector.open') as opened:
            opened.side_effect = urllib.error.HTTPError(fp.ENDPOINT, 404, 'Not Found', {'X-Diagnostic': 'no match'}, io.BytesIO(bodies[0]))
            with self.assertRaises(fp.ProviderFailure): fp.request_json(fp.ENDPOINT)
            opened.side_effect = None
            opened.return_value = Response(bodies[1])
            with self.assertRaises(fp.ProviderFailure): fp.request_json(fp.ENDPOINT)
            opened.side_effect = TimeoutError('No response arrived')
            with self.assertRaises(fp.ProviderFailure): fp.request_json(fp.ENDPOINT)
        records = self.records()
        self.assertEqual(records[0]['response']['http_status'], 404)
        self.assertEqual(records[0]['response']['body']['content'], bodies[0].decode())
        self.assertEqual(records[1]['response']['body']['content'], bodies[1].decode())
        self.assertIsNone(records[2]['response'])
        self.assertEqual(records[2]['state'], 'transport_error')
        self.assertTrue(all(r['cost_usd'] == '' for r in self.rows()))

    def test_size_bound_is_explicit_and_post_checkpoint_precedes_network(self):
        order = []
        def checkpoint():
            current = self.records()[-1]
            order.append(current['state'])
        def opened(request, **kwargs):
            order.append('network')
            return Response(b'abcdefghijk')
        with ar.recording(self.root, 'recording', checkpoint), patch('urllib.request.OpenerDirector.open', side_effect=opened):
            ar.http(urllib.request.Request(fp.ENDPOINT, data=b'{}'), opener=urllib.request.build_opener(), timeout=1, max_bytes=4)
        self.assertEqual(order, ['request_recorded', 'network', 'incomplete_response'])
        body = self.records()[0]['response']['body']
        self.assertFalse(body['complete'])
        self.assertEqual(body['content'], 'abcde')
        self.assertEqual(self.rows()[0]['coverage'], 'incomplete_or_no_response')

    def test_legacy_index_preserves_unknown_and_is_repeatable(self):
        folder = self.root / ar.RUNS / 'old-run'
        cycle.write_json(folder / 'request.json', {'provider': 'openrouter', 'model': fp.MODEL, 'settings': {'prompt': 'original'}})
        cycle.write_json(folder / 'provider-response.json', {'id': 'gen-old', 'usage': {}, 'choices': []})
        cycle.write_json(self.root / 'operations/week-one/run-manifest.json', {'runs': {
            'old-run': {'started_at': '2026-09-24T09:00:00Z', 'status': 'audit_pending'}}})
        old = (folder / 'provider-response.json').read_bytes()
        ar.publish(self.root)
        before = (self.root / ar.THRESHOLD / 'interactions.csv').read_bytes()
        ar.publish(self.root)
        self.assertEqual(before, (self.root / ar.THRESHOLD / 'interactions.csv').read_bytes())
        self.assertEqual(old, (folder / 'provider-response.json').read_bytes())
        row = self.rows()[0]
        self.assertEqual(row['coverage'], 'legacy_partial')
        self.assertEqual(row['cost_usd'], '')
        self.assertEqual(row['method'], '')
        packet = cycle.read_json(self.root / ar.THRESHOLD / 'runs/old-run.json')
        self.assertEqual(packet['status'], 'available_for_digestion')
        self.assertEqual(len(packet['materials']), 2)

    def test_recovery_logs_metadata_and_content_gets_without_a_new_post(self):
        urls = []
        def opened(request, **kwargs):
            self.assertEqual(request.get_method(), 'GET')
            urls.append(request.full_url)
            if '/content?' in request.full_url:
                body = {'data': {'output': {'completion': '{"retained":true}'}, 'extra': 'full stored output'}}
            else:
                body = {'data': {'id': 'gen-audit', 'model': fp.MODEL, 'provider_name': 'Nvidia',
                                'is_byok': False, 'total_cost': 0, 'extra': 'full audit detail'}}
            return Response(json.dumps(body).encode())
        with ar.recording(self.root, 'recording'), patch.dict('os.environ', {'OPENROUTER_API_KEY': 'fixture-secret'}), \
                patch('urllib.request.OpenerDirector.open', side_effect=opened):
            result = fp.complete({'id': 'gen-audit', 'choices': []})
        self.assertTrue(result['result']['retained'])
        self.assertEqual(len(urls), 2)
        self.assertEqual(len(self.records()), 2)
        self.assertIn('full audit detail', self.records()[0]['response']['body']['content'])
        self.assertIn('full stored output', self.records()[1]['response']['body']['content'])


if __name__ == '__main__':
    unittest.main()
