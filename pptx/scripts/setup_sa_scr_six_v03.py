from pathlib import Path
r=Path(__file__).resolve().parents[2];s=r/'pptx/scripts'
t=(s/'build_sa_scr_four_v02.mjs').read_text(encoding='utf8').replace('scr_four_v02','scr_six_v03')
t=t.replace("const base=p.slides.items[3];", "const cover=p.slides.items[0].duplicate();const closing=cover.duplicate();\nconst base=p.slides.items[3];")
t=t.replace('slides.forEach((s,i)=>s.moveTo(i));', '[cover,...slides,closing].forEach((s,i)=>s.moveTo(i));')
t=t.replace("String(i+1)","String(i+2)")
a=t.index('const drivers=[');b=t.index("add(c,'C takeaway'",a)
t=t[:a]+"""const drivers=[
 ['Complication','Driver','What changes for fuel demand and Durban flows'],
 ['1  Demand','Sector activity','Mining, manufacturing and agriculture drive equipment and freight demand along different growth paths.'],
 ['','Eskom recovery','Reliable electricity reduces peaking and backup diesel at utilities, mines, factories and farms.'],
 ['','Road-to-rail','Freight shifted from trucks reduces road diesel use; net savings depend on rail traction.'],
 ['','Vehicle efficiency','Lower fuel consumption per kilometre reduces demand at a given level of road activity.'],
 ['2  Domestic supply','Refinery output and restarts','Higher production displaces imports; outages or lower output increase import dependence.'],
 ['3  Import routes','Ports and inland connections','Matola competes for inland supply. Assess Walvis Bay, pipeline access and delivered cost; Walvis Bay diversion is unquantified.']
];
nativeTable(c,drivers,[190,260,668],174,410,19);
"""+t[b:]
a=t.index('nativeTable(m,[');b=t.index("add(m,'M takeaway'",a)
t=t[:a]+"""const framework=nativeTable(m,[
 ['Sizing step','Basis for the calculation','Market measure'],
 ['1  National demand','Petrol and diesel by end use: road, mining, manufacturing, agriculture and power. Apply activity, rail and efficiency drivers.','21.0bn L in 2025\\nEstimated demand'],
 ['2  Import requirement','Demand − domestic production + exports + stock build (or − stock draw).','16.7bn L in 2025\\nGross import need'],
 ['3  Ports and inland routes','Allocate imports across ports; assess pipeline, road and rail connections. Compare Durban with Matola and potential Walvis Bay routes.','Supply pool by catchment\\nRoute shares to establish'],
 ['4  Addressable market','Size product and customer flows Durban and Lesedi can each serve, by catchment, logistics access and competing supply. Reconcile shared flows.','Addressable volume\\nBy site, product and customer'],
 ['5  Achievable capture','Establish current Vopak throughput, volumes retained and additional customer volumes it can win. Assess competition and contracts; count shared fuel once.','Current + incremental capture\\nBy site and customer'],
 ['6  Capacity and investment','Compare captured throughput with usable tanks, stock turns, receipt and dispatch capacity; identify the incremental constraint.','Capacity shortfall\\nBasis for investment']
],[252,606,260],174,424,18);
"""+t[b:]
t=t.replace("'Size total demand, addressable flows and capture separately; count Durban–Lesedi fuel once.'", "'Steps 4–5 size Vopak’s opportunity: addressable customer flows, then achievable capture.'")
t=t.replace("48,604,1118,39,21", "48,612,1118,32,20")
insert="""
function coverText(slide,name,value){const sh=slide.shapes.items.find(x=>x.name===name);if(sh)sh.text=value;}
coverText(cover,'TextBox 4','South Africa\\nliquid fuels\\nmarket outlook');
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
"""
t=t.replace("await fs.writeFile(qa+'/page_map.json'",insert+"\nawait fs.writeFile(qa+'/page_map.json'")
t=t.replace('main:{1:1,2:2,3:3,4:3}', 'main:{2:1,3:2,4:3,5:3}').replace('keep_count:4','keep_count:6')
t=t.replace('Four-page SCR and market-sizing framework authored','Six-page SCR and market-sizing framework authored')
(s/'build_sa_scr_six_v03.mjs').write_text(t,encoding='utf8')
for old,new in [('trim_sa_scr_four_v02.py','trim_sa_scr_six_v03.py'),('style_sa_scr_four_v02.py','style_sa_scr_six_v03.py'),('apply_sa_scr_four_navigation_v02.py','apply_sa_scr_six_navigation_v03.py'),('finalize_sa_scr_four_v02.mjs','finalize_sa_scr_six_v03.mjs')]:
 t=(s/old).read_text(encoding='utf-8-sig').replace('scr_four_v02','scr_six_v03').replace('SA_SCR_Four_Page_2026-10-11_v02','SA_SCR_Six_Page_2026-10-11_v03')
 if old.startswith('trim'):t=t.replace('[4:]','[6:]')
 if old.startswith('apply'):t=t.replace('Exported 4 slides; 4','Exported 6 slides; 4')
 if old.startswith('finalize'):
  t=t.replace('explicitTotalSlideCount:4','explicitTotalSlideCount:6').replace('requiredNativeTableOwnerSlides:[2,3]','requiredNativeTableOwnerSlides:[3,4]')
  t=t.replace("'--require-native-table-slide','2','--require-native-table-slide','3'", "'--require-native-table-slide','3','--require-native-table-slide','4','--cover-role','cover'")
 (s/new).write_text(t,encoding='utf8')
