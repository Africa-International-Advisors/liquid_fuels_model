"""Add the agreed daily focus table to the canonical story; no model changes."""
import json
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pptx import Presentation
from pptx.util import Inches, Pt
from brand_pptx import BrandStyle, add_themed_slide
from brand_configs import vopak as cfg
from convergence_story_order import native_table, clone_navigation
from convergence_feedback import text, replace


def add_manish_focus(prs, root, brand):
    doc = json.loads((root / 'story/manish_focus_2026_10_07.json').read_text(encoding='utf-8'))
    if any(s.shapes.title and s.shapes.title.text == doc['title'] for s in prs.slides):
        return
    original = list(prs.slides)
    roadmap = next(s for s in original if s.shapes.title and 'six-week' in s.shapes.title.text)
    s = add_themed_slide(prs, 'Header only', brand=brand, title=doc['title'])
    clone_navigation(s, roadmap)
    for p in s.shapes.title.text_frame.paragraphs:
        p.font.name = cfg.THEME_FONT
        p.font.size = Pt(24)
        p.font.bold = True
    text(s, doc['subtitle'], .5, 1.78, 11.65, .34, 14, True)
    rows = [['Priority / focus', 'Manish: output today', 'Nigel: decision / review']] + doc['rows']
    native_table(s, rows, .5, 2.35, [2.05, 5.60, 4.0], [.48] + [.65] * 5, brand, 12)
    text(s, doc['target'], .5, 6.27, 11.65, .43, 13, True)
    text(s, doc['status'], .5, 6.80, 11.65, .25, 10)
    text(s, 'Source: ' + doc['source'], .5, 7.10, 10.6, .25, 7.5).name = 'Unified source footer'
    s.notes_slide.notes_text_frame.text = json.dumps(doc, ensure_ascii=False, indent=2)
    order = original[:original.index(roadmap)+1] + [s] + original[original.index(roadmap)+1:]
    ids = {prs.part.related_slide(r.rId).part: r for r in prs.slides._sldIdLst}
    for r in list(prs.slides._sldIdLst):
        prs.slides._sldIdLst.remove(r)
    for slide in order:
        prs.slides._sldIdLst.append(ids[slide.part])
    pages = {slide.part: i for i, slide in enumerate(prs.slides, 1)}
    for slide in prs.slides:
        frames = [q.text_frame for q in slide.shapes if q.has_text_frame]
        frames += [c.text_frame for q in slide.shapes if q.has_table for row in q.table.rows for c in row.cells]
        for frame in frames:
            for p in frame.paragraphs:
                for run in p.runs:
                    for h in run._r.xpath('.//a:hlinkClick'):
                        rid = h.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                        if rid and not slide.part.rels[rid].is_external:
                            target = slide.part.rels[rid].target_part
                            if target in pages and re.fullmatch(r'\d+', run.text.strip()):
                                run.text = str(pages[target])
    from agenda_answer_page import _links
    overview = original[2]
    table = next(q.table for q in overview.shapes if q.has_table)
    _links(overview, table.cell(7, 4), [21, 22, 23, 24], prs, brand)
    from scr_editorial import apply_confidentiality
    from footer_layout import finish_footer_and_markers
    apply_confidentiality(prs)
    finish_footer_and_markers(prs, brand)
    for i, slide in enumerate(prs.slides, 1):
        nodes = slide._element.xpath('.//p:cNvPr')
        seen = set()
        next_id = max(int(n.get('id')) for n in nodes) + 1
        for node in nodes:
            if node.get('id') in seen:
                node.set('id', str(next_id))
                next_id += 1
            seen.add(node.get('id'))
        for q in slide.shapes:
            if q.has_text_frame and 'Every Henry storyboard prompt' in q.text:
                replace(q, re.sub(r'pages \d+[–-]\d+', 'pages 27–29', q.text))
            if q.has_text_frame and q.top > Inches(7) and q.left > Inches(12) and q.text.strip().isdigit():
                replace(q, str(i))
            assert q.left >= 0 and q.top >= 0 and q.left + q.width <= prs.slide_width + 10 and q.top + q.height <= prs.slide_height + 10, (i, q.name)


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    prs = Presentation(sys.argv[1])
    add_manish_focus(prs, root, BrandStyle.from_module(cfg))
    prs.save(sys.argv[2])
    print(f'Built {len(prs.slides)} pages; Manish focus follows delivery roadmap')
