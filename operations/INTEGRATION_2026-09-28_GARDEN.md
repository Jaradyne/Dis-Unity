# Digest integration and first traversal runtime

Author: Work Aiden, ChatGPT/Codex session, September 28, 2026.

Authority: Jared asked Work to inspect Digest Aiden's integration and begin fleshing out the system. Base main: `ebe4f261afc51b691e46fe463f9a81c9a74cfe66`. Digest PR #24 head: `6cc0593ff007c9ec181f00c0bb6436e95d69b546`; this integration descends from it and preserves its contribution history.

Digest's roadmap identifies the immediate gap correctly: the old Garden validates a supplied complete pass but cannot retain partial movement, branch, or continue from a checkpoint. The new runtime implements that first slice with supplied content. Read [the walkthrough and operating contract](../docs/GARDEN_TRAVERSAL.md).

Integrated from Digest: the Saṃskāra Morphology registry and proposed powers, bounded Governor review context, Customs Authority archetype, and expanded Garden roadmap. Work adds per-node contracts, saved traversal state, deterministic MOVE/CLONE/FANOUT, explicit route decisions, child provenance, rest/resume/new-arrival transitions, replay, and a CSV/material projection for digestion. Language glances and MIRROR information lineage are required records. They are not automated interpretation.

The Q18 worked example carries existing design material into INIT, Production and Economics; its children await supplied ARRIVAL content. It is a reproducible demonstration on main, not a newly dispatched research run. Actual future run records belong on `week-one-state`, and the state copier now includes those optional data folders without importing runtime code. Existing Week One workers are not yet connected to Garden traversal.

Validation covers continuation and replay, duplicate/stale commands, shared budgets, all-or-nothing fanout, repeated-route prevention, inherited evidence, language unknowns, changed arrivals, checkpoint-before-projection recovery, changed Question epochs, formula-safe CSV output, optional state-folder migration and concurrent state updates. CI also reconstructs the committed example. The canonical RC-004 research and completed cycle remain unchanged.

Next: implement the provider-neutral operation boundary using the existing credential-redacted API recorder and these input/output contracts. Preserve prompt, source, test and answer lineage. Then add domain-specific processing and memory reuse records. Continue without a Governor; proposed powers, autonomous routing and new provider permissions remain inactive.

Work reflection: a useful branch is a new function with a visible inherited history. Multiplying branches or model names does not multiply evidence. Unknown observations, quiet rest and interrupted projections all need usable continuation paths, not invented conclusions.
