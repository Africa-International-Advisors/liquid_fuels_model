from pathlib import Path
import win32com.client
root=Path(__file__).resolve().parents[2]
qa=root/'pptx/qa/story_v35'
app=win32com.client.Dispatch('PowerPoint.Application')
deck=app.Presentations.Open(str(root/'pptx/output/delivered/supporting/archive/2026-10-11_cleanup/SA_Market_Story_2026-10-11_v34.pptx'),ReadOnly=False,Untitled=True,WithWindow=False)
try:
    deck.Slides.InsertFromFile(str(qa/'scr_source.pptx'),1,1,1)
    deck.Slides(3).Shapes('brand-pptx section navigation').Copy()
    deck.Slides(2).Shapes.Paste()
    deck.Slides(3).Delete()
    out=qa/'SA_Market_Story_2026-10-11_v35.pptx'
    deck.SaveAs(str(out),24)
    deck.SaveAs(str(out.with_suffix('.pdf')),32)
    deck.Slides(2).Export(str(qa/'SCR.png'),'PNG',1460,864)
    assert deck.Slides.Count==23
    print('Page 2 replaced; 23-slide story preserved')
finally:
    deck.Close()
