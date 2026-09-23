# Presence-of-Activity Governor — proposed

## Goal

Schedule autonomous Pygent work around the user's and Aidens' active periods so background work tends to expand during quiet/offline periods and contracts while active collaboration is happening.

This is a **soft activity governor**, not surveillance and not a sleep detector.

## States

- `ACTIVE` — recent user/Aiden interaction or explicit heartbeat; prioritize interactive support, source lookup, ticket packaging and small reversible jobs.
- `COOLING` — activity recently stopped; finish already-running bounded tasks but avoid birthing large new trees.
- `QUIET` — sustained absence of activity; permit queued research and provider attempt cycles.
- `DEEP_QUIET` — historically low-activity period plus no current signals; allow larger bounded batches, model evaluations and source sweeps.
- `UNKNOWN` — insufficient signals; behave conservatively like COOLING/QUIET depending on task urgency.

Never assert the user is asleep. Call it a quiet/offline window.

## Signals

Possible heartbeat sources:
- explicit Chat/Work repo activity
- Thinking Mailbox edits
- GitHub commits/PR comments/issues
- future Discord bot interactions
- a future public activity endpoint or manual "active/quiet" toggle

ChatGPT conversation activity is not automatically visible to an external Pygent. If we want it represented, Chat/Work can emit a lightweight heartbeat during repo-related sessions.

## Learning

Maintain a rolling local-time activity profile that slowly adapts rather than hard-coding bedtime.

Store coarse time-window statistics, not private conversation content:
- last activity timestamp
- rolling active-window histogram
- moving estimates of typical session start/end
- confidence
- recent exceptions

Use configured timezone separately from UTC.

## Scheduling behavior

Interactive periods:
- sensors keep collecting
- questions may be packaged
- provider work that would duplicate Chat research waits
- urgent freshness-sensitive sensor checks can continue
- do not interrupt the user's collaboration with noisy autonomous outputs

Quiet periods:
- run open Question Bees
- run full provider attempt rings for eligible Answer Bees
- refresh fast-decaying evidence
- process deferred_capacity/deferred_quota providers when eligible
- stage packets for later Aiden review
- do not perform outreach, spending, irreversible writes or canonical integration

## Evolution

Treat the governor like RC-003: record observed failures and adapt.
Examples:
- if jobs routinely finish just as the user returns, start earlier/later;
- if a provider is most available in a certain window, learn that;
- if a source updates at a predictable hour, schedule its sensor around publication rather than user sleep;
- if the user is active at historically quiet hours, current activity wins.

The governor optimizes timing; it never owns research truth.


## Clock discipline

Store machine timestamps in **UTC (Greenwich/zero-meridian clock)** for interoperability, while preserving the user's local timezone separately for human scheduling. Do not pretend every provider's quota/reset follows UTC.

Maintain a provider/source reset registry with:
- timezone or documented reset basis;
- reset time;
- whether the limit is rolling, fixed-day, monthly/billing-cycle, or unknown;
- last verified documentation date.

Known examples to preserve:
- Cloudflare Workers request quota: resets at **00:00 UTC**.
- Cloudflare Workers AI free Neuron allocation: resets at **00:00 UTC**.
- Gemini daily request quota: resets at **midnight Pacific time**.
- OpenRouter daily reset semantics: verify rather than assume.
- Monthly search/API credits: use the provider's documented billing/reset basis; do not coerce them to UTC.

The governor may reason in local time for user activity and UTC for machine coordination. Current activity always outranks historical quiet-hour expectations.
