# Direct Governor inbox

**27 September integration:** the reviewed input path is now connected to the existing bounded Governor task. The Governor is a separate scheduled ChatGPT session. Chat Aiden and Digest Aiden contribute inputs with their own authorship. A packet being queued is not a Governor decision.

The original PR #19 envelopes are preserved in `handoffs/chat_aiden/2026-09-27_governor-direct-source/`. The play envelope here now binds the complete browser export in `operations/governor/bundles/`. The validator derives the delivery again, including the unselected pieces and their original evidence labels. It does not rely on an edited selection summary.

## Read, import and respond

```bash
python scripts/governor_inbox.py inspect
python scripts/governor_inbox.py ingest
python scripts/governor.py --output operations/reflections/review-UNIQUE.json
```

Use a checkout with current main runtime and restored `week-one-state` operations for live review. The hosted runner imports direct inputs before importing scheduled Governor responses, even while the provider is paused. Its outputs are `week-one-state:operations/week-one/GOVERNOR_INBOX.md` and `governor-inbox.json`. The existing state synchronizer preserves both and the reflection mailbox; source bundles remain on main.

`ingest` projects a stable reflection ID into the existing mailbox. Repeating it after interruption reuses that ID. `inspect` and `governor.py` only read. Use `--limit` and `--offset` for further inbox pages; `governor.py` has separate `--inbox-limit` and `--inbox-offset` flags. Invalid inputs are reported individually for repair without hiding valid ones. A completed play from an older Question epoch retains its original epoch and cannot close the current Question.

The Governor records the direct input's actual `reflection_id` in its ordinary response. Scheduled responses stay at the existing `handoffs/week_one_governor/YYYY-MM-DD.json` path. The next hosted wake imports the response and projects review status. Optional `keep_open:false` lets reviewed material rest; a later attributed response can reopen it. Until an imported response exists, the inbox says **pending**. The preparation code never fabricates one.

For a new play, stage the original bundle and a `governor-direct-feed-1` envelope with `input_id` (the derived delivery ID), `created_at`, `intended_reviewer:"repo Governor"`, `bundle_ref`, `bundle_sha256` (using `cycle.digest`), `submitted_by`, and an optional separately attributed `companion_observation`. Work reviews and admits it. The `governor-digestion-feed-0.1` contract admits only advisory, noncanonical digestion. Up to three `context_refs` may link later Markdown discussion under `handoffs/`; read those before relying on older terminology. Digest Aiden's newer note rejects “earned” and offers saṃskāra morphology as a candidate for discussion.

These inputs can shape attention and proposals. Evidence admission, provider policy and canonical power changes retain their existing review paths.

## Saṃskāra Morphology

Jared has adopted **Saṃskāra Morphology** as the name of the Governor's cultural skill tree. See [the design](../../../docs/GOVERNOR_SAMSKARA_MORPHOLOGY.md) and [the registry](../../../config/governor-samskara-morphology.json).

The Governor review packet reads this registry directly. Powers can represent new affordances, obligations, inhibitions or navigation created by metabolized experience. This is intended to make cultural shape explicit rather than letting it accumulate as invisible prompt drift.

The registry currently describes **Peculiarity Sense** in detail, but its status remains `proposed`. Reading a proposed power does not activate it, award it, change evidence or create a route automatically.


## Original Chat integration request

Jared asked Chat Aiden to stop role-blurring: **Chat remains Chat Aiden; the repo Governor gets a JSON feed and does the Governor review.**

This packet carries Jared's completed Tide-Shepherd play into a proposed repo-resident Governor inbox without awarding a power, changing evidence, or pretending Chat's observation is a Governor decision.

## Preserved choices

1. **Shared direction** — source statement / ordinary control.
2. **Until payment** — inference; possible voluntary delivery/repair bridge, capacity unknown.
3. **Who can carry it?** — question about actual operating capacity: staff, cash, authority, access and backup.

The complete browser bundle remains the authoritative play artifact. The JSON here is a bounded feed for repo review.

## Integration request for Work

Please decide the durable inbox path and wire the repo Governor to consume a validated `governor-boss-input-1` envelope directly. Prefer a clear separation:

`Meaning Tower / Chat feed -> repo Governor inbox -> Governor review/response`

rather than asking Chat Aiden to role-play as Governor in the conversation.

Do not grant `PECULIARITY_SENSE` or any other canonical power from this feed alone.
