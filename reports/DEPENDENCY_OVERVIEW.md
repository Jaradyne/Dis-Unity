# Conditional dependency overview

Dashed arrows are proposed propagation paths. They do not mean the downstream harm has occurred. Source-linked thresholds and falsifiers are in CASCADE_GRAPH.md.

```mermaid
flowchart TD
  D["Diesel costs"] --> T["Freight cash pressure"]
  D --> A["Harvest expenses"]
  T -. "If delivery capacity falls" .-> F["Food access"]
  A -. "If operations are delayed" .-> F
  S["Sulfur availability"] --> P["Phosphate economics"]
  P -. "If timely inputs fail" .-> A
  B["Transit funding gap"] -. "If service is reduced" .-> M["Essential mobility"]
  M -. "If alternatives fail" .-> C["Work and care access"]
  R["Protected partner reserves"] -. "Capacity checked" .-> M
  R -. "Capacity checked" .-> F
```

Food stocks, existing operating service and diverse production are buffers. Borrowing, shared bus capacity and volunteer effort are finite. Any rescue proposal needs a donor minimum and a route to replenishment.
