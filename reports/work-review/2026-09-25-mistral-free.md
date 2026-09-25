# Mistral Free API review — 25 September 2026

Status: public documentation review complete; account mode and model role fit unverified. Prepared by the bounded Work research subagent on 25 September 2026. The initial checkpoint is superseded by this report.

Work follow-through: the documented Subscription page was opened in the connected browser and showed an ordinary sign-in page. No authenticated Organization settings were available. The two account checks below therefore remain pending. Work reread the Subscription and API-key documentation and saved the unexecuted three-case prompt in `prompts/mistral-parallax-role-fit.md`.

Scope: establish the public Free versus paid API boundary and a bounded Parallax role-fit plan. Jared reports saving a Mistral key in GitHub secrets. That establishes neither account mode nor model suitability. This review retrieved no credentials, made no inference request, and changed no provider configuration or schedule.

The configured provider remains the reviewed OpenRouter/Nvidia route; its actual live operating status must be read from `week-one-state`. Mistral is a candidate only. Zero spend, NO GROQ, four shared POST reservations per UTC day, and one-generation-one-POST remain unchanged.

## Finding and two account checks

Mistral documents self-service Studio API access in Free mode with no card required [S1]. New accounts default to Free mode; enabling pay-as-you-go permits billed usage beyond the included allowance [S2]. Crucially, API keys inherit the Organization's plan and PAYG setting; there is no separately scoped “Free API key” [S3]. Adding the secret does not establish a free-only boundary.

At [Admin → Subscription](https://admin.mistral.ai/subscription), verify only these two settings for the Organization that owns the saved Studio key:

1. **Plan: Free mode.** Identify the correct Workspace/Organization from non-secret key metadata if necessary.
2. **Pay-as-you-go: disabled.** Preserve a dated, non-secret confirmation of the displayed setting.

No new key, payment method, paid plan, or top-up is needed for this check. Mistral also exposes usage, per-model limits, and Organization/Workspace spending caps [S4]. The reviewed docs do not establish that setting a cap to zero is an atomic, free-compatible guarantee, so this review does not recommend a speculative cap workaround.

The API key itself can later become billable if its Organization settings change. No verified account-state API check or per-generation dollar receipt was established in this five-page review. Before an adapter is enabled, Work must establish how to verify the account boundary and spending outcome without pretending token counts prove zero cost. Positive reported cost must retain the existing Week One closure behavior; uncertainty must not be converted to a zero-cost assertion.

## Candidate and bounded role-fit plan

**Candidate: direct Mistral, exact model `mistral-small-2603` (Mistral Small 4).** Its official card lists chat completion, reasoning, and structured output capabilities [S5]. These make a bounded packet-comparison trial reasonable; they do not prove Chinese/English fidelity, successful Parallax work, or Free-account availability. The public model card lists positive paid tariffs, so an exact model ID alone is not a free-only handshake. Do not use a moving `latest` alias, aggregator route, or fallback.

While account mode is unresolved, prepare three offline fixtures from the reviewed Translation/Parallax packet, with no model call:

| Fixture | Required behavior |
| --- | --- |
| Matched official comparison plus an ordinary control | Preserve URLs, dates, units, scope and ordinary wording/genre explanations; identify what agrees. |
| One original unavailable | Report that a substantive mismatch cannot be established; do not reconstruct a missing original. |
| Jared's preserved flotsam | Record attention and the surviving question; leave every item's evidence status unchanged. |

Save one exact trial prompt and expected output fields: source references, comparison, ordinary explanations, residual, uncertainty and proposed Garden return. Offline validation can establish schema and reference integrity only; it cannot establish model quality.

After both account checks and an appropriate spending-verification method are established, a reviewed, explicitly bounded trial may make **one** direct Mistral POST containing these fixtures, within the existing shared daily allowance and authorized window. Record actual returned model/provider identity and the full response; no tools, external search, automatic retry, fallback, or scheduling. Failure or missing identity ends the trial. Work compares the response with the fixtures before any runtime adoption. A role definition remains available/not-running meanwhile.

## Source ledger

All five pages are primary Mistral documentation, retrieved **2026-09-25 UTC**. Dates below distinguish a dated model release from dynamic documentation. These pages do not establish Jared's account state.

| Ref | Actual URL | Publication/event date | Observation and access limit |
| --- | --- | --- | --- |
| S1 | https://docs.mistral.ai/getting-started/quickstarts/studio/activate-and-generate-api-key | Publication/update date not shown | Public setup instructions observed on retrieval; self-service Free mode, no credit card required. |
| S2 | https://docs.mistral.ai/admin/billing-usage/subscriptions | Publication/update date not shown | Public plan/PAYG rules observed on retrieval. Its linked console URL redirected to sign-in in public retrieval; no account inspection performed by this reviewer. |
| S3 | https://docs.mistral.ai/admin/identity-access/api-keys | Publication/update date not shown | Public key metadata and scope rules observed on retrieval; no key values accessed. |
| S4 | https://docs.mistral.ai/admin/billing-usage/usage-limits | Publication/update date not shown | Public usage/rate/spending-cap descriptions observed on retrieval; account-specific remaining allowance unknown. |
| S5 | https://docs.mistral.ai/models/mistral-small-4-0-26-03 | Model card dated 2026-03-16 (release); last revision not shown | Current exact model ID and listed capabilities observed on retrieval; availability to Jared's Free Organization and actual role fit remain untested. |

Shareable reflection: a free account mode can supply a clearer billing boundary than an inference model's name, but the key does not freeze that mode. Keep the human check to two settings, and make the first trial demonstrate restraint and source fidelity before treating fluent output as useful specialist work.
