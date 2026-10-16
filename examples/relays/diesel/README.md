# Fictional emergency-power inputs

Every actor, date, receipt and measurement in [sources.json](sources.json) is invented by Work Aiden for the Relay Continuity acceptance exercise. Nothing was retrieved from a real supplier, carrier, clinic or meter. One authored source family is retained across all simulated roles; multiple records are not independent corroboration.

The two reviewed snapshots in [the journal](../../../operations/relays/journal.json) use fictional cutoffs of October 1, 2026 at 08:20 and 11:30 UTC. They were assembled/reviewed on October 16. These are as-of fixture projections, not a record of a real collector or a blind forecast. Source records preserve separate allocation, order, stock, dispatch, movement, receipt, runtime and service observations.

| Fictional input | Value / implication |
| --- | --- |
| Critical circuit | 10 kW; the exercise only covers this electrical service, not the whole clinic or clinical outcomes |
| Initial fuel at 08:00 | 10 L at 10 L/hour gives one hour of cover; exhaustion/switching at 09:00 also has an explicit fixture record |
| Primary order | 80 L promised; actual usable supplier stock is zero; callback successfully communicates the shortfall |
| Alternate allocation / order | 100 L announced by the coordination desk; 80 L actually promised by the alternate supplier at 08:20, due 08:50 |
| Carrier / receipt | Dispatch 08:25; en route 08:40; 80 L received 09:20, 30 minutes late |
| Generator | Restart 09:30; two logged hours at 10 kW through 11:30; 20 L consumed and 60 L remaining |
| Battery | 12 kWh usable AC energy, 12 kW power limit; supplies 10 kW from 09:00–09:30, using 5 kWh and leaving 7 kWh |
| Essential service | Separate fictional monitoring records uninterrupted supply through 11:30; delivery/arithmetic alone cannot establish this outcome |

The calculations provide internal consistency checks; the outcome classifications require their separate supplied observations. The shared runtime contains no diesel-specific equations or assumptions. No input asserts a real shortage, route, person, patient outcome or later service result.
