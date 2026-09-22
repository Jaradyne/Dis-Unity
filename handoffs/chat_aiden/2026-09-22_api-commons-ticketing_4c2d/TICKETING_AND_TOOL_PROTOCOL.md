# Ticketing and worker tool protocol

## Problem

A research question can be noticed by the Alchemical Mailbox, Thinking Mailbox, Chat Aiden, a Python worker, or a future child agent. The answer may later come from a different actor. The repository needs a durable join key so the question and answer do not separate.

## Ticket identity

Every bounded question gets a stable `ticket_id`, for example:

`TKT-20260922-DIESEL-RURAL-0042`

The ticket is the durable object. Model calls are merely attempts against it.

Suggested lifecycle:

`open -> ready -> claimed -> answered`

with side states:

`deferred_capacity`, `deferred_quota`, `blocked_access`, `needs_refresh`, `superseded`, `closed_no_answer`.

A ticket can be answered by Chat Aiden without API use. That is still an ordinary answer attached to the same `ticket_id`.

## Attempt records

Before any model/API attempt, persist:

- ticket ID
- attempt ID
- actor/runtime/provider/model
- role definition version/hash
- exact rendered prompt or immutable prompt reference
- context references + hashes
- source/evidence cutoff
- generation/tool settings
- creation time

Afterward append:

- start/end time
- result state
- provider status/error category
- raw response/artifact reference when retained
- answer packet reference if usable

Never mutate a failed attempt into a successful one. Make another attempt.

## Answers

An answer references:

- the same ticket ID
- actor/model/runtime
- attempt ID if an API/model attempt produced it
- evidence references
- claims/counterevidence
- limitations
- birth requests
- status: provisional / ready_for_review / superseded

If Chat Aiden resolves a queued question before a worker bee gets it, the ticket becomes answered and later workers should not repeat it unless the answer explicitly requests review or freshness has expired.

## Provider policy

Do not assume one universal “best model.”

A provider/model is **eligible for a role** when current official documentation plus Dis-Unity tests show it is suitable for the job's needed capabilities (reasoning depth, context length, structured output, tool use, coding, vision, etc.).

Rules:

1. preserve actual provider/model identity;
2. do not silently replace an unavailable requested/approved class with a materially weaker model;
3. multiple independently suitable providers/models may attempt different tickets or review one another;
4. a transient capacity error creates a deferred attempt, not a failed research conclusion;
5. do not spray retries across many models merely to force an answer;
6. provider diversity is useful when it creates independent reasoning, not fake corroboration.

## Capacity behavior

**Exponential backoff** means waiting progressively longer between retries rather than hammering a busy server: e.g. 1 second, then 2, 4, 8, with random jitter. Google officially recommends this for transient Gemini 429/503 errors.

Dis-Unity should also use a higher-level queue. One or a few same-run retries can handle tiny hiccups; persistent provider capacity returns the ticket to `deferred_capacity` for a later run.

No arbitrary project-wide ban on API concurrency is proposed. Each adapter should obey the provider's actual limits and the task's cost/priority. A circuit breaker may pause one failing provider without stopping other providers or non-model work.

## Worker tool surface

The Python worker currently has repository files plus a Gemini HTTPS call. A GitHub Actions runner itself has outbound Internet access, so future adapters can expose much more.

### Protocols

- HTTPS REST/JSON
- RSS/Atom
- CSV/JSON/XML public datasets
- OAuth 2.0 for scoped private APIs
- API-key authentication via Actions Secrets
- Webhooks for inbound events
- Git/GitHub APIs
- published Google Sheets/CSV feeds
- SMTP/IMAP only when explicitly chosen; OAuth APIs are preferred for account access
- ordinary package installation inside ephemeral GitHub Actions jobs

### Tool classes

**Sensors**
- EIA, USDA, USGS, BLS, Census, NOAA, FRED and similar public APIs
- RSS/Atom alert feeds
- published Thinking Mailbox
- direct HTTP page retrieval where lawful and technically appropriate
- structured local/public datasets

**Search**
A worker does not automatically possess ChatGPT web search. Give it an explicit search adapter. Current free/small-use options include:
- Tavily free plan: 1,000 API credits/month, no card required
- Brave Search API: $5 monthly credits, roughly 1,000 Search-plan requests, card verification required
Search output remains a discovery surface; agents should open/inspect primary sources rather than treating snippets as evidence.

**Other model brains**
- Gemini free-tier eligible models
- Groq free tier for supported hosted models
- Cloudflare Workers AI free daily allocation and eligible open models
- OpenRouter free models (limited daily requests)
- other providers only after current terms/capabilities are checked

**Compute/storage**
- GitHub Actions standard public-repository runners: ephemeral VMs, free standard runner usage
- Cloudflare Workers Free: lightweight public endpoints/cron/orchestration, not heavy Python jobs
- Git repository, Actions artifacts, and later purpose-built object/queue storage

## Free-resource reality

Free does not mean “guaranteed.”

Free AI tiers typically have no contractual SLA and may expose lower quotas or capacity pressure. The architecture should therefore assume:
- a provider sometimes says no;
- a question can wait;
- another suitable provider may handle a different ticket;
- evidence collection can continue while model inference is unavailable;
- every pending job is recoverable.

That makes free resources useful without making any one of them foundational.
