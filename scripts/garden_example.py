#!/usr/bin/env python3
"""Replay a supplied Garden scenario into an inspectable example directory."""
import argparse
from pathlib import Path

import cycle
import garden_runtime as garden

ROOT = Path(__file__).resolve().parents[1]


def build(root, scenario, output):
    document = garden.new_document(garden.load_config(root), scenario['start'],
                                  scenario['question_snapshot'])
    for command in scenario['commands']:
        document = garden.apply_event(document, command, scenario['recorded_at'])
    garden.replay(document)
    cycle.write_json(garden.path_for(output, document['state']['run_id']), document, replace=True)
    garden.project(output, record_base_url=scenario['record_base_url'])
    return document


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', type=Path, default=ROOT / 'examples/garden-traversal/q18-scenario.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    document = build(ROOT, cycle.read_json(args.scenario), args.output)
    print(f"Example only: {len(document['state']['branches'])} branches, "
          f"{document['state']['used']['steps']} supplied steps, zero API calls")
