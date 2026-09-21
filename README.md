# Resilience Cascade

An operating research workspace for stress → interaction → opportunity → adaptation → resilience.

Cycle RC-001 started on 20 September 2026. Six specialist agents contributed early research and exchanged findings with a coordinating intake/modeling thread. A shared usage limit ended their turns before final reports and full cross-review. The coordinator continued, verified the key claims and completed this bounded first cycle. The independent final skeptic pass remains incomplete and is queued for the next cycle. Twelve requested roles are assigned across the research threads. All evidence is public; no private accounts, personal threat profiling, outbound contacts or subscriptions are used.

## What runs

The coordinator launches tool-enabled specialist agents, passes a shared checkpoint to them, requests focused follow-ups where signals intersect, obtains a skeptic review, and commits reviewed results to common state. This first cycle performs those steps. Agents do not run between conversations. Persistent files support the next active research cycle; they are not an unattended monitoring service and no schedule has been created.

## Canonical state and views

`Resilience_Cascade_STATE.json` is the machine-readable source of truth. Its ten required sections are SYSTEM_MAP, ACTIVE_SIGNALS, CASCADE_GRAPH, RESERVES_AND_LIFEBOATS, ISLANDS_OF_STABILITY, TRANSITION_OPPORTUNITIES, COMMUNITY_COMMONS, QUESTIONS_TO_WATCH, SOURCE_LEDGER and CHANGELOG. The `state/` Markdown views are generated from those sections. The executive briefing is the readable entry point. Reports contain supporting detail; the inbox holds attributed agent submissions and reviews.

Only the coordinator commits canonical state. Agents write their own inbox files, read the common checkpoint and peer submissions, and exchange specific findings. This avoids competing edits while allowing disagreement to remain visible. Each merge retains sources, epistemic labels, dates, provenance, limitations and changes in status.

## Resume without asking the user to maintain records

1. Resolve and read the current Resilience Cascade state and latest project bundle. Preserve existing file identities when updating them. Read the most recent changelog; do not recreate a first baseline.
2. Set an explicit research cutoff and a new cycle ID. Reopen dynamic sources for the attention queue. Distinguish observation date, publication date, retrieval date and model horizon. Older evidence remains a dated structural baseline.
3. Launch specialist agents for unanswered consequential questions. In this environment, use the collaboration tools; scripts in this bundle validate and render state but do not call an AI service by themselves. Group lightly active roles and allocate additional concurrent work to interacting, independently evidenced signals.
4. Use common state to exchange findings. A new signal must identify what it changes: magnitude, mechanism, buffer, threshold, implementation, reversal or confidence. Repeated headlines about one event count once. A missing public indicator is a coverage gap, not reassurance or alarm.
5. Ask the skeptic to review every material warning and claimed reserve. Update or retire hypotheses explicitly, preserving earlier status and the reason for change. Keep improving evidence beside worsening evidence.
6. Commit the ten sections, run `python3 scripts/validate_state.py Resilience_Cascade_STATE.json`, regenerate views with `python3 scripts/render_state.py Resilience_Cascade_STATE.json`, and issue the briefing. Save updated state and bundle with version history.

## Role registry

| Requested role | First-cycle execution |
| --- | --- |
| Signal Intake | Coordinator + source ledgers in each thread |
| Energy & Diesel | energy_logistics |
| Food / Fertilizer / Agriculture | food_trade |
| Infrastructure | infrastructure_health |
| Economic / Industrial | skeptic_industry, with independent reconnaissance before review |
| Social Temperature | networks_social |
| Geographic Context | local_commons (SF/Bay Area/California), networks_social (international), coordinator (nested integration) |
| Cascade Modeler | Coordinator, drawing on specialist mechanisms |
| Skeptic / Red-Team | skeptic_industry + coordinator admission review |
| Resilience / Overflow | Mandatory lens in every thread; coordinator reserve gates |
| Islands of Stability | networks_social + sector-specific reserve records |
| Commons | local_commons + practical interventions from all threads |

The skeptic's dual assignment is disclosed: evidence they originated is independently checked by the coordinator or another specialist. Agreement between agents repeating one source is not independent corroboration.

## Evidence and activation rules

FACT describes a supported observation or the existence of a forecast, not realization of that forecast. PLAUSIBLE MECHANISM is a conditional causal link. EARLY SIGNAL is a preliminary indicator. UNKNOWN marks an unanswered question. SPECULATION is excluded from operational warnings unless explicitly discussed as a scenario.

Source grades: A = direct primary record or measurement; B = authoritative analysis/identified secondary account; C = lead needing corroboration. Source grade does not determine confidence on its own. Official forecasts remain forecasts. Working capacity must be separated from authorized, financed, announced, under-construction and projected capacity.

Every consequential cascade identifies initiation, affected system, mechanism, evidence, buffers, thresholds, substitutes, horizon, uncertainty, confirming observation and falsifier. Status is observed link, conditional watch, not established, downgraded or retired. Thresholds are analyst decision rules unless a source establishes an operator trigger; they are not predicted probabilities.

No composite resilience or collapse score is used. Separate descriptive gauges cover load, reserve, recovery, dependency, substitutability, shedding, growth, lifeboat, social temperature and confidence. Unknown gauges remain unknown. Geography-specific risks are not generalized nationally.

## Overflow and donor rules

Protect essential function: detect, redistribute, substitute, shed safely, isolate, operate in degraded mode, use lifeboats, recover. Shedding nonessential trips or avoidable waste differs from denying mobility, food or treatment. Essential service loss must not be relabeled a healthy transition.

A proposed donor must retain its protected minimum, operating reserve and credible replenishment time. Exportable help is at most verified available capacity minus committed local needs and protected contingency reserve, further limited by route, staffing, fuel, permissions and recipient compatibility. Unknown reserve means candidate support, not committed rescue capacity. Check whether donor and recipient fail under the same hazard.

Every major decline gets a transition record: function to preserve, released assets (verified or merely possible), safe demand reduction, growth candidate, conversion requirements, lead time, adverse effects and evidence. Do not book released labor/buildings/capital before they actually become available.

## Coverage and privacy

Public-source reconnaissance is incomplete. It cannot establish live facility inventories, staffing rosters, accessibility or partner commitments without operational confirmation. We do not publish sensitive facility weaknesses, investigate private individuals, infer hostile intent from correlated failure, or classify populations as dangerous. Social evidence distinguishes rhetoric, organization, capacity, behavior and violence and tracks de-escalation with equal care.

The included commons cards are research-backed proposals, not agreements, purchases or messages sent on the user's behalf. A practical next cycle should resolve the most important gaps before expanding scope.
