# Alchemical Mailbox

A mutable queue for questions that may transmute one clue into a useful cascade, reserve, adaptation, local investigation or specialist handoff. It is not canonical state and its contents are not findings.

## Current questions

### Phosphate / sulfur timing
- Mosaic has reduced phosphate production under sulfur availability and affordability pressure. How long does a producer-level dip typically take to reach wholesale, dealer and farmgate availability or pricing?
- Separate immediate price transmission from actual physical shortage.
- What finished-product, distributor, retailer and on-farm inventories can absorb the loss, and for how long?
- Which fields can safely defer phosphorus because soil tests are Optimum/High/Very High, and which low-testing soils cannot?
- Which alternatives matter in practice: other domestic producers, imports, different phosphate products, manure/recovered nutrients, altered application timing, or reduced maintenance applications?
- Which alternatives share the same sulfur, port, credit, rail, barge or seasonal-application bottlenecks?
- What would prove recovery: sulfur contracts, plant restart, operating rate, finished-product shipments, dealer inventories, farmer fulfillment, or normal application windows?

### Ant-colony / specialist birth
- A parent worker may propose a narrower child when several clues intersect outside its useful beat. A birth request is a proposal, not an automatic spawn.
- Look for geographic localization: multiple consequential signals resolving to one city, district, corridor, facility class or trade node.
- Look for cross-domain coupling: a finding requires two or more specialist lenses and neither existing role can resolve the interaction cleanly.
- Look for persistent contradiction: credible evidence remains in conflict after an ordinary skeptical pass.
- Look for hidden adaptation: local people have improvised a workaround that solves one hazard while creating or revealing another.
- Look for possible disparate access or exclusion. Birth a focused investigation when public records or direct reports show a repeated comparative pattern affecting an explicitly identified group. Do not infer protected traits from names, faces, addresses or proxies. The child investigates whether discrimination exists; it does not begin by declaring motive.
- Look for overload: the parent has enough material that a bounded subquestion can be handed off without fragmenting the larger model.

A useful child has a narrow question, a stop condition, relevant context, a budget ceiling and an inbox return path. Child-of-child spawning should consume an explicit shared budget so a useful ant colony does not become recursive noise.

### Evidence texture
- Prefer on-the-ground direct reporting for what a person, operator or local observer directly experienced.
- Distinguish event truth from representativeness. One firsthand report can establish that one event occurred; it cannot by itself establish prevalence.
- Primary operational records and direct measurements are strong for the quantities they actually measure.
- Specialist/industry analysis can connect mechanisms but should not silently outrank contradictory ground evidence.
- Other model outputs, including Gemini consultations, are research leads one step above an unvetted random blog unless they bring inspectable sources.
- Preserve dissent rather than collapsing it into a reputation score.

### Thinking mailbox / public feed
- Explore a dedicated research mailbox and/or public feed for alerts, newsletters, field notes and incoming research suggestions.
- Prefer a public/read-only transport when possible so ingestion does not require a credential.
- If private ingestion is needed, use least-privilege read-only authorization and keep credentials out of Git.
- A shared spreadsheet may act as a human-editable staging table for questions, URLs, place-specific observations and follow-up status, but should not become hidden canonical state.


### Geography coordinator / reciprocal logistics
- Build soil-reserve geography instead of treating fertilizer tonnage as uniform farm resilience.
- For each place, ask both "what is needed?" and "what can travel back?" A pickup delivering compost or recovered nutrients may be able to return with water, food, repair parts, medicine, empty containers, field reports, or another locally useful load.
- Track route dependencies: vehicle type, fuel, road/bridge access, legal permission, driver availability, loading equipment, refrigeration, storage and unloading capacity.
- Distinguish "exists somewhere" from "can reach this place in time."
- Prefer reachable local stocks and observed local production as practical reserves. International trade capacity remains important but receives a larger access-risk discount when shipping lanes, finance, sanctions, insurance, port capacity or political permission can interrupt delivery.
- Candidate standing role: `agents/geography_coordinator.json`.

### Ground reporting without meme capture
- Direct reporting gets high weight for the event actually witnessed, not for the popularity of the post.
- Virality does not create independent corroboration. Trace reposts, clips and quotes back toward the earliest observable source.
- Separate event confidence, attribution confidence, location/time confidence and prevalence confidence.
- Attention-grabbing footage may be excellent evidence of one event and terrible evidence of frequency.
- Preserve quiet negative evidence too: local operators reporting normal service, stocked shelves, functioning routes or absence of the claimed condition can materially constrain a viral narrative.


### Diesel / farm / medical stress escalation
- Apply `scenarios/PANDEMIC_LOCKDOWN_LENS.md` to diesel-dependent systems. A pandemic/lockdown scenario is a stress test, not a forecast.
- Refrigeration includes medicines, vaccines, biologics and diagnostics as well as food. Track both mobile reefer fuel and stationary backup-power fuel.
- Add **diesel elasticity**: how much fuel can a function shed before output or safety drops, and which substitute absorbs the function?
- Track farm failures, Chapter 12/agricultural Chapter 11 stress, creditor sales, land auctions, operator exit and ownership/operating-control changes. Monitor concentration without assuming motive.
- Distinguish temporary station-level outages from structural supply tightness. Ask whether the station, terminal, PADD, refinery and global distillate layer tell the same story.
- Examine existing biofuel capacity before imagining greenfield microplants; feedstock, methanol/catalyst, quality control, permitting, waste handling, cold weather and distribution can become bottlenecks.
- Question for labor substitution: which farm tasks are human-substitutable at emergency scale, which require machines, and where could volunteer/paid surge labor protect harvest or food handling without pretending people can replace combines?
- Standing scout: `agents/us_rural_logistics.json`. It should propose bounded U.S. children first. Mature local/national children can seed analogous agents abroad; several continental syntheses may eventually propose `agents/global_logistics_synthesis.json`.
