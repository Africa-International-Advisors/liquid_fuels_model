"""Apply the collated visual, analytical and headline feedback to a new vintage."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
folder=root/'pptx/story'
story=json.loads((folder/'sa_market_story_top_down_2026_10_07.json').read_text(encoding='utf-8'))
s=story['slides']
titles=[
'Vopak’s growth opportunity lies in serving inland demand through the Durban–Lesedi corridor',
'Capturable volumes, route competitiveness and tank turnover determine the investment required',
'Nine demand–supply worlds test the investment choice against the Medium / Medium baseline',
'Petrol demand has declined while diesel has grown slowly, limiting the case for demand-led expansion',
'Power shortages and road freight have supported diesel consumption, but that support can change',
'Lower domestic production has increased imports and shifted how inland demand is supplied',
'Domestic sources and competing gateways contest the same inland customers',
'Higher turnover could let Durban and Lesedi serve more demand through existing tanks',
'Rail recovery, EV adoption and efficiency could reduce transport fuel demand',
'Power recovery could lower diesel use further, while outages and replacement delays could reverse the gains',
'Refinery recovery could reduce import needs, while further production losses could increase them',
'Changes in delivered cost and reliability could shift inland flows between competing corridors',
'Expansion requires capturable throughput beyond achievable capacity at an adequate return',
]
for slide,title in zip(s,titles):slide['title']=title
s[0]['headers']=['Investment thesis','Why it matters','What determines the choice']
s[0]['icons']=['ship','route','turns','matrix']
s[0]['rows']=[
 ['Capture inland\nsupply','Imported and domestic fuel can serve\ninland demand. Terminal access and\ncustomer capture determine volumes.','Size the accessible market by origin,\nproduct and destination, then estimate\nVopak’s share of the resulting flows.'],
 ['Use the corridor\nposition','Durban and Lesedi connect coastal\nhandling with inland distribution\ninto the Gauteng catchment.','Compare delivered costs, access and\nreliability with competing gateways\nand domestic sources.'],
 ['Increase asset\nturnover','Growth can increase throughput\nthrough existing tanks. Receipt and\ndispatch constrain achievable turns.','Use existing assets, debottleneck or\nadd storage according to working\ncapacity, turnover and returns.'],
 ['Test nine\nmarket worlds','Demand and domestic supply each\nhave L/M/H paths. Medium/Medium\nis the market baseline.','Track captured flow, required turns\nand capacity headroom in every world;\nphase investment against clear triggers.'],
]
s[0]['note']='Working thesis for the Durban–Lesedi corridor into Gauteng. Domestic and imported origins require verified access. No measured Vopak share, calibrated nine-world outputs or approved expansion returns are asserted.'
s[1]['rows'][0][3]='D1–D4 define activity, rail, EV and efficiency paths. Translate them into capturable product demand.'
s[1]['rows'][1][3]='D5 adds fleet recovery, replacement timing and diesel dispatch to the same demand paths.'
s[1]['rows'][2][3]='S1–S4 define plant output and sourcing mix. Imports are one consequence of the domestic balance.'
s[1]['rows'][3][3]='T1–T2 compare delivered economics and capture for domestic and imported fuel serving common destinations.'
s[1]['rows'][4][3]='T3–T5 compare working capacity, required/achievable turns and dispatch limits. F1 tests incremental returns.'
s[1]['rows'][4][1]='Durban and Lesedi provide connected assets whose throughput can rise through higher turnover.'
s[1]['rows'][4][2]='Working tankage, receipt/dispatch, peaks and stock requirements constrain achievable turnover.'
s[1]['note']='Lever IDs are mapped in the appendix. All nine market worlds use explicit routing, capture and operational assumptions. Tank occupancy, turnover and throughput utilisation are separate measures.'
s[2]['headers']=['Fuel demand / domestic supply','HIGH supply (S1–S4)','MEDIUM supply (S1–S4)','LOW supply (S1–S4)']
s[2]['rows'][0][0]='LOW demand\nD1–D5';s[2]['rows'][1][0]='MEDIUM demand\nD1–D5';s[2]['rows'][2][0]='HIGH demand\nD1–D5'
s[2]['rows'][0][1]='L / H\nLOWEST IMPORT PRESSURE\nDomestic routing and customer capture still determine terminal turns.'
s[2]['rows'][1][2]='M / M\nBASELINE\nReference sourcing, captured throughput, required turns and headroom.'
s[2]['rows'][2][3]='H / L\nHIGHEST IMPORT PRESSURE\nTest the captured flow against working capacity and achievable turns.'
s[2]['caption']='Every cell: sourcing mix → captured Durban / Lesedi flow → required vs achievable turns → headroom → return.'
s[2]['note']='Qualitative matrix, not numerical forecasts. T1–T5 and F1 translate each world into investment outcomes. Imports are an intermediate balance; domestic supply can also generate terminal flows where access is available.'
def visual(i,name,takeaway,note):
    for key in ['headers','rows','chart','side_title','side_text']:
        s[i].pop(key,None)
    s[i]['custom_chart']=f'output/sa_feedback_2026_10_07/{name}.png'
    s[i]['takeaway']=takeaway;s[i]['note']=note
visual(3,'demand_trend','The demand history supports a selective investment case: growth must translate into captured corridor throughput and sufficient tank turns.',
    'Department sales 2013–2023. CAGR from comparable endpoints: petrol −2.08%, diesel +0.82%. FIASA 2024 is excluded from the trend calculation; its observations remain in the evidence data.')
s[4]['rows'][0][2]='D5: availability, retirement and new generation determine dispatch. See the quantitative power exhibit and calibration requirements.'
s[4]['rows'][1][2]='D2: transferable tonne-kilometres, rail reliability and fuel intensity determine the net diesel effect.'
s[4]['rows'][2][2]='D1: sector activity drives end-use demand. Histories precede explicit L/M/H assumptions; missing data remain identified.'
visual(5,'imports_change','Additional imported litres create handling demand. Vopak benefits where it captures inland flows and can increase turnover or profitably remove a constraint.',
    'SARS litre-reported petrol/diesel codes, complete calendar years. 2020–2025 changes are historical comparisons, not plant-level causal attribution. Export histories retained in the source report; unit/blend exclusions remain.')
visual(6,'corridor_map','Compare the same product at the same Gauteng destination. Price headroom only becomes capturable throughput where capacity, rights and reliable access exist.',
    'Existing corridor JSON and Natural Earth boundaries. Approximate authored road/pipeline candidates, not validated operating fuel routes. Domestic-origin and rail links require confirmation; no route tariff or customer right inferred.')
visual(7,'turnover','Required working-capacity turns must be compared with achievable turns at each terminal. Gross handling equivalents do not establish spare capacity or actual market share.',
    'Registered REG-TERMINAL-HANDLING-TURNS: 1/2/3 turns per month, authored operational sensitivity, not the demand–supply worlds or measured limits. Gross Durban mixed-product tankage; no assumed eligible fraction. Do not sum inter-terminal transfers as unique demand.')
visual(8,'transport_timeseries','The time series establish the starting points. Rail, adoption and efficiency levers must be calibrated into the same three demand paths before the matrix is quantified.',
    'Stats SA freight payload; staged naamsa BEV/PHEV annual sales 2019–2025; existing engine petrol-ICE efficiency diagnostics. Dashed efficiency paths are assumptions, not historical OEM evidence. Medium and causal fuel impacts remain uncalibrated.')
visual(9,'power_timeseries','Eskom recovery has lowered diesel dispatch. Wind, solar and gas timing must be tested against demand, fleet retirements and dependable output before forecasting residual diesel.',
    'Eskom FY ending March. Fuel/EAF: 2025 report; GWh: staged 2024–2026 reports. Own Eskom and IPP generation separated. Private backup and load-shedding histories are missing; no assumed annual generation gap is assigned entirely to diesel.')
visual(10,'supply_stack','The existing stacked chart explains the capacity footprint. Plant availability, utilisation and product yields are still required to turn L/M/H supply assumptions into fuel-output paths.',
    'FIASA 2025 p49, staged refinery_capacity_reported.csv. Reported nameplate capacity, not actual production; source dashes excluded from totals. Historical stack reused; no invented Medium or L/H production forecasts. SAPREF/Natref/Secunda/PetroSA remain explicit levers.')
s[11]['rows'][0][0]='Durban–Lesedi'
s[11]['rows'][0][2]='T1–T2: compare access, cost and reliability to the same destination; quantify captured throughput and the resulting tank turns.'
s[11]['rows'][3][1]='Bearable logistics charge = destination selling price less origin product cost, other costs and required margin.'
s[11]['rows'][3][2]='Headroom = bearable charge less actual logistics cost. Capacity and service constrain the share captured through Durban–Lesedi.'
s[12]['headers']=['Investment test','Required measure','Decision consequence']
s[12]['rows']=[
 ['Captured throughput','Domestic + imported unique deliveries by product, customer and terminal.','Establish accessible flows and avoid double-counting Durban–Lesedi transfers.'],
 ['Required turnover','Annual captured m³ / eligible working m³ / 12 = required monthly turns.','Compare with achievable turns, seasonality, stock policy and receipt/dispatch limits.'],
 ['Capacity headroom','Achievable annual handling less required throughput; tank occupancy assessed separately.','Use existing capacity where available, then test targeted debottlenecking or additional storage.'],
 ['Financial return','Storage and handling revenue, operating cost, capex and working capital.','Test incremental cash flow, break-even utilisation, NPV and IRR before committing to expansion.'],
]
s[12]['note']='Public capacity ratios and Gauteng market size are screening evidence only. Working capacity, realised dispatch, routing, tariffs, contracts and capex remain open. No investment return or throughput market share is fabricated.'
# Every appendix headline has a clear role or finding rather than a topic label.
appendix_titles=[
'The supporting evidence calibrates demand, supply and the terminal investment tests',
'Fuel demand has diverged from GDP, so sector activity and fuel intensity need separate treatment',
'Fixed investment has weakened while FDI fluctuates, limiting a simple growth-led fuel argument',
'Mining, agriculture and aviation expose fuel demand to different activity drivers',
'Higher fuel prices strengthen EV running-cost incentives, but ownership economics determine uptake',
'New-vehicle efficiency gains affect fuel demand gradually as older vehicles leave the fleet',
'Eskom’s own OCGT fuel use fell 40% in FY2025 as availability improved',
'Road carries most reported freight tonnage, making transferable haul distance a key diesel lever',
'Rail funding and reliable service determine how much road freight can return to rail',
'Gauteng demand establishes market scale, while Lesedi capture and turnover determine throughput',
]
for slide,title in zip(s[13:],appendix_titles):slide['title']=title
s[13]['rows']=[['Demand','Activity, freight, EVs, efficiency and power','D1–D5 create the three demand paths.'],['Supply','Plant output, gas availability and restart timing','S1–S4 create the three domestic-supply paths.'],['Capture and operations','Routes, customer share, working tankage and turnover','T1–T5 translate each world into terminal flows and constraints.'],['Returns','Rates, costs, capex and funding','F1 translates each investment option into cash flow and returns.']]
s[13]['note']='The main story runs from the opening thesis to the investment tests. The added lever register and power/supply calibration pages record what remains to be populated.'
s.extend([
 dict(title='Every market world passes through explicit demand, supply, capture and operating levers',section=0,headers=['Lever IDs','Inputs to calibrate','Output / remaining evidence'],rows=[
 ['D1–D5 demand','D1 sector growth; D2 rail; D3 EV adoption; D4 efficiency; D5 power.','Historical volumes and time series feed L/M/H demand. OEM, corridor tonne-km and backup evidence remain open.'],
 ['S1–S4 supply','S1 SAPREF; S2 Secunda gas/MRG; S3 Natref; S4 PetroSA.','Dates, utilisation, availability and yields produce L/M/H domestic output. Medium and plant marginal effects require calibration.'],
 ['T1–T2 capture','T1 delivered route economics/access; T2 customer/product/destination capture.','Allocate domestic and imported fuel to unique terminal deliveries. Tariffs, rights and commercial allocation remain open.'],
 ['T3–T5 operations','T3 eligible working tankage; T4 turnover; T5 receipt/dispatch, peaks and stock policy.','Compare required with achievable turns, occupancy and headroom. Existing 1/2/3-turn sensitivity is illustrative only.'],
 ['F1 finance','Storage/handling terms, costs, capex, tax, working capital and hurdle rate.','Translate constrained throughput into cash flow, NPV, IRR and investment triggers. Commercial inputs remain open.']],note='Medium is the reference market world; operational sensitivities are separate. Owner: Nigel / analyst and commercial teams. Resolve each missing input before numeric adoption or investment reliance.'),
 dict(title='Generation timing must close the power balance before residual diesel can be forecast',section=0,headers=['Time series','Assumption / lever','Evidence status and next use'],rows=[
 ['Recovery history','EAF, unserved energy / load-shedding hours, OCGT GWh and litres.','EAF, Eskom fuel and Eskom/IPP GWh staged. Comparable load-shedding and private backup series still needed.'],
 ['Generation supply by year','Existing fleet and retirement profile; wind, solar and gas commissioning; availability and utilisation.','Obtain dated Eskom / approved planning schedules. Report annual GWh alongside dependable capacity and dispatch constraints.'],
 ['Residual dispatch','Electricity demand, hourly/seasonal shape, storage, imports, reserve needs and fuel constraints.','An annual GWh shortfall alone cannot determine diesel use. Calibrate feasible peaking dispatch, then apply consumption rates.'],
 ['L/M/H demand contribution','Sustained recovery, reference and setback assumptions across the same planning horizon.','Output generation and diesel time series with solid actuals / dashed assumptions. No uncalibrated future values are drawn.']],note='Requested generation-balance exhibit remains quantitatively incomplete. Owner: Nigel / power analyst; trigger: before D5 adoption. Do not convert installed renewable MW directly into dependable diesel displacement.'),
 dict(title='Plant-level output and yields must turn the capacity stack into three supply paths',section=0,headers=['Plant lever','Required time-series inputs','Scenario treatment'],rows=[
 ['S1 SAPREF','Restart/FID dates, ramp-up, product yields and operating availability.','Distinguish import operations, announced refinery ambition and commissioned output.'],
 ['S2 Secunda','Actual liquid output, gas decline, MRG allocation and marginal liquids yield.','Quantify output lost or retained; gas diversion is not an end-user demand reduction.'],
 ['S3 Natref','Plant output and ownership basis, outages, utilisation and product yields.','Reconcile reported share with whole-site output before aggregation.'],
 ['S4 PetroSA','Restart scope, timing, feedstock, utilisation and liquid yields.','Separate stopped GTL history from a funded restart assumption.']],note='Three aligned L/M/H production panels require these inputs. Existing stacked history is nameplate capacity. Owner: Nigel / supply analyst; resolve before adopting nine-world domestic supply outputs.'),
])
story['cover_subtitle']='Inland supply, corridor capture and tank turnover'
story['cover_status']='Feedback applied; quantitative calibration gaps explicit'
original=json.loads((folder/'sa_market_story_top_down_2026_10_07.json').read_text(encoding='utf-8'))
proxy=original['slides'][12]
proxy['section']=0
proxy['title']='Public capacity ratios establish scale but cannot substitute for realised terminal throughput'
s.append(proxy)
story['appendix_pages']='15–28'
story['feedback_status']='Headlines, corridor/turnover logic, visuals and available historical evidence implemented; nine-world numerical calibration remains open.'
(folder/'sa_market_story_feedback_2026_10_07.json').write_text(json.dumps(story,indent=2,ensure_ascii=False),encoding='utf-8')
print(f'Prepared {len(s)+1} pages with feedback and explicit calibration requirements.')
