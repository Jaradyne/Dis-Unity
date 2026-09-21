"""Validate consequential state integrity; no network calls or AI service required."""
import json
import sys
from datetime import date
from pathlib import Path

SECTIONS = ['SYSTEM_MAP', 'ACTIVE_SIGNALS', 'CASCADE_GRAPH', 'RESERVES_AND_LIFEBOATS',
            'ISLANDS_OF_STABILITY', 'TRANSITION_OPPORTUNITIES', 'COMMUNITY_COMMONS',
            'QUESTIONS_TO_WATCH', 'SOURCE_LEDGER', 'CHANGELOG']
GAUGES = ['LOAD', 'RESERVE', 'RECOVERY', 'DEPENDENCY', 'SUBSTITUTABILITY', 'SHEDDING',
          'GROWTH', 'LIFEBOAT', 'SOCIAL_TEMPERATURE', 'CONFIDENCE']
LABELS = {'FACT', 'PLAUSIBLE MECHANISM', 'EARLY SIGNAL', 'UNKNOWN', 'SPECULATION'}

def validate(state):
    errors = []
    for key in SECTIONS:
        if key not in state:
            errors.append(f'Missing section {key}')
    if errors:
        return errors
    sources = state['SOURCE_LEDGER']
    source_ids = {s['id'] for s in sources}
    if len(source_ids) != len(sources):
        errors.append('Duplicate source IDs')
    cutoff = date.fromisoformat(state['meta']['research_cutoff'])
    for source in sources:
        for key in ['id', 'title', 'publisher', 'url', 'publication_date', 'observation_period',
                    'retrieved_at', 'grade', 'limitations']:
            if key not in source:
                errors.append(f'{source.get("id")}: missing {key}')
        published = source.get('publication_date')
        if published and len(published) == 10 and date.fromisoformat(published) > cutoff:
            errors.append(f'{source["id"]}: future publication not quarantined')
        if source.get('grade') not in ['A', 'B', 'C']:
            errors.append(f'{source["id"]}: unknown grade')
    def walk(value, location='state'):
        if isinstance(value, dict):
            if 'source_ids' in value:
                for sid in value['source_ids']:
                    if sid not in source_ids:
                        errors.append(f'{location}: unresolved source {sid}')
            for key, item in value.items():
                walk(item, f'{location}.{key}')
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f'{location}[{index}]')
    walk(state)
    for name in ['ACTIVE_SIGNALS', 'RESERVES_AND_LIFEBOATS', 'ISLANDS_OF_STABILITY',
                 'TRANSITION_OPPORTUNITIES', 'COMMUNITY_COMMONS', 'QUESTIONS_TO_WATCH']:
        ids = [r['id'] for r in state[name]]
        if len(set(ids)) != len(ids):
            errors.append(f'{name}: duplicate record IDs')
    for signal in state['ACTIVE_SIGNALS']:
        if signal['epistemic_label'] not in LABELS:
            errors.append(f'{signal["id"]}: unknown epistemic label')
        if signal['epistemic_label'] == 'FACT' and not signal['source_ids']:
            errors.append(f'{signal["id"]}: unsourced FACT')
        for key in ['freshness', 'confidence', 'event_id', 'status']:
            if not signal.get(key):
                errors.append(f'{signal["id"]}: missing {key}')
    nodes = {n['id'] for n in state['SYSTEM_MAP']['systems']}
    for node in state['SYSTEM_MAP']['systems']:
        if set(GAUGES) - node['gauges'].keys():
            errors.append(f'{node["id"]}: missing gauges')
    edges = state['CASCADE_GRAPH']['edges']
    if len({e['id'] for e in edges}) != len(edges):
        errors.append('Duplicate edge IDs')
    for edge in edges:
        for key in ['from', 'to', 'initiating_stress', 'dependent_system', 'mechanism',
                    'source_ids', 'buffers', 'thresholds', 'substitutes', 'time_horizon',
                    'uncertainty', 'confirm', 'falsify', 'activation_status']:
            if not edge.get(key):
                errors.append(f'{edge["id"]}: missing {key}')
        for endpoint in ['from', 'to']:
            if edge.get(endpoint) not in nodes:
                errors.append(f'{edge["id"]}: unresolved graph node {edge.get(endpoint)}')
    for reserve in state['RESERVES_AND_LIFEBOATS']:
        for key in ['readiness', 'donor_guardrail', 'limits']:
            if not reserve.get(key):
                errors.append(f'{reserve["id"]}: missing reserve gate {key}')
    for island in state['ISLANDS_OF_STABILITY']:
        for key in ['offers', 'needs_in_return', 'donor_guardrail', 'available_surplus']:
            if not island.get(key):
                errors.append(f'{island["id"]}: missing island gate {key}')
    registries = {
        'signal_ids': {r['id'] for r in state['ACTIVE_SIGNALS']},
        'buffers': {r['id'] for r in state['RESERVES_AND_LIFEBOATS']},
        'transition_ids': {r['id'] for r in state['TRANSITION_OPPORTUNITIES']},
        'commons_ids': {r['id'] for r in state['COMMUNITY_COMMONS']},
        'outside_reserve': {r['id'] for r in state['ISLANDS_OF_STABILITY']},
        'lifeboats': {r['id'] for r in state['RESERVES_AND_LIFEBOATS']},
    }
    for cluster in state['SYSTEM_MAP']['clusters']:
        for key, allowed in registries.items():
            for ref in cluster.get(key, []):
                if ref not in allowed:
                    errors.append(f'{cluster["id"]}: unresolved {key} reference {ref}')
    return errors

if __name__ == '__main__':
    path = Path(sys.argv[1] if len(sys.argv) > 1 else 'Resilience_Cascade_STATE.json')
    state = json.loads(path.read_text())
    errors = validate(state)
    if errors:
        print('\n'.join(errors))
        sys.exit(1)
    print(f'Valid: {len(state["ACTIVE_SIGNALS"])} signals, '
          f'{len(state["CASCADE_GRAPH"]["edges"])} conditional links, '
          f'{len(state["SOURCE_LEDGER"])} sources; all ten state sections present.')
