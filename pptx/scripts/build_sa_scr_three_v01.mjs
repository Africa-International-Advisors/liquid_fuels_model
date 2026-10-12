import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'../..');
const runtime='C:/Users/ITafr/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const {FileBlob,PresentationFile}=await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const qa=root+'/pptx/qa/scr_three_v01';await fs.mkdir(qa,{recursive:true});
const p=await PresentationFile.importPptx(await FileBlob.load(root+'/pptx/output/delivered/supporting/archive/2026-10-11_cleanup/SA_Market_Story_2026-10-10_v30.pptx'));
const base=p.slides.items[3];const slides=[base.duplicate(),base.duplicate(),base.duplicate()];slides.forEach((s,i)=>s.moveTo(i));
const blue='#0A2373';
function add(s,name,value,x,y,w,h,size=20,bold=false,color='#11151A'){
 const t=s.shapes.add({name,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});t.text=value;t.text.style={typeface:'Lato',fontSize:size,bold,color,autoFit:'none'};return t;
}
function rule(s,name,x,y,w){s.shapes.add({name,geometry:'rect',position:{left:x,top:y,width:w,height:1},fill:'#C5C5C5',line:{fill:'none',width:0}});}
const titles=[
 'South Africa’s large fuel market relies on substantial imports',
 'Changes in demand, domestic supply and import routes could reduce flows through Durban',
 'Substantial imports sustain the market, while customer capture determines Vopak’s expansion'];
const sources=[
 'Department national sales; SARS 2025 trade; analytical workbook v02. 2025 demand is estimated; 5.8bn L production is a planning assumption. Gross import need includes exports and assumes no stock change.',
 'Stats SA sector activity and freight; Eskom Integrated Report 2025 p141; Sasol and Glencore production disclosures; Galp and Petromoc infrastructure disclosures. Detailed evidence: South Africa story v37 pp7–11.',
 'Analytical workbook v02 base scenario; market-sizing workbook and working-capacity assessment. Capture is illustrative; Lesedi is included within Durban flow. Contracted share, product balance and usable capacity remain to be established.'];
for(let i=0;i<3;i++){
 const s=slides[i];
 for(const item of [...s.shapes.items])if((item.position?.top>=150&&item.position?.top<640&&!['Unified source footer','Strictly Confidential footer','Slide Number Placeholder'].includes(item.name))||['SCR 1','SCR 2','SCR 3','SCR 4'].includes(item.name))item.delete();
 for(const t of [...s.tables.items])s.tables.deleteById(t.id);for(const im of [...s.images.items])im.delete();
 const get=name=>s.shapes.items.find(x=>x.name===name);
 get('Title 1').text=titles[i];get('Title 1').text.style={typeface:'Lato',fontSize:28,bold:true,color:'#000000',autoFit:'none'};
 get('Slide Number Placeholder').text=String(i+1);
 const footer=get('Unified source footer');footer.text=sources[i];footer.position={left:48,top:648,width:1118,height:25};footer.text.style={typeface:'Lato',fontSize:7.5,color:'#111111',autoFit:'none'};
 s.speakerNotes.textFrame.setText(sources[i]+'\nFigures reused from South Africa market story v37; no new model assumptions.');
}
const s=slides[0];
const metrics=[['21.0bn L','Estimated demand, 2025','8.9bn petrol and 12.1bn diesel'],['5.8bn L','Domestic production assumption','National planning baseline'],['16.7bn L','Gross import requirement','Broadly matches recorded imports']];
metrics.forEach(([v,label,detail],i)=>{const x=48+i*380;add(s,'S metric '+i,v,x,184,350,65,43,true,blue);add(s,'S label '+i,label,x,254,350,35,21,true,blue);add(s,'S detail '+i,detail,x,298,350,55,19);rule(s,'S metric rule '+i,x,360,350);});
add(s,'S demand heading','A substantial demand base',48,393,510,36,24,true,blue);
add(s,'S demand body','Road transport is the largest use. Mining, agriculture, manufacturing and power also contribute.\n\nDemand has eased from 21.9bn litres in 2023 to an estimated 21.0bn in 2025.',48,438,515,126,21);
add(s,'S route heading','Durban connects imports to inland customers',620,393,545,65,24,true,blue);
add(s,'S route body','Durban customs recorded 13.16bn litres of imports in 2025. The Durban–Lesedi route provides access to inland demand, subject to customer and logistics access.',620,470,545,100,21);
add(s,'S takeaway','South Africa has an established import market serving a large national fuel requirement.',48,594,1118,42,22,true,blue);
const c=slides[1];
add(c,'C left heading','Driver',48,179,330,32,21,true,blue);add(c,'C right heading','What changes for fuel demand and Durban flows',390,179,776,32,21,true,blue);rule(c,'C header rule',48,219,1118);
const drivers=[
 ['Sector activity','Mining, manufacturing and agriculture follow different growth paths, changing equipment and freight demand.'],
 ['Eskom recovery','More reliable electricity reduces peaking and backup diesel at utilities, mines, factories and farms.'],
 ['Road-to-rail and efficiency','Rail recovery and vehicle efficiency can reduce the fuel required to move goods. Rail growth alone does not prove road displacement.'],
 ['Domestic production','Higher refinery output or restarts could displace imports. Lower output would increase import dependence.'],
 ['Competing gateways','Matola provides an alternative route for inland customers. Delivered cost, reliability and access determine the volumes it can win.']];
drivers.forEach(([a,b],i)=>{const y=232+i*65;add(c,'C driver '+i,a,48,y,325,54,21,true,blue);add(c,'C effect '+i,b,390,y,776,55,20);rule(c,'C rule '+i,48,y+61,1118);});
add(c,'C takeaway','A large national import market does not automatically translate into growth for Vopak.',48,594,1118,44,22,true,blue);
const r=slides[2];
add(r,'R import number','16.6bn L',48,184,335,60,42,true,blue);
add(r,'R import label','2030 base-case imports',48,251,335,38,22,true,blue);
add(r,'R import explanation','Activity growth broadly offsets power, rail and efficiency reductions. Domestic production stays at the 5.8bn-litre planning baseline.',48,304,335,160,20);
add(r,'R capture number','2.63bn L',440,184,340,60,42,true,blue);
add(r,'R capture label','Illustrative Durban capture',440,251,340,60,22,true,blue);
add(r,'R capture explanation','Assumes 20% of Durban’s 2025 import pool. Includes 1.32bn litres onward through Lesedi within the same fuel flow.\n\nThis is a capture scenario, not an established customer share.',440,324,340,191,20);
add(r,'R investment header','Expansion follows\nsecured incremental flow',835,193,331,95,25,true,blue);
add(r,'R investment explanation','The illustrative flow fits the preliminary working-tank calculation.\n\nSecure additional customer volumes, establish usable capacity, and identify the constraint that investment would solve.',835,308,331,209,20);
rule(r,'R bottom rule',48,557,1118);
add(r,'R takeaway','Invest where secured additional volumes create a demonstrated capacity shortfall.',48,590,1118,48,23,true,blue);
await fs.writeFile(qa+'/page_map.json',JSON.stringify({nav:{main:{1:1,2:2,3:3},appendix:{}},keep_count:3},null,2));
await (await PresentationFile.exportPptx(p)).save(qa+'/body_untrimmed.pptx');
console.log('Three-page SCR authored');
