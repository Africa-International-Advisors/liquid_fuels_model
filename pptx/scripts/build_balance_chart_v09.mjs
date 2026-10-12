import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'../..'),q=root+'/pptx/qa/evidence_v09';
await fs.mkdir(q,{recursive:true});
const rt='C:/Users/ITafr/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const {Presentation,PresentationFile}=await import(pathToFileURL(rt+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const data=JSON.parse(await fs.readFile(root+'/pptx/story/sa_evidence_additions_v08.json','utf8')).balance;
const v=n=>Number(data.find(x=>x.Measure===n)['Total bn L']);
const p=Presentation.create({slideSize:{width:1217,height:720}}),s=p.slides.add();
s.charts.add('bar',{position:{left:48,top:245,width:676.8,height:325},
 categories:['Supply','Consumption + exports'],
 series:[
 {name:'Production (assumed)',values:[v('Domestic production'),0],fill:'#6782B4'},
 {name:'Imports (recorded)',values:[v('Gross customs imports'),0],fill:'#0A2373'},
 {name:'Consumption (estimated)',values:[0,v('2025 demand')],fill:'#0A2373'},
 {name:'Exports (recorded)',values:[0,v('Customs exports')],fill:'#929292'}
 ].map(s=>({...s,valuesFormatCode:'0.00;-0.00;'})),
 barOptions:{direction:'column',grouping:'stacked',overlap:100,gapWidth:130},
 hasLegend:false,dataLabels:{showValue:true,position:'center',numberFormatCode:'0.00;-0.00;',textStyle:{fontFamily:'Lato',fontSize:15,color:'#FFFFFF'}},
 xAxis:{textStyle:{fontFamily:'Lato',fontSize:14}},yAxis:{numberFormatCode:'0',textStyle:{fontFamily:'Lato',fontSize:12}}});
await (await PresentationFile.exportPptx(p)).save(q+'/chart.pptx');
