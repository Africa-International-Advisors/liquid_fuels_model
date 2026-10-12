"""Balance clarification and two additions; reuse the locked v07 native layout."""
from pathlib import Path
import win32com.client

ROOT=Path(__file__).resolve().parents[2];q=ROOT/'pptx/qa/evidence_v08'
app=win32com.client.Dispatch('PowerPoint.Application')
d=app.Presentations.Open(str(ROOT/'pptx/output/delivered/supporting/archive/2026-10-12_accepted_v10/SA_SCR_Evidence_2026-10-12_v07.pptx'),ReadOnly=True,Untitled=False,WithWindow=False)
c=app.Presentations.Open(str(q/'new_charts.pptx'),ReadOnly=True,Untitled=False,WithWindow=False)
def put(slide,n,value):slide.Shapes(n).TextFrame.TextRange.Text=value
def bounds(sh,x,y,w,h):sh.Left=x*.75;sh.Top=y*.75;sh.Width=w*.75;sh.Height=h*.75
def txt(slide,n,value,x,y,w,h,size=18,bold=False,blue=False):
 s=slide.Shapes.AddTextbox(1,x*.75,y*.75,w*.75,h*.75);s.Name=n
 t=s.TextFrame;t.MarginLeft=t.MarginRight=t.MarginTop=t.MarginBottom=0
 t.WordWrap=True;t.AutoSize=0;t.TextRange.Text=value
 t.TextRange.Font.Name='Lato';t.TextRange.Font.Size=size*.75;t.TextRange.Font.Bold=bold;t.TextRange.Font.Color.RGB=0x73230A if blue else 0
 return s
def link(tr,page):
 h=tr.ActionSettings(1).Hyperlink;h.Address='';h.SubAddress=f'{d.Slides(page).SlideID},{page},Evidence page {page}'
 tr.Font.Color.RGB=0x73230A;tr.Font.Underline=True
try:
 # Add efficiency after vehicle sales; restore scenario chart before resolution.
 d.Slides(8).Duplicate().Item(1).MoveTo(9)
 d.Slides(9).Duplicate().Item(1).MoveTo(14)
 p=d.Slides(2)
 put(p,'Title 1','2025 production and imports broadly cover consumption and exports')
 for i in range(p.Shapes.Count,0,-1):
  if p.Shapes(i).Name.startswith('S '):p.Shapes(i).Delete()
 metrics=[('20.99bn L','Consumption','2025 estimate'),('5.80bn L','Domestic production','2025 planning assumption'),('16.70bn L','Gross imports','2025 recorded customs'),('1.55bn L','Exports','2025 recorded customs')]
 for i,(v,label,basis) in enumerate(metrics):
  x=48+i*284
  txt(p,'Balance value '+str(i),v,x,192,270,55,37,True,True)
  txt(p,'Balance label '+str(i),label,x,254,270,32,22,True,True)
  txt(p,'Balance basis '+str(i),basis,x,297,270,45,18)
 txt(p,'Balance equation heading','Production + imports − exports = availability before stock change',48,364,1118,36,24,True,True)
 txt(p,'Balance equation','5.80 + 16.70 − 1.55 = 20.95bn litres',48,413,1118,47,31,True)
 txt(p,'Balance reconciliation','Availability is 0.034bn litres below estimated consumption. Stock change is unmeasured; this difference remains a reconciliation item.',48,477,1118,55,21)
 txt(p,'Product reconciliation','Petrol and diesel differences offset: −2.00bn L petrol and +1.97bn L diesel. The aggregate match does not establish a reconciled product balance.',48,552,1118,57,20)
 txt(p,'Balance implication','Track consumption, production, imports, exports and stock change together.',48,626,1118,31,22,True,True)
 put(p,'Unified source footer','Analytical workbook v02, Balance; SARS calendar-2025 customs. Demand estimated; production assumed; trade recorded. Stock change and statistical/scope differences unresolved. Values rounded; the 0.034bn L gap uses unrounded data.')
 configs={9:{
  'title':'Improving vehicle efficiency partly offsets growth in fuel demand',
  'left':'Activity and efficiency effects by 2030',
  'right':'Less fuel for each kilometre travelled',
  'unit':'Billion litres versus 2025 | modelled base-case effects',
  'body':'Engine and vehicle improvements, fleet renewal and operating practices can lower fuel use per kilometre.\n\nThe base case assumes 1% annual improvement in road-fuel efficiency, saving 0.79bn L by 2030.\n\nActivity adds 1.54bn L across non-power uses. Rail and power effects are accounted for separately.',
  'takeaway':'The efficiency effect is a planning assumption; new-vehicle sales do not measure fleet-wide fuel savings.',
  'source':'Analytical workbook v02: Driver bridge (Base), Assumptions (Base: efficiency). Effects are modelled, not observed savings. Efficiency applies to road fuel after activity growth; rail is applied afterwards. Do not add a separate EV saving to the same efficiency allowance.',
  'chart':1},14:{
  'title':'Refinery recovery could materially reduce imports from the 16.6bn-litre base case',
  'left':'Gross import requirement, 2025–2030',
  'right':'Domestic supply drives the largest reduction',
  'unit':'Billion litres | existing combined scenarios',
  'body':'2030 imports: base 16.61bn L; low-import case 8.26bn L; high-import case 19.68bn L.\n\nThe low-import case adds 0.87bn L of operating output and 5.67bn L from assumed restarts.\n\nDemand assumptions also vary across these cases. The chart is not an isolated refinery sensitivity or a probability forecast.',
  'takeaway':'Higher domestic output displaces imports; restart timing, utilisation and product yields determine the effect.',
  'source':'Restored from South Africa story v37; analytical workbook v02, Scenarios and Driver bridge. Gross imports = demand − domestic supply + fixed 2025 exports; zero stock change. 2025 production: 5.8bn L assumption. Restart volumes and timing are scenario assumptions.',
  'chart':2}}
 for page,v in configs.items():
  p=d.Slides(page)
  for i in range(p.Shapes.Count,0,-1):
   if p.Shapes(i).HasChart:p.Shapes(i).Delete()
  for n,key in [('Title 1','title'),('Vopak exhibit left heading','left'),('Vopak exhibit right heading','right'),('Evidence unit','unit'),('Evidence insights','body'),('Evidence takeaway','takeaway'),('Unified source footer','source')]:put(p,n,v[key])
  c.Slides(v['chart']).Shapes(1).Copy();p.Shapes.Paste()
  chart=next(s for s in p.Shapes if s.HasChart);bounds(chart,48,245,676.8,310)
  p.Shapes('Evidence insights').TextFrame.TextRange.Font.Size=13.5
  if page==14:
   for i in range(1,5):
    sh=p.Shapes('Section navigation '+str(i));sh.Fill.ForeColor.RGB=0x73230A if i==4 else 0xEEEEEE
    sh.TextFrame.TextRange.Font.Color.RGB=0xFFFFFF if i==4 else 0x73230A;sh.TextFrame.TextRange.Font.Bold=i==4
  for sh in p.NotesPage.Shapes:
   if sh.Type==14 and sh.HasTextFrame:
    try:
     if sh.PlaceholderFormat.Type==2:sh.TextFrame.TextRange.Text=v['source']
    except Exception:pass
 # Updated clickable index: preserve all demand deep dives and include the restored outlook.
 table=next(s.Table for s in d.Slides(3).Shapes if s.HasTable)
 labels={2:('Baseline demand | p4',4),3:('Sector activity | p5',5),4:('Eskom recovery | p6',6),5:('Road-to-rail | p7',7),8:('Ports and inland connections | p11',11)}
 for row,(label,page) in labels.items():
  tr=table.Cell(row,2).Shape.TextFrame.TextRange;tr.Text=label;link(tr,page)
 tr=table.Cell(6,2).Shape.TextFrame.TextRange;tr.Text='Vehicle sales p8 | Efficiency p9'
 link(tr.Characters(1,16),8);link(tr.Characters(20,13),9)
 tr=table.Cell(7,2).Shape.TextFrame.TextRange;tr.Text='Refinery history p10 | Outlook p14'
 link(tr.Characters(1,20),10);link(tr.Characters(24,11),14)
 put(d.Slides(3),'Unified source footer','Demand baseline: p4. Driver evidence: pp5–11. Restored import outlook: p14. Stats SA; Eskom; Sasol; Glencore; Galp; Petromoc; naamsa. Scenario outcomes are separate from observed evidence.')
 for page in range(1,d.Slides.Count+1):
  for sh in d.Slides(page).Shapes:
   if sh.Name=='Slide Number Placeholder':sh.TextFrame.TextRange.Text=str(page)
 d.SaveAs(str(q/'edited.pptx'),24)
finally:
 for x in [c,d]:
  try:x.Close()
  except Exception:pass
print('16 pages: balance clarified; efficiency p9; refinery history p10 retained; import outlook p14 restored.')
