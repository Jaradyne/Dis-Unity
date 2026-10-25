#!/usr/bin/env python3
"""Verify published bytes and retained official HTTP bodies, then replay offline."""
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import community_capacity
import cycle

REPORT=Path(__file__).resolve().parent


def validate_publication_paths(manifest):
    """Reject excluded bytes under aliases and temporary receipt artifacts."""
    excluded_paths={x['excluded_repository_path'] for x in manifest['excluded']}
    excluded_hashes={x['sha256'] for x in manifest['excluded']}
    for name,digest in manifest['files_sha256'].items():
        path=Path(name)
        assert not path.is_absolute() and '..' not in path.parts,name
        assert name not in excluded_paths and digest not in excluded_hashes,name
        if 'receipts' in path.parts:
            assert not any(part.startswith('.') for part in path.parts),name


def verify():
    manifest=json.loads((REPORT/'PUBLICATION.json').read_text())
    assert manifest['version']=='richmond-publication-1'
    validate_publication_paths(manifest)
    for name,digest in manifest['files_sha256'].items():
        path=(ROOT/name).resolve()
        assert path.is_relative_to(ROOT) and path.is_file(),name
        assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
    assert cycle.digest(cycle.read_json(ROOT/'Resilience_Cascade_STATE.json'))==manifest['canonical_digest']
    source=cycle.read_json(REPORT/'sources.json');verified=set()
    for item in source['sources']:
        for material in item.get('materials',[]):
            if material['kind']!='complete_origin_http_record':continue
            path=ROOT/material['path'];receipt=cycle.read_json(path)
            body=receipt['response']['body']
            assert body['complete'] is True and body['encoding']=='base64'
            raw=base64.b64decode(body['content'],validate=True)
            assert len(raw)==body['received_bytes']
            assert hashlib.sha256(raw).hexdigest()==body['saved_sha256']==material['body_sha256']
            assert receipt['request']['url']==item['url']
            verified.add(str(path))
    excluded={x['excluded_repository_path'] for x in manifest['excluded']}
    assert not excluded.intersection(manifest['files_sha256'])
    community_capacity.build(ROOT,check=True)
    return {'status':'pass','published_files':len(manifest['files_sha256']),
            'complete_primary_bodies_verified':len(verified),'canonical_unchanged':True,
            'garden':'ten nodes, one resting branch, no model calls',
            'scope':'Offline byte/history replay, not current empirical verification or Governor review',
            'excluded_originals_reconstructable':False}


if __name__=='__main__':
    try:print(json.dumps(verify(),indent=2))
    except (AssertionError,ValueError,KeyError,OSError,cycle.CycleError) as exc:
        print('INVALID: '+str(exc),file=sys.stderr);sys.exit(1)
