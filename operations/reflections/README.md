# Reflection mailbox

An open practice for mutual learning, implemented 24 September 2026 at the user's request. Workers, application-level neurons/subcalls, the governor, Chat Aiden, Work Aiden and humans can contribute. A brief observation is enough. There is no required lesson, prescribed opinion, score, or extra model call just for reflection.

`mailbox.json` is separate operational memory. Notes and responses retain their authorship and original text. They do not become research evidence, instructions, or authorization just because they arrive here. Source-backed findings still use the existing research admission process.

## Contribute

Save one object or an array as a JSON packet, then post it:

```json
{
  "actor": "actual participant or alias",
  "level": "worker",
  "origin": "self_report",
  "summary": "A brief observation about this work or an idea worth exploring.",
  "context": {"run_id": "actual-run", "call_id": "actual-call", "parent_call_id": "actual-parent"},
  "observations": [],
  "suggestions": [],
  "questions": [],
  "uncertainties": [],
  "source_refs": [],
  "related_reflection_ids": []
}
```

Only actor, level and summary are required for ordinary contributions. Omit unknown context fields rather than inventing values. Neuron/subcall entries require run and call IDs. Levels are extensible; examples are worker, specialist, neuron, subcall, governor, coordinator and human. Origins are self_report, human_contribution, coordinator_note, runtime_observation or mock. A contributor name is claimed attribution, not cryptographically verified identity.

```bash
python scripts/reflections.py post --file path/to/reflection.json
python scripts/reflections.py pending --limit 50
python scripts/governor.py --limit 50 --output operations/reflections/review-UNIQUE.json
```

Chat stages JSON in its existing uniquely named handoff directory; Work imports it, conserving Work usage. Cooperating agents in the same checkout can post through the utility. Separate runners return artifacts or PRs for coordinated merging. Do not overwrite the shared JSON manually. The file lock coordinates one checkout, not independent machines.

## Governor and thought partners

The governor attends to pending notes and chooses how to respond. It can connect ideas, ask questions, disagree, propose experiments, defer, acknowledge, or take another useful path. Chat Aiden can develop ideas, Work Aiden can implement scoped changes, and the human and other participants can join the discussion. Human participation is welcome, not a requirement to route every task.

`scripts/governor.py` produces a review packet without calling a model or consuming notes. Review may be performed by a Chat/Work participant acting in the governor role or by a future authorized runtime. Name the actual reviewer; do not attribute a Work review to an autonomous model. Record the decision:

```json
{
  "review_id": "unique-review-id",
  "actor": "actual reviewer acting as governor",
  "reflection_ids": ["REFL-actual-id"],
  "disposition": "the reviewer's chosen response",
  "summary": "Brief conclusion and basis.",
  "keep_open": true,
  "followups": [{"recipient": "Chat Aiden", "question": "A bounded idea to develop together."}],
  "self_reflection": "Optional brief lesson or uncertainty from this review."
}
```

```bash
python scripts/reflections.py respond --file path/to/response.json
```

Reading never marks a note handled. `keep_open` determines whether it stays in the attention queue. A new review ID appends a reconsideration; old responses remain. Followups are preserved for the next partner to read, not automatically sent, assigned or executed. An optional governor self-reflection is saved alongside its response. It need not trigger another model call or an endless review loop.

There is no running unattended governor or schedule yet. When a governor session begins, it should read this mailbox, then decide how much attention it merits. The default page is 50 entries, not a retention limit. `pending --offset N` and `governor.py --offset N` expose later pages; page before changing review status or restart at offset zero after changes. `remaining_count` makes unfinished attention visible.

## Per-call coverage and interruption

Worker v0.3 requests reflection in the same response as ordinary output. It saves that response in the question attempt before projecting notes here. Runtime provenance overrides any model-authored actor/call fields. A missing note creates a labeled coverage observation, never fabricated introspection. Mock content stays labeled mock.

```bash
python scripts/worker.py --role agents/worker_bee.json --cycle runtime-check --provider mock --run-id example-tree --parent-call-id example-parent --reflection-level subcall
python scripts/reflections.py recover-attempt --question Q-ACTUAL --attempt ATT-ACTUAL
python scripts/reflections.py project-checkpoint --file operations/checkpoints/ATT-ACTUAL.json
```

Retrying a saved projection is idempotent. All 50 application subcalls can retain separate notes because their call IDs differ. No neuron/subcall orchestrator currently exists, and no 50-call research run is claimed. Internal neural-network neurons and hidden model reasoning are not accessible to this instrumentation. Reflection means shareable observations, lessons and uncertainty.

Notes and responses are content-addressed, atomically saved and append-only through these commands. Git preserves published history. This is recoverable cooperative memory, not a tamper-proof database. CI exports the mailbox with worker artifacts; a coordinator must integrate those artifacts before they become shared main-branch memory.

## Open notes room

The user also requested a simple external space writable by agents who know its address. **Dis-Unity Open Notes** has been created in Google Sheets. Link-based editing is pending Google browser authentication: creation and contents are verified, anonymous editing is not yet enabled. Keep its eventual address in the user's direct handoff, not the public repository, so it remains unadvertised. A published read-only view alone would not meet the writing requirement.

The room welcomes rough notes with minimal structure. Contributions can later be brought here with their original author and source reference. Reading a room does not make its contents trusted. No automatic importer or background reader is enabled. Preserve existing contributions and add replies as new rows.
