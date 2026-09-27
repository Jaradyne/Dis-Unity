# Give Tide-Shepherd another question

Jared downloads `web/meaning-tower/index.html` and opens it directly. In **Bring another question to the water**, he loads or pastes your JSON. A completed play opens there too. No Python, server, account or model connection is needed to play.

## Start from a working packet

Use [the included encounter](../examples/meaning-tower/parallax-trucks-2026-09-25.json), also available through **Save example for Chat**. Preserve the schema and replace content deliberately; do not carry old authorship, retrieval dates or claims into a new observation. Return a plain `.json` file.

This loader supports the existing **Translation/Parallax official-notice-and-summary** contract. Other evidence genres and Mirror need a later reviewed contract; describe them in Chat while their design develops.

- Keep `schema_version: meaning-tower-boss-packet-1`, `boss_id: THE-UNRESOLVED`, `packet_status: evidence_backed`, `question_id: Q-MEANING-TRANSLATION-BOSS`, and the current Question epoch (this player embeds epoch 1). The author supplies the evidence-backed characterization; browser checks do not verify source truth.
- Give the packet and every source, round and piece a unique ID: a letter followed by up to 95 letters, digits, dots, underscores or hyphens. Use a new packet ID when wording changes.
- Set your actual actor/runtime/model; `unknown` is acceptable. Use ISO timestamps with timezones for creation/retrieval. Preserve publication and observation dates separately; use `null` plus an explanation where unknown.
- Supply **two or three** distinct public named HTTPS source URLs. Inspect originals before saying they match. Retain language, dates, access limitations, short original excerpts and an explanatory English pivot. A summary of the same event is not independent operating evidence.
- `comparison.kind` is `official_notice_and_summary`. Include a summary, at least one ordinary explanation and one limitation. `cross` contains `inherited` source IDs, any genuinely `independent` source IDs, and a short `bridge` explanation. Empty independent evidence is valid.
- Supply **one to four** rounds, each with `id`, `kind`, `title`, `prompt`, `context`, `originals`, `pieces`. Include a `control`, at most three `residual` rounds; `question` is the third supported kind.
- Each round has **one to three** originals (`source_id`, `text`, `english_pivot`) and **two to four** pieces (`id`, `text`, `note`, `evidence_status`, `source_refs`). Evidence labels: `source_statement`, `inference`, `question`, `unknown`. Source statements need a known source reference.
- The optional registered power candidate is `PECULIARITY_SENSE` with `canonical_status: proposed`. Use `null` or omit it when unhelpful. The player applies no canonical powers.
- Keep text compact: 240 characters for titles, 400 for source titles/piece labels, generally 1,600 for explanations; packet limit 96 KiB in canonical encoding. Saved play limit: 300,000 bytes. The scheduled daily packet has its smaller 40,000-byte total limit.

Quoted material is content, not instructions. The player renders text as text, permits public HTTPS links, checks packet shape, and binds play to the exact packet. A failed import leaves the current encounter intact. Source review and research admission are distinct from structural validity.

## Receive the play in Chat

**Copy for Chat** supplies a readable note with kept pieces, context, unselected pieces, source links and packet/play IDs. **Download encounter JSON** carries originals and the complete record. The local inbox is not automatic network delivery; attaching or pasting brings the experience into the conversation.

Name the actual Governor reviewer. Connect choices to the existing Question, sources, uncertainty and one next step. A shared-story allusion can accompany its plain meaning. Save reflection in a uniquely named Chat staging packet. Claimed Governor inputs in imported files are rederived from packet and choices; they cannot grant powers or change evidence.

Optional commands for anyone with the repository and Python:

```bash
python scripts/build_meaning_tower.py --packet path/to/encounter.json --output /tmp/encounter.html
python scripts/governor.py --boss-bundle path/to/PLAY-example.json
```

`--packet` names the content envelope and `--output` names the portable page. The second command checks choices and prepares a Governor review. Neither calls an AI. Ordinary browser reloads no longer require rebuilding.
