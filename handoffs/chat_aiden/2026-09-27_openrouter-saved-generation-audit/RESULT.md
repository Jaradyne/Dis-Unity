# OpenRouter saved-generation audit — 27 September 2026

Generation: `gen-1790241783-S8W2Vc6pfpCKlAE4OrBL`

Purpose: determine whether the old Week One Answer Bee generation can still be recovered/audited **without making another inference request**.

## Current result

A GitHub-hosted audit used the existing `OPENROUTER_API_KEY` secret and made **GET requests only**.

- `GET /api/v1/generation?id=<generation>` → **HTTP 404**
- `GET /api/v1/generation/content?id=<generation>` → **HTTP 404**
- inference POSTs made by this audit: **0**
- no cost/provider/BYOK receipt can therefore be recovered from the current generation endpoints
- no stored completion is available through the current content endpoint

Run: https://github.com/Jaradyne/Dis-Unity/actions/runs/36299956432

## Interpretation boundary

This does **not** establish that the historical generation incurred a charge. It establishes that the saved generation ID is no longer retrievable through the two currently documented generation-history endpoints using the configured key.

The original saved response remains:
- ID present;
- choices empty;
- usage empty;
- model null;
- OpenRouter metadata empty.

OpenRouter currently documents both GET generation metadata and GET stored generation content endpoints; both document 404 as a possible result.

## Next operator check

The remaining useful human-visible check is OpenRouter **Activity / logs** for the time of the original request (24 September 2026 around 09:23 UTC), using the saved generation ID if the UI supports direct search/filtering.

If Activity no longer contains enough information either, preserve this generation as **historically unverified / no positive spend observed**, retire the recovery loop, and decide separately whether to authorize a new provider-neutral Answer Bee path. Do not rewrite the old event as verified zero-cost.
