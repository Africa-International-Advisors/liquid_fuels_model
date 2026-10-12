import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'../..');
const runtime='C:/Users/ITafr/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const {FileBlob,PresentationFile}=await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
// v30 and v31 have identical slide bodies; v31's native SmartArt is attached
// after editing, using the preserved package components rather than reimporting it.
const source=root+'/pptx/output/delivered/supporting/archive/2026-10-11_cleanup/SA_Market_Story_2026-10-10_v30.pptx';
const qa=root+'/pptx/qa/core_v32';await fs.mkdir(qa,{recursive:true});
const spec=JSON.parse(await fs.readFile(root+'/pptx/story/sa_core_v32_2026_10_11.json','utf8'));
const p=await PresentationFile.importPptx(await FileBlob.load(source));
const old=[...p.slides.items];
const clones={};for(const name of spec.core.filter(x=>typeof x==='string'))clones[name]=old[3].duplicate();
const order=[...spec.core,...spec.appendix];
const ordered=order.map(x=>typeof x==='number'?old[x-1]:clones[x]);
ordered.forEach((s,i)=>s.moveTo(i));
function shape(s,name){return s.shapes.items.find(x=>x.name===name);}
function text(s,name,value){const v=shape(s,name);if(!v)throw new Error('Missing '+name);v.text=value;}
function addText(s,name,value,y,height,size=17){
 const v=s.shapes.add({name,geometry:'textbox',position:{left:48,top:y,width:1118,height},fill:'none',line:{fill:'none',width:0}});
 v.text=value;v.text.style={typeface:'Lato',fontSize:size,color:'#11151A',autoFit:'none'};
}
function clearBody(s){
 for(const item of [...s.shapes.items]){
  const y=item.position?.top;
  if(y>=150&&y<640&&!['Unified source footer','Strictly Confidential footer','Slide Number Placeholder'].includes(item.name))item.delete();
 }
 for(const t of [...s.tables.items])s.tables.deleteById(t.id);
 for(const im of [...s.images.items])im.delete();
}
for(const [pageString,d] of Object.entries(spec.tables)){
 const page=Number(pageString),s=ordered[page-1];clearBody(s);
 text(s,'Title 1',d.title);text(s,'Unified source footer',d.footer);
 const values=[d.headers,...d.rows];const height=d.height??400;
 const t=s.tables.add({rows:values.length,columns:d.headers.length,left:48,top:174,width:1118,height,columnWidths:d.widths,values});
 t.styleOptions={headerRow:false,bandedRows:false};
 t.borders.assign({fill:'#D9D9D9',width:.4,style:'solid'});
 t.rows[0].height=42;
 for(let r=1;r<values.length;r++)t.rows[r].height=(height-42)/(values.length-1);
 for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
  const cell=t.getCell(r,c);cell.fill=r===0?'#F5F5F5':'#FFFFFF';
  cell.text.style={typeface:'Lato',fontFamily:'Lato',fontSize:d.font??18,bold:r===0||c===0,color:c===0||r===0?'#0A2373':'#11151A',verticalAlignment:'top'};
 }
 addText(s,'Core implication',d.takeaway,Math.min(174+height+18,621),page===6?25:60,page===6?14:16);
 s.speakerNotes.textFrame.setText(d.footer+'\n'+d.takeaway+'\nEvidence retained from Manish handback through 9 October and registered 10 October review. Narrative restructuring 11 October; no new model assumptions or forecasts adopted.');
}
for(const [pageString,d] of Object.entries(spec.edits)){
 const s=ordered[Number(pageString)-1];if(d.title)text(s,'Title 1',d.title);
 if(d.interpretation)text(s,'Interpretation',d.interpretation);
}
// Keep HG's original framing on page 2; make page 3 the concise current answer.
const response=ordered[2];const tab=response.tables.items[0];
const answer=[
 'South Africa sold 21.94bn litres of petrol and diesel in 2023. Petrol demand declined over 2013–2023 while diesel grew slowly.\n\nRefinery shutdowns changed the supply base. Gross finished-product imports reached 16.70bn litres in 2025; Durban customs accounted for 13.16bn.\n\nDurban and Lesedi connect coastal supply to inland customers. Their commercial opportunity depends on destination, route cost and access.',
 'Transport and sector demand: road-to-rail recovery, activity in mining/manufacturing/agriculture, and fleet efficiency can change fuel use.\n\nPower: Eskom’s own OCGT fuel use fell 40% in FY2025. Further reductions depend on sustained recovery and the wider generation mix.\n\nRefining: SAPREF and developments at Secunda, Natref and other plants could change domestic output and import requirements.',
 'Compare routes and customer access before assigning Vopak a share of the market.\n\nThe illustrative base gives Durban 2.63bn litres, including 1.32bn through Lesedi. This assumes 20% import capture and 50% onward routing; actual share remains unverified.\n\nCompare captured volumes with actual operating limits. Additional tanks require secured incremental demand, a proven capacity constraint and commercial returns.'
];
answer.forEach((v,c)=>tab.cells.set(1,c,v));
text(response,'SCR progress','Story sequence: baseline (pp4–9); demand and supply complications (pp10–14); competition and Vopak decisions (pp15–19).');
text(response,'Unified source footer','Department sales 2023; SARS customs 2025; Eskom FY2025; Manish DR08. Capture assumptions p16; operating sensitivities p17. Years and scopes differ. Actual customer share and investment returns remain open.');
response.speakerNotes.textFrame.setText('Current analytical response to HG’s original SCR on p2. Source material and underlying figures retained from v31; detailed demand, supply and source limitations appear on pp4–19. Capture: registered market_review.yaml; 20% of Durban customs gateway volume, 50% onward Lesedi routing, two turns monthly. Total scenario volumes, not incremental sales. Separate investment illustration retained in appendix.');
// Page references use the new order, while source-report page numbers stay intact.
const pageMap=Object.fromEntries(order.flatMap((x,i)=>typeof x==='number'?[[x,i+1]]:[]));
const references={
 6:[['pp40–43',`pp${pageMap[40]}–${pageMap[43]}`]],
 7:[['p42',`p${pageMap[42]}`],['p43',`p${pageMap[43]}`]],
 38:[['p36','p16']],42:[['p36','p16']]
};
for(const [oldPage,pairs] of Object.entries(references)){
 const slide=old[Number(oldPage)-1];
 for(const item of slide.shapes.items){
  const value=item.text?.toString();if(!value)continue;
  let updated=value;for(let i=0;i<pairs.length;i++)updated=updated.split(pairs[i][0]).join(`__REF${i}__`);
  for(let i=0;i<pairs.length;i++)updated=updated.split(`__REF${i}__`).join(pairs[i][1]);
  if(updated!==value)item.text=updated;
 }
}
old[37].tables.items[0].getCell(3,1).text.replace('p36','p16');
old[41].tables.items[0].getCell(2,2).text.replace('p36','p16');
// Remove the custom bars before applying package-native SmartArt.
const nav={main:{},appendix:{}};
for(let i=0;i<ordered.length;i++){
 const slide=ordered[i];
 for(const item of [...slide.shapes.items])if(['SCR 1','SCR 2','SCR 3','SCR 4'].includes(item.name))item.delete();
 const n=shape(slide,'Slide Number Placeholder');if(n)n.text=String(i+1);
 if(i>=1&&i<19)nav.main[i+1]=i<3?0:i<9?1:i<15?2:3;
 if(i>=20){const oldPage=order[i];nav.appendix[i+1]=oldPage===21?0:[5,6,7,19].includes(oldPage)||oldPage>=39?3:oldPage>=32?2:1;}
}
await fs.writeFile(qa+'/page_map.json',JSON.stringify({order,pageMap,nav},null,2));
await (await PresentationFile.exportPptx(p)).save(qa+'/body.pptx');
console.log('Exported',p.slides.items.length,'slides; 19-page core');
for(let i=0;i<19;i++){
 const png=await ordered[i].export({format:'png',scale:1});
 await fs.writeFile(qa+`/slide_${i+1}.png`,new Uint8Array(await png.arrayBuffer()));
}
