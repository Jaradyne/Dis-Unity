#!/usr/bin/env python3
"""Replay one retained EIA version comparison; never fetch or admit a finding.

This case-local reader does not expand evidence_arrival's pinned GAO adapter.
XLSX values are read from the publisher's cached XML, without recalculation,
macros, external-link access, or third-party spreadsheet dependencies.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from decimal import Decimal
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[3]
CASE = Path('reports/followups/20261113')
sys.path.insert(0, str(ROOT / 'scripts'))
import continuity as shared
import evidence_arrival as arrival

require = shared.require
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
FORECAST_URL = 'https://www.eia.gov/outlooks/steo/xls/Fig12.xlsx'


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def receipt(root, binding, expected_url):
    value = arrival.pinned(root, binding)
    require(value['schema_version'] == 'api-exchange-1', 'Wrong receipt schema')
    require(value['request']['method'] == 'GET' and value['request']['url'] == expected_url,
            'Source identity mismatch')
    require(arrival.stamp(value['finished_at']) >= arrival.stamp(value['started_at']),
            'Receipt time reversal')
    require(value['state'] == 'response_received' and value['response']['http_status'] == 200,
            'Receipt cannot establish an observable version')
    body = value['response']['body']
    raw = arrival.body_bytes(body)
    require(body['complete'] and body['received_bytes'] == len(raw) and len(raw) <= 2_000_000,
            'Incomplete or oversized body cannot establish a version')
    return value, raw


def workbook_cells(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as book:
        meta = ET.fromstring(book.read('xl/workbook.xml'))
        sheets = meta.findall('m:sheets/m:sheet', NS)
        require(len(sheets) == 1 and sheets[0].get('name') == '12', 'Unexpected workbook sheet')
        date_style = meta.find('m:workbookPr', NS)
        require(date_style is None or date_style.get('date1904', '0') in {'0', 'false'},
                'Unsupported date system')
        rid = sheets[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        rels = ET.fromstring(book.read('xl/_rels/workbook.xml.rels'))
        targets = [rel.get('Target') for rel in rels if rel.get('Id') == rid]
        require(len(targets) == 1 and targets[0] == 'worksheets/sheet1.xml', 'Unexpected sheet target')
        strings = [''.join(item.itertext()) for item in ET.fromstring(book.read('xl/sharedStrings.xml'))]
        cells = {}
        for cell in ET.fromstring(book.read('xl/' + targets[0])).findall('.//m:c', NS):
            value = cell.find('m:v', NS)
            if value is None:
                continue
            cells[cell.get('r')] = strings[int(value.text)] if cell.get('t') == 's' else value.text
        require('Short-Term Energy Outlook' in cells['A2'], 'Missing source title')
        require(cells['D24'] == 'Prices (dollars per gallon)', 'Unexpected units')
        return cells


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, text):
        self.parts.append(text)


def plain(raw):
    parser = Text()
    parser.feed(raw.decode('utf-8'))
    return ' '.join(' '.join(parser.parts).split())


def weekly_values(raw):
    text = plain(raw)
    require('Diesel Fuel Release Date: November 10, 2026' in text, 'Unexpected weekly release')
    start = text.index('U.S. On-Highway Diesel Fuel Prices')
    section = text[start:text.index('*prices include all taxes', start)]
    require('10/26/26 11/02/26 11/09/26' in section, 'Weekly column dates changed')
    values = {}
    for label, key in [('U.S.', 'us'), ('California', 'california')]:
        match = re.search(re.escape(label) + r' ((?:-?\d+\.\d+\s+){5}-?\d+\.\d+)', section)
        require(match is not None, 'Missing weekly row ' + label)
        numbers = [Decimal(item) for item in match.group(1).split()]
        require(numbers[2] - numbers[1] == numbers[5], 'Weekly price/change mismatch')
        values[key] = float(numbers[2])
        values[key + '_week_change'] = float(numbers[5])
    return values


def detect(observations):
    """Version detection only. Reprocessing never manufactures a source visit."""
    previous = None
    queue, results, ids, seen = [], [], set(), set()
    last_real_time = None
    for item in observations:
        require(item['observation_id'] not in ids, 'Duplicate observation ID')
        ids.add(item['observation_id'])
        require(item['source_id'] == 'EIA-STEO-FIG12' and item['source_family'] == 'EIA'
                and item['url'] == FORECAST_URL, 'Source identity mismatch')
        require(item['lane'] in {'recorded_public', 'simulated_unchanged_repeat'}, 'Unknown lane')
        at = arrival.stamp(item['source_observed_at'])
        if item['lane'] == 'recorded_public':
            require(last_real_time is None or at >= last_real_time, 'Real receipt chronology reversed')
            last_real_time = at
        else:
            require(previous == item['body_sha256'], 'An unchanged fixture cannot invent new bytes')
        decision = 'first_observation' if previous is None else (
            'unchanged' if previous == item['body_sha256'] else 'changed_version')
        if decision == 'changed_version' and item['body_sha256'] in seen:
            decision = 'previously_seen_version'
        work_id = None
        if decision in {'first_observation', 'changed_version'}:
            work_id = 'REVIEW-' + item['body_sha256'][:16]
            queue.append({'work_id': work_id, 'status': 'awaiting_review',
                          'source_id': item['source_id'], 'source_family': item['source_family'],
                          'receipt': item['receipt'], 'body_sha256': item['body_sha256'],
                          'reason': decision, 'findings_admitted': 0})
        results.append({**item, 'decision': decision, 'queued_work_id': work_id})
        previous = item['body_sha256']
        seen.add(previous)
    return {'version': 'eia-case-local-arrival-replay-1', 'observations': results,
            'review_queue': queue, 'independent_source_families': ['EIA'],
            'new_network_requests_on_replay': 0, 'automatic_findings': [],
            'limitations': ['Same-URL bytes can change without changing a forecast.',
                            'The unchanged repeat reuses retained bytes; it is not a live second retrieval.',
                            'This case-local queue is not the generic Garden Evidence Arrival adapter.']}


def reconstruct(root=ROOT):
    root = Path(root)
    packet = shared.strict_json(root / CASE / 'packet.json')
    require(packet['version'] == 'eia-bounded-comparison-1', 'Unknown packet')
    for binding in packet['preserved_files']:
        arrival.pinned(root, binding) if binding['path'].endswith('.json') else require(
            arrival.sha(shared.local_path(root, binding['path']).read_bytes()) == binding['sha256'],
            'Historical file changed')
    require(packet['source_id'] == 'EIA-STEO-FIG12' and packet['source_family'] == 'EIA',
            'Source lineage mismatch')
    versions = {}
    for name in ('previous', 'current'):
        r, raw = receipt(root, packet[name]['receipt'], FORECAST_URL)
        cells = workbook_cells(raw)
        require(packet[name]['title'] == cells['A2'], 'Forecast release title mismatch')
        versions[name] = {'receipt': r, 'raw': raw, 'cells': cells}
    require((packet['previous']['release_date'], packet['previous']['model_cutoff'])
            == ('2026-10-06', '2026-10-01'), 'Previous forecast metadata changed')
    require((packet['current']['release_date'], packet['current']['model_cutoff'])
            == ('2026-11-10', '2026-11-05'), 'Current forecast metadata changed')
    overview, overview_raw = receipt(root, packet['overview'], 'https://www.eia.gov/outlooks/steo/')
    weekly, weekly_raw = receipt(root, packet['weekly'], 'https://www.eia.gov/petroleum/gasdiesel/')
    text = plain(overview_raw)
    for expected in ['Release Date: November 10, 2026', 'Forecast Completed: November 5, 2026',
                     'Next Release Date: December 8, 2026',
                     'Retail diesel price (dollars per gallon) $5.25 $5.03 Previous forecast $5.19 $4.49']:
        require(expected in text, 'Overview no longer supports retained metadata: ' + expected)
    rows = []
    for month, row in [('2026-11', 82), ('2026-12', 83), ('2027-01', 84)]:
        amounts = {}
        for name in ('previous', 'current'):
            cells = versions[name]['cells']
            period = datetime(1899, 12, 30) + timedelta(days=int(cells['C' + str(row)]))
            require(period.strftime('%Y-%m') == month, 'Forecast month/cell mismatch')
            amounts[name] = Decimal(cells['E' + str(row)])
        rows.append({'month': month, 'status': 'FORECAST', 'sheet': '12',
                     'period_cell': 'C' + str(row), 'forecast_cell': 'E' + str(row),
                     'previous_usd_per_us_gallon': float(amounts['previous']),
                     'current_usd_per_us_gallon': float(amounts['current']),
                     'revision_usd_per_us_gallon': float(amounts['current'] - amounts['previous'])})
    data = {'version': 'bounded-price-comparison-1', 'compiled_on_local': '2026-11-15',
            'timezone': 'America/Los_Angeles',
            'source_cutoff': '2026-11-13T20:12:42.404932-08:00',
            'weekly_actual': {'observation_date': '2026-11-09', 'release_date': '2026-11-10',
                              'units': 'USD per US gallon, on-highway retail diesel including taxes',
                              'receipt': packet['weekly'], **weekly_values(weekly_raw)},
            'monthly_forecast': {'units': 'USD per US gallon, US retail diesel monthly average',
                                 'previous': packet['previous'], 'current': packet['current'], 'rows': rows},
            'annual_forecast': {'period': 'calendar-year 2027 average', 'status': 'FORECAST',
                                'previous': 4.49, 'current': 5.03, 'published_revision_percent': 12.0,
                                'units': 'USD per US gallon, US retail diesel', 'receipt': packet['overview'],
                                'limit': 'Annual published values are rounded and are not January forecasts.'},
            'lineage': {'source_family': 'EIA', 'independent_source_family_count': 1},
            'limitations': ['This national forecast is neither a California forecast nor a daily price guarantee.',
                            'No completed fuel delivery, generator operation or essential-service outcome is established.',
                            'The November overview revises supply expectations; the retained October global report remains dated.']}
    old, new = versions['previous'], versions['current']
    observations = []
    for obs_id, name, lane in [('EIA-OCT-RECEIPT', 'previous', 'recorded_public'),
                               ('EIA-OCT-UNCHANGED-FIXTURE', 'previous', 'simulated_unchanged_repeat'),
                               ('EIA-NOV-RECEIPT', 'current', 'recorded_public')]:
        v = versions[name]
        observations.append({'observation_id': obs_id, 'source_id': packet['source_id'],
                             'source_family': packet['source_family'], 'url': FORECAST_URL,
                             'lane': lane, 'source_observed_at': v['receipt']['finished_at'],
                             'receipt': packet[name]['receipt'], 'body_sha256': arrival.sha(v['raw'])})
    require(arrival.sha(old['raw']) != arrival.sha(new['raw']), 'Expected retained version difference absent')
    proposal = shared.strict_json(root / CASE / 'assessment-proposal.json')
    require(proposal['status'] == 'ready_for_review' and proposal['canonical_admission'] is False,
            'Authored extraction cannot promote itself into an admitted finding')
    require(proposal['previous_assessment'] == next(b for b in packet['preserved_files']
            if b['path'].endswith('/README.md')), 'Original assessment link changed')
    require(proposal['source_bindings'] == [packet['current']['receipt'], packet['overview'], packet['weekly']],
            'Assessment source lineage changed')
    return {'diesel-data.json': data, 'arrival-output.json': detect(observations)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    results = reconstruct()
    for name, data in results.items():
        path = ROOT / CASE / name
        if args.action == 'build':
            path.write_bytes(encode(data))
        else:
            require(path.read_bytes() == encode(data), 'Saved replay drift: ' + str(path))
    print('PASS: retained receipts, exact forecast cells, historical pins and first/unchanged/changed review queue; no network or automatic findings.')


if __name__ == '__main__':
    main()
