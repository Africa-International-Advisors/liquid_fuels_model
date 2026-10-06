"""Story navigation with section highlighting and internal slide links."""
from pptx.util import Pt, Inches
from brand_configs import vopak as cfg


SECTIONS = [('1  SCR overview', 2), ('2  Situation', 3),
            ('3  Complication', 7), ('4  Resolution', 11)]

EXHIBIT_UNITS = {3:'bn litres/year',4:'bn litres/year',5:'bn litres',
                 6:'bn litres/year',8:'thousand bbl/day',9:'R/litre',
                 11:'R/litre; bn litres/year',12:'bn litres/year',
                 13:'bn litres/year',14:'thousand m³'}


def apply_navigation(prs, brand):
    for page, slide in enumerate(prs.slides, 1):
        if page in (1,16):
            continue  # Preserve the supplied photographic cover and closing.
        for q in list(slide.shapes):
            if q.left<Inches(8) and q.has_text_frame and Inches(1.7)<=q.top<Inches(2.25):
                slide.notes_slide.notes_text_frame.text+='\nExhibit description: '+q.text
                q._element.getparent().remove(q._element)
            elif q.left<Inches(8) and not q.has_text_frame and abs(q.top-Inches(2.13))<10 and q.height<Inches(.02):
                q._element.getparent().remove(q._element)
        if page in EXHIBIT_UNITS:
            q=slide.shapes.add_textbox(Inches(.5),Inches(1.82),Inches(3.4),Inches(.23))
            q.name='Exhibit units'
            tf=q.text_frame;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
            p=tf.paragraphs[0];p.text=EXHIBIT_UNITS[page];p.font.name=cfg.THEME_FONT;p.font.size=Pt(10);p.font.color.rgb=brand.ink
        if page>=3:
            for q in slide.shapes:
                if q.has_text_frame and abs(q.top-Inches(1.78))<10:
                    for p in q.text_frame.paragraphs:
                        p.font.name=cfg.THEME_FONT;p.font.size=Pt(15);p.font.bold=True
                        for run in p.runs:
                            run.font.name=cfg.THEME_FONT;run.font.size=Pt(15);run.font.bold=True
        active = 0 if page==2 else 1 if page<=6 else 2 if page<=10 else 3
        for index, (label, first_page) in enumerate(SECTIONS, 1):
            q = next(s for s in slide.shapes if s.name==f'Section navigation {index}')
            q.text_frame.paragraphs[0].text=label
            for p in q.text_frame.paragraphs:
                p.font.name=cfg.THEME_FONT;p.font.size=Pt(13)
                p.font.bold=index-1==active
                p.font.color.rgb=brand.white if index-1==active else brand.accent_primary
            q.fill.solid()
            q.fill.fore_color.rgb=brand.accent_primary if index-1==active else brand.grey_fill
            q.click_action.target_slide=prs.slides[first_page-1]
        slide.notes_slide.notes_text_frame.text+='\nClickable story chevrons: overview p2; Situation p3; Complication p7; Resolution p11.'
