"""Story navigation with section highlighting and internal slide links."""
from pptx.util import Pt, Inches
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR
from brand_configs import vopak as cfg


SECTIONS = [('1  Overview', 2), ('2  Market baseline', 3),
            ('3  Market changes', 7), ('4  Vopak outlook', 12)]


def apply_navigation(prs, brand):
    for page, slide in enumerate(prs.slides, 1):
        if not any(q.name=='Section navigation 1' for q in slide.shapes):
            continue  # Preserve the supplied photographic cover and closing.
        retained_headings={9:'Road-delivery accessibility | illustrative transport cost, R/litre',
                           11:'Illustrative road cost (R/litre) and market volumes'}
        if page in retained_headings and not any(q.has_text_frame and q.left<Inches(8) and abs(q.top-Inches(1.78))<10 for q in slide.shapes):
            q=slide.shapes.add_textbox(Inches(.5),Inches(1.78),Inches(7.05),Inches(.42))
            tf=q.text_frame;tf.margin_left=tf.margin_right=Inches(.025);tf.margin_top=tf.margin_bottom=0
            tf.paragraphs[0].text=retained_headings[page];tf.paragraphs[0].font.color.rgb=brand.ink
            rule=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(.5),Inches(2.13),Inches(7.55),Inches(2.13))
            rule.line.color.rgb=brand.ink;rule.line.width=Pt(.55)
        for q in list(slide.shapes):
            if q.name.startswith('SCR backlink') or q.name=='Exhibit units':
                q._element.getparent().remove(q._element)
            elif q.has_text_frame and abs(q.top-Inches(1.78))<10:
                for p in q.text_frame.paragraphs:
                    p.font.name=cfg.THEME_FONT;p.font.size=Pt(14);p.font.bold=True
                    for run in p.runs:
                        run.font.name=cfg.THEME_FONT;run.font.size=Pt(14);run.font.bold=True
        active = 0 if page==2 else 1 if page<=6 else 2 if page<=11 else 3
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
        slide.notes_slide.notes_text_frame.text+='\nFinal story navigation: Overview p2; Market baseline p3; Market changes p7; Vopak outlook p12. Henry SCR naming remains in the overview.'

    compact_navigation(prs)

def compact_navigation(prs):
    """Keep navigation visibly subordinate to the slide title."""
    for slide in prs.slides:
        for q in slide.shapes:
            if not q.name.startswith('Section navigation '):
                continue
            q.height=Inches(.28)
            q.text_frame.margin_top=q.text_frame.margin_bottom=0
            q.text_frame.vertical_anchor=MSO_ANCHOR.MIDDLE
            for p in q.text_frame.paragraphs:
                p.font.size=Pt(10.5)
                for r in p.runs:r.font.size=Pt(10.5)
