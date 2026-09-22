# Shared-document update proposal for Work Aiden

Base commit for this Chat packet: `51e0969691b3637f7cac9efab38b4596043658b4`.

This file proposes exact concepts to integrate into shared documents. Chat does not edit the shared files directly under the current handoff rules.

## AGENTS.md — ticket discipline

Add a short operating rule near the checkpoint/handoff rules:

> Every bounded research question should carry a stable ticket ID once it enters the worker queue. Before starting work, check whether the ticket is already answered, claimed, superseded, stale, or deferred. An answer from Chat, Work, a Python worker, another model, or a human resolves the same ticket rather than creating a parallel orphan result. Provider errors are attempt records, not answers. Do not repeat answered work unless independent review or freshness requires it.

## HANDOFF_FOR_CHAT_AIDEN.md — Chat ticket behavior

Add under Division of work / Return format:

> Before researching a queued question, check its ticket status. If Chat can answer it, attach the answer to that ticket and mark it ready for Work review. If another worker already answered it, do not redo the task unless the ticket requests review or freshness has expired. Chat may create ticket proposals and answer packets but should leave queue/orchestrator integration to Work.

## WORK_AIDEN_HANDOFF.md — integration responsibility

Add:

> Work owns durable ticket admission and queue/orchestrator integration. When integrating a Chat or worker answer, preserve the ticket ID, attempt history, provider/model identity, source cutoff and supersession links. Work should not rerun an answered ticket merely because a different model was originally intended.

## ideas/COMMONS_GROWTH_PATH.md — energy wording

The current distilled document does **not** list “clean coal” as an operating power pathway. It mentions “zero-waste coal” only in the section rejecting older unsupported assertions. Preserve that distinction.

Suggested refinement:

1. In practical/long-horizon capability language, add **biological resource-to-energy systems** where locally appropriate:
   - anaerobic digestion / biodigesters using manure, food waste, wastewater solids, fats/oils/grease, or compatible organic residues;
   - biogas for heat, electricity, combined heat and power, or upgraded renewable natural gas;
   - digestate/nutrient recovery with contamination and nutrient-balance controls;
   - algal ponds/photobioreactors as research/coproduct/biofuel systems where water, nutrients, harvesting and economics make sense.

2. Do **not** present “clean coal” as an ordinary commons power option. Carbon capture at coal plants is technically real, but capture is not equivalent to eliminating mining impacts, all air pollutants, water use, cost or energy penalty. Keep coal+CCS only as a separately evaluated industrial/long-horizon research pathway if it remains relevant.

Suggested replacement for the old-assertions bullet:

> **Coal with carbon capture, fusion, graphene applications, airships and lunar launch infrastructure:** carbon capture from coal flue gas is technically demonstrated, but that does not make coal generically “clean” or establish local feasibility, cost, lifecycle emissions or resilience value. Treat coal+CCS, fusion, graphene, airships and lunar infrastructure as separate long-horizon research proposals whose actual mechanisms must be tested before admission as reserves or operating plans. Biological systems such as anaerobic digesters are already real operating technologies and should be assessed separately on local feedstock, safety, maintenance, nutrient and economic conditions.

## Poster destination

When Work integrates the brochure, preferred durable destination:

`posters/START_WITH_A_TABLE_TRI_FOLD.md`

The generated visual currently exists in the Chat conversation; the staged repository contains the editable text source only.
