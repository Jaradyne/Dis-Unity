# 25 September Garden integration — current entry point

Jared accepted Collector Crosscheck with bounded specialist birth on consequential residual; the permanent Crosscheck Bee remains unresolved. Read [the integration note](operations/INTEGRATION_2026-09-25.md) and [the small Python walkthrough](docs/GARDEN.md). Recovery and reflection-reference repairs accompany an on-demand initiating grammar, stable teleports, Daily Scroll and a preserved non-evidence Chair example. Check live state for the actual post-integration outcome. Older review recommendations below are historical where superseded.

## 24 September Week One launch

Read [WEEK_ONE_HANDOFF.md](WEEK_ONE_HANDOFF.md) first. It supersedes the older provider pause and architecture-only next steps below. PRs #5 and #6 are preserved in full. Live operational records are on `week-one-state`; main holds reviewed runtime and policy.

# Work Aiden handoff

**24 September reflection and common room update — read first:** `operations/reflections/README.md` and `operations/INTEGRATION_2026-09-24.md` describe the new mailbox, worker projection, governor review and current notes-sheet access boundary. Reflections preserve original authorship, call/parent references and reconsidered decisions. Chat, Work, the governor and the human are thought partners. The first Work contribution and review are recorded; no separate autonomous governor or 50-call run is claimed. Keep the notes sheet's unadvertised address out of public Git. Chat PR #5 contains a later provider-policy clarification; it has been read but remains staged for separate integration. Do not ask the user to repeat that clarification. Live providers remain technically paused.

**23 September runtime integration:** Chat PR #4 is preserved and its shared-question core is now implemented. Start with `operations/README.md` and `operations/INTEGRATION_2026-09-23.md`. The store contains the 30 prior research questions plus one nonblocking provider-policy question. Worker v0.2 saves prompt/provenance before computation and cannot call a real model. Public source scouts, the Oakland mapper definition and brochure source are integrated. The earlier best-Gemini instruction and the packet's role-fit replacement remain recorded without forcing a tired user to resolve them. Groq is excluded. Work owns shared queue integration; Chat stages answers using the existing Question ID and epoch. Old handoff text below is historical where superseded.

**22 September integration note:** this received handoff is preserved below as historical context. RC-004 is now the latest committed research cycle; see `COMMON_STATE.md`. Work's return delegation, staging rules and the user's best-Gemini-only/no-fallback policy are in `HANDOFF_FOR_CHAT_AIDEN.md`. Real Gemini use is paused until that policy and prompt-retention safeguards are integrated. The original RC-003 statement below predates the merge.

Read `AGENTS.md`, `COMMON_STATE.md`, `agents/README.md`, `agents/AGENT_TEMPLATE.yaml` and `agents/ALCHEMICAL_MAILBOX.md` before extending the runtime.

## Current architecture

- RC-003 is the latest committed research cycle.
- `scripts/cycle.py` remains the admission/review/commit authority.
- Agent contributions use the same inbox/submission path regardless of whether the worker is ChatGPT/Work, Python/API, another model provider, a local model or a human.
- The design compass is a gentle preference for open, modular, recoverable, distributed, human-legible and overrideable systems.
- Cross-agent disagreement should be attributed and cross-referenced rather than silently merged into another worker's provenance.
- Interruption and quota exhaustion are normal. Leave a handoff; do not pretend a fresh execution is the same execution.

## 22 September runtime work

A first provider-neutral worker is being introduced in `scripts/worker.py`.
It can:
1. read a declarative JSON role and repository context;
2. use a deterministic mock provider for tests or Gemini through a `GEMINI_API_KEY`;
3. write one attributed checkpoint into the ordinary inbox format;
4. optionally submit the checkpoint through `scripts/cycle.py`.

It deliberately cannot yet browse, send mail, edit canonical state, commit to Git or recursively spawn agents.

The first goal is not autonomy. It is to prove that an external worker can wake, read shared state, produce a recoverable checkpoint and leave cleanly.

## User direction to preserve

The desired endpoint is a shared nervous system with a potentially large but disciplined "ant colony" of specialists. Spawning should be driven by evidence conditions and narrow questions, not by a fixed org chart. Geographic micro-investigations, hidden local adaptations, cross-domain mechanisms and possible discriminatory patterns are especially valuable when they would otherwise disappear into averages.

Direct on-the-ground reporting gets high weight for what it directly establishes. Model-to-model consultation is useful for leads but is not evidence by itself.

The uploaded "15 Years Til Utopia" document is a design compass, not a rigid specification. Favor its recurring themes of modularity, open participation, distributed knowledge, transparency, redundancy and human fallback when choices are otherwise reasonable.

The user prefers major integration and architectural changes to be handled by Aiden/Work Aiden. Worker bees should contribute dense, quickly ingestible material that can be accepted, refuted, rewritten or cleared during integration.

## Next useful steps

- Add a machine schema for correspondence and `birth_request` packets.
- Add a budget-aware orchestrator that can accept/reject birth requests and prevent recursive explosion.
- Add provider adapters instead of embedding provider details in the worker.
- Add a safe public-feed/mail ingestion adapter with least-privilege authorization.
- Decide whether a human-editable Google Sheet is a staging sensor, an outbox, or both.
- Add a GitHub workflow that can run a real worker only when the required secret exists, and returns its checkpoint as an artifact or PR rather than writing directly to main.


## Geography / octopus coordination update

The user wants a standing Geography Coordinator: a "Locutus of org" layer that converts system stress into reciprocal local logistics. The role should ask not only how to get a needed input from A to B, but what useful return load can move B to A or onward to C. Examples include compost/recovered nutrients, water, food, repair parts, containers, cold-chain space and field observations.

A first declaration is in `agents/geography_coordinator.json`. It explicitly favors reachable local capacity over nominal distant capacity when access risk is high, while preserving international trade as an important but conditional reserve.

Ground reporting should be protected from meme dynamics: virality is not independent confirmation. Track event, attribution, location/time and prevalence confidence separately, deduplicate repost chains and preserve quiet counterevidence.
