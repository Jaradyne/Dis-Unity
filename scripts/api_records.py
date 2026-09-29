#!/usr/bin/env python3
"""Record HTTP exchanges before interpretation; project their materials to digestion."""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import base64
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse

import cycle

RUNS = Path('operations/week-one/runs')
THRESHOLD = Path('digestion/threshold/api')
REMOTE = 'https://github.com/Jaradyne/Dis-Unity/blob/week-one-state/'
ACTIVE = ContextVar('api_recording', default=None)
SENSITIVE = re.compile(r'authorization|cookie|password|secret|(?:api[-_]?key)|token|signature', re.I)
COLUMNS = ['record_id', 'run_id', 'question_id', 'started_at_utc', 'kind', 'service', 'method', 'url', 'http_status',
           'state', 'coverage', 'generation_id', 'model', 'cost_usd', 'prompt_tokens', 'completion_tokens',
           'full_record', 'request_material', 'response_material', 'outcome', 'notes']


class Redactor:
    def __init__(self, headers):
        self.secrets = {v for k, v in os.environ.items() if SENSITIVE.search(k) and len(v) >= 8}
        for name, value in headers:
            if SENSITIVE.search(name):
                self.secrets.add(value)
                if name.lower() == 'authorization' and ' ' in value:
                    self.secrets.add(value.split(' ', 1)[1])
        self.count = 0

    def text(self, value):
        for secret in sorted(self.secrets, key=len, reverse=True):
            if secret:
                value, count = re.subn(re.escape(secret), '[REDACTED]', value)
                self.count += count
        # Also cover credential fields or bearer tokens echoed by an upstream.
        value, count = re.subn(r'(?i)("(?:api[-_]?key|access[-_]?token|refresh[-_]?token|password|secret|authorization)"\s*:\s*)"(?:\\.|[^"\\])*"',
                               r'\1"[REDACTED]"', value)
        self.count += count
        value, count = re.subn(r'(?i)\bBearer\s+[A-Za-z0-9._~+/-]+=*', 'Bearer [REDACTED]', value)
        self.count += count
        value, count = re.subn(r'\bsk-or-v1-[A-Za-z0-9_-]+', '[REDACTED]', value)
        self.count += count
        return value

    def headers(self, headers):
        result = []
        for name, value in headers:
            if SENSITIVE.search(name):
                self.count += 1
                value = '[REDACTED]'
            else:
                value = self.text(str(value))
            result.append([name, value])
        return result

    def url(self, url):
        value = self.text(url)
        return re.sub(r'([?&])([^=&]+)=([^&]*)',
                      lambda m: m[1] + m[2] + '=' + ('[REDACTED]' if SENSITIVE.search(urllib.parse.unquote(m[2])) else m[3]), value)

    def body(self, raw, complete=True):
        if raw is None:
            return None
        original_size = len(raw)
        try:
            saved = self.text(raw.decode('utf-8')).encode('utf-8')
            encoding, content = 'utf-8', saved.decode('utf-8')
        except UnicodeDecodeError:
            saved = raw
            for secret in self.secrets:
                if secret:
                    count = saved.count(secret.encode())
                    self.count += count
                    saved = saved.replace(secret.encode(), b'[REDACTED]')
            encoding, content = 'base64', base64.b64encode(saved).decode('ascii')
        return {'encoding': encoding, 'content': content, 'received_bytes': original_size,
                'complete': complete, 'saved_sha256': hashlib.sha256(saved).hexdigest()}


class Exchange:
    def __init__(self, journal, request):
        self.journal = journal
        folder = journal.root / RUNS / journal.rid / 'api'
        folder.mkdir(parents=True, exist_ok=True)
        sequence = max([int(p.stem) for p in folder.glob('*.json')] or [0]) + 1
        self.path = folder / f'{sequence:04d}.json'
        headers = list(request.header_items())
        self.redactor = Redactor(headers)
        self.value = {'schema_version': 'api-exchange-1', 'record_id': f'API-{journal.rid}-{sequence:04d}',
                      'run_id': journal.rid, 'started_at': cycle.now(), 'state': 'request_recorded',
                      'request': {'method': request.get_method(), 'url': self.redactor.url(request.full_url),
                                  'headers': self.redactor.headers(headers), 'body': self.redactor.body(request.data)},
                      'response': None}
        self.save(checkpoint=request.get_method() == 'POST')

    def save(self, checkpoint=False):
        self.value['redaction'] = {'replacement_count': self.redactor.count,
                                  'policy': 'Credentials and authentication cookies only; no content-field allowlist.'}
        cycle.write_json(self.path, self.value, replace=True)
        if checkpoint and self.journal.checkpoint:
            publish(self.journal.root)
            self.journal.checkpoint()

    def response(self, status, headers, body, complete):
        self.value.update(state='http_error' if status >= 300 else 'response_received', finished_at=cycle.now(),
                          response={'http_status': status, 'headers': self.redactor.headers(headers),
                                    'body': self.redactor.body(body, complete)})
        if not complete:
            self.value['state'] = 'incomplete_response'
        self.save(checkpoint=True)

    def error(self, exc):
        if self.value['response'] is None:
            self.value['state'] = 'transport_error'
        self.value.update(finished_at=cycle.now(), exception={
            'type': type(exc).__name__, 'message': self.redactor.text(str(exc))})
        self.save(checkpoint=True)


class Journal:
    def __init__(self, root, rid, checkpoint=None):
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', rid):
            raise cycle.CycleError('Invalid API journal run ID')
        self.root, self.rid, self.checkpoint = Path(root), rid, checkpoint


@contextmanager
def recording(root, rid, checkpoint=None):
    token = ACTIVE.set(Journal(root, rid, checkpoint))
    try:
        yield
    finally:
        ACTIVE.reset(token)
        publish(Path(root))


def recorded_run(function):
    @wraps(function)
    def wrapped(root, rid, *args, **kwargs):
        with recording(root, rid):
            return function(root, rid, *args, **kwargs)
    return wrapped


def http(request, *, opener, timeout, max_bytes):
    """Return bytes/status without parsing; preserve HTTP errors before re-raising."""
    journal = ACTIVE.get()
    record = Exchange(journal, request) if journal else None
    try:
        try:
            response = opener.open(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            with exc:
                try:
                    body = exc.read(max_bytes + 1)
                except Exception as read_error:
                    if record:
                        record.response(exc.code, list(exc.headers.items()) if exc.headers else [],
                                        getattr(read_error, 'partial', b''), False)
                    raise
            if record:
                record.response(exc.code, list(exc.headers.items()) if exc.headers else [], body, len(body) <= max_bytes)
            raise urllib.error.HTTPError(exc.url, exc.code, exc.reason, exc.headers, io.BytesIO(body)) from None
        with response:
            status = response.status
            headers = list(response.headers.items())
            try:
                body = response.read(max_bytes + 1)
            except Exception as exc:
                if record:
                    record.response(status, headers, getattr(exc, 'partial', b''), False)
                raise
        if record:
            record.response(status, headers, body, len(body) <= max_bytes)
        return body, status
    except Exception as exc:
        if record:
            record.error(exc)
        raise


def read(path, default=None):
    return cycle.read_json(path) if path.exists() else default


def body_json(body):
    try:
        value = json.loads(body['content']) if body and body.get('encoding') == 'utf-8' else {}
        return value if isinstance(value, dict) else {}
    except (ValueError, TypeError):
        return {}


def link(root, path):
    return REMOTE + path.as_posix() if (root / path).exists() else ''


def publish(root):
    """Deterministic CSV and per-run material packets; no model call or implied digestion."""
    root = Path(root)
    manifest = read(root / 'operations/week-one/run-manifest.json', {'runs': {}})
    runs = set(manifest['runs']) | {p.name for p in (root / RUNS).glob('*') if p.is_dir()}
    rows = []
    for rid in sorted(runs):
        folder = RUNS / rid
        rec = manifest['runs'].get(rid, {})
        request_path, response_path = folder / 'request.json', folder / 'provider-response.json'
        outcome_path = folder / 'outcome.json'
        material = []
        for path in sorted((root / folder).glob('*')):
            if path.is_file():
                material.append({'path': str(path.relative_to(root)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                 'url': link(root, path.relative_to(root))})
        exchanges = sorted((root / folder / 'api').glob('*.json'))
        for path in exchanges:
            value = read(path)
            req, resp = value['request'], value.get('response') or {}
            payload, body = body_json(req.get('body')), body_json(resp.get('body'))
            usage = body.get('usage') or body.get('data') or {}
            if not isinstance(usage, dict):
                usage = {}
            coverage = 'full_received' if resp.get('body', {}).get('complete') else 'incomplete_or_no_response'
            generation_id = body.get('id') or usage.get('id')
            if not isinstance(generation_id, str) or not generation_id.startswith('gen-'):
                generation_id = None
            row = {'record_id': value['record_id'], 'run_id': rid, 'question_id': rec.get('question_id'),
                   'started_at_utc': value['started_at'],
                   'kind': 'http_exchange', 'service': urllib.parse.urlsplit(req['url']).hostname,
                   'method': req['method'], 'url': req['url'], 'http_status': resp.get('http_status'),
                   'state': value['state'], 'coverage': coverage, 'generation_id': generation_id,
                   'model': body.get('model') or payload.get('model') or usage.get('model'),
                   'cost_usd': usage.get('cost', usage.get('total_cost')), 'prompt_tokens': usage.get('prompt_tokens', usage.get('tokens_prompt')),
                   'completion_tokens': usage.get('completion_tokens', usage.get('tokens_completion')),
                   'full_record': link(root, path.relative_to(root)), 'request_material': link(root, request_path),
                   'response_material': link(root, response_path), 'outcome': link(root, outcome_path),
                   'notes': 'Credentials redacted; raw body saved before interpretation.'}
            rows.append(row)
            material.append({'path': str(path.relative_to(root)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                             'url': row['full_record']})
        if not exchanges:
            request, response, outcome = read(root / request_path, {}), read(root / response_path, {}), read(root / outcome_path, {})
            receipt = outcome.get('provider_receipt', outcome.get('output', {}).get('receipt', {}))
            rows.append({'record_id': 'LEGACY-' + rid, 'run_id': rid, 'question_id': rec.get('question_id'),
                         'started_at_utc': rec.get('started_at'),
                         'kind': 'legacy_run_materials', 'service': request.get('provider', ''), 'method': '', 'url': '',
                         'http_status': response.get('_transport', {}).get('http_status'),
                         'state': rec.get('result', rec.get('status', 'historical_materials')), 'coverage': 'legacy_partial',
                         'generation_id': response.get('id'), 'model': response.get('model') or request.get('model'),
                         'cost_usd': receipt.get('total_cost'), 'prompt_tokens': receipt.get('tokens_prompt'),
                         'completion_tokens': receipt.get('tokens_completion'), 'full_record': '',
                         'request_material': link(root, request_path), 'response_material': link(root, response_path),
                         'outcome': link(root, outcome_path),
                         'notes': 'Run materials, not an HTTP call count. Raw exchanges were not retained; no missing content reconstructed.'})
        packet = {'schema_version': 'digestion-api-materials-1', 'run_id': rid, 'status': 'available_for_digestion',
                  'question_id': rec.get('question_id'), 'attempt_id': rec.get('attempt_id'),
                  'record_ids': [r['record_id'] for r in rows if r['run_id'] == rid], 'materials': material,
                  'coverage': 'recorded_exchanges' if exchanges else 'legacy_partial',
                  'run_status': rec.get('result', rec.get('status')), 'operator_disposition': rec.get('operator_disposition'),
                  'meaning': 'Capture and delivery only; not a Governor review, digestion result or canonical admission.'}
        cycle.write_json(root / THRESHOLD / 'runs' / (rid + '.json'), packet, replace=True)
    rows.sort(key=lambda r: (r.get('started_at_utc') or '', r['record_id']))
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=COLUMNS, lineterminator='\n')
    writer.writeheader()
    for row in rows:
        # Spreadsheet imports must treat provider-controlled strings as text.
        writer.writerow({k: "'" + v if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@')) else v for k, v in row.items()})
    cycle.write_bytes(root / THRESHOLD / 'interactions.csv', output.getvalue().encode(), replace=True)
    full = sum(r['kind'] == 'http_exchange' for r in rows)
    legacy = len(rows) - full
    text = ('# API materials for digestion\n\n'
            '[Open the CSV ledger](interactions.csv) · [Per-run material packets](runs/)\n\n'
            f'{full} recorded HTTP exchanges; {legacy} historical run summaries with partial coverage. '
            'Historical summaries are not a count of API calls.\n\n'
            'Each new exchange preserves the method, URL, request headers/body, status, response headers/body and transport errors before parsing. '
            'Credentials and authentication cookies are redacted. Bodies exceeding existing transport bounds, interrupted reads and missing responses are explicitly marked incomplete. '
            'Unknown cost stays blank; zero means a reported zero. Full provider-returned fields are retained in the exchange record; the smaller operational response is a separate projection.\n\n'
            'Packets link and hash all saved run materials. Delivery means available for digestion, not already digested. '
            'Governor review remains paused. No extra inference is created by recording or indexing.\n')
    cycle.write_bytes(root / THRESHOLD / 'README.md', text.encode(), replace=True)
    return {'http_exchanges': full, 'legacy_run_summaries': legacy}
