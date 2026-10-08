"""Apply the approved appendix moves while preserving exhibits and slide targets."""
import json
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Pt


def apply(source, destination, allocation=False):
    deck = Presentation(source)
    if allocation:
        assert len(deck.slides) == 30
        assert 'Provincial sales locate demand' in deck.slides[5].shapes.title.text
        assert deck.slides[14].shapes.title.text == 'Appendix'
        moved = [6]
        divider_page = 15
        order = [n for n in range(1, 16) if n != 6] + [6] + list(range(16, 31))
    else:
        assert len(deck.slides) == 31
        moved = [8, 9, 11, 12, 13, 14]
        divider_page = 22
        order = [n for n in range(1, 23) if n not in moved] + moved + list(range(23, 32))
    mapping = {old: new for new, old in enumerate(order, 1)}
    original = list(deck.slides)
    ids = list(deck.slides._sldIdLst)
    for item in ids:
        deck.slides._sldIdLst.remove(item)
    for old in order:
        deck.slides._sldIdLst.append(ids[old - 1])
    page_by_part = {s.part: n for n, s in enumerate(deck.slides, 1)}
    for old in moved:
        for shape in list(original[old - 1].shapes):
            if shape.name.startswith('Section navigation '):
                shape._element.getparent().remove(shape._element)
    for n, slide in enumerate(deck.slides, 1):
        frames = [q.text_frame for q in slide.shapes if q.has_text_frame]
        frames += [c.text_frame for q in slide.shapes if q.has_table for row in q.table.rows for c in row.cells]
        for frame in frames:
            for paragraph in frame.paragraphs:
                for run in paragraph.runs:
                    linked = False
                    for h in run._r.xpath('.//a:hlinkClick'):
                        rid = h.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                        if rid and not slide.part.rels[rid].is_external:
                            target = slide.part.rels[rid].target_part
                            if target in page_by_part and re.fullmatch(r'\s*(?:/\s*)?\d+\s*', run.text):
                                run.text = (' / ' if '/' in run.text else '') + str(page_by_part[target])
                                linked = True
                    if not linked:
                        # Only explicit in-deck references; source citations (pp., p. etc.) remain intact.
                        run.text = re.sub(r'\b(page |on p)(\d+)\b', lambda m: m[1] + str(mapping.get(int(m[2]), int(m[2]))), run.text)
        for shape in slide.shapes:
            if shape.has_text_frame and shape.name == 'Slide Number Placeholder':
                shape.text = str(n)
                for p in shape.text_frame.paragraphs:
                    p.font.name = 'Lato'
                    p.font.size = Pt(10)
    divider = original[divider_page - 1]
    for shape in divider.shapes:
        if shape.has_text_frame and shape.text.startswith('Turnover sensitivity'):
            p = shape.text_frame.paragraphs[0]
            p.runs[0].text = 'Demand drivers · scenario framework · fuel assumptions · operating sensitivities'
            for run in list(p.runs)[1:]:
                run.text = ''
    target = Path(destination)
    if target.exists():
        raise FileExistsError(target)
    deck.save(target)
    target.with_suffix('.structure.json').write_text(json.dumps({
        'source': str(source), 'original_to_revised_page': mapping,
        'appendix_divider': mapping[divider_page], 'moved_original_pages': moved,
    }, indent=2), encoding='utf-8')
    print(target)


if __name__ == '__main__':
    apply(sys.argv[1], sys.argv[2], allocation='--allocation' in sys.argv[3:])
