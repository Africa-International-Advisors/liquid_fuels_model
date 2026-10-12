from pathlib import Path

root = Path(__file__).resolve().parents[2]
scripts = root / 'pptx/scripts'
t = (scripts / 'build_sa_scr_three_v01.mjs').read_text(encoding='utf8')
t = t.replace('scr_three_v01', 'scr_four_v02')
t = t.replace('base.duplicate(),base.duplicate(),base.duplicate()', 'base.duplicate(),base.duplicate(),base.duplicate(),base.duplicate()')
t = t.replace(" 'Substantial imports sustain", " 'How the national fuel market translates into Vopak’s addressable volume',\n 'Substantial imports sustain")
t = t.replace(" 'Analytical workbook v02 base scenario;", " 'Framework: analytical workbook v02 and market-sizing workbook. Gateway shares and customer access require validation. Walvis Bay is a route to assess; no diversion volume is assigned. Stock build increases import need; stock draw reduces it.',\n 'Analytical workbook v02 base scenario;")
t = t.replace('i<3;i++', 'i<4;i++')
start = t.index("add(c,'C left heading'")
end = t.index("add(c,'C takeaway'")
t = t[:start] + """
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
 ['Driver','What changes for fuel demand and Durban flows'],
 ['Sector activity','Mining, manufacturing and agriculture follow different growth paths, changing equipment and freight demand.'],
 ['Eskom recovery','More reliable electricity reduces peaking and backup diesel at utilities, mines, factories and farms.'],
 ['Road-to-rail','Freight transferred from trucks to rail reduces road diesel use; the net effect also depends on rail traction.'],
 ['Vehicle efficiency','Lower fuel consumption per kilometre reduces demand for a given level of road activity.'],
 ['Domestic production','Higher refinery output or restarts could displace imports. Lower output increases import dependence.'],
 ['Competing gateways','Matola offers an alternative inland route. Assess Walvis Bay on delivered cost, reliability and access; diversion is unquantified.']
];
nativeTable(c,drivers,[342,776],174,398,20);
""" + t[end:]
t = t.replace('const r=slides[2];', """
const m=slides[2];
nativeTable(m,[
 ['Sizing step','Basis for the calculation','Market measure'],
 ['1  National demand','Petrol and diesel demand by end-use segment; apply sector, power, rail and efficiency drivers.','21.0bn L in 2025\\nEstimated demand'],
 ['2  Import requirement','Demand − domestic production + exports + stock build (or − stock draw).','16.7bn L in 2025\\nGross import need'],
 ['3  Gateway allocation','Allocate to Durban, other SA ports and Matola; assess Walvis Bay. Compare delivered cost, reliability and access.','Durban-served pool\\nRoute shares to establish'],
 ['4  Addressable flows','Identify customers and products Vopak can serve, given routes, contracts and terminal access.','Addressable volume\\nCustomer-level assessment'],
 ['5  Achievable capture','Apply achievable customer capture; identify Lesedi onward volumes within the same Durban fuel flow.','2.63bn L illustration\\nIncludes 1.32bn L Lesedi'],
 ['6  Capacity and investment','Compare incremental captured flow with usable tanks, stock turns, receipt and dispatch capacity.','Capacity shortfall\\nBasis for investment']
],[264,602,252],174,410,18.5);
add(m,'M takeaway','Size total demand, addressable flows and capture separately; count Durban–Lesedi fuel once.',48,604,1118,39,21,true,blue);
const r=slides[3];
""")
t = t.replace('2030 base-case imports', '2030 national imports')
t = t.replace('Activity growth broadly offsets power, rail and efficiency reductions. Domestic production stays at the 5.8bn-litre planning baseline.', 'Base-case imports across all gateways. Activity growth broadly offsets power, rail and efficiency reductions; domestic production stays at 5.8bn litres.')
t = t.replace('This is a capture scenario, not an established customer share.', 'Illustrative share; no explicit deduction for Matola or Walvis Bay diversion.')
t = t.replace('main:{1:1,2:2,3:3}', 'main:{1:1,2:2,3:3,4:3}').replace('keep_count:3','keep_count:4')
t = t.replace('Three-page SCR authored','Four-page SCR and market-sizing framework authored')
(scripts/'build_sa_scr_four_v02.mjs').write_text(t,encoding='utf8')

for old,new in [('trim_sa_scr_three_v01.py','trim_sa_scr_four_v02.py'),('apply_sa_scr_three_navigation_v01.py','apply_sa_scr_four_navigation_v02.py'),('finalize_sa_scr_three_v01.mjs','finalize_sa_scr_four_v02.mjs')]:
    t=(scripts/old).read_text(encoding='utf8').replace('scr_three_v01','scr_four_v02').replace('SA_SCR_Three_Page_2026-10-11_v01','SA_SCR_Four_Page_2026-10-11_v02')
    if old.startswith('trim'): t=t.replace('[3:]','[4:]')
    if old.startswith('apply'):
        t=t.replace("clean=QA/'body.pptx'", "clean=QA/'styled_body.pptx'").replace('len(native)==3','len(native)==4').replace('Exported 3 slides; 3','Exported 4 slides; 4')
    if old.startswith('finalize'):
        t=t.replace('workspaceDir:root,','workspaceDir:root,explicitTotalSlideCount:4,requiredNativeTableOwnerSlides:[2,3],')
        t=t.replace("'--validate-heading-fit']", "'--validate-heading-fit','--require-native-table-slide','2','--require-native-table-slide','3']")
    (scripts/new).write_text(t,encoding='utf8')
