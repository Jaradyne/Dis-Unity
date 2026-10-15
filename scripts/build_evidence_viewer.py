#!/usr/bin/env python3
"""Build a self-contained, read-only viewer from the saved Camp arrival/review."""
import argparse
import json
from pathlib import Path

import continuity as shared
import cycle
import evidence_arrival as arrival

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'web/evidence-arrival'
EVIDENCE_COMMIT = 'cb4ac6a79075f92fcdef9492428d9d307661b6f2'
REMOTE = 'https://github.com/Jaradyne/Dis-Unity/blob/' + EVIDENCE_COMMIT + '/'


def document():
    # Reconstruct and validate existing evidence without capture or mutation.
    outputs = arrival.outputs(ROOT)
    for name, expected in outputs.items():
        shared.require((ROOT/'reports/evidence-arrival/generated'/name).read_bytes() == expected,
                       'Saved arrival projection differs; review/build the evidence first')
    intake = json.loads(outputs['intake.json'])
    decision = json.loads(outputs['reviewed.json'])
    simulations = json.loads(outputs['simulated.json'])
    handoff = intake['handoffs'][0]
    receipt = arrival.pinned(ROOT, handoff['receipt'])
    review = arrival.pinned(ROOT, decision['review']['evidence_review'])
    shared.require(decision['safeguard_dimensions']['effectiveness'] == 'unknown',
                   'Viewer narrative needs review when the case assessment changes')
    shared.require([x['classification'] for x in simulations['observations']] ==
                   ['new','unchanged','unchanged','changed','changed','unobservable'],
                   'Viewer simulation narrative needs review when its fixtures change')
    data = {
        'evidenceCommit': EVIDENCE_COMMIT,
        'intakeSha256': cycle.digest(intake),
        'observedAt': intake['observations'][0]['observed_at'],
        'reviewedAt': decision['review']['reviewed_at'],
        'httpStatus': receipt['response']['http_status'],
        'receivedBytes': receipt['response']['body']['received_bytes'],
        'rawHash': receipt['response']['body']['saved_sha256'],
        'textHash': handoff['content_sha256'],
        'product': handoff['item_id'],
        'sourceFamily': handoff['source_family'],
        'recommendations': review['recommendations'],
        'reviewer': decision['review']['reviewer'],
        'evidenceReviewer': review['reviewer'],
        'dimensions': decision['safeguard_dimensions'],
        'continuity': decision['review']['continuity']['disposition'],
        'counterevidence': decision['review']['contrary_evidence'],
        'residual': decision['review']['residual'],
        'links': {key:REMOTE + path for key,path in {
            'receipt':handoff['receipt']['path'],
            'assessment':'operations/safeguards/journal.json',
            'review':decision['review']['evidence_review']['path'],
            'foia':'reports/evidence-arrival/FOIA_DRAFT.md',
            'handoff':'reports/evidence-arrival/DIGEST_HANDOFF.md',
        }.items()},
        'simulations': [{
            'id':item['observation_id'], 'classification':item['classification'],
            'handoff':any(h['observation_id']==item['observation_id'] for h in simulations['handoffs']),
            'text':item['text'] if item['observation_id'] in {'SIM-CLOSURE-INCONCLUSIVE','SIM-CONTRADICTORY'} else None,
        } for item in simulations['observations']],
    }
    # Source-derived text remains data, including strings containing HTML.
    encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    template = (FOLDER/'template.html').read_text(encoding='utf-8')
    shared.require(template.count('<!--CASE_DATA-->') == 1, 'Missing/duplicate data slot')
    return template.replace('<!--CASE_DATA-->', '<script type="application/json" id="case-data">'+encoded+'</script>').encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    expected, path = document(), FOLDER/'index.html'
    if args.check:
        shared.require(path.read_bytes() == expected, 'Saved viewer differs')
    else:
        path.write_bytes(expected)
    print('PASS: saved evidence viewer; one static file, no collection or assessment mutation')


if __name__ == '__main__':
    main()
