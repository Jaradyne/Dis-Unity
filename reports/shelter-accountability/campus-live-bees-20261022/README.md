# Campus Motel: three live Work-session Bees

Start with [FINDINGS.md](FINDINGS.md). [Chat](HANDOFF_CHAT.md) and [Digest](HANDOFF_DIGEST.md) handoffs are concise projections; the original returns remain attributed:

- [Agreement Bee](returns/campus_agreement_bee.md) / [JSON](returns/campus_agreement_bee.json)
- [Funding Bee](returns/campus_funding_bee.md) / [JSON](returns/campus_funding_bee.json)
- [Safeguard Bee](returns/campus_safeguard_bee.md) / [JSON](returns/campus_safeguard_bee.json)
- [Funding and Safeguard peer reviews](peer-reviews/), [Agreement peer review](returns/campus_agreement_bee-peer-review-of-campus_funding_bee.md), and [coordinator review](REVIEW.json)

Jared explicitly requested live Bees. These were three actual collaboration tasks in the Work session using the existing provider-neutral Worker Bee role. [DISPATCH.json](DISPATCH.json) retains accepted task names, exact prompts and role/input hashes. A task's acceptance, its completed return, source verification and canonical admission are separate states. The host did not expose per-agent served model identity or cost receipts; no zero-cost host receipt is claimed. The external API runner's expired window was not renewed. No external-provider inference, recurring monitoring, Governor change, contact or private resident investigation occurred.

Research occurred October 22, 2026. Packaging/review resumed October 23 after interruptions, including a usage-limit stop. Original returns/checkpoints are preserved; later notes have their actual dates. RC-009 is **open review intake**, not a committed research cycle. Saving a reviewed report to Git does not admit it to `Resilience_Cascade_STATE.json`. The earlier Campus case and its Garden pass are unchanged.

`tool-captures/` contains saved tool responses, not necessarily complete origin documents. Origin HTTP recordings are identified separately. The complete budget exchange was compressed losslessly to [receipts/budget-http-receipt.json.gz](receipts/budget-http-receipt.json.gz); [its manifest](receipts/manifest.json) maps the original path and SHA-256 to the archive. Decompression recreates the full recorder JSON, including the base64 PDF body, headers and retrieval times. HTTP Last-Modified is not a document publication or adoption date. No request is needed for verification.

Some search responses incidentally contained personal narratives or unrelated social results. Their unchanged originals are excluded from public Git. Explicitly filtered publication copies record omissions and original hashes; **they are not full raw responses**, and omitted material cannot be reconstructed from this public packet. [PUBLICATION.json](PUBLICATION.json) maps every exclusion to its published derivative and checksums all published packet/cycle files. None of the omitted material supports a finding. The full official budget HTTP receipt is retained without these filters.

From the repository root, verify the published bytes, source-body hash, dispatch inputs, original case and canonical preservation:

```bash
python reports/shelter-accountability/campus-live-bees-20261022/verify_packet.py
python scripts/cycle.py status RC-009
```

The first command is an offline integrity replay, not a new Garden assessment or empirical validation. It has no network, model or canonical writes. Its expected output is saved in [VERIFICATION.json](VERIFICATION.json). PUBLICATION.json and that derived output are excluded from the manifest's own file list to avoid self-referential hashes; Git supplies their version history.

For source inspection, decompress `receipts/budget-http-receipt.json.gz`, then base64-decode `response.body.content` in the JSON to reconstruct the PDF. The manifest supplies both hashes. The original receipt path in the Bee return is intentionally preserved and mapped rather than rewritten.
