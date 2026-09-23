# Agent definitions

**23 September operating update:** `../operations/README.md` describes shared questions and recoverable attempts. Reuse Question IDs and evidence epochs; a ticket is an escalation, not a prerequisite for asking. The Oakland mapper is now an available role definition. Public RSS/Atom scouts can operate through explicit commands without a model. Live model execution remains paused pending reconciliation of the old Gemini instruction and newer role-fit proposal; Groq is excluded. No automatic worker spawning or schedule is enabled.

For work allocation and contribution boundaries, read [HANDOFF_FOR_CHAT_AIDEN.md](../HANDOFF_FOR_CHAT_AIDEN.md). Effective provider status and the pending policy decision are in [operations/README.md](../operations/README.md). Retained task material is in [GEMINI_RESEARCH_PROMPTS.md](../handoffs/deferred_prompts/GEMINI_RESEARCH_PROMPTS.md).

Dis-Unity may be approached by ChatGPT/Work agents, API-driven Python workers, other model providers, local models, humans, or future runtimes. They should not need provider-specific code in order to understand the role they are taking.

The declarative template in `AGENT_TEMPLATE.yaml` describes a role's mission, beat, permissions, inputs, outputs, correspondence behavior and continuity rules. It is a contract for the worker, not a script for its reasoning.

A worker may be highly open-ended inside its beat. Unexpected relevant leads, counterevidence and cross-domain connections are welcome. The shared rules are: preserve provenance, checkpoint early, use the same cycle submission path, do not silently rewrite a peer's work, and leave enough state for another worker to continue after interruption.

## Shared inbox

Python/API workers do not need a separate evidence channel. They may write the same cycle inbox/submission format used by any other agent, subject to the current cycle schema and `scripts/cycle.py`.

Cross-agent correspondence should reference the claims, source IDs, edges, reserves or prior messages it addresses. Prefer explicit kinds such as `support`, `challenge`, `correction`, `question`, `handoff` and `synthesis`. A disagreement is new attributed information; it is not permission to edit another worker's provenance.

## Design compass

When two otherwise reasonable implementations compete, gently prefer the direction already present in the project's guiding material: open over closed, modular over monolithic, recoverable over brittle, distributed knowledge over privileged knowledge, human-legible state over opaque scoring, multiple access modes over one mandatory interface, and human override over inaccessible automation.

This compass is a tiebreaker and design orientation. It never substitutes for evidence, safety, legality, feasibility or an explicit user instruction.
