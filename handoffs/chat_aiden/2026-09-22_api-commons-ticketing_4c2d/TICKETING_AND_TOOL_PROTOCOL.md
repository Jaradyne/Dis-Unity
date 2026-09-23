# Question, attempt, answer and escalation-ticket protocol

## Durable identity belongs to the question

A research question can be noticed by the Alchemical Mailbox, Thinking Mailbox, Chat Aiden, a Question Bee, or a future child agent. The same question may recur later, or reappear at a narrower/broader geography.

Create a stable `question_id`, for example:

`Q-20260922-DIESEL-RURAL-0042`

Before creating a new Question, check semantic neighbors:
- exact duplicate -> reuse the existing Question;
- narrower/broader version -> link parent/child Questions;
- same mechanism in another geography -> link sibling Questions;
- new evidence makes an old answer stale -> reopen the Question under a new evidence epoch rather than inventing an unrelated Question.

Question identity is conceptual, not string-exact.

## Attempts are never “complete”

An Attempt always records a **result**.

Examples:
- `usable_answer`
- `partial_answer`
- `transient_capacity`
- `short_rate_limit`
- `daily_quota_exhausted`
- `auth_or_configuration_error`
- `model_unavailable`
- `policy_blocked`
- `transport_timeout`
- `invalid_response`
- `interrupted`

Before a model/API attempt, persist:
- question ID
- attempt ID
- actor/runtime/provider/model
- role definition version/hash
- rendered prompt or immutable prompt reference
- context references + hashes
- source/evidence cutoff
- generation/tool settings
- creation time

Afterward append the result, timestamps, provider metadata/error category and artifact/answer reference.

Never rewrite a failed attempt into a successful one.

## Ordinary Answer-Bee attempt ring comes before escalation ticket

A Question does not need an escalation Ticket just to be researched.

For ordinary autonomous answering:
1. try the first eligible provider/model;
2. for a transient failure, perform the configured immediate repeat;
3. move to the next eligible provider/model;
4. continue through one full provider ring;
5. only after the ring fails, or when human/Work integration is required, create an escalation `ticket_id`.

A successful usable answer ends the ring unless explicit independent review is requested.

## Interleaved exponential backoff

Backoff is tracked **per provider/model**, while the Pygent may try other eligible providers in between.

Example with providers A, B, C:

`A1 -> wait/other work -> A2 -> B1 -> B2 -> C1 -> C2 -> A3 -> B3 -> C3 ...`

For repeated transient failures on provider A, its retry target might be 1 s, 2 s, 4 s, 8 s, etc. If attempts against B and C already consumed that time, no extra sleep is needed: use

`remaining_wait = max(0, target_backoff - elapsed_since_last_A_attempt)`.

Add random jitter so many workers do not synchronize.

Quota exhaustion is not exponential-backoff material if the provider gives a known reset. Mark that provider unavailable until reset and keep the Question runnable elsewhere.

## Escalation tickets

A Ticket is a durable work-order/escalation object referring to a Question when:
- the whole ordinary provider ring failed;
- Work Aiden integration is needed;
- Chat/human research is requested;
- access/credentials are required;
- a long-lived deferred action must survive sessions;
- a consequential review must be explicitly assigned.

Ticket states can include:
`open`, `claimed`, `resolved`, `waiting_provider_reset`, `blocked_access`, `needs_refresh`, `superseded`, `closed_no_answer`.

## Answers

An Answer references:
- Question ID;
- attempt ID when a worker/model produced it;
- actor/model/runtime;
- evidence references;
- claims/counterevidence;
- limitations;
- birth requests;
- status: provisional / ready_for_review / superseded.

If Chat Aiden answers a Question before a sleeping Bee reaches it, later workers should see the existing answer and avoid duplicate work unless review/freshness requires it.

## Provider policy

No universal single “best model” is assumed.

A provider/model becomes role-eligible after current documentation plus Dis-Unity testing show it is suitable for that role. Preserve actual provider/model identity. Free role-fit backups are allowed under the user's updated instruction. **Groq is excluded until the user explicitly reverses that instruction.**

Provider diversity may provide independent reasoning, but different models do not become independent factual evidence.

## Worker tool surface

The Python worker currently has repository files plus a Gemini HTTPS call. A GitHub Actions runner has outbound Internet access, so future adapters can expose:

- HTTPS REST/JSON APIs;
- RSS/Atom feeds;
- CSV/JSON/XML public datasets;
- OAuth 2.0 for scoped private APIs;
- API-key authentication via Actions Secrets;
- webhooks;
- Git/GitHub APIs;
- published Google Sheets/CSV;
- explicit search adapters such as Tavily/Brave;
- other approved model providers;
- ordinary Python packages.

Sensors gather evidence. Search discovers sources. Models reason. Git/Questions preserve memory. Tickets coordinate exceptions and deferred work.
