# Week One output contract

The autonomous week should produce **small pieces that compose**, not a monolith.

## Directory concept

```
operations/week-one/
  INDEX.md
  run-manifest.json
  days/
    2026-09-XX/
      discovery.json
      questions.json
      attempts/
      answers/
      reflections/
      governor-review.json
      HUMAN_NOTE.md
  final/
    WEEK_ONE_DIGEST.md
    CHAT_INDEX.md
    PROVIDER_NOTES.md
    REFLECTION_THEMES.md
```

Exact paths may change during implementation; preserve the semantic separation.

## CHAT_INDEX.md

Designed specifically for future Chat sessions.

Each item should have:
- Question ID;
- one-sentence reason it matters;
- status;
- evidence cutoff;
- best packet to read first;
- unresolved point;
- suggested next bounded conversation/research task.

The user should be able to say:

> "Pick up item 7"

without needing to reread the whole system.

## Human readability

Backend packets may be structured/dense.

Human-facing notes should answer:
- What changed?
- Why might it matter?
- What did not happen?
- What is still unknown?
- Is there something useful to do/think about next?

If the answer is "nothing important changed," say that plainly.

## No forced volume

A quiet day is not a failed day.

The system should not manufacture novelty to justify being scheduled.
