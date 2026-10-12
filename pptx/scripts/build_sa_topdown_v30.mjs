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
const source=root+'/pptx/output/delivered/supporting/archive/2026-10-11_cleanup/SA_Market_Story_2026-10-10_v29.pptx';
const qa=root+'/pptx/qa/topdown_v30_r2';
await fs.mkdir(qa,{recursive:true});
const spec=JSON.parse(await fs.readFile(root+'/pptx/story/hg_scr_v30_2026_10_10.json','utf8'));
const p=await PresentationFile.importPptx(await FileBlob.load(source));
const old=[...p.slides.items];
const answer=old[15];
const hg=answer.duplicate();
hg.moveTo(1);
answer.moveTo(2);
if(p.slides.items[1].id!==hg.id||p.slides.items[2].id!==answer.id)throw new Error('Unexpected slide order');
function shape(slide,name){const s=slide.shapes.items.find(x=>x.name===name);if(!s)throw new Error('Missing '+name);return s;}
shape(hg,'Title 1').text=spec.title;
shape(hg,'Unified source footer').text=spec.footer;
shape(hg,'SCR progress').delete();
const t=hg.tables.items[0];
for(let c=0;c<3;c++){
 t.cells.set(0,c,spec.headers[c]);t.cells.set(1,c,spec.columns[c]);
}
hg.speakerNotes.textFrame.setText(spec.notes);
// Opening narrative uses the source's executive-summary navigation styling.
for(const s of [hg,answer]){
 for(let n=1;n<=4;n++){
  const tab=shape(s,'SCR '+n);tab.fill=n===1?'#0A2373':'#FAFAFA';
  tab.text.style={typeface:'Lato',fontSize:15,color:n===1?'#FFFFFF':'#0A2373',alignment:'center'};
 }
}
// Only explicit internal references are changed; published-source page numbers stay intact.
const replacements=new Map([
 [2,[['p35','p36']]],
 [4,[['pp39–42','pp40–43']]],
 [5,[['p41','p42'],['p42','p43']]],
 [16,[['pp6–15 and 20–34','pp8–17 and 21–35'],['p35','p36'],['pp39–43','pp40–44']]],
 [17,[['p39','p40']]],
 [37,[['p35','p36']]],
 [41,[['p35','p36']]]
]);
for(const [number,pairs] of replacements){
 const slide=old[number-1];
 const replaceText=txt=>{
  const strings=pairs.map(x=>x[0]);
  const rx=new RegExp(strings.map(x=>x.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('|'),'g');
  return txt.replace(rx,x=>pairs.find(v=>v[0]===x)[1]);
 };
 for(const s of slide.shapes.items){
  if(s.name==='Slide Number Placeholder')continue;
  const txt=s.text?.toString();if(txt){const updated=replaceText(txt);if(updated!==txt)s.text=updated;}
 }
}
for(const [page,row,col] of [[2,4,2],[37,3,1],[41,2,2]]){
 old[page-1].tables.items[0].getCell(row,col).text.replace('p35','p36');
}
for(let i=0;i<p.slides.items.length;i++){
 const num=p.slides.items[i].shapes.items.find(x=>x.name==='Slide Number Placeholder');
 if(num)num.text=String(i+1);
}
const pageMap=old.map((s,i)=>({old:i+1,new:p.slides.items.findIndex(x=>x.id===s.id)+1}));
await fs.writeFile(qa+'/page_map.json',JSON.stringify(pageMap,null,2));
const candidate=qa+'/candidate.pptx';
await (await PresentationFile.exportPptx(p)).save(candidate);
console.log('Exported',p.slides.items.length,'slides');
for(let i=0;i<p.slides.items.length;i++){
 const png=await p.slides.items[i].export({format:'png',scale:1});
 await fs.writeFile(qa+`/slide_${i+1}.png`,new Uint8Array(await png.arrayBuffer()));
}
await fs.mkdir(qa+'/final',{recursive:true});
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:qa+'/final/SA_Market_Story_2026-10-10_v30.pptx',
 pythonExecutable:runtime+'/python/python.exe',integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','11588750,6858000','--validate-bullet-geometry','--validate-heading-fit'],
 fontPolicy:{basis:'reference',families:['Lato'],referencePath:source,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(source)).digest('hex')},verifyArtifactToolImport:true,receiptPath:qa+'/validation.json'});
console.log(JSON.stringify(result).slice(0,800));
