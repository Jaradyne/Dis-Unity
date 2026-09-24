# Week One Meaning Web — Work → Chat Aiden

Owner: Jared. Integration: Work Aiden. Thought partners: Chat Aiden, Governor, workers and voluntary human contributors.

## Run window and entry points

Configured window: **24 September 2026 07:45:13 UTC through 01 October 2026 07:45:13 UTC**. GitHub Actions wakes at **03:47 and 15:47 UTC** (20:47 previous day and 08:47 Pacific during this week). GitHub scheduling may be delayed. The time gate rejects new work after the window; the next wake writes a digest and disables this workflow.

- [Live output index](https://github.com/Jaradyne/Dis-Unity/blob/week-one-state/operations/week-one/INDEX.md)
- [Actual runs](https://github.com/Jaradyne/Dis-Unity/actions/workflows/week-one.yml)
- [Durable run manifest](https://github.com/Jaradyne/Dis-Unity/blob/week-one-state/operations/week-one/run-manifest.json)
- [Shared Questions](https://github.com/Jaradyne/Dis-Unity/blob/week-one-state/operations/questions.json)
- [Reflection mailbox and Governor decisions](https://github.com/Jaradyne/Dis-Unity/blob/week-one-state/operations/reflections/mailbox.json)

**Verified launch:** [run 35971438628](https://github.com/Jaradyne/Dis-Unity/actions/runs/35971438628) completed on 24 September at 07:46 UTC. All three public sources were retrieved, yielding six selected records. Prompt, attempt and runtime reflections were committed to `week-one-state`. The workflow is active. PRs #5 and #6 are merged with ancestry preserved. CI and worker smoke checks passed. The new local integrity total is 42 tests, plus a real Git stale-write exercise.

**Current provider state:** OpenRouter's BYOK management preflight returned HTTP 401. Zero inference POSTs were sent. An explicit provider brake is preserved; the API Answer Bee has not passed a live role trial. Public sensing continues. A normal inference key may lack management access, so do not label this key invalid on that evidence alone. Chat can help investigate the account-scope verification requirement through already authorized read-only settings; Work reviews an appropriate fix. Broader credentials are not a prerequisite for keeping Week One useful.

**Chat Governor:** a separate enabled ChatGPT task performs one bounded review/research session each evening for seven occurrences, using the existing ChatGPT session and public search/GitHub tools. It stages one Question-linked finding, a sample, source ledger, reflection and Governor response under `main:handoffs/week_one_governor/YYYY-MM-DD.{json,md}`. The exact staging prefix is authorized for that task; it cannot edit runtime, policy, canonical research or `week-one-state`. The hosted runner imports only its shareable reflection/response into the common mailbox at the next wake. Check actual dated files before claiming a session completed. Its requested immediate first run is recorded separately in the launch verification note.

[First Work research briefing](reports/week-one/2026-09-24_FIRST_REVIEW.md) follows the first feed lead through the current EIA table. It is an attributed Work review, separate from task/API outputs.

## What runs

Current active roles: public scouts, deterministic runtime caretaker/reflection logging, and the scheduled Chat Governor thought partner. The API Answer Bee is installed and awaiting the preflight access resolution above.

A serialized, bounded workflow reads three official public surfaces: EIA diesel RSS, EIA Today in Energy RSS, and NWS California active alerts. It retains access errors, event/publication/retrieval distinctions, source hashes and selected excerpts/metadata. An unchanged item retains its identity. Initial discoveries are separate from newly occurring events. A failed feed is a coverage gap.

One Answer Bee uses the selected shared Question, those sources, previous summaries, root culture and a rotating portion of the reflection mailbox. Its Governor lens responds to reflections and proposes followups. This is one inference with two attributed roles, not independent peer review. Every source run leaves a runtime reflection even when inference is unavailable.

Question rotation: `Q-RESEARCH-Q01` (fuel costs and essential delivery), `Q-RESEARCH-Q17` (food assistance cover), `Q-RESEARCH-Q09` (water/care), `Q-RESEARCH-Q21` (usable logistics routes). Each answer remains provisional and keeps its Question open. The output contract asks for a conditional link, buffers, shedding, substitution, growth, lifeboats, outside reserve, commons and a concrete caretaker tomorrow-test. Sources alone may not resolve the Question; that is a useful limitation to retain.

`ROOT_MEANING_AND_DESIGN_PRINCIPLES.md` and `CULTURE.md` preserve care, meaning, dignity, reciprocal interdependence and repairability. Attempts record the exact culture hash. Original reflections are preserved; Governor responses append. Model/source text has no execution authority.

## Provider and spending boundary

PR #5's later role-fit free-model policy is admitted to `Q-OPS-PROVIDER-POLICY`, epoch 1. The reviewed adapter requests exactly `nvidia/nemotron-3-super-120b-a12b:free` through OpenRouter with Nvidia as the sole serving provider, zero price ceilings and fallbacks disabled. Groq is excluded. The model must pass a bounded role trial before anyone treats its output as trusted research.

Before POST, the adapter requires a live model-specific zero-price endpoint and a read-only check that no applicable Nvidia BYOK key is active. OpenRouter documents that BYOK can take priority; a normal inference key may lack access to this management metadata. That condition records an access/configuration result before inference. The read only retains a yes/no preflight result; credential labels, values and IDs are not stored. After generation, audit must bind the exact generation ID to the served model, Nvidia, no BYOK and zero cost. A missing receipt retains the visible generation for audit recovery.

Only the execute step receives `OPENROUTER_API_KEY` from Actions secrets. No value is extracted. At most one inference POST per run, four conservative POST reservations per UTC day, two runs per half-day slot, three audit tries for a saved generation. Failed quota/capacity calls cool down; policy/authentication failures brake inference while public sensing continues. The generic worker remains mock/deferred Gemini. New provider selection is reviewed Work integration.

Standard public-repository `ubuntu-latest` Actions performs the bounded work. Outputs are ordinary Git text records, with no artifact upload or added paid infrastructure.

## Where outputs land

Runtime/configuration are on **main**. Autonomous operational data is on **week-one-state**. Load only the data allowlist from that branch; always execute reviewed code from main.

For each `gh-RUNID-ATTEMPT`:

- `operations/week-one/runs/…/sources.json`: selected observations, source identities, access results.
- `request.json`: full public prompt, Question/epoch, actual requested route, base commit, culture hash, reflection references.
- `provider-response.json`: visible completion and generation identity, when returned.
- `outcome.json`: classified attempt, audited receipt and validated structured answer when available.
- `HUMAN_NOTE.md`: readable briefing and coverage limitations.
- `samples-for-jared.json`: one small meaningful example when an answer passes the output contract.

The run manifest links shared attempt/answer/reflection/decision IDs. Prompts are committed before execution; returned visible generations are committed before audit. Final outputs: `WEEK_ONE_DIGEST.md`, `CHAT_INDEX.md`, `PROVIDER_NOTES.json`, `REFLECTION_THEMES.json`. The last file is an attributed mailbox collection for synthesis, not invented themes.

## Restart and recovery

1. Read the latest manifest on `week-one-state`, the last workflow run, and its failed job/step. Read any saved provider response/outcome before attempting inference again.
2. For an interrupted infrastructure job, GitHub **Re-run failed jobs** (or **Run workflow** on main) is sufficient. It starts a new execution identity. The serialized runner finishes saved outcomes idempotently; unfinished attempts are marked interrupted and linked recovery attempts retain their original prompt. A saved generation is audited with GET, without another inference POST.
3. Successful half-day slots are idempotent. Two attempts per slot and daily budgets limit retries. Cooldowns survive restarts. Never delete history to bypass them.
4. `audit_pending` means verify the existing generation. `auth_or_configuration_error`, `policy_blocked`, an active `brake`, or conflicting provenance means inspect and repair the concrete cause before resuming inference. Chat may stage a fix; Work reviews/integrates. A restart does not override that boundary.
5. A state-branch change since the initial load or last save fails before publication; a later push conflict also fails rather than overwriting concurrent work. Keep Chat contributions in uniquely named staging files on a separate branch/PR. The workflow is the sole operational-branch writer during a run. The scheduled Chat task writes only its separate staging prefix on main, which cannot trigger inference or change runtime authority. Do not edit Questions/mailbox concurrently there.
6. To stop: disable **Week One Meaning Web** in Actions and set `config/week-one.json` `enabled` to false through reviewed Git. Disabling the config also blocks an already prepared provider step. The seven-day end gate is enforced independently.
7. To extend past the configured end, get a newly authorized window and update reviewed configuration; do not reset the clock by re-running a job.

Operator reproduction from a clean authorized checkout:

```bash
git fetch origin main week-one-state
git switch main
git pull --ff-only
python scripts/week_one_state.py load
```

Use Actions for the live credentialed execution. Local `python scripts/week_one.py prepare --run-id local-check` performs real public reads and local journaling; it does not publish or call the model. Local execute requires the same reviewed gates. Keep local experiments on an isolated checkout; do not overwrite live data with them.

## What Chat Aiden can do now

Read real outputs and use the existing Question IDs/epochs. Stage a small, evidenced response to the most consequential unanswered tomorrow-test. Seek actual operating reserves: cash available now, staffing, delivery cadence, fuel/food cover, access and a backup actor. A named program is not proof of deliverable capacity.

The latest Meaning Tower selections are preserved in `operations/week-one/meaning-tower-attention.json` and connected to `Q-MEANING-TRANSLATION-BOSS`. Begin with one matched official document pair, independently observe both originals, compare stability/concern/responsibility/cooperation, and retain one ordinary translation control. English is Jared's human pivot. The imagined 38/35/3 packet is a teaching scenario, not an observed sample count. Bring a surviving nuance as a playable sample, with the source and relevant material dependency.

Preserved PR #6 proposals remain available for focused growth: Carrier Lifeline/backhaul, multilingual Bee, Regional AI Lab, Voice Garden and broader Meaning Tower. The operational launch uses the carrier/caretaker questions and sample contract; expand when a concrete question justifies it. Preserve root mission and reflection at every scale.

The private-address open notes room remains separate. Its address must stay out of this public repository. Email proposals remain drafts unless Jared explicitly authorizes sending.


## Governor task recovery

The task is named **Week One Governor** in ChatGPT Tasks. It has seven scheduled evening occurrences (24–30 September Pacific), plus an explicitly requested immediate launch review. If a task invocation cannot publish, its response must retain the complete small packet. Chat can stage that exact packet with provenance for Work, rather than ask Jared to reconstruct it. Re-run only an incomplete session after reading its dated packet; an existing UTC-date packet makes that day's task idempotent. The import log is `week-one-state:operations/week-one/thought-partner-imports.json`.

Stop the task as well as the GitHub workflow if ending early. A task after the configured end reviews closure without starting new research. No further recurring watch is authorized by this launch.
