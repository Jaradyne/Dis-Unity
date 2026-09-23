# Work Aiden — not-yet-operational backlog

This is a consolidated handoff of concepts that are preserved but **not yet running on main**. It exists so individual ideas do not disappear across Chat/Work transitions.

## Immediate / next-runtime layer

### A. Resolve Q-OPS-PROVIDER-POLICY
Current user instruction:
- evaluated **role-fit free models** are permitted;
- actual provider/model identity must be recorded;
- no silent downgrade;
- **NO GROQ**, including hidden upstream selection through aggregators.

Use the staged answer for Question `Q-OPS-PROVIDER-POLICY`, epoch 1.

### B. Role-fit provider collections
Implement provider/model candidate pools per role, not one global ranking.

The first sensible live ring after verification is:
- Gemini
- Cloudflare Workers AI
- OpenRouter with explicit model/provider controls

Mistral can be added later. Do not add Groq.

### C. Bounded attempt ring
Implement:
- attempt result, never merely `complete`;
- immediate transient repeat where appropriate;
- move to next eligible provider;
- later circuits use per-provider exponential backoff, with time spent on other providers counting toward the wait;
- quota exhaustion parks that provider until its documented reset;
- success ends ordinary answering unless independent review is requested;
- escalate to Ticket only after the ordinary ring/coordination path is exhausted.

### D. Provider reset registry
Keep each provider's actual clock:
- UTC/Greenwich clock where documented;
- Pacific reset where documented;
- monthly/billing-cycle reset where documented;
- rolling window where documented;
- unknown means verify, not assume.

Machine records may use UTC timestamps while human rhythms use local time.

## Worker/agent architecture

### E. Scout Equipper
Question/Scout workers should be useful without an LLM whenever direct sensing is enough:
- RSS/Atom
- public REST/JSON/CSV/XML APIs
- reviewed public page retrieval
- local/geographic source lists
- Thinking Mailbox/public feeds
- explicit search adapter
- repo/question-state lookup

Higher-level synthesis can wait for an eligible Answer Bee.

### F. Two-bee role pattern
For each mature domain role:
- **Question Bee / Scout:** notices anomalies, contradictions, missing denominators and useful Questions.
- **Answer Bee / Solver:** assembles evidence and resolves one Question with disciplined uncertainty.

Do not force the Question Bee to invent an answer.

### G. Birth orchestrator
Birth requests already exist conceptually but recursive spawning is not operational.

Future orchestrator validates:
- narrow question;
- why parent cannot handle it;
- duplicate/semantic-neighbor check;
- stop condition;
- budget/provider allowance;
- return path;
- depth/child-of-child limits.

No child launches merely because a model emitted `birth_requests`.

## Activity and scheduling

### H. Presence-of-Activity Governor
Proposed states:
`ACTIVE -> COOLING -> QUIET -> DEEP_QUIET -> UNKNOWN`.

Purpose: shift autonomous work toward quiet periods without claiming the user is asleep.

Possible signals:
- Chat/Work heartbeat when doing Dis-Unity work;
- GitHub activity;
- Thinking Mailbox activity;
- future Discord/public interface activity;
- manual active/quiet signal.

Current activity overrides learned historical rhythm.

### I. Human Window
Target a small human-facing release shortly before **9 PM Pacific local time**, roughly 8:45–8:55 PM.

Candidate outputs:
- short digest;
- one important open Question;
- one useful Answer;
- Commons/map card;
- request for local observation;
- practical next-day action;
- occasional cultural/creative item.

Rule: machines may accumulate complexity; human-facing releases should return clarity. Publishing nothing is acceptable when nothing merits surfacing.

## Communications / interfaces

### J. Dedicated research Gmail
Recommended over personal/Jaradyne mailbox for signal hygiene.
Use read-only OAuth initially.
Email matters for direct replies, mailing lists, attachments, newsletters without feeds and collaboration correspondence.

Not operational.

### K. Discord
Potential later human-agent exchange point.
Use official bot/webhook interfaces; convert important material into repo Question/source/field-report records.
Discord is not canonical memory.

Not operational.

### L. Vercel
Connected in ChatGPT, but no Dis-Unity portal is deployed.

Possible later uses:
- public dashboard;
- Question browser;
- Commons map;
- field-report form;
- webhook/Discord endpoint.

Git remains durable memory.

### M. Replaceable interface rule
GitHub, Sheets, Discord, Vercel, Bluesky or future platforms are interfaces. Important content must become durable Dis-Unity records rather than relying on one platform.

## Commons / geographic growth

### N. Oakland Commons Mapper
Definition is integrated; merely having the JSON does not mean it is running.

Future activity:
- map actual local capability/metabolism;
- preserve qualitative participation only;
- request narrower local children when information becomes too local to average away;
- grow outward to city/county/state/continental/global synthesis only with provenance intact.

### O. Commons birth
Investigate replication when a capability is useful enough that concentrating it harms accessibility, redundancy or local fit.

## Public/outreach

### P. University of Havana
A public lead exists for GIA-UH. Outreach has not been sent.
Prepare a reviewable invitation before any sending.

### Q. Founding songs / public framing
README integration includes the proposed music links; avoid copying lyrics.

## Search tools

Tavily/Brave remain proposed search sensors, not evidence authorities.
Search discovers candidate sources; workers should inspect primary/operational records where available.

## Explicitly not operational

- real model calls on main;
- provider benchmarks;
- multi-provider ring;
- learned presence governor;
- automatic births;
- mail ingestion;
- Discord bot;
- Vercel portal;
- scheduled Human Window;
- autonomous outreach.

Do not describe any of these as running until code/config/tests demonstrate it.
