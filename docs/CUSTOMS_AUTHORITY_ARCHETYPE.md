# Customs Authority archetype — jurisdiction, entry point and observed enforcement

Status: **design archetype; not a running Bee/tree and not a global enforcement claim.**

Customs recurs often enough across trade, logistics, sanctions, law, diplomacy, production and resilience work that it should not be rebuilt from scratch for every Question. The recommended shape is a reusable archetype instantiated by jurisdiction and then by actual port/entry-point.

The archetype supplies **questions and evidence fields**. Each instance must supply its own current law, agency, procedure, language surfaces and observations.

## Inheritance shape

```text
CUSTOMS AUTHORITY ARCHETYPE
        |
        +-- CONTINENT / MACRO-REGION COVERAGE
        |       |
        |       +-- NATIONAL / CUSTOMS-UNION JURISDICTION
        |               |
        |               +-- REGIONAL / STATE / PROVINCIAL INTERFACE
        |                       |
        |                       +-- CITY / PORT-OF-ENTRY INSTANCE
        |                               |
        |                               +-- seaport
        |                               +-- airport
        |                               +-- land crossing
        |                               +-- rail terminal
        |                               +-- inland / dry port
        |                               +-- postal / express gateway
        |                               +-- free-zone / special-regime gateway
        |
        +-- TREATY / CUSTOMS-UNION / SPECIAL-REGIME OVERLAYS
```

The coverage registry should be able to represent **Africa, Asia, Europe, North America, South America, Oceania and an Antarctica special-case logistics/gateway overlay**. Antarctica should not be forced into ordinary national-customs assumptions; any gateway/operator/jurisdiction relationship there must be separately sourced.

No single pass needs to populate every entry point. The architecture is global; instances can be added incrementally as Questions make them relevant.

## Shared Customs questions

Every jurisdiction/entry-point instance can ask:

- Who has legal customs/border authority here?
- Which law, regulation, treaty, union rule or special regime controls the function?
- What goods/classification/valuation rules apply?
- Which exemptions, quotas, de minimis rules or special regimes matter?
- Which agency actually performs inspection, clearance and enforcement?
- Which other agencies share the port-of-entry function?
- What filing, manifest, digital-clearance or pre-arrival systems are required?
- What appeal/review process exists?
- Which emergency, sanctions, export-control or security overlays alter ordinary flow?
- What anti-corruption, audit or integrity controls exist?
- Which trade-facilitation obligations or service targets exist?
- What happens when the national rule meets a regional/state/provincial or city/port operator?

The archetype should link outward rather than absorb adjacent specialties. A customs residual may CLONE or FANOUT into trade, sanctions, logistics, law, diplomacy, production, public finance, security or language inspection when warranted.

## Language in every customs spoon

Every customs instance gets a cheap language glance.

Record:
- official/publication languages actually available;
- issuing office and jurisdiction;
- whether surfaces are originals, official translations, summaries or later restatements;
- publication/version dates;
- terminology for obligation, exemption, authority, classification, valuation and enforcement;
- whether one surface changes actor, scope, timing, certainty or legal force.

Most scans should be boring and rest. A consequential mismatch can route to the Language Exception Tree / Parallax-style deeper inspection.

A language difference is not, by itself, evidence of deception, selective enforcement or bad faith.

## Enforcement evidence ladder

Customs enforcement is especially vulnerable to confusing **what should happen** with **what did happen**. Keep these states typed and separate:

1. **AUTHORIZED** — law/rule grants an enforcement power or duty.
2. **PLANNED** — policy, budget, staffing plan, target or announced operation says activity is expected.
3. **RESOURCED** — public evidence shows staff, equipment, contracts, systems or appropriations available for the function.
4. **REPORTED_EVENT** — an identified agency or other attributable source reports a specific enforcement/inspection event.
5. **OBSERVED_ACTIVITY** — dated operational data or independently inspectable records show activity occurred.
6. **MEASURED_VOLUME** — counts/rates/clearance times/seizures/inspections are reported for a defined population and period.
7. **AUDITED_OUTCOME** — an audit/review tests whether reported activity/outcomes match controls, records or targets.
8. **UNKNOWN** — evidence does not establish the relevant operational state.

Never promote a target, authorized headcount, expected inspection rate, budgeted officer count or modeled throughput into an observed number.

For every number preserve:
- numerator and denominator;
- unit;
- jurisdiction/entry point;
- time period;
- source;
- whether the figure is planned, reported, observed, measured or audited;
- known coverage gaps.

A seizure announcement proves that announced event only; it does not establish an overall enforcement rate. A staffing authorization proves authority/headcount ceiling only; it does not establish officers actually present on a given shift.

## Garden fit

A Customs pass can use the normal initiating Garden:

- **ARRIVAL:** identify jurisdiction, entry point, modality, source surfaces and languages.
- **EPIST:** separate law/policy, expected capacity, reported event, measured activity and unknown.
- **FUNC:** name the actual customs/logistics function under inspection.
- **MIRROR:** generate ordinary explanations for a discrepancy: timing, data coverage, classification, jurisdiction, staffing, language/summary compression, special regime.
- **CROSS:** attach independent operational observations and epistemic bridges where available.
- **RESID:** retain only the mismatch or unknown that survives ordinary controls.
- **EXIT/RETURN:** rest, answer, or route/clone into the warranted specialist tree.

## Instance identity

A durable instance should have stable IDs rather than relying on names:

`CUSTOMS:<continent>:<jurisdiction>:<regional-interface?>:<entry-point>:<modality>`

Names remain human-facing labels. Boundary changes, renames and agency reorganizations should preserve history and create explicit successor relationships rather than silently rewriting old records.

## What this archetype does not assume

It does not assume:
- every country has the same customs structure;
- every city/port operator possesses customs authority;
- enforcement targets equal enforcement activity;
- an official report is an independent audit;
- multiple agencies reporting one event are multiple independent events;
- language differences imply intent;
- every port must be continuously watched.

It creates a common skeleton so exceptions become visible.
