# Work Aiden handoff

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


## 22 September — diesel escalation, pandemic lens, and first Gemini bee

New user direction:
- Treat reserve stacks as normal and explicitly estimate access as well as existence.
- Maintain a COVID-like pandemic/lockdown stress parameter at several stages, especially for systems whose behavior changes sharply under movement restrictions, absenteeism or priority allocation. This is a scenario lens, not a prediction.
- Add medical refrigeration/cold-chain dependencies to diesel analysis.
- Track farm failures/bankruptcies, food/industrial output effects, distressed land transfers and changes in ownership/operating concentration without assuming motives.
- Treat extra human labor as a possible bounded adaptation, not a magical replacement for broadacre mechanization.
- Create a U.S. rural logistics scout focused on places too far from rail/water or too poor for expensive trucking. It should birth bounded place/corridor children when warranted. Once the schema works, analogous national/local scouts can appear elsewhere; several continental syntheses may jointly propose a dormant global logistics synthesis agent.
- Gemini current-event reasoning should be supplied with dated evidence from 2025-01-01 onward; do not ask it to recall post-cutoff events from model memory.

Files added in this pass:
- `scenarios/PANDEMIC_LOCKDOWN_LENS.md`
- `agents/us_rural_logistics.json`
- `agents/global_logistics_synthesis.json`
- `briefings/CURRENT_PACKET_2026-09-22.md`

The user created the repository Actions secret `GEMINI_API_KEY` under a free-tier Gemini project. A one-shot Gemini 3.8 Flash run is being used to test the real external-model path. Its output should remain an attributed inbox/checkpoint contribution, not canonical truth.
