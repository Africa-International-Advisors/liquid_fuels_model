from pathlib import Path
import json,win32com.client
r=Path(__file__).resolve().parents[2];q=r/'pptx/qa/evidence_v06';q.mkdir(exist_ok=True)
app=win32com.client.Dispatch('PowerPoint.Application')
deck=app.Presentations.Open(str(r/'pptx/output/delivered/supporting/archive/2026-10-12_accepted_v10/SA_SCR_Evidence_2026-10-12_v05.pptx'),ReadOnly=True,Untitled=False,WithWindow=False)
blue=0x73230A
def txt(slide,name,text,x,y,w,h,size=18,bold=False):
 sh=slide.Shapes.AddTextbox(1,x*.75,y*.75,w*.75,h*.75);sh.Name=name
 tf=sh.TextFrame;tf.MarginLeft=0;tf.MarginRight=0;tf.MarginTop=0;tf.MarginBottom=0
 tr=tf.TextRange;tr.Text=text;tr.Font.Name='Lato';tr.Font.Size=size*.75;tr.Font.Bold=bold;tr.Font.Color.RGB=blue if bold else 0x1A1511
 return sh
def clearbody(slide):
 for i in range(slide.Shapes.Count,0,-1):
  sh=slide.Shapes(i)
  if sh.Name not in ['Title 1','Unified source footer','Strictly Confidential footer','Slide Number Placeholder','brand-pptx section navigation'] and 150<=sh.Top/.75<645:sh.Delete()
def link(tr,page):
 tr.ActionSettings(1).Hyperlink.SubAddress=f'{deck.Slides(page).SlideID},{page},Evidence {page}'
 tr.Font.Color.RGB=blue
try:
 # Evidence index: one table with all seven evidence pages.
 p=deck.Slides(3)
 for i in range(p.Shapes.Count,0,-1):
  if p.Shapes(i).Name=='Demand baseline link':p.Shapes(i).Delete()
 table=next(sh for sh in p.Shapes if sh.HasTable).Table
 table.Rows.Add(2)
 vals=['Baseline','Baseline demand | p4','Estimated 21.0bn-litre market in 2025; petrol/diesel history and the end-use split establish the starting point.']
 for c,v in enumerate(vals,1):table.Cell(2,c).Shape.TextFrame.TextRange.Text=v
 for row in range(1,9):
  table.Rows(row).Height=(40 if row==1 else 53)*.75
  for col in range(1,4):
   tr=table.Cell(row,col).Shape.TextFrame.TextRange;tr.Font.Name='Lato';tr.Font.Size=13.5
   tr.Font.Bold=(row==1 or col==1)
 for row,page in zip(range(2,9),range(4,11)):link(table.Cell(row,2).Shape.TextFrame.TextRange,page)
 # Strip only the issue-tree cross-references; keep its page footer.
 flow=deck.Slides(11)
 for i in range(flow.Shapes.Count,0,-1):
  sh=flow.Shapes(i)
  if 'deep dive' in sh.Name.lower() or sh.Name in ['Deep dive legend marker','Deep dive legend']:sh.Delete()
 for sh in flow.Shapes:
  if sh.Name=='National market tag':sh.TextFrame.TextRange.Text='2025 demand estimate'
  if sh.Name=='Share tag':sh.TextFrame.TextRange.Text='Illustrative capture'
 # Production history and separate planning assumption.
 p=deck.Slides(9);clearbody(p)
 p.Shapes('Title 1').TextFrame.TextRange.Text='Reported fuel production declined through 2021; the 2025 baseline assumes 5.8bn litres'
 txt(p,'Production history heading','Reported petrol and diesel production',48,176,745,30,21,True)
 txt(p,'Production units','Billion litres | reported history, 2014–2021',48,211,745,24,13)
 src=app.Presentations.Open(str(q/'production_chart.pptx'),ReadOnly=True,Untitled=False,WithWindow=False)
 try:
  next(sh for sh in src.Slides(1).Shapes if sh.HasChart).Copy();p.Shapes.Paste()
 finally:pass
 p=deck.Slides(9)
 txt(p,'Production implication','2025 planning baseline',835,176,332,30,21,True)
 txt(p,'Production assumption','5.8bn litres',835,223,332,56,35,True)
 txt(p,'Production commentary','Petrol/diesel planning assumption; not a reported national observation.\n\nReported combined production fell from 20.42bn L in 2014 to 11.67bn L in 2021.\n\nSAPREF and PetroSA contribute no refining output in the 2025 assessment. Operating output and product yields determine import displacement.',835,294,332,260,18)
 txt(p,'Production events','Plant context: Secunda 27.6m barrels in FY2025 → 30.6m in FY2026.\nNatref reporting scope changes; Astron reports in energy units. These disclosures cannot be summed directly.',48,550,745,70,17)
 p.Shapes('Unified source footer').TextFrame.TextRange.Text='Department energy balances 2014–2021; consolidated review workbook, DR01 national balance rows 8/17. Sasol FY2025/FY2026; Glencore 2024/2025. 2025: 5.8bn L planning assumption. Historical production ends in 2021; no interpolated observations.'
 # Map left; retain all route evidence on right.
 p=deck.Slides(10);clearbody(p)
 txt(p,'Map heading','Competing inland supply corridors',48,176,515,32,21,True)
 txt(p,'Map evidence heading','Evidence and implications',590,176,576,32,21,True)
 picture=p.Shapes.AddPicture(str(r/'output/delivered/sa_subtitles_2026_10_08_v17/corridor_map.png'),False,True,36,180,600,232)
 crop=picture.PictureFormat.Crop
 crop.PictureWidth=600;crop.PictureHeight=232;crop.ShapeWidth=375;crop.ShapeHeight=232;crop.PictureOffsetX=112.5;crop.PictureOffsetY=0
 picture.Left=36;picture.Top=176
 txt(p,'Map scope','Mapped road and rail connectivity; tanker access and operating services require confirmation. NMPP is the established inland connection discussed at right. Walvis Bay is a potential alternative.',48,552,500,80,16)
 items=[
 ('Durban and other SA ports','2025 Durban customs: 13.16bn L. Allocate national imports across ports before sizing inland reach.'),
 ('Durban–NMPP–Lesedi','Existing inland connection; customer/product access, receipt and dispatch constraints determine serviceable flows.'),
 ('Matola infrastructure','Galp/IPG: 60,000m³ petrol/diesel; Petromoc: 390,000m³ across fuels. Do not add overlapping capacities or equate storage with SA throughput.'),
 ('Mozambique flows','Komatipoort imports: 0.303bn L in 2022 → 0.086bn L in 2025. Observed flows anchor route volumes.'),
 ('Walvis Bay','Comparable delivered cost, access and SA flows remain unestablished. No quantified diversion or capture is assigned.')]
 for i,(a,b) in enumerate(items):
  y=219+i*78;txt(p,'Route heading '+str(i),a,590,y,576,23,17,True);txt(p,'Route body '+str(i),b,590,y+25,576,50,16)
 p.Shapes('Unified source footer').TextFrame.TextRange.Text='SARS 2022/2025; Galp Matola, 3 Dec 2020; Petromoc logistics; market-sizing workbook. Map: © OpenStreetMap contributors / Geofabrik; Natural Earth; geoBoundaries. Routes show connectivity, not validated tanker access. Compare the same product and destination.'
 for n in [9,10]:
  for ph in deck.Slides(n).NotesPage.Shapes:
   if ph.Type==14 and ph.HasTextFrame:
    try:
     if ph.PlaceholderFormat.Type==2:ph.TextFrame.TextRange.Text=deck.Slides(n).Shapes('Unified source footer').TextFrame.TextRange.Text
    except Exception:pass
 out=q/'SA_SCR_Evidence_2026-10-12_v06.pptx';deck.SaveAs(str(out),24);deck.SaveAs(str(out.with_suffix('.pdf')),32);deck.Export(str(q/'render'),'PNG',1217,720)
 src.Close()
finally:
 try:deck.Close()
 except Exception:pass
print('Updated pages 3, 9, 10 and 11')
