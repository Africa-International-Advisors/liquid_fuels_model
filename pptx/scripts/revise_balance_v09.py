from pathlib import Path
import win32com.client
r=Path(__file__).resolve().parents[2];q=r/'pptx/qa/evidence_v09'
a=win32com.client.Dispatch('PowerPoint.Application')
d=a.Presentations.Open(str(r/'pptx/output/delivered/supporting/archive/2026-10-12_accepted_v10/SA_SCR_Evidence_2026-10-12_v08.pptx'),ReadOnly=True,Untitled=False,WithWindow=False)
c=a.Presentations.Open(str(q/'chart.pptx'),ReadOnly=True,Untitled=False,WithWindow=False)
try:
 p=d.Slides(2)
 for i in range(p.Shapes.Count,0,-1):
  if p.Shapes(i).Name.startswith('Balance ') or p.Shapes(i).Name=='Product reconciliation':p.Shapes(i).Delete()
 for sh in d.Slides(6).Shapes:
  if sh.Name.startswith('Vopak exhibit ') or sh.Name in ['Evidence unit','Evidence insights','Evidence takeaway']:
   sh.Copy();p.Shapes.Paste()
 p.CustomLayout=d.Slides(6).CustomLayout
 updates={
 'Vopak exhibit left heading':'2025 petrol and diesel balance',
 'Vopak exhibit right heading':'Reported trade; estimated domestic balance',
 'Evidence unit':'Billion litres | calendar 2025',
 'Evidence insights':'Supply: 5.80bn L assumed production + 16.70bn L recorded imports.\n\nUses: 20.99bn L estimated consumption + 1.55bn L recorded exports.\n\nSupply is 0.034bn L below uses. Stock change is unmeasured; the gap remains a reconciliation item.\n\nPetrol and diesel differences offset: −2.00bn L and +1.97bn L respectively.',
 'Evidence takeaway':'Production + imports − exports = 20.95bn L available, versus 20.99bn L estimated consumption.'}
 for n,t in updates.items():p.Shapes(n).TextFrame.TextRange.Text=t
 p.Shapes('Evidence insights').TextFrame.TextRange.Font.Size=13
 p.Shapes('Vopak exhibit right heading').TextFrame.TextRange.Font.Size=13
 c.Slides(1).Shapes(1).Copy();p.Shapes.Paste()
 d.SaveAs(str(q/'edited.pptx'),24)
finally:
 for p in [c,d]:
  try:p.Close()
  except Exception:pass
