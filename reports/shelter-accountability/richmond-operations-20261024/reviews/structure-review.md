# Richmond integration: independent structure review

Reviewer: `richmond_structure_review`, an actual Work-session collaboration agent. Base inspected: `f243e11686de5597610a22ee86eef1674bf8da9b`. This is an architecture review of repository contracts, not an independent factual investigation of Richmond. The host does not expose the served model or a per-agent cost receipt. Initial checkpoint is retained in RC-010.

The user's framing is: **why can't communities help themselves when the capacity is right there?** The current lead is that replacement operators' asking prices block the Richmond village. Keep that as an attributed lead until priced proposals and current decision records establish it. The tree should trace community-created capacity → permissions and operating obligations → finance and staffing → usable shelter, with each gate's controller and evidence status visible. Do not define community stewardship as inherently deficient or treat a formal requirement as demonstrated protection.

## Smallest safe implementation

| Surface | Concrete implementation | Boundary |
| --- | --- | --- |
| Bee | Reusable role plus the actual bounded Work-session task, exact dispatch prompt, checkpoints and attributed return | A role definition is not a run; changing agent or model is not independent evidence |
| Garden tree | Separate, reviewed extension containing one new tree; bounded case runner composes it with the existing validated traversal config | Preserve the base config and earlier case pins; this tree is available through the new runner, not automatically through the unmodified global dispatcher |
| Question | Stable Richmond Question/epoch, linked to the community-capacity framing; case-local snapshot for reproducibility and separately registered operational record on current `week-one-state` if integration is completed | A case-local dictionary does not establish shared registration; pending or provisional results remain open |
| Assessment | Shared source/event references and append-only dated reviewed entries; deterministic ten-node Garden pass ending at RETURN | No automatic canonical admission, causation, motive, verified failure, successful protection or source independence |
| Meaning Tower | New loadable packet under the existing official-notice-and-summary contract; optional separate portable HTML built by the existing builder | Keep the Translation Boss Question and its actual epoch; the Richmond Question is linked in context/narrative, not substituted into the fixed player contract |
| Governor | An advisory `governor-digestion-feed-0.1` envelope and explanatory handoff; ingest into current operational mailbox | Source presence is `awaiting_projection`; successful ingest is `pending`; neither is a Governor response, play, approval or power |

## Garden constraints checked in code

`scripts/garden_runtime.py:load_config` validates the shared config's zero model budget, complete node contracts, INIT node templates, tree identifiers and routing rules. `new_document` embeds a complete config snapshot and Question epoch; `replay` reconstructs against that snapshot. Old saved documents therefore remain reproducible without changing their config. Existing Campus and shelter runners also hash-pin the shared config, so a global edit would fail their current checks even when their saved replay still reconstructs.

A minimal extension loader should start with `garden_runtime.load_config(root)`, copy the result, and admit only the explicitly reviewed new tree. Reject duplicate tree IDs, an unsupported node template, unknown or overridden config fields, and base-pin mismatch. Preserve `limits`, `node_contracts`, `rules`, `grammar` and `model_execution` exactly. Pin extension bytes and the base config in the new case. Adding a new tree does not require adding a routing rule when the saved pass starts directly in that tree.

The unmodified `garden_runtime.start()` reads only `config/garden-traversal.json`. Do not claim the extension is a globally dispatchable route. A new case runner can call `new_document` with the composed config, replay the saved document, and later place that complete supplied pass in the operational run folder. `garden_runtime.project()` can replay such a document from its embedded config without loading an external extension. Actual continuation through `submit()` still checks the current shared Question epoch.

The source catalog must preserve `ref`, `lineage_id` and `kind`. A user's report can be a labelled context source, not a public-source corroboration. CROSS rejects inherited source lineage offered as independent evidence; using a different article URL does not establish a new underlying observation. MIRROR should preserve practical alternatives and the possibility that some mandatory services protect residents, while leaving their staffing and effectiveness separately assessed.

## Meaning Tower constraints checked in code

`scripts/meaning_boss.py:validate_packet` strictly requires:

- `meaning-tower-boss-packet-1`, `THE-UNRESOLVED`, `packet_status: evidence_backed`, `Q-MEANING-TRANSLATION-BOSS` and the registry's actual current epoch.
- Two or three distinct named public HTTPS URLs, separate source publication/observation/retrieval dates, and explicit limitations when a date is unknown.
- `comparison.kind: official_notice_and_summary`, at least one ordinary explanation and limitation, and an inherited source reference. The sources must actually support the described comparison; the validator does not verify that.
- One to four rounds, including a control; one to three originals and two to four labelled pieces per round. Question and unknown pieces can carry the unresolved price barrier; a source-statement piece must have an inspected source that supports it.
- Unique IDs throughout, bounded text, and no added top-level fields. Cross-link the Richmond Question in existing narrative/context strings and the handoff. Use a new packet ID if wording changes.

Use a public grant/lease notice with its public summary only to the extent they concern the same arrangement. Distinguish that historical comparison from the unresolved current replacement-operator demand. Do not label two unmatched financial instruments as a notice and its summary to fit the player.

The packet can be loaded by the existing portable player. A distinct HTML build is optional; if produced, use `build_meaning_tower.py --packet ... --output ...` and leave the old default encounter unchanged. Tests of loading, output or deterministic choices are rehearsals, not a play by Jared. Do not create a completed-play Governor envelope unless an actual attributed completed play exists. No power candidate is needed.

## Governor constraints checked in code

`scripts/governor_inbox.py` already accepts advisory digestion without a play. Required fields include the schema/kind, digest ID, aware timestamp, actor with `authority: advisory_noncanonical`, `intended_reviewer: repo Governor`, `digestion.core_shape`, and all four boundary flags explicitly false: evidence status changed, power awarded, canonical state changed, implementation authorized.

Up to three context documents are allowed, each Markdown under `handoffs/` and at most 24,000 bytes. A report path elsewhere is not a valid `context_refs` path. The whole inbox envelope is capped at 40,000 bytes. The handoff should identify the actual research return and saved pass, the user's community-capacity question, what is established, the unresolved current quote/authority question, and a narrowly bounded next test.

Reviewable inbox sources belong on main. `ingest()` posts content-addressed reflections and writes queue projections to operational state; repeat ingestion reuses the reflection rather than manufacturing another review. `snapshot()` reports `awaiting_projection` before import and `pending` after import. Only an attributed response naming the reflection can establish a reviewed status. Preserve any existing mailbox entries and decisions when working from fresh `week-one-state`; do not overwrite them with the older main snapshot.

## Acceptance checks for the finished packet

1. Replay the new pass twice from retained inputs and require byte-identical outputs, one resting branch and zero model calls. Change a pinned source or extension and require rejection.
2. Verify the original shared config, earlier Garden cases, canonical state and RC-005/006 records are unchanged. Run the existing affected replay commands; do not regenerate historical pins to silence a failure.
3. Reject tree-ID replacement, modified base rules/limits and a false independent-source promotion. Keep extension registration distinct from global runtime availability.
4. Preserve every assessment revision and its predecessor hash or shared append-only history invariant. A later review cannot replace the original user-reported barrier with a newly asserted fact.
5. Costs retain instrument/date/period/status and scope. A quoted all-in operating price is neither manager salary nor payment/profit; construction cost is not annual operating cost. Unknown denominators prevent an asserted per-occupied-bed price.
6. A historical operator appointment, announcement, opening celebration or website label cannot be the sole basis for current operation. A missing replacement agreement is not proof that none exists. Preserve genuinely contrary evidence and its dates.
7. Validate the Meaning packet using the existing Python contract and existing JavaScript loader tests. A test result must be labelled a fixture or rehearsal, never human play.
8. Validate the Governor envelope, ingest it twice against a temporary copy of current live state, and check one stable reflection ID, pending status and zero new decisions. Publication to the real state branch is a separate coordinator action.
9. Keep possible community-run, shared-service or reduced-cost alternatives labelled proposals until authority, willing people, capacity, funding and protections are verified. Preserve buffers and successful access if evidence establishes them.

This review authorizes no implementation or external action. It records the smallest compatible path and its evidence limits. Finished-packet review remains pending.
