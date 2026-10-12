"""Arrange existing calculated evidence into the reviewed story structure."""
import json
from pathlib import Path
from lfm.model.sa_story_views import power_scenario_endpoints
root=Path(__file__).resolve().parents[2]
old=json.loads((root/'pptx/story/sa_story_v33_2026_10_11.json').read_text())
mapping={2:22,4:4,5:5,6:6,7:21,8:7,9:8,10:9,11:10,12:11,13:12,14:13,15:14,16:15,17:16,18:17,19:18,21:20,22:23}
slides=[]
for s in old['slides']:
    if s['page']==3:continue
    s['page']=mapping[s['page']]
    slides.append(s)
by={s['page']:s for s in slides}
m=json.loads((root/'output/delivered/sa_analytics_2026_10_11_v02/analytics.json').read_text())
val=lambda v:v['value'] if isinstance(v,dict) else v
hist=[[val(v) for v in r] for r in m['sheets']['Demand history']['rows'][:13]]
slides.append(dict(page=3,kind='chart',chartType='line',direction='column',
 title='Fuel demand has eased to 21.0bn litres and stays broadly flat through 2030 in the base case',
 categories=[str(r[0])+('E' if r[0]>2023 else '') for r in hist],
 series=[{'name':name,'values':[r[c] for r in hist]} for name,c in [('Total',3),('Petrol',1),('Diesel',2)]],
 chartHeading='National fuel demand, 2013–2025',
 side=['Five drivers of the outlook','Sectors: activity supports demand.','Eskom: recovery lowers power fuel use.','Road-to-rail and efficiency reduce road fuel use.','Refineries: recovery displaces imports.','Matola / Walvis Bay: gateways compete for inland flows.','2030 base: 20.9bn L demand; 16.6bn L gross imports.'],
 takeaway='Demand determines consumption, domestic production determines import need, and competing gateways determine Durban’s share.',
 source='Department sales 2013–2023; analytical workbook v02. E = estimated 2024–2025. 2030 is the base scenario, not an observed outcome. Walvis Bay diversion remains unquantified.'))
# Show scenario endpoints directly; do not invent an annual power path.
by[8]=dict(page=8,kind='chart',chartType='bar',direction='column',
 title='Further power recovery halves fuel demand to 0.54bn litres in the 2030 base case',
 categories=['2025 estimate','2030 base','2030 lower use','2030 unchanged use'],
 series=[{'name':'Utility and private power','values':power_scenario_endpoints(m)}],
 chartHeading='Power fuel demand across scenarios',
 side=['Base case and sensitivities','2025 estimate: 1.08bn L, including 0.20bn L assumed private backup.','Base: 50% retained in 2030; a 0.54bn L reduction.','Lower-use case: 35% retained. Unchanged-use case: 100% retained.'],
 takeaway='Improved electricity supply lowers peaking and backup fuel use, even where transport and industrial activity continue to grow.',
 source='Analytical workbook v02: calculated power baseline and registered 2030 retention assumptions. Estimated utility/private scope includes FY proxies and IPP conversion. Scenario endpoints, not forecasts of annual dispatch.')
slides=[by[8] if s['page']==8 else s for s in slides]
by={s['page']:s for s in slides}
by[4]['categories']=[str(r[0])+('E' if r[0]>2023 else '') for r in hist]
by[4]['side']=['Petrol demand outlook','Petrol: 9.04bn L in 2023 to 8.86bn L in 2025E.','Assumed efficiency and fleet changes outweigh activity growth.','Diesel: 12.13bn L in 2025E.','2013–23: reported Department series. 2024–25: estimates.']
by[4]['chartHeading']='Petrol and diesel demand, 2013–2025'
by[5]['chartHeading']='2025 estimated demand by use'
pairs=sorted(zip(by[5]['categories'],by[5]['series'][0]['values']),key=lambda p:p[1])
by[5]['categories']=[p[0] for p in pairs];by[5]['series'][0]['values']=[p[1] for p in pairs]
by[6]['chartHeading']='Estimated sector diesel demand'
by[7]['chartHeading']='Eskom diesel and kerosene use'
by[9]['chartHeading']='Reported road and rail freight'
by[13]['chartHeading']='Gross import requirement, 2025–2030'
by[14]['rows'].append(['Walvis Bay','Alternative route identified in HG’s framing','Test delivered cost, reliability and customer access; no diversion volume assigned'])
by[14]['title']='Matola and Walvis Bay provide competing route options for inland supply'
by[14]['takeaway']='Matola has quantified infrastructure evidence; Walvis Bay remains a route sensitivity requiring comparable cost and access evidence.'
by[14]['font']=16
by[14]['source']+=' Walvis Bay: HG supplied storyboard, 6 October 2026; qualitative route sensitivity only.'
by[22]['rows']=[[('0.00' if x=='-0.00' else x) for x in r] for r in by[22]['rows']]
for r,new in zip(by[23]['rows'],['3–6, 21–22','7–10','11–13, 20','14–15','16–18']):r[1]=new
slides.append({'page':2,'kind':'scr','title':'South Africa remains an import-led fuel market, making customer capture Vopak’s priority','source':'Analytical workbook v02 and market review. Demand is estimated; production and capture are planning assumptions. Product reconciliation remains open; Walvis Bay diversion is unquantified.','takeaway':''})
spec={'slides':sorted(slides,key=lambda s:s['page']),'core_pages':18,'total_pages':23,'hg_page':19}
(root/'pptx/story/sa_story_v36_2026_10_11.json').write_text(json.dumps(spec,indent=2),encoding='utf8')
print('Prepared 23-page story: 18 core, five appendix')
