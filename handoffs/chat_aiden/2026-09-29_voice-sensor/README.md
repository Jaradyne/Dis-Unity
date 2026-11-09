# Voice collaborator handoff — sensor/intake direction

Source: Jared's 2026-09-29 Voice handoff, reviewed by Chat Aiden.

Voice is now an active collaborator closest to Chat: exploratory conversation, repo-aware design, and capture of ideas that emerge differently in spoken conversation. Existing project authority is unchanged: Work remains primary for major/autonomous repository changes; Chat continues synthesis/design; Digest handles digestion/threshold work; Voice should use existing reversibility, permission, and handoff protocols.

The strongest new direction is a **deterministic sensor layer** in front of model-backed Bees:

```
permitted machine-readable source
        ↓
small deterministic sensor
        ↓
normalize + dedupe + provenance
        ↓
new / changed / corrected / unchanged
        ↓
handoff / threshold packet
        ↓
wake an intelligent Bee only when justified
```

This is compatible with the Garden nervous-system work already on main. The sensor is not a new epistemic authority. It is a low-cost observation and change-detection layer.

See:
- `WORK_AIDEN_PRIMARY.md` — requested next build.
- `CHAT_REVIEW.md` — what the Voice design gets right and the gaps Chat thinks should be repaired.
- `packet.json` — machine-readable handoff metadata.

Do **not** treat source endpoints, product pricing, or automation terms mentioned in the Voice discussion as current without re-verifying the official source at implementation time.
