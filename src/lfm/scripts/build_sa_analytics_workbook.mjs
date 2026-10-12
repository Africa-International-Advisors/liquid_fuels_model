// Presentation only: the model's cell graph supplies all calculations.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'../../..');
const {Workbook,SpreadsheetFile}=await import(pathToFileURL('C:/Users/ITafr/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const directed=process.argv.includes('--planning-case');
const out=root+'/output/delivered/sa_analytics_2026_10_11'+(directed?'_v02':'');
const qa=root+'/output/sa_analytics_build'+(directed?'_v02':'');await fs.mkdir(qa,{recursive:true});
const model=JSON.parse(await fs.readFile(out+'/analytics.json','utf8'));
const wb=Workbook.create();const sheets={};
for(const name of Object.keys(model.sheets))sheets[name]=wb.worksheets.add(name);
const navy='#0B2475';
for(const [name,tab] of Object.entries(model.sheets)){
 const s=sheets[name],last=tab.rows.length+4,end=String.fromCharCode(64+tab.headers.length);
 s.showGridLines=false;
 const used=s.getRange(`A1:${end}${last}`);used.format.font={name:'Arial',size:10,color:'#202020'};
 used.format.verticalAlignment='top';used.format.rowHeight=42;
 tab.widths.forEach((width,i)=>s.getRange(`${String.fromCharCode(65+i)}1:${String.fromCharCode(65+i)}${last}`).format.columnWidth=Math.min(width,75));
 s.getRange('A1').values=[[tab.title]];s.getRange('A1').format.font={name:'Arial',size:15,bold:true,color:navy};s.getRange('A1').format.rowHeight=27;
 s.getRange('A2').values=[['11 October 2026. Estimates and sensitivities; sources and assumptions are retained.']];s.getRange('A2').format.rowHeight=23;
 s.getRange(`A4:${end}4`).values=[tab.headers];s.getRange(`A4:${end}4`).format={fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:40};
 s.getRange(`A5:${end}${last}`).values=tab.rows.map(row=>row.map(cell=>typeof cell==='object'&&cell!==null?null:cell));
 for(let i=0;i<tab.rows.length;i++)for(let j=0;j<tab.rows[i].length;j++){
   const cell=tab.rows[i][j],range=s.getCell(i+4,j);
   if(cell&&typeof cell==='object'){range.formulas=[[cell.formula]];range.setNumberFormat('0.000;[Red](0.000);0.000');}
   else if(typeof cell==='number'&&j>0){range.setNumberFormat('0.000;[Red](0.000);0.000');if(name==='Assumptions'){range.format.fill='#FFF0CC';range.format.font.color='#0000FF';}}
 }
 s.getRange(`A5:A${last}`).format.wrapText=true;
 s.getRange(`${end}5:${end}${last}`).format.wrapText=true;
 if(name==='Summary'){s.getRange(`A5:${end}${last}`).format.rowHeight=57;}
 if(name==='Assumptions'||name==='Evidence'){s.getRange(`C5:C${last}`).format.wrapText=true;s.getRange(`A5:${end}${last}`).format.rowHeight=65;s.freezePanes.freezeRows(4);}
 if(name==='Segments'||name==='Plant supply'||name==='Balance'||name==='Scenarios'||name==='Driver bridge'){s.getRange(`A5:${end}${last}`).format.rowHeight=72;}
 if(name==='Mozambique'){s.getRange(`C5:C${last}`).format.wrapText=true;s.getRange(`A5:${end}${last}`).format.rowHeight=72;}
 if(name==='Plant supply')s.getRange('C5:D10').setNumberFormat('0.0%');
 if(name==='Mozambique')s.getRange('B5:B11').setNumberFormat('#,##0');
 if(name==='Assumptions')for(let i=0;i<tab.rows.length;i++)if(tab.rows[i][2]==='fraction')s.getRange(`B${i+5}`).setNumberFormat('0.0%');
 if(name==='Demand history')s.getRange('A5:A17').setNumberFormat('0');
 if(name==='Balance'){s.getRange('A10:E10').format.fill='#FFF0CC';s.getRange('A10:E10').format.font.bold=true;}
}
// Editable native chart, separated from the chronological data table.
const history=sheets['Demand history'];
history.getRange('A23:C23').values=[['Year','Petrol bn L','Diesel bn L']];
for(let i=0;i<13;i++){
 const r=24+i,src=5+i;
 history.getRange(`A${r}`).values=[[String(model.sheets['Demand history'].rows[i][0])]];
 history.getRange(`B${r}:C${r}`).formulas=[[`=B${src}`,`=C${src}`]];
}
history.getRange('A23:C36').format.font={name:'Arial',size:10};history.getRange('B24:C36').setNumberFormat('0.00');
const chart=history.charts.add('line',history.getRange('A23:C36'));chart.title='Petrol and diesel demand (bn L); 2024–25 estimated';chart.setPosition('G4','P20');chart.yAxis={numberFormatCode:'0.0',numberFormatSourceLinked:false};
chart.series.items[0].fill='#0B2475';chart.series.items[1].fill='#607DB4';
// Check every calculated value against the model's single calculation graph.
let maxDifference=0;const mismatches=[];
for(const [name,tab] of Object.entries(model.sheets)){
 const vals=sheets[name].getRange(`A5:${String.fromCharCode(64+tab.headers.length)}${tab.rows.length+4}`).values;
 for(let i=0;i<tab.rows.length;i++)for(let j=0;j<tab.rows[i].length;j++){
  const expected=tab.rows[i][j];if(!expected||typeof expected!=='object')continue;
  const actual=vals[i][j],diff=Math.abs(actual-expected.value);maxDifference=Math.max(maxDifference,diff);
  if(typeof actual!=='number'||diff>1e-8*Math.max(1,Math.abs(expected.value)))mismatches.push({name,row:i+5,col:j+1,actual,expected:expected.value});
 }
}
await fs.writeFile(qa+'/calculation_comparison.json',JSON.stringify({maxDifference,mismatches},null,2));
if(mismatches.length)throw new Error('Workbook/model differences: '+JSON.stringify(mismatches.slice(0,5)));
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'Formula error scan'});
await fs.writeFile(qa+'/formula_scan.ndjson',errors.ndjson);
await fs.writeFile(qa+'/summary.ndjson',(await wb.inspect({kind:'table',range:'Summary!A4:D14',include:'values,formulas',tableMaxRows:15,tableMaxCols:4})).ndjson);
for(const [name,tab] of Object.entries(model.sheets)){
 const range=`A1:${String.fromCharCode(64+tab.headers.length)}${Math.min(tab.rows.length+4,15)}`;
 const blob=await wb.render({sheetName:name,range,scale:1,format:'png'});
 await fs.writeFile(qa+'/'+name.replaceAll(' ','_')+'.png',new Uint8Array(await blob.arrayBuffer()));
}
const chartPreview=await wb.render({sheetName:'Demand history',range:'G4:P20',scale:1,format:'png'});
await fs.writeFile(qa+'/demand_chart.png',new Uint8Array(await chartPreview.arrayBuffer()));
const target=out+'/SA_Fuel_Analytics_2025_Baseline_2026-10-11_'+(directed?'v02':'v01')+'.xlsx';
await (await SpreadsheetFile.exportXlsx(wb)).save(target);
console.log(JSON.stringify({target,maxDifference,sheets:Object.keys(sheets).length}));
