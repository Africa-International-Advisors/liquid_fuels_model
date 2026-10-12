import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'../..');
const runtime='C:/Users/ITafr/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const {FileBlob,PresentationFile}=await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const qa=root+'/pptx/qa/scr_six_v03';await fs.mkdir(qa,{recursive:true});
const p=await PresentationFile.importPptx(await FileBlob.load(root+'/pptx/output/delivered/supporting/archive/2026-10-11_cleanup/SA_Market_Story_2026-10-10_v30.pptx'));
const cover=p.slides.items[0].duplicate();const closing=cover.duplicate();
const base=p.slides.items[3];const slides=[base.duplicate(),base.duplicate(),base.duplicate(),base.duplicate()];[cover,...slides,closing].forEach((s,i)=>s.moveTo(i));
const blue='#0A2373';
function add(s,name,value,x,y,w,h,size=20,bold=false,color='#11151A'){
 const t=s.shapes.add({name,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});t.text=value;t.text.style={typeface:'Lato',fontSize:size,bold,color,autoFit:'none'};return t;
}
function rule(s,name,x,y,w){s.shapes.add({name,geometry:'rect',position:{left:x,top:y,width:w,height:1},fill:'#C5C5C5',line:{fill:'none',width:0}});}
const titles=[
 'South Africa’s large fuel market relies on substantial imports',
 'Changes in demand, domestic supply and import routes could reduce flows through Durban',
 'How the national fuel market translates into Vopak’s addressable volume',
 'Substantial imports sustain the market, while customer capture determines Vopak’s expansion'];
const sources=[
 'Department national sales; SARS 2025 trade; analytical workbook v02. 2025 demand is estimated; 5.8bn L production is a planning assumption. Gross import need includes exports and assumes no stock change.',
 'Stats SA sector activity and freight; Eskom Integrated Report 2025 p141; Sasol and Glencore production disclosures; Galp and Petromoc infrastructure disclosures. Detailed evidence: South Africa story v37 pp7–11.',
 'Framework: analytical workbook v02 and market-sizing workbook. Gateway shares and customer access require validation. Walvis Bay is a route to assess; no diversion volume is assigned. Stock build increases import need; stock draw reduces it.',
 'Analytical workbook v02 base scenario; market-sizing workbook and working-capacity assessment. Capture is illustrative; Lesedi is included within Durban flow. Contracted share, product balance and usable capacity remain to be established.'];
for(let i=0;i<4;i++){
 const s=slides[i];
 for(const item of [...s.shapes.items])if((item.position?.top>=150&&item.position?.top<640&&!['Unified source footer','Strictly Confidential footer','Slide Number Placeholder'].includes(item.name))||['SCR 1','SCR 2','SCR 3','SCR 4'].includes(item.name))item.delete();
 for(const t of [...s.tables.items])s.tables.deleteById(t.id);for(const im of [...s.images.items])im.delete();
 const get=name=>s.shapes.items.find(x=>x.name===name);
 get('Title 1').text=titles[i];get('Title 1').text.style={typeface:'Lato',fontSize:28,bold:true,color:'#000000',autoFit:'none'};
 get('Slide Number Placeholder').text=String(i+2);
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

function nativeTable(s,values,widths,top,height,size){
 const table=s.tables.add({rows:values.length,columns:values[0].length,left:48,top,width:1118,height,columnWidths:widths,values});
 table.styleOptions={headerRow:false,bandedRows:false};
 table.borders.assign({fill:'#D9D9D9',width:.4,style:'solid'});
 table.rows[0].height=42;
 for(let i=1;i<values.length;i++)table.rows[i].height=(height-42)/(values.length-1);
 for(let i=0;i<values.length;i++)for(let j=0;j<values[0].length;j++){
  const cell=table.getCell(i,j);cell.fill='#FFFFFF';cell.text.style={typeface:'Lato',fontFamily:'Lato',fontSize:size,bold:i===0||j===0,color:'#11151A',verticalAlignment:'top'};
 }
 return table;
}
const drivers=[
 ['Complication','Driver','What changes for fuel demand and Durban flows'],
 ['1  Demand','Sector activity','Mining, manufacturing and agriculture drive equipment and freight demand along different growth paths.'],
 ['','Eskom recovery','Reliable electricity reduces peaking and backup diesel at utilities, mines, factories and farms.'],
 ['','Road-to-rail','Freight shifted from trucks reduces road diesel use; net savings depend on rail traction.'],
 ['','Vehicle efficiency','Lower fuel consumption per kilometre reduces demand at a given level of road activity.'],
 ['2  Domestic supply','Refinery output and restarts','Higher production displaces imports; outages or lower output increase import dependence.'],
 ['3  Import routes','Ports and inland connections','Matola competes for inland supply. Assess Walvis Bay, pipeline access and delivered cost; Walvis Bay diversion is unquantified.']
];
nativeTable(c,drivers,[190,260,668],174,410,19);
add(c,'C takeaway','A large national import market does not automatically translate into growth for Vopak.',48,594,1118,44,22,true,blue);

const m=slides[2];
const framework=nativeTable(m,[
 ['Sizing step','Basis for the calculation','Market measure'],
 ['1  National demand','Petrol and diesel by end use: road, mining, manufacturing, agriculture and power. Apply activity, rail and efficiency drivers.','21.0bn L in 2025\nEstimated demand'],
 ['2  Import requirement','Demand − domestic production + exports + stock build (or − stock draw).','16.7bn L in 2025\nGross import need'],
 ['3  Ports and inland routes','Allocate imports across ports; assess pipeline, road and rail connections. Compare Durban with Matola and potential Walvis Bay routes.','Supply pool by catchment\nRoute shares to establish'],
 ['4  Addressable market','Size product and customer flows Durban and Lesedi can each serve, by catchment, logistics access and competing supply. Reconcile shared flows.','Addressable volume\nBy site, product and customer'],
 ['5  Achievable capture','Establish current Vopak throughput, volumes retained and additional customer volumes it can win. Assess competition and contracts; count shared fuel once.','Current + incremental capture\nBy site and customer'],
 ['6  Capacity and investment','Compare captured throughput with usable tanks, stock turns, receipt and dispatch capacity; identify the incremental constraint.','Capacity shortfall\nBasis for investment']
],[252,606,260],174,424,18);
add(m,'M takeaway','Steps 4–5 size Vopak’s opportunity: addressable customer flows, then achievable capture.',48,612,1118,32,20,true,blue);
const r=slides[3];

add(r,'R import number','16.6bn L',48,184,335,60,42,true,blue);
add(r,'R import label','2030 national imports',48,251,335,38,22,true,blue);
add(r,'R import explanation','Base-case imports across all gateways. Activity growth broadly offsets power, rail and efficiency reductions; domestic production stays at 5.8bn litres.',48,304,335,160,20);
add(r,'R capture number','2.63bn L',440,184,340,60,42,true,blue);
add(r,'R capture label','Illustrative Durban capture',440,251,340,60,22,true,blue);
add(r,'R capture explanation','Assumes 20% of Durban’s 2025 import pool. Includes 1.32bn litres onward through Lesedi within the same fuel flow.\n\nIllustrative share; no explicit deduction for Matola or Walvis Bay diversion.',440,324,340,191,20);
add(r,'R investment header','Expansion follows\nsecured incremental flow',835,193,331,95,25,true,blue);
add(r,'R investment explanation','The illustrative flow fits the preliminary working-tank calculation.\n\nSecure additional customer volumes, establish usable capacity, and identify the constraint that investment would solve.',835,308,331,209,20);
rule(r,'R bottom rule',48,557,1118);
add(r,'R takeaway','Invest where secured additional volumes create a demonstrated capacity shortfall.',48,590,1118,48,23,true,blue);

function coverText(slide,name,value){const sh=slide.shapes.items.find(x=>x.name===name);if(sh)sh.text=value;}
coverText(cover,'TextBox 4','South Africa\nliquid fuels\nmarket outlook');
coverText(cover,'TextBox 6','Demand, supply and routes — implications for Vopak');
coverText(cover,'TextBox 7','Durban and Lesedi | Market-sizing framework');
coverText(cover,'TextBox 8','11 October 2026');
coverText(cover,'TextBox 9','Planning estimates and illustrative capture. Customer access and usable capacity remain to be established.');
coverText(closing,'TextBox 4','Thank you');
coverText(closing,'TextBox 6','South Africa fuel market and Vopak opportunity');
coverText(closing,'TextBox 7','Discussion');
coverText(closing,'TextBox 8','11 October 2026');
coverText(closing,'TextBox 9','');
cover.speakerNotes.textFrame.setText('South Africa fuel market outlook. Sources and assumptions are stated on the analytical pages. Cover photograph: Royal Vopak, Terminal Durban.');
closing.speakerNotes.textFrame.setText('Closing discussion. Cover photograph: Royal Vopak, Terminal Durban.');

await fs.writeFile(qa+'/page_map.json',JSON.stringify({nav:{main:{2:1,3:2,4:3,5:3},appendix:{}},keep_count:6},null,2));
await (await PresentationFile.exportPptx(p)).save(qa+'/body_untrimmed.pptx');
console.log('Six-page SCR and market-sizing framework authored');
