# Direct input for the repo Governor — 27 September

Jared asked to keep Chat Aiden distinct from the repo Governor and send his played encounter directly to the latter. This integration connects PR #19's inputs to the existing bounded Governor session and preserves PR #20's completed receipt audit.

## What now works

- The complete second play, `PLAY-b803b289-ff43-4f29-aa48-5ce4dd62d24d`, is preserved under `operations/governor/bundles/`. Its regenerated delivery exactly matches the supplied export. The choices are **Shared direction → Until payment → Who can carry it?** Sources, ordinary control, unselected pieces, original evidence labels and the no-power step survive the handoff.
- Digest Aiden's advisory feed retains its authorship and links the newer `INTEGRATION_AFTER_DIGESTION.md`. That discussion refines the older machine feed, including the rejected “earned” language and candidate saṃskāra morphology. Model mesh, memory lifecycle, language sensing and power development remain design discussion.
- `scripts/governor_inbox.py` checks the inputs and projects each into the existing reflection mailbox. The runner does this during an Answer Bee pause too. A repeated or interrupted import reuses the same reflection IDs.
- `scripts/governor.py` includes full direct inputs alongside the Daily Scroll, existing reflections, voice and series context. The existing scheduled Governor session receives the same live input file. Reading or preparing does not count as review.
- A scheduled response names the input's real reflection ID; its optional `keep_open:false` permits rest. Responses keep their actual actor, and later reconsideration appends rather than replaces them.

## Where to look

Main contains reviewed inputs, bundles and runtime. On `week-one-state`:

- `operations/week-one/GOVERNOR_INBOX.md` — readable queue and review status;
- `operations/week-one/governor-inbox.json` — validated full inputs, separate companion observations, later context and response history;
- `operations/reflections/mailbox.json` — durable imported notes and attributed responses.

The Governor's research/review output still lands on main at `handoffs/week_one_governor/YYYY-MM-DD.json` and `.md`. Its next hosted import makes the response visible in live status. The original schedule and October 3 Pacific endpoint remain in force.

## Recovery and a small Python walkthrough

A Python `dict` holds one envelope's named fields. `validate` opens the referenced original and derives its delivery again. `snapshot` assembles readable inputs and checks for an actual response. `ingest` places their references into the existing mailbox. It does not ask a model to think; the separate Governor session does the review.

On a checkout with reviewed main and current restored operational state:

```bash
python scripts/governor_inbox.py inspect
python scripts/governor_inbox.py ingest
python scripts/governor.py --output operations/reflections/review-UNIQUE.json
```

For interrupted imports, repeat `ingest`; existing content-addressed notes remain. For a malformed input, inspect the per-file error, repair the reviewed source, and retry. Page with `--offset` when `remaining_count` is nonzero. For live publication use the existing `week_one_state.py load/save` workflow, retaining its concurrent-change check. Main input and runtime files must never be restored from the operational branch.

## Provider audit and current limits

PR #20 records two HTTP 404 results for saved generation `gen-1790241783-S8W2Vc6pfpCKlAE4OrBL`: metadata and stored-content GETs. The linked hosted run completed successfully. This integration preserves that report as attributed audit evidence; it does not convert missing data into a zero-cost receipt or a spend event. The one-off workflow is archived as `handoffs/chat_aiden/2026-09-27_openrouter-saved-generation-audit/AUDIT_WORKFLOW.yml`, so merging does not create another credential-bearing audit entry point.

The Answer Bee remains at its saved receipt brake. Source scouting and the separately scheduled Governor continue within the existing window. Mistral's account/429 discussion is preserved as Chat's report; this integration does not verify or activate a Mistral adapter. Existing four-POST limit, zero spend, NO GROQ and the stop-on-positive-cost behavior remain.

## Verification

Targeted tests cover original-play binding, source/evidence preservation, interrupted imports, malformed inputs, reference paths, historical epochs, pagination, review/rest/reconsideration and intake during a provider brake. The original play was validated against current main Question and Garden records. Tests use synthetic review responses; none is attributed to a real Governor run.

Local verification: **90 Python tests passed**, including nine new inbox tests; the JavaScript interaction contract passed, canonical validation passed, and the diff has no whitespace errors. Base reviewed: main `1cc33ae724c472997cdb1548fd8a14e6fec56f52`, live operational state `1fafec4da6b66b4919e4afffa31badc48fc0e733`. Reopen live status for subsequent runs.

No new research cycle is opened: RC-004, its canonical state and immutable history remain intact.
