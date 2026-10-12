import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'../..');
const runtime='C:/Users/ITafr/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const skill='C:/Users/ITafr/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations';
const {FileBlob,PresentationFile}=await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const {applyPresentationChartFont}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
const qa=root+'/pptx/qa/story_v36';await fs.mkdir(qa,{recursive:true});
const p=await PresentationFile.importPptx(await FileBlob.load(root+'/pptx/output/delivered/supporting/archive/2026-10-11_cleanup/SA_Market_Story_2026-10-10_v30.pptx'));
if(process.argv.includes('--help-slides')){console.log(p.help('slides',{include:'index,notes,examples',maxChars:4500}).ndjson);process.exit(0);}
const spec=JSON.parse(await fs.readFile(root+'/pptx/story/sa_story_v36_2026_10_11.json','utf8'));
const old=[...p.slides.items],slideMap={1:old[0],19:old[1]};
for(const d of spec.slides)slideMap[d.page]=old[3].duplicate();
const keep=Object.keys(slideMap).map(Number).sort((a,b)=>a-b).map(k=>slideMap[k]);
keep.forEach((s,i)=>s.moveTo(i));
// Tail slides are removed from the exported presentation by the package stage.
const get=(s,name)=>s.shapes.items.find(x=>x.name===name);
function txt(s,name,value){const v=get(s,name);if(v)v.text=value;}
function add(s,name,value,x,y,w,h,size=18,bold=false,color='#11151A'){
 const t=s.shapes.add({name,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});t.text=value;t.text.style={typeface:'Lato',fontSize:size,bold,color,autoFit:'none'};return t;
}

function rule(s,name,x,y,w,h){s.shapes.add({name,geometry:'rect',position:{left:x,top:y,width:w,height:h},fill:'#B7B7B7',line:{fill:'none',width:0}});}
function drawScr(s){
 const blue='#0A2373';
 add(s,'S label','SITUATION',48,170,165,28,18,true,blue);
 add(s,'S answer','A large fuel market relies on substantial imports',225,166,820,30,22,true,blue);
 add(s,'S reference','pp3–6, 22',1080,170,90,28,15,true,blue);
 add(s,'S body','2025 demand is estimated at 21.0bn litres: 8.9bn petrol and 12.1bn diesel, down from 21.9bn in 2023. Road use dominates. At the assumed 5.8bn litres of domestic production, gross import need is about 16.7bn litres.',225,203,941,57,18);
 rule(s,'S divider',48,269,1118,1);
 add(s,'C label','COMPLICATION',48,280,170,28,18,true,blue);
 add(s,'C answer','Sector growth supports demand, but fuel use, supply and routes are changing',225,279,810,30,20,true,blue);
 add(s,'Deep dive label','Deep dive',1080,279,90,28,15,true,blue);
 const rows=[
 ['Mining, manufacturing\nand agriculture','Production, exports and harvests drive diesel use in equipment and freight; sector growth paths differ.','p6'],
 ['Eskom and power\ngeneration','Recovery reduces peaking and backup diesel at utilities, mines, factories and farms, while supporting activity.','pp7–8'],
 ['Road-to-rail shift and\nvehicle efficiency','Moving goods from trucks to rail and improving vehicle efficiency reduce fuel consumed per unit of activity.','pp9–10, 21'],
 ['Refineries and domestic\nfuel production','Higher output or restarts displace imports relative to the 5.8bn-litre assumption; lower output increases import need.','pp11–13'],
 ['Matola and Walvis Bay','Competing gateways could divert inland flows from Durban, depending on delivered cost, reliability and access.','pp14–15']
 ];
 rows.forEach(([a,b,c],i)=>{const y=320+i*44;add(s,'SCR driver '+i,a,225,y,235,40,16.5,true,blue);add(s,'SCR meaning '+i,b,472,y,585,40,16.5);add(s,'SCR pages '+i,c,1080,y,90,40,15,true,blue);if(i<4)rule(s,'SCR row divider '+i,225,y+42,941,.6);});
 rule(s,'C divider',48,544,1118,1);
 add(s,'R label','RESOLUTION',48,555,170,28,18,true,blue);
 add(s,'R answer','Vopak should secure customer capture before expanding',225,551,835,31,22,true,blue);
 add(s,'R reference','pp16–18',1080,555,90,28,15,true,blue);
 add(s,'R body','Base imports remain about 16.6bn litres in 2030. Illustrative capture is 2.63bn litres through Durban, including 1.32bn onward through Lesedi within the same flow; this fits the preliminary working-tank screen.',225,587,941,43,18);
 add(s,'R decision','Expansion requires secured incremental volumes and a demonstrated capacity shortfall.',225,634,941,25,18,true,blue);
 const footer=get(s,'Unified source footer');footer.position={left:48,top:663,width:1118,height:12};
}

for(const d of spec.slides){
 const s=slideMap[d.page];
 for(const item of [...s.shapes.items])if(item.position?.top>=150&&item.position?.top<640&&!['Unified source footer','Strictly Confidential footer','Slide Number Placeholder'].includes(item.name))item.delete();
 for(const t of [...s.tables.items])s.tables.deleteById(t.id);
 for(const im of [...s.images.items])im.delete();
 txt(s,'Title 1',d.title);const title=get(s,'Title 1');title.text.style={typeface:'Lato',fontSize:28,bold:true,color:'#000000',autoFit:'none'};
 txt(s,'Unified source footer',d.source);const footer=get(s,'Unified source footer');if(footer){footer.position={left:48,top:648,width:1118,height:30};footer.text.style={typeface:'Lato',fontSize:7.5,color:'#111111',autoFit:'none'};}
 if(d.kind==='scr'){
  drawScr(s);
 }else if(d.kind==='table'){
  const vals=[d.headers,...d.rows];const height=d.page===22?400:380;
  const t=s.tables.add({rows:vals.length,columns:d.headers.length,left:48,top:174,width:1118,height,columnWidths:d.widths??[350,350,418],values:vals});
  t.styleOptions={headerRow:false,bandedRows:false};t.borders.assign({fill:'#D9D9D9',width:.4,style:'solid'});
  t.rows[0].height=d.page===22?43:42;
  for(let r=1;r<vals.length;r++)t.rows[r].height=(height-t.rows[0].height)/(vals.length-1);
  for(let r=0;r<vals.length;r++)for(let c=0;c<vals[0].length;c++){
   const cell=t.getCell(r,c);cell.fill='#FFFFFF';cell.text.style={typeface:'Lato',fontFamily:'Lato',fontSize:d.font,bold:r===0||c===0,color:'#11151A',verticalAlignment:'top'};
  }
 }else{
  const colors=['#0A2373','#6782B4','#868686'];
  add(s,'Chart heading',d.chartHeading??'Demand trend',48,173,760,37,21,true,'#0A2373');
  rule(s,'Chart header rule',48,210,770,1);rule(s,'Insight header rule',850,210,316,1);rule(s,'Chart divider',832,173,1,380);
  const ch=s.charts.add(d.chartType,{position:{left:48,top:236,width:770,height:310},categories:d.categories,
   series:d.series.map((series,i)=>({...series,fill:colors[i],line:{fill:colors[i],width:2.5},valuesFormatCode:'0.00'})),
   hasLegend:d.series.length>1,legend:{position:'bottom'},
   barOptions:{direction:d.direction,grouping:'clustered'},
   xAxis:{textStyle:{fontSize:12,fill:'#555555'}},yAxis:{numberFormatCode:'0.0',textStyle:{fontSize:12,fill:'#555555'}},
   dataLabels:{showValue:d.chartType==='bar',position:'outEnd',textStyle:{fontSize:12,fill:'#333333'},numberFormatCode:'0.00'}});
  applyPresentationChartFont(ch,{fontFamily:'Lato'});
  add(s,'Chart unit',d.page===9?'Million tonnes':'Billion litres',55,208,750,23,13,false,'#626262');
  add(s,'Chart insight header',d.side[0],850,173,310,37,21,true,'#0A2373');
  add(s,'Chart insights',d.side.slice(1).join('\n\n'),850,230,310,330,d.page===3?17:18);
 }
 if(d.kind!=='scr')add(s,'Story implication',d.takeaway,48,586,1118,57,17,false,'#0A2373');
 s.speakerNotes.textFrame.setText(d.source+'\n'+d.takeaway+'\nPlanning baseline: user-directed 5.8bn litres of domestic petrol/diesel production; not reported output. Workbook: SA_Fuel_Analytics_2025_Baseline_2026-10-11_v02.xlsx.\nMozambique sources: https://www.galp.com/corp/pt/media/comunicados-de-imprensa/comunicado/id/1172 ; https://www.petromoc.co.mz/product-service/logistica/ ; https://sasol.com/our-businesses/energy/gas-sourcing-and-operations');
}
for(const item of slideMap[1].shapes.items){const str=item.text?.toString();if(str)item.text=str.replaceAll('10 October 2026','11 October 2026').replaceAll('10 Oct 2026','11 Oct 2026');}
const nav={main:{},appendix:{}};
keep.forEach((s,i)=>{
 for(const item of [...s.shapes.items])if(['SCR 1','SCR 2','SCR 3','SCR 4'].includes(item.name))item.delete();
 txt(s,'Slide Number Placeholder',String(i+1));
 if(i>=1&&i<18)nav.main[i+1]=i<3?0:i<6?1:i<15?2:3;
 if(i>=18)nav.appendix[i+1]=i===18?0:2;
});
await fs.writeFile(qa+'/page_map.json',JSON.stringify({nav,keep_count:23},null,2));
await (await PresentationFile.exportPptx(p)).save(qa+'/body_untrimmed.pptx');
await fs.writeFile(qa+'/content.json',JSON.stringify(spec,null,2));
console.log('Authored 23-page story; package stage retains these ordered slides');
