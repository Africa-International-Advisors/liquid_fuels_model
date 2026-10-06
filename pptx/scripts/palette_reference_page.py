"""Editable colour reference derived from the actual deck configuration."""
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from brand_pptx import add_themed_slide
from provincial_demand_map import COLOURS


def add_palette_page(prs, text, brand, cfg):
    s = add_themed_slide(prs, 'Header only', brand=brand,
                         title='Presentation palette | colours and HEX codes')
    text(s, 'Reference | colours used in this presentation', .5, 1.78, 11.65, .35, 14, True)
    groups = [
        ('Core presentation colours', [
            ('Vopak blue', cfg.THEME_COLOURS['accent1']),
            ('Secondary blue', cfg.THEME_COLOURS['accent2']),
            ('Text / ink', str(brand.ink)),
            ('White', cfg.THEME_COLOURS['lt1']),
            ('Unassessed / neutral', str(brand.grey_fill)),
            ('Header divider', str(cfg.DIVIDER_HEADER)),
            ('Body divider', str(cfg.DIVIDER_BODY)),
            ('Frame divider', str(cfg.DIVIDER_FRAME)),
        ]),
        ('Sales-map colours | provincial totals, bn litres/year', list(zip(
            ['Below 1', '1 to below 2', '2 to below 4', '4 to below 6', '6 and above'], COLOURS))
            + [('Map background', 'F5F8FB')]),
        ('Other template theme colours', [
            ('Theme dark 2', cfg.THEME_COLOURS['dk2']),
            ('Theme light 2', cfg.THEME_COLOURS['lt2']),
            ('Accent 3', cfg.THEME_COLOURS['accent3']),
            ('Accent 4', cfg.THEME_COLOURS['accent4']),
            ('Accent 5', cfg.THEME_COLOURS['accent5']),
            ('Accent 6', cfg.THEME_COLOURS['accent6']),
        ]),
    ]
    for heading, entries, top in [(groups[0][0], groups[0][1], 2.33),
                                   (groups[1][0], groups[1][1], 3.83),
                                   (groups[2][0], groups[2][1], 5.33)]:
        text(s, heading, .5, top, 11.65, .28, 12, True, brand.accent_primary)
        for i, (label, code) in enumerate(entries):
            x = .5 + (i % 4)*3.0
            y = top + .39 + (i // 4)*.49
            q = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(.38), Inches(.32))
            q.fill.solid(); q.fill.fore_color.rgb = RGBColor.from_string(code)
            q.line.color.rgb = cfg.DIVIDER_HEADER; q.line.width = Pt(.5)
            text(s, label, x+.49, y-.03, 2.35, .21, 10.5)
            text(s, '#'+code.upper(), x+.49, y+.18, 2.35, .20, 10.5, True, brand.accent_primary)
    text(s, 'Typeface: Lato. Sales colours show totals, not density or market share. Grey denotes unassessed demand.',
         .5, 6.90, 11.65, .23, 9)
    text(s, 'Source: supplied Vopak template; pptx/brand_configs/vopak.py; provincial_demand_map.py.',
         .5, 7.16, 10.6, .23, 7.6)
    from copy import deepcopy
    for q in prs.slides[2].shapes:
        if q.left>Inches(10) and q.top>Inches(7) and not (q.has_text_frame and q.text.isdigit()):
            if q.shape_type==13:
                from io import BytesIO
                s.shapes.add_picture(BytesIO(q.image.blob),q.left,q.top,q.width,q.height)
            else:
                s.shapes._spTree.insert_element_before(deepcopy(q._element),'p:extLst')
    s.notes_slide.notes_text_frame.text += '\nReference appendix. Colour values are read from the theme and map palette; no evidence or model assumptions changed.'
    return s
