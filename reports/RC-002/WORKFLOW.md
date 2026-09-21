# Checkpointed research-cycle workflow

This utility records active-session agent research. It does not start AI agents, browse, contact people or monitor between sessions.

## Ordinary cycle

Run from the repository root. The coordinator performs these operations; the user does not need to maintain the records.

```bash
python scripts/cycle.py begin RC-003 --cutoff YYYY-MM-DD
python scripts/cycle.py submit RC-003 --agent fuel --file inbox/RC-003/fuel.json --phase checkpoint
python scripts/cycle.py status RC-003
```

Each submission receives a content hash and an immutable snapshot. New checkpoints preserve earlier ones. The agent/cycle declaration is checked to prevent accidental cross-cycle admission.

Prepare a complete candidate JSON using the baseline and reviewed findings. It must retain all ten state sections, matching cycle/cutoff metadata and resolvable evidence references. Record a named review of that exact candidate:

```bash
python scripts/cycle.py review RC-003 --candidate cycles/RC-003/candidate.json --reviewer coordinator --role coordinator --decision accepted_with_limitations --note "Checked admitted changes and counterevidence." --limitation "State the remaining material limitation."
python scripts/cycle.py commit RC-003 --candidate cycles/RC-003/candidate.json
python scripts/render_state.py Resilience_Cascade_STATE.json
```

Use `--role independent --decision passed` only when an independent reviewer actually completed that review. The flag is a declaration, not authentication or automatic truth verification. A later change to a candidate requires a new review; `changes_requested` blocks admission. An independent source review of an earlier cycle is not a candidate-wide pass for a later one.

## Recovery

`status` distinguishes open, recovery_required and committed. If a write stopped after commit preparation, rerun:

```bash
python scripts/cycle.py commit RC-003
```

The saved candidate and intent allow recovery even if canonical replacement already occurred. If another writer changed canonical state, the utility refuses to overwrite it. Review and rebase into a new cycle. Repeating a successful commit is idempotent. A committed cycle cannot accept new submissions.

The OS lock serializes cooperating cycle processes. Baseline hashes, immutable records and a linked event journal detect accidental changes. They are not a tamper-proof adversarial security boundary. Git adds historical review and recovery; it does not make claims true or prevent a person editing files outside the workflow.

## Verified behavior

Seven tests passed on Linux: missing/exact-candidate review, orphan source rejection, lost-update protection, idempotent commit, recovery after canonical replacement, altered baseline/journal detection, and preserved checkpoints with cross-cycle rejection. Windows locking is implemented but untested; directory flush durability differs from POSIX.

RC-002 was actually run through begin → six saved submissions → explicit limited coordinator review → validated commit → view generation. Its audit lists changed source and record IDs. This is an executed deployment, not a sample-only scaffold.

## Git maintenance

Preserve the user's initial license commit, then the RC-001 baseline and RC-002 implementation/research changes. Inspect upstream before each update and use a non-forced fast-forward. Keep descriptions and license unchanged unless requested. GitHub is the current project home; older exported first-cycle artifacts are historical snapshots.
