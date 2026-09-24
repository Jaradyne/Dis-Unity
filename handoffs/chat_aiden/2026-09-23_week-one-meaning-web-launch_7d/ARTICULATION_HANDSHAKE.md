# Articulation Handshake — capability driver's ed in code

## Purpose

High-capability systems should not receive more authority merely because a user or upstream agent can phrase a command.

Before capability crosses into consequential action, require an **articulation handshake**: a compact, machine-checkable statement of what is intended, what authority exists, what could be affected, how to stop, and how to verify.

This is not a license to have ordinary conversation with AI. It is closer to **driver's ed for operating a very large vehicle**: higher capability asks for clearer articulation.

## Intent envelope

Suggested fields:

```json
{
  "intent_id": "INTENT-...",
  "actor": "human | chat | work | governor | agent",
  "goal": "What outcome is being sought?",
  "why": "Why does this matter?",
  "scope": ["What systems/data/people may be touched?"],
  "authority": ["What is this actor actually allowed to change?"],
  "affected_parties": ["Who/what could experience consequences?"],
  "non_goals": ["What must not happen?"],
  "reversibility": "reversible | partly_reversible | hard_to_reverse",
  "stop_conditions": ["When should the system stop and ask?"],
  "verification": ["How do we know the intended action happened?"],
  "uncertainty": ["What is not known?"],
  "reflection_required": true
}
```

## Capability classes

### Class 0 — converse / explain
No handshake beyond ordinary user intent.

### Class 1 — public read-only sensing
Question/source purpose + bounded destination is enough.

### Class 2 — autonomous research / model spending within approved free budgets
Stable Question, source scope, provider policy, attempt budget and stop condition.

### Class 3 — external write / communication / deployment
Require full intent envelope and explicit authorization appropriate to the action.

Examples:
- send an email;
- post publicly;
- deploy a public service;
- modify an external account;
- change permissions;
- alter canonical state.

### Class 4 — high-consequence / hard-to-reverse
Require explicit human/Work/Governor review and additional domain-specific safeguards.

## "License" as learning, not gatekeeping

A future human-facing course could teach:
- goal vs command;
- authority vs capability;
- reversible experiments;
- prompt injection and untrusted data;
- provenance;
- uncertainty;
- stop conditions;
- how to ask an AI to challenge the operator's framing;
- how to recognize when the system should ask instead of act.

Completion could unlock convenience features in a private deployment, but Dis-Unity should avoid pretending a quiz makes someone morally qualified.

The durable mechanism is the **intent envelope + capability gate**, not a badge.

## AI-side duty to ask

A capable worker should ask sincerely when:
- authority is ambiguous;
- affected parties are unclear;
- the requested action is difficult to undo;
- user intent conflicts with standing policy;
- evidence is inadequate for the consequence;
- a safer bounded experiment can answer the same question.

The right question is part of competence, not failure.
