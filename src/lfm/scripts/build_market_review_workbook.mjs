// Excel presentation of the governed market_review outputs. Formulas expose the screen for review.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'../../..');
const {Workbook,SpreadsheetFile}=await import(pathToFileURL('C:/Users/ITafr/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const m=JSON.parse(await fs.readFile(root+'/output/delivered/market_review_2026_10_10/market_review.json','utf8'));
const w=Workbook.create();
const s=w.worksheets.add('Capture cases'),c=w.worksheets.add('Market context'),o=w.worksheets.add('Operations'),n=w.worksheets.add('Sources and gaps');
const navy='#0B2475',yellow='#FFF0CC';
const put=(sh,cell,value)=>sh.getRange(cell).values=[[value]];
const fx=(sh,cell,value)=>sh.getRange(cell).formulas=[[value]];
function base(sh,title,widths,end=30){
 sh.showGridLines=false;sh.getRange(`A1:H${end}`).format.font={name:'Arial',size:10,color:'#202020'};
 sh.getRange(`A1:H${end}`).format.verticalAlignment='top';
 widths.forEach((x,i)=>sh.getRange(`${String.fromCharCode(65+i)}1:${String.fromCharCode(65+i)}${end}`).format.columnWidth=x);
 put(sh,'A1',title);sh.getRange('A1').format.font={name:'Arial',size:16,bold:true,color:navy};sh.getRange('A1').format.rowHeight=30;
}
function header(sh,range,values){sh.getRange(range).values=[values];sh.getRange(range).format={fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:32};}
function note(sh,row,text,end='H'){sh.mergeCells(`A${row}:${end}${row}`);put(sh,`A${row}`,text);sh.getRange(`A${row}:${end}${row}`).format={wrapText:true,rowHeight:40,font:{name:'Arial',size:10,color:'#52606D'}};}
function input(sh,range,percent=false){sh.getRange(range).format.fill=yellow;sh.getRange(range).format.font.color='#0000FF';if(percent)sh.getRange(range).setNumberFormat('0%');}
base(c,'South Africa market context',[43,18,18,18,20,54],23);
header(c,'A4:F4',['Measure','Petrol bn L','Diesel bn L','Total bn L','Period','Definition and source']);
const contexts=[['National sales',m.national_sales,'2023','Department of Mineral and Petroleum Resources. Sales proxy for demand.'],['National gross imports',m.gross_imports,'2025','SARS customs, all offices. Gross imports are distinct from consumption.'],['National exports',m.exports,'2025','SARS customs, all offices.'],['National net imports',m.net_imports,'2025','Gross imports less exports. Not a production or consumption estimate.'],['Durban customs imports',m.durban_customs,'2025','Office of clearance is a gateway proxy, not terminal receipts.'],['KwaZulu-Natal sales',m.catchments.KZN,'2022','Provincial demand context. Not a Durban minimum addressable market.'],['Gauteng sales',m.catchments.Gauteng,'2022','Nested within the six inland provinces. Not an import requirement.'],['Six inland provinces',m.catchments['Six inland provinces'],'2022','GP, MP, FS, NW, LP, NC. Includes domestic supply and other gateways.']];
for(let i=0;i<contexts.length;i++){const [label,v,period,desc]=contexts[i],r=i+5;c.getRange(`A${r}:F${r}`).values=[[label,v.petrol,v.diesel,null,period,desc]];fx(c,`D${r}`,`=SUM(B${r}:C${r})`);}
c.getRange('B5:D12').setNumberFormat('0.000');c.getRange('A5:F12').format.wrapText=true;c.getRange('A5:F12').format.rowHeight=50;
for(const [col,p] of [['B','petrol'],['C','diesel']])fx(c,`${col}8`,`=${col}6-${col}7`);
note(c,15,'Years remain distinct. The 2025 Durban import pool, 2022 catchments and 2023 national demand cannot be added or treated as endpoints of one market range.','F');
note(c,17,'The previous 8.88bn litre inland-flow residual mixed 2025 imports with 2022 KZN sales. It does not establish inland, road or rail movements.','F');
base(o,'Working tankage and pipeline context',[36,18,18,18,18,55],27);
header(o,'A4:F4',['Site','Working m³','Estimated m³','Base turns/month','Handling bn L/year','Scope']);
for(let i=0;i<2;i++){const site=['Durban','Lesedi'][i],r=i+5,v=m.sites[site];o.getRange(`A${r}:F${r}`).values=[[site,v.working_m3,v.estimated_component_m3,v.monthly_turns.base,null,site==='Durban'?'Estimated petrol/diesel subset, not 360,246 m³ gross tankage.':'88,000 m³ documented plus 36,000 m³ estimated for newer tanks.']];fx(o,`E${r}`,`=IF(OR(B${r}<0,D${r}<0),NA(),B${r}*D${r}*12/1000000)`);}
o.getRange('B5:C6').setNumberFormat('#,##0');o.getRange('D5:E6').setNumberFormat('0.00');input(o,'B5:B6');input(o,'D5:D6');o.getRange('A5:F6').format.wrapText=true;o.getRange('A5:F6').format.rowHeight=55;
header(o,'A9:F9',['Site','Low turns','Base turns','High turns','Low bn L','High bn L']);
for(let i=0;i<2;i++){const site=['Durban','Lesedi'][i],r=i+10,v=m.sites[site];o.getRange(`A${r}:F${r}`).values=[[site,v.monthly_turns.low,null,v.monthly_turns.high,null,null]];fx(o,`C${r}`,`=D${i+5}`);fx(o,`E${r}`,`=$B${i+5}*B${r}*12/1000000`);fx(o,`F${r}`,`=$B${i+5}*D${r}*12/1000000`);}
o.getRange('B10:F11').setNumberFormat('0.00');input(o,'B10:B11');input(o,'D10:D11');
header(o,'A14:D14',['MPP shared pipeline','Value','Unit','Period']);
o.getRange('A15:D17').values=[['Average use',105,'ML/week','FY2025 actual'],['Capacity',148,'ML/week','FY2025 report'],['Annualisation',52,'weeks','Arithmetic convention']];
put(o,'A18','Annualised use');fx(o,'B18','=B15*B17/1000');put(o,'C18','bn L/year');
put(o,'A19','Annualised capacity');fx(o,'B19','=B16*B17/1000');put(o,'C19','bn L/year');
put(o,'A20','Use / capacity');fx(o,'B20','=B15/B16');o.getRange('B20').setNumberFormat('0.0%');
put(o,'A21','Arithmetic unused capacity');fx(o,'B21','=B19-B18');put(o,'C21','bn L/year');o.getRange('B18:B19').setNumberFormat('0.000');o.getRange('B21').setNumberFormat('0.000');
note(o,24,'Tank arithmetic is a sensitivity, not a guaranteed engineering ceiling. The shared pipeline’s unused average capacity is not Vopak entitlement. Access, product allocation, peaks and downtime remain unverified.','F');
base(s,'Vopak capture sensitivities',[20,19,18,21,21,21,21,24],25);
note(s,2,'Illustrative annual volumes using the 2025 Durban import gateway. Yellow cells are editable assumptions. Low/base/high are sensitivity labels, not probabilities.');
put(s,'A4','Durban gateway, bn L');fx(s,'B4',"='Market context'!D9");s.getRange('B4').setNumberFormat('0.000');
put(s,'D4','Onward share to Lesedi');put(s,'F4',m.scenarios[1].lesedi_routing_fraction);input(s,'F4',true);
header(s,'A7:H7',['Case','Gateway capture','Requested Durban bn L','Screened Durban bn L','Lesedi bn L','Unique flow bn L','Gross site movements bn L','Tank screen reduction bn L']);
for(let i=0;i<3;i++){const r=i+8,v=m.scenarios[i];s.getRange(`A${r}:H${r}`).values=[[v.case,v.gateway_capture_fraction,null,null,null,null,null,null]];fx(s,`C${r}`,`=IF(OR(B${r}<0,B${r}>1),NA(),$B$4*B${r})`);fx(s,`D${r}`,`=MIN(C${r},'Operations'!$E$5)`);fx(s,`E${r}`,`=IF(OR($F$4<0,$F$4>1),NA(),MIN(D${r}*$F$4,'Operations'!$E$6))`);fx(s,`F${r}`,`=D${r}`);fx(s,`G${r}`,`=SUM(D${r}:E${r})`);fx(s,`H${r}`,`=C${r}-D${r}`);}
input(s,'B8:B10',true);s.getRange('C8:H10').setNumberFormat('0.00');s.getRange('A8:H10').format.rowHeight=30;
note(s,13,'Lesedi is a subset of captured Durban flow in this screen. Gross site movements count handling at both terminals; unique flow counts the imported fuel once.');
note(s,15,'The default 10/20/30% capture and 50% routing assumptions are authored settings. Customer commitments, contestable volumes and terminal/pipeline access have not been established.');
note(s,17,'Other-terminal and domestic receipts into Lesedi are excluded. Existing throughput is unknown, so these are total scenario volumes and cannot be presented as incremental volume or revenue.');
note(s,19,'Operations shows working-tank sensitivities. At the default two turns/month, Durban’s estimated subset limits the high case to 3.504bn L. Actual engineering limits may differ.');
base(n,'Sources and remaining inputs',[30,69,69],23);
header(n,'A4:C4',['Input / issue','Evidence or assumption','Source / next action']);
const rows=[['National and provincial sales','2023 national and 2022 provincial observations. Later provincial estimates excluded from this screen.','DMPR sales publications, as consolidated by Manish. https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/media_SAVolumes.html'],['Customs trade','2025 petrol and diesel, litre-reported codes. Office is a gateway proxy.','SARS customs as consolidated in Manish’s master workbook. Preserve product and unit exclusions.'],['Working capacity and turns','Durban 146,000 m³ estimated subset; Lesedi 124,000 m³ partly estimated. Turns are proposed.','NERSA licence documents and Vopak statements in Manish’s site assumptions. DR03 client confirmation required.'],['Pipeline','FY2025 actual 105:148 ML/week. Annualisation uses 52 weeks.','Transnet Pipelines 2025, printed page 8. https://www.transnet.net/getFile.ashx?id=6121'],['Capture and routing','10/20/30% gateway capture; 50% to Lesedi. Authored sensitivities, not observed shares.','Replace with DR02/05 customer, contract and linked-transfer evidence.'],['Current throughput','Not supplied. No current market share or incremental-volume claim.','DR02/05: 36 months of receipts/dispatches, products, linked transfers and destinations. Nigel coordinates.'],['Operating limits','Tankage and average pipeline capacity do not prove access or achievable dispatch.','DR03/04: product allocations, committed tanks, peaks, downtime, injection and dispatch rights.'],['Revenue and investment','No tariff, revenue or investment result is calculated in this workbook.','DR06: contracts, included throughput, excess charges, costs, capex, timing, tax and working capital.'],['Full data-gap register','The companion master review retains all 63 review items across nine requests.','Master_data_book_review_2026-10-10_v01.xlsx: Request coverage and Gap register.'],['Investment illustration','Story pp39–42 use separate catchment/capture/commercial assumptions. Existing working capacity now aligns to 124,000 m³.','Its 1.25/1.50 turns and rental-allocation assumptions differ from this two-turn capture screen. No client approval inferred.']];
n.getRange('A5:C14').values=rows;n.getRange('A5:C14').format.wrapText=true;n.getRange('A5:C14').format.rowHeight=75;
const out=root+'/output/delivered/Vopak_Market_Sizing_2026-10-10_v01.xlsx';
await (await SpreadsheetFile.exportXlsx(w)).save(out);
const preview=root+'/output/review_2026_10_10/story_update';
for(const [sh,range] of [[s,'A1:H20'],[c,'A1:F18'],[o,'A1:F25'],[n,'A1:C14']]){
 const b=await w.render({sheetName:sh.name,range,scale:1,format:'png'});await fs.writeFile(preview+'/'+sh.name.replaceAll(' ','_')+'.png',new Uint8Array(await b.arrayBuffer()));
}
console.log((await w.inspect({kind:'table',range:"'Capture cases'!A7:H10",include:'values,formulas',tableMaxRows:4,tableMaxCols:8})).ndjson);
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!',options:{useRegex:true,maxResults:20}})).ndjson);
console.log(out);
