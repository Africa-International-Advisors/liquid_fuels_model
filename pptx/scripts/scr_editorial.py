"""Apply authored SCR copy and cartographic hierarchy without changing evidence."""
import json
from pptx.util import Inches, Pt
from scr_structure import panel
from brand_configs import vopak as cfg


def replace(q, value):
    """Preserve the approved first paragraph style when replacing authored copy."""
    p = q.text_frame.paragraphs[0]
    if p.runs:
        p.runs[0].text = value
        for run in list(p.runs)[1:]:
            run._r.getparent().remove(run._r)
        for extra in list(q.text_frame.paragraphs)[1:]:
            extra._p.getparent().remove(extra._p)
    else:
        p.text = value


def apply_editorial(prs, text, root, brand):
    copy = json.loads((root/'story/scr_editorial_2026_10_06.json').read_text(encoding='utf-8'))
    for page, title in copy['titles'].items():
        s = prs.slides[int(page)-1]
        q = next(q for q in s.shapes if q.is_placeholder and q.has_text_frame and 'Title' in q.name)
        replace(q, title)
    for page, content in copy['panels'].items():
        panel(prs.slides[int(page)-1], text, brand, content['findings'], content['action'])
    overview = prs.slides[1]
    t = next(q.table for q in overview.shapes if q.has_table)
    for i, value in enumerate(copy['overview_rows'], 1):
        cell = t.cell(i, 1)
        cell.text = value
        for p in cell.text_frame.paragraphs:
            p.font.name = cfg.THEME_FONT; p.font.size = Pt(10.5)
            p.font.color.rgb = brand.ink; p.space_after = Pt(0)
    for s in list(prs.slides)[1:-1]:
        for q in s.shapes:
            if not q.has_text_frame:
                continue
            if q.text == 'Evidence and implications':
                replace(q, 'What the evidence shows')
            elif q.text == 'Next steps | proposed owners':
                replace(q, 'To resolve next')
            if abs(q.top-Inches(1.78)) < 10:
                for p in q.text_frame.paragraphs:
                    p.font.size = Pt(14)
                    for run in p.runs:
                        run.font.size = Pt(14)
    # Keep map quantities and tiles unchanged. Explain each map's measure.
    demand = prs.slides[2]
    for q in demand.shapes:
        if not q.has_text_frame:
            continue
        if q.text == 'bn L/year; darker = more sales':
            replace(q, 'Provincial totals, not density')
        elif q.text.startswith('Lease offers are not operating capacity.'):
            replace(q, 'LAEA/WGS84. Sites approximate. Lease tanks are conditional. *Magdala location needs verification. Jet excluded.')
    for page in (9, 11):
        s = prs.slides[page-1]
        for q in list(s.shapes):
            if q.has_text_frame and q.text.startswith('Diamonds: Vopak'):
                q._element.getparent().remove(q._element)
                continue
            if q.has_text_frame and q.text.startswith('   Transnet lease offers'):
                replace(q, '   Lease offers (context)\n1 Ladysmith | 2 Standerton\n3 Kroonstad | 4 Bethlehem\n5 Magdala*')
            elif q.has_text_frame and q.top == Inches(1.78) and q.left < Inches(8):
                replace(q, 'Illustrative road cost, R/litre' if page == 9 else 'Illustrative volumes, bn litres/year; road cost, R/litre')
        q = text(s, 'Diamonds: Vopak. Triangles: lease offers (context).',
                 2.30, 6.16, 5.05, .16, 8.5, color=brand.ink)
        q.fill.solid(); q.fill.fore_color.rgb = brand.white
        s.notes_slide.notes_text_frame.text += '\nEditorial map revision: tiles and illustrative rates unchanged. Symbols distinguish cost origins from conditional lease context.'
    # Optional service page: replace generic placeholder prose with a decision sequence.
    s = prs.slides[14]
    replacements = {
        'EVIDENCE GAP | analysis specification, not a populated result': 'OPTIONAL NEXT STAGE | after customer flows and access are established',
        'New storage and investment scope': 'Translate incremental flows into service needs',
        'Evidence required before quantification': 'Confirm usable assets before sizing additions',
    }
    for q in s.shapes:
        if q.has_text_frame:
            if q.text in replacements:
                replace(q, replacements[q.text])
            elif q.left < Inches(8) and q.text.startswith('Incremental accessible flows,'):
                replace(q, 'Use incremental customer deliveries, peak inventory and seasonality to assess receipt, storage and dispatch needs.\nThen test usable tank space, inventory days, turnover and commercial returns.')
            elif q.left < Inches(8) and q.text.startswith('Partial gross/lease stocks,'):
                replace(q, 'Verify product compatibility, working capacity and operating status.\nDetailed sizing follows the market case and remains secondary to fuel integration.')
    for s in prs.slides:
        s.notes_slide.notes_text_frame.text += '\n6 October SCR editorial pass: presentation copy and map hierarchy only. Source observations, example volumes and model inputs unchanged.'
