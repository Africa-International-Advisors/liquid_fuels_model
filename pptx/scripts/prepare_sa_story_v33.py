"""Format registered analytical outputs into the approved 19-page core story."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
m=json.loads((ROOT/'output/delivered/sa_analytics_2026_10_11_v02/analytics.json').read_text())
market=json.loads((ROOT/'output/delivered/market_review_2026_10_10/market_review.json').read_text())
def value(v):return v['value'] if isinstance(v,dict) else v
def rows(name):return [[value(v) for v in r] for r in m['sheets'][name]['rows']]
def lookup(name):return {r[0]:r for r in rows(name)}
seg=lookup('Segments');bal=lookup('Balance');bridge=lookup('Driver bridge');sc=lookup('Scenarios');ev={r[0]:r[1] for r in rows('Evidence')};ass={r[0]:r[1] for r in rows('Assumptions')}
f=lambda x:f'{x:.2f}'
slides=[]
def table(page,title,headers,data,takeaway,source,widths=None,font=18):
    slides.append(dict(page=page,title=title,kind='table',headers=headers,rows=data,takeaway=takeaway,source=source,widths=widths,font=font))
def chart(page,title,categories,series,side,takeaway,source,kind='line',direction='column'):
    slides.append(dict(page=page,title=title,kind='chart',categories=categories,series=series,side=side,takeaway=takeaway,source=source,chartType=kind,direction=direction))
source='2025 analytical workbook v02: registered demand assumptions and user-directed 5.8bn L domestic production case. Estimates are not reported actuals.'
table(2,'Our 2025 baseline is 21.0bn litres, with road use accounting for most demand',
      ['Demand segment','2025 estimate\nbn litres','Change since 2023\nbn litres'],
      [[r[0],f(r[3]),f(r[4])] for r in rows('Segments')[:9]],
      'Petrol: 8.86bn L. Diesel: 12.13bn L. Total demand falls from 21.94bn L in 2023 to an estimated 20.99bn L in 2025.',
      'Department sales through 2023; energy balances and Stats SA activity; Eskom/IPP evidence. All 2025 segment allocations are estimates; other diesel retains an explicit residual.',[610,235,273],17)
table(3,'Demand stays broadly flat in our base case; supply and routes determine where imports enter',
      ['Driver and deep dive','Evidence / planning assumption','Base-case implication by 2030'],[
      ['Power | pp8–9','Eskom fuel fell from 1.13bn L in FY2024 to 0.68bn in FY2025',f'Power demand reduction: {f(-bridge["Base"][4])}bn L; includes assumed private backup'],
      ['Freight and vehicles | pp7, 10–11','7.5% road-freight shift to rail; 1% annual road-fuel efficiency gain',f'Rail saves {f(-bridge["Base"][3])}bn L; road efficiency saves {f(-bridge["Base"][2])}bn L'],
      ['Domestic production | pp12–14','5.8bn L directed planning baseline; no restart in base case','Demand-implied gross imports remain about 16.6bn L in 2030'],
      ['Mozambique routes | pp15–16','Existing Matola infrastructure and an assumed 0.20bn L additional SA flow','Imports change gateway; national fuel demand stays unchanged']],
      'Activity adds 1.54bn L by 2030, broadly offsetting power, efficiency and rail reductions. Customer access determines Vopak capture.',source,[255,415,448],18)
history=rows('Demand history')[:13]
chart(4,'Petrol has declined since 2013, while diesel has sustained the market',
      [str(r[0]) for r in history],[{'name':'Petrol','values':[r[1] for r in history]},{'name':'Diesel','values':[r[2] for r in history]}],
      ['2025 estimate','Petrol 8.86bn litres','Diesel 12.13bn litres','2024–25 are estimates; 2013–23 use one consistent Department series.'],
      'Petrol remains below its earlier level; diesel demand responds more directly to freight, industry and power.',
      'Department annual sales, 2013–2023. Estimated 2024–2025: analytical workbook v02. Earlier deck FIASA comparison figures are not spliced into this series.')
chart(5,'Road use dominates the baseline, with meaningful diesel demand outside transport',
      ['Petrol road','Freight diesel','Other road diesel','Mining','Agriculture','Power','Manufacturing','Other petrol','Other diesel'],
      [{'name':'2025 estimated bn litres','values':[seg[k][3] for k in ['Petrol road use','Road freight diesel','Other road diesel','Mining','Agriculture','Utility and private power','Manufacturing','Other petrol','Other diesel / unallocated']]}],
      ['Demand allocation','Road freight: 4.82bn L','Mining: 1.41bn L','Agriculture: 1.13bn L','Other diesel: 1.91bn L remains unallocated to a specific end use.'],
      'Sector-attributed vehicle fuel stays in its sector; the road split is an explicit allocation assumption.',
      'Analytical workbook v02, Segments. 2021 energy-balance road volume; 75% of road diesel allocated to freight. Historical sector intensities at current activity.',kind='bar',direction='bar')
chart(6,'Agricultural demand rebounds in 2025 while mining and manufacturing remain broadly flat',
      ['2023','2024','2025'],[{'name':k,'values':seg[k][1:4]} for k in ['Mining','Agriculture','Manufacturing']],
      ['Estimated diesel use','Mining: 1.40 → 1.41bn L','Agriculture: 1.06 → 1.13bn L','Manufacturing: about 0.17bn L','Manufacturing covers the energy-balance industry residual, not a complete industrial census.'],
      'Sector activity produces different demand paths; applying one GDP growth rate would hide these differences.',
      'Stats SA mining/manufacturing indices and agriculture real GVA; mean 2018–2021 fuel intensity. Sector diesel values after 2021 are estimates.')
table(7,'Efficiency offsets activity growth in the petrol baseline',
      ['Demand component','Assumption / result','How it enters the estimate'],[
      ['Petrol activity','+0.5% per year in 2024–2025','More vehicle use supports consumption'],
      ['Petrol fuel intensity','−1.5% per year in 2024–2025','A combined efficiency / fleet-mix assumption reduces fuel per unit of activity'],
      ['Petrol demand','9.04bn L in 2023 → 8.86bn L in 2025','Compounding activity and intensity yields a modest decline'],
      ['2030 road outlook','Base: 1% annual efficiency improvement','Applied after activity growth; rail displacement is then applied to freight only']],
      'The assumptions are explicit and editable; EV uptake is not counted again as a separate reduction.',
      'Department 2023 sales; analytical workbook v02, Assumptions and Demand history. Activity and efficiency settings are authored planning assumptions.',[260,360,498],19)
chart(8,'Eskom fuel use fell by about 40% in FY2025 as supply performance improved',
      ['FY2023','FY2024','FY2025'],[{'name':'Eskom diesel + kerosene, bn litres','values':[ev[f'eskom_{y}'] for y in (2023,2024,2025)]}],
      ['Observed utility trend','FY2024: 1.130bn L','FY2025: 0.679bn L','The utility series includes kerosene. Fiscal years end in March.'],
      'The demand baseline replaces annual power consumption explicitly, so the decline is not hidden in a generic growth rate.',
      'Eskom Integrated Report 2025 p141; staged source series. 679.1m L diesel + kerosene supersedes the earlier slide’s 677.9m figure for this scope.',kind='bar')
table(9,'Further power recovery removes 0.54bn litres in the 2030 base case',
      ['Power measure','Volume / assumption','Interpretation'],[
      ['2025 utility + private baseline','1.08bn litres','Eskom FY proxy, IPP generation conversion and private backup'],
      ['Private backup within 2025 baseline','0.20bn litres assumed','Separate from reported Eskom fuel; not a measured national census'],
      ['Base case to 2030','50% retained; 0.54bn L reduction','Recovery persists across utility and backup requirements'],
      ['Sensitivity cases','0.00–0.70bn L reduction','High-import case retains power use; low-import case retains 35%']],
      'Power demand can fall without an equivalent decline in transport or industrial demand.',
      'Analytical workbook v02, Segments / Driver bridge. Private backup 2023/24/25: 0.8/0.6/0.2bn L. IPP conversion: 0.31 L/kWh. FY-to-calendar and fuel-mix assumptions apply.',[320,320,478],19)
chart(10,'Road still carries most reported freight despite the recent recovery in rail volumes',
      ['2024','2025'],[{'name':'Road, million tonnes','values':[ev[f'freight_road_{y}'] for y in (2024,2025)]},{'name':'Rail, million tonnes','values':[ev[f'freight_rail_{y}'] for y in (2024,2025)]}],
      ['Reported freight','Road: 979.8 → 976.5m tonnes','Rail: 160.7 → 168.3m tonnes','Tonnes measure payload, not tonne-kilometres or directly displaced diesel.'],
      'Rail recovery changes fuel demand through eligible freight, distance, truck efficiency and the rail traction mix.',
      'Stats SA P7162 December 2025 p7; all reported freight. Analytical workbook v02, Evidence.',kind='bar')
table(11,'A 7.5% shift of road-freight activity to rail saves 0.33bn litres in the base case',
      ['2030 case','Road-freight shift','Net diesel reduction'],[
      ['Low imports','15.0%',f'{f(-bridge["Low imports"][3])}bn litres'],
      ['Base','7.5%',f'{f(-bridge["Base"][3])}bn litres'],
      ['High imports','2.5%',f'{f(-bridge["High imports"][3])}bn litres'],
      ['Calculation order','Activity → efficiency → modal shift','10% diesel rebound allowance for rail']],
      'These shifts apply to road-freight activity, not the entire diesel market; sector demand and power remain separate.',
      'Analytical workbook v02, Driver bridge and scenario assumptions. Shift interpreted as freight tonne-km share. Distances and eligibility remain assumed; cases also vary growth and efficiency.',[350,310,458],20)
table(12,'The 5.8bn-litre production assumption leaves a gross import requirement of about 16.7bn litres',
      ['2025 national balance','bn litres','Basis'],[
      ['Demand',f(bal['2025 demand'][3]),'Estimated from the 2023 sales baseline'],
      ['Domestic production','5.80','User-directed national planning assumption'],
      ['Gross imports',f(bal['Gross customs imports'][3]),'SARS recorded customs litres'],
      ['Exports',f(bal['Customs exports'][3]),'SARS recorded customs litres'],
      ['Production + net imports',f(bal['Supply plus net imports'][3]),'Availability before stock / statistical differences'],
      ['Availability less demand',f(bal['Unexplained availability less demand'][3]),'Aggregate near-balance; product differences remain']],
      '5.8bn litres sets the planning case. Aggregate closure does not validate domestic output or its petrol/diesel split.',
      'Analytical workbook v02, Balance and Supply assumption. User direction 11 October 2026. Original plant-based estimate 10.23bn L retained in appendix.',[475,170,473],18)
table(13,'Refinery recovery is the largest downside risk to the import requirement',
      ['Supply lever','Base case','Low-import sensitivity'],[
      ['Operating domestic supply','5.8bn L through 2030','15% increase in the national planning volume'],
      ['SAPREF','No refining restart through 2030','Assumed 2029 start; 65% utilisation after a two-year ramp'],
      ['PetroSA / Mossel Bay','No refining restart through 2030','Assumed 2029 start; 50% utilisation after a two-year ramp'],
      ['Combined restart contribution','Zero',f'{f(bridge["Low imports"][6])}bn L petrol/diesel in 2030']],
      'Restart dates and ramp-up settings are scenario assumptions. Import-terminal operations can compete before refining resumes.',
      'Registered scenario assumptions; DR08 refinery evidence. Capacity inputs: SAPREF 180kb/d, PetroSA 45kb/d; 70% petrol/diesel yield in restart sensitivities. Dates are not project commitments.',[310,310,498],18)
chart(14,'Base-case imports remain near 16.6bn litres; refinery recovery creates a much lower outcome',
      [str(y) for y in range(2025,2031)],[{'name':case,'values':[sc[f'{case} {y}'][3] for y in range(2025,2031)]} for case in ('Low imports','Base','High imports')],
      ['2030 gross import need',*[case+': '+f(sc[case+' 2030'][3])+'bn L' for case in ('Low imports','Base','High imports')],'Cases are sensitivities, not assigned probabilities.'],
      'The base case balances activity growth against efficiency, rail and power reductions; supply assumptions drive the widest spread.',
      'Analytical workbook v02, Scenarios. Demand-implied gross imports = demand − domestic supply + 2025 exports. Zero stock change; 5.8bn L directed opening supply.')
table(15,'Matola provides an existing alternative gateway; new gas projects have a different role',
      ['Node','Evidence','Implication for South African fuel routes'],[
      ['Galp/IPG Matola','60,000m³ petrol/diesel storage; opened 2020','Existing import and distribution infrastructure'],
      ['Petromoc Língamo / Matola','390,000m³ across liquid fuels','Broader storage base; product allocation and overlap need confirmation'],
      ['Beira, Nacala and Pemba','Existing central / northern logistics nodes','Regional supply; no additional SA flow assigned in the base case'],
      ['Temane PSA','Light oil, gas and LPG; production began December 2025','No direct finished petrol/diesel output credited'],
      ['Komatipoort recorded imports','0.303bn L in 2022 → 0.086bn L in 2025','Current cross-border flow is far smaller than gross storage suggests']],
      'Storage capacity, berth capacity and delivered South African volumes measure different things and are not added together.',
      'Galp Matola announcement (3 Dec 2020); Petromoc logistics; Sasol Mozambique operations; SARS customs. URLs retained in notes / workbook.',[280,380,458],17)
table(16,'Matola needs a landed-price or service advantage to offset border and logistics costs',
      ['Route sensitivity','Result','Assumptions behind the result'],[
      ['Durban → same inland destination','R0.95 per litre logistics','600km one way; round trip; R25/truck-km; 40,000L payload'],
      ['Matola → same inland destination','R1.14 per litre logistics','550km one way; terminal and border costs; one-day delay'],
      ['Matola premium','R0.19 per litre','Required landed-product discount under these illustrative costs'],
      ['Border-delay sensitivity','R0.09–R0.40 per litre premium','Zero to three delay days'],
      ['Base incremental Mozambique flow','0.20bn L by 2030','About 15 additional loaded trucks/day over 330 days']],
      'Mozambique diversion changes the gateway serving demand. It does not reduce South Africa’s national import requirement.',
      'Analytical workbook v02, Mozambique. Distances, tariffs, border charges, financing and allocation are authored sensitivities, not carrier quotes or confirmed access.',[350,300,468],18)
table(17,'Vopak’s capture depends on the accessible share of Durban imports',
      ['Market / flow measure','Annual volume','Meaning for Vopak'],[
      ['National demand, 2025 estimate','20.99bn litres','Total consumption context'],
      ['National gross imports, 2025','16.70bn litres','All recorded import gateways'],
      ['Durban customs imports, 2025',f(market['durban_customs']['total'])+'bn litres','Gateway proxy before customer and route allocation'],
      ['Illustrative Durban capture','2.63bn litres','20% of Durban gateway volume; no contracted share inferred'],
      ['Illustrative onward Lesedi flow','1.32bn litres','50% of captured Durban flow; counted within the same fuel volume']],
      'The illustrative unique flow is 2.63bn litres. Adding Lesedi would double-count fuel handled at both sites.',
      'Registered market_review.yaml and market_review.json, 10 October. Capture is total conditional flow, not incremental sales; domestic and other-terminal Lesedi receipts are outside this screen.',[400,245,473],18)
table(18,'The illustrative capture case fits the tank-turn screen, making usable capacity the next test',
      ['Site','Illustrative flow\nbn L/year','Handling screen\nbn L/year','Operating basis'],[
      ['Durban','2.63','3.50','146,000m³ estimated working subset; two turns/month'],
      ['Lesedi','1.32','2.98','124,000m³ working capacity, partly estimated; two turns/month'],
      ['Investment test','Incremental contracts','Actual constraint','Receipt, product segregation, dispatch, pipeline access and peak demand']],
      'Working-tank arithmetic screens feasibility. Engineering limits and current customer flows determine actual headroom.',
      'Registered terminal_site_assumptions.csv and market_review.json. Durban working subset is not the full terminal; access, peaks and current throughput remain open.',[210,230,230,448],19)
table(19,'The market supports an import platform; customer capture and capacity constraints govern investment',
      ['Conclusion','Evidence from this story','Decision implication'],[
      ['A substantial demand base','2025 estimated demand of 21.0bn litres','Prioritise identifiable customer segments and destinations'],
      ['Base imports remain substantial','About 16.6bn litres in 2030 under the 5.8bn supply case','Plan for ongoing imports; retain refinery sensitivities'],
      ['Gateways compete for the same fuel','Mozambique base diversion of 0.20bn L is a route assumption','Validate delivered cost, service and customer access'],
      ['Expansion follows incremental capture','Illustrative 2.63bn L unique flow fits the tank-turn screen','Secure additional volumes, prove the bottleneck, then compare improvement and expansion returns']],
      'Next decisions: review the product balance, obtain route quotes and customer commitments, and establish usable capacity at both sites.',source,[305,370,443],18)
table(21,'The national supply assumption closes the total balance but leaves the product mix unresolved',
      ['2025 measure','Petrol bn L','Diesel bn L','Total bn L'],
      [[k,*[f(v) for v in bal[k][1:4]]] for k in ['2025 demand','Domestic production','Gross customs imports','Customs exports','Supply plus net imports','Unexplained availability less demand']],
      'The 5.8bn L override uses the original estimated production mix. Offsetting product differences remain visible; no product allocation is claimed as verified.',
      'Analytical workbook v02, Supply assumption and Balance. Original plant estimate: Secunda 3.95, Natref 2.37, Astron 3.91bn L; 10.23bn total. These do not govern the directed case.',[520,199,199,200],18)
table(22,'The conclusions are traceable to sources and a small set of explicit planning assumptions',
      ['Evidence / assumption','Used on pages','Basis / next validation'],[
      ['National sales and sector activity','2, 4–7','Department sales; energy balances; Stats SA. Manish: sales coverage and segment boundaries'],
      ['Power and freight','3, 8–11','Eskom / IPP and Stats SA. Nigel: backup demand, eligible rail shift and efficiency'],
      ['Domestic supply and imports','12–14, 21','5.8bn L user-directed supply; SARS trade. Manish: product-level reconciliation'],
      ['Mozambique infrastructure and costs','15–16','Operator disclosures; authored cost sensitivities. Nigel: comparable quotes and access'],
      ['Vopak capture and handling','17–19','Registered illustrative capture and working tanks. Vopak/Nigel: contracts and operating limits']],
      'Planning assumptions remain editable in workbook v02. Source observations, estimates and sensitivities retain separate labels.',
      'Source register: REG-SA-ANALYTICS-202510 and REG-SA-STORY-CASE-2025. Exception EXC-SA-ANALYTICS-202510; review before external use, expiry 12 November 2026.',[330,150,638],17)
spec={'slides':slides,'core_pages':19,'total_pages':22,'hg_page':20,'source_case':m['status']}
(ROOT/'pptx/story/sa_story_v33_2026_10_11.json').write_text(json.dumps(spec,indent=2),encoding='utf8')
print('Prepared',len(slides),'analytical slides plus cover and original HG SCR')
