# Garden operation spine

This is the bounded implementation of [PR #28's primary request](../handoffs/chat_aiden/2026-09-29_nervous-system-work-request/WORK_AIDEN_PRIMARY.md). `garden_runtime.py` remains a deterministic event reducer. `garden_operations.py` supplies the separate request, selection, execution, recording and return interface. A worker cannot submit traversal commands or change reviewed configuration.

## Request and return

Start a linked run with `operations: true`. The request names an existing Question/epoch, branch, reason, exact task, role, method, permissions, budget and stop condition. Preparation binds it to the current tree/node/visit/arrival and parent-output hash. It retains the exposed source catalog, Question history and attempts, supplied context, output schema, blinding conditions and return path. The original Garden example remains unchanged.

All ten nodes may initiate work. A pending operation holds its branch at the exact node until a validated, UNKNOWN, deferred or error return arrives. Other branches may continue. A return attaches attributed material; it cannot add an independent source or mark an answer admitted. CROSS still checks underlying source lineage, including clones and inherited material. Changing models does not provide empirical independence.

Supported methods:

| Method | Executor | Current boundary |
| --- | --- | --- |
| `lineage_inventory` | Deterministic local code | Inventories exposed references; does not interpret their empirical content |
| `cognition` | Approved OpenRouter/Nvidia route | One bounded structured completion; existing fixed adapter, catalog checks and receipt audit |
| `public_source` | Public Collector | One GET of a named reviewed source; no redirects, arbitrary URLs or automatic evidence admission |

Candidate lists are saved before selection. They include current tree/node and requested role, prior executor history, publication-language metadata, stated fitness limits, lineage constraints, permissions, remaining run capacity and shared provider gates. Tree-role and language fit order otherwise eligible candidates deterministically. There is no learned fitness score or claim that an unbenchmarked model is a domain expert. Gemini, Mistral and Cloudflare are labelled first-use approval required; no live adapter for those routes is enabled.

## Budgets and recovery

`config/garden-operations.json` caps a linked run at eight operations, two child births, depth one, one model POST reservation and two public source GET reservations. Each child inherits one source operation and zero model calls. Traversal branch/step/event limits also apply; accepted work reserves enough event slots for its returns. Requests can narrow permissions and per-operation budgets. They cannot raise the reviewed ceilings.

Garden model reservations share Week One's UTC daily/half-day limits, window and spend brakes. **There is no generic provider cooldown.** Only genuine external waiting states—saved-generation audit delay, rate/quota pressure, transient provider capacity, or transport timeout—may create a timed bandwidth wait. Local schema/validator failures, an unavailable pinned model, first-use questions and policy/review conditions remain visible for rerouting or peer/operator attention without idling unrelated work. A pending or uncertain Garden model attempt still blocks a replacement POST for that same uncertain generation. Positive cost closes the shared window. First or peculiar provider paths defer to Jared; no Groq upstream or paid fallback is permitted. This integration does not extend the October 4, 00:45:13 Pacific cutoff.

Requests and reservations are durably saved before transport. The full recorder checkpoints HTTP material before parsing; outcomes and stable event IDs make a partially saved return repairable. An interrupted POST is never repeated. A saved generation may be recovered by GET only. With no generation, the uncertainty and shared brake remain for review. `audit_pending` has at most three total audit attempts, respects cooldowns and preserves the original return while appending audit material. Recovery is explicit, not an unattended retry loop.

## Child work

A valid birth carries the narrow question, why the parent cannot answer, registered target tree, role, named source need, budget and stop condition. The orchestrator derives the return location, parent/arrival/source lineage and depth. Duplicate, branch, child, depth and event limits prevent expansion. A child may fetch one reviewed public surface, then return to its original parent visit even if the parent has moved. The parent does not wait indefinitely for an unavailable executor.

Unregistered trees, unavailable sources, first-use providers and unresolved results remain available to **Chat Aiden and Digest Aiden** in the shared unresolved queue. Each unresolved operation also gets a small **Bee handoff** packet describing what was attempted, what blocked it, required capabilities, current candidate states, lineage and the exact return path. These are records for those participants, not a claim that either has read them. v1's executable child is a Collector; model-backed specialists remain deferred preparation.

## Capacity weather and Luna Mode

`digestion/threshold/garden-operations/capacity.json` projects current routing weather. **Luna Mode** means no approved model lane is locally eligible at that moment. It is not a weaker model and it is not a global stop. Deterministic work and public Collectors may continue within their budgets; unresolved cognition is routed to Chat Aiden and Digest Aiden for research, repair, digestion or preparation while provider capacity/approval changes. The projection does not wake either conversation automatically.

When an approved model lane becomes locally eligible again, the projection returns to `normal`. Remote availability is still checked at execution. Later provider adapters may let a task move among approved contextual executors rather than waiting on one provider, while preserving first-use approval and exact lineage.

## Run from reviewed main

The **Garden bounded operation** GitHub workflow loads `week-one-state`, executes code/configuration from main, and saves only operational data. It uses the same serialization group as Week One. Its first merge/push runs the fixed Q18 acceptance. Repeated default runs replay the completed record without another inference or source GET.

For another reviewed operation, add a JSON packet directly under `operations/garden/requests/` containing `run_id`, optional `start`, optional Garden `commands`, and an `operation` specification. Use **Run workflow** on main with `request_path` set to that repository path. The local equivalent, after loading live state into an isolated authorized checkout, is:

```bash
python scripts/garden_operations.py run --file operations/garden/requests/your-reviewed-packet.json
```

For an interrupted or audit-pending operation, leave `request_path` empty and set `recover_operation` to its saved ID. Inspect the latest outcome and cooldown first. Recovery accepts an existing executing/returned operation and never starts a new inference. Do not delete a record, reuse an ID for changed input, or clear a brake to force progress. A materially changed request needs a linked new ID within remaining limits.

Chat may initiate already-approved workflows where its tools expose that capability. Otherwise the GitHub Actions UI is the available mechanism; a suggested click is not proof of execution. Read [Chat's main-edit permission and reversal protocol](CHAT_MAIN_EDIT_PROTOCOL.md) before publishing a new request or runtime change.

## Materials and Q18 proof

All live data is on `week-one-state`:

- `operations/garden/runs/Q18-NERVOUS-SYSTEM-20260929.json`: linked real Question run, events and replay hashes.
- `operations/garden/operations/`: exact requests, candidate sets, rendered prompts, structured returns and birth decisions.
- `digestion/threshold/garden-operations/operations.csv`: formula-safe operation ledger.
- `digestion/threshold/garden-operations/unresolved.json`: shared Chat/Digest queue, including the current capacity mode and per-operation handoff references.
- `digestion/threshold/garden-operations/handoffs/`: resumable Bee handoff packets for unresolved/deferred/error/UNKNOWN work.
- `digestion/threshold/garden-operations/capacity.json`: normal/Luna routing projection and any genuine bandwidth wait.
- `digestion/threshold/garden-operations/Q18-acceptance.json`: actual calls, receipt if available, result and supplied/automatic boundaries.
- `digestion/threshold/garden/branches.csv`: current traversal branches.
- `digestion/threshold/api/`: full HTTP ledger and material hashes. Deterministic/deferred operations are explicitly `no_http_exchange`, not historical missing data.

The acceptance uses Q18's existing staged electric-vessel lineage, asks for one ordinary control and operating-evidence test, returns to MIRROR, preserves inherited/independent/bridge distinctions at CROSS, and births one Production Collector around a real freight-service gap. The task framing, node interpretations and conservative continuation policy are supplied by reviewed code. Worker selection/execution/validation/return, the child operation, recording and replay are automatic. Model output is not a freight-service measurement. UNKNOWN is a legitimate empirical result.
