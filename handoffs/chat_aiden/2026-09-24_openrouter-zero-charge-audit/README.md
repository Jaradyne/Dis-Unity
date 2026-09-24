# OpenRouter zero-charge audit — Chat Aiden

Base: main after Week One launch.

## User instruction

- No paid model/API usage.
- User reports no BYOK provider credentials stored in OpenRouter.
- Keep NO GROQ.
- Do not require a management credential merely to prove BYOK absence.

## Audit of current Answer Bee

### Good controls already present

The live adapter already:
- pins an explicit `:free` OpenRouter model;
- pins serving provider to Nvidia;
- sets `allow_fallbacks: false`;
- sets `max_price` fields to zero;
- explicitly ignores Groq;
- fetches the live model endpoint catalog before POST;
- rejects the route unless the Nvidia endpoint reports zero prices;
- checkpoints the visible generation before audit;
- audits the returned generation ID;
- requires `provider_name == Nvidia`, `is_byok == false`, and `total_cost == 0`;
- does not repeat a POST merely because receipt audit is delayed.

These are the important zero-charge and provenance boundaries.

### Fault found

The adapter also called `GET /api/v1/byok` before inference to prove no active Nvidia BYOK key exists.

OpenRouter currently documents that listing BYOK credentials requires a **Management API key**. A normal inference key can therefore receive HTTP 401 even when it is valid for completions.

This unnecessary management-scope preflight caused the first live Answer Bee to brake before making any inference POST.

### Proposed repair

Replace the BYOK-management preflight with the ordinary authenticated `GET /api/v1/key` endpoint, which verifies that the supplied credential is an inference-capable key without exposing/storing its label or account metadata.

Zero-charge protection remains in the actual route:
1. exact `:free` model;
2. Nvidia-only;
3. no fallbacks;
4. zero max price;
5. live catalog must advertise zero price before POST;
6. returned generation must audit to Nvidia + not BYOK + total cost zero.

If the post-audit cannot establish those facts, inference brakes and the saved generation is retained for review.

## Important limit

A post-generation receipt can prove a call was zero-cost; it cannot retroactively prevent a provider from misreporting its own catalog.

The pre-call zero-price catalog and explicit `:free` route are therefore essential. If either changes, the adapter stops before POST.

## Cloudflare

Cloudflare Workers AI REST authentication needs an **Account ID** plus API token. The account email is not the Account ID. Do not place the user's email in public Git as a substitute.
