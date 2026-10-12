import fs from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../..');
const rt='C:/Users/ITafr/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const {Presentation,PresentationFile}=await import(pathToFileURL(rt+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const d=JSON.parse(await fs.readFile(root+'/pptx/story/sa_evidence_additions_v08.json','utf8'));
const p=Presentation.create({slideSize:{width:1217,height:720}});
for(const [key,type] of [['efficiency','bar'],['refinery','line']]){
 const s=p.slides.add(), v=d[key];
 s.charts.add(type,{position:{left:48,top:245,width:676.8,height:310},categories:v.categories,
 series:v.series.map((a,i)=>({...a,fill:['#0A2373','#6782B4','#929292'][i],line:{fill:['#0A2373','#6782B4','#929292'][i],width:2.5},valuesFormatCode:'0.00'})),
 hasLegend:type==='line',legend:{position:'bottom'},barOptions:{direction:'column'},
 dataLabels:type==='bar'?{showValue:true,position:'outsideEnd',textStyle:{fontFamily:'Lato',fontSize:12},numberFormatCode:'0.00'}:undefined,
 xAxis:{textStyle:{fontFamily:'Lato',fontSize:12}},yAxis:{numberFormatCode:'0.0',textStyle:{fontFamily:'Lato',fontSize:12}}});
}
await (await PresentationFile.exportPptx(p)).save(root+'/pptx/qa/evidence_v08/new_charts.pptx');
