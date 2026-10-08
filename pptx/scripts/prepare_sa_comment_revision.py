"""Prepare revised copy and comment dispositions; does not author PowerPoint files."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORY = ROOT / 'pptx/story'
def save(name, value):
    (STORY / name).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')

plan = json.loads((STORY / 'sa_review_signed_off_2026_10_07.json').read_text())
plan['cover_title'] = 'South Africa\nmarket review\nwork programme'
plan['cover_subtitle'] = 'Revised following review comments'
plan['cover_status'] = 'Scope approved; revised delivery specification'
s = plan['slides']
for x in s:
    x['sub'] = ''
s[0]['rows'][1][2] = 'Four explicit complications. Evidence and mechanics now; scenario calibration deferred.'
s[0]['rows'][2][2] = 'Share inference, catchment dashboards and a specified financial forecast. Commercial inputs remain open.'
s[1]['rows'][0][2] = 'Explain weak real activity and investment separately from changes in sector mix. Test manufacturing trends and agriculture headwinds; do not assume either causes the full fuel trend.'
s[1]['rows'][1][2] = 'Separate short shipping/crude/FX shocks from persistent delivered-price changes. Test EV total ownership cost, then adoption and fleet turnover. Energy savings alone do not establish uptake.'
s[2]['rows'][2][2] = 'Prioritise Durban–Gauteng road and rail, with pipeline as fuel benchmark. Use the supplied funding brief, then verify Network Statement v4 / Annexure 17 capacity, funding and delivery milestones.'
s[2]['note'] = 'Transnet 250 Mt ambition is network-wide. Supplied AIA brief cites funding dependency; primary corridor tables still require reconciliation.'
s[4]['headers'][1] = 'Mechanics to develop'
s[4]['rows'][0][1] = 'Durban–Gauteng first: transferable commodities, haul distance, rail capacity, reliability and funding milestones.'
s[4]['rows'][3][1] = 'Mining output, agriculture activity and aviation traffic, supported by GDP and investment evidence.'
s[4]['rows'][3][2] = 'Separate mining/agriculture diesel from aviation jet fuel. Manufacturing is contextual. Avoid adding FDI or confidence multipliers to the same activity effect.'
s[4]['note'] = 'Scenario levels and dates will follow separately. Freight displacement and fuel-distribution routing are distinct calculations.'
s[5]['sub'] = ''
s[5]['headers'][0] = 'Power-system driver'
s[5]['note'] = 'Power and load shedding remain a standalone complication. No new forecast paths are calibrated in this revision.'
s[6]['rows'][0] = ['SAPREF restart', 'Separate finished-product import operations from a future refinery restart and ramp-up.', 'CEF roadmap identifies staged ambitions, subject to investment and approvals. Capacity announcements are not operating output.']
s[6]['rows'][1] = ['Secunda production', 'Declining gas supply and diversion to methane-rich gas (MRG) could reduce liquid-fuel output.', 'User clarification adopted. Source the gas balance and marginal liquid yield before quantifying the loss.']
s[6]['note'] = 'Research candidates confirmed: SAPREF and Natref. Secunda driver corrected to gas decline and MRG diversion; scenarios deferred.'
s[7]['rows'][3] = ['Origin–destination submodel', 'Delivered fuel cost for the same product and destination via Durban, Matola and Walvis Bay.', 'Calculate price bearability, route headroom and feasible volume. Include border costs, losses, inventory finance, reliability and capacity constraints.']
s[7]['note'] = 'Delivered-cost module specification: origin + destination + product + period; compare feasible routes and their maximum affordable logistics charge.'
s[8]['title'] = "Catchment dashboards must connect Vopak's market position to a financial forecast"
s[8]['rows'][0] = ['Current market share', 'Gauteng is the provisional Lesedi catchment. Test capacity-based inference while actual terminal throughput remains unavailable.', 'Separate observed demand, capacity proxies and inferred throughput. Show denominator coverage and transfers between Durban and Lesedi.']
s[8]['rows'][1] = ['Catchment deep dives', 'Separate Durban and Gauteng dashboards: demand, imports/supply, routes, competitor capacity and inferred share.', 'Include source vintage, uncertainty and capacity headroom. Future scenario outputs follow after calibration.']
s[8]['rows'][3] = ['Financial forecast', 'Translate contracted storage and billable handling into revenue, opex, EBITDA and cash flow, then capex, NPV and IRR.', 'Investment-board decision page: returns, utilisation/break-even, funding, phasing and triggers. Rates, contracts, capex and hurdle rate remain open.']
s[8]['note'] = 'Commercial inputs are unavailable. Provide a transparent share inference now; quantify the financial forecast once commercial assumptions are supplied and reviewed.'
s[9]['rows'][1][1] = 'Gauteng catchment and SAPREF/Natref scope adopted. Prioritise Durban–Gauteng; validate remaining corridor definitions.'
s[9]['rows'][4][1] = 'Deferred by user. Retain the step for later calibration of coherent demand, supply and routing paths.'
s[9]['rows'][5][1] = 'Build share-inference dashboards and financial forecast structure, then populate with reviewed commercial inputs.'
s[10]['rows'][1][1] = 'Gauteng provisional catchment; SAPREF/Natref candidates; Secunda gas decline/MRG driver. Remaining routes and denominators require evidence.'
s[10]['rows'][2][1] = 'Origin–destination delivered-cost submodel, unique terminal deliveries, and storage/handling financial forecast.'
s[10]['note'] = 'All annotated comments have a disposition in the accompanying comment log. Scope sign-off does not approve new evidence or results.'
save('sa_review_comments_applied_2026_10_07.json', plan)

slides = []
def table(title, section, rows, note, headers=('Evidence', 'Interpretation', 'Implication for Vopak')):
    slides.append(dict(title=title, section=section, sub='', headers=headers, rows=rows, note=note))
def chart(title, section, filename, takeaway, note):
    slides.append(dict(title=title, section=section, sub='', chart=filename, takeaway=takeaway, note=note))

table('Vopak’s opportunity depends on import needs and the routes customers choose', 1, [
 ['Demand', 'Petrol and diesel have diverged. Power recovery can remove a source of diesel demand.', 'Separate product and end-use trends before projecting terminal volumes.'],
 ['Supply', 'Domestic plant output and restart timing can change import requirements even with flat demand.', 'An import opportunity can grow without equivalent growth in national consumption.'],
 ['Capture', 'Durban competes through delivered cost and service into inland markets.', 'Test accessible customer volumes, then the storage and handling economics.'],
], 'Working synthesis of the evidence on subsequent pages. Scenarios deferred; no investment recommendation or measured Vopak throughput share.')
chart('Petrol fell 19% over 2013–2023 while diesel rose 9%',2,'01_demand.svg',
 'The flat-market shorthand hides different product trajectories. Demand growth alone is an insufficient basis for tank investment.',
 'Department fuel sales, 2013–2023, same-series comparison. FIASA 2024 shown separately; source definitions require reconciliation.')
chart('GDP and fuel volumes need separate explanations of activity and sector mix',2,'02_growth.svg',
 'Economic weakness means limited growth in real activity and investment. Structural change means a different mix of output, travel and fuel use; this chart alone cannot attribute causality.',
 'Staged GDP and department fuel sales, indices 2013=100. Sector attribution remains open; COVID distorts short-period comparisons.')
chart('Investment evidence informs the growth outlook but does not establish extra fuel demand',2,'03_investment.svg',
 'Fixed investment helps frame productive capacity. FDI can include large transactions; neither series is a direct investor-confidence measure or an additional fuel-demand multiplier.',
 'World Bank WDI, FDI net inflows and gross fixed capital formation as % of GDP, 2010–2025. Confidence series remains an evidence gap.')
table('Mining, agriculture and aviation require distinct demand explanations',2,[
 ['Mining', 'Output, commodity mix and haul distance influence diesel use and freight.', 'Separate mine activity from the fuel impact of changing freight mode.'],
 ['Agriculture', 'Crop cycles, weather, irrigation and logistics can shift seasonal diesel use.', 'Establish sector activity and fuel exposure before assigning a headwind.'],
 ['Aviation', 'Traffic, distance, load factors and aircraft efficiency drive jet-fuel demand.', 'Keep jet fuel separate from petrol/diesel shares and verify terminal eligibility.'],
 ['Manufacturing', 'Real output and industrial composition help explain the economic backdrop.', 'Test changes using sector data; a national fuel chart does not prove deindustrialisation.'],
], 'Analytical framework following user comments. Sector-specific exhibits and causal attribution remain to be completed.')
chart('Fuel-price shocks affect running costs; sustained economics influence EV uptake',2,'04_prices.svg',
 'Shipping disruption, crude prices and FX can move fuel costs temporarily. EV adoption depends on sustained total ownership cost, purchase affordability, charging access and fleet replacement.',
 'Department fuel-price history, nominal R/litre. No quantified geopolitical premium or calibrated EV adoption response is asserted.')
table('More efficient new vehicles reduce fuel intensity gradually as the fleet turns over',2,[
 ['Fleet growth', 'More vehicles or distance travelled can raise demand.', 'Measure activity before attributing lower fuel volumes to efficiency.'],
 ['Efficiency', 'New-cohort consumption gains enter the fleet over successive replacement cycles.', 'Obtain OEM and real-world evidence by segment; do not apply new-vehicle gains to every vehicle.'],
 ['EV substitution', 'EVs remove some combustion-engine vehicle activity from the fuel calculation.', 'Count each vehicle transition once, then calculate efficiency on the remaining combustion fleet.'],
], 'Mechanism supported by existing cohort architecture. OEM historical and future efficiency evidence is still missing; no new forecast shown.')
chart('Eskom’s reported OCGT fuel use fell 40% in FY2025',2,'05_eskom_fuel.svg',
 'Reported fuel fell from 1,129.5 to 679.1 million litres as EAF improved from 54.56% to 60.60%. This removes part of the recent diesel-demand support.',
 'Eskom integrated report 2025: FY March, own-fleet diesel + kerosene. EAF association is not a dispatch model; private backup use excluded.')
chart('Road-to-rail recovery matters through transferable freight and haul distance',2,'08_freight.svg',
 'Payload establishes the historical direction. Diesel displacement requires corridor tonne-kilometres, road fuel intensity, rail traction and last-mile activity.',
 'Stats SA monthly freight payload, complete calendar years. National tonnes are not corridor tonne-kilometres or transferable freight.')
chart('Domestic production and imports must be read as one supply balance',2,'10_trade.svg',
 'Imports address the gap between demand and domestic product supply. Plant outages and lost output matter, alongside exports, stock movements and product definitions.',
 'SARS trade: complete years and litre-reported petrol/diesel codes. Kg, unknown units and excluded blends prevent treatment as a complete physical balance.')
table('Plant-specific uncertainty can change the import requirement in either direction',3,[
 ['SAPREF', 'CEF describes an import phase followed by a proposed large refinery development.', 'Import infrastructure can precede any local production recovery. Timing, financing and yields remain conditional.'],
 ['Secunda', 'Declining gas supply and potential MRG diversion could reduce liquid output.', 'MRG bridge is conditional. A quantified liquids penalty requires a gas balance and marginal conversion yield.'],
 ['Natref', 'Sasol reported an operational disruption in September 2026.', 'An outage is not evidence of permanent closure. Confirm recovery and the longer-term investment outlook.'],
 ['Mossgas / PetroSA', 'GTL has not operated since December 2020; a recommissioning proposal exists.', 'Separate stopped historical production from a funded future restart.'],
], 'CEF 10 Sep 2026 roadmap; Sasol 6 Nov 2025 MRG and 1 Sep 2026 Natref releases; PetroSA recommissioning scope. URLs and qualifications in evidence report.')
table('Power recovery can persist, but availability and replacement timing remain risks',3,[
 ['Recovery persists', 'A more available coal fleet and replacement generation reduce residual diesel dispatch.', 'Recent Eskom fuel consumption should not be extrapolated as a permanent growth source.'],
 ['Recovery reverses', 'Major breakdowns or retirements before dependable replacement create a generation gap.', 'Quantify dispatch and operating constraints before translating a gap into fuel litres.'],
 ['Load shedding', 'Grid shortages can also affect private backup generation.', 'Separate Eskom OCGT use from private generators. Ending load shedding does not imply zero Eskom diesel use.'],
], 'Standalone power complication retained as requested. EAF, retirement and commissioning assumptions require later scenario calibration.')
table('Rail recovery on the Durban corridor depends on funding and reliable service',3,[
 ['Network ambition', 'The supplied brief reports a 250 Mt target dependent on a funding plan.', 'Do not treat every additional rail tonne as road displacement. Commodity, corridor and origin matter.'],
 ['Funding constraint', 'Brief: R46.34bn approved over five years, including R1.71bn expansion.', 'Maintenance and sustaining spend dominate. A published plan is insufficient evidence of delivered capacity.'],
 ['Container corridor', 'Brief: R2.11bn in 2026/27–2028/29; private funding expected thereafter.', 'Prioritise Durban–Gauteng road/rail competition and reconcile the corridor to Network Statement v4.'],
 ['Two fuel effects', 'Rail can displace truck diesel while improved infrastructure also changes fuel-distribution economics.', 'Keep freight-demand effects separate from the route delivering fuel to Gauteng.'],
], 'User-supplied AIA Transnet Funding Brief, Sep 2026, pp1–2; cites FY2026 AFS and Network Statement v4 Annexure 17. Primary figures not independently reconciled.')
table('Origin–destination economics determine which supply route can win a customer',3,[
 ['Durban–Gauteng', 'Compare road, rail and pipeline to the same receiving point and product specification.', 'Include handling, transport, losses, inventory finance and service constraints.'],
 ['Matola / Maputo', 'Include inland haul and border costs for each reachable destination.', 'A port-level cost comparison cannot establish Gauteng competitiveness.'],
 ['Walvis Bay', 'Test distance, transit time and corridor capacity into each target market.', 'Do not assume that every inland customer is economically addressable.'],
 ['Price bearability', 'Maximum affordable logistics cost = destination netback less origin product and other delivered costs.', 'Output R/litre headroom, feasible volume and binding constraints. Route rates and access terms remain missing.'],
], 'Submodel specification adopted from the annotated review. No route winner is asserted without matched costs, access and capacity.')
table('Durban capacity provides a limited proxy, not a measured throughput share',4,[
 ['Published capacity', 'Vopak Durban: 360,246 m³. Bidvest Durban: 439,306 m³.', 'These two published totals cover different product mixes and exclude other operators.'],
 ['Inference test', 'Vopak holds 45.1% of the combined gross capacity of this two-operator set.', 'This is an asset-footprint proxy only. It is neither total Durban storage share nor petrol/diesel throughput share.'],
 ['Missing bridge', 'Eligible working tankage × realised turnover × destination allocation gives a throughput estimate.', 'Product mix and turnover can change the inferred share materially. Obtain these before reporting a central share estimate.'],
], 'Vopak / Bidvest operator inventory checked 6–7 Oct 2026. 360,246 / (360,246 + 439,306). Public capacities are gross; complete denominator unavailable.')
chart('Gauteng provides a demand denominator for testing Lesedi’s potential reach',4,'09_gauteng.svg',
 '2022 petrol + diesel sales total 6.81bn litres. Lesedi’s 140,000m³ equals 2.06% of that annual market per effective gross-capacity turn. Actual turns and Gauteng allocation remain unknown.',
 'Department provincial sales, latest complete staged year 2022; Vopak Lesedi current capacity. Cross-vintage scale test only, not current observed market share.')
table('Catchment dashboards must lead to a forecast of revenue and cash flow',4,[
 ['Durban dashboard', 'Demand served, import flows, eligible competitor capacity, inferred throughput and corridor economics.', 'Separate port handling from deliveries to final customers. Avoid counting Durban–Lesedi transfers twice in a group share.'],
 ['Gauteng dashboard', 'Petrol/diesel demand, route access, Lesedi capacity, implied turns and unique customer deliveries.', 'Refresh the 2022 denominator and reconcile the geographic allocation before estimating current share.'],
 ['Financial bridge', 'Contracted m³ × storage tariff, plus billable handling × handling rate, plus eligible services.', 'Deduct opex to EBITDA, then tax, working capital and capex to cash flow. Avoid overlapping tariff revenue.'],
 ['Investment decision', 'Compare phased capex with incremental cash flow, NPV, IRR and break-even utilisation.', 'Commercial rates, contracts, cost, capex and hurdle rate are missing. The forecast structure is defined; an investment return is not yet estimated.'],
], 'User comments adopted: separate deep dives and investment-board financial resolution. Scenarios deferred; finance and origin–destination modules are specified, not implemented.')
table('The next decision is which evidence can support Vopak’s accessible volume',4,[
 ['Supported now', 'Different petrol/diesel histories; lower Eskom fuel use; documented plant uncertainty; provisional Gauteng scope.', 'Continue the story with explicit product, geographic and period boundaries.'],
 ['Tested now', 'Durban two-operator capacity proxy and Lesedi capacity-to-market scale.', 'Use these as transparent inference tests, not measured terminal market shares.'],
 ['Next evidence', 'Corridor primary tables and tariffs; eligible tankage/turnover; refreshed Gauteng sales; sector and OEM evidence.', 'Owner: Nigel / analyst validation. Resolve before adopting a central market-share or routing result.'],
 ['Next decision layer', 'Commercial inputs and approved forecast assumptions.', 'Owner: Nigel / commercial team. Resolve before financial returns or an investment recommendation; scenarios follow separately.'],
], 'Evidence review draft, 7 Oct 2026. Not independently peer-reviewed or approved for investment reliance. Open items remain in the audit tracker.')
save('sa_market_story_2026_10_07.json', dict(style_reference=plan['style_reference'], cover_title='South Africa\nliquid fuels\nmarket story', cover_subtitle='Evidence, implications and Vopak’s opportunity', cover_status='Evidence review draft; scenarios deferred', slides=slides))

comments = json.loads((ROOT/'output/sa_review_feedback_2026_10_07/Vopak_SA_Review_Signed_Off_2026_10_07_v2_comments.json').read_text(encoding='utf-8'))
actions = {1:'Logo blue #0A2373 confirmed on cover and applied consistently to theme, headings and active navigation.',2:'Page number set to 11pt and logo widened to 75pt, with footer spacing rebalanced.',3:'Economic weakness and structural change defined; agriculture/manufacturing attribution qualified; geopolitical price shocks distinguished from sustained EV ownership economics and adoption.',4:'Situation/Complication/Resolution navigation shapes replace prior navigation; redundant section subtitle removed.',5:'SCR shapes applied.',6:'Durban–Gauteng prioritised; Network Statement v4 and funding brief specified; mining/agriculture/aviation separated; SCR applied.',7:'Standalone power complication retained; SCR applied.',8:'Secunda driver corrected and SAPREF/Natref scope confirmed; SCR applied.',9:'Origin–destination price bearability submodel specified; Durban/Matola/Walvis comparisons retained; SCR applied.',10:'Catchment dashboard specifications and financial forecast bridge added. Commercial input gap explicit; SCR applied.'}
log=ROOT/'workstreams/WS0_governance/workplan/sa_review_comment_disposition_2026_10_07.csv'
with log.open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['page','comment','disposition','status','owner','resolution_trigger'])
    for page in comments:
        for a in page['annotations']:
            w.writerow([page['page'],a['/Contents'],actions[page['page']],'Applied to copy/design; analytical modules remain scoped where noted','Nigel / analyst','Review revised pack; validate inputs before quantitative adoption'])
print(f'Prepared revised plan ({len(s)+1} slides), market story ({len(slides)+1} slides) and comment dispositions.')
