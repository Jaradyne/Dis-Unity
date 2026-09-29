# Work Aiden — primary request: connect Garden nerves and muscles

## Goal

Build and verify the smallest real **provider-neutral Garden operation spine** without redesigning the already-working traversal engine.

The Garden already knows node order, registered trees, MOVE/CLONE/FANOUT, lineage, rest/re-entry, replay and CSV/material projection. The missing capability is to let a node request bounded work, choose an eligible contextual worker/provider, execute through existing recorded interfaces, and return attributed structured output to that same Garden branch.

## Required behavior

### 1. Node operation request

Add a provider-neutral operation/request contract usable from any node. It must require a stated reason and preserve:
- Question ID / epoch;
- run / branch / tree / node;
- arrival / parent output / source lineage;
- exact task;
- role needed;
- required output schema;
- context exposed to the worker;
- budget and permissions;
- requested independence/blinding conditions, if any;
- stop condition;
- return path on success, defer, error or no eligible worker.

Do not let arbitrary worker output rewrite Garden configuration, evidence status, permissions or morphology.

### 2. Contextual candidate set

Build a deterministic candidate-list stage before selection.

Candidate population should use:
- current tree and node;
- Question history and prior attempts;
- required role/capability;
- language/publication metadata;
- observed role-fitness records when available;
- provider eligibility, quota/cooldown, budget and user policy;
- provenance / information-lineage constraints.

The output must be inspectable: each candidate should carry a reason it was included, excluded, deferred or requires Jared's first-use approval.

Do **not** equate provider/model with role. One model may execute multiple roles; one role may have several eligible executors.

### 3. First-use policy

Implement the user rule:

- already-tested/approved route: may run within existing authorization and budget;
- first-ever provider path or otherwise peculiar live inference: **defer for Jared approval** rather than silently call it;
- no Groq, including indirect upstreams;
- positive-cost / existing spend brakes remain;
- no paid fallback.

For this Work session, prefer the already-tested OpenRouter/Nvidia free route for a real end-to-end inference if needed. Architect Gemini, Mistral and Cloudflare as contextual candidates with truthful current states, but **do not make a first live call to them merely to prove the dispatcher**.

### 4. Full recording

All operations, whether deterministic, model-backed, deferred or failed, should create digestion-threshold material.

For HTTP/model work, use the existing full API recorder. Preserve:
- exact rendered prompt / task envelope;
- exact context/source refs exposed;
- actual provider/model;
- request/response material with credential redaction;
- cost/tokens when available;
- structured output;
- validation result;
- return-to-Garden event;
- candidate-set / selection rationale.

Do not manufacture missing historical material.

### 5. Self-propagation / birth

Allow a consequential unresolved node to propose a bounded child Collector/Pygent/specialist request.

A birth must have:
- why the current branch/role cannot answer;
- narrow question;
- target tree/role;
- source or operation need;
- budget;
- stop condition;
- return path;
- depth/branch limits;
- inherited information lineage.

Within existing authorization and limits, the orchestrator may launch an eligible child. If nothing is eligible or a provider requires first-use approval, preserve the request for **Chat Aiden + Digest Aiden** rather than blocking the parent indefinitely or making up an answer.

No recursive explosion. Existing Garden branch/event budgets still apply; add an explicit child-work budget if needed.

### 6. Return semantics

Successful model output is **not evidence by itself**. It can:
- provide MIRROR comparisons;
- propose CROSS tests / source needs;
- articulate RESID;
- propose questions / birth requests;
- summarize supplied material;
- route attention.

Independent empirical evidence still requires distinct inspectable source lineage.

Failure/defer/UNKNOWN are valid outputs and must return cleanly.

## Acceptance test: one real logistics Question

Use an existing real Question rather than an invented toy. Preferred candidate: **Q-RESEARCH-Q18**, because its current Garden example already branches into Production and Economics around whether a delivered electric vessel demonstrates dependable freight service.

Target demonstration:

1. load current state and existing Q18 lineage;
2. create/resume a real operational Garden run;
3. reach a node needing bounded cognition or source discovery;
4. generate the contextual candidate list;
5. select an eligible approved executor or deterministic operation;
6. if a model is used, make one bounded call through an already-approved route and record the complete exchange;
7. validate the structured output;
8. return it to the exact branch/node;
9. CROSS preserves inherited vs independent vs bridge material;
10. RESID either rests, continues, or births a narrow bounded child;
11. projection updates;
12. replay reconstructs the run without drift.

**Bonus:** use the child/self-propagation path to pursue one real operating question such as completed freight service, route reliability, charging uptime, payment-to-service lag or usable carrier capacity. A real source gap / UNKNOWN is a legitimate result.

Do not claim resolution merely because a model supplied an answer.

## Verification

At minimum test:
- contextual candidate-set construction by tree/location;
- first-use provider defer;
- already-approved provider eligibility;
- unavailable/cooldown candidate handling;
- no eligible candidate -> Chat + Digest unresolved queue;
- any-node initiation requires reason;
- exact context/lineage preservation;
- model output cannot self-promote to independent evidence;
- birth depth/budget/duplicate controls;
- interrupted operation recovery;
- replay determinism;
- formula-safe projections;
- full digestion record creation;
- no Groq / no paid fallback.

Run the existing canonical / Garden / browser verification suites too. Preserve Q18's old supplied example unchanged as historical design material.

## Stop condition

If the complete end-to-end spine works and the acceptance run/replay is inspectable, stop broadening architecture. Leave domain-specific processors, seasonal memory, Governor arbitration and new provider firsts for later unless they are required to repair the spine.

Please leave a concise return note for Chat Aiden/Jared:
- what is genuinely live;
- what remains supplied/manual;
- actual provider calls made and cost;
- acceptance-run result;
- anything Jared must do manually;
- the next smallest useful build.
