"""A pinned supplemental Garden tree without changing dispatch or authority."""
import argparse
from copy import deepcopy
import hashlib
from pathlib import Path
import re

import continuity as shared
import cycle
import garden_runtime as garden


def load(root, extension):
    config = garden.load_config(root)
    ext = extension
    require = shared.require
    require(isinstance(ext, dict) and set(ext) == {
        'version', 'base_sha256', 'tree_id', 'definition', 'context_trees'
    }, 'Invalid tree extension')
    require(ext['version'] == 'garden-tree-extension-1', 'Unknown extension version')
    require(hashlib.sha256((Path(root) / 'config/garden-traversal.json').read_bytes()).hexdigest()
            == ext['base_sha256'], 'Tree base pin changed')
    require(ext['tree_id'] not in config['trees'], 'Tree extension cannot replace a tree')
    require(isinstance(ext['tree_id'], str) and
            re.fullmatch(r'[A-Z][A-Z0-9-]*', ext['tree_id']) is not None, 'Invalid tree ID')
    d = ext['definition']
    require(isinstance(d, dict) and set(d) == {'name', 'node_template', 'status'}
            and d['node_template'] == 'INIT'
            and d['status'] == 'traversable_with_supplied_content'
            and isinstance(d['name'], str) and d['name'].strip(), 'Invalid tree definition')
    require(isinstance(ext['context_trees'], list) and
            all(isinstance(t, str) for t in ext['context_trees']) and
            set(ext['context_trees']) <= set(config['trees']), 'Unknown context tree')
    config['trees'][ext['tree_id']] = deepcopy(d)
    return config


def build(root, scenario, output, *, tree_extension):
    """Use the existing reducer without changing historically pinned entry points."""
    document = garden.new_document(load(root, tree_extension), scenario['start'],
                                   scenario['question_snapshot'])
    for command in scenario['commands']:
        document = garden.apply_event(document, command, scenario['recorded_at'])
    garden.replay(document)
    cycle.write_json(garden.path_for(output, document['state']['run_id']), document, replace=True)
    garden.project(output, record_base_url=scenario['record_base_url'])
    return document


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', type=Path, required=True)
    parser.add_argument('--tree-extension', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = build(root, shared.strict_json(args.scenario), args.output,
                   tree_extension=shared.strict_json(args.tree_extension))
    print(f"Supplied pass: {result['state']['used']['steps']} steps, "
          f"{result['state']['used']['branches']} branches, zero provider calls")
