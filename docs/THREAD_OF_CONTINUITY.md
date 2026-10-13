# Thread of Continuity

Three relationships now connect existing historical records across lanes without copying each specialist's archive. Start with the [Digest handoff](../reports/continuity/DIGEST_HANDOFF.md) or the [generated projection](../reports/continuity/generated/DIGEST.md). This is a supplied-content review ledger over the existing Garden runtime. It performs no source retrieval, worker dispatch or canonical evidence admission.

## Files and reconstruction

| File | Purpose |
| --- | --- |
| [Relationship schema](../schemas/continuity-relationship.schema.json) | Typed fields, bounded vocabulary, explicit unknown target and one proposed next test |
| [Reference manifest](../operations/continuity/references.json) | Shared file, collection, record ID and semantic SHA-256 for each event/source alias |
| [Relationship journal](../operations/continuity/journal.json) | Attributed, ordered assessments with revision reasons and chained entry hashes |
| [Projector](../scripts/continuity.py) | Standard-library validation, journal replay and deterministic Garden projection |
| [Generated directory](../reports/continuity/generated/) | Reconstructed relationships, readable Digest table and three complete saved Garden passes |
| [Tests](../tests/test_continuity.py) | Evidence, date, reference and revision boundary checks |

From the repository root:

```bash
python scripts/continuity.py validate
python scripts/continuity.py replay
python scripts/continuity.py check
python examples/garden-case-studies/camp-east-montana/replay.py --check
```

`validate` and `replay` both reconstruct all supplied journal entries, resolving and checking the referenced shared records. `check` also regenerates all five continuity outputs in memory, replays every Garden pass and compares the saved files byte for byte. `build` writes the generated projection after reviewed input changes. It does not alter the journal, shared archive or canonical state. The Git revision retains the code, schema, catalog, supplied assessments and Garden configuration needed to reproduce this version. No wall-clock value is introduced during replay.

The existing verification workflow runs these checks on the same push/pull-request/manual triggers it already had. This adds no monitoring schedule.

## Relationship contract

Each relationship preserves its ID and type, source and target event aliases, lane names, claim and scope, time interval, explicit epistemic status, supporting source references and locators, ordinary explanations, counterevidence, limitations, one bounded next test and rest condition. Attribution, recording time and revision reason belong to its journal entry. All relationship object fields are required; unexpected fields and unsupported values fail validation.

The four initial relationship types are `precedes`, `contracts_for`, `changes_reporting_authority` and `affects_decision`. Type describes the proposed connection; it does not determine truth. Status is separately `documented`, `partly_documented`, `hypothesized`, `contested`, `refuted` or `unknown`.

Evidence is explicitly classified as `direct_record`, `context` or `temporal_only`. A documented/partly documented assessment must cite at least one source marked direct record. The validator checks that declaration and resolves its source; it cannot decide whether the author's interpretation is sound. Human review of the source, locator, scope and counterevidence remains necessary. `direct_record` includes the retained GAO audit as direct documentation of its reported findings; it does not imply this project inspected every underlying contract. The AFCB sources retain their indexed-text/facsimile access limits.

An unobserved target is `to_event: null` with a required explanation. It cannot be documented or partly documented. It may remain hypothesized/unknown, be contested, or be refuted after an explicit changed evidence assessment. Refuting a candidate path never requires inventing a historical target. A newly observed target needs its own retained event and a new relationship ID, with a reason linking back to the original candidate; the old hypothesis remains inspectable.

## Time and inference

Event, effective, publication, retrieval and assessment-recording dates remain distinct. References retain the full original records. The readable projection reproduces their date fields and qualifications; it also shows source publication/catalog retrieval dates and access limits. The Camp source's catalog retrieval date is not substituted for the original HTTP capture date retained in the Camp case.

Time-scope bounds accept ISO day, ISO month or unknown/null. Month values retain their whole possible calendar interval; mixed-precision bounds are rejected only when definitely reversed. A null end is unknown, not a claim that an institution remains active indefinitely.

Only two precise day dates produce a computed order and day gap. A missing or imprecise endpoint produces `unresolved_or_imprecise` and no invented day count. A declared `precedes` relationship requires known ordered day dates. Even a precise temporal order never upgrades an epistemic status, proves a mechanism, or connects two different relationship records causally. The February 2025 assessment-development event remains earlier than ORA's September 2026 creation; it is context, not an ORA implementation outcome.

## Shared references and revisions

The manifest points into the existing RC-005/RC-006 report catalogs and the preserved Camp case. It contains selectors and hashes, not a second copy of every historical event or document. Record hashes use the repository's canonical JSON encoding: formatting-only changes do not change meaning, while a changed record fails the pin. Source families stay attached to the original records. Reusing a source in several lanes, or adding an alias for it, does not create independent corroboration.

Journal replay requires contiguous sequence numbers, timezone-aware nondecreasing recording timestamps, correct per-relationship expected revisions, and an intact entry-hash chain. It retains the earlier entry when a new assessment supersedes it. Changing endpoints or relationship type under an existing ID fails. A status revision also requires a changed supporting-evidence or counterevidence assessment, rather than a bare status edit.

For a future reviewed revision, append an entry using `make_entry` with the current relationship revision and last entry hash; preserve existing entries. To cite new shared records, add new aliases and update the journal's manifest digest in the same reviewed change. Never retarget or repin an existing alias to different historical content; introduce a distinct reference instead. Schema changes need a reviewed version change. Git history retains the previous manifest/schema snapshots; these editorial extension rules are subject to review, not a separate permissions engine. There is deliberately no collection loop or automatic status-upgrade command.

The hashes detect mismatches against the retained pins. They are not digital signatures or a defense against a party rewriting and resealing the entire repository. Catalog record hashes also do not authenticate external URLs or every underlying archive byte. The Camp case retains its own stronger input/PDF pins. Source accuracy, changed public documents and evidence admission require the existing review process.

## Garden boundary and stopping point

Each latest assessment projects into the existing ten-node Garden traversal, with one branch, ten steps, zero fanout and zero model calls. Sources are inherited; CROSS has no manufactured independent return. ARRIVAL uses an explicitly unknown language glance because the projector reads supplied metadata, not fresh source language. Each saved run has a case-local Question snapshot, returns to rest, and can be replayed by the existing Garden reducer. No Question is registered in the shared registry and no proposed test is executed.

These demonstration passes live with the reviewed code and case inputs. They do not represent a live `week-one-state` operation or a new research cycle. RC-005, RC-006, the Camp case and canonical RC-004 remain unchanged. No Bee, provider, schedule, model or Governor authority is activated. The accepted scope ends when the three connections can be reconstructed and inspected reliably; the narrow tests remain proposals for later review.
