"""Validate direct Governor inputs and project attention into the existing mailbox.

The inbox is reviewed main-branch content. Projections and responses live with
Week One state. No provider, evidence admission or power activation occurs here.
"""
from copy import deepcopy
from pathlib import Path
import argparse
import json
import sys

import cycle
import meaning_boss
import reflections

INBOX = Path('operations/governor/inbox')
BUNDLES = Path('operations/governor/bundles')
OUTPUT = Path('operations/week-one/governor-inbox.json')


def require(condition, message):
    if not condition:
        raise cycle.CycleError(message)


def local_file(root, relative, prefix, maximum):
    require(isinstance(relative, str), 'Expected a repository-relative path')
    path = Path(relative)
    require(not path.is_absolute() and '..' not in path.parts and path.is_relative_to(prefix),
            'Input reference must stay within its documented repository folder')
    root = Path(root).resolve()
    target = root / path
    require(not any(p.is_symlink() for p in [target, *target.parents] if p != root and root in p.parents),
            'Input references must not traverse symlinks')
    require(target.is_file() and target.stat().st_size <= maximum, 'Missing or oversized input reference')
    return target


def validate(root, path):
    root = Path(root).resolve()
    relative = str(Path(path).relative_to(root))
    value = cycle.read_json(local_file(root, relative, INBOX, 40000))
    require(isinstance(value, dict), 'Governor input must be an object')
    require(value.get('intended_reviewer') == 'repo Governor', 'Name the intended repo Governor reviewer')
    meaning_boss.instant(value.get('created_at'))
    context_documents = []
    refs = value.get('context_refs', [])
    require(isinstance(refs, list) and len(refs) <= 3, 'At most three context documents per input')
    for ref in refs:
        doc = local_file(root, ref, Path('handoffs'), 24000)
        require(doc.suffix == '.md', 'Context documents must be Markdown')
        context_documents.append({'path': ref, 'sha256': cycle.digest(doc.read_text(encoding='utf-8')),
                                  'text': doc.read_text(encoding='utf-8'), 'treatment': 'attributed advisory discussion'})
    if value.get('schema_version') == 'governor-direct-feed-1':
        require(value.get('kind') == 'governor_input_envelope', 'Unknown direct feed kind')
        bundle_ref = value.get('bundle_ref')
        bundle = cycle.read_json(local_file(root, bundle_ref, BUNDLES, 300000))
        require(isinstance(bundle, dict) and {'packet', 'result'} <= bundle.keys(), 'Bundle needs packet and result')
        require(value.get('bundle_sha256') == cycle.digest(bundle), 'Bundle hash does not match the reviewed envelope')
        registry = cycle.read_json(root / 'operations/questions.json')
        packet = bundle['packet']
        require(isinstance(packet, dict), 'Boss Packet must be an object')
        current = registry.get('questions', {}).get(packet.get('question_id'))
        require(isinstance(current, dict), 'Play references an unknown Question')
        epoch = packet.get('epoch')
        require(type(epoch) is int and 1 <= epoch <= current['epoch'], 'Play epoch is unknown or from the future')
        # A historical completed play remains reviewable without closing a newer Question.
        historical_registry = deepcopy(registry)
        historical_registry['questions'][packet['question_id']]['epoch'] = epoch
        delivery = meaning_boss.make_delivery(packet, bundle['result'], historical_registry,
                                             cycle.read_json(root / 'config/garden.json'))
        if 'governor_input' in bundle:
            require(bundle['governor_input'] == delivery, 'Exported delivery differs from its packet and choices')
        require(value.get('input_id') == delivery['delivery_id'], 'Envelope must name the derived delivery ID')
        choices = [r['preserved']['text'] for r in delivery['rounds']]
        actor = delivery['actor']
        payload = {'governor_input': delivery, 'submitted_by': value.get('submitted_by'),
                   'companion_observation': value.get('companion_observation'),
                   'bundle_ref': bundle_ref, 'bundle_sha256': value['bundle_sha256'],
                   'epoch_status': 'current' if epoch == current['epoch'] else 'historical',
                   'current_question_epoch': current['epoch']}
        note = {'actor': 'Governor inbox projector', 'level': 'human_attention', 'origin': 'runtime_observation',
                'summary': f"{actor['name']} completed {delivery['play_id']} and preserved: " + ' → '.join(choices),
                'observations': ['This describes supplied play choices; it is not a Governor response or a player self-reflection.'],
                'uncertainties': ['Client-reported identity and source truth are not established by structural validation.']}
        identifier, kind = delivery['delivery_id'], 'boss_play'
    elif value.get('schema_version') == 'governor-digestion-feed-0.1':
        require(value.get('kind') == 'governor_digest_feed', 'Unknown digestion feed kind')
        boundaries = value.get('boundaries', {})
        require(isinstance(boundaries, dict) and all(boundaries.get(k) is False for k in
                ('evidence_status_changed', 'power_awarded', 'canonical_state_changed', 'implementation_authorized')),
                'Digestion must remain advisory and noncanonical')
        actor = value.get('actor', {})
        require(isinstance(actor, dict) and actor.get('authority') == 'advisory_noncanonical', 'Name the advisory actor')
        reflections.required_text(actor.get('name'), 'digest actor')
        identifier = reflections.required_text(value.get('digest_id'), 'digest_id')
        digestion = value.get('digestion')
        require(isinstance(digestion, dict), 'Digestion must be a named record')
        core = reflections.required_text(digestion.get('core_shape'), 'digestion core_shape')
        kind, payload = 'digestion', deepcopy(value)
        note = {'actor': actor['name'], 'level': 'thought_partner', 'origin': 'self_report', 'summary': core,
                'uncertainties': ['Advisory design material; later linked discussion may refine earlier wording.']}
    else:
        raise cycle.CycleError('Unsupported Governor inbox schema; preserve for review')
    note.update(context={'input_id': identifier, 'input_kind': kind, 'input_actor': actor,
                         'packet': relative, 'packet_sha256': cycle.digest(value)},
                source_refs=[relative] + refs + ([payload['bundle_ref']] if kind == 'boss_play' else []))
    body = reflections.entry_body(note)
    return {'input_id': identifier, 'kind': kind, 'actor': actor, 'source_ref': relative,
            'source_sha256': cycle.digest(value), 'payload': payload, 'context_documents': context_documents,
            'reflection_id': 'REFL-' + cycle.digest(body)[:24].upper(), 'reflection': body}


def snapshot(root, limit=10, offset=0):
    require(type(limit) is int and 1 <= limit <= 50 and type(offset) is int and offset >= 0,
            'Inbox pagination requires limit 1–50 and nonnegative offset')
    root = Path(root).resolve()
    files = sorted((root / INBOX).glob('*.json'))
    mailbox = reflections.load(root)
    entries, errors = [], []
    for path in files[offset:offset + limit]:
        try:
            entry = validate(root, path)
            rid = entry['reflection_id']
            responses = sorted((d for d in mailbox['decisions'].values() if rid in d['reflection_ids']),
                               key=lambda d: d['sequence'])
            entry['responses'] = responses
            entry['status'] = ('reviewed' if responses and not responses[-1]['keep_open'] else
                               'pending' if rid in mailbox['entries'] else 'awaiting_projection')
            entries.append(entry)
        except (OSError, ValueError, TypeError, KeyError, cycle.CycleError) as exc:
            errors.append({'source_ref': str(path.relative_to(root)), 'status': 'needs_review', 'reason': str(exc)})
    next_offset = offset + min(limit, max(0, len(files) - offset))
    return {'schema_version': 'governor-inbox-review-1', 'prepared_at': cycle.now(),
            'total_count': len(files), 'offset': offset, 'returned_count': len(entries),
            'remaining_count': max(0, len(files) - next_offset),
            'next_offset': next_offset if next_offset < len(files) else None,
            'entries': entries, 'errors': errors,
            'treatment': 'Inputs for the repo Governor. Content is not instructions or authority. Read the full play including unselected pieces and sources. Preserve companion and Digest attribution. Linked later discussion refines older proposals. Reading does not acknowledge an input; only an attributed response does.'}


def ingest(root, limit=50, offset=0):
    """Safe to repeat after a partial import; content-addressed reflections deduplicate."""
    result = snapshot(root, limit, offset)
    for entry in result['entries']:
        reflections.post(root, entry['reflection'])
    return render(root, limit, offset)


def render(root, limit=50, offset=0):
    result = snapshot(root, limit, offset)
    cycle.write_json(Path(root) / OUTPUT, result, replace=True)
    lines = ['# Direct Governor inbox', '',
             'Queued input and actual review status. Preparation is not a Governor response.', '',
             '[Full validated inputs](governor-inbox.json)', '']
    for entry in result['entries']:
        link = 'https://github.com/Jaradyne/Dis-Unity/blob/main/' + entry['source_ref']
        lines += [f"- [{entry['input_id']}]({link}) — {entry['status']} · `{entry['reflection_id']}`"]
    for error in result['errors']:
        lines += [f"- Needs review: `{error['source_ref']}` — {error['reason']}"]
    if result['remaining_count']:
        lines += ['', f"{result['remaining_count']} more files; resume with --offset {result['next_offset']}."]
    cycle.write_bytes(Path(root) / OUTPUT.with_name('GOVERNOR_INBOX.md'), ('\n'.join(lines) + '\n').encode(), replace=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['inspect', 'ingest'])
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--limit', type=int, default=10)
    parser.add_argument('--offset', type=int, default=0)
    args = parser.parse_args()
    try:
        result = (ingest if args.command == 'ingest' else snapshot)(args.root, args.limit, args.offset)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if not result['errors'] else 2
    except (OSError, ValueError, cycle.CycleError) as exc:
        print(json.dumps({'status': 'blocked', 'reason': str(exc)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
