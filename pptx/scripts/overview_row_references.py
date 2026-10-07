"""Prefix analytical titles with their numbered opening-overview references."""
import re
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN
from brand_configs import vopak as cfg
from scr_editorial import replace

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
        labels=' / '.join(ROW_LABELS[i-1] for i in rows)
        q=next(q for q in s.shapes if q.name=='Title 1')
        base=re.sub(r'^(?:(?:S/C|S|C|R)\d+(?: / )?)+\.\s*','',q.text)
        replace(q,f'{labels}. {base}')
        s.notes_slide.notes_text_frame.text+=f'\nTitle supports overview row(s) {labels}; Overview chevron returns to page 2.'
    overview.notes_slide.notes_text_frame.text+='\nOverview rows numbered continuously 1–7: '+', '.join(ROW_LABELS)+'. Each analytical title starts with its matching row reference(s).'
