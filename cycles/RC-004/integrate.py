"""Reproducible RC-004 candidate assembly. Never writes canonical state."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'cycles/RC-004'
DAY = '2026-09-21'
state = json.loads((OUT / 'baseline.json').read_text())
aliases = {}
by_url = {s['url'].rstrip('/'): s for s in state['SOURCE_LEDGER']}

def save(path, value):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n')

def admit(source, verification=None):
    source = copy.deepcopy(source)
    source.setdefault('retrieved_at', DAY)
    source['grade'] = source['grade'][0]
    if isinstance(source['limitations'], list):
        source['limitations'] = ' '.join(source['limitations'])
    url = source['url'].rstrip('/')
    if url in by_url:
        old = by_url[url]
        aliases[source['id']] = old['id']
        old['last_verified_at'] = DAY
        old.setdefault('verification_history', []).append({
            'cycle': 'RC-004', 'source_alias': source['id'],
            'observation_period': source['observation_period'],
            'note': verification or 'Reopened in bounded specialist research; see submitted packet. This is not another independent source.'})
        return old['id']
    if verification:
        source['coordinator_verification'] = verification
    state['SOURCE_LEDGER'].append(source)
    by_url[url] = source
    aliases[source['id']] = source['id']
    return source['id']

for name in ['fuel_cover', 'sulfur_leadtime', 'food_horizons', 'commons_access', 'maritime_access']:
    packet = json.loads((ROOT / f'inbox/RC-004/{name}.json').read_text())
    for source in packet['sources']:
        if source['id'] == 'RC4M06':
            continue  # Search excerpt only; no operational claim admitted from it.
        note = None
        if source['id'] == 'RC4C03':
            source['publication_date'] = '2022-06-09'
            source['observation_period'] = 'Historical June 2022 commissioning; full operator page read by coordinator on 2026-09-21'
            source['limitations'] = 'Coordinator opened full operator release. Historical commissioning of the Humboldt airport/Coast Guard microgrid; not an Oakland site, current endurance test, uncommitted capacity or an unlimited-power guarantee.'
            note = 'Full primary page read by coordinator on 2026-09-21, upgrading the original agent search-only lead.'
        if source['id'] == 'RC4C04':
            source['observation_period'] = 'Undated current program page fully read by coordinator on 2026-09-21; next-cohort contact date December 1, 2026'
            source['limitations'] = 'Coordinator opened full program page. Feasibility/technical assistance and installation incentives; first cohort installation underway. December 1, 2026 contact date for next cohort is not a grant award or commissioned service.'
            note = 'Full program page read by coordinator on 2026-09-21; public contact verified. Original checkpoint remains unchanged.'
        admit(source, note)

def src(id, title, publisher, url, published, observation, limitations, grade='A'):
    return dict(id=id, title=title, publisher=publisher, url=url, publication_date=published,
                observation_period=observation, retrieved_at=DAY, grade=grade, limitations=limitations)

rail_sources = [
    src('RC4R01', 'Caltrain Commences Fully Electrified Service', 'Caltrain',
        'https://www.caltrain.com/news/caltrain-commences-fully-electrified-service', '2024-09-21',
        'September 2024 passenger service launch', 'SF–San Jose passenger corridor; diesel freight and southern connector remain. Not a national fleet count.'),
    src('RC4R02', 'Governor Newsom and new High-Speed Rail CEO celebrate Caltrain electrification', 'California Governor',
        'https://www.gov.ca.gov/2024/08/10/governor-newsom-and-new-high-speed-rail-ceo-celebrate-caltrains-electrification-as-key-part-of-high-speed-rail-plan/', '2024-08-10',
        'Construction began July 2017; service launch in 2024', 'One corridor benchmark; planning preceded construction. Not a universal conversion schedule.'),
    src('RC4R03', 'Freight Rail and Climate Change', 'Association of American Railroads',
        'https://www.aar.org/issue/freight-rail-climate-change/', None,
        'Undated industry efficiency description retrieved September 2026',
        'Industry association estimate: freight rail averages 3–4 times truck fuel efficiency. Does not establish spare train paths, route-specific savings or independence from diesel.', 'B'),
    src('RC4R05', 'Class I Railroad Locomotive Fleet by Year Built', 'Bureau of Transportation Statistics',
        'https://www.bts.gov/content/class-i-railroad-locomotive-fleet-year-built', None,
        'Current landing page; linked table_01_32_072726.xlsx not retrieved',
        'Landing page read; workbook unavailable. No 2026 locomotive total or diesel/electric share admitted. Locomotive counts are not train movements.')
]
rail_packet = {
    'agent': 'coordinator_rail_recovery', 'cycle_id': 'RC-004',
    'status': 'bounded_recovery_of_delivered_agent_findings', 'cutoff': DAY,
    'attribution': 'Rail specialist delivered a final source packet but saved only its initial checkpoint. Coordinator preserved its delivered findings and reopened the sources; this is not a second independent research pass.',
    'sources': rail_sources,
    'findings': [
        'Diesel-electric traction already uses electric motors; the change is the energy source and its supporting infrastructure, not simply exchanging the traction motor.',
        'Caltrain provides a completed corridor example: construction July 2017, full electric passenger service September 2024, excluding earlier planning.',
        'Existing compatible rail can conserve diesel before electrification, subject to paths, terminals, crews and last-mile capacity.',
        'A current national diesel/electric fleet split was not verified; no exact count is admitted.'
    ],
    'limitations': ['No route capacity audit, fleet procurement schedule or current national fuel-type census.', 'Conversion duration for any particular yard, branch or mainline remains project-specific.']
}
save('inbox/RC-004/coordinator_rail_recovery.json', rail_packet)
for s in rail_sources:
    admit(s, 'Coordinator reopened full primary landing/page; underlying BTS workbook remains unavailable.')

extra_sources = [
    src('RC4X01', 'Shelf-Stable Food Safety', 'USDA Food Safety and Inspection Service',
        'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/shelf-stable-food', None,
        'Current storage guidance retrieved September 2026',
        'Guidance for intact properly stored commercial packages; low-acid canned food quality guidance 2–5 years. Not stock actually held by any food bank or safe duration after opening.'),
    src('RC4X02', 'Two New Ownership Opportunities', 'Oakland Community Land Trust',
        'https://oakclt.org/two-new-ownership-opportunities/', '2024-07-01',
        'Two rehabilitated homes offered in July 2024',
        'Historical offering with expired July 2024 deadline. Evidence of later activity, not present available property.'),
    src('RC4X03', 'OakCLT Properties', 'Oakland Community Land Trust',
        'https://oakclt.org/about/oakclt-properties/', None,
        'Portfolio page; metadata February 2025; read September 2026',
        'Operator-maintained project list, not a title audit, vacancy listing or independently verified financial position.'),
    src('RC4X04', 'Harvest House', 'Oakland Community Land Trust',
        'https://oakclt.org/portfolio-items/harvest-house/', None,
        'August 2019 acquisition; page metadata February 2022',
        'Documents A Diamond in the Ruff partnership; historical project record does not prove present program capacity.')
]
for s in extra_sources:
    admit(s, 'Full public page read by coordinator on 2026-09-21.')
save('inbox/RC-004/coordinator_verification.json', {
    'agent': 'coordinator_verification', 'cycle_id': 'RC-004', 'status': 'completed_bounded_checks',
    'sources': extra_sources, 'source_aliases': aliases,
    'checks': ['EIA dated tables and arithmetic', 'Japan petroleum import row and release date',
               'September IEA public summary', 'Caltrain and BTS landing pages',
               'EPA sulfur/copper and current glyphosate page; IARC monograph announcement',
               'Industrial sulfur project dates and SMM material flow', 'OakCLT later project activity',
               'Full PG&E commissioning release and Ava program page', 'Oakland compost and UC crop/nutrient guidance',
               'USDA shelf-stable storage guidance', 'EUNAVFOR and CMF September incident reports'],
    'public_contacts_verified': [
        {'organization': 'Oakland Community Land Trust', 'address': 'information@oakclt.org', 'source': 'https://oakclt.org/'},
        {'organization': 'Emerald Cities Collaborative / Ava resilience-hub program', 'address': 'cyoro@emeraldcities.org', 'source': 'https://avaenergy.org/community/resilience-hubs/'}],
    'limits': ['Only public contacts; no private mail read, email drafted in Gmail or message sent.',
               'Current voyage-time series, futures contract settlements, local inventories and donor surplus remain unknown.',
               'Root search/GitHub connector metadata failures were not treated as lack of general internet connectivity; ordinary public primary-page retrieval remained available.']
})

def refs(*ids):
    return list(dict.fromkeys(aliases.get(x, x) for x in ids))

def signal(id, title, systems, observation, sources, direction='mixed', label='FACT', event=None,
           implication='', geography=None, confidence='High within stated source scope; operational limits retained'):
    state['ACTIVE_SIGNALS'].append(dict(
        id=id, title=title, systems=systems, geography=geography or ['California', 'United States', 'Global resource and trade nodes'],
        epistemic_label=label, observation=observation, source_ids=refs(*sources), direction=direction,
        confidence=confidence, freshness='RC-004 late discovery or recheck; observation date stated explicitly, not a new event on retrieval day',
        event_id=event or f'rc004_{id.lower()}', status='Bounded evidence admitted; downstream cascade conditional',
        implication=implication, first_seen_cycle='RC-004', last_reviewed_cycle='RC-004'))

for s in state['ACTIVE_SIGNALS']:
    if s['id'] in ['SIG01', 'SIG02', 'SIG21']:
        s['last_reviewed_cycle'] = 'RC-004'
        s['rc004_note'] = 'Existing September EIA observations reconfirmed; not counted as a new price or inventory shock.'

signal('SIG43', 'Dated spot-price increase and physical product-flow contraction', ['diesel', 'trade', 'trucking'],
       'EIA NY Harbor ULSD spot increased from $4.549/gal September 4 to $5.048 September 11 (10.97%). IEA September 11 public report describes August Gulf/Russian diesel/gasoil export losses and stock draws; it reports Brent futures near $105/bbl, $21 above early August, without a contract month. No current diesel futures settlement series verified.',
       ['RC4F01', 'RC4F03'], 'worsening', event='middle_distillate_supply_2026',
       implication='Price stress and physical flow evidence coexist; spot, retail and futures measures remain separate. Do not infer local fuel run-out.')
signal('SIG44', 'Japan import quantity provides counterevidence to uniform East Asian decline', ['trade', 'diesel'],
       'Japan Customs provisional August 2026 PETROLEUM imports were 11.594 million kilolitres, up 3.6% year on year; value rose 58.7%. The category differs from the separate petroleum-products row. Customs clearance does not measure voyage delay, local distillate reserves or regional refinery suitability.',
       ['RC4F05'], 'improving', implication='Test country, product and time definitions before generalizing East Asian oil-arrival stress.', geography=['Japan', 'East Asia'])
signal('SIG45', 'Completed rail electrification supplies a years-scale conversion benchmark', ['rail', 'diesel', 'grid'],
       'Caltrain construction began July 2017 and fully electric SF–San Jose passenger service began September 21, 2024. Diesel freight and the southern passenger connector remain. This is a roughly seven-year construction example, not a universal schedule or a current national fleet census.',
       ['RC4R01', 'RC4R02', 'RC4R03'], 'improving', implication='Use existing compatible rail efficiency now; plan power-source conversion by corridor and preserve grid/terminal fallback.')
signal('SIG46', 'Venezuelan historical upgrading capability and industrial build comparators', ['sulfur', 'industrial', 'fertilizer'],
       'Equinor documented Sincor construction from 1998 and completion by January 2002. Saipem Shah initial development ran 2010–2015; a 2010 Petrofac Qatar treatment/recovery project had an announced 38-month schedule. These comparators support a years-scale scenario for major new capacity, not a current Venezuelan reserve, condition assessment or guaranteed delivery date.',
       ['RC4S02', 'RC4S03', 'RC4S04'], 'mixed', implication='Evaluate repairable existing trains first; distinguish concept start, funded construction, first output and sustained exportable surplus.')
signal('SIG47', 'Japan–Philippines sulfur/acid exchange demonstrates complementary industrial resilience', ['sulfur', 'industrial', 'trade'],
       'Sumitomo Metal Mining describes acid recovered from Japanese copper processing and sulfur from nickel processing feeding Philippine HPAL operations. This is an operating material-flow example, not uncommitted merchant acid or resilience to every shared shipping shock.',
       ['RC4S05', 'RC4S07'], 'improving', implication='Map useful coproducts before retiring parent systems; verify donor commitments and transport compatibility.', geography=['Japan', 'Philippines', 'Global resource and trade nodes'])
signal('SIG48', 'OakCLT has public activity after its Harvest House partnership', ['commons', 'municipal'],
       'OakCLT posted two rehabilitated-home offerings in July 2024 and maintains portfolio and staff/governance pages, with staff page metadata in August 2026. Harvest House records its August 2019 acquisition and A Diamond in the Ruff partnership. These establish later public presence/activity, not a current vacancy or independently audited financial strength.',
       ['RC4C01', 'RC4X02', 'RC4X03', 'RC4X04'], 'improving', implication='Investigate existing community control and modifiable space without treating listed projects as available property.', geography=['Oakland', 'Bay Area', 'California'])
signal('SIG49', 'Microgrid examples and Oakland-area support are broader than San Anselmo', ['commons', 'grid'],
       'PG&E reported the Humboldt airport/Coast Guard renewable microgrid operational in June 2022. Ava offers community resilience-hub feasibility support and installation incentives, with first-cohort installation underway and a December 1, 2026 contact date for the next cohort. Neither establishes a commissioned Oakland site or unlimited independent power.',
       ['RC4C03', 'RC4C04'], 'improving', implication='Replication is plausible with site control, essential-load design, islanding and maintenance; a commons can begin before those upgrades.', geography=['California', 'Oakland', 'Humboldt County'])
signal('SIG50', 'Oakland organics have a verified public compost return point', ['agriculture', 'commons'],
       'Oakland provides compost made from city-collected food scraps and yard waste through Acta Non Verba at West Oakland Farm Park, 2847 Peralta Street. Posted access: Tuesday–Friday 1–6 pm, Saturday 10 am–2 pm; self-load and bring containers. Stock may run out. The complete current processing route of every green-bin load is unverified.',
       ['RC4A01', 'RC4A02', 'RC4A05'], 'improving', implication='Connect gardens to an actual recovery loop while testing soil/compost and checking quantity; compost volume is not a complete plant-nutrient budget.', geography=['Oakland', 'Bay Area'])
signal('SIG51', 'Food storage and replacement production run on different clocks', ['agriculture', 'food_assistance', 'food_logistics'],
       'USDA guidance allows 2–5 years of quality storage for properly stored intact low-acid commercial canned food; this is not food-bank days of cover. UC describes radishes reaching harvest in 3–6 weeks and tomatoes as warm-season crops with regional planting windows. Compost nitrogen release depends on conditions; dosing compost for nitrogen alone can overapply phosphorus/potassium.',
       ['RC4X01', 'RC4A03', 'RC4A04', 'RC4A05'], 'mixed', implication='Hold a rotating nutrition bridge before planting; garden vegetables add useful food but do not automatically replace calories, protein, water and cooking.')
signal('SIG52', 'Commons access can fail while the building or equipment survives', ['commons', 'food_assistance', 'social'],
       'Conditional mechanism: pandemic closure, exclusionary rules, informal exclusion, reduced hours or displacement can remove useful access. No new specific hygiene law or current blanket closure is alleged. Indoor, outdoor, encampment-led and mobile nodes have different but overlapping failure modes.',
       ['RC4C04', 'DC07'], 'unclear', label='PLAUSIBLE MECHANISM',
       implication='Begin with modifiable space and useful presence; diversify access pathways and count emergency service only when its actual function is supported.', confidence='Mechanism plausible; no current new law or closure measured')

gauges = {
    'LOAD': 'Fuel-price exposure and interest in modal substitution; route demand unmeasured',
    'RESERVE': 'Spare paths, crews, rolling stock and terminal capacity unknown',
    'RECOVERY': 'Service changes depend on equipment, track and crews; major corridor electrification takes years',
    'DEPENDENCY': 'Bulk freight and selected passenger/essential supply corridors',
    'SUBSTITUTABILITY': 'Compatible rail can replace some truck linehaul; first/last mile persists',
    'SHEDDING': 'Consolidate nonurgent loads and avoid empty movements where service permits',
    'GROWTH': 'Existing rail/intermodal use, terminal efficiency and suitable electrified corridors',
    'LIFEBOAT': 'Protected essential cargo slots and local delivery links are proposals, not reserved capacity',
    'SOCIAL_TEMPERATURE': 'Not measured; worker capacity and rest remain protected',
    'CONFIDENCE': 'Strong corridor example; industry efficiency estimate; current national split and spare capacity unknown'
}
state['SYSTEM_MAP']['systems'].append(dict(id='rail', label='Rail traction and compatible freight substitution', geography='United States with California corridor example', gauges=gauges, source_ids=refs('RC4R01', 'RC4R02', 'RC4R03', 'RC4R05')))
for n in state['SYSTEM_MAP']['systems']:
    if n['id'] == 'commons':
        n['label'] = 'Adaptable community spaces and access networks'
        n['gauges']['GROWTH'] = 'Begin with modifiable space, useful presence and portable amenities; durable control and engineered services can grow later'
        n['gauges']['LIFEBOAT'] = 'Indoor/outdoor/mobile partner nodes with different access failures; actual service endurance remains unmeasured'
        n['gauges']['CONFIDENCE'] = 'Named programs and access points verified; available space, inclusion and emergency endurance remain unverified'
        n['source_ids'] = list(dict.fromkeys(n['source_ids'] + refs('RC4C04', 'RC4A01')))

def edge(id, origin, dest, stress, mechanism, sources, buffers, thresholds, substitutes, horizon, uncertainty, confirm, falsify):
    state['CASCADE_GRAPH']['edges'].append(dict(id=id, **{'from': origin, 'to': dest}, initiating_stress=stress,
        dependent_system=dest, mechanism=mechanism, source_ids=refs(*sources), buffers=buffers,
        thresholds=thresholds, substitutes=substitutes, time_horizon=horizon, uncertainty=uncertainty,
        confirm=confirm, falsify=falsify, activation_status='Conditional; not automatically activated by source-system strain'))

edge('EDGE22', 'diesel', 'rail', 'Delivered traction fuel unavailable or unaffordable on an essential corridor',
     'Diesel-dependent rail can conserve fuel per freight unit but still shares the fuel shock; terminals and last-mile trucks add dependencies.',
     ['RC4R03', 'RC4F01'], ['Protected traction fuel', 'Load consolidation', 'Suitable electric corridors'],
     ['Named essential service loses fuel access and alternatives cannot carry it'], ['Compatible intermodal routes', 'Prioritize essential cargo'],
     'Days to weeks for operations; years for major power-source conversion', 'National locomotive fuel-type count and route fuel cover unverified',
     'Operator reports fuel-related service loss and essential cargo delay', 'Rail maintains essential movements through stocks, contracts or existing electric operation')
edge('EDGE23', 'rail', 'trucking', 'Suitable road-freight lanes face high fuel demand or reduced capacity',
     'Available rail linehaul can reduce diesel demand per delivered tonne, if terminals, schedules and road connections fit.',
     ['RC4R03'], ['Existing intermodal terminals', 'Cargo aggregation'],
     ['Usable rail path, loading equipment, crew and protected last-mile capacity confirmed'], ['Coastal transport where suitable', 'Local aggregation'],
     'Operational adjustment can be shorter than infrastructure construction; route-specific timing unknown',
     'Average efficiency is not spare capacity or compatibility for every perishable load',
     'Trial delivers essential cargo reliably with lower total fuel use including terminal and last mile',
     'Terminal congestion, time windows, handling or last-mile constraints erase useful substitution')
edge('EDGE24', 'commons', 'food_assistance', 'Access to a useful node closes or becomes exclusionary',
     'Food, information, cooling and coordination can become inaccessible even if physical equipment remains intact.',
     ['DC07', 'RC4C04'], ['Differently governed partner site', 'Outdoor or mobile node', 'Portable storage and communications'],
     ['People lose an essential service and no accessible alternate can meet it'], ['Distributed collection/delivery', 'Open-air access when appropriate'],
     'Immediate loss; restoration depends on access, staffing and conditions', 'No new pandemic closure or specific exclusionary law asserted',
     'Observed access loss coincides with unmet essential service', 'Alternate routes and sites preserve service inclusively')
edge('EDGE25', 'agriculture', 'food_assistance', 'Food procurement buffer weakens before replacement harvest',
     'Planting can expand food supply but cannot fill the interval before harvest or supply all nutrition from quick vegetables.',
     ['RC4A03', 'RC4A04', 'RC4A05', 'RC4X01'], ['Rotating staples', 'Existing producers', 'Multiple-season planting', 'Nutrient testing'],
     ['Projected accessible food cover ends before usable harvest and confirmed deliveries'], ['Seasonal crop diversity', 'Storage crops', 'Interregional exchange'],
     'Weeks for some vegetables; longer for substantial replacement production', 'Yield, land, water, season, nutrition and labor unmeasured for any proposed site',
     'Gap between stressed consumption and dated harvest/delivery persists', 'Protected stocks and reliable deliveries bridge all essential nutrition to harvest')
edge('EDGE26', 'trade', 'diesel', 'Product cargo arrival delay exceeds accessible buffer',
     'Shipping disruption transmits to physical fuel service when compatible local stock and feasible refining or rerouting cannot bridge the delay.',
     ['RC4F01', 'RC4F03', 'RC4F05'], ['Accessible product stocks', 'Confirmed replacement cargo', 'Regional swaps', 'Compatible refinery feed and output'],
     ['Usable stock after protected floor falls below demand before confirmed arrival; crude is not counted as ready diesel'],
     ['Safe demand deferral', 'Compatible rail or electric service', 'Alternate product origins'],
     'Days to weeks for buffers and voyages; expansion longer', 'No matched East Asian voyage-time, terminal stock and demand series established',
     'Named region/product shows low deliverable cover plus confirmed late cargo or rationed essential service',
     'Timely arrivals, stock rebuilding, swaps or reduced nonessential demand preserve essential service')

protocol = {
    'purpose': 'Match response networks by the time they can actually cover, then overlap bridges before any protected floor is crossed.',
    'separate_clocks': ['Physical shelf life or equipment life', 'Inventory turnover', 'Usable accessible stock cover', 'Activation time', 'Replenishment arrival time', 'Replacement production or construction lead time'],
    'cover_rule': 'For positive net depletion, cover = compatible accessible usable quantity above protected floor / (stressed use rate - dependable accessible inflow rate), with matching units and service boundaries. If the denominator is zero or negative, do not claim infinite security: test inflow interruption and shared failures.',
    'service_limit': 'Food, water, power, labor, inclusion/access, route and compatible equipment can each end useful service before stock runs out.',
    'handoff_rule': 'Next capacity must be usable before the preceding bridge reaches its protected floor; include commissioning, transport and learning time.',
    'national_ratio_caution': '107.9 million barrels / 3.602 million barrels per day is approximately 30 days of gross US distillate stocks relative to recent domestic products supplied. It excludes continuing flows and many constraints; it is not a local endurance estimate or run-out forecast.',
    'donor_rule': 'Protect donor essential demand and contingency floor; ownership, geographic delivery, grade and time determine whether a reserve can actually help.',
    'unknown_policy': 'Unmeasured quantity, access or demand remains unknown; institution count and budget are not service-days.'
}
state['SYSTEM_MAP']['response_time_protocol'] = protocol

def reserve(id, name, kind, function, readiness, guard, limits, sources):
    state['RESERVES_AND_LIFEBOATS'].append(dict(id=id, name=name, type=kind, essential_function=function,
        readiness=readiness, donor_guardrail=guard, limits=limits, source_ids=refs(*sources),
        shared_failure_audit=dict(epistemic_label='PLAUSIBLE MECHANISM', audit_status='Structural screen; current surplus not audited',
            expectation_gap='Nominal capacity can fail to provide accessible service at the needed time',
            shared_failure_modes=limits, current_stressed_surplus='Unknown', required_service_proof='Dated accessible capacity and delivery before protected floor crossing')))

reserve('RES19', 'Northeast Home Heating Oil Reserve', 'Designated public fuel reserve',
        'Emergency heating-oil supply under designated release arrangements',
        'DOE program describes approximately one million barrels of ULSD; not a fresh independent tank audit',
        'Protect eligible Northeast heating needs and release authority; not a freely available California donor',
        'Release, transport, grade, terminal access and local demand constrain delivery; do not add stock to EIA totals without overlap accounting', ['RC4F04'])
reserve('RES20', 'Compatible existing rail service', 'Substitution and fuel conservation',
        'Move suitable essential linehaul cargo with lower fuel intensity',
        'Existing rail operates; spare paths, crews, loading and last-mile capacity unverified',
        'Do not displace essential committed cargo or exceed safe crew/terminal capacity',
        'Diesel, terminal power, crew and final-delivery dependencies persist; aggregate efficiency is not route capacity', ['RC4R03', 'RC4R01'])
reserve('RES21', 'Oakland public compost return loop', 'Nutrient recycling input',
        'Improve soil and recycle some nutrients into local production',
        'Verified public self-load location and hours; current stock quantity and composition unknown',
        'Respect equitable access and existing garden demand; no bulk allocation assumed',
        'Compost can run out; nutrient release varies; test soil and material rather than treating it as complete fertilizer or new topsoil', ['RC4A01', 'RC4A05'])
reserve('RES22', 'Overlapping seasonal food-production network', 'Proposed production lifeboat',
        'Add fresh food and diversified seasonal supply beyond donations',
        'Proposal; no site, planted crop, harvest volume or winter delivery contract established',
        'Protect local nutrition, water and labor before promising exports; no free donor surplus assumed',
        'Seed, water, soil nutrients, light, weather, labor, time, nutrition balance and transport remain necessary', ['RC4A03', 'RC4A04', 'RC4A05', 'RC4X01'])

for r in state['RESERVES_AND_LIFEBOATS']:
    r['response_time'] = {
        'physical_life': 'Asset- and condition-specific; not inferred from turnover',
        'inventory_turnover': 'Unmeasured; not a shelf-life or endurance estimate',
        'usable_quantity_above_floor': 'Unknown unless explicitly quantified in this record',
        'stressed_demand_rate': 'Unknown', 'dependable_inflow': 'Unknown under the initiating shock',
        'accessible_service_cover': 'Unknown; no institution-count proxy',
        'activation_time': 'Unmeasured', 'replenishment_arrival': 'Unverified',
        'replacement_lead_time': 'Unverified', 'limiting_dependencies': r['limits'],
        'assessed_cycle': 'RC-004'}
    if r['id'] == 'RES01':
        r['limits'] = 'Seasonally thin; region, grade, contract and route limit use. EIA Table 6 excludes designated public reserve categories. RES19 now records DOE\'s approximately one-million-barrel Northeast program description; current independently audited usable quantity, lawful release and local access remain unverified. SPR crude is not ready distillate.'
        r['source_ids'] = list(dict.fromkeys(r['source_ids'] + refs('RC4F01', 'RC4F04')))
        r['response_time']['limiting_dependencies'] = r['limits']
        r['response_time'].update(usable_quantity_above_floor='Unknown locally after protected floors',
            stressed_demand_rate='Unknown locally under the initiating shock',
            accessible_service_cover='Unknown locally; do not substitute the separately recorded gross national reference ratio',
            dependable_inflow='Unknown locally under the initiating shock; national reported production does not establish accessible local inflow',
            national_reference={'observation_date': '2026-09-11', 'gross_distillate_stocks_million_barrels': 107.9,
                'recent_four_week_domestic_products_supplied_million_barrels_per_day': 3.602,
                'weekly_distillate_production_million_barrels_per_day': 5.2,
                'gross_stock_use_ratio_days': 'Approximately 30; calculated reference, not usable service cover or countdown'},
            replacement_lead_time='Near-term rerouting and compatible output changes versus years for major new build')
    if r['id'] == 'RES16':
        r['response_time'].update(physical_life='Properly stored intact low-acid commercial cans: USDA quality guidance 2–5 years; contents and packaging matter',
            accessible_service_cover='Unknown until actual quantity, diet, users, access, water and cooking are measured',
            replacement_lead_time='Radishes can take 3–6 weeks; full nutrition and seasonal production take longer and remain site-specific')
        r['source_ids'] = list(dict.fromkeys(r['source_ids'] + refs('RC4X01', 'RC4A04')))
    if r['id'] == 'RES21':
        r['response_time'].update(activation_time='Use posted public pickup hours if compost remains available',
            replacement_lead_time='Crop- and weather-dependent nutrient mineralization plus time to harvest')
    if r['id'] == 'RES22':
        r['response_time'].update(activation_time='Site/seed/water preparation required; starting now does not provide an immediate harvest',
            replacement_lead_time='Radishes may reach harvest in 3–6 weeks under suitable conditions; other crops, seasons and full nutrition supply have different lead times')
    if r['id'] == 'RES17':
        r['name'] = 'Adaptable commons space and operating access'
        r['readiness'] = 'A commons may start with modifiable space and regular useful presence; no specific new site or emergency endurance verified'
        r['essential_function'] = 'Enable community presence, adaptation and incremental service development'
        r['limits'] += ' Pandemic closure, exclusion, displacement and outdoor exposure can remove usable access; no current new rule is alleged.'
        r['response_time']['limiting_dependencies'] = r['limits']

state['ISLANDS_OF_STABILITY'].append(dict(id='ISL10', name='Japan–Philippines complementary process-input network',
    offers='Documented sulfur and sulfuric-acid coproduct exchange supporting metal processing',
    needs_in_return='Ore/feed, energy, vessels, processing hardware, maintenance and reliable counterpart operations',
    available_surplus='Unknown; reported flows are committed industrial operations',
    donor_guardrail='Do not divert committed process acid or sulfur without verifying donor needs and replacement',
    self_sufficient=False, limits='Shipping concentration and parent-process disruption can affect both partners', source_ids=refs('RC4S05', 'RC4S07')))

def transition(id, cluster, name, function, release, assets, growth, requirements, risks, horizon, success, sources):
    state['TRANSITION_OPPORTUNITIES'].append(dict(id=id, cluster_id=cluster, name=name,
        classification='Conditional creative transition', function_to_preserve=function, safe_load_release=release,
        released_assets=assets, growth_candidate=growth, conversion_requirements=requirements, risks=risks,
        time_horizon=horizon, success_observation=success, source_ids=refs(*sources),
        status='Proposed; no procurement, partner commitment or verified donor surplus'))

transition('TR13', 'CL08', 'Conserve transport fuel before corridor conversion', 'Reliable essential freight and passenger service',
           'Avoidable road mileage, empty movements and suitable nonurgent trips', 'Road capacity and fuel only after actual modal substitution',
           'Compatible rail/intermodal links and selected electrified corridors', 'Paths, terminals, crews, last mile and usable energy supply',
           'Rail may share diesel shock; unsuitable transfers can add delay or handling', 'Operations can change before construction; major corridors years',
           'Lower total fuel per completed essential movement with adequate reserve', ['RC4R01', 'RC4R02', 'RC4R03'])
transition('TR14', 'CL07', 'Bridge donation dependence with rotating nutrition and new production', 'Accessible nutrition despite reduced avoidable surplus',
           'Avoidable food waste while preserving access to nutrition', 'Recovered compost, adaptable growing space and logistics knowledge where actually available',
           'Seasonal gardens, producer agreements, storage foods and nutrient-recycling loops',
           'Protected bridge stock, water, seed, soil testing, appropriate crops, labor and distribution',
           'Fast vegetables do not replace all calories/protein; common drought, energy or access failure',
           'Stock rotation now; weeks to first crops; seasons for a durable network',
           'Measured nutrition service survives declining surplus and spans planting-to-harvest gaps', ['RC4A01', 'RC4A03', 'RC4A04', 'RC4A05', 'RC4X01'])
transition('TR15', 'CL04', 'Grow commons from adaptable space', 'Useful inclusive presence and progressively stronger shared services',
           'Unused or inaccessible space where conversion is lawful and does not displace existing users', 'Portable furniture, shade, tools, power and knowledge actually made available',
           'Indoor, outdoor, encampment-led and mobile partner nodes',
           'A modifiable place and people able to use it; durable control, staffing and engineered systems can develop in stages',
           'Closure, exclusion, displacement, heat, water and sanitation limits; availability not established by a listed building',
           'Small beginnings when space is available; upgrades as resources and use justify them',
           'People can use and modify the space; particular services gain demonstrable endurance over time', ['RC4C04', 'RC4C01', 'RC4A01'])

for c in state['COMMUNITY_COMMONS']:
    if c['id'] == 'COM09':
        c['name'] = 'Start an adaptable commons and grow its services'
        c['first_steps'] = ['Find a modifiable place and establish ordinary useful presence without waiting for a complete institution.',
            'Add comfort through shade, seating, tools, communications or shared activity as appropriate.',
            'Allow outdoor, continuous-use, encampment-led and mobile extensions where people can actually use them.',
            'Develop durable control and power/water/storage over time; identify which services can operate through specific interruptions.']
        c['resources'] = 'Modifiable space and willing participants first; later improvements matched to actual use, resources and protected existing users'
        c['success_measure'] = 'Accessible useful space grows organically; emergency claims remain bounded by demonstrated service'
        c['source_ids'] = list(dict.fromkeys(c['source_ids'] + refs('RC4C04', 'RC4A01')))

state['COMMUNITY_COMMONS'].extend([
    dict(id='COM11', cluster_id='CL07', name='Compost-to-crop and rotating-food bridge', who_can_act='Neighbors, gardeners, food groups and willing local producers',
         first_steps=['Use the verified ANV public compost return point within posted hours and available stock.',
                      'Choose season-appropriate crops and test soil; use compost analysis and crop needs to identify nutrient gaps.',
                      'Overlap a rotating staple supply with successive plantings and existing producer deliveries.',
                      'Track meals/nutrition available and earliest plausible harvest, not just bags distributed or bed area.'],
         resources='Space, water, seed, appropriate growing medium, tools, labor and a bridging food supply; quantities not secured',
         protected_floor='Protect existing compost users, local food needs and water availability before exporting food',
         success_measure='Actual edible output and essential nutrition supplied across the harvest gap', status='Proposed; no land, crop or allocation committed',
         source_ids=refs('RC4A01', 'RC4A03', 'RC4A04', 'RC4A05', 'RC4X01'), recordkeeping='Aggregate crop, nutrient, inventory and service measures; no beneficiary profiling'),
    dict(id='COM12', cluster_id='CL04', name='Partner indoor, outdoor and mobile commons nodes', who_can_act='Existing informal groups, libraries, tenant groups and willing space stewards',
         first_steps=['Start with usable modifiable space and portable amenities.',
                      'Map which partner remains accessible when one site closes or becomes unusable.',
                      'Share movable tools, shade, communications and transport where available.',
                      'Add solar/storage or other infrastructure for a defined essential load when feasible.'],
         resources='People and space first; portable amenities and later infrastructure according to use and resources',
         protected_floor='Preserve existing users and dignified access; do not shift all load to a partner with unmeasured reserve',
         success_measure='Useful access persists through a specific site interruption; no 24/7 endurance claimed without support',
         status='Proposed network; no specific park, encampment, library or owner enrolled', source_ids=refs('RC4C04', 'DC07', 'RC4C03'),
         recordkeeping='Public service/access conditions only; no personal location tracking')
])

def extend(cluster_id, **fields):
    c = next(c for c in state['SYSTEM_MAP']['clusters'] if c['id'] == cluster_id)
    for k, v in fields.items():
        c[k] = list(dict.fromkeys(c.get(k, []) + v)) if isinstance(v, list) else v

extend('CL01', signal_ids=['SIG43', 'SIG44'], buffers=['RES19', 'RES20'], transition_ids=['TR13'],
       source_ids=refs('RC4F01', 'RC4F03', 'RC4F05', 'RC4R03'),
       independence='Existing retail/inventory observations were reconfirmed, not counted again. EIA, IEA and Japan Customs measure different periods/products; common oil shock is not multiplied by source count.')
extend('CL03', signal_ids=['SIG46', 'SIG47', 'SIG50'], buffers=['RES21'], outside_reserve=['ISL10'], commons_ids=['COM11'], source_ids=refs('RC4S02', 'RC4S03', 'RC4S04', 'RC4S05', 'RC4A05'))
extend('CL04', signal_ids=['SIG48', 'SIG49', 'SIG52'], transition_ids=['TR15'], commons_ids=['COM12'], source_ids=refs('RC4C01', 'RC4C03', 'RC4C04'))
extend('CL07', signal_ids=['SIG50', 'SIG51', 'SIG52'], buffers=['RES21', 'RES22'], transition_ids=['TR14'], commons_ids=['COM11', 'COM12'], lifeboats=['RES22'], source_ids=refs('RC4X01', 'RC4A01', 'RC4A03', 'RC4A04', 'RC4A05'))
extend('CL08', signal_ids=['SIG45'], buffers=['RES20'], transition_ids=['TR13'], source_ids=refs('RC4R01', 'RC4R02', 'RC4R03'))
extend('CL09', signal_ids=['SIG43', 'SIG44'], source_ids=refs('RC4M05', 'RC4F03', 'RC4F05'),
       status='September incident response and product-flow constraints documented; no verified piracy-fleet diversion, uniform Arabian Peninsula blockade or whole-East-Asia import decline')

new_questions = [
    ('Q23', 'Which East Asian product routes have actual arrival delays beyond accessible stock cover?', 'Voyage delays, aggregate imports and refinery output are different measures.', 'Match port/product arrival data, refinery throughput, compatible stocks and dated cargo ETAs; prioritize Japan and a Singapore-linked product route.', 'Energy + Logistics + Geographic Context', 'high', 'Dated port, customs or refinery update', refs('RC4F03', 'RC4F05')),
    ('Q24', 'What is the current diesel futures curve, with contract month and settlement date?', 'Spot and pump prices cannot answer a futures-price question.', 'Obtain a public exchange settlement series and compare the same contract or transparently rolled series; keep the EIA April 2024 futures table quarantined.', 'Economic / Industrial + Skeptic', 'high', 'Public dated exchange settlements', refs('RC4F06', 'RC4F01')),
    ('Q25', 'How many current US locomotives use each energy source and where can rail carry more essential freight?', 'A locomotive count is not train frequency, tonne-km or route reserve.', 'Retrieve accessible BTS/rail operator fleet data; distinguish stored locomotives, passenger units and diesel-electric power; assess one compatible lane.', 'Infrastructure + Energy', 'high', 'Accessible fleet workbook or operator filing', refs('RC4R05', 'RC4R03')),
    ('Q26', 'Which Venezuelan sulfur assets can be repaired, and when would net exportable product be available?', 'Historical capability does not establish current condition or spare output.', 'Seek public asset condition, funded project scope, feed/hydrogen/utilities, commissioning and storage/export milestones before assigning a date.', 'Sulfur + Industrial + Skeptic', 'high', 'Operator disclosure or funded project award', refs('RC4S02', 'RC4S03', 'RC4S04')),
    ('Q27', 'How do food-access cover and replenishment gaps compare in one rural Tennessee county and an East Bay locality?', 'Bay Area convenience is not evidence of greatest need; rural last-mile depth may differ.', 'Use public regional food-bank service calendars, county transport/access data and purchasing disclosures; calculate no food-days without usable inventory and demand.', 'Food + Geographic Context + Commons', 'high', 'Comparable county service and inventory evidence', refs('RC4X01')),
    ('Q28', 'Where does Oakland organics processing occur now, and how much suitable compost reaches local growers?', 'Public pickup is verified; complete processing path, quantity and nutrient content are not.', 'Review current collection/processing contract and material analysis, with actual public pickup stock and crop demand; keep design capacity separate from output.', 'Food + Commons + Industrial', 'medium', 'Current municipal processing report or material analysis', refs('RC4A01', 'RC4A02', 'RC4A05')),
    ('Q29', 'Can seasonal food exchange bridge winter access without exporting donor shortage?', 'A planting calendar or hypothetical tomato route does not establish a harvest, surplus or viable delivery.', 'Pair dated winter production and donor nutrition floor with weather-safe transport, storage and receiver capability; include staples and protein as well as fresh vegetables.', 'Food + Logistics + Islands of Stability', 'medium', 'Crop forecast and matched lane evidence', refs('RC4A03', 'RC4X01'))
]
for id, q, why, action, owner, priority, trigger, sources in new_questions:
    state['QUESTIONS_TO_WATCH'].append(dict(id=id, question=q, why_it_matters=why, next_public_action=action,
        owner_role=owner, priority=priority, revisit_trigger=trigger, source_ids=sources, status='open',
        user_manual_work_required=False, last_reviewed_cycle='RC-004'))

meta = state['meta']
meta['agent_run_history'].append({'cycle_id': 'RC-003', 'runs': meta['agent_runs'], 'review_scope': meta['review_scope']})
meta.update(cycle_id='RC-004', research_cutoff=DAY, completed_on=DAY,
    baseline='Continuation of RC-003; reconfirmations and late discoveries are distinguished from new events.',
    status='Focused time-cover research integrated; coordinator acceptance with explicit gaps',
    coverage_note='Fuel/logistics, rail, sulfur/mining, food/soil, commons access and maritime response deepened. Current fleet split, diesel futures settlements, local stock cover and physical donor surplus remain open. Other sectors retain dated context.',
    independent_review='Specialists exchanged findings; coordinator reopened selected primary sources. Candidate review scope and limitations are recorded in reports/RC-004/REVIEW.md; no whole-state independent pass.',
    review_scope={'coordinator_checks': ['Dated fuel/market observations', 'Import-denominator counterevidence', 'Rail benchmark and count gap', 'Sulfur project comparator dates', 'Commons full-page upgrades', 'Crop/nutrient and shelf-life distinctions', 'Maritime report deduplication', 'Public contact verification'],
                 'limitations': ['Unknown current local inventory, cargo timing, reserve floor and donor surplus', 'No physical site assessment or partner commitment', 'No whole-state independent source audit', 'Exact diesel futures and locomotive counts not established']})
meta['agent_runs'] = [dict(name=n, full_report_received=True, status='completed_bounded_research_with_gaps')
    for n in ['fuel_cover', 'sulfur_leadtime', 'food_horizons', 'commons_access', 'maritime_access']]
meta['agent_runs'] += [dict(name='rail_transition', full_report_received=True, status='Final source packet delivered; original saved checkpoint remained initial; coordinator recovery attributed separately'),
                       dict(name='coordinator_verification', full_report_received=True, status='Selected primary sources reopened; no full independent audit')]
meta['role_coverage'] = {
    'Signal Intake': 'Six bounded specialists plus coordinator primary checks',
    'Energy & Diesel': 'fuel_cover and rail_transition', 'Food / Fertilizer / Agriculture': 'food_horizons and sulfur_leadtime',
    'Infrastructure': 'Rail conversion, commons critical loads and access', 'Economic / Industrial': 'Commodity price definitions and sulfur construction/operating networks',
    'Social Temperature': 'Access/exclusion mechanisms only; no new group dangerousness or violence assessment',
    'Geographic Context': 'California, Japan, Philippine industrial link, Venezuelan historical assets and named maritime routes; rural Tennessee comparison remains open',
    'Cascade Modeler': 'Coordinator time-cover protocol and conditional edges',
    'Skeptic / Red-Team': 'Peer exchanges and coordinator counterevidence; whole-state independent audit not claimed',
    'Resilience / Overflow': 'Usable stock, swaps, rail conservation, compost and seasonal production',
    'Islands of Stability': 'Complementary industrial network; donor surplus unknown',
    'Commons': 'commons_access and food_horizons; modifiable space first, services grow in stages'}
meta['access'] = 'Public sources only. Proposed email text saved for user review; no private mail, outbound contact or partner commitment.'
state['CHANGELOG'].extend([
    dict(cycle='RC-004', date=DAY, action='Focused continuation', details='Six specialist threads used the shared exchange. Five full packets saved; delivered rail findings recovered by coordinator without rewriting initial checkpoint. Selected full-page verification upgraded two commons leads.'),
    dict(cycle='RC-004', date=DAY, action='Correct interpretation', details='RC-003 means third research cycle, not crisis level. Its 42 signals, 21 links and 77 source records are cumulative records, not independent emergencies or confirmations. Full enumerated inventory saved.'),
    dict(cycle='RC-004', date=DAY, action='Reserve clocks and commons correction', details='All reserves now separate shelf life, turnover, usable cover, activation, replenishment and replacement. Commons can start in modifiable space; formal facilities and engineered power are later additions. Pandemic/exclusion access losses are conditional, not an invented current law.'),
    dict(cycle='RC-004', date=DAY, action='Counterevidence and uncertainty', details='Existing EIA retail/inventory readings reconfirmed without new-shock counting. Japan petroleum import volume increased year on year. San Anselmo uniqueness rejected. OakCLT later public activity found. No actual anti-piracy fleet diversion, current Venezuelan surplus, national rail split or diesel futures series established.'),
    dict(cycle='RC-004', date=DAY, action='Attention redirected', details='Prioritize matched fuel arrival/stock cover, futures definitions, rail conversion capacity and rural food-access comparisons. Bay Area was a demonstration geography, not a finding of greatest need. No mass migration is assumed. Outreach proposals remain unsent.')
])
# Later user steering is design provenance, outside the unchanged empirical cutoff.
admit(src('VISION01', '15 Years Til Utopia — user-supplied historical conversation concept',
    'User-supplied document developed with an earlier assistant',
    'https://github.com/Jaradyne/Dis-Unity/blob/main/ideas/15_YEARS_TIL_UTOPIA_SOURCE.md', None,
    'Undated historical concept; supplied and read on 2026-09-22',
    'Design provenance only, not external empirical evidence. Original PDF has 69 pages; page-labelled text and original hash preserved. Contains internal revisions and unvalidated technological/governance claims.', 'C'))
vision_source = next(s for s in state['SOURCE_LEDGER'] if s['id'] == 'VISION01')
vision_source['retrieved_at'] = '2026-09-22'
vision_source['source_kind'] = 'User-authorized design input, not a public monitoring source'
meta['completed_on'] = '2026-09-22'
meta['design_intake_date'] = '2026-09-22'
meta['access'] = 'Public research sources plus one user-supplied concept document explicitly authorized for Git incorporation. Proposed email text saved for review; no private mail, outbound contact or partner commitment.'
state['SYSTEM_MAP']['growth_direction'] = {
    'name': 'Commons growth informed by 15 Years Til Utopia',
    'status': 'Proposed direction; no new institution, site or promised timeline',
    'document': 'ideas/COMMONS_GROWTH_PATH.md', 'source_ids': ['VISION01'],
    'purpose': 'Preserve essential function while increasing agency, learning, beauty, voluntary participation and shared prosperity.',
    'beginning': 'Modifiable space plus people able to use it; useful presence and comfort can precede formal facilities.',
    'growth': ['Tools and open learning', 'Seasonal food and nutrient circulation', 'Defined essential services',
               'Productive shared assets and protected funds', 'Reciprocal networks of places', 'Long-horizon experiments'],
    'measurement': 'Demonstrated useful service, accessible participation and maintainable capability; no public worth score for individuals.',
    'boundary': 'Historical technology, income, surveillance and exclusion proposals are not adopted operating assumptions; see source limitations and growth document.'
}
transition('TR16', 'CL04', 'Turn shared making and learning into enduring common capability',
    'Agency, social connection, usable tools and accessible essential services',
    'Avoidable duplication and discarded repairable resources, when replacement does not shift harm',
    'Repairable equipment, skills and modifiable space actually offered',
    'Repair networks, workshops, cultural gatherings and cooperatively controlled productive assets',
    'Useful shared activity; open learning; transparent budgets and maintenance reserves as money and assets accumulate',
    'Unpaid labor exhaustion, inaccessible participation, optimistic revenue promises and dependence on unproved technology',
    'Small activities when people and space are available; expansion follows demonstrated use and resources',
    'Capabilities survive organizer absence; net resources support common access after maintenance and reserves', ['VISION01'])
state['COMMUNITY_COMMONS'].append(dict(id='COM13', cluster_id='CL04',
    name='Computers and campfires: a making, learning and gathering commons',
    who_can_act='People already using or able to shape a shared place, with willing neighbors and organizations',
    first_steps=['Choose one useful shared activity and let people alter the space around it.',
                 'Make something that improves ordinary life: seating, planters, a repaired tool, art or an understandable service guide.',
                 'Share practical knowledge in several accessible formats; allow rest and participation without a contribution score.',
                 'Let a small gathering showcase what grew; record money and maintenance needs if the project acquires resources.'],
    resources='Modifiable space, interested people and actually available materials first; no full-campus plan or breakthrough technology required',
    protected_floor='Essential access and dignity are not contingent on productivity; protect existing users and organizer capacity',
    success_measure='People can use, change, understand and enjoy the place; useful capability and reciprocal support persist',
    status='Design proposal adapted from user-supplied vision; no event scheduled or space committed',
    source_ids=['VISION01'], recordkeeping='Project decisions and aggregate capability; no personal worth score, tracking or public beneficiary dossiers'))
extend('CL04', transition_ids=['TR16'], commons_ids=['COM13'])
state['QUESTIONS_TO_WATCH'].append(dict(id='Q30',
    question='Which small commons activity can grow durable capability in the direction of the supplied vision?',
    why_it_matters='The goal includes ordinary flourishing and agency, not emergency survival alone.',
    next_public_action='Use the verified local space, compost and power-program leads to identify compatible starting conditions; research maintainable incremental options without treating hypothetical space or volunteers as available.',
    owner_role='Commons + Resilience / Overflow + Transition', priority='high',
    revisit_trigger='Publicly available space/program evidence or user direction about an actual willing node',
    source_ids=refs('VISION01', 'RC4A01', 'RC4C04', 'RC4C01'), status='open',
    user_manual_work_required=False, last_reviewed_cycle='RC-004'))
state['CHANGELOG'].append(dict(cycle='RC-004', date='2026-09-22', action='User-authorized vision incorporation',
    details='Read all 69 pages of supplied 15 Years Til Utopia PDF; preserved page-labelled text and original file hash. Added an incremental commons growth pathway, transition and commons card. Vision remains design provenance, not evidence of ready technology or a fifteen-year forecast. Empirical evidence cutoff remains September 21.'))

save('cycles/RC-004/source_aliases.json', aliases)
save('cycles/RC-004/candidate.json', state)
print(json.dumps({'signals': len(state['ACTIVE_SIGNALS']), 'edges': len(state['CASCADE_GRAPH']['edges']), 'sources': len(state['SOURCE_LEDGER']), 'reserves': len(state['RESERVES_AND_LIFEBOATS']), 'aliases': len(aliases)}))
