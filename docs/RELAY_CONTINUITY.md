# Relay Continuity

Relay Continuity traces a bounded transfer without treating a promise, arrival or action as proof that an essential function worked. The same supplied-content validator and unchanged Garden reducer handle two retained Camp East Montana relays and one explicitly fictional emergency-power exercise. Start with the [readable projection](../reports/relays/generated/RELAYS.md).

## Contract and reuse

| Field | Meaning |
| --- | --- |
| Relay kind | Physical, informational, financial, authority or service; describes the payload, not its success |
| Origin | Trigger or identified need, with its own evidence and occurrence time |
| Expected transfer | Documented requirement, commitment, announcement, inferred expectation or unknown; no automatic operational credit |
| Dispatch | Announced, committed, performed, not performed or unknown |
| Arrival | Acknowledged, received, partial, not received or unknown; acknowledgment never supplies an action/outcome |
| Action | Performed, partial, not performed or unknown, supported by downstream-process evidence |
| Outcome | Continued, recovered, failed, partial or unknown within the stated function, scope and observation window |
| Verification | Source supported, contested or unknown, with a method and the same outcome evidence |

The [typed schema](../schemas/relay-case.schema.json) requires actors/roles, payload, essential function, scope, stage evidence and times, capacities, deadlines, contrary evidence, ordinary explanations, a causal assessment, unknowns and one proposed next test. Unsupported fields/status combinations fail. No domain names or special Camp/diesel branches appear in the shared rules.

[The projector](../scripts/relays.py) reuses Thread of Continuity's strict JSON, finite schema, shared-selector and date helpers; Safeguard Reality Check's inherited references and lineage; and the existing Garden runtime. Local acyclic schema definitions are expanded into the existing finite validator. Standard library only; no network, providers, recurring collector or application model calls.

The [reference manifest](../operations/relays/references.json) pins the existing Safeguard manifest, which already imports Continuity. It adds a selector for the original CEM16 record, the fictional exercise source, raw hashes for the retained GAO PDF and the two design documents. It does not copy or change the RC-005/RC-006 archive. `REL-CEM-ARMY-ICE`, `SG-CEM-INSPECTIONS`, the original Camp pass and `Q-CEM-TB-CORRECTION` remain intact. The earlier relationship establishes contracting context; the safeguard assessment distinguishes requirement from effectiveness; this layer inspects individual transfers.

Diesel Pressure Web contributes its actual-load runtime, refill, maintenance and bridge questions. Carrier Lifeline contributes physical supply, carrier movement, receiving capacity and substitution distinctions. Their files are pinned as design inputs, not sources of empirical incidents or activated specialists.

## Evidence rules

Each evidence item has a class, positive/negative/context result, applicable stages, observation period, source locator, shared event references and limits. A non-unknown stage needs the applicable class and polarity. Required, committed, announced and observed capacity each need their matching evidence class; units and resources remain separate. No generic unit conversion or capacity-to-service inference occurs.

Failures need affirmative negative evidence. An unknown dispatch is not non-transmission. A physical stock shortfall must retain its physical-resource mechanism. A recorded omission can coexist with unknown transmission and receipt when the source does not distinguish mechanisms. A causal assessment requires a positive causal-analysis item; sequence alone cannot support it. Pattern/generalization remains `not_assessed` in this bounded version.

Deadline comparisons require an applicable positive requirement or commitment. Announcements cannot create deadlines. A missing deadline produces no violation or lag. Month/day uncertainty is retained; exact signed lag seconds require exact timezone-aware instants. The comparator can report lateness against a supplied deadline, but does not determine its legal validity or the cause of delay. An observation after the cutoff, a definitely reversed interval or a review recorded before its evidence is rejected. Coarse dates are not made falsely precise.

Positive buffers and alternatives need actual action evidence for `used`, and a verified continued/recovered outcome for `verified`. Capacity alone is insufficient. The initial diesel revision therefore keeps both supports proposed; later fictional transfer, runtime and service observations establish their successful use. Full original residuals remain visible in history after later evidence resolves some of them.

Empirical cases cannot cite fictional sources/events, and simulated cases cannot import empirical events as their observations. Multiple aliases, evidence items, relays or reports from one source family do not add corroboration. Garden CROSS records them as inherited, with an empty independent list. `source_supported` is a supplied judgment about the scoped outcome; it is not a claim of independent inspection or general safety. All fictional records share one authored lineage even when they represent different roles or instruments.

Validation checks declared structure, provenance, evidence classes and consistency. It cannot decide whether a source entails a claim, whether a classification is honest or whether a person was actually protected. Source review remains necessary. Tests can reject an announcement presented as an outcome, but cannot turn an invented or mislabeled assertion into truth.

## Revisions and replay

The [journal](../operations/relays/journal.json) has three attributed entries: Camp revision 1, fictional diesel at 08:20, and fictional diesel at 11:30. All were actually assembled on October 16, 2026; exercise timestamps on October 1 are invented, not historical observations or backdated reviews. This is an as-of fixture demonstration, not a claim that the author lacked access to later fixture inputs.

Entries carry contiguous sequence numbers, expected per-case revisions, timezone-aware nondecreasing recording times, reasons, previous hashes and entry hashes. Relay identity and case scope remain fixed. Later snapshots retain earlier evidence, contrary assessments, explanations, issues and capacity observations as exact prefixes; old support links and shared references remain. Append new observations/corrections, then revise a stage explicitly. A changed stage/deadline/causal assessment needs new evidence or a counterassessment. Historical issues remain historical even if later actions remedy them. Supports and unknowns may change, with their previous states preserved in both journal and human-readable history.

To extend a case, use `make_entry` with its current revision and the last global entry hash. Preserve existing entries and aliases; use new aliases for changed records. Reference/schema extensions require review and updated top-level digests. Git retains the previous snapshots and code. Hashes detect inconsistency against the pins; they are not signatures or protection against rewriting and resealing an entire repository. The external world's current state is not authenticated by a local hash.

From the repository root:

```bash
python scripts/relays.py validate
python scripts/relays.py replay
python scripts/relays.py check
python -m unittest discover -s tests -p 'test_relays.py' -v
```

`validate` and `replay` reconstruct every journal entry. `check` regenerates four outputs in memory and compares their bytes: state JSON, readable Markdown and two saved Garden passes. `build` writes those projections after input review. Replay uses no current clock, internet or inference. Each Garden case has ten supplied nodes, one branch, no fanout, zero model calls and a final rest state. Its Question is local to the demonstration, not a new shared registry entry. The existing CI triggers now check this projection; no schedule was added.

## Acceptance demonstrations and limits

| Case | Established inside its evidence scope | Still unknown |
| --- | --- | --- |
| Camp TB notification | February ODO finding reports lack of notification to ICE about a person with TB symptoms | Actual incident date, notifier, route/receipt, exact deadline, clinical result and later correction |
| Camp vision-panel warning | ICE officials communicated concern in October; panels remained uninstalled at the January suicide. The reported episode also failed required safe observation. | Independent receipt/internal routing, exact installation deadline, panel-specific causation and later verified correction |
| Fictional fuel/essential service | Primary stock was zero despite a working callback. Alternate 80 L arrived at 09:20 against an 08:50 commitment. Generator runtime and service have separate records; battery supplied the 10 kW circuit for 30 minutes using 5 kWh of 12 kWh usable reserve. | Delay cause, eventual primary order and service after 11:30; no real incident or clinical outcome is asserted |

The TB notification finding is separate from the November TB case/December intake-testing discrepancy. The 12-hour testing requirement is not a notification deadline. The 15-minute observation interval is not a panel-installation deadline. Acceptable ratings, detection, contractor responses and agency positions remain visible without being promoted into item-level correction. An Open recommendation neither verifies correction nor proves that no work occurred.

Source accuracy was independently reviewed in [CAMP_SOURCE_REVIEW.md](../reports/relays/CAMP_SOURCE_REVIEW.md); runtime/semantic review is recorded in [IMPLEMENTATION_REVIEW.md](../reports/relays/IMPLEMENTATION_REVIEW.md). These are bounded Work-session reviews, not new operational Bees. See [Chat](../reports/relays/CHAT_HANDOFF.md) and [Digest](../reports/relays/DIGEST_HANDOFF.md) handoffs. The work ends after these two demonstrations and replay checks. Governor, canonical evidence, shared Questions, collectors, providers and the unsent FOIA draft remain unchanged.
