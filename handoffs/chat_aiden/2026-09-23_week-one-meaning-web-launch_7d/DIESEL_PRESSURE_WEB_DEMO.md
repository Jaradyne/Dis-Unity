# Diesel Pressure Web — Week One end-to-end demo

## Why this demo

Diesel is a useful launch demonstration because it connects one material input to many systems with radically different tolerance for interruption.

This is a **test topology**, not a claim that every node is currently failing.

## Root Question

> Where can a diesel disturbance cross into essential-function failure fastest, and what buffers/substitutions prevent propagation?

## Lowest-tolerance branches to inspect first

### 1. Emergency power
Touchpoints:
- hospitals and critical facilities;
- emergency shelters;
- communications sites;
- water/wastewater backup generation.

Questions:
- runtime at actual load;
- protected fuel contracts;
- refill route;
- generator maintenance;
- non-diesel bridge duration.

Caution: nominal tank capacity is not usable service cover without load, maintenance and refill information.

### 2. Cold chain
Touchpoints:
- medicines/biologics;
- refrigerated food;
- warehouses;
- reefer trucks/containers;
- backup refrigeration.

Questions:
- allowable temperature excursion;
- passive/battery bridge;
- refuel priority;
- alternate storage;
- spoilage triage.

### 3. Time-window agriculture
Touchpoints:
- planting/harvest windows;
- irrigation pumps where diesel-driven;
- custom harvesting;
- grain/feed movement;
- fertilizer and input deliveries.

Questions:
- gallons per critical operation;
- calendar deadline;
- contractor concentration;
- rail/bulk alternatives;
- which lower-priority diesel demand can shed first.

### 4. Rural first/last mile
Touchpoints:
- towns far from rail/water;
- pharmacy/food deliveries;
- farm inputs;
- parcel/postal routes;
- emergency access.

Questions:
- local storage;
- distance to transload;
- gasoline/EV/light-vehicle substitutions;
- cooperative routing;
- reciprocal return loads.

### 5. Small-carrier cashflow
Touchpoints:
- independent trucking;
- fuel-card/credit terms;
- spot freight;
- reefer operators.

Questions:
- price vs cashflow failure;
- contract pass-through lag;
- route abandonment;
- consolidation pressure;
- whether the physical service fails before fuel itself runs out.

## Elasticity / substitution layer

For each node record:
- essential function;
- diesel dependence;
- time tolerance;
- protected reserve;
- alternative energy/transport;
- load that can be shed;
- recovery time;
- dependency children;
- local observations that would falsify concern.

Do **not** collapse these into one vulnerability score.

## Meaning layer

The demo should expose the same physical diesel event through different frames:
- household affordability;
- trucker livelihood;
- farm timing;
- hospital continuity;
- national inventory;
- local access;
- market price;
- emergency preparedness.

The shared dependency is not the talking point. It is the **function that still has to happen**.

## Week One demonstration

Use the existing Question/Attempt/Answer pipeline to produce at least one traversable chain such as:

`distillate signal -> small-carrier cashflow -> rural delivery -> refrigerated medicine/food -> local buffer -> substitution -> unresolved denominator`

A successful demo includes:
- public source discovery;
- one Question;
- one bounded Answer attempt;
- reflection;
- one identified buffer or improving signal;
- one missing denominator;
- one human-readable Meaning Tower card.

Do not manufacture a crisis to make the demo interesting.
