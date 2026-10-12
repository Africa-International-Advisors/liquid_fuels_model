"""Separate observed complications from model outcomes and supporting sensitivities."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
old=json.loads((root/'pptx/story/sa_story_v36_2026_10_11.json').read_text())
mapping={2:2,3:3,4:4,5:5,6:7,7:8,8:17,9:9,10:18,11:6,12:19,13:12,14:11,15:20,16:13,17:14,18:15,20:21,21:22,22:23,23:24}
slides=[]
for s in old['slides']:
 s['page']=mapping[s['page']];slides.append(s)
by={s['page']:s for s in slides}
by[6]['source']='Analytical workbook v02, national demand and trade balance. Domestic production is a planning assumption; the alternative plant-based estimate is retained in the appendix.'
by[6]['rows'][1][2]='National planning assumption'
by[8]['title']='Eskom’s fuel use fell by 40% in FY2025 as electricity supply improved'
by[8]['side']=['Lower power-related fuel use','Eskom diesel and kerosene fell from 1.130bn L in FY2024 to 0.679bn L in FY2025.','Better supply can also reduce backup diesel at mines, factories and farms.','Private backup use is estimated separately; it is not measured by this Eskom series.']
by[8]['takeaway']='Power recovery reduces a source of diesel demand created by electricity shortages; the 2030 assumptions are in the appendix.'
by[8]['source']='Eskom Integrated Report 2025, p141. Fiscal years end in March. Reported series includes diesel and kerosene; private backup consumption is outside this series.'
by[9]['title']='Rail volumes are recovering, creating scope to reduce road diesel use'
by[9]['side']=['Recovery and displacement','Rail: 160.7m tonnes in 2024 to 168.3m in 2025. Road: 979.8m to 976.5m tonnes.','A shift of mining, agricultural and manufactured goods to rail can reduce truck fuel use.','Rail growth alone does not prove road displacement; distance, cargo and traction mix matter.']
by[9]['takeaway']='Road remains the dominant freight mode; sustained rail recovery could change the diesel required to move goods.'
by[11]['title']='Matola provides an existing alternative gateway for inland fuel supply'
by[11]['rows']=[r for r in by[11]['rows'] if r[0]!='Walvis Bay']
by[11]['takeaway']='Matola’s infrastructure creates an alternative supply route; recorded cross-border flows remain much smaller than storage capacity.'
by[11]['source']='Galp Matola commissioning release, 3 December 2020; Petromoc logistics disclosures; Sasol Mozambique operations; SARS customs, 2022 and 2025. Storage is not annual throughput.'
by[11]['font']=17
by[12]['title']='The base case leaves imports near 16.6bn litres in 2030, with refinery recovery driving the downside'
by[19]['title']='Refinery restart assumptions drive the lower-import sensitivity'
by[20]['title']='Illustrative route costs put Matola at a R0.19-per-litre logistics premium'
by[24]['title']='Source definitions and explicit assumptions underpin the demand and import outlook'
by[24]['headers']=['Evidence / assumption','Pages','Source and analytical treatment']
by[24]['rows']=[
 ['National sales and sector activity','3–7, 22–23','Department sales, energy balances and Stats SA activity. Demand after 2023 is estimated; segment boundaries retain an unallocated residual.'],
 ['Power and freight','8–9, 17–18','Eskom fuel and Stats SA freight observations. Private backup, future rail shift and efficiency remain explicit planning assumptions.'],
 ['Domestic supply and imports','6, 10, 12, 19, 21','Sasol and Glencore plant disclosures; SARS trade. The 5.8bn-litre national production case is an assumption; product reconciliation remains open.'],
 ['Matola infrastructure and costs','11, 20','Operator infrastructure disclosures and SARS customs. Logistics costs are illustrative, rather than carrier quotations.'],
 ['Vopak capture and capacity','13–15','Illustrative gateway capture and working-tank turnover. Customer commitments and engineering constraints determine achievable volumes.']]
by[24]['takeaway']='Observed data, estimates and scenario assumptions are labelled separately throughout the analysis.'
by[24]['source']='Sources: Department energy statistics; Stats SA; Eskom; Sasol; Glencore; SARS; Galp; Petromoc. Supporting calculations: analytical workbook v02 and market-sizing workbook.'
by[3]['side']=[x.replace('Matola / Walvis Bay: gateways compete for inland flows.','Matola: an alternative gateway competes for inland flows.') for x in by[3]['side']]
by[3]['source']=by[3]['source'].replace(' Walvis Bay diversion remains unquantified.','')
slides.append(dict(page=10,kind='table',title='Changes in refinery output alter the volume that imports must supply',
 headers=['Domestic supply','Reported evidence','Implication for imports'],rows=[
 ['Secunda','Refined-products output: 29.1m barrels in FY2024; 27.6m in FY2025; 30.6m in FY2026','Operating recovery can increase domestic supply; petrol and diesel yields determine import displacement.'],
 ['Natref','Sasol-reported output: 17.8m barrels in FY2024; 14.7m in FY2025; 25.8m in FY2026','FY2026 includes above-share production, so the latest reported change cannot be treated as a like-for-like change in whole-plant output.'],
 ['Astron','Reported refined products: 166,204 billion Btu in 2024; 164,365 billion Btu in 2025','Output and product mix affect supply; energy units require conversion before comparison with customs litres.'],
 ['SAPREF and PetroSA','No refining contribution included in the 2025 production assessment','Restored refining would displace imports only when plants produce saleable products. Terminal handling is not refinery output.']],
 widths=[240,425,453],font=17,
 takeaway='Domestic production can recover or fall independently of demand; actual output and product yields determine the import requirement.',
 source='Sasol production metrics FY2025 and FY2026; Glencore annual reports 2024 and 2025; 2025 plant assessment. Fiscal and calendar periods and reporting scopes differ. Restart sensitivities are in the appendix.'))
slides.append(dict(page=16,kind='divider',title='Appendix',source='',takeaway=''))
replacements={
 'user-directed':'','User-directed':'','directed planning':'planning','directed opening':'assumed opening','directed case':'planning case','directed supply':'assumed supply','directed 5.8bn':'assumed 5.8bn',
 '5.8bn L override':'5.8bn L planning case','Source register:':'Source basis:',
 'Registered market_review.yaml and market_review.json, 10 October.':'Market-sizing analysis, October 2026.',
 'Registered terminal_site_assumptions.csv and market_review.json.':'Terminal working-capacity assessment, October 2026.',
 'Registered scenario assumptions; DR03 refinery evidence.':'Refinery production and restart scenario assumptions.',
 'Registered scenario assumptions; DR08 refinery evidence.':'Refinery production and restart scenario assumptions.',
 'registered 2030 retention assumptions':'2030 retention assumptions',
 'Authored':'Illustrative','authored':'illustrative',
 'Analytical workbook v02 and market review.':'Analytical workbook v02 and market-sizing analysis.',
 ' Walvis Bay diversion is unquantified.':'',' Walvis Bay diversion remains unquantified.':'',
 'Earlier deck FIASA comparison figures are not spliced into this series.':'The Department series is used consistently.',
 'registered demand assumptions and':'demand assumptions and',
 'Planning assumptions remain editable in workbook v02.':'Planning assumptions are detailed in the supporting workbook.'}
def clean(v):
 if isinstance(v,str):
  for a,b in replacements.items():v=v.replace(a,b)
  return v.replace('  ',' ')
 if isinstance(v,list):return [clean(x) for x in v]
 if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
 return v
spec=clean({'slides':sorted(slides,key=lambda s:s['page']),'core_pages':15,'total_pages':24,'appendix_page':16})
(root/'pptx/story/sa_story_v37_2026_10_11.json').write_text(json.dumps(spec,indent=2),encoding='utf8')
print('Prepared 15 core pages, appendix divider and eight supporting pages')
