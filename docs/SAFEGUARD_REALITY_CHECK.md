# Safeguard Reality Check

A written safeguard defines an obligation or right. It does not measure whether people can use it or whether it prevents harm. This small supplied-content mechanism keeps those claims separate, using existing RC-005/RC-006 and Camp records over the unchanged Garden reducer.

Read the [three demonstrations](../reports/safeguards/generated/SAFEGUARDS.md), [Chat handoff](../reports/safeguards/CHAT_HANDOFF.md) and [Digest handoff](../reports/safeguards/DIGEST_HANDOFF.md). The design follows merged PR #38 and Digest's October 8–9 retained observations about written protections versus practical refusal, access, incentives, consequences and remedies. The latest conversation guidance reiterated those distinctions; it is design input, not empirical evidence.

## Claim contract

| Dimension | Supported statuses | What the validator requires |
| --- | --- | --- |
| Formal safeguard | documented, not_in_force, unknown | A non-unknown assessment cites a formal-text record. Law/policy existence is not operational or outcome evidence. |
| Operational people | observed, partial, absent, unknown | A non-unknown assessment cites dated implementation or noncompliance observations about personnel, not merely assigned responsibilities. |
| Operational procedures | observed, partial, absent, unknown | Dated evidence of procedure use or an observed gap; an announced process alone leaves practice unknown. |
| Operational authority | observed, partial, absent, unknown | Dated evidence bearing on usable authority or a gap, rather than only a legal grant. |
| Observed effectiveness | observed, unknown | A cited, dated effectiveness observation names the harm, action, result, scope and whether harm was prevented, stopped or remedied. |
| Failure | documented, reported, unknown | Documented requires observed noncompliance; reported requires an attributed concern/report. Unknown and recommendation status cannot establish failure. |

These dimensions are supplied assessments with explicit scope, source references and limitations. There is no composite score or automatic promotion. A partial operational assessment does not mean people are partly protected. Unknown effectiveness does not mean proven failure. A verified remedy in one scope can coexist with a documented earlier failure; it cannot retroactively satisfy a missed opening inspection.

The [schema](../schemas/safeguard.schema.json) also requires contrary evidence, ordinary explanations, residuals and one proposed next test bounded to one public record. Evidence has a separate class: `formal_text`, `implementation_observation`, `effectiveness_observation`, `noncompliance_observation`, `agency_response`, `recommendation_status`, `reported_concern` or `context`. Every item has its own period, citations with locators, event links and limits. Formal constraints stay labelled formal when presented against a concern. They never become empirical counterevidence merely by appearing in the contrary-evidence list.

An inspection, appointment, replacement contractor, agency assurance, rating or Open recommendation cannot by itself support observed effectiveness. Inspection may document operation and detect failure without proving a remedy. An Open recommendation does not mean no work occurred, and a closed one would not certify every protection. No generic “safe” conclusion is produced.

## Shared history and dated revisions

[The manifest](../operations/safeguards/references.json) imports and pins PR #38's shared reference catalog, adding selectors for existing records only. It cannot shadow an existing alias. The original Camp product-page observation is referenced as a pinned snapshot, with its declared parent source ID and URL checked against the parent. It retains its own observation date and lineage ID while inheriting the same source family for Garden. A recheck of the same GAO page is not independent corroboration.

The [journal](../operations/safeguards/journal.json) contains three case IDs and four assessment entries. The Camp revision adds the already-retained October 12 recommendation-status observation to the June GAO material. It leaves historical failure documented and effectiveness unknown. Both assessment entries were actually assembled on October 14; neither pretends to have been written in June. Event, publication, retrieval, snapshot-observation, evidence-cutoff and assessment-recording dates remain distinct.

Entry sequence, hashes, aware timestamps and per-case expected revisions detect inconsistency and stale writes. Earlier evidence items and contrary assessments must remain unchanged in subsequent snapshots; append a correction or challenge, then explicitly revise the assessment and reason. An assessment may cite that corrective material while the earlier record remains visible. A status revision requires changed evidence or an explicit changed counterassessment. Changed scope requires a new safeguard ID. The evidence cutoff cannot move backward. Day/month precision is retained; only definitely reversed intervals or observations definitely after the cutoff are rejected. Unknown dates are not invented, and empirical observations require a dated bound.

Reference/schema extensions need reviewed changes and new aliases for changed records. Historical Git revisions retain their prior manifests and code. As in Thread of Continuity, hashes are consistency checks, not signatures: wholesale rewriting and resealing requires repository review to detect. Catalog pins do not authenticate the external web or every underlying artifact; the unchanged Camp case retains its separate artifact pins.

## Replay and existing behavior

```bash
python scripts/safeguards.py validate
python scripts/safeguards.py replay
python scripts/safeguards.py check
python scripts/continuity.py check
python examples/garden-case-studies/camp-east-montana/replay.py --check
```

`validate` and `replay` resolve the pinned records, validate every assessment and reconstruct the latest state and revision history. `check` also rebuilds five outputs in memory and compares saved bytes: the safeguard state, readable projection, and three complete Garden passes. After reviewed changes, `build` writes those generated files. No replay uses the current clock, internet or model. The new workflow step uses the existing verification triggers; there is no new schedule.

Each demonstration has ten supplied nodes, one branch, no fanout, zero model calls, inherited sources and a final rest state. Question snapshots are case-local and do not register new Questions or execute the proposed tests. `scripts/safeguards.py` reuses Thread of Continuity's JSON/schema, reference and date helpers. Existing Garden, Continuity and Camp code/data remain unchanged, with their saved output checks exercising that boundary.

Validation checks whether an assessment supplies the required kind of evidence. It cannot decide whether the source actually establishes the assertion, whether a classification is honest, whether practical access is adequate, or whether a single observed case generalizes. Those remain evidence-review judgments. The observed-effect success fixtures in the tests are explicitly synthetic and are never saved as empirical case findings. All three real demonstrations leave observed effectiveness unknown on the bounded retained evidence.

## Stopping point

This is a reusable review mechanism with three demonstrations, not a new research cycle, operational Bee or general military investigation. RC-005/RC-006, the Camp case, canonical RC-004 and the shared Question registry retain their original records. No provider, model, monitoring schedule, Governor power, outbound request or evidence admission is activated. The work stops after the three cases validate/replay and Chat/Digest can inspect them.
