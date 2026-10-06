"""Link analytical pages back to numbered rows in the opening overview."""
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from brand_configs import vopak as cfg

ROW_LABELS=['S1','S2','S/C3','C4','C5','R6','R7']
PAGE_ROWS={3:[1],4:[2],5:[2],6:[1],7:[3],8:[4],9:[3,4],10:[5],11:[5],12:[6],13:[6],14:[6],15:[7],16:[7],17:[7],18:[1,2,3,4],19:[3,4,5],20:[6,7]}

def apply_row_references(prs,brand):
    overview=prs.slides[1]
    for i,label in enumerate(ROW_LABELS,1):
        q=next(q for q in overview.shapes if q.name==f'SCR pill {i}')
        q.text_frame.paragraphs[0].text=label
        for p in q.text_frame.paragraphs:
            p.font.name=cfg.THEME_FONT;p.font.size=Pt(8);p.font.bold=True;p.font.color.rgb=brand.accent_primary;p.alignment=PP_ALIGN.CENTER
    for page,rows in PAGE_ROWS.items():
        s=prs.slides[page-1]
        for q in list(s.shapes):
            if q.name=='Overview row reference':q._element.getparent().remove(q._element)
            elif q.has_text_frame and q.text.startswith('Source:') and q.width>Inches(8.35):q.width=Inches(8.35)
        labels=' / '.join(ROW_LABELS[i-1] for i in rows)
        q=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(9.0),Inches(7.13),Inches(1.80),Inches(.19))
        q.name='Overview row reference';q.fill.solid();q.fill.fore_color.rgb=brand.grey_fill;q.line.fill.background()
        q.text=labels;q.text_frame.margin_left=q.text_frame.margin_right=0;q.text_frame.margin_top=q.text_frame.margin_bottom=0;q.text_frame.vertical_anchor=MSO_ANCHOR.MIDDLE
        p=q.text_frame.paragraphs[0];p.font.name=cfg.THEME_FONT;p.font.size=Pt(8);p.font.bold=True;p.font.color.rgb=brand.accent_primary;p.alignment=PP_ALIGN.CENTER
        q.click_action.target_slide=overview
        s.notes_slide.notes_text_frame.text+=f'\nSupports overview row(s) {labels}; clickable footer badge returns to page 2.'
    overview.notes_slide.notes_text_frame.text+='\nOverview rows numbered continuously 1–7: '+', '.join(ROW_LABELS)+'. Analytical pages have clickable matching row references in the footer.'
