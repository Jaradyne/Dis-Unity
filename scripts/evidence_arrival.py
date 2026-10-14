#!/usr/bin/env python3
"""One explicit public receipt, deterministic intake, and separate supplied review.

Replay never fetches. Capture is one-shot, recorded before parsing, and cannot retry.
"""
from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.request

import api_records
import continuity as shared
import cycle
import garden_runtime as garden
import safeguards
import scout

ROOT = Path(__file__).resolve().parents[1]
CASE = Path('examples/evidence-arrival/camp-east-montana')
SOURCE = CASE / 'source.json'
LIVE_RECEIPT = CASE / 'live/operations/week-one/runs/CEM-FIRST-ARRIVAL/api/0001.json'
MAX_BYTES = 2_000_000
require = shared.require


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def stamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(parsed.tzinfo is not None, 'Timestamp requires timezone')
    return parsed


def source_record(root):
    source = shared.strict_json(root / SOURCE)
    require(source['version'] == 'evidence-source-1', 'Unsupported source registry')
    scout.checked_url(source['url'], source['allowed_hosts'])
    require(source['url'] == 'https://www.gao.gov/products/gao-26-108886'
            and source['source_id'] == 'GAO-CEM-STATUS'
            and source['item_id'] == source['lineage_id'] == 'GAO-26-108886', 'This proof permits one known product only')
    require(source['access']['max_live_requests'] == 1
            and source['access']['mode'] == 'one_shot_public_read', 'No monitoring authorization')
    stamp(source['access']['recorded_at'])
    parent = safeguards.resolve(root, shared.strict_json(root / safeguards.REFERENCES))[source['parent_source_ref']]['record']
    require(source['url'] == parent['url'] and source['parent_source_id'] == parent['source_id']
            and source['source_family'] == parent['source_family'], 'Source lineage mismatch')
    return source


def capture(root=ROOT, opener=None):
    """Consume the one request allowance even if interrupted/error/redirected."""
    root = Path(root)
    source = source_record(root)
    folder = root / CASE / 'live'
    folder.mkdir(parents=True, exist_ok=True)
    # Exclusive creation is the durable authorization/budget boundary, not a lock
    # removed after execution. An interrupted attempt needs review, never retry.
    with (folder / 'attempt.json').open('x', encoding='utf-8') as handle:
        json.dump({'source_sha256':cycle.digest(source), 'started_at':cycle.now(),
                   'limit':1, 'authorization':source['access']['authorization'],
                   'meaning':'One attempt consumed; interruption does not permit retry.'}, handle, indent=2)
        handle.write('\n')
    request = urllib.request.Request(source['url'], headers={
        'User-Agent':'Dis-Unity-Bounded-Public-Read/1.0', 'Accept':'text/html'})
    # Use the existing recorder in an isolated root; its Week One publisher must
    # not mutate live operational state or produce misleading branch links here.
    journal = api_records.Journal(folder, 'CEM-FIRST-ARRIVAL')
    token = api_records.ACTIVE.set(journal)
    try:
        try:
            api_records.http(request, opener=opener or urllib.request.build_opener(scout.NoRedirect()),
                             timeout=30, max_bytes=MAX_BYTES)
        except Exception:
            # The existing recorder has retained the exact error/partial body.
            pass
    finally:
        api_records.ACTIVE.reset(token)
    stage(root)
    return root / LIVE_RECEIPT


class ProductText(HTMLParser):
    """Visible main text only. No execution, summaries, statuses or findings."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.main = 0
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'main':
            self.main += 1
        if tag in {'script', 'style', 'noscript'}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag == 'main':
            self.main -= 1
        if tag in {'script', 'style', 'noscript'}:
            self.skip -= 1

    def handle_data(self, text):
        if self.main > 0 and self.skip == 0:
            self.parts.append(text)


def body_bytes(body):
    require(isinstance(body, dict) and body['encoding'] in {'utf-8', 'base64'}, 'Unsupported body encoding')
    raw = body['content'].encode('utf-8') if body['encoding'] == 'utf-8' else base64.b64decode(body['content'], validate=True)
    require(sha(raw) == body['saved_sha256'], 'Raw body hash mismatch')
    return raw


def normalize(receipt, source):
    """Return a text version or an explicit unobservable result; never infer harm."""
    require(receipt['schema_version'] == 'api-exchange-1', 'Not a recorded HTTP receipt')
    require(receipt['request']['url'] == source['url'] and receipt['request']['method'] == 'GET', 'Wrong endpoint/method')
    start, end = stamp(receipt['started_at']), stamp(receipt.get('finished_at', receipt['started_at']))
    require(end >= start, 'Receipt time reversal')
    response = receipt.get('response')
    raw = body_bytes(response['body']) if response and response.get('body') else b''
    status = response['http_status'] if response else None
    base = {'observed_at':receipt.get('finished_at', receipt['started_at']), 'http_status':status,
            'raw_body_sha256':sha(raw) if response and response.get('body') else None,
            'last_modified':next((v for k,v in (response or {}).get('headers', []) if k.lower() == 'last-modified'), None),
            'etag':next((v for k,v in (response or {}).get('headers', []) if k.lower() == 'etag'), None)}
    if status == 304:
        require(response['body']['complete'] and not raw, 'Incomplete/nonempty 304')
        return {**base, 'outcome':'not_modified', 'text':None, 'content_sha256':None}
    if (status != 200 or receipt['state'] != 'response_received' or not response['body']['complete']
            or len(raw) > MAX_BYTES):
        return {**base, 'outcome':'unobservable', 'text':None, 'content_sha256':None}
    try:
        parser = ProductText()
        parser.feed(raw.decode('utf-8-sig'))
        text = ' '.join(' '.join(parser.parts).split())
    except (UnicodeError, ValueError):
        text = ''
    if not all(marker in text for marker in source['required_text']):
        return {**base, 'outcome':'unobservable', 'text':None, 'content_sha256':None}
    return {**base, 'outcome':'observed', 'text':text, 'content_sha256':sha(text.encode('utf-8'))}


def pinned(root, binding):
    require(set(binding) == {'path', 'sha256'}, 'Invalid file binding')
    path = shared.local_path(root, binding['path'])
    require(sha(path.read_bytes()) == binding['sha256'], 'Pinned file changed: '+binding['path'])
    return shared.strict_json(path)


def receipt_record(root, binding, lane):
    record = pinned(root, binding)
    if record['schema_version'] == 'arrival-fixture-receipt-1':
        require(lane == 'simulation', 'Synthetic receipt cannot enter live evidence')
        require(set(record) == {'schema_version', 'label', 'exchange', 'body_from'}, 'Invalid fixture envelope')
        value = copy.deepcopy(record['exchange'])
        if record['body_from'] is not None:
            # A repeated synthetic 200 uses the already retained body, not a copy.
            prior = pinned(root, record['body_from'])
            require(prior['schema_version'] == 'api-exchange-1', 'Body reference must name a raw receipt')
            require(value['response']['body'] is None, 'Fixture cannot override a referenced body')
            value['response']['body'] = prior['response']['body']
        return value
    require(record['schema_version'] == 'api-exchange-1', 'Unsupported receipt')
    return record


def replay(root=ROOT, ledger=None):
    root = Path(root)
    source = source_record(root)
    ledger = shared.strict_json(root / CASE / 'observations.json') if ledger is None else ledger
    require(set(ledger) == {'version', 'source_sha256', 'lane', 'observations'}
            and ledger['version'] == 'evidence-arrival-ledger-1', 'Invalid intake ledger')
    require(ledger['source_sha256'] == cycle.digest(source), 'Source registry changed')
    lane = ledger['lane']
    require(lane in {'live', 'simulation'}, 'Unknown evidence lane')
    require(isinstance(ledger['observations'], list) and ledger['observations'], 'No observations')
    if lane == 'live':
        require(len(ledger['observations']) == 1, 'One live retrieval limit')
        attempt = shared.strict_json(root / CASE / 'live/attempt.json')
        require(attempt['limit'] == 1 and attempt['source_sha256'] == cycle.digest(source), 'Live attempt binding changed')
        require(attempt['authorization'] == source['access']['authorization']
                and stamp(attempt['started_at']) >= stamp(source['access']['recorded_at']), 'Invalid attempt authorization/date')
        require(ledger['observations'][0]['receipt']['path'] == str(LIVE_RECEIPT), 'Live receipt must be the fixed captured exchange')
    previous, previous_time, ids, last, observations, queue = shared.ZERO, None, set(), None, [], []
    for index, entry in enumerate(ledger['observations'], 1):
        require(set(entry) == {'sequence', 'observation_id', 'receipt', 'previous_sha256', 'entry_sha256'}, 'Invalid observation')
        require(type(entry['sequence']) is int and entry['sequence'] == index, 'Intake sequence mismatch')
        require(entry['previous_sha256'] == previous, 'Broken intake chain')
        require(entry['entry_sha256'] == cycle.digest({k:v for k,v in entry.items() if k != 'entry_sha256'}), 'Observation altered')
        oid = entry['observation_id']
        require(isinstance(oid, str) and re.fullmatch(r'[A-Z][A-Z0-9-]+', oid) and oid not in ids, 'Duplicate/invalid observation ID')
        ids.add(oid)
        receipt = receipt_record(root, entry['receipt'], lane)
        if lane == 'live':
            require(receipt['run_id'] == 'CEM-FIRST-ARRIVAL' and receipt['record_id'] == 'API-CEM-FIRST-ARRIVAL-0001'
                    and stamp(receipt['started_at']) >= stamp(attempt['started_at']), 'Receipt does not belong to the authorized attempt')
        normalized = normalize(receipt, source)
        when = stamp(normalized['observed_at'])
        require(previous_time is None or when >= previous_time, 'Observation time reversal')
        previous_time = when
        old_hash = last['content_sha256'] if last else None
        outcome = normalized['outcome']
        if outcome == 'not_modified':
            headers = {k.lower():v for k,v in receipt['request']['headers']}
            require(last is not None and last['etag'] and headers.get('if-none-match') == last['etag'],
                    '304 requires a matching prior validator')
            classification = 'unchanged'
            normalized['content_sha256'] = old_hash
        elif outcome == 'unobservable':
            classification = 'unobservable'
        else:
            classification = 'new' if last is None else 'unchanged' if old_hash == normalized['content_sha256'] else 'changed'
            last = normalized
        observation = {'observation_id':oid, 'lane':lane, 'classification':classification,
                       'receipt':entry['receipt'], 'prior_content_sha256':old_hash, **normalized}
        observations.append(observation)
        if classification in {'new', 'changed'}:
            queue.append({'handoff_id':'ARR-'+cycle.digest([source['source_id'], lane, entry['entry_sha256']])[:24],
                          'status':'awaiting_review', 'observation_id':oid, 'lane':lane,
                          'question_id':'Q-CEM-TB-CORRECTION', 'source_id':source['source_id'],
                          'item_id':source['item_id'], 'url':source['url'],
                          'source_family':source['source_family'], 'lineage_id':source['lineage_id'],
                          'reason':classification+' visible product-text version; meaning not assessed',
                          'content_sha256':normalized['content_sha256'], 'receipt':entry['receipt'],
                          'temporal_validity':{**source['temporal_validity'], 'retrieved_at':normalized['observed_at'],
                                               'http_last_modified':normalized['last_modified'],
                                               'last_observed_version_at':normalized['observed_at']},
                          'authority':'Queue only; no model, Governor, canonical admission or assessment change.'})
        previous = entry['entry_sha256']
    return {'version':'evidence-arrival-state-1', 'lane':lane, 'source_sha256':cycle.digest(source),
            'ledger_sha256':cycle.digest(ledger), 'observations':observations, 'handoffs':queue,
            'model_calls':0, 'dispatches':0, 'last_observed_content_sha256':last['content_sha256'] if last else None}


def stage(root=ROOT):
    """Turn the one saved capture into a pending queue; repeat staging is a no-op."""
    root = Path(root)
    binding = {'path':str(LIVE_RECEIPT), 'sha256':sha((root/LIVE_RECEIPT).read_bytes())}
    path = root / CASE / 'observations.json'
    if path.exists():
        ledger = shared.strict_json(path)
        require(len(ledger['observations']) == 1 and ledger['observations'][0]['receipt'] == binding,
                'A different capture is already staged; review required')
    else:
        entry = {'sequence':1, 'observation_id':'CEM-LIVE-001', 'receipt':binding, 'previous_sha256':shared.ZERO}
        entry['entry_sha256'] = cycle.digest(entry)
        ledger = {'version':'evidence-arrival-ledger-1','source_sha256':cycle.digest(source_record(root)),
                  'lane':'live','observations':[entry]}
    state = replay(root, ledger)
    if not path.exists():
        cycle.write_json(path,ledger)
    output = root / 'reports/evidence-arrival/generated/intake.json'
    cycle.write_json(output,state,replace=True)
    return state


def reviewed(root, intake, review=None):
    """Check a separately authored review and linked append; never manufacture one."""
    review = shared.strict_json(root / CASE / 'reviewed-revision.json') if review is None else review
    shared.shape(review, shared.strict_json(root / 'schemas/evidence-arrival-review.schema.json'))
    require(intake['lane'] == 'live', 'Simulation cannot revise empirical assessments')
    require(review['intake_sha256'] == cycle.digest(intake), 'Review is for a different intake')
    handoffs = {x['handoff_id']:x for x in intake['handoffs']}
    require(review['handoff_id'] in handoffs, 'Review must name a queued handoff')
    handoff = handoffs[review['handoff_id']]
    require(stamp(review['reviewed_at']) >= stamp(handoff['temporal_validity']['retrieved_at']), 'Review predates arrival')
    evidence_review = pinned(root, review['evidence_review'])
    require(evidence_review['disposition'].startswith('accepted_as_bounded_recommendation_status_arrival'),
            'Independent review has not accepted this material')
    require(evidence_review['reviewer'] != review['reviewer'], 'Independent and integrating reviewers must be distinct')
    require(evidence_review['receipt'] ['path'] == handoff['receipt']['path']
            and evidence_review['receipt']['sha256'] == handoff['receipt']['sha256'], 'Independent review receipt mismatch')
    require(evidence_review['classification'] == review['classification'], 'Reviewed evidence class mismatch')
    require(stamp(evidence_review['reviewed_at']) <= stamp(review['reviewed_at']), 'Integration predates evidence review')
    require(stamp(evidence_review['reviewed_at']) >= stamp(handoff['temporal_validity']['retrieved_at']), 'Evidence review predates arrival')
    journal = shared.strict_json(root / safeguards.JOURNAL)
    base_count = int(review['base_entry_count'])
    require(base_count > 0 and base_count < len(journal['entries']), 'Missing reviewed append')
    require(cycle.digest(journal['entries'][:base_count]) == review['base_entries_sha256'], 'Original assessment history changed')
    state, resolved = safeguards.replay(root)
    entry = journal['entries'][base_count]
    require(entry['entry_sha256'] == review['revision_entry_sha256']
            and entry['safeguard']['safeguard_id'] == review['safeguard_id']
            and entry['actor'] == review['reviewer'] and entry['recorded_at'] == review['reviewed_at'], 'Revision is not the reviewed append')
    source = resolved[review['source_ref']]['record']
    require(source['receipt'] == handoff['receipt'] and source['intake_sha256'] == cycle.digest(intake)
            and source['content_sha256'] == handoff['content_sha256'], 'Assessment source is not the queued material')
    require(source['retrieved_at'] == handoff['temporal_validity']['retrieved_at']
            and source['observed_date'] == source['retrieved_at'][:10]
            and source['recommendations'] == evidence_review['recommendations'], 'Snapshot differs from reviewed observation')
    evidence = next((x for x in entry['safeguard']['evidence'] if x['evidence_id'] == review['evidence_id']), None)
    require(evidence and evidence['kind'] == review['classification']
            and any(x['source_ref'] == review['source_ref'] for x in evidence['citations']), 'Missing reviewed evidence citation')
    require(evidence['period']['start'] == handoff['temporal_validity']['retrieved_at'][:10], 'Arrival observation date mismatch')
    require(review['classification'] == 'recommendation_status', 'This bounded review does not establish empirical correction')
    old = next(x['safeguard'] for x in reversed(journal['entries'][:base_count]) if x['safeguard']['safeguard_id'] == review['safeguard_id'])
    require(safeguards.dimensions(old) == safeguards.dimensions(entry['safeguard'])
            and entry['safeguard']['effectiveness']['status'] == 'unknown', 'Status arrival must not promote effectiveness or erase failure')
    continuity, _ = shared.replay(root)
    relationship = continuity['relationships'][review['continuity']['relationship_id']]
    require(cycle.digest(relationship) == review['continuity']['assessment_sha256'], 'Continuity assessment changed')
    return {'version':'reviewed-evidence-arrival-1', 'review':review,
            'queue_disposition':'reviewed_with_limits; no further dispatch',
            'safeguard_dimensions':safeguards.dimensions(entry['safeguard']),
            'question_result':'UNKNOWN: no qualifying TB verification in the one received product page.',
            'not_established':'Absence of correction or absence of records elsewhere.'}, state, resolved


def garden_pass(root, intake, decision):
    handoff = intake['handoffs'][0]
    review = decision['review']
    actor = {'name':'Work Aiden', 'runtime':'supplied evidence arrival review', 'model':'none invoked'}
    source = {'ref':review['source_ref'], 'lineage_id':source_record(root)['source_family'],
              'kind':'public_source', 'receipt':handoff['receipt']}
    qid, sid = handoff['question_id'], 'CEM-FIRST-ARRIVAL'
    arrival = {'id':handoff['handoff_id'], 'from':str(CASE/'observations.json'),
               'to':'INIT:ROOT-0001', 'payload':handoff}
    start = {'run_id':sid, 'question_id':qid, 'epoch':1, 'actor':actor, 'tree':'INIT',
             'focus':'One post-transition TB correction test', 'arrival':arrival, 'sources':[source],
             'budget':{'max_steps':10,'max_branches':1,'max_events':10,'max_fanout':0,'model_calls':0},
             'status':'case-local reviewed observation; shared Question and old Camp pass unchanged'}
    outputs = [
        ('ROOT', {'name':'First Camp TB evidence arrival'}),
        ('ARRIVAL', {'arrival':arrival,'language_glance':{'languages':['en'],'basis':'participant_supplied','issuing_office':'GAO',
            'surface_kind':'summary','source_refs':[source['ref']],'note':'Full received public HTML; one GAO family.'}}),
        ('EPIST', {'prompt':'Does this page verify TB correction?', 'starting_state':'Awaiting separate review; content change is not a finding.'}),
        ('FUNC', {'task':qid,'function':'Review a bounded recommendation-status arrival', 'review':review}),
        ('MIRROR', {'comparisons':[{'explanation':review['contrary_evidence'],'queries':[],'answers':[]}],
                    'information_lineage':{'parent_answer_visible':True,'source_refs':[source['ref']],
                        'parent_output_refs':[handoff['receipt']['path']], 'criteria_refs':[str(CASE/'reviewed-revision.json')],
                        'api_record_refs':[handoff['receipt']['path']], 'test_origin':'inherited'}}),
        ('CROSS', {'inherited':[{'ref':source['ref'],'status':'same GAO lineage'}], 'independent':[], 'bridge':[]}),
        ('RESID', {'summary':decision['question_result'],'predicates':{'consequential':True,'distinct_functions':False,'language_exception':None}}),
        ('MEAN', {'summary':review['reason'], 'dimensions':decision['safeguard_dimensions']}),
        ('EXIT', {'kind':'question','summary':'Jared may review the narrow unsent FOIA draft; no request is sent.'}),
        ('RETURN', {'new_arrival':None,'reason':'One-source budget reached; rest pending a separately approved record.'})]
    document = garden.new_document(garden.load_config(root),start,{'questions':{qid:{'epoch':1}}})
    for index,(node,output) in enumerate(outputs):
        document = garden.apply_event(document,{'event_id':sid+'-'+str(index+1),'expected_revision':index,
            'actor':actor,'branch_id':'B0','kind':'step','node':node,'output':output},review['reviewed_at'])
    return garden.replay(document)


def outputs(root=ROOT):
    root = Path(root)
    live = replay(root)
    fixture = replay(root, shared.strict_json(root / CASE / 'fixtures/observations.json'))
    decision, _, _ = reviewed(root, live)
    lines = ['# First evidence arrival', '',
             'One live source; changes below marked simulation are not empirical observations. '
             'Every handoff starts awaiting review. Replaying never dispatches work.', '',
             '| Lane | Observation | Detected state | Content SHA-256 |', '| --- | --- | --- | --- |']
    for state in (live, fixture):
        for item in state['observations']:
            lines.append('| '+' | '.join([state['lane'],item['observation_id'],item['classification'],item['content_sha256'] or 'unknown'])+' |')
    lines += ['', 'Live result: '+decision['question_result'], '', 'Contrary evidence: '+decision['review']['contrary_evidence'], '',
              'The October 12 paraphrase is not a comparable byte/text baseline. The live receipt is the first version in this sensor, not the first historical knowledge of the source.', '',
              'Full receipts and their timestamps are linked in [intake.json](intake.json). '
              '[Review](reviewed.json) separately binds the queued material to a dated assessment append. '
              'The [Garden pass](garden.json) rests without dispatch.']
    return {'intake.json':cycle.encoded(live), 'simulated.json':cycle.encoded(fixture),
            'reviewed.json':cycle.encoded(decision), 'garden.json':cycle.encoded(garden_pass(root,live,decision)),
            'ARRIVAL.md': ('\n'.join(lines)+'\n').encode()}


def run(command, root=ROOT):
    generated = outputs(root)
    destination = Path(root) / 'reports/evidence-arrival/generated'
    if command == 'check':
        actual = {p.relative_to(destination).as_posix():p.read_bytes() for p in destination.rglob('*') if p.is_file()}
        require(actual == generated, 'Saved evidence-arrival output differs')
    elif command == 'build':
        for name, data in generated.items():
            path = destination/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print('PASS: one live receipt, isolated simulations, reviewed revision and deterministic Garden replay; no dispatch')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['capture', 'stage', 'validate', 'replay', 'build', 'check'])
    args = parser.parse_args()
    if args.command == 'capture':
        print(capture())
    elif args.command == 'stage':
        state = stage()
        print(f"PASS: {len(state['handoffs'])} queued handoff(s); no assessment mutation")
    else:
        run(args.command)


if __name__ == '__main__':
    main()
