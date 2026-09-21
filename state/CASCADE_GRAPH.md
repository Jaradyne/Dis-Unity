# CASCADE_GRAPH

Cycle RC-003; cutoff 2026-09-21.

**activation rule:** Conditional links require threshold observations. No automatic transitive propagation from a single stressed node.

## edges

**activation status:** Cost link observed; capacity-loss branch conditional

### buffers

- Surcharges, contracts, route consolidation, stock recovery

**confirm:** Carrier filings and repeated missed/declined loads linked to fuel cash flow

**dependent system:** trucking

**falsify:** Stable service, timely surcharges and adequate working capital despite prices

**from:** diesel

**id:** EDGE01

**initiating stress:** Sustained fuel cost increase

**mechanism:** Fuel paid before freight invoices settle can squeeze carrier working capital.

**Sources:** [SRC01: EIA](https://www.eia.gov/petroleum/gasdiesel/), [SRC24: Reuters](https://www.reuters.com/business/energy/record-us-diesel-prices-squeeze-farmers-food-prices-may-rise-2026-09-18/)

### substitutes

- Rail for suitable routes; pooled loads; appropriate electric routes

### thresholds

- Actual payment mismatch persists through billing cycle; named essential lanes lose reliable service
- Separate carrier diesel-cost exposure from produce-truck availability; a contemporaneous shortage rating alone cannot identify fuel as the cause.

**time horizon:** Days to months

**to:** trucking

**uncertainty:** No representative carrier failure wave verified


---

**activation status:** Some reported truck availability constraints observed; missed-delivery branch conditional

### buffers

- Multiple suppliers, existing distribution, some contracts
- September grain rail/barge throughput provides sector-specific counterevidence; Mexico–Texas slight reefer surplus is only a candidate after route/commodity/driver constraints.

**confirm:** Delivery reliability/temperature failures coincide with lane capacity losses

**dependent system:** food_logistics

**falsify:** On-time delivery and food availability persist while rates stabilize

**from:** trucking

**id:** EDGE02

**initiating stress:** Essential refrigerated freight loses capacity

**mechanism:** Higher delivered cost or missed windows can reduce food access and increase spoilage.

**Sources:** [SRC24: Reuters](https://www.reuters.com/business/energy/record-us-diesel-prices-squeeze-farmers-food-prices-may-rise-2026-09-18/), [SRC21: Alameda County Community Food Bank](https://www.accfb.org/get-food/), [FF-S03: USDA AMS](https://agtransport.usda.gov/resource/25pi-t6xr.json), [FF-S04: USDA AMS](https://www.ams.usda.gov/sites/default/files/media/RTQ1stQuarter2026.pdf), [FF-S05: USDA AMS](https://www.ams.usda.gov/sites/default/files/media/GTR09172026.pdf)

### substitutes

- Food aggregation; local distribution; nutritionally suitable shelf-stable mix

### thresholds

- Missed perishable deliveries and lack of qualified alternate carrier

**time horizon:** Days to weeks

**to:** food_logistics

**uncertainty:** Rates indicate pressure; local spoilage or empty shelves not established


---

**activation status:** Cost transmission observed; production loss conditional

### buffers

- Crop receipts, aid, stored inputs, equipment adaptation

**confirm:** Farm-level delayed harvest/input purchases tied to operating liquidity

**dependent system:** agriculture

**falsify:** Timely harvest, supported margins and payments prevent disruption

**from:** diesel

**id:** EDGE03

**initiating stress:** High fuel cost during harvest

**mechanism:** Essential field operations have low short-run deferrability and consume working capital.

**Sources:** [SRC05: USDA ERS](https://www.ers.usda.gov/topics/farm-economy/farm-sector-income-finances/farm-sector-income-forecast), [SRC24: Reuters](https://www.reuters.com/business/energy/record-us-diesel-prices-squeeze-farmers-food-prices-may-rise-2026-09-18/)

### substitutes

- Shared equipment and route planning; suitable equipment substitution

### thresholds

- Farm unable to finance timely operations; verified work delayed past agronomic window

**time horizon:** Harvest weeks; next season for reinvestment

**to:** agriculture

**uncertainty:** Aggregate farm forecast not individual liquidity; on-road price not off-road price


---

**activation status:** Upstream producer curtailment corroborated; farm-level access loss conditional

### buffers

- Existing stocks, diverse vendors, soil testing and agronomic efficiency

**confirm:** Independent producer cuts plus farmer order delays

**dependent system:** agriculture

**falsify:** Stable output/deliveries and adequate nutrient access Verified restarts, timely distributor fulfillment and nutrient-suitable deliveries would weaken the downstream branch.

**from:** fertilizer

**id:** EDGE04

**initiating stress:** Phosphate/sulfur supply or margin tightening

**mechanism:** Insufficient timely nutrient access can alter application and future yields; nutrients differ.

**Sources:** [SRC07: Nutrien](https://www.nutrien.com/news/press-releases/nutrien-reports-second-quarter-2026-results-1753), [SRC05: USDA ERS](https://www.ers.usda.gov/topics/farm-economy/farm-sector-income-finances/farm-sector-income-forecast), [TRS02: The Mosaic Company](https://mosaicco.com/Article/Fertilizer-Markets-Facts-and-Context), [TRS01: CF Industries](https://ir.cfindustries.com/Investors/news/news-details/2026/CF-Industries-Holdings-Inc--Reports-First-Half-2026-Net-Earnings-of-1-34-Billion-Adjusted-EBITDA-of-2-18-Billion/default.aspx)

### substitutes

- Agronomically equivalent sources; safe nutrient recovery longer term

### thresholds

- Verified order rationing/delivery delay during application window

**time horizon:** Months and growing seasons

**to:** agriculture

**uncertainty:** One producer cannot establish global shortage; H1 output grew


---

**activation status:** Conditional watch; fiscal mechanism documented

### buffers

- Adopted bridges and potential recurring revenue

**confirm:** Budget amendment/service timetable implements reductions

**dependent system:** transit

**falsify:** Recurring revenue arrives and service maintained without accumulating unsafe deferrals

**from:** municipal

**id:** EDGE05

**initiating stress:** Temporary operating bridges expire before recurring funds

**mechanism:** Funding gap can trigger service/staff cuts and reduce network usefulness.

**Sources:** [SRC08: BART](https://www.bart.gov/sites/default/files/2026-09/FY27%20Adopted%20Budget%20Memo_FINAL_SIGNED.pdf), [SRC09: SFMTA](https://www.sfmta.com/projects/sfmta-budget-planning-fy-2026-27-and-fy-2027-28), [LC_SRC03: Alameda-Contra Costa Transit District](https://www.actransit.org/sites/default/files/2026-09/FY2026-27%20District%20Adopted%20Budget%20Book.pdf)

### substitutes

- Timetable integration and targeted essential-trip transport, capacity checked

### thresholds

- Revenue decision fails or receipts too late; operative service-reduction decision

**time horizon:** November decision through FY27-28

**to:** transit

**uncertainty:** Election, receipts, expenses and ridership unresolved New AC Transit evidence is specialist-read but coordinator retrieval failed; no quantified substitute fleet.


---

**activation status:** Conditional watch

### buffers

- Current service, paratransit and appointment coordination

**confirm:** Attendance/staffing impairment follows specified service loss

**dependent system:** healthcare

**falsify:** Essential access maintained or alternative funded with real capacity

**from:** transit

**id:** EDGE06

**initiating stress:** Loss of affordable accessible essential trips

**mechanism:** Patients and workers may miss appointments/shifts if alternatives cannot carry them.

**Sources:** [SRC08: BART](https://www.bart.gov/sites/default/files/2026-09/FY27%20Adopted%20Budget%20Memo_FINAL_SIGNED.pdf), [SRC09: SFMTA](https://www.sfmta.com/projects/sfmta-budget-planning-fy-2026-27-and-fy-2027-28)

### substitutes

- Targeted ride pool; suitable remote appointment; neighborhood service access

### thresholds

- Documented missed essential trips with no usable accessible alternative

**time horizon:** Days to months after service change

**to:** healthcare

**uncertainty:** No measured local effect established in this cycle


---

**activation status:** Scenario only; not current warning

### buffers

- Network switching, stored water and backup if verified
- Historical reservoir storage does not establish current delivery reserve; map gravity, pumping, treatment and local distribution separately before activating this edge.

**confirm:** Utility incident notice documents power-driven service impairment

**dependent system:** water

**falsify:** Verified redundancy keeps required flow/treatment through outage

**from:** grid

**id:** EDGE07

**initiating stress:** Local outage outlasts utility operational backup

**mechanism:** Pumping/treatment depend on power and supported equipment.

**Sources:** [SRC10: CAISO](https://www.caiso.com/documents/2026-summer-loads-and-resources-assessment.pdf), [SRC26: EBMUD](https://www.ebmud.com/water/about-your-water/water-supply/water-supply-reports), [LC_SRC01: East Bay Municipal Utility District](https://www.ebmud.com/download_file/force/58167/703?WOD_-_Water_Supply_Update_-_April_14_2026_Final_Board.pdf=)

### substitutes

- Alternate power; approved potable supply and conservation

### thresholds

- Actual outage plus verified backup/pressure/treatment limit reached

**time horizon:** Hours to days

**to:** water

**uncertainty:** Conceptual dependency; no local outage or backup shortfall established


---

**activation status:** Scenario only; not current warning

### buffers

- Facility continuity arrangements subject to verification

**confirm:** Public facility service interruption/transfer notice linked to water

**dependent system:** healthcare

**falsify:** Water and sanitation maintained within facility requirements

**from:** water

**id:** EDGE08

**initiating stress:** Water/sanitation service impairment

**mechanism:** Essential care can require water, sanitation and functioning local utilities.

**Sources:** [SRC16: CDEMA](https://www.cdema.org/index.php/cdemanews/categories/situation-reports/1852-situation-report-18-hurricane-melissa), [SRC26: EBMUD](https://www.ebmud.com/water/about-your-water/water-supply/water-supply-reports)

### substitutes

- Alternate clinical site and official distribution support

### thresholds

- Operator confirms inability to sustain essential service

**time horizon:** Hours to days

**to:** healthcare

**uncertainty:** No hospital-specific capacity or failure inferred


---

**activation status:** Not established; causal attribution withheld

### buffers

- Supplier alternatives; targeted exemptions/incentives if eligible; spending priorities

**confirm:** Procurement records connect tariff/delivery shock to reduced repair scope

**dependent system:** construction

**falsify:** Quotes recover, rules mitigate costs, or repairs proceed on time

**from:** trade

**id:** EDGE09

**initiating stress:** Changed duties or route constraints raise equipment landed costs

**mechanism:** Budgeted repair may be delayed if actual quotes exceed finance and substitutes fail specification.

**Sources:** [SRC18: White House](https://www.whitehouse.gov/presidential-actions/2026/06/further-adjusting-the-tariff-regimes-for-imports-of-aluminum-steel-and-copper-into-the-united-states/), [SRC19: White House](https://www.whitehouse.gov/presidential-actions/2026/07/further-strengthening-actions-taken-to-adjust-imports-of-aluminum-into-the-united-states/), [SRC08: BART](https://www.bart.gov/sites/default/files/2026-09/FY27%20Adopted%20Budget%20Memo_FINAL_SIGNED.pdf)

### substitutes

- Refurbishment; compatible parts; supplier diversification

### thresholds

- Bid/lead-time evidence AND documented repair deferral attributable to affected item

**time horizon:** Months to years

**to:** construction

**uncertainty:** BART deferrals not shown caused by tariffs; legal rate depends on product/origin


---

**activation status:** Scenario only; supplier lead-time refresh required

### buffers

- Compatible spares, mutual aid, qualified repairs

**confirm:** Operator outage-duration/parts evidence

**dependent system:** grid

**falsify:** Repair times normal and compatible replacement available

**from:** construction

**id:** EDGE10

**initiating stress:** Necessary repair cannot obtain compatible equipment

**mechanism:** Specific damaged equipment may delay restoration even with ample generation.

**Sources:** [SRC10: CAISO](https://www.caiso.com/documents/2026-summer-loads-and-resources-assessment.pdf), [SRC23: Reuters](https://www.reuters.com/business/energy/hitachi-invest-1-billion-produce-power-grid-components-us-2025-09-04/)

### substitutes

- Certified refurbishment or mobile unit if compatible

### thresholds

- Public operator confirms equipment shortfall delays restoration

**time horizon:** Days for available spares; much longer if manufacturing required

**to:** grid

**uncertainty:** No current numerical lead time or facility shortfall verified


---

**activation status:** Opportunity hypothesis

### buffers

- Income support and employer training if available

**confirm:** Actual placements with retained income and service gains

**dependent system:** labor

**falsify:** No matching demand, training funds or realistic qualification path

**from:** industrial

**id:** EDGE11

**initiating stress:** Sector contractions release jobs/skills

**mechanism:** Voluntary supported retraining and hiring can move compatible skills into repair/logistics needs.

**Sources:** [SRC13: BLS](https://www.bls.gov/news.release/empsit.nr0.htm), [SRC23: Reuters](https://www.reuters.com/business/energy/hitachi-invest-1-billion-produce-power-grid-components-us-2025-09-04/)

### substitutes

- Adjacent role training, apprenticeships and shared services

### thresholds

- Verified vacancies and compatible skills with paid transition

**time horizon:** Months to years

**to:** labor

**uncertainty:** Information-sector losses do not equal available electricians or nurses


---

**activation status:** Inactive hypothesis; no escalation inference

### buffers

- Transparent decisions, trusted intermediaries, inclusive conflict resolution

**confirm:** Documented organized intimidation paired with operational interference

**dependent system:** municipal

**falsify:** Disagreement remains nonviolent and cooperation/decision capacity holds

**from:** social

**id:** EDGE12

**initiating stress:** Grievance combined with organized coercion

**mechanism:** Trust erosion may impair cooperation if documented intimidation blocks service decisions.

**Sources:** [SRC14: FBI](https://www.fbi.gov/news/press-releases/fbi-releases-2025-reported-crimes-in-the-nation-statistics), [SRC15: CDEMA](https://www.cdema.org/index.php/cdemanews/categories/press-releases/146-press-releases/1870-cdema-launches-regional-recovery-experts-roster-to-strengthen-caribbean-recovery)

### substitutes

- Multiple credible engagement channels; mediation

### thresholds

- Independent evidence of organization, capability AND obstructive behavior

**time horizon:** Weeks to years

**to:** municipal

**uncertainty:** No current escalating cluster established; ordinary anger/activism not a threat indicator


---

**activation status:** Producer-level capacity withdrawal observed; downstream cascade conditional

**buffers:** Alternative sourcing, inventories and preserved restart crews; quantities and lead times unverified

**confirm:** Continuing reduced output plus unmet phosphate orders near application windows

**dependent system:** Phosphate production, agricultural input distribution and workers

**falsify:** Restarts, replenished stocks and normal delivered order completion

**from:** industrial

**id:** EDGE13

**initiating stress:** Sulfur availability and affordability constrain phosphate producers

**mechanism:** Unavailable or uneconomic feedstock leads to rate reductions or idling. Company cash preservation can transfer costs to workers and customers.

**Sources:** [SRC07: Nutrien](https://www.nutrien.com/news/press-releases/nutrien-reports-second-quarter-2026-results-1753), [TRS02: The Mosaic Company](https://mosaicco.com/Article/Fertilizer-Markets-Facts-and-Context)

**substitutes:** Nutrient-appropriate imports/recovery/efficiency; potash and nitrogen cannot replace phosphorus function

**thresholds:** Operator-disclosed idling observed; downstream escalation requires distributor or farmer fulfillment evidence

**time horizon:** Weeks to months; application windows matter

**to:** fertilizer

**uncertainty:** Lost volumes, restart dates, distributor stocks and individual farm exposure unknown


---

**activation status:** Conditional watch; dated stress and improving hardware evidence coexist

**buffers:** Grant award; local public ownership and equipment replacement; confirmed recurring reimbursement and partnerships if available

**confirm:** Current public financials plus documented service reduction and inability of nearby providers to absorb load

**dependent system:** Healthcare access, workforce retention and essential transport

**falsify:** Sustained operating liquidity, retained staffed services and demonstrated shorter waits/less transfer demand

**from:** municipal

**id:** EDGE14

**initiating stress:** Operating cash shortage persists beyond grant bridge

**mechanism:** If cash cannot cover staffed services, patients may need neighboring providers and longer trips; donor clinics and transport must have actual reserve. The branch is conditional, not a present closure claim.

**Sources:** [RC2H01: California HCAI](https://hcai.ca.gov/facilities/health-facility-financing/distressed-hospital-loan-program/), [RC2H04: Pajaro Valley Health Care District](https://www.pvhcd.org/home-page/page/federal-cuts-put-watsonville-community-hospital-risk-partnership-way-forward), [RC2H05: Pajaro Valley Health Care District](https://www.pvhcd.org/home-page/page/new-mri-and-ct-imaging-now-available-watsonville-community-hospital)

**substitutes:** Clinically appropriate outpatient/referral capacity and coordinated accessible transport subject to confirmed availability

**thresholds:** Dated board/operator evidence of reduced staffed service or payment-driven supply interruption

**time horizon:** Weeks to months for cash; months to years for durable operating model

**to:** healthcare

**uncertainty:** Current cash balance, grant disbursement, staffing and partner surplus unverified


---

**activation status:** Upstream curtailment observed; farmer/crop cascade conditional

**buffers:** Stocks, alternative qualified suppliers, acid regeneration and agronomic demand reduction

**confirm:** Missed phosphate orders after documented idles

**dependent system:** fertilizer

**falsify:** Restarts or replacement supply fill needs on time

**from:** sulfur

**id:** EDGE15

**initiating stress:** Insufficient affordable, deliverable sulfur/acid

**mechanism:** Wet-process phosphate production needs acid; lost feed or unaffordable operation can idle usable mineral-processing capacity.

**Sources:** [NUT02: U.S. EPA](https://www.epa.gov/sites/default/files/2020-09/documents/8.9_phosphoric_acid.pdf), [TRS02: The Mosaic Company](https://mosaicco.com/Article/Fertilizer-Markets-Facts-and-Context), [RC3C02: International Energy Agency](https://www.iea.org/reports/global-critical-minerals-outlook-2026/executive-summary)

**substitutes:** Compatible fertilizer imports and tested recovered phosphorus; N and K do not replace P

**thresholds:** Plant input cover exhausted or economics force idling; farm effects need unmet orders/application windows

**time horizon:** Days to months; new plants longer

**to:** fertilizer

**uncertainty:** Current downstream inventories and restarts unknown


---

**activation status:** Unactivated conditional transition hypothesis

**buffers:** Sour-gas recovery, compatible smelter acid, regeneration and reduced avoidable demand

**confirm:** Linked output loss plus unmet essential acid demand after adaptation

**dependent system:** sulfur

**falsify:** Stable delivered supply through contraction

**from:** diesel

**id:** EDGE16

**initiating stress:** Long-run refining throughput contraction

**mechanism:** A useful sulfur coproduct may decline as fuel processing contracts; net effect depends on feed sulfur and alternative sources.

**Sources:** [NUT03: U.S. EPA](https://www.epa.gov/sites/default/files/2020-09/documents/8.13_sulfur_recovery.pdf), [NUT04: U.S. EPA](https://www.epa.gov/sites/default/files/2020-09/documents/8.10_sulfuric_acid.pdf)

**substitutes:** Verified sulfur/acid sources and nutrient recovery

**thresholds:** Recovered output falls faster than accessible alternatives and demand reductions

**time horizon:** Months to years; structural transition

**to:** sulfur

**uncertainty:** No EV attribution for current shortage; net supply response unknown


---

**activation status:** Planning dependency; no named fleet failure established

**buffers:** Charged reserve vehicles, managed charging and genuinely independent charging paths

**confirm:** Named missed deliveries linked to charger/feeder failure

**dependent system:** trucking

**falsify:** Routes completed with tested independent replenishment

**from:** grid

**id:** EDGE17

**initiating stress:** Depot charging unavailable or insufficient

**mechanism:** Electrified routes shift replenishment from diesel delivery to chargers and electrical service; simultaneous outages can remove the substitute.

**Sources:** [EFS04: U.S. Department of Energy, Alternative Fuels Data Center](https://afdc.energy.gov/vehicles/electric-fleets), [EFS06: U.S. Department of Energy, Alternative Fuels Data Center](https://afdc.energy.gov/fuels/electricity-infrastructure-development)

**substitutes:** Compatible alternate depot; pooled essential trips; phased fleet transition

**thresholds:** Usable energy cannot cover essential route through replenishment interruption

**time horizon:** Hours to days during outages; months/years for interconnection

**to:** trucking

**uncertainty:** Site route, payload, weather and charger data absent


---

**activation status:** Unactivated shared-shock hypothesis

**buffers:** Separate purchasing fund, USDA channels, rotating stocks and route-diverse suppliers

**confirm:** Dated rise in unmet requests plus falling recoveries/fulfillment and insufficient independent cover

**dependent system:** food_assistance

**falsify:** Stable essential service despite changing donation mix

**from:** food_logistics

**id:** EDGE18

**initiating stress:** Supply disruption alongside increased need

**mechanism:** Rescued supply may fall while food prices, demand for aid and delivery costs rise. Stranded surplus elsewhere is not automatically usable.

**Sources:** [EFS01: Feeding America](https://www.feedingamerica.org/sites/default/files/2025-12/FA_25AnnReport_DIGITAL_final.pdf), [EFS02: Alameda County Community Food Bank](https://www.accfb.org/wp-content/uploads/2026/01/ACCFB-2025-Audit-FS.pdf), [EFS03: Alameda County Community Food Bank](https://www.accfb.org/annual-report-2025/)

**substitutes:** Funded interregional procurement and safe menu substitution; cash assistance where markets work

**thresholds:** Delivered usable nutrition falls below agreed essential service floor after purchases and inventory drawdown

**time horizon:** Days to months

**to:** food_assistance

**uncertainty:** No local reserve-days baseline or current famine; some disruptions increase recoverable surplus


---

**activation status:** Ordinary hours reduction observed; emergency cascade conditional

**buffers:** Protected activation budget, paid staff, durable access agreement and differently funded partner

**confirm:** Service closures during needed activation with unmet demand

**dependent system:** commons

**falsify:** Funded emergency hours and successful accessible activation

**from:** municipal

**id:** EDGE19

**initiating stress:** Operating-budget pressure

**mechanism:** Reduced paid opening hours can remove accessible community refuge and information capacity even when the building remains intact.

**Sources:** [DC09: City of Hayward](https://www.hayward-ca.gov/discover/news/jan26/library-hours-be-reduced-two-digital-streaming-resources-eliminated), [DC05: City of Hayward](https://www.hayward-ca.gov/public-library/using-library/locations-hours), [DC06: City of Hayward](https://www.hayward-ca.gov/public-library/using-library/meeting-rooms)

**substitutes:** Accessible partner site with independent funded operation

**thresholds:** Reduced hours overlap verified essential need and alternate sites cannot absorb it

**time horizon:** Weeks/months for budget changes; hours during events

**to:** commons

**uncertainty:** No heat-related harm measured in Hayward


---

**activation status:** Specific historical fertilizer-cargo interruption observed; broader cascade conditional

**buffers:** Stocks, route-diverse origins, vessel security and confirmed replacement bookings

**confirm:** Matched shipment loss, depleted stocks and missed customer orders

**dependent system:** fertilizer

**falsify:** Replacement arrives before need or procurement chain unaffected

**from:** trade

**id:** EDGE20

**initiating stress:** Cargo disruption or inaccessible maritime route

**mechanism:** Loss, delay or rerouting consumes freight capacity and working capital; consequences depend on local cover and crop timing.

**Sources:** [MAR05: EUNAVFOR ATALANTA](https://eunavfor.eu/news/update-ongoing-piracy-incidents-northern-coast-somalia), [MAR07: ICC International Maritime Bureau](https://icc-ccs.org/piracy-and-armed-robbery-prone-areas-and-warnings/), [RC3C02: International Energy Agency](https://www.iea.org/reports/global-critical-minerals-outlook-2026/executive-summary)

**substitutes:** Alternate origin/port/route with correct product and verified capacity

**thresholds:** Delay exceeds usable cover or application deadline

**time horizon:** Days to months

**to:** fertilizer

**uncertainty:** No California exposure or current route-wide closure established


---

**activation status:** Structural concentration and planning dependency; project-level activation unverified

**buffers:** Repair, compatible spares, diversified processing and equipment procurement

**confirm:** Documented input-related commissioning slippage without alternatives

**dependent system:** grid

**falsify:** Timely equipment delivery or effective substitution

**from:** industrial

**id:** EDGE21

**initiating stress:** Concentrated equipment and battery inputs

**mechanism:** A substitute can be available as a design but not in the required grade, equipment, workforce or delivery slot; LFP manufacturing uses purified phosphoric acid.

**Sources:** [RC3C02: International Energy Agency](https://www.iea.org/reports/global-critical-minerals-outlook-2026/executive-summary), [RC3C03: International Energy Agency](https://www.iea.org/reports/global-critical-minerals-outlook-2025/executive-summary), [EFS06: U.S. Department of Energy, Alternative Fuels Data Center](https://afdc.energy.gov/fuels/electricity-infrastructure-development)

**substitutes:** Suitable alternate chemistry/design after engineering review; preserve functioning assets

**thresholds:** Verified critical orders delay essential commissioning or repair

**time horizon:** Months to years

**to:** grid

**uncertainty:** No evidence LFP demand caused current fertilizer curtailments; grade conversions are not automatic

**priority rule:** Consequential interaction + independent evidence + actionable response; no opaque score

**reserve independence rule:** Stress-test the fallback under the same initiating event. Trace shared suppliers, routes, grids, funders, staff, tenure and replenishment; multiple names need not mean independent capacity.

## review decisions

**claim:** The US has already fallen below 100m barrels of distillates.

**decision:** Rejected as current fact

**id:** REV01

**reason:** It is a forecast; Sept11 observed107.859m and three builds.

**Sources:** [SRC03: EIA](https://www.eia.gov/dnav/pet/pet_stoc_wstk_a_epd0_sae_mbbl_w.htm), [SRC04: EIA](https://www.eia.gov/outlooks/steo/)


---

**claim:** Diesel price stress proves a nationwide physical shortage or trucking failure wave.

**decision:** Downgraded to cost-pressure watch

**id:** REV02

**reason:** Delivered-service and carrier failure data not established; refinery output and stock builds buffer.

**Sources:** [SRC02: EIA](https://ir.eia.gov/wpsr/wpsrsummary.pdf), [SRC24: Reuters](https://www.reuters.com/business/energy/record-us-diesel-prices-squeeze-farmers-food-prices-may-rise-2026-09-18/)


---

**claim:** Aggregate cereal stocks remove food risk.

**decision:** Rejected

**id:** REV03

**reason:** Location, affordability, nutrients, payment and transport remain distinct.

**Sources:** [SRC06: FAO](https://www.fao.org/worldfoodsituation/csdb/en/), [SRC24: Reuters](https://www.reuters.com/business/energy/record-us-diesel-prices-squeeze-farmers-food-prices-may-rise-2026-09-18/)


---

**claim:** BART cuts have occurred and buses can absorb displaced riders.

**decision:** Rejected

**id:** REV04

**reason:** Contingency differs from operating plan; SFMTA shares funding pressure.

**Sources:** [SRC08: BART](https://www.bart.gov/sites/default/files/2026-09/FY27%20Adopted%20Budget%20Memo_FINAL_SIGNED.pdf), [SRC09: SFMTA](https://www.sfmta.com/projects/sfmta-budget-planning-fy-2026-27-and-fy-2027-28)


---

**claim:** California is approaching systemwide electricity failure.

**decision:** Unsupported by admitted evidence

**id:** REV05

**reason:** Improved modeled adequacy; local recovery and coincident extremes are separate.

**Sources:** [SRC10: CAISO](https://www.caiso.com/documents/2026-summer-loads-and-resources-assessment.pdf)


---

**claim:** Tariffs have caused the observed BART deferrals.

**decision:** Causal attribution withheld

**id:** REV06

**reason:** Budget does not establish that cause; product-specific procurement evidence needed.

**Sources:** [SRC08: BART](https://www.bart.gov/sites/default/files/2026-09/FY27%20Adopted%20Budget%20Memo_FINAL_SIGNED.pdf), [SRC18: White House](https://www.whitehouse.gov/presidential-actions/2026/06/further-adjusting-the-tariff-regimes-for-imports-of-aluminum-steel-and-copper-into-the-united-states/)


---

**claim:** All fertilizer types are contracting.

**decision:** Rejected

**id:** REV07

**reason:** Potash and H1 phosphate production improved in cited producer record.

**Sources:** [SRC07: Nutrien](https://www.nutrien.com/news/press-releases/nutrien-reports-second-quarter-2026-results-1753)


---

**claim:** National social hostility is demonstrably rising now.

**decision:** Not established

**id:** REV08

**reason:** 2025 matched reported hate incidents declined; current/local lanes unmeasured.

**Sources:** [SRC14: FBI](https://www.fbi.gov/news/press-releases/fbi-releases-2025-reported-crimes-in-the-nation-statistics)


---

**claim:** Regional rosters or planning margins are spare rescue capacity.

**decision:** Rejected until donor gate satisfied

**id:** REV09

**reason:** Availability, commitments, time, routes and simultaneous hazard must be checked.

**Sources:** [SRC10: CAISO](https://www.caiso.com/documents/2026-summer-loads-and-resources-assessment.pdf), [SRC15: CDEMA](https://www.cdema.org/index.php/cdemanews/categories/press-releases/146-press-releases/1870-cdema-launches-regional-recovery-experts-roster-to-strengthen-caribbean-recovery), [SRC17: ENTSO-E](https://www.entsoe.eu/outlooks/seasonal/)


---

**claim:** Saudi October cancellations have two independent confirmations.

**decision:** Quarantined as warning evidence

**id:** REV10

**reason:** Reuters explicitly relays unverified Bloomberg report; one source chain.

**Sources:** [SRC25: Reuters relaying Bloomberg](https://www.reuters.com/business/energy/aramco-halts-october-crude-deliveries-some-european-refiners-after-pipeline-2026-09-18/)


---

**claim:** SIG01, SIG02, CL01, RES01

**decision:** confirmed

**id:** RC002-IR01

**reason:** EIA retail diesel table reports US $6.285/gal and California $8.039/gal on September 14, with weekly increases $0.318 and $0.275. September 11 national distillate stocks 107.859m barrels follow three builds from August 21 at 103.391m. WPSR gives 13% below five-year seasonal average and 96.8% refinery utilization. Retain cost pressure and thin/rebuilding bulk reserve. Neither price nor these inventory estimates establishes terminal stockouts or failures to deliver. Retail includes taxes and is not a farm off-road contract price.

**reviewer:** independent_review

**scope:** RC-001 primary-claim check; not final peer approval of RC-002

**Sources:** [SRC01: EIA](https://www.eia.gov/petroleum/gasdiesel/), [SRC02: EIA](https://ir.eia.gov/wpsr/wpsrsummary.pdf), [SRC03: EIA](https://www.eia.gov/dnav/pet/pet_stoc_wstk_a_epd0_sae_mbbl_w.htm)


---

**claim:** SIG03, SRC04

**decision:** corrected

**id:** RC002-IR02

**reason:** September STEO was released September 9 using September 3 inputs. Its below-100m September inventory outcome remains a forecast. September 11 weekly stock above that threshold does not falsify the forecast for the still-unfinished month. Current STEO also records a correction: original notable-changes table referenced gasoline crack-spread figures under a distillate label. Keep warning against reporting the forecast as observed, but do not call the forecast refuted or obsolete solely from one mid-month estimate. Retain correction metadata before any crack-spread comparisons. No RC-001 numerical price claim required correction.

**reviewer:** independent_review

**scope:** RC-001 primary-claim check; not final peer approval of RC-002

**Sources:** [SRC04: EIA](https://www.eia.gov/outlooks/steo/), [SRC03: EIA](https://www.eia.gov/dnav/pet/pet_stoc_wstk_a_epd0_sae_mbbl_w.htm)


---

**claim:** SIG08, SIG09, RES03, CL02

**decision:** confirmed

**id:** RC002-IR03

**reason:** BART September FY27 adopted budget assumes November 2026 measure passage and April 2027 receipts; tables show $52.1m capital deferrals and $88.5m borrowing (executive summary rounds to $52m/$89m). It also anticipates $52.4m emergency carryforward, amount not final until close. Alternative Service Plan is contingent, subject to further Board action, and not the adopted operating timetable. SFMTA April 21 budget protects regular Muni/paratransit FY26-27, with later cuts conditional on funding. Keep fiscal-capacity warning conditional. Capital deferral can shift burden into recovery, but no present rail failure or specific reliability loss has been established. Treat carryforward as separate from capital deferral and no neighboring transit donor surplus is quantified.

**reviewer:** independent_review

**scope:** RC-001 primary-claim check; not final peer approval of RC-002

**Sources:** [SRC08: BART](https://www.bart.gov/sites/default/files/2026-09/FY27%20Adopted%20Budget%20Memo_FINAL_SIGNED.pdf), [SRC09: SFMTA](https://www.sfmta.com/projects/sfmta-budget-planning-fy-2026-27-and-fy-2027-28)


---

**claim:** SIG06, SIG07, ISL01

**decision:** confirmed

**id:** RC002-IR04

**reason:** Nutrien August 5 disclosure gives Q2 phosphate P2O5 operating rate 75% versus 79%, H1 P2O5 output 656k versus 615k tonnes, and H1 potash output 7.656m versus 6.820m tonnes. Sulfur constraints/global reductions are management characterization. These are different nutrients and comparison periods. Retain mixed fertilizer signal and do not infer an overall fertilizer collapse, a current potash surplus for emergency export, or nutrient interchangeability. Available uncommitted surplus remains unknown.

**reviewer:** independent_review

**scope:** RC-001 primary-claim check; not final peer approval of RC-002

**Sources:** [SRC07: Nutrien](https://www.nutrien.com/news/press-releases/nutrien-reports-second-quarter-2026-results-1753)


---

**claim:** SIG10, SIG16, RES04, ISL03

**decision:** confirmed

**id:** RC002-IR05

**reason:** CAISO May assessment reports a modeled 2,547 MW surplus relative to its 0.1 LOLE target using existing and anticipated resources, expressly excluding certain coincident extremes and within-zone transmission limits. ENTSO-E summer page supports generally favorable adequacy with local exceptions, while describing a scenario assessment rather than live dispatch. Reassuring planning evidence is valid, but neither source quantifies presently deployable donor reserve. Retain hourly capacity/interface/home-floor checks; do not add the CAISO modeled surplus to emergency supply as a guaranteed export pool.

**reviewer:** independent_review

**scope:** RC-001 primary-claim check; not final peer approval of RC-002

**Sources:** [SRC10: CAISO](https://www.caiso.com/documents/2026-summer-loads-and-resources-assessment.pdf), [SRC17: ENTSO-E](https://www.entsoe.eu/outlooks/seasonal/)


---

**claim:** SIG15, RES05, ISL04, SRC15, SIG11, SRC11

**decision:** confirmed

**id:** RC002-IR06

**reason:** CDEMA page carries August 30 publication, August 27 dateline and August 26 first orientation of 14 experts; all precede cutoff. This verifies a roster and coordination process, not funded idle teams or present medical surge capacity. Federal Reserve release September 18 explicitly marks August estimates preliminary and gives flat industrial output month/month, +1.4% year/year, manufacturing -0.3% month/month and +0.9% year/year. Retain improving institutional evidence and mixed industry evidence; do not infer operational rescue surplus from a roster or immediately convertible spare production from aggregate utilization. Source event/release dates checked independently.

**reviewer:** independent_review

**scope:** RC-001 primary-claim check; not final peer approval of RC-002

**Sources:** [SRC15: CDEMA](https://www.cdema.org/index.php/cdemanews/categories/press-releases/146-press-releases/1870-cdema-launches-regional-recovery-experts-roster-to-strengthen-caribbean-recovery), [SRC11: Federal Reserve](https://www.federalreserve.gov/releases/g17/current/default.htm)


---

**claim:** Phosphate strain is only a price signal

**decision:** Upgraded

**id:** RC002-CR01

**reason:** Mosaic names physical idles and curtailments. No farm stockout inferred.

**reviewer:** coordinator

**Sources:** [TRS02: The Mosaic Company](https://mosaicco.com/Article/Fertilizer-Markets-Facts-and-Context)


---

**claim:** A completed hub proves staffed outage capacity

**decision:** Not admitted

**id:** RC002-CR02

**reason:** Construction and solar use verified; outage service duration/access/drill unverified.

**reviewer:** coordinator

**Sources:** [LC_SRC02: Town of San Anselmo](https://www.sananselmo.gov/1677/Town-Hall-Resilience-Hub)


---

**claim:** A regional reserve can support any other region

**decision:** Narrowed

**id:** RC002-CR03

**reason:** CL04 global donor links removed pending a specific compatible offer, route, home reserve and staffing. Europe power is not directly exportable to California.

**reviewer:** coordinator

**Sources:** [SRC17: ENTSO-E](https://www.entsoe.eu/outlooks/seasonal/), [SRC15: CDEMA](https://www.cdema.org/index.php/cdemanews/categories/press-releases/146-press-releases/1870-cdema-launches-regional-recovery-experts-roster-to-strengthen-caribbean-recovery)


---

**claim:** Capital investment establishes hospital operating reserve

**decision:** Rejected

**id:** RC002-CR04

**reason:** Restricted capital, grant award and recurring cash are separate. Installed/licensed scanners do not prove current utilization or liquidity.

**reviewer:** coordinator

**Sources:** [RC2H01: California HCAI](https://hcai.ca.gov/facilities/health-facility-financing/distressed-hospital-loan-program/), [RC2H04: Pajaro Valley Health Care District](https://www.pvhcd.org/home-page/page/federal-cuts-put-watsonville-community-hospital-risk-partnership-way-forward), [RC2H05: Pajaro Valley Health Care District](https://www.pvhcd.org/home-page/page/new-mri-and-ct-imaging-now-available-watsonville-community-hospital)


---

**claim:** New local budget assertion independently reproduced

**decision:** Limited admission

**id:** RC002-CR05

**reason:** AC Transit source was read by specialist; coordinator reopen failed. Preserve provenance and medium confidence; existing BART/Muni evidence anchors cluster.

**reviewer:** coordinator

**Sources:** [LC_SRC03: Alameda-Contra Costa Transit District](https://www.actransit.org/sites/default/files/2026-09/FY2026-27%20District%20Adopted%20Budget%20Book.pdf)


---

**claim:** September social escalation and tariff-driven repair failure

**decision:** Remain unestablished

**id:** RC002-CR06

**reason:** Focused cycle produced no qualifying new evidence; do not treat unchanged unknowns as improvement.

**reviewer:** coordinator

**Sources:** [SRC14: FBI](https://www.fbi.gov/news/press-releases/fbi-releases-2025-reported-crimes-in-the-nation-statistics), [SRC18: White House](https://www.whitehouse.gov/presidential-actions/2026/06/further-adjusting-the-tariff-regimes-for-imports-of-aluminum-steel-and-copper-into-the-united-states/), [SRC19: White House](https://www.whitehouse.gov/presidential-actions/2026/07/further-strengthening-actions-taken-to-adjust-imports-of-aluminum-into-the-united-states/)


---

**claim:** Mosaic August 27 curtailments

**decision:** Independently confirmed operator disclosure; September restart and farmer effects unknown

**id:** RC003-IR01

**reviewer:** nutrient_network

**Sources:** [TRS02: The Mosaic Company](https://mosaicco.com/Article/Fertilizer-Markets-Facts-and-Context)


---

**claim:** SWARD fertilizer cargo and July captivity

**decision:** Independently confirmed April event and July status; September status/California link unknown

**id:** RC003-IR02

**reviewer:** nutrient_network

**Sources:** [MAR05: EUNAVFOR ATALANTA](https://eunavfor.eu/news/update-ongoing-piracy-incidents-northern-coast-somalia)


---

**claim:** IEA shared sulfur/acid dependency

**decision:** Independently confirmed July report; does not clear or close a September route

**id:** RC003-IR03

**reviewer:** nutrient_network

**Sources:** [RC3C02: International Energy Agency](https://www.iea.org/reports/global-critical-minerals-outlook-2026/executive-summary)


---

**claim:** Food banks are only supplied by rescued surplus

**decision:** Rejected; purchased and government channels documented, with own funding/logistics constraints

**id:** RC003-CR01

**reviewer:** coordinator

**Sources:** [EFS02: Alameda County Community Food Bank](https://www.accfb.org/wp-content/uploads/2026/01/ACCFB-2025-Audit-FS.pdf), [EFS03: Alameda County Community Food Bank](https://www.accfb.org/annual-report-2025/), [EFS07: U.S. Department of Agriculture, Agricultural Marketing Service](https://www.ams.usda.gov/selling-food)


---

**claim:** San Anselmo is a fully tested public outage lifeboat

**decision:** Downgraded to constructed infrastructure and solar operation; public activation/endurance unknown

**id:** RC003-CR02

**reviewer:** coordinator

**Sources:** [LC_SRC02: Town of San Anselmo](https://www.sananselmo.gov/1677/Town-Hall-Resilience-Hub)


---

**claim:** Bayer is responsible for current sulfur constraint

**decision:** Not established; separate corporate watch and input-chain evidence

**id:** RC003-CR03

**reviewer:** coordinator

**Sources:** [BAY01: U.S. EPA](https://www.epa.gov/ingredients-used-pesticide-products/glyphosate), [TRS02: The Mosaic Company](https://mosaicco.com/Article/Fertilizer-Markets-Facts-and-Context)


---

**claim:** Several vendors or partners guarantee independent rescue

**decision:** Rejected as an assumption; shared upstream failures and donor floors must be tested

**id:** RC003-CR04

**reviewer:** coordinator

**Sources:** [EFS03: Alameda County Community Food Bank](https://www.accfb.org/annual-report-2025/), [MAR08: California ISO](https://www.caiso.com/about/our-business/regional-collaboration)


---

**claim:** Conditional new edges and reserve claims

**decision:** Scoped pass with limitations for EDGE15-21 and RES15-18; reviewer authored nutrient inputs; pre-final hash and full limits preserved in closing_review.json

**id:** RC003-SR01

**reviewer:** nutrient_network_review

**safety rule:** A donor retains protected demand and contingency reserve; route/compatibility constrain assistance.

