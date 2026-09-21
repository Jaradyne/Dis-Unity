"""Render canonical state into readable Markdown views; preserve JSON as authority."""
import json
import sys
from pathlib import Path
from validate_state import SECTIONS, validate

path = Path(sys.argv[1] if len(sys.argv) > 1 else 'Resilience_Cascade_STATE.json')
state = json.loads(path.read_text())
errors = validate(state)
if errors:
    raise SystemExit('\n'.join(errors))
out = path.parent / 'state'
out.mkdir(exist_ok=True)
sources = {s['id']: s for s in state['SOURCE_LEDGER']}

def render(value, level=2):
    if isinstance(value, dict):
        lines = []
        for key, item in value.items():
            label = key.replace('_', ' ')
            if key == 'source_ids':
                links = [f'[{sid}: {sources[sid]["publisher"]}]({sources[sid]["url"]})' for sid in item]
                lines.append(f'**Sources:** {", ".join(links)}\n')
            elif isinstance(item, (dict, list)):
                lines.extend([f'{"#" * min(level, 6)} {label}\n', render(item, level+1)])
            else:
                lines.append(f'**{label}:** {item if item is not None else "Not established"}\n')
        return '\n'.join(lines)
    if isinstance(value, list):
        if all(not isinstance(x, (dict,list)) for x in value):
            return '\n'.join(f'- {x}' for x in value) + '\n'
        return '\n\n---\n\n'.join(render(x, level) for x in value)
    return str(value)

for section in SECTIONS:
    header = f'# {section}\n\nCycle {state["meta"]["cycle_id"]}; cutoff {state["meta"]["research_cutoff"]}.\n\n'
    (out / f'{section}.md').write_text(header + render(state[section]) + '\n')
print(f'Rendered {len(SECTIONS)} state views.')
