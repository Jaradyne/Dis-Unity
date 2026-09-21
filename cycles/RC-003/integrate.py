"""Build the RC-003 candidate from its immutable baseline and attributed checkpoints."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FOLDER = Path(__file__).resolve().parent
state = json.loads((FOLDER / 'baseline.json').read_text())
inbox = ROOT / 'inbox/RC-003'
threads = ['coordinator_network', 'nutrient_network', 'maritime_network',
           'electric_food', 'durable_commons', 'coordinator_bayer']
payloads = {name: json.loads((inbox / (name + '.json')).read_text()) for name in threads}

# Deduplicate repeated readings of one publication. Preserve its original identity.
aliases = {}
by_url = {r['url']: r for r in state['SOURCE_LEDGER']}
for name in threads:
    for source in payloads[name]['sources']:
        source = copy.deepcopy(source)
        existing = by_url.get(source['url'])
        if existing:
            aliases[source['id']] = existing['id']
            existing['last_verified'] = '2026-09-21'
            readers = existing.setdefault('rc003_readers', [])
            if name not in readers:
                readers.append(name)
        else:
            state['SOURCE_LEDGER'].append(source)
            by_url[source['url']] = source
            aliases[source['id']] = source['id']

def ids(*names):
    return list(dict.fromkeys(aliases.get(n, n) for n in names))

def row(section, key):
    collection = state[section] if section in state else state['SYSTEM_MAP'][section]
    return next(r for r in collection if r['id'] == key)

# Repair the four known list/string-extension defects; no historical cycle is edited.
repairs = []
for records, field in [(state['CASCADE_GRAPH']['edges'], 'thresholds'),
                       (state['CASCADE_GRAPH']['edges'], 'buffers'),
                       (state['COMMUNITY_COMMONS'], 'resources')]:
    for record in records:
        value = record.get(field)
        if not isinstance(value, list) or sum(isinstance(v, str) and len(v) == 1 for v in value) < 8:
            continue
        fixed, run = [], []
        for part in value:
            if isinstance(part, str) and len(part) == 1:
                run.append(part)
            else:
                if run:
                    fixed.append(''.join(run).strip())
                    run = []
                fixed.append(part)
        if run:
            fixed.append(''.join(run).strip())
        record[field] = fixed
        repairs.append(record['id'] + '.' + field)
assert len(repairs) == 4, repairs

meta = state['meta']
meta['agent_run_history'].append({'cycle_id': meta['cycle_id'], 'runs': meta['agent_runs']})
meta.update({
    'schema_version': '1.2', 'cycle_id': 'RC-003', 'research_cutoff': '2026-09-21',
    'completed_on': '2026-09-21',
    'baseline': 'Continuation of RC-002; older newly discovered evidence is explicitly dated.',
    'status': 'Focused research integrated with scoped independent checks and explicit operating gaps',
    'coverage_note': 'Nutrients, maritime security, conditional electrification, food assistance and durable commons deepened. Bayer admitted by coordinator; no complete legal or toxicological review. Other domains retain dated context.',
    'independent_review': 'Nutrient specialist independently reopened Mosaic curtailments, SWARD fertilizer-cargo report and coordinator IEA sulfur/acid claim. Closing review covered EDGE15-21 and RES15-18; reviewer authored nutrient inputs and did not independently replicate those inputs. No whole-state independent pass.',
    'review_scope': {'independent_checks': ['Mosaic operating disclosure', 'SWARD cargo and July status', 'IEA July sulfur/acid dependency'],
                     'coordinator_checks': ['Feeding America totals', 'ACCFB procurement', 'DOE fleet and parked refrigeration', 'OFAC GL52C', 'IMB H1 totals', 'OakCLT property model', 'Hayward hours notice', 'EPA and IARC positions'],
                     'limitations': ['No available commons property or tested site endurance established', 'No current Venezuelan sulfur surplus or September route clearance', 'No local food-bank emergency days or current physical famine established', 'Closing whole-candidate independent review not claimed']},
    'agent_runs': [{'name': n, 'status': payloads[n]['status'], 'full_report_received': True} for n in threads] +
                  [{'name': 'bayer_review', 'status': 'Initial checkpoint only; no research findings delivered; coordinator completed bounded watch', 'full_report_received': False}],
    'role_coverage': {
        'Signal Intake': 'All four completed specialist threads and coordinator',
        'Energy & Diesel': 'electric_food; nutrient coproduct lens',
        'Food / Fertilizer / Agriculture': 'nutrient_network and electric_food',
        'Infrastructure': 'durable_commons; charging and Western grid lenses',
        'Economic / Industrial': 'coordinator and nutrient conversion lenses',
        'Social Temperature': 'No new population or violence assessment; commons access/governance only',
        'Geographic Context': 'California and named global input/routes; incomplete global coverage',
        'Cascade Modeler': 'Coordinator integrates conditional edges and shared-failure audits',
        'Skeptic / Red-Team': 'Scoped nutrient peer checks plus coordinator source checks',
        'Resilience / Overflow': 'All admitted clusters paired with buffers and donor floors',
        'Islands of Stability': 'Complementary offer/need networks; uncommitted surplus unknown',
        'Commons': 'durable_commons and electric_food'
    }
})

def signal(num, title, systems, observation, source_ids, label='FACT', direction='mixed',
           geography=None, confidence='High for the stated source scope; operational gaps retained',
           freshness='Late discovery or structural evidence; see source observation dates', status='Admitted with scope limits', implication=''):
    state['ACTIVE_SIGNALS'].append({'id': f'SIG{num:02}', 'title': title,
        'geography': geography or ['California', 'United States', 'Global resource and trade nodes'],
        'systems': systems, 'epistemic_label': label, 'observation': observation,
        'direction': direction, 'source_ids': source_ids, 'confidence': confidence,
        'freshness': freshness, 'event_id': f'rc003_{num}', 'status': status,
        'implication': implication, 'first_seen_cycle': 'RC-003', 'last_reviewed_cycle': 'RC-003'})

signal(31, 'Glyphosate review remains open; evidence lanes separated', ['agriculture', 'industrial'],
       'EPA August 26 page anticipates an updated health assessment late 2026 and lists September 24 literature comments. IARC 2015 Group 2A hazard classification and EPA prior risk assessment differ; 2022 partial vacatur and withdrawal remain relevant history.',
       ids('BAY01', 'BAY02'), implication='Watch regulation, independent evidence, operational access and research integrity separately. No Bayer-caused sulfur shortage or malicious intent inferred.')
signal(32, 'Food rescue is a major, incomplete component of assistance', ['food_assistance', 'food_logistics'],
       'Feeding America FY2025 reports 4.3 billion pounds rescued of 7.2 billion sourced: about 60%, calculated from rounded national figures. This is not a local supply mix or current inventory.',
       ids('EFS01'), direction='unclear', geography=['United States'], implication='Stress-test rescued supply separately from purchases and government commodities.')
signal(33, 'ACCFB demonstrates procurement beyond surplus recovery', ['food_assistance', 'food_logistics'],
       'FY2025 audit distinguishes purchased, donated, government and recovered food. Annual report describes wholesale-price access and a five-food-bank purchasing partnership. Available emergency balances and delivery commitments remain unknown.',
       ids('EFS02', 'EFS03', 'EFS07'), direction='improving', geography=['Bay Area'], implication='Build from existing purchasing capacity; do not assume food banks rely only on leftovers.')
signal(34, 'Hayward fiscal pressure reduces staffed library access', ['municipal', 'commons'],
       'City notice says library hours reduced effective January 1, 2026 for budget savings; current schedule closes Sunday and Monday. Ordinary room reservations remain within public hours and require advance booking.',
       ids('DC09', 'DC05', 'DC06'), direction='worsening', geography=['Bay Area'], implication='Potential refuge capacity needs funded access hours; no heat-emergency service failure established.')
signal(35, 'Maritime incident totals improve while severity remains uneven', ['trade', 'food_logistics'],
       'IMB H1 2026 global reports fell to 38 from 90. ReCAAP separately reports Asian armed robbery fell to 35 from 96; totals have different intake and must not be added. Missing voyage denominators prevent per-voyage probabilities.',
       ids('MAR01', 'MAR02', 'MAR03'), direction='improving', implication='Regional enforcement is a buffer; global averages do not clear an individual route.')
signal(36, 'Somali attacks continue; a recent response protected crew', ['trade', 'fertilizer'],
       'EUNAVFOR September 11 account says the September 10 GLAMOR incident ended with crew safe after coordinated response. Its July 29 report documents SWARD fertilizer cargo hijacked April 26 en route to Mombasa; September cargo/captivity status unknown.',
       ids('MAR04', 'MAR05', 'MAR06'), freshness='September 10 response is current within cutoff; April/July cargo event is historical', implication='Observed local interruption, not established California nutrient loss or guaranteed naval coverage.')
signal(37, 'Sulfur and acid connect fertilizer to mineral processing', ['sulfur', 'fertilizer', 'industrial'],
       'IEA July 2026 report describes sulfur shipping disruption and sulfuric-acid export curbs affecting fertilizer and mineral value chains. Its dated Hormuz account does not establish September 21 passage status.',
       ids('RC3C02', 'TRS02'), direction='worsening', implication='Diversification must include processing acid and routes, not just ore deposits.')
signal(38, 'Venezuela has conditional lawful pathways; sulfur reserve unmeasured', ['sulfur', 'trade'],
       'OFAC GL52C effective September 14 authorizes qualifying PDVSA transactions under stated conditions and exclusions. EIA historical context describes heavy sour crude and processing constraints. Current incremental recoverable/exportable sulfur is unknown.',
       ids('NUT05', 'NUT06', 'NUT03'), freshness='September 14 license; 2023 structural production context retained as historical', implication='Investigate functioning recovery and delivered contracts before counting reserve; no transaction authorization supplied here.')
signal(39, 'Staged electrification can remove diesel load while preserving food delivery', ['diesel', 'trucking', 'grid', 'food_logistics'],
       'DOE fleet guidance identifies return-to-base duty-cycle opportunities. A 2018 Portland Meals on Wheels case used shore power for parked refrigeration; it does not establish traction conversion or present equipment status.',
       ids('EFS04', 'EFS05', 'EFS06', 'EFS08'), direction='improving', implication='Measure diesel displaced per preserved service and commission charging before retiring working capacity.')
signal(40, 'Community-held property provides an established tenure model', ['commons', 'municipal'],
       'OakCLT documents 2017 acquisition of Liberated 23rd Avenue with housing, nonprofit storefronts and garden. Existing occupancy is protected; no available space or outage endurance established. RYSE, West Oakland and municipal libraries are separate partnership leads.',
       ids('DC03', 'DC08', 'DC02', 'DC04', 'DC07'), direction='improving', geography=['Bay Area'], implication='Seek durable operating rights and community governance; an existing commons is not vacant inventory.')
signal(41, 'Electric replacement changes mineral and coproduct dependencies', ['diesel', 'sulfur', 'grid', 'industrial'],
       'LFP batteries use purified phosphoric acid. Refinery contraction can reduce recovered sulfur if alternate supply and efficiency lag. Neither mechanism establishes that EVs caused current fertilizer curtailments.',
       ids('RC3C03', 'RC3C02', 'NUT03', 'NUT04'), label='PLAUSIBLE MECHANISM', implication='Track industrial grades, deployment stages and coproduct continuity alongside diesel benefits.')
signal(42, 'Food assistance can face simultaneous demand growth and supply loss', ['food_assistance', 'food_logistics'],
       'Conditional hypothesis: widespread physical supply loss can reduce rescued food while increasing assistance demand, with purchasing capacity also strained by prices and transport. Income-based hunger or distribution breakdown can instead coexist with abundant food or stranded surplus.',
       ids('EFS01', 'EFS02', 'EFS03'), label='PLAUSIBLE MECHANISM', direction='unclear', status='Unactivated stress scenario; no famine declaration', implication='Use protected procurement, rotating stock and routes with different failure exposures; cash alone cannot replace absent food.')

for key in ['SIG24', 'SIG27']:
    row('ACTIVE_SIGNALS', key)['last_reviewed_cycle'] = 'RC-003'

def node(key, label, sources, **gauges):
    names = ['LOAD', 'RESERVE', 'RECOVERY', 'DEPENDENCY', 'SUBSTITUTABILITY', 'SHEDDING', 'GROWTH', 'LIFEBOAT', 'SOCIAL_TEMPERATURE', 'CONFIDENCE']
    state['SYSTEM_MAP']['systems'].append({'id': key, 'label': label, 'geography': 'Nested local-to-global context',
        'source_ids': sources, 'gauges': {n: gauges.get(n, 'Unknown; not measured this cycle') for n in names}})

node('sulfur', 'Sulfur recovery and processing acid', ids('NUT01','NUT02','NUT03','NUT04','TRS02','RC3C02'),
     LOAD='Operator curtailments and dated trade disruption', RESERVE='Merchant spare supply and local stocks unknown',
     RECOVERY='Plant- and route-specific; new recovery capacity can take years', DEPENDENCY='Fertilizer plus multiple mineral-processing chains',
     SUBSTITUTABILITY='Alternative acid sources and nutrient recovery require compatible processes',
     SHEDDING='Some avoidable nutrient demand; deficient soils must remain supplied', GROWTH='Acid regeneration, safe nutrient recycling and diversified recovery',
     LIFEBOAT='Verified stocks and crop-specific nutrient plans; local capacity unmeasured', CONFIDENCE='High process evidence; low current donor availability')
node('food_assistance', 'Food assistance and minimum nutrition continuity', ids('EFS01','EFS02','EFS03','EFS07'),
     LOAD='Local current demand-to-service ratio unmeasured', RESERVE='Supply mix verified; emergency days and unrestricted purchasing cash unknown',
     RECOVERY='Needs food, funding, transport, access and paid coordination', DEPENDENCY='Essential household nutrition and health',
     SUBSTITUTABILITY='Purchases/government commodities supplement rescue while markets and funding work',
     SHEDDING='Reduce waste and avoidable handling; preserve essential nutrition and dignified access', GROWTH='Shared procurement, fair farm contracts and storage',
     LIFEBOAT='Proposed rotating purchased minimum supply with ready-to-eat options', CONFIDENCE='High documented channels; conditional shared-shock risk')
node('commons', 'Durably controlled community service spaces', ids('DC03','DC08','DC09','DC05','DC07','DC01'),
     LOAD='Ordinary and emergency access needs; utilization unmeasured', RESERVE='Buildings exist; funded hours and tested outage capacity often unverified',
     RECOVERY='Dependent on staffing, utilities, maintenance, tenure and accessibility', DEPENDENCY='Information, thermal refuge, tools, food coordination and local ties',
     SUBSTITUTABILITY='Another site helps only with independent access and usable capacity',
     SHEDDING='Close nonessential rooms while preserving a staffed essential room', GROWTH='Land stewardship and funded public-community operation',
     LIFEBOAT='Proposed one-room essential service plus a differently exposed partner', CONFIDENCE='Strong named-node evidence; unknown available property and endurance')

def edge(num, a, b, stress, mechanism, sources, buffers, thresholds, substitutes, horizon, uncertainty, confirm, falsify, status):
    state['CASCADE_GRAPH']['edges'].append({'id':f'EDGE{num:02}', 'from':a, 'to':b, 'initiating_stress':stress,
        'dependent_system':b, 'mechanism':mechanism, 'source_ids':sources, 'buffers':buffers,
        'thresholds':thresholds, 'substitutes':substitutes, 'time_horizon':horizon, 'uncertainty':uncertainty,
        'confirm':confirm, 'falsify':falsify, 'activation_status':status})

edge(15,'sulfur','fertilizer','Insufficient affordable, deliverable sulfur/acid',
     'Wet-process phosphate production needs acid; lost feed or unaffordable operation can idle usable mineral-processing capacity.',
     ids('NUT02','TRS02','RC3C02'), 'Stocks, alternative qualified suppliers, acid regeneration and agronomic demand reduction',
     'Plant input cover exhausted or economics force idling; farm effects need unmet orders/application windows',
     'Compatible fertilizer imports and tested recovered phosphorus; N and K do not replace P', 'Days to months; new plants longer',
     'Current downstream inventories and restarts unknown', 'Missed phosphate orders after documented idles',
     'Restarts or replacement supply fill needs on time', 'Upstream curtailment observed; farmer/crop cascade conditional')
edge(16,'diesel','sulfur','Long-run refining throughput contraction',
     'A useful sulfur coproduct may decline as fuel processing contracts; net effect depends on feed sulfur and alternative sources.',
     ids('NUT03','NUT04'), 'Sour-gas recovery, compatible smelter acid, regeneration and reduced avoidable demand',
     'Recovered output falls faster than accessible alternatives and demand reductions', 'Verified sulfur/acid sources and nutrient recovery',
     'Months to years; structural transition', 'No EV attribution for current shortage; net supply response unknown',
     'Linked output loss plus unmet essential acid demand after adaptation', 'Stable delivered supply through contraction',
     'Unactivated conditional transition hypothesis')
edge(17,'grid','trucking','Depot charging unavailable or insufficient',
     'Electrified routes shift replenishment from diesel delivery to chargers and electrical service; simultaneous outages can remove the substitute.',
     ids('EFS04','EFS06'), 'Charged reserve vehicles, managed charging and genuinely independent charging paths',
     'Usable energy cannot cover essential route through replenishment interruption', 'Compatible alternate depot; pooled essential trips; phased fleet transition',
     'Hours to days during outages; months/years for interconnection', 'Site route, payload, weather and charger data absent',
     'Named missed deliveries linked to charger/feeder failure', 'Routes completed with tested independent replenishment',
     'Planning dependency; no named fleet failure established')
edge(18,'food_logistics','food_assistance','Supply disruption alongside increased need',
     'Rescued supply may fall while food prices, demand for aid and delivery costs rise. Stranded surplus elsewhere is not automatically usable.',
     ids('EFS01','EFS02','EFS03'), 'Separate purchasing fund, USDA channels, rotating stocks and route-diverse suppliers',
     'Delivered usable nutrition falls below agreed essential service floor after purchases and inventory drawdown',
     'Funded interregional procurement and safe menu substitution; cash assistance where markets work', 'Days to months',
     'No local reserve-days baseline or current famine; some disruptions increase recoverable surplus',
     'Dated rise in unmet requests plus falling recoveries/fulfillment and insufficient independent cover',
     'Stable essential service despite changing donation mix', 'Unactivated shared-shock hypothesis')
edge(19,'municipal','commons','Operating-budget pressure',
     'Reduced paid opening hours can remove accessible community refuge and information capacity even when the building remains intact.',
     ids('DC09','DC05','DC06'), 'Protected activation budget, paid staff, durable access agreement and differently funded partner',
     'Reduced hours overlap verified essential need and alternate sites cannot absorb it', 'Accessible partner site with independent funded operation',
     'Weeks/months for budget changes; hours during events', 'No heat-related harm measured in Hayward',
     'Service closures during needed activation with unmet demand', 'Funded emergency hours and successful accessible activation',
     'Ordinary hours reduction observed; emergency cascade conditional')
edge(20,'trade','fertilizer','Cargo disruption or inaccessible maritime route',
     'Loss, delay or rerouting consumes freight capacity and working capital; consequences depend on local cover and crop timing.',
     ids('MAR05','MAR07','RC3C02'), 'Stocks, route-diverse origins, vessel security and confirmed replacement bookings',
     'Delay exceeds usable cover or application deadline', 'Alternate origin/port/route with correct product and verified capacity',
     'Days to months', 'No California exposure or current route-wide closure established',
     'Matched shipment loss, depleted stocks and missed customer orders', 'Replacement arrives before need or procurement chain unaffected',
     'Specific historical fertilizer-cargo interruption observed; broader cascade conditional')
edge(21,'industrial','grid','Concentrated equipment and battery inputs',
     'A substitute can be available as a design but not in the required grade, equipment, workforce or delivery slot; LFP manufacturing uses purified phosphoric acid.',
     ids('RC3C02','RC3C03','EFS06'), 'Repair, compatible spares, diversified processing and equipment procurement',
     'Verified critical orders delay essential commissioning or repair', 'Suitable alternate chemistry/design after engineering review; preserve functioning assets',
     'Months to years', 'No evidence LFP demand caused current fertilizer curtailments; grade conversions are not automatic',
     'Documented input-related commissioning slippage without alternatives', 'Timely equipment delivery or effective substitution',
     'Structural concentration and planning dependency; project-level activation unverified')

def reserve(key,name,kind,sources,readiness,limits,guard,function):
    state['RESERVES_AND_LIFEBOATS'].append({'id':key,'name':name,'type':kind,'source_ids':sources,'readiness':readiness,
       'limits':limits,'donor_guardrail':guard,'essential_function':function})

reserve('RES15','ACCFB shared purchasing channels','Operating procurement model',ids('EFS02','EFS03','EFS07'),
        'Documented FY2025 channels; current emergency allocations unverified','Funds, supplier harvests, roads and cold storage can fail together',
        'Protect existing households, donor farm viability and restricted funds; reserve no uncommitted volume without evidence','Acquire usable food beyond rescued surplus')
reserve('RES16','Rotating minimum food supply','Proposed community lifeboat',ids('EFS01','EFS03'),
        'Design only; no food purchased or space secured','Duration requires menu, usable stock, water, preparation and delivery data',
        'Build through normal purchasing and rotation, preserve nutrition/access and avoid draining existing distributions','Minimum nutrition through replenishment interruption')
reserve('RES17','Durable commons operating rights','Proposed institutional buffer',ids('DC03','DC08','DC06'),
        'Tenure models verified; no new agreement or available property secured','Ownership, keys, staffing, permitted use and backup endurance are distinct',
        'Protect current residents/users, pay core labor and fund maintenance before expansion','Continuity of accessible space and essential services')
reserve('RES18','Western electricity exchange','Existing exchange network',ids('RC3C01','MAR08'),
        'Operational market; current deliverable surplus unknown','Regional heat, fire, drought and constrained lines can reduce both local and donor reserve',
        'Count only dispatchable offer above donor commitments/floor and within transfer capability at the needed hour','Balance geographically differing power availability')

audits = {
 'RES01': ('Fuel stock may be remote or already committed','Refinery/terminal/route disruptions and multiple vendors sharing one supplier','Delivered allocation and protected critical-fuel cover'),
 'RES02': ('Global grain stock is not local usable nutrition','Export restrictions, affordability and shared routes','Correct product, ownership, route and timely local delivery'),
 'RES03': ('A fiscal bridge expires or defers repair','Shared tax base, borrowing access and future capital needs','Dated cash receipts plus protected maintenance/service floor'),
 'RES04': ('Neighboring grids peak together','Heat, drought, fire and transmission limits','Separate regional networks; verify hour-specific offers and paths'),
 'RES05': ('Response roster members may be affected too','Regional hurricane, travel and staffing constraints','Available people, transport and home-service floor'),
 'RES06': ('Food referrals point to supply also under strain','Shared wholesalers, donations, delivery routes and funding','Current open hours, fulfillment, procurement and inventory'),
 'RES07': ('Tools exist but cannot be reached or maintained','Building access, staff, repairs and power','Open access, working tools and trained repair capacity'),
 'RES08': ('A project listing may precede usable backup','Capital delays, utilities, paid staffing and public access','Commissioned and exercised essential service'),
 'RES09': ('Relief drivers and vehicles face the same shock','Fuel/charging, roads, illness and household commitments','Confirmed accessible trips above protected obligations'),
 'RES10': ('Backup equipment lacks endurance or replenishment','Grid, fuel, refrigeration maintenance and room access','Measured critical load and tested replenishment'),
 'RES11': ('A reported spare route does not match need','Cargo type, border, driver hours and backhaul','Confirmed suitable booking at required time'),
 'RES12': ('Constructed microgrid may lack public activation','Town staff, battery state, water and accessible hours','Published and exercised public outage service'),
 'RES13': ('Reservoir water may lack treatment or delivery','Pumps, treatment chemicals, network damage and power','Dated storage plus actual potable delivery capacity'),
 'RES14': ('Awarded capital/cash may not be spendable now','Restricted uses, disbursement delays and payroll','Received eligible funds and staffed clinical service'),
 'RES15': ('Purchasing cannot create absent food','Same farms, wholesaler, credit, roads and utility','Contracted usable food plus protected operating cash'),
 'RES16': ('Stored staples require preparation and rotation','Water, energy, diet compatibility and staffing','Measured usable meals under a defined drill'),
 'RES17': ('Control of property does not provide operations','Debt, staffing, insurance, utilities and maintenance','Enforceable funded rights plus demonstrated service'),
 'RES18': ('Imports may shrink during a common regional peak','Donor load and shared transmission exposure','Verified protected-floor surplus and transfer path')
}
for r in state['RESERVES_AND_LIFEBOATS']:
    expectation, shared, proof = audits[r['id']]
    r['shared_failure_audit'] = {'epistemic_label':'PLAUSIBLE MECHANISM','expectation_gap':expectation,
        'shared_failure_modes':shared,'required_service_proof':proof,'audit_status':'Structural screening; not a quantified common-shock reserve test',
        'current_stressed_surplus':'Unknown unless separately measured in readiness record'}

state['ISLANDS_OF_STABILITY'].extend([
 {'id':'ISL07','name':'Western power complementarity','source_ids':ids('RC3C01','MAR08'),
  'offers':'Hourly exchange of available generation/flexibility through physical interconnection',
  'needs_in_return':'Reciprocal balancing, transmission, reliable contracts and donor load protection',
  'available_surplus':'Unknown at the required hour; market membership is not spare capacity',
  'donor_guardrail':'Retain essential demand and contingency reserves, then verify path and delivery',
  'limits':'Common heat/drought/fire and line constraints; overseas electricity is not a direct substitute','self_sufficient':False},
 {'id':'ISL08','name':'Sour-gas sulfur recovery network: Shah example','source_ids':ids('NUT08','NUT03','RC3C02'),
  'offers':'Established industrial sulfur recovery; operator names 4.2 million tons/year capacity',
  'needs_in_return':'Working equipment, gas operations, maintenance, customers, lawful shipping and finance',
  'available_surplus':'Uncommitted operating output and delivered reserve unknown',
  'donor_guardrail':'Existing customers and domestic gas obligations take precedence over hypothetical rescue',
  'limits':'Capacity is not inventory; common regional route exposures remain','self_sufficient':False},
 {'id':'ISL09','name':'East Bay community land and purchasing institutions','source_ids':ids('DC03','DC08','EFS03','DC02'),
  'offers':'Existing land-stewardship models, community space, organizing and food purchasing experience',
  'needs_in_return':'Funded staffing, utilities, maintenance, food suppliers and shared governance',
  'available_surplus':'No available property or uncommitted service slots verified',
  'donor_guardrail':'Protect existing occupants, youth/community programs and food recipients',
  'limits':'Institutional continuity is relative; site outage endurance remains unmeasured','self_sufficient':False}
])

def transition(key,name,cluster,classification,function,assets,shed,growth,requirements,horizon,risks,sources,success):
    state['TRANSITION_OPPORTUNITIES'].append({'id':key,'name':name,'cluster_id':cluster,'classification':classification,
        'function_to_preserve':function,'released_assets':assets,'safe_load_release':shed,'growth_candidate':growth,
        'conversion_requirements':requirements,'time_horizon':horizon,'risks':risks,'source_ids':sources,
        'status':'Proposed transition with dated operating examples; no local procurement commitment','success_observation':success})

transition('TR09','Replace suitable diesel functions in stages','CL08','Conditional healthy replacement and managed shedding',
 'Reliable delivery, refrigeration and accessible mobility','Avoidable idling/fuel expense; repairable chassis and mechanical skills only where usable',
 'Parked diesel refrigeration/idling and unnecessary trips while preserving temperature and access',
 'Shore power, return-to-base electric routes, suitable repowers, charging and repair services',
 'Measured duty cycle, lifecycle cost, compatible equipment, funded electrical service, trained maintenance and outage plan',
 'Existing applicable technology; site installation months or longer','Charging bottlenecks, battery/equipment concentration and premature retirement of working capacity',
 ids('EFS04','EFS05','EFS06','EFS08','RC3C03'), 'Same essential deliveries and temperatures with less diesel, acceptable costs and demonstrated fallback')
transition('TR10','Give surplus recovery an independent minimum food supply','CL07','Creative transition toward dependable nutrition',
 'Usable food access including people lacking kitchens, power or transport','Shared buying/storage capability and recoverable food; surplus quantity may decrease',
 'Waste and redundant handling, not essential meals','Fair farm purchasing, regional aggregation, rotating staple stock and protected operating finance',
 'Separate supply-channel ledger, replenishment routes, nutrition/food safety, paid staff, water and cooking/ready-to-eat options',
 'Weeks/months for a pilot; wider reserves longer','Cash loses buying power in physical shortage; local-only farms can share weather; pantry stock without access is not a meal',
 ids('EFS01','EFS02','EFS03','EFS07'), 'Essential service persists during a defined loss-of-donations/replenishment exercise without draining donor floors')
transition('TR11','Convert existing civic/community assets into durably operated commons','CL04','Potential creative transition; ordinary services preserved',
 'Accessible thermal refuge, information, tools and coordination','Possible underused rooms and partner skills; no vacancy or transferable asset assumed',
 'Nonessential conditioned area and duplicate purchases','Community land stewardship and funded public-community operation',
 'Negotiated tenure, keys, permitted activity, governance, maintenance, core paid staffing and tested critical utility support',
 'Agreement/pilot months; acquisition/capital longer','Displacement, unfunded ownership costs, revocable access and utilities shared with affected neighborhood',
 ids('DC03','DC08','DC05','DC06','DC07','DC01'), 'Reliable agreed opening and essential service with accountable resident participation')
transition('TR12','Preserve sulfur and acid functions through refining transition','CL03','Conditional creative transition',
 'Agronomically necessary nutrients and useful processing acid','Recovery expertise and adaptable assets only where technically suitable',
 'Avoidable fertilizer use determined by soil/crop testing and process losses',
 'Acid regeneration, qualified alternative recovery and recycled phosphorus','Input specifications, environmental controls, nutrient testing and funded compatible processing',
 'Efficiency now; major industrial changes years','No automatic grade conversion or sufficient recovery scale; contamination and transport costs',
 ids('NUT02','NUT03','NUT04','NUT07'), 'Delivered essential nutrients preserved while unnecessary fuel demand contracts')

def commons(key,name,cluster,who,steps,floor,measure,resources,sources):
    state['COMMUNITY_COMMONS'].append({'id':key,'name':name,'cluster_id':cluster,'status':'Proposed; no outreach, space reservation or purchase',
       'who_can_act':who,'first_steps':steps,'protected_floor':floor,'success_measure':measure,
       'resources':resources,'source_ids':sources,'recordkeeping':'Aggregate service and supply measures; no personal histories or public beneficiary lists'})

commons('COM08','Purchased nutrition floor and cooperative replenishment','CL07','Food bank partners, farms, community kitchens and neighborhood organizations',
 ['Define a minimum useful menu with ready-to-eat and dietary-access options.',
  'Separate recovered, purchased, government and already-stored food; trace shared suppliers/routes.',
  'Cost normal stock rotation, reserve procurement and paid handling together.',
  'Test loss of the largest donation source plus a delayed replenishment route against usable meals.'],
 'Protect regular recipients, farm viability, food safety, workers and unrestricted operating cash',
 'Minimum usable meals delivered through the agreed exercise, with donor floors intact',
 'Existing purchasing channels; proposed rotating stocks, suitable storage, water, preparation and transport; no committed surplus',ids('EFS01','EFS02','EFS03','EFS07'))
commons('COM09','Durably controlled one-room commons with partner node','CL04','Resident-led organizations, library staff, land trusts and municipal partners',
 ['Use verified node shortlist; protect current occupants and programs.',
  'Negotiate term, keys, storage, hours, permitted uses and alteration/maintenance rights.',
  'Fund core staffing and a critical-load/water/sanitation plan before counting reserve.',
  'Pair with a node having different power, route, funding or hazard exposure and run a small service drill.'],
 'No displacement; fair access and paid core labor; each node retains protected ordinary service',
 'Agreed accessible opening and essential functions demonstrated during a defined interruption',
 'One room, secure storage, toilet, drinking water, communications and suitable thermal/power support; all site capacities to be measured',ids('DC03','DC08','DC05','DC06','DC07','DC01'))
commons('COM10','Electrify one suitable food-logistics function','CL08','Community meal providers, fleet operators, mechanics and qualified electrical partners',
 ['Measure route distance/load, idle hours, refrigeration and return-to-base windows.',
  'Assess shore-power refrigeration before or alongside traction conversion.',
  'Confirm electrical service, charging access, cost and maintenance support.',
  'Prove essential delivery and replenishment during an outage scenario before retiring replacement-covered equipment.'],
 'Preserve food temperatures, driver rest, accessible service and a charged/otherwise usable essential-trip reserve',
 'Diesel consumed per completed essential delivery falls without worse reliability or shifted unpaid labor',
 'Real operating data and engineering assessment; no vehicle order or grant entitlement assumed',ids('EFS04','EFS05','EFS06','EFS08'))

def cluster(key,title,signals,buffers,transitions,common,outside,lifeboats,sources,status,interaction):
    state['SYSTEM_MAP']['clusters'].append({'id':key,'title':title,'signal_ids':signals,'buffers':buffers,
      'transition_ids':transitions,'commons_ids':common,'outside_reserve':outside,'lifeboats':lifeboats,
      'source_ids':sources,'status':status,'interaction':interaction,
      'independence':'Evidence of structure or separate events does not automatically establish synchronized local service failure.'})

cluster('CL07','Food assistance and correlated supply/funding loss',['SIG32','SIG33','SIG42'],['RES06','RES15','RES16'],['TR10'],['COM08','COM02'],['ISL02','ISL09'],['RES16'],ids('EFS01','EFS02','EFS03','EFS07'),
        'Conditional stress scenario with operating procurement counterevidence; no famine inferred',
        'A supply shock can raise assistance need while reducing rescue and buying power; income and distribution shocks have different remedies.')
cluster('CL08','Diesel replacement and new grid/material dependencies',['SIG39','SIG41'],['RES01','RES10','RES18'],['TR09'],['COM10'],['ISL07'],['RES09','RES10'],ids('EFS04','EFS05','EFS06','EFS08','RC3C02','RC3C03'),
        'Transition case; no named electric fleet failure established',
        'Diesel demand can be shed while new charger, grid, parts and industrial-grade input dependencies need working buffers.')
cluster('CL09','Maritime routes and nutrient deliverability',['SIG35','SIG36','SIG37','SIG38'],['RES01','RES02'],['TR12','TR02'],['COM05','COM08'],['ISL01','ISL02','ISL08'],['RES16'],ids('MAR01','MAR02','MAR04','MAR05','MAR07','NUT05','RC3C02'),
        'Specific cargo interruption and dated acid stress; California cascading impact unverified',
        'Piracy, war risk, legal access and transport timing are separate filters on otherwise available material.')
row('clusters','CL03')['signal_ids'] += ['SIG37','SIG38','SIG41']
row('clusters','CL03')['transition_ids'] += ['TR12']
row('clusters','CL03')['source_ids'] += ids('NUT02','NUT03','RC3C02')
row('clusters','CL04')['signal_ids'] += ['SIG34','SIG40']
row('clusters','CL04')['buffers'] += ['RES17']
row('clusters','CL04')['transition_ids'] += ['TR11']
row('clusters','CL04')['commons_ids'] += ['COM09']
row('clusters','CL04')['source_ids'] += ids('DC09','DC03','DC08')

def question(num,question,why,action,owner,sources,trigger,priority='high'):
    state['QUESTIONS_TO_WATCH'].append({'id':f'Q{num:02}','priority':priority,'question':question,'why_it_matters':why,
       'next_public_action':action,'owner_role':owner,'source_ids':sources,'revisit_trigger':trigger,
       'status':'open','user_manual_work_required':False,'last_reviewed_cycle':'RC-003'})
question(16,'What changes in Bayer/Monsanto evidence, operating access and governance?',
 'Health/ecological evidence, market access, legal liabilities and operational capacity are distinct; concentration can affect choices without proving hostile intent.',
 'Follow EPA docket and assessment, independent research/retractions, company filings, court orders, distributor access, licensing and qualified agronomic alternatives; verify every claimed causal link.',
 'Signal Intake + Food + Industry + Skeptic',ids('BAY01','BAY02','BAY03'),'New assessment/order/filing, documented product access change or independently supported harm; next active research cycle')
question(17,'How many usable food-service days survive losing a major supply channel?',
 'Annual pounds and referral lists do not reveal stressed reserve.',
 'Read current public food-bank reports for supply mix, purchased-food cash, delivery fill rates and usable stocks; derive no local ratio from national totals.',
 'Food + Commons',ids('EFS01','EFS02','EFS03'),'New operating data or reported unfilled distributions')
question(18,'Which local diesel function can be replaced with demonstrated reliable service?',
 'A staged replacement can preserve scarce diesel for less substitutable work.',
 'Use public fleet/utility plans and project disclosures to identify return-to-base routes, shore-power sites, energized chargers and maintenance support.',
 'Energy + Infrastructure + Commons',ids('EFS04','EFS05','EFS06','EFS08'),'Named commissioning, duty-cycle results or delayed electrical service')
question(19,'Which commons candidate can secure lasting control and funded public operation?',
 'Existing space, community ownership and actual emergency service are separate stages.',
 'Inspect public property/project records and operating agreements for tenure, keys, hours, storage, allowed alterations, budget and activation rights; record lack of availability candidly.',
 'Commons + Geographic Context',ids('DC03','DC08','DC06','DC07','DC01'),'Published offering or operating agreement; no contact without authorization')
question(20,'Which sulfur/acid offers are genuinely deliverable after donor commitments?',
 'Sour crude or large recovery capacity alone cannot fill a fertilizer order.',
 'Seek dated operator recovery utilization, restart, merchant stock and shipment evidence; verify Venezuela legal scope and recipient recovery capacity separately.',
 'Energy + Food + Industry',ids('NUT05','NUT06','NUT08','RC3C02'),'New recovery/restart/export evidence or applicable authorization change')
question(21,'Are the relevant routes currently usable, insurable and timely?',
 'H1 incident totals and a July conflict account cannot establish September passage.',
 'Obtain dated operator/security/port reports and matched voyage denominators; separate war, piracy, sanctions and insurance; link any delay to actual orders.',
 'Trade + Geographic Context + Skeptic',ids('MAR01','MAR02','MAR04','MAR07','RC3C02'),'New dated route advisory or matched shipment/fulfillment record')
question(22,'Does transition planning preserve useful coproducts and independent fallback?',
 'Retiring fuel demand can alter sulfur output; electric systems need compatible materials and charging.',
 'Track refinery sulfur continuity, acid regeneration and crop-specific nutrient efficiency alongside commissioned electric service; reject unsupported battery-caused famine narratives.',
 'Cascade Modeler + Resilience + Skeptic',ids('NUT03','NUT04','RC3C03','EFS06'),'Documented coproduct output loss or replacement project data','medium')
row('QUESTIONS_TO_WATCH','Q13')['status'] = 'partially addressed: Mosaic independently rechecked; remaining RC-002 claims still require scoped review'
row('QUESTIONS_TO_WATCH','Q13')['last_reviewed_cycle'] = 'RC-003'

state['SYSTEM_MAP']['replacement_protocol'] = {
 'definition':'A technology/institution can decline beneficially if its essential function is preserved and new dependencies are supportable.',
 'required_fields':['Function to preserve','Avoidable load','Released assets actually accessible','Replacement maturity and tested service','New dependencies and shared failures','Useful coproducts at risk','Worker/community effects','Transition funding and timeline','Reversal/fallback conditions'],
 'first_case':'TR09: staged diesel replacement; technology existence is not site readiness',
 'success_rule':'Verified essential service with lower avoidable load and adequate reserves; no simple green/red technology label'
}
state['CASCADE_GRAPH']['reserve_independence_rule'] = 'Stress-test the fallback under the same initiating event. Trace shared suppliers, routes, grids, funders, staff, tenure and replenishment; multiple names need not mean independent capacity.'
state['SYSTEM_MAP']['coverage_inventory'] += [
 {'area':'Food-assistance reserve dependence','status':'National supply mix and local procurement channels verified; local current stressed reserve unknown'},
 {'area':'Bayer/Monsanto','status':'Evidence and governance watch established; no operational shortage or present-intent attribution'},
 {'area':'Maritime security','status':'Dated regional incidence and response evidence; live chokepoint and voyage exposure gaps'},
 {'area':'Durable commons control','status':'Five existing nodes/models verified; no available property or new operating agreement secured'}
]
for n in state['SYSTEM_MAP']['systems']:
    if n['id']=='diesel': n['gauges']['GROWTH']='Staged shore-power and suitable fleet electrification; preserve sulfur coproduct function separately'
    if n['id']=='fertilizer': n['gauges']['SUBSTITUTABILITY']='N, P and K not interchangeable; sulfur/acid recovery and tested recycled P can help, with grade and capacity gates'

checks = [
 ('RC003-IR01','Mosaic August 27 curtailments','nutrient_network','Independently confirmed operator disclosure; September restart and farmer effects unknown',ids('TRS02')),
 ('RC003-IR02','SWARD fertilizer cargo and July captivity','nutrient_network','Independently confirmed April event and July status; September status/California link unknown',ids('MAR05')),
 ('RC003-IR03','IEA shared sulfur/acid dependency','nutrient_network','Independently confirmed July report; does not clear or close a September route',ids('RC3C02')),
 ('RC003-CR01','Food banks are only supplied by rescued surplus','coordinator','Rejected; purchased and government channels documented, with own funding/logistics constraints',ids('EFS02','EFS03','EFS07')),
 ('RC003-CR02','San Anselmo is a fully tested public outage lifeboat','coordinator','Downgraded to constructed infrastructure and solar operation; public activation/endurance unknown',ids('DC01')),
 ('RC003-CR03','Bayer is responsible for current sulfur constraint','coordinator','Not established; separate corporate watch and input-chain evidence',ids('BAY01','TRS02')),
 ('RC003-CR04','Several vendors or partners guarantee independent rescue','coordinator','Rejected as an assumption; shared upstream failures and donor floors must be tested',ids('EFS03','MAR08'))
]
for key,claim,reviewer,decision,sources in checks:
    state['CASCADE_GRAPH']['review_decisions'].append({'id':key,'claim':claim,'reviewer':reviewer,'decision':decision,'source_ids':sources})
closing = json.loads((inbox/'closing_review.json').read_text())
meta['review_scope']['closing_candidate_review'] = {
 'record':'inbox/RC-003/closing_review.json',
 'reviewed_candidate_sha256':closing['candidate_file_sha256'],
 'scope':closing['scope'], 'decision':closing['decision'],
 'limitations':closing['explicit_limits'],
 'coordinator_followup':'Applied may shrink wording to RES18; added review metadata and healthy food-waste transition guidance. The original review covers its recorded pre-final candidate hash; final admission is coordinator acceptance with limitations.'}
meta['agent_runs'].append({'name':'nutrient_network_review','status':'Scoped closing review delivered; nutrient-input authorship limits independence','full_report_received':True})
row('TRANSITION_OPPORTUNITIES','TR10')['healthy_decline_test'] = 'Reducing avoidable food waste is desirable even if rescued donations shrink. Preserve minimum nutrition through predictable procurement and income/access support; do not preserve waste to preserve charitable supply.'
state['CASCADE_GRAPH']['review_decisions'].append({
 'id':'RC003-SR01','claim':'Conditional new edges and reserve claims',
 'reviewer':'nutrient_network_review','decision':'Scoped pass with limitations for EDGE15-21 and RES15-18; reviewer authored nutrient inputs; pre-final hash and full limits preserved in closing_review.json',
 'source_ids':[]})
state['CHANGELOG'].append({'date':'2026-09-21','cycle':'RC-003','action':'Research and model expansion',
 'details':'Added Bayer watch, sulfur/phosphate/Venezuela distinction, regional maritime evidence, durable commons leads, conditional diesel replacement and shared-failure audits for every reserve. No famine, blanket piracy escalation, available property or uncommitted international surplus asserted.'})
state['CHANGELOG'].append({'date':'2026-09-21','cycle':'RC-003','action':'Integrity repair',
 'details':'Reassembled original sentence text in four RC-002 list fields: '+', '.join(repairs)+'. Historical cycle unchanged; validator rejects fragmented narrative. Baseline hashes remain authoritative across stricter validation; every new candidate passes current rules. Regression tests cover blocked admission, migration and canonical-state preservation.'})

# Any specialist aliases referenced by this integrator resolve to one source identity.
def remap(value):
    if isinstance(value, dict):
        for k,v in value.items():
            if k=='source_ids': value[k]=list(dict.fromkeys(aliases.get(x,x) for x in v))
            else: remap(v)
    elif isinstance(value,list):
        for v in value: remap(v)
remap(state)
(FOLDER/'candidate.json').write_text(json.dumps(state,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
(FOLDER/'source_aliases.json').write_text(json.dumps(aliases,indent=2,sort_keys=True)+'\n')
print('Built RC-003 candidate with',len(state['ACTIVE_SIGNALS']),'signals and',len(state['SOURCE_LEDGER']),'sources; repaired',repairs)
