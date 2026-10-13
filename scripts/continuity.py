#!/usr/bin/env python3
"""Validate/replay a supplied relationship journal and project it through Garden.

Standard library only. No network, source collection, inference or evidence admission.
"""
from __future__ import annotations

import argparse
import calendar
import copy
from datetime import date, datetime
import json
from pathlib import Path
import re
import sys

import cycle
import garden_runtime as garden

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = Path('schemas/continuity-relationship.schema.json')
REFERENCES = Path('operations/continuity/references.json')
JOURNAL = Path('operations/continuity/journal.json')
OUTPUT = Path('reports/continuity/generated')
ZERO = '0' * 64


class ContinuityError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise ContinuityError(message)


def strict_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=pairs,
                      parse_constant=lambda v: (_ for _ in ()).throw(ContinuityError('Nonfinite JSON')))


def shape(value, schema, where='relationship'):
    """Validate the finite JSON Schema subset used by the checked-in schema."""
    supported = {'$schema', '$id', 'title', 'type', 'anyOf', 'enum', 'const',
                 'properties', 'required', 'additionalProperties', 'items',
                 'minItems', 'minLength', 'pattern'}
    require(set(schema) <= supported, where + ': unsupported schema keyword')
    if 'anyOf' in schema:
        for option in schema['anyOf']:
            try:
                shape(value, option, where)
                return
            except ContinuityError:
                pass
        raise ContinuityError(where + ': no allowed shape')
    if 'enum' in schema:
        require(value in schema['enum'], where + ': invalid enum')
    if 'const' in schema:
        require(type(value) is type(schema['const']) and value == schema['const'], where + ': invalid constant')
    typ = schema.get('type')
    checks = {'object': lambda x: isinstance(x, dict), 'array': lambda x: isinstance(x, list),
              'string': lambda x: isinstance(x, str), 'null': lambda x: x is None}
    if typ:
        require(typ in checks and checks[typ](value), where + ': expected ' + typ)
    if typ == 'object':
        props = schema['properties']
        require(set(schema.get('required', [])) <= set(value), where + ': missing fields')
        if schema.get('additionalProperties') is False:
            require(set(value) <= set(props), where + ': unexpected fields')
        for key, item in value.items():
            shape(item, props[key], where + '.' + key)
    elif typ == 'array':
        require(len(value) >= schema.get('minItems', 0), where + ': too few entries')
        for i, item in enumerate(value):
            shape(item, schema['items'], where + '[' + str(i) + ']')
    elif typ == 'string':
        require(len(value.strip()) >= schema.get('minLength', 0), where + ': empty string')
        if 'pattern' in schema:
            require(re.fullmatch(schema['pattern'], value) is not None, where + ': invalid identifier')


def local_path(root, path):
    require(isinstance(path, str) and path and not Path(path).is_absolute(), 'Use repository-relative paths')
    root = Path(root).resolve()
    result = (root / path).resolve()
    require(result.is_relative_to(root), 'Reference escapes repository')
    return result


def resolve(root, catalog):
    require(set(catalog) == {'version', 'references'} and catalog['version'] == 'continuity-references-1',
            'Invalid reference catalog')
    require(isinstance(catalog['references'], dict), 'References must be keyed objects')
    resolved, files = {}, {}
    for key, binding in catalog['references'].items():
        require(re.fullmatch(r'[A-Z][A-Z0-9-]*', key) is not None, 'Invalid reference alias')
        require(set(binding) == {'kind', 'path', 'collection', 'id_field', 'record_id', 'sha256'}, 'Invalid binding')
        require(binding['kind'] in {'event', 'source'}, 'Unknown reference kind')
        expected = ('events', 'event_id') if binding['kind'] == 'event' else ('sources', 'source_id')
        require((binding['collection'], binding['id_field']) == expected, 'Reference kind/selector mismatch')
        path = local_path(root, binding['path'])
        if path not in files:
            files[path] = strict_json(path)
        records = files[path][binding['collection']]
        require(isinstance(records, list), 'Reference collection must be a list')
        matches = [r for r in records if r.get(binding['id_field']) == binding['record_id']]
        require(len(matches) == 1, key + ': missing or ambiguous shared record')
        record = matches[0]
        require(cycle.digest(record) == binding['sha256'], key + ': pinned record changed')
        if binding['kind'] == 'source':
            require(record.get('source_family') or record.get('source_lineage'), key + ': source lineage absent')
        resolved[key] = {'binding': binding, 'record': record}
    return resolved


def day(value):
    if isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    return None


def date_value(value):
    if value is None:
        return
    require(isinstance(value, str), 'Date must be a string or unknown/null')
    if re.fullmatch(r'\d{4}-\d{2}', value):
        try:
            date.fromisoformat(value + '-01')
            return
        except ValueError:
            pass
    require(day(value) is not None, 'Use ISO day/month dates; unknown is null')


def date_bounds(value):
    """Month-only values retain their full possible interval."""
    date_value(value)
    if value is None:
        return None
    if len(value) == 7:
        year, month = map(int, value.split('-'))
        return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])
    return day(value), day(value)


def chronological(relation, resolved):
    a = resolved[relation['from_event']]['record'].get('event_date')
    b = resolved[relation['to_event']]['record'].get('event_date') if relation['to_event'] else None
    da, db = day(a), day(b)
    if da and db:
        lag = (db - da).days
        order = 'precedes' if lag > 0 else ('same_day' if lag == 0 else 'follows')
    else:
        lag, order = None, 'unresolved_or_imprecise'
    return {'from_event_date': a, 'to_event_date': b, 'order': order, 'lag_days': lag,
            'meaning': 'Date comparison only; no inference of mechanism, implementation or causation.'}


def validate_relation(relation, schema, resolved):
    shape(relation, schema)
    def known(key, kind):
        require(key in resolved and resolved[key]['binding']['kind'] == kind, 'Missing/wrong-kind ' + kind + ': ' + str(key))
    known(relation['from_event'], 'event')
    if relation['to_event'] is None:
        require(bool(relation['unobserved_target']), 'Missing target needs an explicit unknown description')
        require(relation['epistemic_status'] in {'hypothesized', 'unknown', 'contested', 'refuted'},
                'Unobserved endpoint cannot be established')
    else:
        known(relation['to_event'], 'event')
        require(relation['unobserved_target'] is None, 'Observed endpoint cannot also be missing')
    for ref in relation['context_events']:
        known(ref, 'event')
    for evidence in relation['supporting_evidence']:
        known(evidence['source_ref'], 'source')
    for group in ['ordinary_explanations', 'counterevidence']:
        for explanation in relation[group]:
            for ref in explanation['source_refs']:
                known(ref, 'source')
    if relation['epistemic_status'] in {'documented', 'partly_documented'}:
        require(any(e['basis'] == 'direct_record' for e in relation['supporting_evidence']),
                'Documented edges need explicit direct-record support; time/context alone cannot establish them')
    if relation['relationship_type'] == 'precedes':
        require(chronological(relation, resolved)['order'] == 'precedes', 'Precedes requires resolved ordered day dates')
    for field in ['start', 'end']:
        date_value(relation['time_scope'][field])
    start, end = relation['time_scope']['start'], relation['time_scope']['end']
    if start and end:
        require(date_bounds(start)[0] <= date_bounds(end)[1], 'Definitely reversed time interval')


def make_entry(relationship, *, sequence, recorded_at, actor, reason, expected_revision, previous):
    entry = {'sequence': sequence, 'recorded_at': recorded_at, 'actor': actor, 'reason': reason,
             'expected_revision': expected_revision, 'previous_entry_sha256': previous,
             'relationship': copy.deepcopy(relationship)}
    return {**entry, 'entry_sha256': cycle.digest(entry)}


def replay(root=ROOT, journal=None, catalog=None, schema=None):
    schema = strict_json(Path(root) / SCHEMA) if schema is None else schema
    catalog = strict_json(Path(root) / REFERENCES) if catalog is None else catalog
    journal = strict_json(Path(root) / JOURNAL) if journal is None else journal
    require(set(journal) == {'version', 'schema_sha256', 'references_sha256', 'entries'}, 'Invalid journal fields')
    require(journal['version'] == 'continuity-journal-1', 'Unknown journal version')
    require(journal['schema_sha256'] == cycle.digest(schema), 'Schema snapshot mismatch')
    require(journal['references_sha256'] == cycle.digest(catalog), 'Reference manifest mismatch')
    resolved = resolve(root, catalog)
    latest, revisions, history = {}, {}, []
    previous, prior_stamp = ZERO, None
    require(isinstance(journal['entries'], list) and journal['entries'], 'Journal needs entries')
    for i, entry in enumerate(journal['entries'], 1):
        require(set(entry) == {'sequence','recorded_at','actor','reason','expected_revision','previous_entry_sha256','relationship','entry_sha256'}, 'Invalid journal entry')
        require(type(entry['sequence']) is int and entry['sequence'] == i, 'Journal sequence mismatch')
        require(entry['previous_entry_sha256'] == previous, 'Broken history chain')
        body = {k: v for k, v in entry.items() if k != 'entry_sha256'}
        require(cycle.digest(body) == entry['entry_sha256'], 'Entry modified')
        require(isinstance(entry['actor'], str) and entry['actor'].strip() and isinstance(entry['reason'], str) and entry['reason'].strip(), 'Attribution and revision reason required')
        try:
            stamp = datetime.fromisoformat(entry['recorded_at'].replace('Z', '+00:00'))
        except (ValueError, TypeError, AttributeError) as exc:
            raise ContinuityError('Invalid entry timestamp') from exc
        require(stamp.tzinfo is not None and (prior_stamp is None or stamp >= prior_stamp), 'Journal timestamps must be aware and nondecreasing')
        relation = entry['relationship']
        validate_relation(relation, schema, resolved)
        rid = relation['relationship_id']
        old = latest.get(rid)
        require(type(entry['expected_revision']) is int and entry['expected_revision'] == revisions.get(rid, 0), 'Stale relationship revision')
        if old:
            require(all(old[k] == relation[k] for k in ('from_event', 'to_event', 'relationship_type', 'unobserved_target')),
                    'Different endpoints/type require a new relationship ID; preserve the original hypothesis')
            if old['epistemic_status'] != relation['epistemic_status']:
                require(old['supporting_evidence'] != relation['supporting_evidence'] or old['counterevidence'] != relation['counterevidence'],
                        'Evidence-status revision requires an explicit changed evidence assessment')
        latest[rid] = copy.deepcopy(relation)
        revisions[rid] = revisions.get(rid, 0) + 1
        history.append({'sequence': i, 'relationship_id': rid, 'revision': revisions[rid],
                        'epistemic_status': relation['epistemic_status'], 'recorded_at': entry['recorded_at'],
                        'actor': entry['actor'], 'reason': entry['reason'], 'entry_sha256': entry['entry_sha256']})
        previous, prior_stamp = entry['entry_sha256'], stamp
    state = {'version':'continuity-state-1', 'status':'supplied relationships for review; not canonical admission',
             'journal_sha256':cycle.digest(journal), 'relationships':latest, 'revisions':revisions,
             'history':history, 'temporal':{rid: chronological(r, resolved) for rid, r in sorted(latest.items())}}
    return state, resolved


def source_keys(relation):
    refs = [e['source_ref'] for e in relation['supporting_evidence']]
    for group in ['ordinary_explanations', 'counterevidence']:
        refs += [r for e in relation[group] for r in e['source_refs']]
    return sorted(set(refs))


def garden_pass(root, relation, resolved, recorded_at):
    rid = relation['relationship_id']
    qid = 'Q-' + rid
    actor = {'name':'Work Aiden', 'runtime':'deterministic projection of supplied relationship', 'model':'none invoked'}
    sources = []
    for key in source_keys(relation):
        record = resolved[key]['record']
        sources.append({'ref':key, 'lineage_id':record.get('source_family') or record['source_lineage'],
                        'kind':'public_source', 'binding':resolved[key]['binding'],
                        'access_limit':record.get('limitations', 'See shared source record')})
    arrival = {'id':rid + '-ARRIVAL', 'from':str(JOURNAL), 'to':'INIT:ROOT-0001',
               'payload':{'relationship_id':rid, 'relationship_sha256':cycle.digest(relation)}}
    start = {'run_id':rid + '-GARDEN', 'question_id':qid, 'epoch':1, 'actor':actor, 'tree':'INIT',
             'focus':relation['claim'], 'arrival':arrival, 'sources':sources,
             'budget':{'max_steps':10,'max_branches':1,'max_events':10,'max_fanout':0,'model_calls':0},
             'status':'case-local supplied projection; no shared Question registration'}
    source_refs = [x['ref'] for x in sources]
    outputs = [
        ('ROOT', {'name':rid + ': ' + relation['relationship_type']}),
        ('ARRIVAL', {'arrival':arrival, 'language_glance':{'languages':[], 'basis':'unknown',
            'issuing_office':'See shared source metadata', 'surface_kind':'summary','source_refs':source_refs,
            'note':'This projector performs no language detection or fresh source reading.'}}),
        ('EPIST', {'prompt':relation['claim'], 'starting_state':relation['epistemic_status'],
                   'time_scope':relation['time_scope'], 'chronology':chronological(relation,resolved)}),
        ('FUNC', {'task':'Inspect the declared relationship against pinned shared references',
                  'function':relation['scope'], 'from_event':relation['from_event'], 'to_event':relation['to_event'],
                  'unobserved_target':relation['unobserved_target'], 'evidence':relation['supporting_evidence']}),
        ('MIRROR', {'comparisons':[{'explanation':x['statement'],'queries':[], 'answers':[{'source_refs':x['source_refs']}]} for x in relation['ordinary_explanations']],
                    'counterevidence':relation['counterevidence'], 'information_lineage':{
                        'parent_answer_visible':True,'source_refs':source_refs,'parent_output_refs':[str(JOURNAL)],
                        'criteria_refs':[str(SCHEMA)],'api_record_refs':[],'test_origin':'inherited'}}),
        ('CROSS', {'inherited':[{'ref':r,'status':'inherited archive; not independent corroboration'} for r in source_refs],
                   'independent':[],'bridge':[{'question':relation['next_test']['question'],
                       'status':'proposed only; not executed','source_refs':source_refs}]}),
        ('RESID', {'summary':'; '.join(relation['limitations']), 'next_test':relation['next_test'],
                   'predicates':{'consequential':True,'distinct_functions':False,'language_exception':None}}),
        ('MEAN', {'summary':relation['claim'] + ' — supplied status: ' + relation['epistemic_status']}),
        ('EXIT', {'kind':'question','summary':relation['next_test']['question'], 'epistemic_status':relation['epistemic_status']}),
        ('RETURN', {'new_arrival':None,'reason':relation['rest_until']})]
    document = garden.new_document(garden.load_config(root), start, {'questions':{qid:{'epoch':1}}})
    for i, (node, output) in enumerate(outputs):
        command = {'event_id':rid + '-STEP-' + str(i+1), 'expected_revision':i, 'actor':actor,
                   'branch_id':'B0','kind':'step','node':node,'output':output}
        document = garden.apply_event(document,command,recorded_at)
    return garden.replay(document)


def markdown(state, resolved):
    def display(value):
        return 'unknown' if value is None else str(value)
    def cell(value):
        return str(value).replace('|','\\|').replace('\n',' ')
    def link(ref):
        bind = resolved[ref]['binding']
        return '[' + bind['record_id'] + '](../../../' + bind['path'] + ')'
    lines = ['# Thread of Continuity', '',
             'Supplied, reviewable relationships reconstructed from shared records. Date order is not causation. '
             'Garden replay checks record consistency, not empirical truth. No new source collection or live worker execution.', '',
             '| Relationship | Lanes | Shared events | Status | Temporal comparison |',
             '| --- | --- | --- | --- | --- |']
    for rid, relation in sorted(state['relationships'].items()):
        target = link(relation['to_event']) if relation['to_event'] else '**Unobserved target**'
        temporal = state['temporal'][rid]
        lines.append('| ' + ' | '.join([rid,cell(relation['lanes']['from']+' → '+relation['lanes']['to']),
            link(relation['from_event'])+' → '+target,relation['epistemic_status'],
            cell(display(temporal['from_event_date'])+' → '+display(temporal['to_event_date'])+'; '+temporal['order'])])+' |')
    for rid, relation in sorted(state['relationships'].items()):
        lines += ['', '## ' + rid + ' · ' + relation['relationship_type'], '', relation['claim'], '',
                  '**Scope:** ' + relation['scope'], '', '**Time scope:** ' + display(relation['time_scope']['start'])
                  + ' → ' + display(relation['time_scope']['end']) + '. ' + relation['time_scope']['note'], '',
                  '**Supplied status:** ' + relation['epistemic_status'] + '. Revision ' + str(state['revisions'][rid]) + '.', '']
        if relation['unobserved_target']:
            lines += ['**Missing event:** '+relation['unobserved_target'], '']
        lines += ['**Support and lineage:**','']
        for e in relation['supporting_evidence']:
            source = resolved[e['source_ref']]['record']
            lines.append('- '+link(e['source_ref'])+' · '+e['basis']+' · '+e['locator']+': '+e['statement'])
            lines.append('  Source family: '+str(source.get('source_family',source.get('source_lineage')))+'. Access: '+str(source.get('access_level','see shared record'))+'.')
            lines.append('  Publication: '+display(source.get('publication_date'))+'; catalog retrieval: '
                         +display(source.get('retrieved_date_utc'))+'. Limits: '+str(source.get('limitations','See shared record')))
        for label, group in [('Ordinary explanations','ordinary_explanations'),('Counterevidence / constraints','counterevidence')]:
            lines += ['', '**'+label+':**', '']
            for item in relation[group]:
                lines.append('- '+item['statement']+' '+', '.join(link(ref) for ref in item['source_refs']))
        lines += ['', '**Limits:** ' + ' '.join(relation['limitations']), '', '**One bounded next test (proposed):**', '']
        for key in ('question','required_record','supports_if','weakens_if','stop_condition'):
            lines.append('- '+key.replace('_',' ').capitalize()+': '+relation['next_test'][key])
        lines += ['', '**Rest:** '+relation['rest_until'], '']
        lines += ['**Original event dates and qualifications:**', '']
        for ref in dict.fromkeys([relation['from_event'],relation['to_event'],*relation['context_events']]):
            if ref is None:
                continue
            rec = resolved[ref]['record']
            dates = {k:v for k,v in rec.items() if 'date' in k or k in ('date_precision','discovery','discovery_status','status','implementation_status','uncertainty','limitations','limits')}
            lines.append('- '+link(ref)+': '+'; '.join(k.replace('_',' ')+': '+display(v) for k,v in sorted(dates.items())))
    return '\n'.join(lines)+'\n'


def outputs(root=ROOT):
    state, resolved = replay(root)
    journal = strict_json(Path(root)/JOURNAL)
    result = {'relationships.json':cycle.encoded(state), 'DIGEST.md':markdown(state,resolved).encode('utf-8')}
    for rid, relation in sorted(state['relationships'].items()):
        timestamp = next(e['recorded_at'] for e in reversed(journal['entries']) if e['relationship']['relationship_id'] == rid)
        doc = garden_pass(root,relation,resolved,timestamp)
        result['garden/'+rid+'.json'] = cycle.encoded(doc)
    return result


def build(root=ROOT, check=False):
    generated = outputs(root)
    destination = Path(root)/OUTPUT
    if check:
        actual = {p.relative_to(destination).as_posix():p.read_bytes() for p in destination.rglob('*') if p.is_file()}
        require(actual == generated, 'Generated continuity projections differ; inspect before rebuilding')
    else:
        for name, body in generated.items():
            path = destination/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(body)
    return len(generated)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['validate','replay','build','check'])
    parser.add_argument('--root',type=Path,default=ROOT)
    args = parser.parse_args()
    try:
        if args.command in {'build','check'}:
            count = build(args.root,args.command=='check')
            print(f'PASS: {count} deterministic outputs; {count - 2} case-local Garden runs; no dispatch')
        else:
            state,_ = replay(args.root)
            print(f"PASS: {len(state['relationships'])} relationships, {len(state['history'])} journal entries; {cycle.digest(state)}")
    except (ContinuityError,cycle.CycleError,ValueError,KeyError,TypeError,OSError) as exc:
        print('INVALID: '+str(exc),file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
