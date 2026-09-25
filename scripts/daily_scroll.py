"""A bounded readable projection of recorded work; no new research or model call."""
from pathlib import Path
import re

import cycle

BASE = Path('operations/week-one')


def snapshot(root, limit=6):
    root = Path(root)
    path = root / BASE / 'run-manifest.json'
    state = cycle.read_json(path) if path.exists() else {'runs': {}}
    count = max(1, min(limit, 12))
    recent = sorted(state.get('runs', {}).items(), key=lambda item: (item[1].get('started_at', ''), item[0]))[-count:]
    rows = []
    for rid, rec in recent:
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', rid):
            continue
        folder = root / BASE / 'runs' / rid
        outcome = cycle.read_json(folder / 'outcome.json') if (folder / 'outcome.json').exists() else {}
        sources = cycle.read_json(folder / 'sources.json') if (folder / 'sources.json').exists() else {}
        rows.append({'run_id': rid, 'started_at': rec.get('started_at'),
                     'status': rec.get('status'), 'result': rec.get('result'),
                     'question_id': rec.get('question_id'),
                     'summary': str(outcome.get('answer_summary') or outcome.get('reason') or 'No synthesis recorded.')[:1600],
                     'retrieved_at': sources.get('retrieved_at'),
                     'changed_source_count': len(sources.get('new_or_changed_ids', [])),
                     'source_ref': str(BASE / 'runs' / rid / 'sources.json'),
                     'note_ref': str(BASE / 'runs' / rid / 'HUMAN_NOTE.md')})
    return {'kind': 'daily_scroll', 'as_of': cycle.now(), 'manifest_hash': cycle.digest(state),
            'scope': f'Current snapshot of up to {count} recent recorded runs; their original dates remain visible.',
            'evidence_status': 'Projection of records, not additional corroboration or admitted research.',
            'closed': state.get('closed', False), 'closure_reason': state.get('closure_reason'),
            'brake': state.get('brake'), 'cooldown_until': state.get('cooldown_until'),
            'recent_runs': rows}


def render(root):
    scroll = snapshot(root)
    cycle.write_json(Path(root) / BASE / 'daily-scroll.json', scroll, replace=True)
    lines = ['# Daily Scroll', '', scroll['scope'], '', f"As of {scroll['as_of']}.", '', scroll['evidence_status']]
    for row in scroll['recent_runs']:
        lines += ['', f"## {row['run_id']}", '',
                  f"{row['started_at']} · {row['status']} / {row['result']}", '', row['summary'], '',
                  f"[Saved note](runs/{row['run_id']}/HUMAN_NOTE.md) · {row['changed_source_count']} changed selected source records."]
    if scroll['closed']:
        lines += ['', 'Week One is closed: ' + str(scroll['closure_reason'] or 'configured end').replace('\n', ' ')]
    cycle.write_bytes(Path(root) / BASE / 'DAILY_SCROLL.md', ('\n'.join(lines) + '\n').encode(), replace=True)
    return scroll
