import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'../..');
const runtime='C:/Users/ITafr/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const {FileBlob,PresentationFile}=await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const qa=root+'/pptx/qa/story_v34';await fs.mkdir(qa,{recursive:true});
const p=await PresentationFile.importPptx(await FileBlob.load(root+'/pptx/output/delivered/supporting/archive/2026-10-11_cleanup/SA_Market_Story_2026-10-10_v30.pptx'));
const s=p.slides.items[3].duplicate();s.moveTo(0);
for(const item of [...s.shapes.items])if((item.position?.top>=150&&item.position?.top<640&&!['Unified source footer','Strictly Confidential footer','Slide Number Placeholder'].includes(item.name))||['SCR 1','SCR 2','SCR 3','SCR 4'].includes(item.name))item.delete();
for(const t of [...s.tables.items])s.tables.deleteById(t.id);
for(const im of [...s.images.items])im.delete();
const get=name=>s.shapes.items.find(x=>x.name===name);
get('Title 1').text='South Africa remains an import-led fuel market, making customer capture Vopak’s priority';
get('Title 1').text.style={typeface:'Lato',fontSize:28,bold:true,color:'#000000',autoFit:'none'};
get('Slide Number Placeholder').text='2';
const source='Source: analytical workbook v02 and registered market review. 2025 demand is estimated; 5.8bn L production is a planning assumption. Capture is illustrative; petrol/diesel reconciliation remains open.';
get('Unified source footer').text=source;
get('Unified source footer').text.style={typeface:'Lato',fontSize:7.5,color:'#111111',autoFit:'none'};
function add(name,text,x,y,w,h,size,bold=false){const t=s.shapes.add({name,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});t.text=text;t.text.style={typeface:'Lato',fontSize:size,bold,color:bold?'#0A2373':'#11151A',autoFit:'none'};}
const cols=[
 ['SITUATION','A large market relies on imports','2025 demand is an estimated 21.0bn litres: 8.9bn petrol and 12.1bn diesel. Road use dominates, alongside mining, agriculture and power.\n\nDemand has eased from 21.9bn litres in 2023. With domestic production assumed at 5.8bn litres, gross import need is about 16.7bn litres.'],
 ['COMPLICATION','Demand stabilises while supply and routes can shift','By 2030, activity growth adds 1.54bn litres, broadly offset by efficiency (0.79bn), power recovery (0.54bn) and rail shift (0.33bn).\n\nRefinery recovery could materially reduce imports. Matola competes for inland deliveries and changes the gateway serving demand.'],
 ['RESOLUTION','Vopak should secure capture before expanding','Base-case imports remain about 16.6bn litres in 2030, supporting an enduring import platform.\n\nIllustrative capture is 2.63bn litres through Durban, including 1.32bn onward through Lesedi. This fits the working-tank screen.\n\nSecure customer volumes and establish usable capacity before committing to expansion.']
];
cols.forEach((c,i)=>{const x=48+i*380;add('SCR section '+i,c[0],x,178,350,30,18,true);add('SCR answer '+i,c[1],x,220,350,65,23,true);add('SCR evidence '+i,c[2],x,304,350,273,19);});
add('SCR decision','Investment depends on contracted incremental flow and a demonstrated capacity constraint.',48,601,1118,39,20,true);
s.speakerNotes.textFrame.setText(source+'\nAll figures trace to v33 deep dives and analytical workbook v02. No new model assumptions. Unique flow counts Lesedi within Durban capture.');
await (await PresentationFile.exportPptx(p)).save(qa+'/scr_source.pptx');
console.log('SCR authored as slide 1 for insertion after the cover');
