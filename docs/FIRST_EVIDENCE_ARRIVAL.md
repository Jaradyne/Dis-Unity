# First Evidence Arrival — one Camp TB recheck

This combines Chat's arrival-path request and Digest's empirical safeguard test, as Jared approved on October 14, 2026. It reviews merged PRs #38–39 and the Voice handoff in draft [PR #32](https://github.com/Jaradyne/Dis-Unity/pull/32), head `c5df86848f5551917f0373c2cf2b555e179753f4`. PR #32 remains a design contribution; it is not merged or activated by this implementation.

One source, one live request, one reviewed case. No model dispatch, spending, recurring monitoring, Bee or Governor activation. The existing public Question [Q-CEM-TB-CORRECTION](../examples/garden-case-studies/camp-east-montana/follow-up-question.json) remains historically intact; this case-local attempt records the new authorization separately.

## What was observed

At **2026-10-14T17:45:15.166200Z**, the single GET to `https://www.gao.gov/products/gao-26-108886` completed with HTTP 200. The existing `api_records` recorder retained request headers, response headers and all 95,569 received bytes before parsing. [The receipt](../examples/evidence-arrival/camp-east-montana/live/operations/week-one/runs/CEM-FIRST-ARRIVAL/api/0001.json) records zero redaction replacements. Raw-body SHA-256: `99309dd5d28cf2f12ae8a9c762ffaebdabef7f6c792bdc918330b67d2410d945`.

The page displays four Open recommendations, May agency responses and August Army white-paper planning milestones. It contains no dated post-April 18, 2026 verification of TB intake-testing/notification correction. That is an **insufficient-evidence result on this one page**, not a finding that no correction occurred or no public record exists elsewhere. No links, search results or other sources were retrieved. The earlier October 12 page observation was a paraphrase, so it cannot establish byte-level unchangedness against this new receipt.

The official page worked as an anonymous one-shot public HTML read. No product-specific API/feed or publisher automation terms were verified. User authorization for this read and an HTTP 200 do not establish permission for recurring automated access. The source registry records that UNKNOWN explicitly. The capture command is consumed and refuses another attempt, including after an interrupted or failed request. It follows no redirects and makes no fallback requests. A future connector would need a separately reviewed interface/access basis; this task does not create it.

## Small reusable path

1. **Capture:** `evidence_arrival.capture()` uses the existing HTTP recorder with an isolated root, explicit host, 30-second timeout and 2 MB bound. An exclusive attempt file consumes the allowance before network access. The fixed receipt path, run/record identity, source pin and timestamp order bind the result to that attempt. HTTP errors and incomplete reads remain receipts, not empty successful versions.
2. **Stage:** `stage()` pins the saved receipt and writes one observation and pending handoff. Repeating staging is a no-op for evidence work. It never writes an assessment. The existing attempt marker prevents repeating `capture` on this saved case.
3. **Detect:** `replay()` checks the hash chain and files, extracts visible `<main>` text using the standard-library HTML parser, normalizes whitespace and compares text hashes. It does not classify recommendation meaning. GAO's product number/URL are stable identity; raw-byte and text-version hashes are separate. Templates inside `<main>` may cause extra review candidates; a text change is not necessarily a substantive finding. Unrecognized/partial pages become unobservable without erasing the last successful version.
4. **Queue:** new/changed text creates one deterministic handoff, always `awaiting_review`. Exact repeats and matching ETag/304 fixtures create no handoff. Replaying has no network or dispatch side effects. The entire history remains inspectable. Correction/retraction semantics are not guessed; source text is retained for review.
5. **Review:** a separate typed [review record](../examples/evidence-arrival/camp-east-montana/reviewed-revision.json) binds the queued material, independent evidence review, new source snapshot, immutable old journal prefix and exact appended assessment entry. Intake cannot manufacture this record. The independent reviewer and Work integration are attributed; hashes detect inconsistency, not authorship or external truth.
6. **Reassess:** Camp safeguard revision 3 appends recommendation-status evidence and contrary evidence. Historical failure remains documented; effectiveness remains unknown. Continuity's Army–ICE relationship receives an explicit no-change review because this page does not revise the contracting/handoff dates or mechanism. No temporal proximity becomes causation.

The [saved Garden pass](../reports/evidence-arrival/generated/garden.json) carries the handoff, receipt, supplied review and residual through all ten existing nodes, then rests. It references the existing TB Question without registering a duplicate, rewriting the original Camp pass, or invoking the live operation scheduler. The source inherits the same GAO family as its parent: a recheck is not independent corroboration.

## Dates, simulations and review limits

Publication, historical action dates, request start, response finish, HTTP Last-Modified, observation cutoff and actual review time remain separate. Last-Modified is server metadata, not a medical correction date. No update cadence, event date or freshness expiry is invented. October 14's snapshot does not redate May/August actions.

The live ledger contains one real observation. A separate simulation ledger demonstrates first observation, exact repeated 200, conditional 304, a fictional closure without TB results, a contradictory fictional inspection/agency dispute, and an incomplete response. Repeated-body fixtures reference the retained body rather than storing it again. Every synthetic exchange is wrapped and labeled; neither simulation intake nor a raw-form substitute outside the fixed live capture can support the empirical review. None of those changes or requests actually occurred. Conditional-request support by the real GAO server was not tested.

The mechanism is generic at the receipt/identity/change/queue boundary; the current adapter, live allowance and reviewed assessment binding are intentionally restricted to this one product and case. Adding another source or an effectiveness-bearing record requires explicit source/review work, not changing a status flag. Supplied classification still requires source reading; validators cannot decide whether a purported verification is persuasive.

## Reproduce without network

```bash
python scripts/evidence_arrival.py stage
python scripts/evidence_arrival.py check
python scripts/safeguards.py check
python scripts/continuity.py check
python examples/garden-case-studies/camp-east-montana/replay.py --check
```

`stage` reuses the saved receipt. `validate` and `replay` reconstruct the inputs/review/Garden in memory; `build` writes the five projections; `check` compares their exact bytes. None captures again. The existing CI workflow adds only this offline check under its existing triggers. The original Garden and safeguard validators are unchanged.

See the [acceptance record](../reports/evidence-arrival/ACCEPTANCE.md), [Chat handoff](../reports/evidence-arrival/CHAT_HANDOFF.md), [Digest handoff](../reports/evidence-arrival/DIGEST_HANDOFF.md) and [unsent FOIA draft](../reports/evidence-arrival/FOIA_DRAFT.md). Stop here: one bounded test produced UNKNOWN, one reviewed revision is saved, and further collection is inactive.
