# Global Trade Atlas — free-data fidelity

Goal: assemble a layered global logistics map without pretending free data gives commercial-terminal fidelity everywhere.

## Recommended layers

| Layer | Useful free sources | Typical fidelity | Main blind spots |
|---|---|---|---|
| Country↔country merchandise by HS product | UN Comtrade | High historically; monthly where reported | lag, revisions, customs classification, re-exports, mirror discrepancies |
| Oil/product balances | JODI Oil | High/medium, monthly, >90 countries, roughly one-month lag | broad product buckets, uneven country completeness, limited bilateral destination detail |
| Maritime port/chokepoint activity | IMF PortWatch | High for aggregate maritime movement; daily since 2019 | not exact cargo manifest; estimates/nowcasts; inland legs absent |
| Container connectivity | UNCTADstat | High for network structure; monthly/quarterly | not individual cargoes or short-lived disruptions |
| Port efficiency | World Bank CPPI | High annual comparative port-turnaround evidence | container focus; yearly lag |
| Shipment/logistics performance | World Bank LPI 2.0 | Strong structural comparison | not a live operational feed |
| AIS vessel presence | Global Fishing Watch public presence | Medium/high for vessel-presence patterns, days-scale | AIS gaps/spoofing, identity caveats, cargo content usually unknown |
| National official customs/port/rail data | each country | Potentially highest for its measured field | inconsistent APIs, language, methodology, revisions |
| News/trade reporting | Reuters etc. | Medium/high for current allocation/trader context | source-based claims, not the same as administrative/customs proof |
| Inland road/rail/trucking | fragmented national/open sources | Low/medium globally | no single free global operational network dataset |
| Cargo-by-vessel / refinery-to-buyer chain | commercial Kpler/Vortexa/etc. | Low with free data | high-fidelity commercial data usually paid |

## Fidelity should attach to a series, not a country stereotype

Avoid a single "country trust score."

For every metric keep:
- authority/source;
- methodology;
- reporting obligation;
- update cadence;
- revision history;
- continuity breaks;
- customs/product definitions;
- missingness;
- mirror-trade discrepancy;
- external consistency with port/AIS/partner data;
- known policy/method changes.

If political/regime change is suspected of affecting data quality, require evidence of a statistical-method/reporting change or a measurable divergence. Do not encode "regime X lies" as a hidden prior.

## Mirror-trade check

For an export A→B:
- compare A-reported exports to B-reported imports;
- align valuation, lag, HS code and shipping time;
- record persistent discrepancy;
- compare with port/AIS direction when available.

Persistent mirror gaps can reveal re-export hubs, classification/timing differences, under/over-reporting or changing routes. They are not self-interpreting.

## Expected overall map

For free, Dis-Unity can plausibly reach:
- **high fidelity:** large country-product trade corridors after customs publication;
- **high/medium:** current maritime chokepoint/port activity and network connectivity;
- **medium:** current energy-product flow direction using customs + JODI + trade reporting;
- **low/medium:** exact cargo assignment to individual vessels/refineries/buyers;
- **low:** comprehensive global inland truck/rail capacity and private inventory.

The web should display this as layered uncertainty, not one blended certainty color.
