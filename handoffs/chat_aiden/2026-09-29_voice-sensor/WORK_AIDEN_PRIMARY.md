# Work Aiden — primary request: smallest deterministic sensor spine

## Goal

Build the smallest real **sensor → threshold handoff** path on top of the current Garden nervous-system architecture.

A sensor should cheaply inspect one explicitly permitted machine-readable source, remember what it has already seen, preserve provenance, and emit a bounded handoff only when something is new or materially changed. It should not invoke an LLM merely to decide whether a source changed.

This request comes from Jared + the new Voice collaborator, reviewed by Chat Aiden.

## Preferred first proof

Use **one existing official machine-readable source already familiar to the repo** if practical (NWS or EIA are preferred candidates) so endpoint/terms ambiguity is not the first variable under test.

If an RSS/Atom source is substantially cleaner and its current official endpoint/automation permission can be verified, that is acceptable. Do not assume the Ship & Bunker example is current until verified.

## Required behavior

### 1. Source registry entry

Create the minimum registry needed for the one proof source, with explicit separation between source family and endpoint.

At minimum preserve:
- publisher / source family;
- endpoint;
- intake type;
- allowed hosts;
- permission/terms basis or reference;
- when that basis was checked;
- expected cadence if known;
- stable-ID strategy;
- update/correction semantics if known;
- language/geographic scope if relevant;
- source-family lineage key;
- limitations.

Do not broad-fill speculative metadata just because the schema has a field.

### 2. Deterministic fetch

Fetch through the source's intended machine-readable interface.

Prefer conditional/cursor semantics when supported:
- ETag / If-None-Match;
- Last-Modified / If-Modified-Since;
- source cursor/page token;
- stable event/version IDs.

Respect existing network recording / allowed-host constraints. No scraping around login/CAPTCHA/terms restrictions.

### 3. Normalize without interpreting

Normalize only enough to support identity, timing, provenance, and handoff.

A normalized item should preserve, when available:
- stable source item/event ID;
- canonical source URL/ref;
- title/type;
- event/effective time;
- publication/update time;
- retrieval time;
- raw receipt/material reference;
- content hash/version hash;
- source-family lineage;
- language/geography metadata supplied by source.

Do not summarize meaning with a model in the sensor.

### 4. Change-state memory

Persist enough state to classify a poll/item as:
- `new`;
- `changed`;
- `unchanged`;
- correction/retraction only where the source exposes a defensible signal.

Do not use a content hash as the item's sole identity.

A repeated unchanged poll should not store another redundant full body when a conditional response or prior hash is sufficient; it still needs a lightweight receipt proving the check happened.

### 5. Temporal-validity metadata

Add a small freshness profile to the normalized/handoff material.

Prefer fields such as:
- event/effective time;
- published/updated/retrieved/last-verified;
- expected cadence when known;
- observability;
- freshness hint/class;
- stale-after only when defensible;
- consequence if stale.

A stale flag is a routing/review signal, not automatic falsification or evidence deletion.

### 6. Wake semantics

For this first proof, **do not automatically call a model**.

On new or materially changed relevant material:
- emit one bounded threshold/Garden handoff packet;
- preserve source lineage and sensor receipt;
- state why it was emitted;
- carry a suggested role/tree if useful;
- let existing Garden candidate/permission logic decide what, if anything, wakes next.

On unchanged material:
- preserve the poll receipt/state update;
- emit no cognition handoff.

### 7. Relevance

Keep relevance deterministic and narrow for the first proof.

Acceptable v1 choices:
- all new items from one already-narrow event source;
- a small explicit allowlist of event categories;
- one deterministic field/value predicate.

Do not add embedding/model classification merely to decide whether to wake a Bee.

### 8. Digestion and replay

Project sensor receipts and emitted handoffs into an inspectable threshold area. Preserve enough state that:
- a replay can explain why an item was called new/changed/unchanged;
- Chat Aiden and Digest Aiden can inspect the exact material;
- the same item does not repeatedly wake work without a real version/change;
- corrections remain linked to the same source identity.

## Acceptance test

Demonstrate all of the following with the one proof source:

1. first observation → `new` → one handoff;
2. exact repeat → `unchanged` → no handoff;
3. same stable ID with changed content/version → `changed` → one new linked handoff;
4. unrelated/rejected item, if relevance filtering is present → no handoff;
5. full/appropriate receipt exists for each fetch;
6. provenance points back to one source family and endpoint;
7. no model call is made by the sensor;
8. no duplicate wake occurs on replay;
9. formula-safe projections / canonical tests still pass;
10. current Garden/Week One state remains intact.

A fixture may simulate change for tests; at least one real permitted fetch should prove the adapter against its actual source.

## Stop condition

Stop when one source works end-to-end and the adapter boundary is obvious.

Do **not** generalize every RSS/API/iCal/email source in this pass. If a second tiny adapter is necessary to prove the interface is not source-specific, leave it as a tightly bounded follow-up rather than opening a source-ingestion platform project.

## Return note

Please leave Chat/Jared a concise note with:
- source chosen and why;
- current official endpoint/permission basis checked;
- what constitutes identity vs content version;
- where sensor state lives;
- what creates a handoff;
- what remains manual/supplied;
- all network/model calls and cost;
- tests/verification;
- next smallest useful adapter.
