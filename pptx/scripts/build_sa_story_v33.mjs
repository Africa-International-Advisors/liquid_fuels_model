import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'../..');
const runtime='C:/Users/ITafr/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const skill='C:/Users/ITafr/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations';
const {FileBlob,PresentationFile}=await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const {applyPresentationChartFont}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
const qa=root+'/pptx/qa/story_v33';await fs.mkdir(qa,{recursive:true});
const p=await PresentationFile.importPptx(await FileBlob.load(root+'/pptx/output/delivered/supporting/archive/2026-10-11_cleanup/SA_Market_Story_2026-10-10_v30.pptx'));
if(process.argv.includes('--help-slides')){console.log(p.help('slides',{include:'index,notes,examples',maxChars:4500}).ndjson);process.exit(0);}
const spec=JSON.parse(await fs.readFile(root+'/pptx/story/sa_story_v33_2026_10_11.json','utf8'));
const old=[...p.slides.items],slideMap={1:old[0],20:old[1]};
for(const d of spec.slides)slideMap[d.page]=old[3].duplicate();
const keep=Object.keys(slideMap).map(Number).sort((a,b)=>a-b).map(k=>slideMap[k]);
keep.forEach((s,i)=>s.moveTo(i));
// Tail slides are removed from the exported presentation by the package stage.
const get=(s,name)=>s.shapes.items.find(x=>x.name===name);
function txt(s,name,value){const v=get(s,name);if(v)v.text=value;}
function add(s,name,value,x,y,w,h,size=18,bold=false,color='#11151A'){
 const t=s.shapes.add({name,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});t.text=value;t.text.style={typeface:'Lato',fontSize:size,bold,color,autoFit:'none'};return t;
}
for(const d of spec.slides){
 const s=slideMap[d.page];
 for(const item of [...s.shapes.items])if(item.position?.top>=150&&item.position?.top<640&&!['Unified source footer','Strictly Confidential footer','Slide Number Placeholder'].includes(item.name))item.delete();
 for(const t of [...s.tables.items])s.tables.deleteById(t.id);
 for(const im of [...s.images.items])im.delete();
 txt(s,'Title 1',d.title);const title=get(s,'Title 1');title.text.style={typeface:'Lato',fontSize:28,bold:true,color:'#000000',autoFit:'none'};
 txt(s,'Unified source footer',d.source);const footer=get(s,'Unified source footer');if(footer){footer.position={left:48,top:648,width:1118,height:30};footer.text.style={typeface:'Lato',fontSize:7.5,color:'#111111',autoFit:'none'};}
 if(d.kind==='table'){
  const vals=[d.headers,...d.rows];const height=d.page===2?400:380;
  const t=s.tables.add({rows:vals.length,columns:d.headers.length,left:48,top:174,width:1118,height,columnWidths:d.widths??[350,350,418],values:vals});
  t.styleOptions={headerRow:false,bandedRows:false};t.borders.assign({fill:'#D9D9D9',width:.4,style:'solid'});
  t.rows[0].height=d.page===2?43:42;
  for(let r=1;r<vals.length;r++)t.rows[r].height=(height-t.rows[0].height)/(vals.length-1);
  for(let r=0;r<vals.length;r++)for(let c=0;c<vals[0].length;c++){
   const cell=t.getCell(r,c);cell.fill=r===0?'#F5F5F5':'#FFFFFF';cell.text.style={typeface:'Lato',fontFamily:'Lato',fontSize:d.font,bold:r===0||c===0,color:r===0||c===0?'#0A2373':'#11151A',verticalAlignment:'top'};
  }
 }else{
  const colors=['#0A2373','#6782B4','#868686'];
  const ch=s.charts.add(d.chartType,{position:{left:48,top:190,width:770,height:360},categories:d.categories,
   series:d.series.map((series,i)=>({...series,fill:colors[i],line:{fill:colors[i],width:2.5},valuesFormatCode:'0.00'})),
   hasLegend:d.series.length>1,legend:{position:'bottom'},
   barOptions:{direction:d.direction,grouping:'clustered'},
   xAxis:{textStyle:{fontSize:12,fill:'#555555'}},yAxis:{numberFormatCode:'0.0',textStyle:{fontSize:12,fill:'#555555'}},
   dataLabels:{showValue:d.chartType==='bar',position:'outEnd',textStyle:{fontSize:12,fill:'#333333'},numberFormatCode:'0.00'}});
  applyPresentationChartFont(ch,{fontFamily:'Lato'});
  add(s,'Chart unit',d.page===10?'Million tonnes':'Billion litres',55,164,750,25,14,false,'#626262');
  add(s,'Chart insight header',d.side[0],850,185,310,48,22,true,'#0A2373');
  add(s,'Chart insights',d.side.slice(1).join('\n\n'),850,245,310,305,18);
 }
 add(s,'Story implication',d.takeaway,48,586,1118,57,17,false,'#0A2373');
 s.speakerNotes.textFrame.setText(d.source+'\n'+d.takeaway+'\nPlanning baseline: user-directed 5.8bn litres of domestic petrol/diesel production; not reported output. Workbook: SA_Fuel_Analytics_2025_Baseline_2026-10-11_v02.xlsx.\nMozambique sources: https://www.galp.com/corp/pt/media/comunicados-de-imprensa/comunicado/id/1172 ; https://www.petromoc.co.mz/product-service/logistica/ ; https://sasol.com/our-businesses/energy/gas-sourcing-and-operations');
}
for(const item of slideMap[1].shapes.items){const str=item.text?.toString();if(str)item.text=str.replaceAll('10 October 2026','11 October 2026').replaceAll('10 Oct 2026','11 Oct 2026');}
const nav={main:{},appendix:{}};
keep.forEach((s,i)=>{
 for(const item of [...s.shapes.items])if(['SCR 1','SCR 2','SCR 3','SCR 4'].includes(item.name))item.delete();
 txt(s,'Slide Number Placeholder',String(i+1));
 if(i>=1&&i<19)nav.main[i+1]=i<3?0:i<7?1:i<16?2:3;
 if(i>=19)nav.appendix[i+1]=i===19?0:2;
});
await fs.writeFile(qa+'/page_map.json',JSON.stringify({nav,keep_count:22},null,2));
await (await PresentationFile.exportPptx(p)).save(qa+'/body_untrimmed.pptx');
await fs.writeFile(qa+'/content.json',JSON.stringify(spec,null,2));
console.log('Authored 22-page story; package stage retains these ordered slides');
