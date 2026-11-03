#!/usr/bin/env python3
"""Offline receipt extraction and replay of the actual supervised diesel pass."""
import argparse
from datetime import datetime
from decimal import Decimal
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import cycle
import garden_runtime as garden


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.table = self.row = self.cell = self.caption = None
        self.text = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'}:
            self.skip += 1
        if tag == 'table':
            require(self.table is None, 'Nested table needs review')
            self.table = {'caption': '', 'rows': []}
        if self.table is not None:
            if tag == 'caption':
                self.caption = []
            elif tag == 'tr':
                self.row = []
            elif tag in {'td', 'th'}:
                self.cell = []

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)
        if self.caption is not None:
            self.caption.append(data)
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in {'script', 'style'}:
            self.skip = max(0, self.skip - 1)
        if self.table is None:
            return
        if tag == 'caption':
            self.table['caption'] = ' '.join(' '.join(self.caption).split())
            self.caption = None
        elif tag in {'td', 'th'} and self.cell is not None:
            self.row.append(' '.join(' '.join(self.cell).split()))
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            self.table['rows'].append(self.row)
            self.row = None
        elif tag == 'table':
            self.tables.append(self.table)
            self.table = None


def extract(html):
    parser = Tables()
    parser.feed(html)
    matches = [t for t in parser.tables if t['caption'].startswith(
        'U.S. On-Highway Diesel Fuel Prices*(dollars per gallon)')]
    require(len(matches) == 1, 'Need exactly one explicitly labelled diesel table')
    rows = matches[0]['rows']
    require(len(rows) >= 3 and len(rows[1]) == 7, 'Unexpected table layout')
    require(rows[1][0] == '' and rows[1][4:] == ['2 year ago', 'year ago', 'week ago'],
            'Change columns shifted or renamed')
    dates = [datetime.strptime(v, '%m/%d/%y').date().isoformat() for v in rows[1][1:4]]
    require(dates == sorted(set(dates)), 'Observation dates must be distinct and ordered')
    values = []
    for row in rows[2:]:
        require(len(row) == 7 and row[0], 'Unexpected diesel row')
        require(all(re.fullmatch(r'-?\d+\.\d{3}', v) for v in row[1:]), 'Unexpected price precision')
        require(all(Decimal(v) >= 0 for v in row[1:4]), 'Negative retail price')
        require(Decimal(row[3]) - Decimal(row[2]) == Decimal(row[6]),
                'Weekly change disagrees with displayed prices')
        values.append({'geography': row[0], 'prices': dict(zip(dates, row[1:4])),
                       'change_from_two_years': row[4], 'change_from_year': row[5],
                       'change_from_week': row[6]})
    require(len({r['geography'] for r in values}) == len(values), 'Duplicate geography')
    require({'U.S.', 'California', 'West Coast (PADD5)'} <= {r['geography'] for r in values},
            'Required geographic observations missing')
    text = ' '.join(' '.join(parser.text).split())
    require('*prices include all taxes' in text, 'Tax scope missing')
    release = re.search(r'Diesel Fuel Release Date:\s*(\w+ \d{1,2}, \d{4})\s*Next Release Date:\s*(\w+ \d{1,2}, \d{4})', text)
    require(release is not None, 'Diesel release dates missing')
    published, next_release = [datetime.strptime(d, '%B %d, %Y').date().isoformat() for d in release.groups()]
    require(dates[-1] <= published < next_release, 'Inconsistent publication dates')
    return {'source_id': 'EIA-DIESEL-PRICES', 'publication_date': published,
            'next_release_date_displayed': next_release, 'observation_dates': dates,
            'units': 'USD per U.S. gallon, retail on-highway diesel, all taxes included',
            'lineage_id': 'EIA-GAS-DIESEL-WEEKLY', 'rows': values,
            'not_measured': ['local usable fuel stocks', 'operator-specific purchase costs',
                             'missed essential deliveries', 'cause of a missed delivery',
                             'verified service protection']}


def receipts():
    index = json.loads((HERE / 'receipt-index.json').read_text())
    result = {}
    for source in index['sources']:
        path = HERE / 'receipts' / source['receipt']
        require(hashlib.sha256(path.read_bytes()).hexdigest() == source['receipt_sha256'],
                'Receipt bytes changed')
        record = json.loads(path.read_text())
        require(record['state'] == 'response_received' and record['response']['http_status'] == 200,
                'Receipt is not a successful response')
        body = record['response']['body']
        require(body['complete'] is True and body['encoding'] == 'utf-8', 'Incomplete or unsupported receipt')
        require(hashlib.sha256(body['content'].encode()).hexdigest() == body['saved_sha256'],
                'Body hash changed')
        result[source['id']] = body['content']
    return result


def verify(operational_root=None):
    bodies = receipts()
    summary = extract(bodies['EIA-DIESEL-PRICES'])
    require(summary == json.loads((HERE / 'prices.json').read_text()), 'Price extraction changed')
    events = json.loads((HERE / 'garden-events.json').read_text())
    arrival = events['start']['arrival']['payload']
    require(arrival['price_file_sha256'] == hashlib.sha256((HERE / 'prices.json').read_bytes()).hexdigest(),
            'Garden arrival price hash differs from retained extraction')
    require(arrival['receipt_index_sha256'] == hashlib.sha256((HERE / 'receipt-index.json').read_bytes()).hexdigest(),
            'Garden arrival receipt-index hash differs from retained sources')
    functions = [e['command']['output'] for e in events['events'] if e['command'].get('node') == 'FUNC']
    require(len(functions) == 1 and functions[0]['observations'] == summary,
            'Garden FUNC observations differ from source extraction')
    for path, expected in events['runtime_sha256'].items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected,
                'Pinned runtime changed: ' + path)
    run = garden.new_document(garden.load_config(ROOT), events['start'], events['question_snapshot'])
    for event in events['events']:
        run = garden.apply_event(run, event['command'], event['recorded_at'])
        require(run['events'][-1] == event, 'Recorded event differs from reconstruction')
    require(cycle.digest(run) == events['run_document_sha256'], 'Run document changed')
    require(run['state_sha256'] == events['final_state_sha256'], 'Final state changed')
    garden.replay(run)
    require(run['state']['used'] == {'steps': 10, 'branches': 1, 'model_calls': 0}, 'Unexpected work count')
    require(run['state']['branches']['B0']['status'] == 'resting', 'Run did not rest')
    if operational_root:
        actual = cycle.read_json(garden.path_for(operational_root, run['state']['run_id']))
        require(actual == run, 'Published operational run differs')
    return {'status': 'passed', 'receipt_count': len(bodies), 'price_rows': len(summary['rows']),
            'run_id': run['state']['run_id'], 'state_sha256': run['state_sha256'],
            'mode': 'Offline replay of saved live receipts and supplied Work-session review; zero network calls'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--operational-root', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.operational_root), indent=2))
