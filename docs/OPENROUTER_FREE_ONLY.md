# “Sell me nothing” — checked 25 September 2026

The useful boundary is two checks: **request free or refuse; verify what was served**. Four POST reservations per UTC day remains our conservative project limit. No new paid service, provider substitution or Groq route is authorized.

The request pins `nvidia/nemotron-3-super-120b-a12b:free`, permits only Nvidia, disables fallbacks, and sets prompt/completion/request/image price ceilings to zero. OpenRouter documents provider allowlists and price filtering. A live catalog check establishes advertised prices immediately before a new POST. The receipt then establishes actual generation/model/provider, non-BYOK and cost. Missing fields remain unverified and recover the same ID by GET. A positive cost closes Week One; missing cost is not proof of spending. [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection).

I did not establish a universal account/key setting that guarantees every permitted operation is intrinsically free while retaining the required controls. The key API describes a USD limit, but does not establish that `limit:0` remains usable for free calls or is an atomic protection against every charge. Guardrails describe model/provider restrictions, but availability is plan-dependent: the current Free pricing surface lists no budgets/spend controls, preferred vendor selection or management API key. Do not upgrade or request broader credentials to solve this. [Key API](https://openrouter.ai/docs/api/api-reference/api-keys/create-a-new-api-key), [guardrails](https://openrouter.ai/docs/guides/features/guardrails), [pricing](https://openrouter.ai/pricing).

Jared's small account check, with no keys to paste:

1. Keep auto top-up off and buy no credits for Week One. A nonzero spending cap authorizes some spending, so it is not a substitute for the zero-price route. [Billing FAQ](https://openrouter.ai/docs/faq).
2. Keep this route free of extras: no applicable Nvidia BYOK key and paid default plugins off. Account-enforced plugins can override a request's disable flag. The adapter explicitly disables web search, file parsing and response healing; the last is disabled to preserve the raw output, not because a fee was established. [BYOK](https://openrouter.ai/docs/guides/overview/auth/byok), [plugins](https://openrouter.ai/docs/guides/features/plugins).

These are account setup conditions, not settings inspected in this session. BYOK filters can scope a provider key away from this application; do not change unrelated applications. The inference credential does not prove account settings. No credential values or management metadata were retrieved.

Observed control: [run 36116582032](https://github.com/Jaradyne/Dis-Unity/actions/runs/36116582032), completed 25 September at 09:07 UTC, saved an actual Nvidia/non-BYOK receipt with total cost 0. That demonstrates one free completed generation; it does not prove a universal billing lock.

Documentation was retrieved on 25 September 2026; the pages do not supply a single common publication date. Findings are limited to the documented request route and publicly saved receipts. Provider limits and account entitlements may change. The positive-cost stop is detection and shutdown, not a promise that an external billing error cannot happen. Actions disables itself at closure; the separate Chat Governor notices closure at its next wake before research.
