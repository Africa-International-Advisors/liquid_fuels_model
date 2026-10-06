"""Agenda-led opening answer and exhaustive Henry storyboard response appendix."""
import json
from copy import deepcopy
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from brand_pptx import _strip_table_style, cell_bottom_rule
from brand_configs import vopak as cfg
from scr_editorial import replace


def _table(slide, rows, widths, top, height, brand, size=10.5):
    sh=slide.shapes.add_table(len(rows),len(widths),Inches(.5),Inches(top),Inches(sum(widths)),Inches(height))
    t=sh.table;_strip_table_style(t)
    for col,w in zip(t.columns,widths):col.width=Inches(w)
    for i,row in enumerate(rows):
        t.rows[i].height=Inches(.38 if i==0 else (height-.38)/(len(rows)-1))
        for j,value in enumerate(row):
            c=t.cell(i,j);c.text=value;c.margin_left=c.margin_right=Inches(.045)
            c.margin_top=Inches(.045);c.margin_bottom=Inches(.02);c.vertical_anchor=MSO_ANCHOR.TOP
            c.fill.solid();c.fill.fore_color.rgb=brand.white
            for p in c.text_frame.paragraphs:
                p.font.name=cfg.THEME_FONT;p.font.size=Pt(size);p.font.bold=i==0;p.font.color.rgb=brand.ink;p.space_after=Pt(0)
            cell_bottom_rule(c,color=brand.grey_fill,w_pt=.6)
    return t


def _links(slide,cell,pages,prs,brand):
    p=cell.text_frame.paragraphs[0];p.clear()
    for i,page in enumerate(pages):
        r=p.add_run();r.text=(' / ' if i else '')+str(page);r.font.name=cfg.THEME_FONT;r.font.size=Pt(10.5);r.font.color.rgb=brand.accent_primary
        h=OxmlElement('a:hlinkClick');h.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id',slide.part.relate_to(prs.slides[page-1].part,RT.SLIDE));h.set('action','ppaction://hlinksldjump');r._r.get_or_add_rPr().append(h)


def apply_agenda_answer(prs,root,brand):
    overview=prs.slides[1]
    title='Imports are material; Vopak growth depends on accessible customer flows'
    for q in list(overview.shapes):
        if Inches(1.7)<=q.top<Inches(7.05):q._element.getparent().remove(q._element)
        elif q.has_text_frame and Inches(.5)<q.top<Inches(1.6) and q.width>Inches(8):replace(q,title)
    def text(s,value,x,y,w,h,size=11,bold=False,color=None):
        q=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));q.text=value
        q.text_frame.margin_left=q.text_frame.margin_right=0;q.text_frame.margin_top=q.text_frame.margin_bottom=0
        for p in q.text_frame.paragraphs:p.font.name=cfg.THEME_FONT;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=color or brand.ink;p.space_after=Pt(0)
        return q
    text(overview,'Current answer | validate customer access before committing additional capacity',.5,1.78,11.65,.3,14,True)
    rows=[['Agenda','SCR','Current answer and implication','Next step / proposed lead','Deep dives'],
    ['Market\nbaseline','','Imports underpin the national market\n2024 net petrol/diesel imports: 13.078 bn L. Production, stocks and sales coverage remain unmatched.','Match the national balance\nManish; Nigel source access',''],
    ['','','Demand is concentrated, but later provincial data are estimates\nGP, KZN and WC account for 68.6% of reported 2022 sales. The map does not establish customer access.','Refresh observed demand and destinations\nManish; Nigel review',''],
    ['Market\nchanges','','Demand drivers can move in different directions\nPower, freight, prices and vehicle mix need separate mechanisms; observed activity is not a fuel forecast.','Define growth, lever cases and back-tests\nManish; Nigel review',''],
    ['','','Supply change makes import needs conditional\nCapacity has declined; redevelopment is conditional. Secunda/Natref product output and future cases remain open.','Confirm plant status, timing and yields\nManish; Henry review',''],
    ['','','Alternative gateways challenge the same inland market\nMatola and Walvis Bay have storage; their competitiveness depends on full costs, route capacity and access.','Compare one product and destination\nManish; Nigel / Henry',''],
    ['Vopak\noutlook','','Market share of Vopak in Dbn and Lesedi\nShare is not established. Published tanks show footprint; unique customer deliveries establish served demand.','Obtain flows, remove transfers, test capture gates\nNigel client data; Manish',''],
    ['','','Potential scope for new investment?\nPrioritise Durban/Lesedi customer flows. Additional storage follows secured volumes and a usable-capacity gap.','Validate where, how and when to act\nNigel; Manish / Henry','']]
    widths=[1.30,.55,5.05,3.30,1.45]
    t=_table(overview,rows,widths,2.26,4.48,brand,10.5)
    for a,b in [(1,2),(3,5),(6,7)]:
        t.cell(a,0).merge(t.cell(b,0))
        for p in t.cell(a,0).text_frame.paragraphs:p.font.bold=True;p.font.color.rgb=brand.accent_primary
    for i,(pill,pages) in enumerate(zip(['S','S','S/C','C','C','R','R'],[[3,6],[4,5],[7,9],[8,9],[10,11],[12,13,14],[15,16,17]]),1):
        y=2.26+.38+(i-1)*(4.48-.38)/7+.075
        q=overview.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(1.845),Inches(y),Inches(.46),Inches(.27));q.name=f'SCR pill {i}'
        q.fill.solid();q.fill.fore_color.rgb=brand.grey_fill;q.line.fill.background();q.text=pill
        q.text_frame.margin_left=q.text_frame.margin_right=0;q.text_frame.margin_top=q.text_frame.margin_bottom=0;q.text_frame.vertical_anchor=MSO_ANCHOR.MIDDLE
        p=q.text_frame.paragraphs[0];p.alignment=PP_ALIGN.CENTER;p.font.name=cfg.THEME_FONT;p.font.size=Pt(9);p.font.bold=True;p.font.color.rgb=brand.accent_primary
        _links(overview,t.cell(i,4),pages,prs,brand)
    text(overview,'S = Situation   C = Complication   R = Resolution | Every Henry storyboard prompt has a response on pages 18–20; open items remain open.',.5,6.86,11.65,.25,9.5)
    data=json.loads((root/'story/henry_question_answers_2026_10_06.json').read_text(encoding='utf-8'))
    appended=[]
    for section in data['sections']:
        s=prs.slides.add_slide(overview.slide_layout)
        for q in list(s.shapes):q._element.getparent().remove(q._element)
        for q in overview.shapes:
            if q.top<Inches(1.7) or q.top>=Inches(7.05):
                el=deepcopy(q._element)
                for link in list(el.iter()):
                    if link.tag.endswith('hlinkClick'):link.getparent().remove(link)
                s.shapes._spTree.insert_element_before(el,'p:extLst')
        for q in s.shapes:
            if q.has_text_frame:
                if Inches(.5)<q.top<Inches(1.6) and q.width>Inches(8):replace(q,f"Henry storyboard answers | {section['agenda']}")
                elif q.text.startswith('Source:'):replace(q,'Source: Henry storyboard pp30–32; reporting evidence and explicit gaps, 6 Oct 2026. Responses do not establish closure.')
        text(s,f"{section['pill']} | Every prompt addressed; partial and open findings require the stated evidence",.5,1.78,11.65,.32,14,True)
        rs=[['Henry storyboard prompt','Current answer / evidence gap','Deep dives']]+[[v['question'],v['answer'],''] for v in section['questions']]
        tb=_table(s,rs,[3.15,7.05,1.45],2.30,4.52 if len(section['questions'])>2 else 1.80,brand,10)
        for i,v in enumerate(section['questions'],1):_links(s,tb.cell(i,2),v['pages'],prs,brand)
        s.notes_slide.notes_text_frame.text=json.dumps(section,indent=2)
        appended.append(prs.slides._sldIdLst[-1])
    ids=list(prs.slides._sldIdLst)
    for item in appended:ids.remove(item)
    ids[-2:-2]=appended
    for item in list(prs.slides._sldIdLst):prs.slides._sldIdLst.remove(item)
    for item in ids:prs.slides._sldIdLst.append(item)
    for page,s in enumerate(prs.slides,1):
        for q in s.shapes:
            if q.has_text_frame and q.left>Inches(12) and q.top>Inches(7) and q.text.strip().isdigit():replace(q,str(page))
    from scr_navigation import apply_navigation
    apply_navigation(prs,brand)
    for index in range(17,20):
        s=prs.slides[index]
        for q in s.shapes:
            if q.name.startswith('Section navigation '):
                n=int(q.name.rsplit(' ',1)[-1]);active=[2,3,4][index-17]
                q.fill.fore_color.rgb=brand.accent_primary if n==active else brand.grey_fill
                for p in q.text_frame.paragraphs:p.font.bold=n==active;p.font.color.rgb=brand.white if n==active else brand.accent_primary
    overview.notes_slide.notes_text_frame.text+='\nAgenda-led opening answer. Henry prompt-by-prompt current responses are on pages 18–20. Source pp30–32; open is not closed.'
