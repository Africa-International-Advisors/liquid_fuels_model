"""Insert the authored SCR into the preserved native PowerPoint package."""
from pathlib import Path
import win32com.client

root=Path(__file__).resolve().parents[2]
qa=root/'pptx/qa/story_v34'
app=win32com.client.Dispatch('PowerPoint.Application')
deck=app.Presentations.Open(str(root/'pptx/output/delivered/supporting/archive/2026-10-11_cleanup/SA_Market_Story_2026-10-11_v33.pptx'),ReadOnly=False,Untitled=True,WithWindow=False)
try:
    deck.Slides.InsertFromFile(str(qa/'scr_source.pptx'),1,1,1)
    deck.Slides(3).Shapes('brand-pptx section navigation').Copy()
    deck.Slides(2).Shapes.Paste()
    for slide in deck.Slides:
        for shape in slide.Shapes:
            if shape.Name=='Slide Number Placeholder':
                shape.TextFrame.TextRange.Text=str(slide.SlideIndex)
            if shape.HasTextFrame and shape.TextFrame.HasText:
                text=shape.TextFrame.TextRange.Text
                if 'Pages 2-19 present' in text:
                    shape.TextFrame.TextRange.Text=text.replace('Pages 2-19 present','Pages 2-20 present')
    # References in the driver overview and source map follow the inserted page.
    replacements={
        4:{'pp8–9':'pp9–10','pp7, 10–11':'pp8, 11–12','pp12–14':'pp13–15','pp15–16':'pp16–17'},
        23:{'2, 4–7':'3, 5–8','3, 8–11':'4, 9–12','12–14, 21':'13–15, 22','15–16':'16–17','17–19':'18–20'}
    }
    for page, mapping in replacements.items():
        for shape in deck.Slides(page).Shapes:
            if not shape.HasTable: continue
            for r in range(1,shape.Table.Rows.Count+1):
                for c in range(1,shape.Table.Columns.Count+1):
                    tr=shape.Table.Cell(r,c).Shape.TextFrame.TextRange
                    old=tr.Text
                    for a,b in mapping.items():
                        if a in old: tr.Text=old.replace(a,b); break
    out=qa/'SA_Market_Story_2026-10-11_v34.pptx'
    deck.SaveAs(str(out),24)
    deck.SaveAs(str(out.with_suffix('.pdf')),32)
    render=qa/'powerpoint_render';render.mkdir(exist_ok=True)
    deck.Export(str(render),'PNG',1217,720)
    assert deck.Slides.Count==23
    assert bool(deck.Slides(2).Shapes('brand-pptx section navigation').HasSmartArt)
    print('23 slides exported, with native SmartArt on the new SCR')
finally:
    deck.Close()
