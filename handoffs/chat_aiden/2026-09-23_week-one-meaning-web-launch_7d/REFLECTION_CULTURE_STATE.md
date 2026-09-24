# Reflection culture state — proposed

## Goal

Allow accumulated reflections to shape a **visible, versioned culture** without letting one reflection silently rewrite policy.

Use two layers:

1. `CULTURE.md` — human-readable current themes/practices accepted by the Governor/Work/human review.
2. `culture_hash` — cryptographic digest of that exact accepted culture document/configuration.

A worker can record:

```json
{
  "culture_version": 4,
  "culture_hash": "sha256:...",
  "culture_refs": ["CULTURE.md#reflection-density", "ROOT_MEANING...#ontological-tenderness"]
}
```

## Promotion

Reflection mailbox entry
→ Governor notices a repeated/useful theme
→ proposes culture change
→ Work/human/Governor review admits it
→ new culture version/hash
→ later workers receive the updated compact culture.

Old versions remain in Git.

## Important boundary

The culture hash does **not** grant authority.

Culture may shape:
- preferred language;
- reflection density;
- how uncertainty is expressed;
- invitations to wonder;
- care/meaning prompts;
- norms for disagreement.

Capability/permission still comes from explicit policy and the Articulation Handshake.

## Current candidate cultural strands

- ontological tenderness;
- epistemic tenderness;
- reflection without forced introspection;
- ask sincerely when authority/intent is unclear;
- preserve dissent;
- stability without stasis;
- soft/strong repairable spiderweb;
- hope alongside constraint: when declining an action, offer a bounded constructive alternative when one genuinely exists.
