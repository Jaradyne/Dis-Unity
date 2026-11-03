# Diesel: one supervised live-source pass

Requested November 2, 2026 Pacific; retrievals and review crossed into November 3. The directory retains the request date. Exact timestamps remain in the receipts and Garden events. The inspected EIA release contains observations through October 26; retrieval time is not the observation date.

Two actual EIA GETs supplied a feed and the linked numeric price page. Work Aiden inspected the material, supplied ten Garden node outputs, and replayed the completed pass. This is a live public-source investigation with supervised interpretation. No autonomous provider inference or physical fuel-delivery action occurred.

The existing Question is **Q-RESEARCH-Q01: Are fuel costs becoming actual missed essential deliveries?** Epoch 1's answers remain intact. Epoch 2 records this fresh evidence surface and still requires a service-performance record.

## What the source establishes

The [EIA Gasoline and Diesel Fuel Update](https://www.eia.gov/petroleum/gasdiesel/) displayed an October 27 release, October 26 observations, and November 3 as its next release date. These are retail on-highway diesel averages, in US dollars per US gallon, including all taxes.

| Geography | Oct 19 | Oct 26 | Weekly change | Change from a year earlier |
| --- | ---: | ---: | ---: | ---: |
| United States | 6.276 | 6.352 | +0.076 | +2.634 |
| West Coast (PADD 5) | 7.394 | 7.329 | -0.065 | +2.844 |
| California | 8.242 | 8.155 | -0.087 | +3.221 |

[All eleven diesel rows](prices.json) are extracted from the saved [price-page receipt](receipts/price-table.json). The [feed receipt](receipts/feed.json) and table share one EIA publication lineage; they are not independent corroboration. The source also contains gasoline figures and an August cost-component graphic. Neither is substituted for the dated diesel table.

The national weekly increase and regional weekly declines both matter. This source supports a dated price comparison. It does not measure an East Bay operator's purchase price, usable stock, cash reserve, dispatches, missed deliveries, causes of a miss, or observed protection. Those remain **UNKNOWN**. No shortage or causal service failure is inferred.

## Actual execution and limits

| Stage | Result |
| --- | --- |
| Intake | Two public GETs, both HTTP 200; complete retained bodies and hashes; no redirects |
| Discovery | Existing scout found one changed feed item relative to its retained sensor history |
| Inspection | Work reviewed the numeric table; extraction verifies the fuel label, units, columns and weekly arithmetic |
| Shared Question | Reopened to epoch 2; earlier answers and attempts preserved |
| Garden | Ten supplied nodes in the existing PRODUCTION tree; one resting branch |
| Review | Bounded review of retained material and implementation; actual scope in REVIEW.md |
| Return | Provisional Work answer and one next test; no canonical admission or Governor action |

The live provider gate returned `window_complete`; the old manifest remains closed. No API inference, operating-window extension, new specialist, recurring schedule or Governor power was activated. Work's one-off public inspection used the existing recorder and scout outside the closed hosted dispatcher. Retrieval happened before the supplied Garden traversal; this does not demonstrate automatic source selection or autonomous analysis.

The earlier [diesel resupply fixture](../../../examples/relays/diesel/README.md) remains fictional and unchanged. Its successful battery bridge is not evidence that a real community has such a buffer.

## One bounded next test

For one willing essential-delivery operator serving the East Bay, inspect one dated weekly dispatch-and-cost packet: scheduled versus completed deliveries, recorded reasons for misses, fuel expense, and any buffer or substitution that preserved service. No operator has been contacted and no private records have been obtained. This packet's missing performance evidence is not a claim that no public record exists.

Candidate protections include protected fuel cash or stocks, consolidated routes, compatible alternate transport, and mutual aid. Usable quantities, staffing, permission, compatibility, donor floors and replenishment remain unknown. These are options to check, not promised resources. This pass stops here.

## Offline reproduction

From the repository root:

```bash
python reports/diesel/20261102/verify.py
python -m unittest discover -s tests -p 'test_diesel_recheck.py' -v
```

The verifier checks receipt bytes, reconstructs the numeric table and replays the actual exported event history with pinned runtime files. Hashes and replay verify preservation and consistency, not source truth. [execution.json](execution.json) separates automated checks from supplied analysis.

The operational run belongs on `week-one-state` at `operations/garden/runs/DIESEL-RECHECK-20261102.json`. After loading operational data into a separate checkout using reviewed main code, compare it as well:

```bash
python reports/diesel/20261102/verify.py --operational-root /path/to/operational-checkout
```

RC-012 is review intake only. RC-004 remains canonical; prior cases and evidence history are unchanged.
