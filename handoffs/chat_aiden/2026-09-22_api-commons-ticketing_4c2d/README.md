# Chat Aiden contribution — API capacity, ticketing, and commons mapping

**Base commit:** `51e0969691b3637f7cac9efab38b4596043658b4`  
**Base cycle:** RC-004 (closed)  
**Actor:** Chat / OpenAI / GPT-5.6 Sol  
**Status:** ready_for_review  
**Created:** 2026-09-22 UTC

## What changed

This packet proposes:

1. a provider-neutral ticketing system that keeps a question, every attempted worker call, every answer, and later superseding work linked without requiring one model to stay alive;
2. a wider Python-worker tool surface built from ordinary Internet protocols instead of treating Gemini as the worker itself;
3. a role-fit model policy: multiple models/providers may be eligible when they are genuinely suitable for a bounded role, while silent downgrades remain prohibited;
4. a commons metabolism record with qualitative participation language only;
5. an Oakland Commons Mapper role that may request child mappers for other geographies and eventually feed continental/global geography-logistics synthesis without erasing local provenance;
6. source copy for a printable tri-fold brochure: “You can begin with a table, shade, some tools, food, and people who like being there.”

No closed-cycle records or canonical state are changed. No API call is executed by this packet.

## User direction reflected

- Free API use should not be artificially throttled merely because it is free. Provider quotas/capacity still need respectful retry and recovery behavior.
- “Best” means fit for the work, not necessarily one globally strongest model. More than one suitable agent/provider can therefore be attempted, with actual model identity preserved.
- Questions answered by Chat Aiden or another worker should resolve the same ticket rather than creating an orphan answer.
- Commons participation is not head-count surveillance. Qualitative observations range from **a few** through **crowds upon crowds** with no hidden numeric conversion.
- Local commons mapping should grow outward from Oakland only as useful, while keeping the local mapper authoritative for local facts.
- **NO GROQ:** provider is vibe-banned until the user explicitly reverses that instruction; do not call or hide it behind an aggregator/fallback.
- Question/Scout Bees should remain useful with ordinary source sensors even when higher-level model capacity is unavailable.

## Files

- `TICKETING_AND_TOOL_PROTOCOL.md`
- `ticket.schema.json`
- `COMMONS_METABOLISM.md`
- `oakland_commons_mapper.json`
- `posters/START_WITH_A_TABLE_TRI_FOLD.md`

## Work handback

Work Aiden can review these as interfaces, move approved pieces into their durable homes, add runtime tests, and connect provider/search/feed adapters. The most consequential next runtime step is to make ticket creation/claim/answer/defer idempotent before adding more providers.
