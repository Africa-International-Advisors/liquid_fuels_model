"""Authored market priorities and decision gates; no capture model is executed."""
import json
from pptx.util import Inches, Pt
from pptx.oxml.xmlchemy import OxmlElement
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from supply_review_pages import table, line
from scr_editorial import replace


def add_market_playbook(prs,slide,text,root,brand):
    data=json.loads((root/'story/market_playbook_2026_10_06.json').read_text(encoding='utf-8'))
    s=slide(data['title'],'Authored market hypotheses; demand, gateway and storage evidence on pp.4, 9–14. Customer capture remains unverified.',json.dumps(data,indent=2))
    draw_market_playbook(s,text,root,brand)
    ids=list(prs.slides._sldIdLst); new=ids.pop()
    ids.insert(14,new)
    for sid in list(prs.slides._sldIdLst):prs.slides._sldIdLst.remove(sid)
    for sid in ids:prs.slides._sldIdLst.append(sid)
    overview=prs.slides[1];t=next(q.table for q in overview.shapes if q.has_table)
    # R2 now points to published assets, market outlook and inventory sizing.
    cell=t.cell(7,4);p=cell.text_frame.paragraphs[0];p.clear()
    for i,page in enumerate([14,15,16]):
        run=p.add_run();run.text=(' / ' if i else '')+str(page)
        run.font.size=Pt(11);run.font.color.rgb=brand.accent_primary
        link=OxmlElement('a:hlinkClick')
        link.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id',overview.part.relate_to(prs.slides[page-1].part,RT.SLIDE))
        link.set('action','ppaction://hlinksldjump');run._r.get_or_add_rPr().append(link)
    t.cell(7,1).text='Market outlook and optional investment\nPrioritise markets, validate service/cost and secure flows. Size storage after usable-capacity and operating checks.'
    from brand_configs import vopak as cfg
    for p in t.cell(7,1).text_frame.paragraphs:
        p.font.name=cfg.THEME_FONT;p.font.size=Pt(10.5);p.font.color.rgb=brand.ink;p.space_after=Pt(0)
    for page,s in enumerate(prs.slides,1):
        for q in s.shapes:
            if q.has_text_frame and q.left>Inches(12) and q.top>Inches(7) and q.text.strip().isdigit():replace(q,str(page))
    from scr_navigation import apply_navigation
    apply_navigation(prs,brand)


def outlook_icon(s,kind,x,y,brand):
    from pptx.enum.shapes import MSO_SHAPE
    def ring(dx,dy,w,h):
        q=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x+dx),Inches(y+dy),Inches(w),Inches(h))
        q.fill.background();q.line.color.rgb=brand.accent_primary;q.line.width=Pt(1.2)
        q.name='Outlook icon: '+kind
    ring(0,0,.28,.28)
    if kind=='target':ring(.07,.07,.14,.14)
    elif kind=='location':
        ring(.105,.07,.07,.07)
        line(s,(x+.07,y+.22),(x+.14,y+.34),brand.accent_primary,1.2)
        line(s,(x+.14,y+.34),(x+.21,y+.22),brand.accent_primary,1.2)
    elif kind=='clock':
        line(s,(x+.14,y+.04),(x+.14,y+.14),brand.accent_primary,1.2)
        line(s,(x+.14,y+.14),(x+.22,y+.14),brand.accent_primary,1.2)
    else:
        line(s,(x+.07,y+.15),(x+.12,y+.20),brand.accent_primary,1.2)
        line(s,(x+.12,y+.20),(x+.22,y+.08),brand.accent_primary,1.2)


def draw_market_playbook(s,text,root,brand):
    data=json.loads((root/'story/market_playbook_2026_10_06.json').read_text(encoding='utf-8'))
    text(s,'Market outlook | priority hypotheses and conditional timing',.5,1.78,11.65,.32,14,True)
    line(s,(.5,2.13),(12.15,2.13),brand.ink,.55)
    for x,kind in zip([.55,2.85,5.95,9.00],['location','target','clock','check']):
        outlook_icon(s,kind,x,2.40,brand)
    table(s,data['rows'],.5,2.85,[2.30,3.10,3.05,3.20],2.91,brand,size=11.5)
    text(s,'Investment gate',.5,5.96,11.65,.25,12,True,brand.accent_primary)
    text(s,data['investment_gate'],.5,6.26,11.65,.38,11.5)
    text(s,'Nigel: '+data['nigel_action'],.5,6.66,5.62,.32,9.5)
    text(s,'Manish: '+data['manish_action'],6.45,6.66,5.70,.32,9.5)
