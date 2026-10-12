"""Prepare presentation-only edits from the governed 10 October result files."""
import json
from pathlib import Path
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / 'output/delivered/market_review_2026_10_10/market_review.json'
m = json.loads(RESULTS.read_text('utf8'))
inv = json.loads((ROOT / 'output/delivered/vopak_illustration_2026_10_10/results.json').read_text('utf8'))
spec = {'date': '2026-10-10', 'result_source': str(RESULTS.relative_to(ROOT)), 'decks': {}}


def deck(key, source, output):
    spec['decks'][key] = dict(source=source, output=output, edits=[], notes={}, replacements=[])
    return spec['decks'][key]


s = deck('story', 'pptx/output/delivered/supporting/archive/2026-10-11_cleanup/SA_Market_Story_2026-10-08_v27.pptx', 'SA_Market_Story_2026-10-10_v28')
z = deck('sizing', 'pptx/output/delivered/supporting/archive/2026-10-11_cleanup/09102026_Vopak_Market_Sizing_v1900.pptx', '10102026_Vopak_Market_Sizing_v2000')


def text(d, page, name, value, **options):
    d['edits'].append(dict(page=page, name=name, text=value, **options))


def cell(d, page, row, col, value, name='Table 46'):
    d['edits'].append(dict(page=page, name=name, row=row, col=col, text=value))


def note(d, page, value):
    d['notes'][str(page)] = value


def footer(d, page, value):
    text(d, page, 'Unified source footer', value)


def body(d, page, headers, rows, widths, explanation, height=300):
    d['replacements'].append(dict(page=page, headers=headers, rows=rows, widths=widths, explanation=explanation, height=height))


for d in (s, z):
    text(d, 1, 'TextBox 8', '10 October 2026')
    text(d, 1, 'TextBox 9', 'Public evidence and illustrative capture cases. Customer access, operating limits and returns remain provisional.')
text(s, 19, 'TextBox 8', '10 October 2026')
text(s, 2, 'Title 1', 'Import dependence supports the terminal opportunity, while customer access determines Vopak capture')
cell(s, 2, 2, 1, '2025 gross imports: 16.70bn L.\nNet imports: 15.15bn L.\nDurban customs: 13.16bn L (79%).')
cell(s, 2, 3, 1, 'Shared MPP pipeline: 105 / 148ML\nper week in FY2025, 70.9% used.\nVopak access remains unverified.')
cell(s, 2, 4, 0, 'Capture sensitivity\nand nine worlds')
cell(s, 2, 4, 1, 'Base capture screen: Durban 2.63bn L;\nLesedi 1.32bn L within that flow.\nAssumed shares, not measured volumes.')
cell(s, 2, 4, 2, 'Capture cases are shown on p35.\nThe nine-world investment illustration\nuses separate capture assumptions.')
footer(s, 2, 'Department sales 2023; SARS customs 2025. Transnet Pipelines 2025 p8. Capture screen: 20% gateway share, 50% routed through Lesedi, two turns/month. Conditional illustration, no customer commitment.')
text(s, 3, 'Title 1', 'Existing assets provide the starting point for capturing demand and testing expansion')
cell(s, 3, 3, 1, 'High demand / low domestic supply favours extra tanks in the illustration. Working-capacity assumptions materially affect its value.')
cell(s, 3, 4, 2, 'Validate capture, chargeable revenues and capex. The illustrated tank choice reverses in the downside tests.')
text(s, 6, 'Title 1', 'Petrol demand declined while diesel grew slowly over 2013–2023')
text(s, 7, 'Title 1', 'Power recovery reduces diesel support while freight and sector activity remain important')
cell(s, 7, 3, 2, '2025 activity-based diesel estimates:\nmining 1.406, industry residual 0.165,\nagriculture 1.131bn L. Uses can overlap.')
sector = [(1.40634678462, 'Mining activity drives the estimate. Average historical intensity and road-use overlap remain uncertain.'),
          (0.16507618, 'Industry residual excludes mining and construction. This is an estimate, not a complete industrial census.'),
          (1.13122469824, '2025 real GVA R134.8bn, 2015 prices. Weather, irrigation and transport affect fuel intensity.')]
for i, (value, explanation) in enumerate(sector):
    text(s, 8, f'Year {i} 2', '2025 est.')
    text(s, 8, f'Value {i} 2', f'{value:.2f}', position={'left':(263+value/2*274)*4/3})
    text(s, 8, f'Sector interpretation {i}', explanation)
    s['edits'].append(dict(page=8, name=f'Sector bar {i} 2', position={'width':value/2*274*4/3}))
text(s, 8, 'Interpretation', '2025 estimates apply average 2018–2021 intensity to sector activity. They require reconciliation with road use and total diesel sales.')
footer(s, 8, 'Manish master workbook, DR01 sector activity: 2025 activity × historical average intensity. Department energy balance ends in 2021. Later sector litres are estimates; attribution and road overlap remain open.')
text(s, 9, 'Title 1', 'Refinery shutdowns have increased reliance on imported petrol and diesel')
text(s, 9, 'Interpretation', '2025 imports: diesel 12.25bn L and petrol 4.45bn L, net 15.15bn L. Durban customs accounts for 13.16bn L; terminal capture remains unverified.')
note(s, 9, 'SARS customs 2025, registered fuel_trade_sars_by_office.csv. Office of clearance is a gateway proxy, not a measured Vopak terminal receipt. Do not divide 2025 imports by 2023 sales to infer current import penetration.')
text(s, 10, 'Interpretation', 'MPP use averaged 105ML/week in FY2025 against 148ML/week capacity. Compare route costs and access by destination; average spare capacity gives no Vopak entitlement.')
note(s, 10, 'Transnet Pipelines 2025 printed p8: https://www.transnet.net/getFile.ashx?id=6121. Annualised use 5.460bn L and capacity 7.696bn L using 52 weeks. All shippers; no deduction of road/rail volumes from mismatched customs and demand years.')
cell(s, 11, 1, 2, '146,000 m³ estimated working subset from the 162,000 m³ expansion. Full petrol/diesel allocation still needs confirmation.')
cell(s, 11, 2, 2, '124,000 m³ working estimate: 88,000 documented plus 36,000 estimated for newer tanks. Actual throughput remains open.')
cell(s, 11, 3, 1, 'MPP use/capacity: 105 / 148ML per week in FY2025. Shared annualised use 5.46bn L.')
footer(s, 11, 'Vopak terminal directory; NERSA Lesedi licence documents; registered terminal_site_assumptions.csv; Transnet Pipelines 2025 p8. Gross capacity, estimated working tankage and annual throughput have different meanings.')
text(s, 12, 'Title 1', 'Rail recovery, EV adoption and combustion-vehicle efficiency could reduce transport fuel demand')
text(s, 12, 'Interpretation', '2025 BEV sales were 0.18% of new sales. Manish reviewed the implemented EV/efficiency pair; hybrid savings and rail diversion still need explicit combination rules.')
text(s, 13, 'Interpretation', 'The engine still includes 3,000MW of notional plants. Reconcile power and road baselines jointly against reported Eskom fuel and estimated IPP burn before forecasting.')
note(s, 13, 'generation.yaml contains new_1 1000MW and new_2 2000MW, alongside older capacities. Current model power estimate around 3.58bn L (2024) differs from FY2024 Eskom plus estimated IPP fuel around 1.60bn L and FY2025 around 0.89bn L. Fiscal/calendar alignment and private backup remain unresolved. No engine recalibration was adopted in this presentation update.')
text(s, 14, 'Interpretation', 'SAPREF’s import-terminal phase can compete before any refinery restart. Natref availability and Secunda output also matter; these capacity cases are not product forecasts.')
cell(s, 15, 1, 1, 'FY2025 MPP 105 / 148ML per week. Match tariffs, injection rights and reliable inland dispatch by customer.')
text(s, 16, 'Imports', 'Gross imports, 2025\n16.70bn L petrol and diesel\nNet imports: 15.15bn L')
text(s, 16, 'National market', 'National sales baseline\n2023: 21.94bn litres\n2024 source unverified\n2025 sales unavailable')
text(s, 16, 'Durban opportunity', 'Durban gateway context\n2025 customs imports: 13.16bn L\nAccessible customer share remains open')
text(s, 16, 'Lesedi opportunity', 'Lesedi demand context\nGauteng 6.81bn L, inland 11.95bn L\n2022 catchments overlap the import pool')
text(s, 16, 'Share and headroom', 'Conditional capture screen, p35\nBase: Durban 2.63bn L, Lesedi 1.32bn L\nUnique flow 2.63bn L; Lesedi is a subset\nActual share and incremental volume open')
text(s, 16, 'Routes', 'Ports and inland delivery network\nDurban, Richards Bay and other gateways\nMPP FY2025: 5.46bn L annualised use\nVopak access and product allocation open')
footer(s, 16, 'Registered market_review.yaml and terminal_site_assumptions.csv. 2023 sales, 2025 customs and 2022 catchments retain separate periods. The 8.88bn L mixed-year residual is withdrawn as evidence of inland flow. Capture assumptions: p35.')
footer(s, 18, 'Public handback DR01/04/07/08 received and updated through 9 October. Client DR02/05/03/06 prepared; sending and receipt not recorded. Review workbook covers all nine requests, including separate DR09 EV adjacency.')
cell(s, 18, 1, 1, 'Received: sales, customs and energy balance to 2021. Open: stocks, product output after 2021 and comparable 2024–25 sales.')
cell(s, 18, 2, 1, 'Received: entry, tariff and FY2025 MPP evidence. Open: customer access, route quotes and modal flows.')
cell(s, 18, 3, 1, 'Received: power, fleet, refinery and EV/efficiency review. Open: joint baseline and hybrid/rail rules.')
s['row_heights']=[dict(page=18,name='Table 46',heights=[42,66,66,66,66,66,66])]
cell(s, 23, 1, 1, '2025 activity-based diesel estimate: 1.406bn L. Post-2021 fuel volumes are estimated.')
cell(s, 23, 2, 1, '2025 industry-residual diesel estimate: 0.165bn L. Sector boundary needs review.')
cell(s, 25, 3, 2, 'Implemented EV/efficiency pair reviewed. New-cohort efficiency applies to combustion vehicles. Avoid counting hybrid savings twice.')
cell(s, 26, 4, 3, 'Fuel/class splits and electric-LCV paths remain estimates. Sales shares do not establish fleet shares or hybrid fuel savings.', name='Native evidence table')
text(s, 27, 'Interpretation', 'Own-fleet fuel fell from 1,129.5 to 679.1m L. FY2025 Eskom plus estimated IPP fuel is ~0.89bn L; the model’s power/road split needs joint recalibration.')
text(s, 28, 'Interpretation', 'Apply freight diversion once to a defined road baseline. The ~3.15bn L operator-spending proxy has partial coverage and does not establish corridor tonne-km.')
cell(s, 29, 4, 2, 'Apply road-to-rail diversion once to eligible freight activity. Separately assess the route used to distribute fuel inland.')
text(s, 30, 'Interpretation', 'Gauteng sales were 6.81bn L in 2022; the six inland provinces totalled 11.95bn L. These are nested catchments, not low/high Lesedi market scenarios.')
cell(s, 31, 1, 2, 'EV/efficiency pair reviewed. Hybrid, freight/rail and baseline combination rules remain open. Proposed annual paths require agreement.')
cell(s, 31, 4, 2, 'Working-tank sensitivity uses Durban 146,000 and Lesedi 124,000 m³, both partly estimated. Validate turns, peaks and route access.')
cell(s, 32, 1, 2, 'Align FY/calendar scope. Reconcile the model’s 3.58bn L power estimate with reported/estimated fuel and other demand uses.')
cell(s, 32, 3, 2, 'Engine includes 3,000MW of notional plants. Treat these separately from the four existing stations and proposed coal-site cases.')
text(s, 33, 'Case qualification', 'The engine also contains 3,000MW of notional capacity. Reconcile it with these cases and historical power/road use before adopting a forecast.')
cell(s, 34, 1, 2, 'SAPREF plans an import-terminal phase before refining. No committed refinery restart date or product slate is established.')
cell(s, 34, 2, 2, 'Natref is separate from Secunda. FY2026 Sasol output uses co-owner capacity; do not scale by historic ownership mechanically.')
cell(s, 34, 3, 1, 'All-refined-products output: 29.1m barrels FY2024, 27.6m FY2025 and 30.6m FY2026.')
cell(s, 34, 4, 0, 'Other plant inputs')
cell(s, 34, 4, 1, 'Astron output evidence is available; its petrol/diesel 50/50 split is an assumption. PetroSA restart remains uncertain.')
cell(s, 34, 4, 2, 'Confirm product yields and actual operator output. No PetroSA addition appears in the existing capacity illustration.')
footer(s, 34, 'Manish DR08 refinery evidence, updated 9 October; Sasol FY2026 metrics; Glencore/Astron evidence; CEF SAPREF roadmap. FY output, calendar capacity and product yields differ. Capacity sensitivities remain illustrative.')
text(s, 35, 'Title 1', 'A conditional Durban import-capture screen gives a 2.63bn litre base case')
screen_rows = []
for r in m['scenarios']:
    screen_rows.append([f"{r['case']}\n{r['gateway_capture_fraction']:.0%} gateway share", f"Durban {r['durban_bn_l']:.2f}bn L\nLesedi {r['lesedi_bn_l']:.2f}bn L\nUnique flow {r['unique_bn_l']:.2f}bn L", '50% of captured Durban flow routed to Lesedi. '+('Durban tank screen caps the requested 3.95bn L at 3.50bn L.' if r['case']=='High' else 'Conditional on customer allocation and terminal/pipeline access.')])
body(s, 35, ['Illustrative case', 'Annual physical volumes', 'Assumptions and interpretation'], screen_rows, [190,265,384], '10/20/30% shares and 50% routing are authored sensitivities. Base turns fixed at two/month. Lesedi is a subset, so volumes are counted once. Domestic and other-terminal Lesedi receipts are excluded.', 270)
footer(s, 35, 'Registered market_review.yaml and terminal_site_assumptions.csv; 2025 Durban customs proxy 13.1605bn L. No forecast probabilities, measured market share or incremental revenue. Product mix, access and working tankage need validation.')
cell(s, 36, 3, 0, '2025 SARS imports / exports')
cell(s, 36, 6, 1, '2025 gross imports 16.70bn L; net 15.15bn L. Durban customs 13.16bn L.')
cell(s, 36, 6, 2, 'Current import penetration cannot be calculated using 2023 sales. Post-2021 production and stocks remain open.')
cell(s, 37, 1, 1, 'Public handback received through 9 October. Review workbook maps all nine requests and source-level limitations.')
cell(s, 37, 3, 1, 'Conditional Durban import-capture cases now quantified. Shared Lesedi transfers count once, see p35.')
cell(s, 37, 6, 2, 'EV/efficiency implementation review complete for the pair. Baseline, hybrid/rail interactions and annual paths remain open.')

# Reconcile the investment illustration with the 124,000 m3 working estimate.
a = inv['anchor']; opts=a['options']; gap=(opts[2]['npv_zar']-opts[1]['npv_zar'])/1e6
threshold = inv['reversal_captured_m3']
text(s, 4, 'Title 1', 'The revised working-capacity assumption changes the illustrated expansion value')
cell(s, 4, 1, 2, f"Assumed capture {a['captured_lesedi_m3']/1e6:.3f}bn L/year; tanks win above {threshold['tanks_vs_improvement']/1e6:.3f}bn L/year.")
cell(s, 4, 3, 2, f"Existing {opts[0]['achievable_annual_m3']/1e6:.3f}bn L/year; improvement {opts[1]['achievable_annual_m3']/1e6:.3f}bn; tanks {opts[2]['achievable_annual_m3']/1e6:.3f}bn.")
cell(s, 4, 3, 3, '124,000 m³ working estimate; 36,000 m³ estimated. Turns 1.25 / 1.50 remain assumptions.')
cell(s, 4, 4, 2, f"Improvement NPV R+{opts[1]['npv_zar']/1e6:.0f}m; combined R+{opts[2]['npv_zar']/1e6:.0f}m. Difference R{gap:.0f}m.")
footer(s, 4, 'ILLUSTRATIVE ONLY. Working tankage aligned to 124,000 m³. Difference was R8m at 126,000 m³; it is now R58m because the assumed rental allocation changes. Commercial terms and engineering remain unvalidated. Details pp39–42.')
for ri,demand in enumerate(['Low','Medium','High'],1):
    for ci,supply in enumerate(['High','Medium','Low'],1):
        w=next(w for w in inv['worlds'] if w['demand_world']==demand and w['supply_world']==supply)
        label={'Existing':'USE EXISTING ASSETS','Improve access / dispatch':'IMPROVE ACCESS / DISPATCH','Improve + add tanks':'TEST IMPROVEMENT + TANKS'}[w['preferred_option']]
        cell(s, 5, ri, ci, f"{demand[0]} / {supply[0]}"+(' | REFERENCE' if ri==ci==2 else '')+f"\n{label}\nCapture {w['captured_lesedi_m3']/1e6:.2f}bn L/year\nIncremental NPV R+{w['preferred_npv_zar']/1e6:.0f}m")
text(s, 39, 'Title 1', f'The revised illustration gives extra tanks R{gap:.0f}m more NPV than improvement alone')
for ri,o in enumerate(opts,1):
    cell(s, 39, ri, 1, f"R{o['capex_zar']/1e6:.0f}m capex\n{o['served_m3']/1e6:.3f}bn L/year served")
    cell(s, 39, ri, 2, f"NPV R{o['npv_zar']/1e6:+.1f}m\nUnserved {o['unserved_m3']/1e6:.3f}bn L/year")
cell(s, 39, 4, 1, f"Improvement beats existing above {threshold['improvement_vs_existing']/1e6:.3f}bn L/year.")
cell(s, 39, 4, 2, f"Tanks beat improvement above {threshold['tanks_vs_improvement']/1e6:.3f}bn L/year; assumed capture {a['captured_lesedi_m3']/1e6:.3f}bn.")
footer(s, 39, 'ILLUSTRATIVE, 100% site basis, pre-tax at 10% for 20 years. Working tankage reduced from 126,000 to 124,000 m³. Model allocates more incremental contracted storage to added tanks, increasing assumed rent. This is model sensitivity, not new commercial evidence.')
cell(s, 41, 2, 2, 'Separate investment illustration with imported and domestic capture. Its shares differ from the Durban-only capture screen on p35.')
cell(s, 41, 3, 1, '124,000 m³ working, 88.57% of gross; turns 1.25 existing / 1.50 improved; +40,000 gross m³.')
cell(s, 41, 3, 2, '159,429 working m³ with tanks at the same assumed fraction. Receipt/dispatch ceiling 3.5bn L/year remains illustrative.')
sens = [[r['case'],f"{r['options'][1]['npv_zar']/1e6:+.1f}",f"{r['options'][2]['npv_zar']/1e6:+.1f}",r['preferred_option']] for r in inv['sensitivity']]
text(s, 42, 'Title 1', 'Capture and commercial assumptions can reverse the illustrated expansion choice')
body(s, 42, ['Independent sensitivity', 'Improve NPV Rm', 'Tanks NPV Rm', 'Preferred package'], sens, [280,140,140,279], 'The lower working-capacity estimate increases assumed incremental rental in the model. The tank option still loses under the tested downside cases. Validate rental inclusions, customer volumes and project costs.', 295)
text(s, 43, 'Title 1', 'Estimated working tankage supports a handling sensitivity of 3.50 and 2.98bn litres at two turns')
rows=[]
for site in ['Durban','Lesedi']:
    r=m['sites'][site]
    rows.append([site, f"{r['working_m3']:,.0f} m³", *[f"{r['handling_bn_l'][c]:.2f}bn L\n{r['monthly_turns'][c]:g} turns/month" for c in ['low','base','high']]])
body(s, 43, ['Site','Working estimate','Low turns','Base turns','High turns'], rows, [125,190,170,170,184], 'Durban: estimated petrol/diesel subset, not all gross tankage. Lesedi: 88,000 m³ documented plus 36,000 estimated. Handling sensitivities are not measured throughput or guaranteed operating limits.', 240)
footer(s, 43, 'Registered terminal_site_assumptions.csv. Capture cases hold base turns at two/month; the investment illustration separately tests 1.25 / 1.50 turns with the same Lesedi starting working capacity. Product allocation, access, peaks and downtime require validation.')

# Market sizing deck: retain its structure while updating definitions and status.
text(z, 2, 'Title 1', 'National petrol and diesel sales were 21.94bn litres in 2023')
text(z, 2, 'Finding 2', 'Balance assembled through 2021\nResiduals remain, including diesel 2021\nStocks and statistical differences unresolved')
text(z, 2, 'Finding 3', '2025 trade is available\nGross imports 16.70B L; net 15.15B L\n2025 sales and product output unavailable')
text(z, 2, 'Finding 3 tag', 'SARS customs; production and stocks open')
footer(z, 2, 'Manish DR01, updated 9 Oct: energy balance through 2021; department sales through 2023; SARS customs through 2025. Supply less sales includes stock change and statistical difference. Figures retain their source periods.')
text(z, 3, 'National market', 'National consumption\nPetrol and diesel sales\n2023: 21.94B L')
text(z, 3, 'Imports', 'Gross imports, 2025\nPetrol 4.45B L\nDiesel 12.25B L')
text(z, 3, 'Imports tag', '2025 gross 16.70B L')
text(z, 3, 'Market sizing', 'Market context\n2025 Durban customs 13.16B L\nCatchments and gateway overlap')
text(z, 3, 'Market sizing tag', 'Gateway proxy; capture not observed')
text(z, 3, 'Durban opportunity', 'Durban context\nImports 13.16B L\nKZN sales 4.28B L')
text(z, 3, 'Durban opportunity tag', '2025 / 2022 context')
text(z, 3, 'Lesedi opportunity', 'Lesedi catchments\nGauteng 6.81B L\nInland 11.95B L')
text(z, 3, 'Lesedi opportunity tag', '2022 nested demand')
text(z, 3, 'Share', 'Conditional base capture\nDurban 2.63B L, Lesedi 1.32B L\nLesedi included in Durban flow')
text(z, 3, 'Share tag', 'Assumed capture; details p.8')
text(z, 3, 'Headroom', 'Incremental opportunity\nNeeds existing throughput baseline\nAccess and commitments unverified')
text(z, 3, 'Inland tag', 'FY25 use 5.46B L/yr')
footer(z, 3, 'SARS 2025; department sales 2023 and provinces 2022; Transnet Pipelines 2025. Gateway, catchment and terminal throughput are separate measures. No inference of an 8.88B L inland flow from mixed-year subtraction.')
text(z, 5, 'Use finding 1', 'Years and scopes differ\nBalance 23.2B L (2021), model 23.4B L (2024)\nSimilar totals do not validate sector allocation')
text(z, 5, 'Use finding 2', 'Power baseline needs joint review\nEngine includes 3,000MW notional plants\nRecalibrate power and road together')
text(z, 5, 'Use reported power', '0.89B L\nFY25; FY24 1.60B L')
text(z, 5, 'Use reported power tag', 'Eskom + estimated IPPs')
text(z, 5, 'Use model power tag', '2024; notional plants')
footer(z, 6, 'Manish proposed lever cases remain unapproved. Implemented EV/efficiency pair reviewed in the 9 Oct handback. Hybrid savings, road activity/rail diversion and inferred fuel/class splits still need rules and calibration.')
text(z, 6, 'Lever 3 reported', 'Eskom + estimated IPP fuel\nFY24 ~1.60B L, FY25 ~0.89B L\nPrivate backup remains unmeasured')
text(z, 7, 'Mode 1 row 2', 'Imports by customs office, 2025\nDurban 13.16 of 16.70B L (79%)\nOffice is a gateway proxy')
text(z, 7, 'Mode 2 row 2', 'Whole pipeline system, FY25\nPetroleum total 13.372B L\nRefined petrol/diesel 8.619B L')
text(z, 7, 'Mode 2 row 2 tag', 'TPL 2025 p8; different from MPP trunk')
text(z, 7, 'Mode 2 row 3', 'MPP usage / capacity, FY25\n105 / 148ML per week (70.9%)\nAnnualised 5.46 / 7.70B L')
text(z, 7, 'Mode 2 row 3 tag', 'TPL 2025 p8; shared, not Vopak rights')
text(z, 7, 'Mode 4 row 2', 'Road and rail volumes\nNo matched corridor flow series\nMixed-year residual withdrawn')
footer(z, 7, 'DR04/08 and Transnet Pipelines 2025 p8, https://www.transnet.net/getFile.ashx?id=6121. 52-week annualisation is arithmetic. MPP, system petroleum, customs and customer flows have different scopes. Average unused capacity is not shipper access.')
footer(z, 8, 'Public DR01/04/07/08 handback received through 9 Oct. Client DR02/05/03/06 prepared; sending/receipt not recorded. Review workbook maps all nine requests. No source review or business approval inferred from receipt.')
cell(z, 8, 1, 1, 'Received through 9 Oct: balance assembled to 2021. Residuals and stock changes unresolved; later product production and comparable sales still missing.', 'Outstanding requests native table')
cell(z, 8, 2, 1, 'Received: entry offices, tariffs, access evidence. FY2025 MPP updated. Open: product/customer access, quoted road/rail costs and matched corridor volumes.', 'Outstanding requests native table')
cell(z, 8, 3, 1, 'Received: power and fleet evidence; implemented EV/efficiency review complete. Open: joint baseline reconciliation and hybrid/rail combination rules.', 'Outstanding requests native table')
cell(z, 8, 4, 1, 'Received: plant status and operator output, including Secunda FY2026. Open: product yields, Natref ownership basis and stocks; Astron 50/50 split assumed.', 'Outstanding requests native table')
text(z, 9, 'Title 1', 'The base capture screen gives Durban 2.63bn litres and Lesedi 1.32bn within that flow')
body(z, 9, ['Illustrative case', 'Durban bn L', 'Lesedi bn L', 'Unique bn L'], [[r['case']+f" ({r['gateway_capture_fraction']:.0%})", *[f"{r[k]:.2f}" for k in ['durban_bn_l','lesedi_bn_l','unique_bn_l']]] for r in m['scenarios']], [285,185,185,184], 'Assumed gateway capture: 10/20/30%. Half of captured Durban flow routes to Lesedi. At two turns/month, Durban’s tank screen caps the high case at 3.50bn L. These are conditional total volumes, not measured shares or incremental sales.', 245)
footer(z, 9, '2025 Durban customs proxy 13.1605bn L. Registered market_review.yaml: authored sensitivities, no probabilities. Working estimates: Durban 146,000 m³; Lesedi 124,000 m³. Customer contestability, product allocation and pipeline access remain unverified. Other-terminal and domestic Lesedi receipts excluded.')

for d in (s,z):
    source = Presentation(ROOT / d['source'])
    for edit in d['edits']:
        matches=[sh for sh in source.slides[edit['page']-1].shapes if sh.name==edit['name']]
        if len(matches)!=1: raise ValueError((edit['page'],edit['name'],len(matches)))
        sh=matches[0]
        edit['original'] = sh.table.cell(edit['row'],edit['col']).text if 'row' in edit else (sh.text if sh.has_text_frame else None)
    for page in sorted({e['page'] for e in d['edits']} | {e['page'] for e in d['replacements']}):
        prior = d['notes'].get(str(page),'')
        d['notes'][str(page)] = prior+'\nSources and assumptions: output/delivered/market_review_2026_10_10/market_review.json; assumptions/2026/market_review.yaml; terminal_site_assumptions.csv; Manish Master_data_book.xlsx and DR01/04/07/08 handback through 9 October. Investment outputs: output/delivered/vopak_illustration_2026_10_10/results.json. Public observations, estimates and authored sensitivities retain their stated scopes. Pipeline source: https://www.transnet.net/getFile.ashx?id=6121, printed p8. No independent approval inferred.'
        original_notes=source.slides[page-1].notes_slide.notes_text_frame.text
        d['notes'][str(page)] += '\n\nPrevious revision notes retained for source history; revised slide values take precedence:\n'+original_notes

out = ROOT / 'pptx/story/sa_market_review_v28_2026_10_10.json'
out.write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf8')
print(out)
