import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'../..');
const runtime='C:/Users/ITafr/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const {FileBlob,PresentationFile}=await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const qa=root+'/pptx/qa/story_v35';await fs.mkdir(qa,{recursive:true});
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
function rule(y){s.shapes.add({name:'SCR divider '+y,geometry:'rect',position:{left:48,top:y,width:1118,height:1},fill:'#D9D9D9',line:{fill:'none',width:0}});}
add('Situation label','SITUATION',48,174,166,30,18,true);
add('Situation answer','A large fuel market relies on substantial imports',225,170,941,30,22,true);
add('Situation evidence','2025 demand is estimated at 21.0bn litres: 8.9bn petrol and 12.1bn diesel, down from 21.9bn litres in 2023. Road use dominates, alongside mining, agriculture and power. With domestic production assumed at 5.8bn litres, gross import need is about 16.7bn litres.',225,206,941,65,18);
rule(278);
add('Complication label','COMPLICATION',48,294,170,30,18,true);
add('Complication answer','Sector growth supports demand, but five drivers reshape fuel flows through Durban',225,292,941,32,21,true);
const drivers=[
 ['Mining, manufacturing\nand agriculture','Production, exports and harvests drive equipment and freight demand; different sector growth paths produce different fuel-demand outcomes.'],
 ['Eskom and power\ngeneration','Eskom recovery reduces peaking and backup diesel at utilities, mines, factories and farms, while better electricity supply can support higher activity.'],
 ['Road-to-rail shift and\nvehicle efficiency','Moving mining, agricultural and manufactured goods from trucks to rail reduces road diesel use; vehicle efficiency further lowers fuel per unit of activity.'],
 ['Refineries and domestic\nfuel production','Higher operating output or refinery restarts could displace imports relative to the 5.8bn-litre production assumption; lower output increases import need.'],
 ['Matola and Walvis Bay','Alternative gateways could divert inland supply from Durban, depending on delivered cost, reliability and customer access.']
];
drivers.forEach(([label,body],i)=>{const y=335+i*39;add('Driver '+i,label,225,y,248,39,17,true);add('Driver implication '+i,body,483,y,683,39,17);});
rule(536);
add('Resolution label','RESOLUTION',48,553,170,30,18,true);
add('Resolution answer','Vopak should secure customer capture before expanding capacity',225,548,941,31,22,true);
add('Resolution evidence','Base-case imports remain about 16.6bn litres in 2030. Illustrative capture is 2.63bn litres through Durban, including 1.32bn onward through Lesedi within the same flow; this fits the preliminary working-tank screen.',225,584,941,43,18);
add('Resolution decision','Expansion requires secured incremental volumes and a demonstrated capacity shortfall.',225,631,941,25,18,true);
get('Unified source footer').position={left:48,top:662,width:1118,height:12};
get('Unified source footer').text='Source: analytical workbook v02 and market review. Demand is estimated; production and capture are planning assumptions. Product reconciliation remains open; Walvis Bay diversion is unquantified.';
s.speakerNotes.textFrame.setText(source+'\nFive agreed complication drivers retained. Walvis Bay is a qualitative route sensitivity with no quantified diversion assigned. All numerical values reuse the v34 story; no model changes.');
await (await PresentationFile.exportPptx(p)).save(qa+'/scr_source.pptx');
console.log('Horizontal SCR authored for replacement of page 2');
