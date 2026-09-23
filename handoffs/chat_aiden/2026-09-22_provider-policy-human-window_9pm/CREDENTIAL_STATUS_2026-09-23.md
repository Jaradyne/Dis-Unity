# Credential status update for Work Aiden — 2026-09-23

User reports the following GitHub Actions secrets have now been added:

- `CLOUDFLARE_API_TOKEN`
- `OPENROUTER_API_KEY`

Existing Gemini credential remains available per prior setup.

## Important handling

- Chat Aiden cannot read GitHub Actions secret values and has not attempted to do so.
- Treat these as **user-reported present**, then let the reviewed adapter fail safely if a secret is absent/mis-scoped.
- Never print, echo, log or persist secret values.
- Secret presence does not itself authorize paid resources; stay within the approved free/zero-spend design unless the user later changes that.

## Cloudflare

For direct Workers AI REST calls, Cloudflare requires both:
- API token in `CLOUDFLARE_API_TOKEN`;
- Account ID.

Recommended repo configuration:
- keep token in Actions Secrets;
- store Account ID as a GitHub Actions **variable** named `CLOUDFLARE_ACCOUNT_ID` (it is an identifier, not a credential).

If the token was made from the Workers AI template it should have the needed Workers AI permissions. If a custom token was used, verify Workers AI Read/Edit as required by the chosen endpoint before live use.

Do not create one token per Cloudflare model.

## OpenRouter

One `OPENROUTER_API_KEY` serves the approved OpenRouter pool.

**NO GROQ** applies inside OpenRouter too.

Adapter requirements:
- name an explicit model rather than opaque `openrouter/auto` for evaluation/role-fit use;
- send provider routing controls that exclude Groq (`provider.ignore`) and/or use an explicit `provider.only` allowlist;
- do not let fallback routing silently reintroduce a denied provider;
- preserve the actual serving provider when OpenRouter reports it;
- consider a persistent OpenRouter guardrail with Groq in `ignored_providers` as defense-in-depth, but request-level enforcement is still required.

No account-side change is required from the user before Work can implement/test this policy safely.

## Later credentials — not needed yet

Only add when an adapter is actually ready:
- `MISTRAL_API_KEY`
- `TAVILY_API_KEY`
- `BRAVE_SEARCH_API_KEY`
- research Gmail OAuth credentials
- Discord bot token

USGS/public-government sources are service-specific: many feeds and endpoints are anonymous/public; some modern USGS Water Data endpoints accept anonymous traffic but use free api.data.gov keys for materially higher rate limits. Do not assume “USGS” has one universal authentication policy.
