from pathlib import Path
import json
import win32com.client
r=Path(__file__).resolve().parents[2];q=r/'pptx/qa/evidence_v05';q.mkdir(exist_ok=True)
app=win32com.client.Dispatch('PowerPoint.Application')
deck=app.Presentations.Open(str(r/'pptx/output/delivered/supporting/archive/2026-10-12_accepted_v10/SA_SCR_Evidence_2026-10-11_v04.pptx'),ReadOnly=True,Untitled=False,WithWindow=False)
out=q/'SA_SCR_Evidence_2026-10-12_v05.pptx'
try:
 deck.Slides.InsertFromFile(str(r/'pptx/output/delivered/supporting/10102026_Vopak_Market_Sizing_v2000.pptx'),10,3,3)
 flow=deck.Slides(11)
 updates={
 'National market':'National consumption\n2025 estimate\n21.0bn litres',
 'Product demand':'Demand by product\nPetrol 8.9bn L\nDiesel 12.1bn L',
 'Sector demand':'Demand by use\nRoad, mining, agriculture\nManufacturing and power',
 'Production':'Domestic production\n5.8bn L in 2025\nPlanning assumption',
 'Ports':'Ports and alternatives\nDurban, Matola\nAssess Walvis Bay',
 'National market tag':'2025 estimate; demand p4',
 'Product demand tag':'2025 estimates',
 'Sector demand tag':'2025 segment estimates',
 'Production tag':'5.8bn L planning baseline',
 'Share tag':'Illustrative capture; p13',
 'National market deep dive':'p4',
 'Imports deep dive':'p2',
 'Production deep dive':'p9',
 'Product demand deep dive':'p4',
 'Sector demand deep dive':'p5',
 'Demand parameters deep dive':'pp5–8',
 'Ports deep dive':'p10',
 'Inland deep dive':'p10',
 'Unified source footer':'Analytical workbook v02; SARS 2025; provincial demand 2022; Transnet Pipelines FY2025. Production is a planning assumption; capture is illustrative. Shared Durban–Lesedi fuel is counted once. Historical catchments retain their stated years.',
 }
 for sh in flow.Shapes:
  if sh.Name in updates:sh.TextFrame.TextRange.Text=updates[sh.Name]
 for i in range(flow.Shapes.Count,0,-1):
  if flow.Shapes(i).Name in ['SCR 1','SCR 2','SCR 3','SCR 4']:flow.Shapes(i).Delete()
 deck.Slides(12).Shapes('brand-pptx section navigation').Copy()
 flow.Shapes.Paste()
 for page in range(1,deck.Slides.Count+1):
  for sh in deck.Slides(page).Shapes:
   if sh.Name=='Slide Number Placeholder':sh.TextFrame.TextRange.Text=str(page)
 # Hyperlink each driver cell to its evidence page; target slide IDs survive reordering.
 def link(text_range,page):
  target=deck.Slides(page)
  h=text_range.ActionSettings(1).Hyperlink
  h.Address='';h.SubAddress=f'{target.SlideID},{page},Evidence page {page}'
  text_range.Font.Color.RGB=0x73230A
 records=[]
 summary=deck.Slides(3)
 for sh in summary.Shapes:
  if sh.HasTable:
   for row,page in zip(range(2,8),range(5,11)):
    tr=sh.Table.Cell(row,2).Shape.TextFrame.TextRange
    link(tr,page);records.append({'label':tr.Text,'target':page,'slide_id':deck.Slides(page).SlideID})
 baseline=summary.Shapes.AddTextbox(1,650,116.5,225,13)
 baseline.Name='Demand baseline link';baseline.TextFrame.MarginLeft=0;baseline.TextFrame.MarginTop=0
 baseline.TextFrame.TextRange.Text='Demand baseline → p4'
 baseline.TextFrame.TextRange.Font.Name='Lato';baseline.TextFrame.TextRange.Font.Size=11
 baseline.TextFrame.TextRange.Font.Bold=True
 link(baseline.TextFrame.TextRange,4);records.append({'label':'Demand baseline → p4','target':4,'slide_id':deck.Slides(4).SlideID})
 # Preserve the flowchart's original deep-dive controls and correct their destinations.
 destinations={'National market deep dive':4,'Imports deep dive':2,'Production deep dive':9,'Product demand deep dive':4,'Sector demand deep dive':5,'Demand parameters deep dive':5,'Ports deep dive':10,'Inland deep dive':10}
 for sh in flow.Shapes:
  if sh.Name in destinations:
   link(sh.TextFrame.TextRange,destinations[sh.Name])
   sh.TextFrame.TextRange.Font.Color.RGB=0xFFFFFF
 for ph in flow.NotesPage.Shapes:
  if ph.HasTextFrame and ph.Type==14:
   try:
    if ph.PlaceholderFormat.Type==2:ph.TextFrame.TextRange.Text='Market-sizing issue tree reused from market-sizing v2000, slide 3. National demand/product estimates and production assumption aligned to analytical workbook v02. Provincial catchments retain 2022 source periods. Capture remains illustrative; Walvis Bay diversion unquantified.'
   except Exception:pass
 deck.SaveAs(str(out),24)
 deck.SaveAs(str(out.with_suffix('.pdf')),32)
 deck.Export(str(q/'render'),'PNG',1217,720)
 (q/'links.json').write_text(json.dumps(records,indent=2),encoding='utf8')
finally:deck.Close()
print('Inserted existing native flowchart as page 11; framework table page 12; linked all seven evidence pages from page 3.')
