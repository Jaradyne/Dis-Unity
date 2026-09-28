#!/usr/bin/env python3
"""Durable supplied-content Garden traversal. No network, model calls or Governor."""
import argparse
import copy
import csv
import io
import json
from pathlib import Path
import sys

import cycle
import garden

STORE = Path('operations/garden/runs')
THRESHOLD = Path('digestion/threshold/garden')
NODES = [node.split('-')[0] for node in garden.NODES]
VERSION = 'garden-traversal-1'
require = garden.require


def strings(value, label):
    require(isinstance(value, list) and all(isinstance(x, str) and x.strip() for x in value), label + ' must be a list of references')
    return value


def actor(value):
    require(isinstance(value, dict) and all(isinstance(value.get(k), str) and value[k].strip()
            for k in ('name', 'runtime')), 'Name the actual actor and runtime')


def current(branch):
    return branch['visits'][-1]


def node(branch):
    return NODES[len(current(branch)['steps'])] if len(current(branch)['steps']) < len(NODES) else 'RETURN'


def load_config(root):
    config = cycle.read_json(Path(root) / 'config/garden-traversal.json')
    config['grammar'] = garden.load_config(root)
    require(config['model_execution'] is False and config['limits']['model_calls'] == 0, 'This runtime does not dispatch models')
    require(set(config['limits']) == {'max_steps','max_branches','max_events','max_fanout','model_calls'}
            and all(type(v) is int and v >= 0 for v in config['limits'].values()), 'Invalid traversal limits')
    require(set(config['node_contracts']) == set(NODES), 'Contracts must cover all ten nodes')
    for tree, definition in config['trees'].items():
        garden.identifier(tree)
        require(definition['node_template'] == 'INIT', 'Unsupported node template')
    rule_ids = [r['id'] for r in config['rules']]
    require(len(rule_ids) == len(set(rule_ids)), 'Duplicate route rule')
    for rule in config['rules']:
        require(set(rule['from'] + rule['to']) <= set(config['trees']), 'Route tree is not registered')
        require(set(rule['actions']) <= {'MOVE','CLONE','FANOUT'} and set(rule['at']) <= set(NODES), 'Unknown route operation or boundary')
        require(type(rule['review_required']) is bool, 'Route review requirement must be explicit')
        garden.evaluate_group(rule['condition'], {})
    return config


def sources(value):
    require(isinstance(value, list), 'Source catalog must be a list')
    result = {}
    for item in value:
        require(isinstance(item, dict) and all(isinstance(item.get(k), str) and item[k].strip()
                for k in ('ref', 'lineage_id')), 'Source needs ref and underlying lineage_id')
        require(item.get('kind') in {'public_source','model_output','context','design_input'}, 'Source needs an explicit kind')
        require(item['ref'] not in result, 'Duplicate source reference')
        result[item['ref']] = copy.deepcopy(item)
    return result


def visit(tree, arrival):
    return {'tree': tree, 'arrival': copy.deepcopy(arrival), 'steps': [], 'status': 'ready'}


def initial_state(config, packet, registry):
    require(isinstance(packet, dict) and len(cycle.encoded(packet)) <= 65536, 'Keep a start packet at or below 64 KiB')
    garden.identifier(packet.get('run_id'))
    actor(packet.get('actor'))
    qid, epoch = packet.get('question_id'), packet.get('epoch')
    require(qid in registry.get('questions', {}) and type(epoch) is int and registry['questions'][qid]['epoch'] == epoch,
            'Use an existing Question and its current epoch')
    tree = packet.get('tree', 'INIT')
    require(tree in config['trees'], 'Unknown traversal tree')
    arrival = packet['arrival']
    garden.validate_arrival(arrival)
    require(arrival['to'] == tree + ':ROOT-0001', 'Arrival must name this tree entry')
    catalog = sources(packet.get('sources', []))
    limits = copy.deepcopy(config['limits'])
    requested = packet.get('budget', {})
    require(isinstance(requested, dict) and set(requested) <= set(limits), 'Unknown budget field')
    for key, value in requested.items():
        require(type(value) is int and 0 <= value <= limits[key], 'Budget cannot exceed reviewed limits')
        limits[key] = value
    require(limits['max_branches'] >= 1, 'Budget must include the root branch')
    return {'run_id': packet['run_id'], 'question_id': qid, 'epoch': epoch, 'revision': 0,
            'limits': limits, 'used': {'steps': 0, 'branches': 1, 'model_calls': 0},
            'sources': catalog, 'route_decisions': [], 'route_signatures': [],
            'branches': {'B0': {'id':'B0', 'parent_branch':None, 'root_branch':'B0', 'question_id':qid, 'epoch':epoch,
                 'status':'ready', 'rest':None, 'focus':packet.get('focus', ''),
                 'lineage':{'source_refs':list(catalog), 'independent_evidence':False},
                 'visits':[visit(tree, arrival)], 'seen_arrival_ids':[arrival['id']],
                 'visited':[{'tree':tree,'payload_hash':cycle.digest(arrival['payload'])}]}}}


def new_document(config, packet, registry):
    snapshot = {packet['question_id']: {'epoch': packet['epoch']}}
    state = initial_state(config, packet, registry)
    return {'schema_version':VERSION, 'initial':{'config':copy.deepcopy(config), 'packet':copy.deepcopy(packet),
            'registry':{'questions':snapshot}}, 'config_sha256':cycle.digest(config), 'events':[], 'state':state,
            'state_sha256':cycle.digest(state)}


def refs(items):
    require(isinstance(items, list), 'Attachments must be a list')
    return strings([x.get('ref') if isinstance(x, dict) else x for x in items], 'attachments')


def validate_output(state, branch, stage, output, config):
    require(isinstance(output, dict) and len(cycle.encoded(output)) <= 65536, 'Node output must be an object at or below 64 KiB')
    contract = config['node_contracts'][stage]
    for key in contract.get('strings', []):
        require(isinstance(output.get(key), str) and output[key].strip(), stage + ' needs ' + key)
    for key in contract.get('lists', []):
        require(isinstance(output.get(key), list), stage + ' needs list ' + key)
    for key in contract.get('objects', []):
        require(isinstance(output.get(key), dict), stage + ' needs object ' + key)
    if stage == 'ARRIVAL':
        require(output['arrival'] == current(branch)['arrival'], 'Preserve the actual arrival')
        glance = output['language_glance']
        strings(glance.get('languages'), 'languages')
        require(glance.get('basis') in {'source_metadata','participant_supplied','unknown'}, 'Language glance needs its basis')
        require(glance.get('surface_kind') in {'original','translation','summary','mixed','unknown'}, 'Record surface kind')
        require(glance.get('issuing_office'), 'Record issuing office or unknown')
        require(set(strings(glance.get('source_refs'), 'language sources')) <= set(state['sources']), 'Unknown language source')
        if glance['basis'] == 'unknown':
            require(not glance['languages'], 'Unknown language cannot assert a language')
    if stage == 'MIRROR':
        for item in output['comparisons']:
            require(isinstance(item, dict) and item.get('explanation') and isinstance(item.get('queries'), list)
                    and isinstance(item.get('answers'), list), 'Comparison needs explanation, queries and supplied answers')
        lineage = output['information_lineage']
        require(type(lineage.get('parent_answer_visible')) is bool or lineage.get('parent_answer_visible') == 'unknown', 'Record parent-answer visibility')
        for key in ['source_refs','parent_output_refs','criteria_refs','api_record_refs']:
            strings(lineage.get(key), key)
        require(set(lineage['source_refs']) <= set(state['sources']), 'Unknown MIRROR source')
        require(lineage.get('test_origin') in {'inherited','separately_specified','unknown'}, 'Record test origin')
        branch['lineage']['source_refs'] = list(dict.fromkeys(branch['lineage']['source_refs'] + lineage['source_refs']))
    if stage == 'CROSS':
        additions = sources(output.get('source_additions', []))
        require(not (set(additions) & set(state['sources'])), 'New source references cannot rewrite existing sources')
        available = {**state['sources'], **additions}
        inherited, independent = refs(output['inherited']), refs(output['independent'])
        require(set(inherited + independent) <= set(available), 'CROSS attachment is absent from the source catalog')
        inherited_lineage = {available[r]['lineage_id'] for r in set(inherited + branch['lineage']['source_refs'])}
        independent_lineage = []
        for ref in independent:
            source = available[ref]
            require(source['kind'] == 'public_source' and source.get('independence_basis'), 'Independent attachment needs a public source and stated basis')
            require(source['lineage_id'] not in inherited_lineage, 'Inherited or cloned material is not independent evidence')
            independent_lineage.append(source['lineage_id'])
        require(len(independent_lineage) == len(set(independent_lineage)), 'Repeated underlying source is not multiple independent attachments')
        for bridge in output['bridge']:
            require(isinstance(bridge, dict) and bridge.get('question') and bridge.get('status'), 'Epistemic bridge needs a question and actual test status')
            require(set(strings(bridge.get('source_refs', []), 'bridge sources')) <= set(available), 'Unknown bridge source')
        state['sources'].update(additions)
        known = inherited + independent + list(additions)
        known += [ref for bridge in output['bridge'] for ref in bridge.get('source_refs', [])]
        branch['lineage']['source_refs'] = list(dict.fromkeys(branch['lineage']['source_refs'] + known))
    if stage == 'RESID':
        require(all(type(v) is bool or v is None for v in output['predicates'].values()), 'Route predicates are true, false or unknown')
    if stage == 'MEAN' and output.get('culture_flower') is not None:
        require(output['culture_flower'].get('evidence') is False, 'Culture flowers remain non-evidence')
    if stage == 'EXIT':
        require(output['kind'] in garden.EXIT_KINDS, 'Unknown EXIT kind')


def rest(branch, reason, kind='participant'):
    branch['status'] = 'resting'
    branch['rest'] = {'kind':kind, 'reason':reason}


def step(state, branch, command, config):
    require(branch['status'] == 'ready', 'Resume a resting branch before advancing')
    stage = node(branch)
    require(command.get('node') == stage, 'Output must match the current node')
    output = copy.deepcopy(command['output'])
    if state['used']['steps'] >= state['limits']['max_steps']:
        rest(branch, 'Step budget exhausted', 'budget')
        return {'status':'rest','reason':'step_budget'}
    validate_output(state, branch, stage, output, config)
    current(branch)['steps'].append({'node':stage,'output':output,'actor':copy.deepcopy(command['actor']), 'event_id':command['event_id']})
    state['used']['steps'] += 1
    if stage == 'RETURN':
        current(branch)['status'] = 'completed'
        return return_arrival(state, branch, output.get('new_arrival'), output['reason'])
    return {'status':'advanced','next_node':node(branch)}


def return_arrival(state, branch, new_arrival, reason):
    result = garden.route_return(current(branch)['arrival'], new_arrival, reason, branch['seen_arrival_ids'])
    if result['status'] == 'rest':
        rest(branch, result['reason'], 'return')
        return result
    arrival = result['arrival']
    tree = current(branch)['tree']
    require(arrival['to'] == tree + ':ROOT-0001', 'RETURN re-enters the same tree; use a route to change trees')
    signature = {'tree':tree, 'payload_hash':cycle.digest(arrival['payload'])}
    if signature in branch['visited']:
        rest(branch, 'Previously inspected payload in this tree', 'loop')
        return {'status':'rest','reason':'previously_seen_payload'}
    if state['used']['steps'] >= state['limits']['max_steps']:
        rest(branch, 'Step budget exhausted', 'budget')
        return {'status':'rest','reason':'step_budget'}
    if current(branch)['status'] == 'ready':
        current(branch)['status'] = 'rested'
    branch['seen_arrival_ids'].append(arrival['id'])
    branch['visited'].append(signature)
    branch['visits'].append(visit(tree, arrival))
    branch.update(status='ready', rest=None)
    return result


def route(state, branch, command, config):
    require(branch['status'] == 'ready', 'Resume a resting branch before routing')
    rule = next((r for r in config['rules'] if r['id'] == command.get('rule_id')), None)
    require(rule is not None, 'Route rule must exist in the reviewed configuration')
    action = command.get('action')
    require(action in rule['actions'] and node(branch) in rule['at'] and current(branch)['tree'] in rule['from'], 'Route is not allowed at this boundary')
    residual = next((s for s in reversed(current(branch)['steps']) if s['node'] == 'RESID'), None)
    require(residual is not None, 'Record a residual before routing')
    targets = command.get('targets')
    require(isinstance(targets, list) and targets and all(isinstance(t, dict) for t in targets), 'Supply bounded route targets')
    require(action == 'FANOUT' or len(targets) == 1, 'MOVE and CLONE need one target')
    require(action != 'FANOUT' or 2 <= len(targets) <= state['limits']['max_fanout'], 'FANOUT exceeds the reviewed bound')
    require(len({t.get('tree') for t in targets}) == len(targets), 'FANOUT needs distinct target trees')
    require(len({t.get('focus') for t in targets}) == len(targets), 'Children need distinct functions')
    for target in targets:
        require(target.get('tree') in rule['to'] and target['tree'] != current(branch)['tree'], 'Unknown or same-tree target')
        require(all(isinstance(target.get(k), str) and target[k].strip() for k in ('focus','reason')), 'Each target needs its function and reason')
    if rule['review_required']:
        review = command.get('review', {})
        actor(review.get('actor'))
        require(review.get('reference') and review.get('decision') == 'approved', 'This route needs attributed reviewed approval')
    decision = {'event_id':command['event_id'], 'branch_id':branch['id'], 'rule_id':rule['id'], 'action':action,
                'from_tree':current(branch)['tree'], 'targets':copy.deepcopy(targets),
                'condition':copy.deepcopy(rule['condition']), 'observations':copy.deepcopy(residual['output']['predicates']),
                'condition_result':garden.evaluate_group(rule['condition'], residual['output']['predicates']),
                'authority':{'kind':'reviewed_configuration','rule_id':rule['id'],'review':copy.deepcopy(command.get('review'))},
                'status':'pending','children':[]}
    state['route_decisions'].append(decision)
    if decision['condition_result'] is not True:
        decision['status'] = 'unknown' if decision['condition_result'] is None else 'condition_false'
        return decision
    payload_hash = cycle.digest(current(branch)['arrival']['payload'])
    signatures = [cycle.digest({'parent':branch['id'], 'visit':len(branch['visits']),
                   'residual':residual['output'], 'target':t['tree']}) for t in targets]
    if any(s in state['route_signatures'] for s in signatures) or any({'tree':t['tree'],'payload_hash':payload_hash} in branch['visited'] for t in targets):
        decision['status'] = 'rest_loop'
        rest(branch, 'This payload or route was already carried here', 'loop')
        return decision
    needed = 0 if action == 'MOVE' else len(targets)
    if state['used']['branches'] + needed > state['limits']['max_branches'] or state['used']['steps'] >= state['limits']['max_steps']:
        decision['status'] = 'rest_budget'
        rest(branch, 'Run step or branch budget exhausted', 'budget')
        return decision
    state['route_signatures'].extend(signatures)
    cross = next((s['output'] for s in reversed(current(branch)['steps']) if s['node']=='CROSS'), {})
    attached = refs(cross.get('inherited', []) + cross.get('independent', []))
    attached += [ref for bridge in cross.get('bridge', []) for ref in bridge.get('source_refs', [])]
    inherited_refs = list(dict.fromkeys(branch['lineage']['source_refs'] + attached))
    lineage = {'parent_branch':branch['id'],'parent_visit':len(branch['visits'])-1,'parent_node':node(branch),
               'parent_output_hash':cycle.digest(current(branch)['steps']), 'source_refs':inherited_refs,
               'originating_residual':copy.deepcopy(residual['output']), 'route_authority':copy.deepcopy(decision['authority']),
               'route_event_id':command['event_id'],
               'independent_evidence':False, 'parent_answer_visibility':'supplied content remains linked; actual visibility recorded at MIRROR'}
    for target in targets:
        target_lineage = {**copy.deepcopy(lineage), 'route_reason':target['reason'], 'route_focus':target['focus']}
        arrival = copy.deepcopy(current(branch)['arrival'])
        arrival.update(id='ARR-' + cycle.digest([command['event_id'], target['tree']])[:24],
                       to=target['tree'] + ':ROOT-0001', from_node=current(branch)['tree'] + ':' + garden.NODES[len(current(branch)['steps'])],
                       parent_arrival_id=current(branch)['arrival']['id'],
                       origin=copy.deepcopy(current(branch)['arrival'].get('origin', current(branch)['arrival'])))
        if action == 'MOVE':
            current(branch)['status'] = 'moved'
            branch['visits'].append({**visit(target['tree'], arrival), 'route_lineage':target_lineage})
            branch['focus'] = target['focus']
            branch['lineage']['source_refs'] = inherited_refs
            branch['visited'].append({'tree':target['tree'],'payload_hash':payload_hash})
            branch['seen_arrival_ids'].append(arrival['id'])
        else:
            bid = 'B' + str(state['used']['branches'])
            child = {'id':bid,'parent_branch':branch['id'],'root_branch':branch['root_branch'],
                     'question_id':branch['question_id'],'epoch':branch['epoch'],'status':'ready','rest':None,
                     'focus':target['focus'], 'lineage':target_lineage, 'visits':[visit(target['tree'], arrival)],
                     'visited':copy.deepcopy(branch['visited']) + [{'tree':target['tree'],'payload_hash':payload_hash}],
                     'seen_arrival_ids':copy.deepcopy(branch['seen_arrival_ids']) + [arrival['id']]}
            state['branches'][bid] = child
            state['used']['branches'] += 1
            decision['children'].append(bid)
    decision['status'] = 'routed'
    return decision


def apply_event(document, command, recorded_at=None):
    require(isinstance(command, dict) and len(cycle.encoded(command)) <= 70000, 'Keep a command bounded')
    garden.identifier(command.get('event_id'))
    actor(command.get('actor'))
    previous = next((e for e in document['events'] if e['command']['event_id'] == command['event_id']), None)
    if previous:
        require(previous['command'] == command, 'An event ID cannot replace earlier input')
        return copy.deepcopy(document)
    require(command.get('expected_revision') == document['state']['revision'] and type(command.get('expected_revision')) is int,
            'Stale revision; reload before writing')
    require(len(document['events']) < document['state']['limits']['max_events'], 'Event budget exhausted')
    result = copy.deepcopy(document)
    state = result['state']
    branch = state['branches'].get(command.get('branch_id'))
    require(branch is not None, 'Unknown branch')
    kind = command.get('kind')
    if kind == 'step':
        decision = step(state, branch, command, result['initial']['config'])
    elif kind == 'route':
        decision = route(state, branch, command, result['initial']['config'])
    elif kind == 'rest':
        require(branch['status'] == 'ready', 'Only an active branch can take a participant rest')
        require(isinstance(command.get('reason'), str) and command['reason'].strip(), 'Rest needs a short reason')
        rest(branch, command['reason'])
        decision = {'status':'rest'}
    elif kind == 'resume':
        require(branch['status'] == 'resting' and command.get('reason'), 'Resume needs a resting branch and reason')
        require(branch['rest']['kind'] == 'participant', 'Completed, looped or exhausted work needs a new pass or arrival, not a resume bypass')
        branch.update(status='ready', rest=None)
        decision = {'status':'resumed'}
    elif kind == 'arrive':
        require(branch['status'] == 'resting' and branch['rest']['kind'] in {'return','loop'}, 'New arrival requires a completed or loop-resting branch')
        require(command.get('new_arrival') is not None, 'Supply the materially new arrival')
        decision = return_arrival(state, branch, command['new_arrival'], command.get('reason'))
    else:
        raise cycle.CycleError('Unknown Garden command')
    state['revision'] += 1
    result['state_sha256'] = cycle.digest(state)
    result['events'].append({'command':copy.deepcopy(command), 'recorded_at':recorded_at or cycle.now(),
                             'before':document['state_sha256'], 'after':result['state_sha256'], 'decision':copy.deepcopy(decision)})
    require(len(cycle.encoded(result)) <= 2_000_000, 'Traversal record exceeds 2 MiB; rest and start a linked pass')
    return result


def replay(document):
    require(document.get('schema_version') == VERSION, 'Unknown traversal schema')
    initial = document['initial']
    require(cycle.digest(initial['config']) == document['config_sha256'], 'Configuration snapshot changed')
    rebuilt = new_document(initial['config'], initial['packet'], initial['registry'])
    for event in document['events']:
        rebuilt = apply_event(rebuilt, event['command'], event['recorded_at'])
    require(rebuilt == document, 'Replay differs from saved history or current state')
    return rebuilt


def path_for(root, rid):
    return Path(root) / STORE / (garden.identifier(rid) + '.json')


def save(root, document):
    rid = document['state']['run_id']
    cycle.write_json(path_for(root, rid), document, replace=True)
    project(root)


def start(root, packet):
    with cycle.locked(root) as root:
        path = path_for(root, packet['run_id'])
        if path.exists():
            old = replay(cycle.read_json(path))
            require(old['initial']['packet'] == packet, 'Run ID already belongs to another start packet')
            project(root)
            return old
        document = new_document(load_config(root), packet, cycle.read_json(root / 'operations/questions.json'))
        save(root, document)
        return document


def submit(root, rid, command):
    with cycle.locked(root) as root:
        document = replay(cycle.read_json(path_for(root, rid)))
        state = document['state']
        registry = cycle.read_json(root / 'operations/questions.json')
        require(registry['questions'].get(state['question_id'], {}).get('epoch') == state['epoch'], 'Question epoch changed; start a new linked pass')
        result = apply_event(document, command)
        save(root, result)
        return result


def project(root, destination=None, record_base_url='https://github.com/Jaradyne/Dis-Unity/blob/week-one-state/'):
    root = Path(root)
    destination = Path(destination) if destination else root / THRESHOLD
    rows = []
    for path in sorted((root / STORE).glob('*.json')):
        document = replay(cycle.read_json(path))
        state = document['state']
        for bid, branch in state['branches'].items():
            rows.append({'run_id':state['run_id'],'branch_id':bid,'parent_branch':branch['parent_branch'],
                         'question_id':branch['question_id'],'epoch':branch['epoch'],'tree':current(branch)['tree'],
                         'node':node(branch),'status':branch['status'],'focus':branch['focus'],
                         'rest_reason':(branch['rest'] or {}).get('reason',''), 'steps_used':state['used']['steps'],
                         'branches_used':state['used']['branches'],'model_calls':0,
                         'record':record_base_url + path.relative_to(root).as_posix()})
        cycle.write_json(destination / (state['run_id'] + '.json'), {
            'schema_version':'digestion-garden-materials-1','run_id':state['run_id'],'status':'available_for_digestion',
            'record_ref':str(path.relative_to(root)), 'record_sha256':cycle.digest(document),
            'state_sha256':document['state_sha256'],'branches':list(state['branches']),
            'meaning':'Supplied traversal and routing; no new evidence, model dispatch or Governor review.'}, replace=True)
    fields = ['run_id','branch_id','parent_branch','question_id','epoch','tree','node','status','focus','rest_reason','steps_used','branches_used','model_calls','record']
    out = io.StringIO(newline=''); writer = csv.DictWriter(out, fieldnames=fields, lineterminator='\n'); writer.writeheader()
    for row in rows:
        writer.writerow({k:"'"+v if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@')) else v for k,v in row.items()})
    cycle.write_bytes(destination / 'branches.csv', out.getvalue().encode(), replace=True)
    return {'branches':len(rows),'index':str(destination / 'branches.csv')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('action', choices=['start','submit','inspect','replay','project'])
    parser.add_argument('--file', type=Path)
    parser.add_argument('--run')
    args = parser.parse_args()
    try:
        if args.action == 'start': result = start(args.root, cycle.read_json(args.file))
        elif args.action == 'submit': result = submit(args.root, args.run, cycle.read_json(args.file))
        elif args.action in {'inspect','replay'}: result = replay(cycle.read_json(path_for(args.root,args.run)))
        else:
            with cycle.locked(args.root):
                result = project(args.root)
        print(json.dumps(result if args.action in {'inspect','project'} else {'status':'ok','run_id':result['state']['run_id'],
                         'revision':result['state']['revision'],'state_sha256':result['state_sha256']}, ensure_ascii=False, indent=2))
        return 0
    except (cycle.CycleError, OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(json.dumps({'status':'blocked','reason':str(exc)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
