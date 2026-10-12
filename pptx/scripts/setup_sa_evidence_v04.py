from pathlib import Path
import json
r=Path(__file__).resolve().parents[2];s=r/'pptx/scripts'
old=json.loads((r/'pptx/story/sa_story_v37_2026_10_11.json').read_text())
by={x['page']:x for x in old['slides']}
e=[dict(by[k]) for k in [4,7,8,9,22,10,11]]
e[0].update(title='South Africa’s estimated 21bn-litre fuel market is dominated by road demand',side=['2025 estimated demand','Petrol road 8.59 | Freight 4.82','Other road diesel 1.61','Mining 1.41 | Agriculture 1.13','Power 1.08 | Manufacturing 0.17','Other petrol 0.27 | Other diesel 1.91','All values: bn litres. Allocations are estimates; manufacturing is an industry residual.'],takeaway='Demand is estimated at 20.99bn litres in 2025; road uses account for most allocated demand.')
e[0]['source']+=' Segment split: analytical workbook v02, Segments. Displayed figures rounded; other diesel remains unallocated.'
e[1]['categories']=['2023E','2024E','2025E']
e[1]['title']='Agricultural fuel demand rebounds while mining and manufacturing remain broadly flat'
e[2]['side']=['Observed use and estimated scope','Eskom: 1.130bn L in FY2024 → 0.679bn L in FY2025 (diesel + kerosene).','2025 utility + private power estimate: 1.08bn L, including 0.20bn L assumed private backup.','IPP conversion and fiscal-year proxies are estimates; private use is not measured by Eskom.']
e[2]['takeaway']='Improved electricity supply reduces peaking and backup fuel use; the private-backup contribution remains estimated.'
e[2]['source']+=' Analytical workbook v02, Segments: IPP conversion and private-backup assumptions.'
e[4]={'kind':'chart','chartType':'bar','direction':'column','title':'Hybrids dominate electrified new-vehicle sales; fleet fuel savings emerge as vehicles turn over','categories':['BEV','Plug-in hybrid','Conventional hybrid'],'series':[{'name':'2025 new sales','values':[1088,2810,12818]}],'chartHeading':'Electrified vehicle sales, 2025','unit':'Vehicles sold','side':['Different fuel-use effects','BEV: 1,088 sales, or 0.18% of all new vehicles.','PHEVs and conventional hybrids still consume fuel; savings depend on usage.','New sales are not fleet penetration. Efficiency and mileage must be modelled separately.'],'takeaway':'The model’s fuel-efficiency path is a planning assumption; new-vehicle sales alone do not quantify national fuel savings.','source':'naamsa all-market sales 2025; master workbook Vehicle history S31:S36; evidence retained in market story v27 p11. Analytical workbook v02: efficiency is a planning assumption; avoid double-counting hybrid savings.'}
e[5]['takeaway']='The 5.8bn-litre 2025 petrol/diesel baseline is a planning assumption; these differently scoped plant disclosures do not sum directly to it.'
e[5]['source']=e[5]['source'].replace(' Restart sensitivities are in the appendix.',' Product yields and reporting scopes require reconciliation to the 5.8bn-litre planning baseline.')
e[6].update(title='Durban’s inland share depends on competing gateways and reliable onward connections',headers=['Supply route','Evidence available','Implication for addressable flows'],rows=[['Durban and other SA ports','Durban customs: 13.16bn L of petrol/diesel imports in 2025','Allocate national imports across gateways before assessing inland customer reach.'],['Durban–NMPP–Lesedi','Existing coastal-to-inland connection; customer and product access remain to be established','Pipeline, receipt and dispatch constraints determine the flows Vopak can serve.'],['Matola infrastructure','Galp/IPG: 60,000m³ petrol/diesel storage; Petromoc: 390,000m³ across liquid fuels','Do not add potentially overlapping capacities or equate tankage with annual SA deliveries.'],['Observed Mozambique route','Komatipoort recorded imports: 0.303bn L in 2022 → 0.086bn L in 2025','Observed cross-border flows provide a firmer volume anchor than storage capacity.'],['Walvis Bay alternative','Comparable delivered-cost, access and SA flow evidence is not established in this review','Retain as a route to assess; no quantified diversion or customer capture is assigned.']],widths=[245,418,455],font=17,takeaway='Compare the same product and inland destination across routes; Matola and Walvis Bay affect gateway share, not national demand.',source='SARS customs 2022/2025; Galp Matola commissioning, 3 December 2020; Petromoc logistics; existing Durban–Lesedi corridor evidence in market-sizing workbook. Walvis Bay diversion is unquantified; comparable delivered-cost evidence remains open.')
(r/'pptx/story/sa_evidence_v04.json').write_text(json.dumps(e,ensure_ascii=False,indent=2),encoding='utf8')
t=(s/'build_sa_scr_six_v03.mjs').read_text(encoding='utf8').replace('scr_six_v03','evidence_v04')
insertion="""
const evidenceSpec=JSON.parse(await fs.readFile(root+'/pptx/story/sa_evidence_v04.json','utf8'));
const evidence=[];
for(const [idx,d] of evidenceSpec.entries()){
 const es=base.duplicate();evidence.push(es);
 for(const sh of [...es.shapes.items])if((sh.position?.top>=150&&sh.position?.top<640&&!['Unified source footer','Strictly Confidential footer','Slide Number Placeholder'].includes(sh.name))||['SCR 1','SCR 2','SCR 3','SCR 4'].includes(sh.name))sh.delete();
 for(const tb of [...es.tables.items])es.tables.deleteById(tb.id);for(const im of [...es.images.items])im.delete();
 const get=n=>es.shapes.items.find(x=>x.name===n);
 get('Title 1').text=d.title;get('Title 1').text.style={typeface:'Lato',fontSize:28,bold:true,color:'#000000',autoFit:'none'};
 get('Unified source footer').text=d.source;get('Unified source footer').position={left:48,top:648,width:1118,height:25};get('Unified source footer').text.style={typeface:'Lato',fontSize:7.5,color:'#111111',autoFit:'none'};
 if(d.kind==='table')nativeTable(es,[d.headers,...d.rows],d.widths,174,398,d.font);
 else{
  add(es,'Evidence chart heading',d.chartHeading,48,173,770,35,21,true,blue);rule(es,'Evidence chart rule',48,210,770);rule(es,'Evidence insight rule',850,210,316);
  es.shapes.add({name:'Evidence divider',geometry:'rect',position:{left:832,top:173,width:1,height:385},fill:'#C5C5C5',line:{fill:'none',width:0}});
  add(es,'Evidence unit',d.unit??(idx===3?'Million tonnes':'Billion litres'),55,214,760,24,13,false,'#626262');
  const colors=['#0A2373','#6782B4','#868686'];
  es.charts.add(d.chartType,{position:{left:48,top:244,width:770,height:306},categories:d.categories,series:d.series.map((v,i)=>({...v,fill:colors[i],line:{fill:colors[i],width:2.5},valuesFormatCode:idx===4?'0':'0.00'})),hasLegend:d.series.length>1,legend:{position:'bottom'},barOptions:{direction:d.direction,grouping:'clustered'},xAxis:{textStyle:{fontSize:12,fontFamily:'Lato',fill:'#555555'}},yAxis:{numberFormatCode:idx===4?'#,##0':'0.0',textStyle:{fontSize:12,fontFamily:'Lato',fill:'#555555'}},dataLabels:{showValue:d.chartType==='bar',position:'outEnd',textStyle:{fontSize:12,fontFamily:'Lato',fill:'#333333'},numberFormatCode:idx===4?'#,##0':'0.00'}});
  add(es,'Evidence insight heading',d.side[0],850,173,316,35,21,true,blue);
  add(es,'Evidence insights',d.side.slice(1).join('\\n\\n'),850,230,316,330,idx===0?16:18);
 }
 add(es,'Evidence takeaway',d.takeaway,48,592,1118,50,19,false,blue);
 es.speakerNotes.textFrame.setText(d.source+'\\n'+d.takeaway);
}
const ordered=[cover,slides[0],slides[1],...evidence,slides[2],slides[3],closing];
ordered.forEach((ss,i)=>{ss.moveTo(i);const n=ss.shapes.items.find(x=>x.name==='Slide Number Placeholder');if(n)n.text=String(i+1);});
"""
t=t.replace("await fs.writeFile(qa+'/page_map.json'",insertion+"\nawait fs.writeFile(qa+'/page_map.json'")
t=t.replace('main:{2:1,3:2,4:3,5:3}', 'main:{2:1,3:2,4:1,5:2,6:2,7:2,8:2,9:2,10:2,11:3,12:3}').replace('keep_count:6','keep_count:13')
t=t.replace('Six-page SCR and market-sizing framework authored','Thirteen-page pack with seven evidence pages authored')
(s/'build_sa_evidence_v04.mjs').write_text(t,encoding='utf8')
for old,new in [('trim_sa_scr_six_v03.py','trim_sa_evidence_v04.py'),('style_sa_scr_six_v03.py','style_sa_evidence_v04.py'),('apply_sa_scr_six_navigation_v03.py','apply_sa_evidence_navigation_v04.py'),('finalize_sa_scr_six_v03.mjs','finalize_sa_evidence_v04.mjs'),('package_sa_chart_workbooks_v37.py','package_sa_evidence_charts_v04.py')]:
 t=(s/old).read_text(encoding='utf8').replace('scr_six_v03','evidence_v04').replace('story_v37','evidence_v04').replace('SA_SCR_Six_Page_2026-10-11_v03','SA_SCR_Evidence_2026-10-11_v04').replace('SA_Market_Story_2026-10-11_v37','SA_SCR_Evidence_2026-10-11_v04')
 if old.startswith('trim'):t=t.replace('[6:]','[13:]')
 if old.startswith('apply'):t=t.replace('len(native)==4','len(native)==11').replace('Exported 6 slides; 4','Exported 13 slides; 11')
 if old.startswith('finalize'):
  t=t.replace('explicitTotalSlideCount:6','explicitTotalSlideCount:13').replace('requiredNativeTableOwnerSlides:[3,4]','requiredNativeTableOwnerSlides:[3,9,10,11]')
  t=t.replace("'--require-native-table-slide','3','--require-native-table-slide','4'","'--require-native-table-slide','3','--require-native-table-slide','9','--require-native-table-slide','10','--require-native-table-slide','11'")
  t=t.replace("candidatePath:qa+'/SA_SCR_Evidence_2026-10-11_v04.pptx'","candidatePath:qa+'/with_chart_workbooks.pptx'")
 (s/new).write_text(t,encoding='utf8')
