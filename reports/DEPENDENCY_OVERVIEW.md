# Dependency overview — RC-002

Solid arrows below indicate a documented input/cost relationship or producer action. Dotted arrows are conditional downstream branches; co-occurrence alone does not activate them.

```mermaid
flowchart TD
  Fuel["Diesel costs and regional stocks"] --> Freight["Transport economics"]
  Trucks["Reported produce-truck constraints"] -.-> Access["Food delivery and access"]
  Freight -.-> Access
  Sulfur["Sulfur availability and cost"] --> Phosphate["Producer phosphate curtailments"]
  Phosphate -.-> Farms["Farm nutrient fulfillment"]
  Farms -.-> Access
  Buffers["Compatible supply, routes and reserves"] -.-> Farms
  Buffers -.-> Access
```

The graph is conditional, not a collapse forecast. Grain rail/barge operations and nutrient-specific production provide counterevidence and potential adaptation. Confirm delivered fulfillment and compatible spare capacity before asserting either failure or rescue.

```mermaid
flowchart TD
  Finance["Time-limited operating finance"] -.-> Service["Staffed mobility and care"]
  Capital["Restricted capital investment"] --> Hardware["Replacement equipment"]
  Hardware -.-> Service
  Power["Local power interruption"] -.-> Functions["Water, communications and care"]
  Hub["Constructed microgrid"] -.-> Functions
  Service --> Access["Essential access"]
  Functions --> Access
```

Capital, cash, staffing and operational reserve are separate. Construction does not establish tested outage duration. Outside help needs a specific compatible function, route, donor floor and replenishment path. Canonical edge records retain sources, thresholds, substitutes, uncertainty, confirming observations and falsifiers.
