"""Structure the forecast narrative without generating uncalibrated forecasts."""
import json
from pptx.util import Inches, Pt
from pptx.oxml.xmlchemy import OxmlElement
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from supply_review_pages import table, line
from scr_editorial import replace
from brand_configs import vopak as cfg


def add_forecast_story(prs,slide,text,root,brand):
    data=json.loads((root/'story/forecast_story_framework_2026_10_06.json').read_text(encoding='utf-8'))
    s=slide(data['title'],'Authored forecast framework; observed series in reporting evidence snapshots. No new growth rates or fuel forecasts inferred.',json.dumps(data,indent=2))
    text(s,'Market changes | historical evidence, forecast cases and decision outputs',.5,1.78,11.65,.32,14,True)
    line(s,(.5,2.13),(12.15,2.13),brand.ink,.55)
    text(s,'STRUCTURE FOR REVIEW | assumptions and fuel-volume effects remain uncalibrated',.5,2.30,11.65,.28,11,True,brand.accent_primary)
    table(s,data['rows'],.5,2.78,[2.75,3.45,2.85,2.60],3.45,brand,size=11)
    text(s,data['bridge'],.5,6.43,11.65,.28,11.5,True,brand.accent_primary)
    text(s,data['gate'],.5,6.82,11.65,.25,10)
    ids=list(prs.slides._sldIdLst);new=ids.pop();ids.insert(8,new)
    for sid in list(prs.slides._sldIdLst):prs.slides._sldIdLst.remove(sid)
    for sid in ids:prs.slides._sldIdLst.append(sid)
    overview=prs.slides[1];t=next(q.table for q in overview.shapes if q.has_table)
    for row,pages in [(1,[4,5]),(2,[3,6]),(3,[7,9]),(4,[8,9]),(5,[10,11]),(6,[12,13,14]),(7,[15,16,17])]:
        p=t.cell(row,4).text_frame.paragraphs[0];p.clear()
        for i,page in enumerate(pages):
            r=p.add_run();r.text=(' / ' if i else '')+str(page);r.font.name=cfg.THEME_FONT;r.font.size=Pt(11);r.font.color.rgb=brand.accent_primary
            link=OxmlElement('a:hlinkClick');link.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id',overview.part.relate_to(prs.slides[page-1].part,RT.SLIDE));link.set('action','ppaction://hlinksldjump');r._r.get_or_add_rPr().append(link)
    copy={3:'Historical drivers and forecast cases\nUse observed performance as the anchor. Agree growth assumptions and levers; calculate demand and regional effects before calibration.',
          6:'Market share of Vopak in Dbn and Lesedi\nMatch unique customer deliveries to regional demand. Test additional accessible volumes and commercial rights.',
          7:'Potential scope for new investment?\nThe outlook lands priorities, service proposition and timing. Storage follows secured flows and a usable-capacity gap.'}
    for row,value in copy.items():
        t.cell(row,1).text=value
        for p in t.cell(row,1).text_frame.paragraphs:p.font.name=cfg.THEME_FONT;p.font.size=Pt(10.5);p.font.color.rgb=brand.ink;p.space_after=Pt(0)
    for page,s in enumerate(prs.slides,1):
        for q in s.shapes:
            if q.has_text_frame:
                if q.left>Inches(12) and q.top>Inches(7) and q.text.strip().isdigit():replace(q,str(page))
                elif 'pages 12 and 14' in q.text:replace(q,q.text.replace('pages 12 and 14','pages 13 and 15'))
                elif 'Accessibility map p9 and competing routes p10' in q.text:replace(q,q.text.replace('Accessibility map p9 and competing routes p10','Accessibility map p10 and competing routes p11'))
                elif 'pp.4, 9–14' in q.text:replace(q,q.text.replace('pp.4, 9–14','pp.4, 10–15'))
                elif 'Incremental opportunity is on page 13' in q.text:replace(q,q.text.replace('Incremental opportunity is on page 13','Incremental opportunity is on page 14'))
        s.notes_slide.notes_text_frame.text+=f'\nFinal structure: baseline pp3–6; changes pp7–11 (forecast framework p9); outlook pp12–17 (market choices p16, inventory p17). Current page {page}.'
    from scr_navigation import apply_navigation
    apply_navigation(prs,brand)
