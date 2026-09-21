# ACTIVE_SIGNALS

Cycle RC-001; cutoff 2026-09-20.

**id:** SIG01

**title:** Diesel cost pressure

**geography:** United States / California

## systems

- diesel
- trucking

**epistemic label:** FACT

**observation:** Sept 14 retail diesel: US $6.285/gal (+$0.318/week), California $8.039 (+$0.275/week); taxes included.

**direction:** worsening

**Sources:** [SRC01: EIA](https://www.eia.gov/petroleum/gasdiesel/)

**confidence:** high for survey

**freshness:** 2026-09-14

**event id:** EV-DIESEL-PRICE

**status:** active

**implication:** Essential transport and harvest cash needs rise before any physical rationing occurs.

**first seen cycle:** RC-001


---

**id:** SIG02

**title:** Thin but rebuilding distillate stocks

**geography:** United States; PADD regions

## systems

- diesel

**epistemic label:** FACT

**observation:** Sept 11 stocks 107.859m barrels, up from 103.391m Aug 21 through three weekly builds; 13% below five-year seasonal average. Refinery utilization 96.8%.

**direction:** mixed

**Sources:** [SRC02: EIA](https://ir.eia.gov/wpsr/wpsrsummary.pdf), [SRC03: EIA](https://www.eia.gov/dnav/pet/pet_stoc_wstk_a_epd0_sae_mbbl_w.htm)

**confidence:** high for weekly estimates

**freshness:** 2026-09-11

**event id:** EV-DISTILLATE-BALANCE

**status:** active

**implication:** Cost stress coexists with recovery in stocks and limited refinery headroom; regional deliverability remains a gap.

**first seen cycle:** RC-001


---

**id:** SIG03

**title:** Below-100m stock forecast is not yet observed

**geography:** United States

## systems

- diesel

**epistemic label:** FACT

**observation:** Sept 9 STEO projected September distillate stocks below 100m barrels; later Sept 11 weekly observation remains above that level.

**direction:** unclear

**Sources:** [SRC04: EIA](https://www.eia.gov/outlooks/steo/), [SRC03: EIA](https://www.eia.gov/dnav/pet/pet_stoc_wstk_a_epd0_sae_mbbl_w.htm)

**confidence:** high on forecast/observation distinction

**freshness:** Forecast frozen 2026-09-03; later observation 2026-09-11

**event id:** EV-DISTILLATE-BALANCE

**status:** downgraded

**implication:** Do not report the forecast as current stock or use stock/use as a countdown to exhaustion.

**first seen cycle:** RC-001


---

**id:** SIG04

**title:** Farm operating costs tighten

**geography:** United States

## systems

- agriculture
- fertilizer
- diesel

**epistemic label:** FACT

**observation:** USDA forecasts 2026 fertilizer/lime/soil conditioner expense +15.3%, fuel/oils +28.8%; inflation-adjusted net farm income -5.5%, still above 2006–25 average. Direct payments forecast $47.4bn.

**direction:** mixed

**Sources:** [SRC05: USDA ERS](https://www.ers.usda.gov/topics/farm-economy/farm-sector-income-finances/farm-sector-income-forecast)

**confidence:** high that forecast was issued; medium realized outcome

**freshness:** 2026-09-03 forecast

**event id:** EV-FARM-FORECAST

**status:** active

**implication:** Cash-flow exposure differs by farm; aid/payment timing and crop receipts buffer some producers.

**first seen cycle:** RC-001


---

**id:** SIG05

**title:** Cereal buffer substantial but unevenly accessible

**geography:** Global / Black Sea / Americas

## systems

- agriculture
- food_logistics

**epistemic label:** FACT

**observation:** FAO forecasts 2026/27 cereal stocks/use 31.6%, historically comfortable; Black Sea logistics constraints may accumulate stocks behind export bottlenecks.

**direction:** mixed

**Sources:** [SRC06: FAO](https://www.fao.org/worldfoodsituation/csdb/en/)

**confidence:** medium for outlook

**freshness:** 2026-09-04 forecast

**event id:** EV-CEREAL-OUTLOOK

**status:** active

**implication:** Global abundance does not guarantee delivery or affordable food in a specific place.

**first seen cycle:** RC-001


---

**id:** SIG06

**title:** Sulfur pressure on phosphate

**geography:** North America / global fertilizer trade

## systems

- fertilizer
- industrial

**epistemic label:** FACT

**observation:** Nutrien attributes phosphate pressure to sulfur costs and availability. Its Q2 P2O5 operating rate was 75% vs 79%; H1 output increased to 656k tonnes from 615k.

**direction:** mixed

**Sources:** [SRC07: Nutrien](https://www.nutrien.com/news/press-releases/nutrien-reports-second-quarter-2026-results-1753)

**confidence:** high company metrics; medium broad applicability

**freshness:** Q2/H1 2026, released Aug 5

**event id:** EV-NUTRIEN-Q2

**status:** active

**implication:** Unexpected feedstock dependency deserves a separate phosphate watch; a universal fertilizer shutdown is unsupported.

**first seen cycle:** RC-001


---

**id:** SIG07

**title:** Potash capacity offers a buffer

**geography:** Canada / global buyers

## systems

- fertilizer

**epistemic label:** FACT

**observation:** Nutrien reports record H1 potash production, 7.656m tonnes vs 6.820m a year earlier.

**direction:** improving

**Sources:** [SRC07: Nutrien](https://www.nutrien.com/news/press-releases/nutrien-reports-second-quarter-2026-results-1753)

**confidence:** high company disclosure

**freshness:** H1 2026, released Aug 5

**event id:** EV-NUTRIEN-Q2

**status:** active

**implication:** Output is evidence of supply strength; available uncommitted export surplus remains unknown. Potash is not interchangeable with phosphate.

**first seen cycle:** RC-001


---

**id:** SIG08

**title:** BART fiscal bridge preserves service with future costs

**geography:** Bay Area

## systems

- transit
- municipal

**epistemic label:** FACT

**observation:** FY27 budget assumes November revenue measure passage and April 2027 receipts; bridge includes $52m capital deferrals and $89m borrowing. Current service preserved; alternative service plan conditional.

**direction:** mixed

**Sources:** [SRC08: BART](https://www.bart.gov/sites/default/files/2026-09/FY27%20Adopted%20Budget%20Memo_FINAL_SIGNED.pdf)

**confidence:** high budget terms

**freshness:** September 2026 FY27 adopted budget

**event id:** EV-BART-FY27

**status:** active

**implication:** Liquidity bridge buys time while transferring some load to future budgets and asset renewal.

**first seen cycle:** RC-001


---

**id:** SIG09

**title:** Muni finance shares the regional constraint

**geography:** San Francisco

## systems

- transit
- municipal

**epistemic label:** FACT

**observation:** April 21 adopted budget protects regular Muni/paratransit in FY26-27; significant cuts from FY27-28 remain conditional on funding. Agency describes $307m deficit.

**direction:** mixed

**Sources:** [SRC09: SFMTA](https://www.sfmta.com/projects/sfmta-budget-planning-fy-2026-27-and-fy-2027-28)

**confidence:** high agency budget description

**freshness:** Budget decision 2026-04-21; current page

**event id:** EV-SFMTA-FY27

**status:** active

**implication:** Another transit operator cannot be assumed to be a funded spare compartment.

**first seen cycle:** RC-001


---

**id:** SIG10

**title:** California generation adequacy improved in planning

**geography:** CAISO area

## systems

- grid

**epistemic label:** FACT

**observation:** May assessment models 2,547 MW margin relative to its reliability target. It includes anticipated additions and does not cover all coincident extreme events or local constraints.

**direction:** improving

**Sources:** [SRC10: CAISO](https://www.caiso.com/documents/2026-summer-loads-and-resources-assessment.pdf)

**confidence:** high assessment; medium current applicability

**freshness:** May 2026 planning snapshot

**event id:** EV-CAISO-SUMMER

**status:** active

**implication:** Downgrade statewide insufficiency assumption; assess local recovery/fuel/equipment separately.

**first seen cycle:** RC-001


---

**id:** SIG11

**title:** Industrial output contradicts blanket decline

**geography:** United States

## systems

- industrial
- construction

**epistemic label:** FACT

**observation:** August total industrial output flat month/month and +1.4% year/year; manufacturing -0.3% month/month and +0.9% year/year.

**direction:** mixed

**Sources:** [SRC11: Federal Reserve](https://www.federalreserve.gov/releases/g17/current/default.htm)

**confidence:** high preliminary aggregate

**freshness:** August 2026, released Sept 18

**event id:** EV-G17-AUG

**status:** active

**implication:** Sector-specific stress is plausible; broad industrial collapse not established.

**first seen cycle:** RC-001


---

**id:** SIG12

**title:** Credit access varies by borrower

**geography:** United States

## systems

- industrial
- municipal

**epistemic label:** FACT

**observation:** Q2 bank survey: C&I standards basically unchanged across firm sizes; consumer and nonbank lending remain relatively tight by historical comparison.

**direction:** mixed

**Sources:** [SRC12: Federal Reserve](https://www.federalreserve.gov/data/sloos/sloos-202607.htm)

**confidence:** medium; bank survey

**freshness:** Q2 2026, published Aug 3

**event id:** EV-SLOOS-Q2

**status:** active

**implication:** Do not describe all business credit as freezing; household and nonbank financing deserve distinct checks.

**first seen cycle:** RC-001


---

**id:** SIG13

**title:** Labor reallocation and healthcare growth divergence

**geography:** United States

## systems

- labor
- industrial
- healthcare

**epistemic label:** FACT

**observation:** August manufacturing employment +16k, healthcare +13k versus prior 12-month average +32k; information employment -23k. Transportation/warehousing little changed.

**direction:** mixed

**Sources:** [SRC13: BLS](https://www.bls.gov/news.release/empsit.nr0.htm)

**confidence:** high preliminary estimates; low causal attribution

**freshness:** August 2026, released Sept 4

**event id:** EV-JOBS-AUG

**status:** active

**implication:** No evidence released workers can immediately fill licensed or technical roles; healthcare headcount does not measure care access.

**first seen cycle:** RC-001


---

**id:** SIG14

**title:** Reported hate-crime trend improved in prior year

**geography:** United States

## systems

- social

**epistemic label:** FACT

**observation:** FBI matched reporting sample: incidents fell 7.0% from 11,404 in 2024 to 10,606 in 2025. Total all-reporting incidents 10,881 is a different sample.

**direction:** improving

**Sources:** [SRC14: FBI](https://www.fbi.gov/news/press-releases/fbi-releases-2025-reported-crimes-in-the-nation-statistics)

**confidence:** high reported matched trend; low for 2026 climate

**freshness:** 2025 data, published 2026-08-14

**event id:** EV-FBI-2025

**status:** active

**implication:** Retain improving evidence. Current rhetoric, organization, intimidation and institutional trust remain unmeasured.

**first seen cycle:** RC-001


---

**id:** SIG15

**title:** Caribbean regional recovery coordination grows

**geography:** Caribbean

## systems

- healthcare
- labor
- municipal

**epistemic label:** FACT

**observation:** CDEMA recovery roster launched with first orientation for 14 experts on Aug 26; announced Aug 27 and published Aug 30.

**direction:** improving

**Sources:** [SRC15: CDEMA](https://www.cdema.org/index.php/cdemanews/categories/press-releases/146-press-releases/1870-cdema-launches-regional-recovery-experts-roster-to-strengthen-caribbean-recovery)

**confidence:** high launch; unknown deployable reserve

**freshness:** 2026-08-26 to 2026-08-30

**event id:** EV-CDEMA-ROSTER

**status:** active

**implication:** Institutional complementary capacity; roster count is not a verified deployment commitment.

**first seen cycle:** RC-001


---

**id:** SIG16

**title:** European electricity seasonal buffer

**geography:** European interconnected systems

## systems

- grid

**epistemic label:** FACT

**observation:** ENTSO-E summer assessment finds broadly favorable adequacy, with specific risks in Moldova, Ireland, Malta and Cyprus.

**direction:** mixed

**Sources:** [SRC17: ENTSO-E](https://www.entsoe.eu/outlooks/seasonal/)

**confidence:** medium current relevance

**freshness:** Summer 2026 assessment; exact publication date unverified

**event id:** EV-EU-SUMMER

**status:** active

**implication:** Cross-border coordination is a buffer; live export reserve must be measured by time and interconnector.

**first seen cycle:** RC-001


---

**id:** SIG17

**title:** Metal trade rules create differentiated exposure

**geography:** United States / trade partners

## systems

- trade
- construction
- industrial

**epistemic label:** FACT

**observation:** June proclamation adjusted specified metal-product duties effective June 8. July 20 authorized reduced-duty incentives tied to approved new/refurbished primary-aluminum production.

**direction:** mixed

**Sources:** [SRC18: White House](https://www.whitehouse.gov/presidential-actions/2026/06/further-adjusting-the-tariff-regimes-for-imports-of-aluminum-steel-and-copper-into-the-united-states/), [SRC19: White House](https://www.whitehouse.gov/presidential-actions/2026/07/further-strengthening-actions-taken-to-adjust-imports-of-aluminum-into-the-united-states/)

**confidence:** high existence of measures; low project-level impact

**freshness:** June/July 2026 decisions

**event id:** EV-METAL-RULES

**status:** active

**implication:** Need product-origin-specific quotes, HTS and delivery evidence before attributing repair delays to tariffs.

**first seen cycle:** RC-001


---

**id:** SIG18

**title:** Grid manufacturing expansion has lead time

**geography:** United States

## systems

- industrial
- grid

**epistemic label:** EARLY SIGNAL

**observation:** Reuters reported a Sept 2025 Hitachi $1bn US grid-manufacturing plan including a Virginia transformer facility targeted for 2028.

**direction:** improving

**Sources:** [SRC23: Reuters](https://www.reuters.com/business/energy/hitachi-invest-1-billion-produce-power-grid-components-us-2025-09-04/)

**confidence:** medium announcement; current progress unknown

**freshness:** Late discovery: 2025-09-04 announcement

**event id:** EV-HITACHI-EXPANSION

**status:** watch

**implication:** Planned industrial growth cannot be counted as a September 2026 spare transformer.

**first seen cycle:** RC-001


---

**id:** SIG19

**title:** Harvest and refrigerated freight cost propagation

**geography:** US farm/produce corridors

## systems

- diesel
- trucking
- food_logistics

**epistemic label:** EARLY SIGNAL

**observation:** Sept 18 reporting describes named farmers absorbing fuel increases and elevated refrigerated freight prices; some operators already adapting equipment use.

**direction:** worsening

**Sources:** [SRC24: Reuters](https://www.reuters.com/business/energy/record-us-diesel-prices-squeeze-farmers-food-prices-may-rise-2026-09-18/)

**confidence:** medium reporting; not representative

**freshness:** 2026-09-18

**event id:** EV-HARVEST-LOGISTICS

**status:** active

**implication:** Observed price/cash-flow transmission warrants deepening; predicted trucking bankruptcies remain unconfirmed.

**first seen cycle:** RC-001


---

**id:** SIG20

**title:** October European crude-delivery report needs corroboration

**geography:** Saudi export routes / Europe

## systems

- trade
- diesel

**epistemic label:** EARLY SIGNAL

**observation:** Reuters relays Bloomberg report of October supply cancellations affecting at least two refiners, explicitly unverified by Reuters; alternatives also reported.

**direction:** unclear

**Sources:** [SRC25: Reuters relaying Bloomberg](https://www.reuters.com/business/energy/aramco-halts-october-crude-deliveries-some-european-refiners-after-pipeline-2026-09-18/)

**confidence:** low pending primary corroboration

**freshness:** Report 2026-09-18; delivery horizon October

**event id:** EV-SAUDI-DELIVERY

**status:** quarantined_for_warning

**implication:** Material follow-up lead; do not present multiple outlets in one chain as independent evidence.

**first seen cycle:** RC-001

