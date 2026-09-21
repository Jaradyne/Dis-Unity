# CASCADE_GRAPH

Cycle RC-001; cutoff 2026-09-20.

## edges

**id:** EDGE01

**from:** diesel

**to:** trucking

**initiating stress:** Sustained fuel cost increase

**dependent system:** trucking

**mechanism:** Fuel paid before freight invoices settle can squeeze carrier working capital.

**Sources:** [SRC01: EIA](https://www.eia.gov/petroleum/gasdiesel/), [SRC24: Reuters](https://www.reuters.com/business/energy/record-us-diesel-prices-squeeze-farmers-food-prices-may-rise-2026-09-18/)

### buffers

- Surcharges, contracts, route consolidation, stock recovery

### thresholds

- Actual payment mismatch persists through billing cycle; named essential lanes lose reliable service

### substitutes

- Rail for suitable routes; pooled loads; appropriate electric routes

**time horizon:** Days to months

**uncertainty:** No representative carrier failure wave verified

**confirm:** Carrier filings and repeated missed/declined loads linked to fuel cash flow

**falsify:** Stable service, timely surcharges and adequate working capital despite prices

**activation status:** Cost link observed; capacity-loss branch conditional


---

**id:** EDGE02

**from:** trucking

**to:** food_logistics

**initiating stress:** Essential refrigerated freight loses capacity

**dependent system:** food_logistics

**mechanism:** Higher delivered cost or missed windows can reduce food access and increase spoilage.

**Sources:** [SRC24: Reuters](https://www.reuters.com/business/energy/record-us-diesel-prices-squeeze-farmers-food-prices-may-rise-2026-09-18/), [SRC21: Alameda County Community Food Bank](https://www.accfb.org/get-food/)

### buffers

- Multiple suppliers, existing distribution, some contracts

### thresholds

- Missed perishable deliveries and lack of qualified alternate carrier

### substitutes

- Food aggregation; local distribution; nutritionally suitable shelf-stable mix

**time horizon:** Days to weeks

**uncertainty:** Rates indicate pressure; local spoilage or empty shelves not established

**confirm:** Delivery reliability/temperature failures coincide with lane capacity losses

**falsify:** On-time delivery and food availability persist while rates stabilize

**activation status:** Conditional watch


---

**id:** EDGE03

**from:** diesel

**to:** agriculture

**initiating stress:** High fuel cost during harvest

**dependent system:** agriculture

**mechanism:** Essential field operations have low short-run deferrability and consume working capital.

**Sources:** [SRC05: USDA ERS](https://www.ers.usda.gov/topics/farm-economy/farm-sector-income-finances/farm-sector-income-forecast), [SRC24: Reuters](https://www.reuters.com/business/energy/record-us-diesel-prices-squeeze-farmers-food-prices-may-rise-2026-09-18/)

### buffers

- Crop receipts, aid, stored inputs, equipment adaptation

### thresholds

- Farm unable to finance timely operations; verified work delayed past agronomic window

### substitutes

- Shared equipment and route planning; suitable equipment substitution

**time horizon:** Harvest weeks; next season for reinvestment

**uncertainty:** Aggregate farm forecast not individual liquidity; on-road price not off-road price

**confirm:** Farm-level delayed harvest/input purchases tied to operating liquidity

**falsify:** Timely harvest, supported margins and payments prevent disruption

**activation status:** Cost transmission observed; production loss conditional


---

**id:** EDGE04

**from:** fertilizer

**to:** agriculture

**initiating stress:** Phosphate/sulfur supply or margin tightening

**dependent system:** agriculture

**mechanism:** Insufficient timely nutrient access can alter application and future yields; nutrients differ.

**Sources:** [SRC07: Nutrien](https://www.nutrien.com/news/press-releases/nutrien-reports-second-quarter-2026-results-1753), [SRC05: USDA ERS](https://www.ers.usda.gov/topics/farm-economy/farm-sector-income-finances/farm-sector-income-forecast)

### buffers

- Existing stocks, diverse vendors, soil testing and agronomic efficiency

### thresholds

- Verified order rationing/delivery delay during application window

### substitutes

- Agronomically equivalent sources; safe nutrient recovery longer term

**time horizon:** Months and growing seasons

**uncertainty:** One producer cannot establish global shortage; H1 output grew

**confirm:** Independent producer cuts plus farmer order delays

**falsify:** Stable output/deliveries and adequate nutrient access

**activation status:** Conditional watch


---

**id:** EDGE05

**from:** municipal

**to:** transit

**initiating stress:** Temporary operating bridges expire before recurring funds

**dependent system:** transit

**mechanism:** Funding gap can trigger service/staff cuts and reduce network usefulness.

**Sources:** [SRC08: BART](https://www.bart.gov/sites/default/files/2026-09/FY27%20Adopted%20Budget%20Memo_FINAL_SIGNED.pdf), [SRC09: SFMTA](https://www.sfmta.com/projects/sfmta-budget-planning-fy-2026-27-and-fy-2027-28)

### buffers

- Adopted bridges and potential recurring revenue

### thresholds

- Revenue decision fails or receipts too late; operative service-reduction decision

### substitutes

- Timetable integration and targeted essential-trip transport, capacity checked

**time horizon:** November decision through FY27-28

**uncertainty:** Election, receipts, expenses and ridership unresolved

**confirm:** Budget amendment/service timetable implements reductions

**falsify:** Recurring revenue arrives and service maintained without accumulating unsafe deferrals

**activation status:** Conditional watch; fiscal mechanism documented


---

**id:** EDGE06

**from:** transit

**to:** healthcare

**initiating stress:** Loss of affordable accessible essential trips

**dependent system:** healthcare

**mechanism:** Patients and workers may miss appointments/shifts if alternatives cannot carry them.

**Sources:** [SRC08: BART](https://www.bart.gov/sites/default/files/2026-09/FY27%20Adopted%20Budget%20Memo_FINAL_SIGNED.pdf), [SRC09: SFMTA](https://www.sfmta.com/projects/sfmta-budget-planning-fy-2026-27-and-fy-2027-28)

### buffers

- Current service, paratransit and appointment coordination

### thresholds

- Documented missed essential trips with no usable accessible alternative

### substitutes

- Targeted ride pool; suitable remote appointment; neighborhood service access

**time horizon:** Days to months after service change

**uncertainty:** No measured local effect established in this cycle

**confirm:** Attendance/staffing impairment follows specified service loss

**falsify:** Essential access maintained or alternative funded with real capacity

**activation status:** Conditional watch


---

**id:** EDGE07

**from:** grid

**to:** water

**initiating stress:** Local outage outlasts utility operational backup

**dependent system:** water

**mechanism:** Pumping/treatment depend on power and supported equipment.

**Sources:** [SRC10: CAISO](https://www.caiso.com/documents/2026-summer-loads-and-resources-assessment.pdf), [SRC26: EBMUD](https://www.ebmud.com/water/about-your-water/water-supply/water-supply-reports)

### buffers

- Network switching, stored water and backup if verified

### thresholds

- Actual outage plus verified backup/pressure/treatment limit reached

### substitutes

- Alternate power; approved potable supply and conservation

**time horizon:** Hours to days

**uncertainty:** Conceptual dependency; no local outage or backup shortfall established

**confirm:** Utility incident notice documents power-driven service impairment

**falsify:** Verified redundancy keeps required flow/treatment through outage

**activation status:** Scenario only; not current warning


---

**id:** EDGE08

**from:** water

**to:** healthcare

**initiating stress:** Water/sanitation service impairment

**dependent system:** healthcare

**mechanism:** Essential care can require water, sanitation and functioning local utilities.

**Sources:** [SRC16: CDEMA](https://www.cdema.org/index.php/cdemanews/categories/situation-reports/1852-situation-report-18-hurricane-melissa), [SRC26: EBMUD](https://www.ebmud.com/water/about-your-water/water-supply/water-supply-reports)

### buffers

- Facility continuity arrangements subject to verification

### thresholds

- Operator confirms inability to sustain essential service

### substitutes

- Alternate clinical site and official distribution support

**time horizon:** Hours to days

**uncertainty:** No hospital-specific capacity or failure inferred

**confirm:** Public facility service interruption/transfer notice linked to water

**falsify:** Water and sanitation maintained within facility requirements

**activation status:** Scenario only; not current warning


---

**id:** EDGE09

**from:** trade

**to:** construction

**initiating stress:** Changed duties or route constraints raise equipment landed costs

**dependent system:** construction

**mechanism:** Budgeted repair may be delayed if actual quotes exceed finance and substitutes fail specification.

**Sources:** [SRC18: White House](https://www.whitehouse.gov/presidential-actions/2026/06/further-adjusting-the-tariff-regimes-for-imports-of-aluminum-steel-and-copper-into-the-united-states/), [SRC19: White House](https://www.whitehouse.gov/presidential-actions/2026/07/further-strengthening-actions-taken-to-adjust-imports-of-aluminum-into-the-united-states/), [SRC08: BART](https://www.bart.gov/sites/default/files/2026-09/FY27%20Adopted%20Budget%20Memo_FINAL_SIGNED.pdf)

### buffers

- Supplier alternatives; targeted exemptions/incentives if eligible; spending priorities

### thresholds

- Bid/lead-time evidence AND documented repair deferral attributable to affected item

### substitutes

- Refurbishment; compatible parts; supplier diversification

**time horizon:** Months to years

**uncertainty:** BART deferrals not shown caused by tariffs; legal rate depends on product/origin

**confirm:** Procurement records connect tariff/delivery shock to reduced repair scope

**falsify:** Quotes recover, rules mitigate costs, or repairs proceed on time

**activation status:** Not established; causal attribution withheld


---

**id:** EDGE10

**from:** construction

**to:** grid

**initiating stress:** Necessary repair cannot obtain compatible equipment

**dependent system:** grid

**mechanism:** Specific damaged equipment may delay restoration even with ample generation.

**Sources:** [SRC10: CAISO](https://www.caiso.com/documents/2026-summer-loads-and-resources-assessment.pdf), [SRC23: Reuters](https://www.reuters.com/business/energy/hitachi-invest-1-billion-produce-power-grid-components-us-2025-09-04/)

### buffers

- Compatible spares, mutual aid, qualified repairs

### thresholds

- Public operator confirms equipment shortfall delays restoration

### substitutes

- Certified refurbishment or mobile unit if compatible

**time horizon:** Days for available spares; much longer if manufacturing required

**uncertainty:** No current numerical lead time or facility shortfall verified

**confirm:** Operator outage-duration/parts evidence

**falsify:** Repair times normal and compatible replacement available

**activation status:** Scenario only; supplier lead-time refresh required


---

**id:** EDGE11

**from:** industrial

**to:** labor

**initiating stress:** Sector contractions release jobs/skills

**dependent system:** labor

**mechanism:** Voluntary supported retraining and hiring can move compatible skills into repair/logistics needs.

**Sources:** [SRC13: BLS](https://www.bls.gov/news.release/empsit.nr0.htm), [SRC23: Reuters](https://www.reuters.com/business/energy/hitachi-invest-1-billion-produce-power-grid-components-us-2025-09-04/)

### buffers

- Income support and employer training if available

### thresholds

- Verified vacancies and compatible skills with paid transition

### substitutes

- Adjacent role training, apprenticeships and shared services

**time horizon:** Months to years

**uncertainty:** Information-sector losses do not equal available electricians or nurses

**confirm:** Actual placements with retained income and service gains

**falsify:** No matching demand, training funds or realistic qualification path

**activation status:** Opportunity hypothesis


---

**id:** EDGE12

**from:** social

**to:** municipal

**initiating stress:** Grievance combined with organized coercion

**dependent system:** municipal

**mechanism:** Trust erosion may impair cooperation if documented intimidation blocks service decisions.

**Sources:** [SRC14: FBI](https://www.fbi.gov/news/press-releases/fbi-releases-2025-reported-crimes-in-the-nation-statistics), [SRC15: CDEMA](https://www.cdema.org/index.php/cdemanews/categories/press-releases/146-press-releases/1870-cdema-launches-regional-recovery-experts-roster-to-strengthen-caribbean-recovery)

### buffers

- Transparent decisions, trusted intermediaries, inclusive conflict resolution

### thresholds

- Independent evidence of organization, capability AND obstructive behavior

### substitutes

- Multiple credible engagement channels; mediation

**time horizon:** Weeks to years

**uncertainty:** No current escalating cluster established; ordinary anger/activism not a threat indicator

**confirm:** Documented organized intimidation paired with operational interference

**falsify:** Disagreement remains nonviolent and cooperation/decision capacity holds

**activation status:** Inactive hypothesis; no escalation inference

## review decisions

**id:** REV01

**claim:** The US has already fallen below 100m barrels of distillates.

**decision:** Rejected as current fact

**reason:** It is a forecast; Sept11 observed107.859m and three builds.

**Sources:** [SRC03: EIA](https://www.eia.gov/dnav/pet/pet_stoc_wstk_a_epd0_sae_mbbl_w.htm), [SRC04: EIA](https://www.eia.gov/outlooks/steo/)


---

**id:** REV02

**claim:** Diesel price stress proves a nationwide physical shortage or trucking failure wave.

**decision:** Downgraded to cost-pressure watch

**reason:** Delivered-service and carrier failure data not established; refinery output and stock builds buffer.

**Sources:** [SRC02: EIA](https://ir.eia.gov/wpsr/wpsrsummary.pdf), [SRC24: Reuters](https://www.reuters.com/business/energy/record-us-diesel-prices-squeeze-farmers-food-prices-may-rise-2026-09-18/)


---

**id:** REV03

**claim:** Aggregate cereal stocks remove food risk.

**decision:** Rejected

**reason:** Location, affordability, nutrients, payment and transport remain distinct.

**Sources:** [SRC06: FAO](https://www.fao.org/worldfoodsituation/csdb/en/), [SRC24: Reuters](https://www.reuters.com/business/energy/record-us-diesel-prices-squeeze-farmers-food-prices-may-rise-2026-09-18/)


---

**id:** REV04

**claim:** BART cuts have occurred and buses can absorb displaced riders.

**decision:** Rejected

**reason:** Contingency differs from operating plan; SFMTA shares funding pressure.

**Sources:** [SRC08: BART](https://www.bart.gov/sites/default/files/2026-09/FY27%20Adopted%20Budget%20Memo_FINAL_SIGNED.pdf), [SRC09: SFMTA](https://www.sfmta.com/projects/sfmta-budget-planning-fy-2026-27-and-fy-2027-28)


---

**id:** REV05

**claim:** California is approaching systemwide electricity failure.

**decision:** Unsupported by admitted evidence

**reason:** Improved modeled adequacy; local recovery and coincident extremes are separate.

**Sources:** [SRC10: CAISO](https://www.caiso.com/documents/2026-summer-loads-and-resources-assessment.pdf)


---

**id:** REV06

**claim:** Tariffs have caused the observed BART deferrals.

**decision:** Causal attribution withheld

**reason:** Budget does not establish that cause; product-specific procurement evidence needed.

**Sources:** [SRC08: BART](https://www.bart.gov/sites/default/files/2026-09/FY27%20Adopted%20Budget%20Memo_FINAL_SIGNED.pdf), [SRC18: White House](https://www.whitehouse.gov/presidential-actions/2026/06/further-adjusting-the-tariff-regimes-for-imports-of-aluminum-steel-and-copper-into-the-united-states/)


---

**id:** REV07

**claim:** All fertilizer types are contracting.

**decision:** Rejected

**reason:** Potash and H1 phosphate production improved in cited producer record.

**Sources:** [SRC07: Nutrien](https://www.nutrien.com/news/press-releases/nutrien-reports-second-quarter-2026-results-1753)


---

**id:** REV08

**claim:** National social hostility is demonstrably rising now.

**decision:** Not established

**reason:** 2025 matched reported hate incidents declined; current/local lanes unmeasured.

**Sources:** [SRC14: FBI](https://www.fbi.gov/news/press-releases/fbi-releases-2025-reported-crimes-in-the-nation-statistics)


---

**id:** REV09

**claim:** Regional rosters or planning margins are spare rescue capacity.

**decision:** Rejected until donor gate satisfied

**reason:** Availability, commitments, time, routes and simultaneous hazard must be checked.

**Sources:** [SRC10: CAISO](https://www.caiso.com/documents/2026-summer-loads-and-resources-assessment.pdf), [SRC15: CDEMA](https://www.cdema.org/index.php/cdemanews/categories/press-releases/146-press-releases/1870-cdema-launches-regional-recovery-experts-roster-to-strengthen-caribbean-recovery), [SRC17: ENTSO-E](https://www.entsoe.eu/outlooks/seasonal/)


---

**id:** REV10

**claim:** Saudi October cancellations have two independent confirmations.

**decision:** Quarantined as warning evidence

**reason:** Reuters explicitly relays unverified Bloomberg report; one source chain.

**Sources:** [SRC25: Reuters relaying Bloomberg](https://www.reuters.com/business/energy/aramco-halts-october-crude-deliveries-some-european-refiners-after-pipeline-2026-09-18/)

**activation rule:** Conditional links require threshold observations. No automatic transitive propagation from a single stressed node.

**priority rule:** Consequential interaction + independent evidence + actionable response; no opaque score

**safety rule:** A donor retains protected demand and contingency reserve; route/compatibility constrain assistance.

