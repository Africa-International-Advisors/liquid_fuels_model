// Presentation-only edits. Calculations are supplied by src/lfm/model outputs.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'../..');
const runtime='C:/Users/ITafr/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=runtime+'/node/node_modules';
const {FileBlob,PresentationFile}=await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const skill='C:/Users/ITafr/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
const spec=JSON.parse(await fs.readFile(root+'/pptx/story/sa_market_review_v28_2026_10_10.json','utf8'));
const build=root+'/pptx/qa/market_review_2026_10_10';
await fs.mkdir(build,{recursive:true});
const selected=process.argv[2];
for(const [key,d] of Object.entries(spec.decks)){
 if(selected && selected!==key)continue;
 const folder=build+'/'+key;await fs.mkdir(folder,{recursive:true});
 const source=root+'/'+d.source;
 const p=await PresentationFile.importPptx(await FileBlob.load(source));
 const snapshot=await p.inspect({kind:'slide,textbox,shape,table,image',maxChars:2000000});
 await fs.writeFile(folder+'/before.ndjson',snapshot.ndjson);
 const records=snapshot.ndjson.split('\n').filter(Boolean).map(x=>JSON.parse(x));
 for(const e of d.edits){
  const matches=records.filter(r=>r.slide===e.page && r.name===e.name && (e.row===undefined ? ['shape','textbox'].includes(r.kind) : r.kind==='table'));
  if(matches.length!==1)throw new Error('Non-unique edit '+JSON.stringify(e)+' matches '+matches.length);
  const target=p.resolve(matches[0].id);
  if(e.text!==undefined){
   if(e.row!==undefined)target.getCell(e.row,e.col).text.replace(e.original,e.text);
   else {
    const oldLines=e.original.split('\n'), newLines=e.text.split('\n');
    if(oldLines.length===newLines.length){
     for(let i=0;i<oldLines.length;i++)if(oldLines[i]!==newLines[i])target.text.replace(oldLines[i],newLines[i]);
    } else target.text=e.text;
   }
  }
  if(e.position)target.position={...target.position,...e.position};
 }
 for(const b of d.replacements){
  const slide=p.slides.items[b.page-1];
  // Remove the old body, preserving inherited branding and slide-owned headings.
  for(const item of [...slide.shapes.items]){
   const r=records.find(r=>r.id===item.id || (r.slide===b.page && r.name===item.name));
   const y=r?.bbox?.[1]??item.position?.top;
   if(y>=150 && y<640 && !['Title 1','Unified source footer','Strictly Confidential footer','Slide Number Placeholder'].includes(item.name))item.delete();
  }
  for(const img of [...slide.images.items])img.delete();
  if(b.page===35 && key==='story'){
   // Existing table has the same 4x3 structure and keeps its native template styling.
   const tab=slide.tables.items[0];
   const vals=[b.headers,...b.rows];
   for(let r=0;r<vals.length;r++)for(let c=0;c<vals[0].length;c++)tab.cells.set(r,c,vals[r][c]);
  } else {
   for(const t of [...slide.tables.items])t.delete();
   const values=[b.headers,...b.rows];
   const t=slide.tables.add({rows:values.length,columns:values[0].length,left:48,top:174,width:1118.4,height:b.height*4/3,columnWidths:b.widths.map(x=>x*4/3),values});
   t.styleOptions={headerRow:false,bandedRows:false};
   t.borders.assign({fill:'#DDDDDD',width:0.4,style:'solid'});
   for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
    const cell=t.getCell(r,c);cell.fill=r===0?'#F5F5F5':'#FFFFFF';
    cell.text.style={fontFamily:'Lato',typeface:'Lato',fontSize:r===0?17:18,bold:r===0||c===0,color:c===0?'#0B2475':'#202020',verticalAlignment:'middle'};
   }
  }
  const y=key==='story'&&b.page===35?640:174+b.height*4/3+22;
  const explanation=slide.shapes.add({name:'Review interpretation',geometry:'textbox',position:{left:48,top:y,width:1118,height:key==='story'&&b.page===35?38:64},fill:'none',line:{fill:'none',width:0}});
  explanation.text=b.explanation;explanation.text.style={typeface:'Lato',fontSize:15,color:'#202020',autoFit:'none'};
  if(key==='story'&&b.page===35){
   // Shorten the original table to leave the interpretation above the source footer.
   const t=slide.tables.items[0];for(let i=0;i<4;i++)t.rows[i].height=i===0?40:116;
   explanation.position={left:48,top:583,width:1118,height:56};
  }
 }
 for(const item of d.row_heights??[]){
  const rec=records.find(r=>r.kind==='table'&&r.slide===item.page&&r.name===item.name);
  const table=p.resolve(rec.id);item.heights.forEach((h,i)=>table.rows[i].height=h);
 }
 for(const [page,note] of Object.entries(d.notes)){
  const slide=p.slides.items[Number(page)-1];
  // Preserve original notes and append the updated evidence and qualifications.
  slide.speakerNotes.textFrame.setText('10 October revision\n'+note);
 }
 const candidate=folder+'/candidate.pptx';
 await (await PresentationFile.exportPptx(p)).save(candidate);
 console.log(key,'exported',p.slides.items.length);
 for(let i=0;i<p.slides.items.length;i++){
  const png=await p.slides.items[i].export({format:'png',scale:1});
  await fs.writeFile(folder+`/slide_${i+1}.png`,new Uint8Array(await png.arrayBuffer()));
 }
 const release=folder+'/final_2';
 await fs.mkdir(release,{recursive:true});
 const finalPath=release+'/'+d.output+'.pptx';
 const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath,
  pythonExecutable:runtime+'/python/python.exe',
  integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',
  layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',
  layoutArgs:['--expected-slide-size-emu','11588750,6858000','--validate-bullet-geometry','--validate-heading-fit'],
  fontPolicy:{basis:'reference',families:['Lato'],referencePath:source,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(source)).digest('hex')},
  verifyArtifactToolImport:true,receiptPath:folder+'/validation_2.json'});
 console.log(key,'finalized',JSON.stringify(result).slice(0,1500));
}
