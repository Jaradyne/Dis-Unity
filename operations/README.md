# Working questions and recoverable attempts

**24 September:** [reflection mailbox](reflections/README.md), worker v0.3 reflection projection, and on-demand governor review are implemented. See [the integration record](INTEGRATION_2026-09-24.md). This adds operational learning; it does not open a research cycle or activate providers.

Integrated 23 September 2026 from Chat Aiden's PR #4, head `25cee5fa5184ebdd5e3b66e4018656ed8e9e6e8f`. The original staging packet remains intact under `handoffs/chat_aiden/2026-09-22_api-commons-ticketing_4c2d/`.

This is operational memory, separate from the admitted research in `Resilience_Cascade_STATE.json`. RC-004 remains closed. A runtime change or sensor retrieval is not a new empirical research cycle.

## Available now

- `scripts/questions.py` and `operations/questions.json`: stable questions, explicit geographic relationships, claims, evidence epochs, immutable attempt requests/results, attributed answers and escalation tickets.
- `scripts/worker.py`: writes the exact rendered prompt and provenance before computation, runs a deterministic mock or records a deferred real-provider request, then exports an immutable checkpoint. It checks the shared question before doing work.
- `scripts/scout.py`: one public RSS/Atom retrieval per explicit invocation, with metadata-only parsing, response-size limits, reviewed hosts and no redirect following. Repeated items are deduplicated; retrieval failures preserve the previous successful record.
- `agents/oakland_commons_mapper.json`, `ideas/COMMONS_METABOLISM.md` and `posters/START_WITH_A_TABLE_TRI_FOLD.md`: an available role definition, capability vocabulary and editable brochure copy. No mapper runs just because its definition exists.

The 30 canonical open questions are registered as `Q-RESEARCH-Q01` through `Q-RESEARCH-Q30`, with references to their original records. Their source material remains dated; registration does not refresh evidence or claim a new answer. The additional `Q-OPS-PROVIDER-POLICY` records an unresolved operational choice.

## Coordination rules

**Question:** enduring wording/scope, with a stable ID. Exact case/whitespace-normalized duplicates in the same geography reuse that ID. Semantic equivalence is a Chat/Work judgment; this implementation does not pretend a text hash understands meaning. Different geographic scopes remain separate and can be linked as parent, child, sibling or related.

**Claim:** one cooperating worker can own a bounded lease. An unfinished attempt blocks another attempt even after the lease expires: inspect its saved request and recover it explicitly. Lease expiry is not evidence that a remote request failed. The explicit recovery operation records interruption; it does not retry.

**Attempt:** saved before execution, with exact prompt, role and hash, selected context and hash, base commit, source cutoff, settings and actual provider/model identity. Its request cannot be replaced and its final result cannot be changed into another result. An unselected model remains `unselected`. Policy failures and mock output cannot become research answers.

**Answer:** attributed to Chat, Work, a human or an attempt. Requires summary, evidence references, counterevidence, limitations and readiness status. `ready_for_review` stops duplicate ordinary answering and resolves that epoch's tickets. It is a coordination status, not acceptance into canonical research. A provisional answer leaves the question open.

**Epoch:** explicit reopening records why freshness or scope requires another pass. Old answers, failed attempts and tickets remain visible. A late answer to an older epoch cannot silently close the newer question.

**Ticket:** escalation only. Ordinary questions need no ticket. Repeating the same escalation reason in the same epoch reuses its ticket. Model failures remain attempts, not fabricated answers.

The JSON store is replaced atomically under the existing cross-process repository lock. This serializes cooperating processes in one checkout; it is not a distributed lock across separate computers or GitHub jobs. Separate runners must stage their records as artifacts/PRs for a coordinator to merge, preserving IDs and history. Do not run multiple independent writers against copied registries and silently overwrite one with another.

## Commands

From the repository root:

```bash
python scripts/questions.py status
python scripts/questions.py ask "Can this route deliver before local reserves expire?" --actor chat --geography Oakland
python scripts/worker.py --role agents/worker_bee.json --cycle runtime-check --question Q-RESEARCH-Q01 --provider mock
python scripts/scout.py --source eia-diesel
python scripts/scout.py --source eia-energy
```

`runtime-check` labels a runtime exercise; it does not create a research cycle. Mock output leaves the real research question open. The default checkpoint location is `operations/checkpoints/<attempt-id>.json`, never a closed cycle's inbox.

Chat can return a proposed answer file in its staging directory:

```json
{
  "summary": "The bounded answer, including what remains unknown.",
  "status": "ready_for_review",
  "evidence_refs": ["Public URL or exact repository source/record reference"],
  "counterevidence": [],
  "limitations": ["State source cutoff, access and coverage limits."]
}
```

Work admits it to the coordination queue with the **epoch read when the work began**:

```bash
python scripts/questions.py answer Q-RESEARCH-Q01 --actor chat --epoch 1 --file handoffs/chat_aiden/YOUR_PACKET/answer.json
python scripts/questions.py reopen Q-RESEARCH-Q01 --actor work --reason "New release makes the old answer stale"
python scripts/questions.py recover Q-RESEARCH-Q01 --actor work --attempt ATT-EXISTING-ID --reason "Inspected unfinished local attempt; its execution is no longer running"
```

These examples do not confer evidence review or account authorization. Chat continues to stage proposals rather than edit the shared registry on main. Only public/authorized material belongs in prompts; never add credentials or private account records. Prompt retention is durable only after the changed records are published or exported. A transient checkout is not a backup.

## Real-provider policy

`config/providers.json` records the current effective pause and the pending change. The user's earlier direct instruction required best-eligible Gemini or deferral. PR #4 says the user later approved evaluated role-fit free backups. The user has asked Work to make progress without another decision tonight. Preserve both directions; build the provider-neutral parts and leave the conflict nonblocking.

Groq is excluded, including hidden aggregator routing. No provider or quota listed in the proposal is automatically verified or eligible. No real-provider network call is possible through worker v0.2; passing `--provider gemini` saves the request and a `policy_blocked` result. It does not read a key, downgrade, retry or call another provider. The Actions workflow now exports recovery records even when a run fails and has no model secret attached.

## What is still proposed

The provider attempt ring, per-provider backoff/reset registry, free-model evaluations, learned quiet-window governor, recursive specialist orchestration, mail/Discord ingestion and Vercel portal remain designs. No schedules, heartbeat tracking, paid resources or outreach are enabled. The browser/Chat tools available to Aiden are not automatically tools available to Python workers.

Chat's packet contains a Havana outreach lead; it needs a verified recipient and reviewable draft before any authorized sending. The brochure's editable copy is preserved; the generated visual is not present in this Git packet. The communications platforms are replaceable interfaces, not the project's only memory.

Next useful implementation: reviewed provider eligibility and one adapter, then a bounded attempt ring with persisted cooldowns and a tested stop condition. Chat can prepare those interfaces and current official model evidence; Work integrates. Keep runtime growth separate from evidence admission.
