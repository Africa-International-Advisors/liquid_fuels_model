"""Reorder approved narrative copy; preserve the previous story source."""
import copy
import json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
folder=root/'pptx/story'
base=json.loads((folder/'sa_market_story_2026_10_07.json').read_text(encoding='utf-8'))
old=base['slides']
slides=[]
def table(title, section, rows, note, headers=('What the evidence shows','Why it matters','Consequence for Vopak')):
    slides.append(dict(title=title,section=section,sub='',headers=headers,rows=rows,note=note))

s=copy.deepcopy(old[1])
s['title']='Demand growth alone provides a weak foundation for Vopak’s investment case'
s['takeaway']='Petrol fell 19% and diesel rose 9% over 2013–2023. Vopak’s opportunity therefore needs to be explained through product mix, import requirements and customer routes, as well as demand growth.'
s['note']+=' Economic context and sector mechanisms: appendix pp14–16.'
slides.append(s)

table('Power shortages and road freight have supported parts of diesel demand',2,[
 ['Power generation','Eskom’s own OCGT fuel use rose to 1,129.5m litres in FY2024, then fell to 679.1m in FY2025 as EAF improved.','The historical diesel market includes a material power-system component whose scale can change.'],
 ['Road freight','The national payload series shows road carrying substantially more tonnage than rail.','Diesel use depends on how freight moves as well as how much the economy produces.'],
 ['Demand interpretation','Mining and agriculture add sector-specific diesel exposure; aviation has a separate jet-fuel market.','A national GDP forecast alone cannot explain the product and activity mix that terminals serve.'],
], 'Eskom 2025 integrated report (own-fleet diesel + kerosene); Stats SA freight payload. No causal diesel attribution from tonnes alone. Details: appendix pp16, 19–20.', ('Demand support','Historical evidence','What this establishes'))

s=copy.deepcopy(old[9])
s['title']='Reduced domestic production has increased the importance of imported supply'
s['side_title']='Domestic supply context'
s['side_text']='Mossgas GTL has not operated since December 2020.\n\nSAPREF’s current roadmap starts with finished-product imports.\n\nSecunda and Natref output remains material to the domestic balance.'
s['takeaway']='The import opportunity can expand even with limited consumption growth. The trade trend and plant evidence support this mechanism; a reconciled product balance is still needed to quantify each plant’s contribution.'
s['note']='SARS litre-reported petrol/diesel trade; CEF 10 Sep 2026 roadmap; PetroSA recommissioning scope; Sasol reporting. Excluded units/blends and stock changes prevent a complete balance.'
slides.append(s)

table('The import opportunity is distributed across competing routes into inland markets',2,[
 ['Durban–Gauteng','Vopak’s coastal and inland terminals are linked through the Transnet multi-product pipeline. Durban also has road and rail access.','The relevant market extends beyond the port into inland customer demand.'],
 ['Matola / Maputo','An alternative gateway in the review’s corridor comparison. Reach depends on destination and border logistics.','Compare the same product delivered to the same customer location.'],
 ['Walvis Bay','A further gateway to test for reachable inland destinations. Distance and transit time constrain the comparison.','National imports cannot all be treated as volumes accessible through Durban.'],
], 'Vopak terminal pages and existing corridor evidence. Alternative gateway coverage is a scope for comparison, not a finding that each route is competitive into Gauteng.', ('Route','Position in the supply chain','Market implication'))

table('Vopak has assets at both ends of the Durban–Gauteng supply chain',2,[
 ['Durban','360,246 m³ published gross capacity; vessel, pipeline, road and rail access. Petroleum products and other liquids.','The coastal asset can serve imported-product handling and onward distribution; eligible fuel tankage needs to be isolated.'],
 ['Lesedi','140,000 m³ published capacity for clean petroleum products; connected to Durban via the Transnet pipeline.','The inland asset provides a distribution position in the provisional Gauteng catchment.'],
 ['Commercial question','Assets establish a physical position. Customer allocation, working capacity and realised turnover determine volumes.','The investment question is how much demand these assets can capture and whether existing capacity can serve it.'],
], 'Vopak operator inventory checked 6–7 Oct 2026; Gauteng catchment adopted provisionally by user. Gross capacity is not customer throughput or effective working capacity.', ('Asset','Established position','Implication'))

table('Rail recovery, EVs and efficiency could weaken transport fuel demand',3,[
 ['Road to rail','A funded and reliable rail service can transfer suitable freight from trucks.','Displaced road tonne-kilometres reduce diesel use, after rail traction and last-mile fuel. The 250 Mt ambition is not a direct diesel forecast.'],
 ['EV adoption','Sustained ownership-cost advantages and charging access can influence new-vehicle purchases.','Fuel-price volatility alone does not establish adoption. Replacement cycles govern the effect on the whole fleet.'],
 ['Vehicle efficiency','More efficient incoming vehicles lower combustion-fleet fuel intensity over time.','Efficiency can offset part of fleet and mileage growth. Apply it only to combustion activity that remains after EV switching.'],
], 'Mechanisms drawn from the reviewed scope and current cohort architecture. Rail funding evidence: appendix p21; fuel prices and efficiency: pp17–18. Scenarios remain deferred.', ('Potential reversal','Condition for change','Fuel-demand implication'))

slides.append(copy.deepcopy(old[11]))
slides.append(copy.deepcopy(old[10]))
s=copy.deepcopy(old[13])
s['title']='Competing corridors could divert inland volumes away from Durban'
s['rows'][3][2]='The route with price headroom must also offer capacity and reliable access. Higher national imports do not automatically become Vopak volumes.'
slides.append(s)

table('The initial share tests establish scale; accessible throughput remains the key uncertainty',4,[
 ['Durban','45.1% of the combined published gross capacity of Vopak and Bidvest in Durban.','A two-operator footprint proxy with mixed products and an incomplete market denominator. It does not establish Durban throughput share.'],
 ['Gauteng / Lesedi','2022 petrol + diesel sales: 6.81bn litres. Lesedi’s gross capacity equals 2.06% of that market per effective annual turn.','A cross-vintage scale test. Current sales, eligible working capacity, actual turns and Gauteng allocation are needed for a throughput estimate.'],
 ['Investment implication','Convert eligible tankage and realised turns into unique customer deliveries, then compare with existing capacity.','A large market can coexist with spare terminal capacity. Market scale alone does not establish a need for additional tanks.'],
], 'Operator capacities: Vopak Durban 360,246m³, Bidvest Durban 439,306m³, Lesedi 140,000m³. Department Gauteng sales 2022; appendix p22. Transfers between terminals must not be double-counted.', ('Catchment','Initial inference','What the result can support'))

table('Further investment depends on capturable volume exceeding existing capacity at an adequate return',4,[
 ['Accessible volume','Test each destination against delivered cost, service, access and customer demand.','A volume opportunity that Vopak can realistically serve.'],
 ['Capacity requirement','Compare the resulting flows with eligible working tankage, turnover and operational bottlenecks.','Whether the opportunity requires more tanks, faster handling or better use of existing assets.'],
 ['Financial forecast','Apply storage and handling terms, operating cost, capex, tax and working capital to incremental volumes.','Cash flow, break-even utilisation, NPV and IRR against the required return. Commercial inputs remain open.'],
 ['Decision today','The evidence supports testing an import-and-distribution opportunity. It does not yet establish an expansion return.','Prioritise corridor economics and terminal operating inputs, then quantify investment options. Scenarios follow separately.'],
], 'Resolution framework from the signed-off review and user comments. Financial and origin–destination modules are specified; commercial calibration and investment approval remain outstanding.', ('Decision test','Analysis required','Decision output'))

table('Supporting evidence for the main argument',0,[
 ['Demand context','GDP, investment and sector activity','Pages 14–16 support situation pages 2–3.'],
 ['Transport change','Fuel prices and vehicle efficiency','Pages 17–18 support the transport complication on page 7.'],
 ['Historical diesel support','Eskom fuel use and freight payload','Pages 19–20 support situation page 3 and power complication page 8.'],
 ['Delivery and market reach','Rail funding constraints and Gauteng demand','Pages 21–22 support corridor and share questions on pages 7, 10–11.'],
], 'Detailed evidence retained for review. The main argument is complete on pages 2–12; appendix pages are supporting exhibits, not additional situation pages.', ('Evidence group','Detail retained','Connection to the story'))
for index in [2,3,4,5,6,7,8,12,15]:
    item=copy.deepcopy(old[index]); item['section']=0
    slides.append(item)

base['cover_subtitle']='An import and inland distribution opportunity'
base['cover_status']='Reorganised review draft; scenarios deferred'
base['slides']=slides
base['main_story_pages']='2–12'
base['situation_pages']='2–6'
base['appendix_pages']='13–22'
(folder/'sa_market_story_reorganised_2026_10_07.json').write_text(json.dumps(base,indent=2,ensure_ascii=False),encoding='utf-8')
assert len(slides)==21
assert sum(x['section']==2 for x in slides)==5
print('22 pages: cover + 5 situation + 4 complication + 2 resolution + 10 appendix.')
