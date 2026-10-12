import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'../..');
const runtime='C:/Users/ITafr/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=runtime+'/node/node_modules';
const skill='C:/Users/ITafr/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations';
const {FileBlob,PresentationFile}=await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
const source=root+'/pptx/output/delivered/supporting/archive/2026-10-11_cleanup/SA_Market_Story_2026-10-10_v28.pptx';
const qa=root+'/pptx/qa/partner_scr_v29';
await fs.mkdir(qa,{recursive:true});
const spec=JSON.parse(await fs.readFile(root+'/pptx/story/sa_partner_scr_v29_2026_10_10.json','utf8'));
const p=await PresentationFile.importPptx(await FileBlob.load(source));
const snapshot=await p.inspect({kind:'slide,textbox,shape,table,image',maxChars:2000000});
const records=snapshot.ndjson.split('\n').filter(Boolean).map(JSON.parse);
const slide=p.slides.items[15];
for(const item of [...slide.shapes.items]){
 const r=records.find(x=>x.id===item.id || (x.slide===16&&x.name===item.name));
 const y=r?.bbox?.[1]??item.position?.top;
 if(y>=150&&y<640&&!['Unified source footer','Strictly Confidential footer','Slide Number Placeholder'].includes(item.name))item.delete();
}
for(const t of [...slide.tables.items])t.delete();
for(const im of [...slide.images.items])im.delete();
for(const [name,value] of [['Title 1',spec.title],['Unified source footer',spec.footer]]){
 const r=records.find(x=>x.slide===16&&x.name===name);
 const shape=p.resolve(r.id);shape.text=value;
}
// Brand colours are inherited from the source's Vopak theme; fonts match its named layout.
const brand={accent_primary:'#0A2373',ink:'#11151A',paper:'#FFFFFF',rule:'#D9D9D9'};
const t=slide.tables.add({rows:2,columns:3,left:48,top:173,width:1118,height:382,columnWidths:[372.7,372.7,372.6],values:[spec.headers,spec.columns]});
t.styleOptions={headerRow:false,bandedRows:false};
t.rows[0].height=44;t.rows[1].height=338;
t.borders.assign({fill:brand.paper,width:0,style:'solid'});
for(let r=0;r<2;r++)for(let c=0;c<3;c++){
 const cell=t.getCell(r,c);cell.fill=brand.paper;
 cell.text.style={typeface:'Lato',fontFamily:'Lato',fontSize:r===0?18:18,bold:r===0,color:r===0?brand.accent_primary:brand.ink,verticalAlignment:'top'};
}
const progress=slide.shapes.add({name:'SCR progress',geometry:'textbox',position:{left:48,top:584,width:1118,height:55},fill:'none',line:{fill:'none',width:0}});
progress.text=spec.progress;progress.text.style={typeface:'Lato',fontSize:17,color:brand.accent_primary,autoFit:'none'};
slide.speakerNotes.textFrame.setText(spec.notes);
const candidate=qa+'/candidate.pptx';
await (await PresentationFile.exportPptx(p)).save(candidate);
for(let i=0;i<p.slides.items.length;i++){
 const png=await p.slides.items[i].export({format:'png',scale:1});
 await fs.writeFile(qa+`/slide_${i+1}.png`,new Uint8Array(await png.arrayBuffer()));
}
await fs.mkdir(qa+'/final',{recursive:true});
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:qa+'/final/SA_Market_Story_2026-10-10_v29.pptx',
 pythonExecutable:runtime+'/python/python.exe',integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','11588750,6858000','--validate-bullet-geometry','--validate-heading-fit'],
 fontPolicy:{basis:'reference',families:['Lato'],referencePath:source,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(source)).digest('hex')},verifyArtifactToolImport:true,receiptPath:qa+'/validation.json'});
console.log(JSON.stringify(result).slice(0,1000));
