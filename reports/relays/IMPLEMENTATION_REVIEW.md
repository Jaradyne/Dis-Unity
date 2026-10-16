# Relay Continuity independent implementation review

**Final disposition: accepted with limits. No required implementation changes remain for this bounded task.**

Reviewer: `reporting_review`, an in-session reviewer separate from the core/schema/case author. This reviewer authored the negative tests and independently challenged implementation semantics; this is not independent empirical corroboration.

Reviewed at: 2026-10-16T10:04:49.373036+00:00

Baseline commit: `20cb5166ddff33de4a724bca5aa215d0f7a2a481`.

## Final review

The same typed validator and journal handle both `CEM-RELAYS` and the explicitly fictional `DIESEL-RELAYS` without domain-name branching. They reuse the existing strict schema/date/reference helpers, safeguard source lineage and Garden reducer. Each saved pass contains ten supplied nodes, one resting branch, no fanout, zero application model calls and no independent empirical attachment. The implementation adds no source retrieval or operational dispatch path.

The stage/evidence gates preserve the consequential distinctions: announcement or commitment does not become dispatch; acknowledgment does not become physical arrival or downstream action; delivery does not become service effectiveness; missing evidence does not become omission. Affirmative failure and outcome claims require matching evidence classes and polarity. Verification must cite the same scoped outcome record and state its method. A physical stock shortfall remains physical, and required/committed/announced/observed capacities retain their separate bases. Working support requires action or verified continued/recovered outcomes rather than spare capacity alone.

Time checks preserve timezone equivalence and month/day uncertainty, reject definitely reversed/future observations and avoid inventing deadlines or precise lag. The final correction also checks stage and capacity times against the actual review instant: a day-valued cutoff cannot conceal a known future arrival or capacity measurement from an earlier review. Future commitment deadlines remain permitted. Chronology alone cannot support causation, and the bounded generalization status remains `not_assessed`.

The source manifest rejects inherited alias shadowing, hash drift, parent/artifact mismatch and repository escapes. Simulated evidence and events cannot enter empirical cases, and empirical events cannot become simulated observations. The added CEM16 selector and retained PDF hash reuse the existing archive. A design document is not silently admitted as an empirical source.

Append-only journal checks preserve earlier entries, relay identities, scope, evidence, contrary assessments, ordinary explanations, historical issues and capacities, shared references and support edges. Reviewers can revise current stages using new evidence or a counterassessment. Supports and unknowns can change legitimately; both their earlier and revised states remain visible in the journal and readable history. Hashes detect changes against retained pins, not a malicious whole-repository rewrite and reseal.

## Findings resolved during independent challenge

1. Added stage/issue polarity checks, exact capacity-basis evidence matching, positive applicable deadline/causal evidence, and verification tied to the same outcome.
2. Closed event-mode crossing and document-alias validation gaps in addition to the citation-source checks.
3. Preserved prior ordinary explanations, design references and support edges while exposing changing supports/residuals in history.
4. Rejected reviews recorded before their evidence cutoff or definitely later evidence, then closed the remaining review-instant gap for stage/capacity times inside a coarse day cutoff.
5. Corrected one test assumption: the diesel dispatch assessment legitimately cites two positive records. The polarity mutation now isolates the changed record instead of requiring a valid separate movement observation to be discarded. Mixed supporting and contrary material may remain together for review.

The checkpoint below preserves the preliminary state and questions; this final disposition supersedes its pending status.

## Checks performed by this reviewer

- `python -m unittest discover -s tests -p test_relays.py -v`: **25 tests passed** on the final implementation. Tests cover the semantic gates above, missing versus actual deadlines, offset and coarse-date handling, source/event isolation, alias/hash/path tampering, stale/reordered/modified history, prohibited evidence erasure, preservation of resolved residuals, verified support, and renamed domain-neutral cases.
- `python scripts/relays.py check`: **all four saved outputs match deterministic reconstruction**. The tests also compare two independently generated output dictionaries and replay both saved Garden documents.
- Inspected core, schema, references, all three journal revisions, fictional source records, source review, readable projection, docs, handoffs and CI integration. The compact projection labels statuses as supplied assessments, not verified stages. Documentation distinguishes structural validation from evidence truth and the fictional as-of exercise from a historical blind observation.
- `git diff --check` passed. A tracked-path diff against baseline found no changes to canonical/cycle/agent/config/archive inputs, the existing Continuity/Safeguard/Question material, original Camp/evidence-arrival cases and reports, or `scripts/garden_runtime.py`.

Work Aiden separately reports that the existing saved projections and canonical/Meaning Tower/Garden checks passed unchanged, and that the final full integrity suite passed **221 tests in 15.183 seconds** after the review-instant correction. This reviewer did not rerun that entire suite; the independent final 25-test relay run includes the newly added regression test. CI and publishing remain coordinator responsibilities.

## Exact reviewed bytes

SHA-256 hashes below identify this reviewed version; they do not certify empirical truth. This review excludes its own hash to avoid a self-reference and excludes the two handoff prose files, to which the coordinator is appending the final verification result. Their substantive text was read, but those later report-only additions are not covered by an exact hash here. Later changes to the pinned files require checking whether the review still applies.

| File | SHA-256 |
| --- | --- |
| `scripts/relays.py` | `6a57ba0ea0dc930b8c8b6c9ec5dff2a471865ba7edbe3c63e0c61f0fdedd6d7f` |
| `schemas/relay-case.schema.json` | `ed8bd1242824457189811c2bc180683465691c09df62bdacf064d142aab1eafc` |
| `operations/relays/references.json` | `240bc6964386ec099f6d34c8ca77ef3edcade06575aab57bd5c85b6767a9efee` |
| `operations/relays/journal.json` | `967bcbba8379c78288a1dd0367cd05596d1c7597d947485e3a5ee3ebbb235891` |
| `examples/relays/diesel/sources.json` | `634b6130d0acace9c7c7e1a0e6d98d6992c5ea891581c713cd114aea0342ff50` |
| `tests/test_relays.py` | `96e3c4ff934d1a4e5015465e957fa41698c2e095efc276149b8f2fd2f7fe06f9` |
| `docs/RELAY_CONTINUITY.md` | `f324b5c25e142d32145bff848d34bfe870aed0ea2790a9882a1ba0dbf00acee8` |
| `reports/relays/CAMP_SOURCE_REVIEW.md` | `b6206a85b645a62d459d9ecfbea5d7922c0de492298678501ed8c699cd579802` |
| `reports/relays/generated/relays.json` | `7869e808da30db5607d7288a57d089737d4c23665c0366141232ba95d9cdcdc2` |
| `reports/relays/generated/RELAYS.md` | `f2b52d139dc550ebb11c88e8ec463bc1eaf6456e1d9f84ed0f15c034b65bc615` |
| `reports/relays/generated/garden/CEM-RELAYS.json` | `114420a9a96ae3752349d7a5abb136874dc65e260324527f99762fdf3e44c71c` |
| `reports/relays/generated/garden/DIESEL-RELAYS.json` | `a01c992edcf059e013b8bf809ce7982356565aee2623d36eb6117ef9708d34d2` |
| `.github/workflows/verify.yml` | `a7f03b04ca54dccbc9d0ea707e3919be3cf141c37450952da86bba2f5d7bd0d3` |
| `README.md` | `184c27153faa2e575d9a6be5740ec74168f871985b3205b63ac160d991b35cac` |

## Limits and stop condition

This is a bounded implementation and consistency review. Camp source accuracy is separately attributed to `camp_review` in `CAMP_SOURCE_REVIEW.md`; this review does not claim another independent source inspection. The two Camp relays remain one GAO lineage, and the diesel records are invented fixture inputs. No network request, new public evidence, provider call, recurring monitoring, Bee activation, FOIA submission or Governor change was performed by this reviewer.

The validator cannot determine whether an author honestly classifies evidence, whether a source entails a paraphrase, whether a causal analysis is substantively persuasive, or whether people are protected. Human source review remains necessary. No current Camp condition, correction, panel-specific causation, systemic pattern or real diesel/clinical outcome is established by successful tests.

Stop after these two reconstructable cases, their three reviewed snapshots, four deterministic outputs and bounded negative tests. The saved UNKNOWN findings and existing narrow follow-up remain; no expanded research or operational activation follows from acceptance.

---

# Initial implementation checkpoint

Reviewer: `reporting_review`, independent in-session challenge and negative-test author.

Started: 2026-10-16 UTC. Status: initial implementation inspection; no acceptance yet.

Scope: the proposed shared typed relay model and two bounded cases (`CEM-RELAYS` and `DIESEL-RELAYS`). Review source identity and evidence lineage, time precision/cutoff, typed handoff states, missing evidence versus observed omission, resource shortage versus relay failure, append-only reviewed revisions, outcome-backed buffers, simulation isolation and domain independence.

Owned files: `tests/test_relays.py` and this review/checkpoint only. The coordinator owns implementation, schema and case fixtures. No source retrieval, network request, application provider dispatch, new worker/schedule activation, Governor changes or canonical evidence edits.

Tests will target actual semantic failure risks rather than duplicate implementation. Awaiting the final fixtures before exercising the complete two-case replay. The final review will record exact reviewed inputs, checks, limitations and any unresolved findings.

## Initial design findings

The seven stage-specific evidence gates, typed relay kinds, shared source resolution, local schema expansion, supplied journal and existing Garden projection are a suitably bounded design. The implementation adds no collection path.

Potential gaps sent to the coordinator for resolution before final acceptance:

- Evidence polarity (`result`) was declared in the schema but initially not used: a negative outcome could support recovery, or a positive/context record could support failure.
- Review timestamps initially had no comparison to the case's dated evidence cutoff.
- Source-mode checks initially guarded evidence citations but not inherited event references.
- Latest-case revision preservation initially omitted ordinary explanations, design references and support links, despite keeping the prior journal entries.
- Added document aliases initially lacked the strict identifier validation of shared aliases.

Three initial time-boundary tests pass: offset-equivalent instants/month precision, rejection of definitely future/reversed periods, and conservative deadline comparison without invented deadlines or precise lag for month-only dates. Complete case and negative tests await the final fixture records. These tests are not evidence about facility or supply conditions.
