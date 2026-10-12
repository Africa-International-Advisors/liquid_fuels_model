"""Derive the new builder from the established template-aware pipeline."""
from pathlib import Path
r=Path(__file__).resolve().parents[2];scripts=r/'pptx/scripts'
s=(scripts/'build_sa_story_v33.mjs').read_text()
s=s.replace('v33','v36').replace('20:old[1]','19:old[1]')
s=s.replace("if(d.kind==='table'){", "if(d.kind==='scr'){\n  drawScr(s);\n }else if(d.kind==='table'){")
s=s.replace("const height=d.page===2?400:380", "const height=d.page===22?400:380")
s=s.replace("d.page===2?43:42", "d.page===22?43:42")
s=s.replace("cell.fill=r===0?'#F5F5F5':'#FFFFFF'", "cell.fill='#FFFFFF'")
s=s.replace("color:r===0||c===0?'#0A2373':'#11151A'", "color:'#11151A'")
s=s.replace("top:190,width:770,height:360", "top:236,width:770,height:310")
s=s.replace("d.page===10?'Million tonnes'", "d.page===9?'Million tonnes'")
s=s.replace("55,164,750,25,14", "55,208,750,23,13")
s=s.replace("850,185,310,48,22", "850,173,310,37,21")
s=s.replace("850,245,310,305,18", "850,230,310,330,d.page===3?17:18")
s=s.replace("const colors=['#0A2373','#6782B4','#868686'];", "const colors=['#0A2373','#6782B4','#868686'];\n  add(s,'Chart heading',d.chartHeading??'Demand trend',48,173,760,37,21,true,'#0A2373');\n  rule(s,'Chart header rule',48,210,770,1);rule(s,'Insight header rule',850,210,316,1);rule(s,'Chart divider',832,173,1,380);")
s=s.replace("add(s,'Story implication',d.takeaway", "if(d.kind!=='scr')add(s,'Story implication',d.takeaway")
s=s.replace("if(i>=1&&i<19)nav.main[i+1]=i<3?0:i<7?1:i<16?2:3;", "if(i>=1&&i<18)nav.main[i+1]=i<3?0:i<6?1:i<15?2:3;")
s=s.replace("if(i>=19)nav.appendix[i+1]=i===19?0:2;", "if(i>=18)nav.appendix[i+1]=i===18?0:2;")
s=s.replace('keep_count:22','keep_count:23').replace('22-page','23-page')
insert="""
function rule(s,name,x,y,w,h){s.shapes.add({name,geometry:'rect',position:{left:x,top:y,width:w,height:h},fill:'#B7B7B7',line:{fill:'none',width:0}});}
function drawScr(s){
 const blue='#0A2373';
 add(s,'S label','SITUATION',48,170,165,28,18,true,blue);
 add(s,'S answer','A large fuel market relies on substantial imports',225,166,820,30,22,true,blue);
 add(s,'S reference','pp3–6, 22',1080,170,90,28,15,true,blue);
 add(s,'S body','2025 demand is estimated at 21.0bn litres: 8.9bn petrol and 12.1bn diesel, down from 21.9bn in 2023. Road use dominates. At the assumed 5.8bn litres of domestic production, gross import need is about 16.7bn litres.',225,203,941,57,18);
 rule(s,'S divider',48,269,1118,1);
 add(s,'C label','COMPLICATION',48,280,170,28,18,true,blue);
 add(s,'C answer','Sector growth supports demand, but fuel use, supply and routes are changing',225,279,810,30,20,true,blue);
 add(s,'Deep dive label','Deep dive',1080,279,90,28,15,true,blue);
 const rows=[
 ['Mining, manufacturing\\nand agriculture','Production, exports and harvests drive diesel use in equipment and freight; sector growth paths differ.','p6'],
 ['Eskom and power\\ngeneration','Recovery reduces peaking and backup diesel at utilities, mines, factories and farms, while supporting activity.','pp7–8'],
 ['Road-to-rail shift and\\nvehicle efficiency','Moving goods from trucks to rail and improving vehicle efficiency reduce fuel consumed per unit of activity.','pp9–10, 21'],
 ['Refineries and domestic\\nfuel production','Higher output or restarts displace imports relative to the 5.8bn-litre assumption; lower output increases import need.','pp11–13'],
 ['Matola and Walvis Bay','Competing gateways could divert inland flows from Durban, depending on delivered cost, reliability and access.','pp14–15']
 ];
 rows.forEach(([a,b,c],i)=>{const y=320+i*44;add(s,'SCR driver '+i,a,225,y,235,40,16.5,true,blue);add(s,'SCR meaning '+i,b,472,y,585,40,16.5);add(s,'SCR pages '+i,c,1080,y,90,40,15,true,blue);if(i<4)rule(s,'SCR row divider '+i,225,y+42,941,.6);});
 rule(s,'C divider',48,544,1118,1);
 add(s,'R label','RESOLUTION',48,555,170,28,18,true,blue);
 add(s,'R answer','Vopak should secure customer capture before expanding',225,551,835,31,22,true,blue);
 add(s,'R reference','pp16–18',1080,555,90,28,15,true,blue);
 add(s,'R body','Base imports remain about 16.6bn litres in 2030. Illustrative capture is 2.63bn litres through Durban, including 1.32bn onward through Lesedi within the same flow; this fits the preliminary working-tank screen.',225,587,941,43,18);
 add(s,'R decision','Expansion requires secured incremental volumes and a demonstrated capacity shortfall.',225,634,941,25,18,true,blue);
 const footer=get(s,'Unified source footer');footer.position={left:48,top:663,width:1118,height:12};
}
"""
s=s.replace('for(const d of spec.slides){',insert+'\nfor(const d of spec.slides){',1)
(scripts/'build_sa_story_v36.mjs').write_text(s,encoding='utf8')
for name in ['trim_sa_story_v33.py','apply_sa_story_navigation_v33.py','package_sa_chart_workbooks_v33.py','finalize_sa_story_v33.mjs']:
    t=(scripts/name).read_text().replace('v33','v36')
    if name.startswith('trim_'):t=t.replace('[22:]','[23:]')
    if name.startswith('apply_'):
        t=t.replace('len(native)==21','len(native)==22').replace('Exported 22 slides; 21','Exported 23 slides; 22').replace('Pages 2-19 present','Pages 2-18 present')
        t=t.replace("clean=QA/'body.pptx'","clean=QA/'styled_body.pptx'")
    (scripts/name.replace('v33','v36')).write_text(t,encoding='utf8')
print('Prepared v36 build pipeline')
