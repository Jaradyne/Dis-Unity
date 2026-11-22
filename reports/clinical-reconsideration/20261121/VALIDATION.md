# Integration validation

Work Aiden, coordinator · November 22, 2026 Pacific. Base commit `9f50a6f7ea7d05874961fa149ea0dd4479f58701`. This records completed local checks; hosted CI is recorded on the pull request.

**325 Python tests passed**, including 22 clinical-reconsideration tests. All 21 listed validation commands passed. The full suite uses its existing fixture/mock paths; status messages printed by tests are not evidence of a new live provider or operational-branch run.

| Check | Command | Result |
| --- | --- | --- |
| unit-tests | `python -m unittest discover -s tests -v` | passed |
| canonical | `python scripts/validate_state.py Resilience_Cascade_STATE.json` | passed |
| cycle | `python scripts/cycle.py status RC-004` | passed |
| boss-ui | `node tests/test_boss_ui.js` | passed |
| garden-example | `python scripts/garden_example.py --output examples/garden-traversal/worked` | passed |
| continuity | `python scripts/continuity.py check` | passed |
| camp | `python examples/garden-case-studies/camp-east-montana/replay.py --check` | passed |
| safeguards | `python scripts/safeguards.py check` | passed |
| evidence-arrival | `python scripts/evidence_arrival.py check` | passed |
| evidence-viewer | `python scripts/build_evidence_viewer.py --check` | passed |
| relays | `python scripts/relays.py check` | passed |
| patient-care | `python scripts/patient_care.py check` | passed |
| clinical-reconsideration | `python scripts/clinical_reconsideration.py check` | passed |
| shelters | `python scripts/shelter_accountability.py check` | passed |
| campus | `python scripts/campus_motel.py check` | passed |
| community-capacity | `python scripts/community_capacity.py check` | passed |
| community-ui | `node tests/test_community_capacity_ui.js` | passed |
| meaning-tower | `python scripts/build_meaning_tower.py` | passed |
| state-views | `python scripts/render_state.py Resilience_Cascade_STATE.json` | passed |
| old-generated-unchanged | `git diff --exit-code -- examples/garden-traversal/worked web/meaning-tower/index.html state` | passed |
| diff-check | `git diff --check` | passed |

## Saved acceptance

- One fictional pathway; 16 care milestones; 15 supplied events; two preserved assessment revisions.
- Revision evidence cutoffs: 2026-11-05, 2026-11-13. These are fictional record cutoffs, not patient observation dates.
- Ten Garden nodes, one resting branch, zero provider/model dispatches. Two reconstructions matched every saved Garden file byte for byte.
- New Garden state SHA256: `d17488583c67b9a31dabc696f88e2f62262326fd2ef8fc6eafadb089d9281712`.
- Prior Patient Care Continuity state SHA256 remains `0fd99c8ecd65ca64d6719191010e8ff34aabb71de92af80bc335a91afb47da50`.
- RC-004 canonical file SHA256 remains `16d04f8bb35a588caca60517f90a11944cfbafac7951402d059a6d6131de97b7`.
- Existing tracked changes are limited to the root index and CI addition; all other additions belong to this new wing. Prior runtime, canonical and case files remain unchanged.

## Scope and limitations

The negative tests reject inferred error from a report or changed opinion, policy/booking as a performed review, invented independence, selective omission of contrary evidence, impossible causal chronology, wrong correction recipients, dispatch as receipt, and correction as benefit. A later conflicting independence disclosure is appended without modifying the original opinion or earlier journal entries. Initial opinions may be provisional, definitive or unspecified without settling accuracy.

Validation establishes consistency with supplied records. It does not verify medical truth, professional independence in practice, negligence, individual coverage, clinical outcomes, or the authenticity of a future external submission. The demonstration is synthetic; policy inspection is separately dated November 21 and has no complete raw HTTP archive. Independent review and its exact file pins are in [REVIEW.md](REVIEW.md).

No new operational window, runtime Bee, recurring collector, provider call, outreach, Governor power or canonical admission was enabled.
