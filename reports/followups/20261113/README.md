# Diesel forecast revision and retained Richmond question

Completed November 15, 2026 Pacific, using public EIA receipts captured November 13 Pacific / November 14 UTC. The [November 8 assessment](../20261108/README.md) is preserved byte-for-byte. This is a dated follow-up, not a new canonical research cycle.

**U.S. diesel prices were falling in the latest reported week, and EIA still forecasts easing through January—but the projected prices are higher than in October's forecast.** These are compatible observations about different dates and quantities.

| National monthly average | October 6 forecast | November 10 forecast | Revision |
| --- | ---: | ---: | ---: |
| November 2026 | $5.79/gal | $6.10/gal | +$0.31 |
| December 2026 | $5.34/gal | $5.79/gal | +$0.46 |
| January 2027 | $5.06/gal | $5.55/gal | +$0.49 |

The [same EIA workbook URL](https://www.eia.gov/outlooks/steo/xls/Fig12.xlsx) returned distinct October and November versions. Both complete raw responses are retained. The selected series is retail diesel, sheet `12`, dates `C82:C84`, forecasts `E82:E84`. [Exact values and source bindings](diesel-data.json) preserve the unrounded cached numbers. These are national monthly averages, not California forecasts or daily guarantees.

The [November overview](https://www.eia.gov/outlooks/steo/) was released November 10 with model inputs finalized November 5. It raised the **whole-2027 average** from $4.49 to $5.03/gal, a published 12% increase. EIA expects continued global petroleum-product supply constraints through 2027 while retaining gradual price declines. That conditional outlook does not establish a uniform worldwide retail-price decline. The older IEA assessment in the November 8 report remains dated October material.

[Weekly EIA observations](https://www.eia.gov/petroleum/gasdiesel/) for November 9, released November 10, were **$6.127/gal U.S.** and **$7.897/gal California**, down $0.165 and $0.179 respectively from November 2. Prices include taxes. These measurements do not establish completed fuel deliveries or continuity of essential services.

## What changed in the Garden record

[Packet pins](packet.json) bind the original six files and three new complete HTTP receipts. [Arrival replay](arrival-output.json) distinguishes a real first receipt, a clearly simulated unchanged repeat using saved bytes, and a real changed version. Unchanged or previously seen content creates no duplicate review work. Changed bytes create a pending review item; they do not establish a forecast change without inspecting the series, or admit a finding automatically.

[The proposed assessment](assessment-proposal.json) links the earlier assessment and new sources. [Review](REVIEW.md) records the actual reviewer, evidence checks and limits. This case-local offline comparison reuses existing receipt/hash helpers; it does **not** expand the GAO-pinned generic adapter or claim an EIA-to-Garden assessment runtime. Full generic integration remains future work.

```bash
python reports/followups/20261113/verify_packet.py check
python -m unittest discover -s tests -p test_eia_followup.py -v
```

## Chat and Digest handoff

Carry forward the higher November forecast as a dated revision, keeping October's version reconstructible. All three new documents belong to one EIA source family; their agreement is not independent corroboration. The unchanged-repeat demonstration is simulated. No future price or essential-service outcome has been observed.

**Richmond remains unresolved:** the earlier source check found publicity and recruitment, not a dated occupied-bed count, current paid operator or executed grant transition. Neither operation nor emptiness is established. The approximately $1 million demand remains an unverified lead; no new Richmond investigation is claimed here.

**One next empirical test per retained question:** for diesel, a matched-week operator record joining planned/completed deliveries, actual fuel cost and buffer use; for Richmond, a current operating/funding packet joining occupied beds, responsible staffed coverage and the disposition of grants. No contact, records request, recurring collector, model call, Governor change or canonical admission occurred.
