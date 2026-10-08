"""Check deliverable structure and assemble rendered slide contact sheets."""
import json
import logging
import argparse
from pathlib import Path
from PIL import Image, ImageDraw
from pptx import Presentation
from pypdf import PdfReader

logging.getLogger('pypdf').setLevel(logging.ERROR)
root=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--story', type=Path)
parser.add_argument('--pptx', type=Path)
parser.add_argument('--qa', type=Path)
args=parser.parse_args()
catalog=json.loads((root/'pptx/output/delivered/supporting/archive/records/current_story.json').read_text())
pairs=[(Path(catalog['qa']).parent.name,Path(catalog['story']).name)]
for stem,storyfile in pairs:
    current=json.loads((root/'pptx/output/delivered/supporting/archive/records/current_story.json').read_text())
    out=args.pptx or root/next(f['path'] for f in current['files'] if f['path'].endswith('.pptx'))
    story=json.loads((args.story or root/'pptx/story'/storyfile).read_text(encoding='utf-8'))
    deck=Presentation(out.with_suffix('.pptx'))
    pdf=PdfReader(out.with_suffix('.pdf'))
    assert len(deck.slides)==len(pdf.pages)==len(story['slides'])+1
    errors=[]
    for i,slide in enumerate(deck.slides):
        for shape in slide.shapes:
            if shape.left < -12700 or shape.top < -12700 or shape.left+shape.width > deck.slide_width+12700 or shape.top+shape.height > deck.slide_height+12700:
                errors.append((i+1,shape.name,'outside slide'))
        if i:
            spec=story['slides'][i-1]
            assert ''.join(spec['title'].split()) in ''.join((pdf.pages[i].extract_text() or '').split()), (stem,i,'missing title')
            if spec.get('revision_action') in ('updated','new') and spec.get('rows'):
                table=next(s.table for s in slide.shapes if s.has_table)
                expected=[spec['headers']]+spec['rows']
                actual=[[c.text for c in r.cells] for r in table.rows]
                assert actual==expected, (i+1,'evidence table differs from canonical content')
            if spec.get('revision_action')=='updated' and spec.get('takeaway'):
                caption=next(s for s in slide.shapes if s.name=='Interpretation')
                assert caption.text==spec['takeaway'], (i+1,'caption mismatch')
    assert not errors, errors
    divider_index=next(i+1 for i,s in enumerate(story['slides']) if s.get('divider'))
    assert 'Appendix' in pdf.pages[divider_index].extract_text()
    for original_page,expected in [(7,3),(15,4)]:
        page=next((i+2 for i,s in enumerate(story['slides']) if s.get('source_page')==original_page),original_page)
        assert sum(s.name.startswith('Argument icon') for s in deck.slides[page-1].shapes)==expected
    for page in [i+2 for i, spec in enumerate(story["slides"]) if spec.get("panel_subtitles") and spec.get("margin_rules")]:
        rules=[s for s in deck.slides[page-1].shapes if s.name=='Content margin panel rule']
        assert abs(min(s.left for s in rules)/12700-36)<.1
        assert abs(max(s.left+s.width for s in rules)/12700-874.8)<.1
        heads=[s for s in deck.slides[page-1].shapes if s.name=='Aligned panel subtitle']
        assert len(heads)==len(story['slides'][page-2]['panel_subtitles'])
        assert abs(min(s.left for s in heads)/12700-36)<.1
        shapes=list(deck.slides[page-1].shapes)
        picture_index=next(i for i,s in enumerate(shapes) if s.name=='Evidence chart')
        assert all(i>picture_index for i,s in enumerate(shapes) if s.name=='Content margin panel rule')
    refinery=next((s for s in story['slides'] if s.get('source_page')==13),story['slides'][11])
    assert 'FIASA 2025 p49' in refinery['note']
    d=args.qa or root/'pptx/qa'/stem
    files=sorted(d.glob('Slide*.PNG'),key=lambda p:int(p.stem[5:]))
    assert len(files)==len(deck.slides)
    for start in range(0,len(files),8):
        outimg=Image.new('RGB',(1218,((min(8,len(files)-start)+1)//2)*380),'#dddddd')
        for i,p in enumerate(files[start:start+8]):
            outimg.paste(Image.open(p).resize((609,360)),((i%2)*609,(i//2)*380))
            ImageDraw.Draw(outimg).text(((i%2)*609+5,(i//2)*380+361),p.stem,fill='black')
        outimg.save(d/f'contact{start//8+1}.png')
    report=json.loads((d/'checks.json').read_text()) if (d/'checks.json').exists() else {}
    report.update({'slides':len(deck.slides),'pdf_pages':len(pdf.pages),'bounds':'pass','pdf_titles':'pass','render_count':len(files)})
    (d/'checks.json').write_text(json.dumps(report,indent=2))
    print(out.stem, len(deck.slides), 'slides/pages; bounds, titles, evidence content and render count pass')
