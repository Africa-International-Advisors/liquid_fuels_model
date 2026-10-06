"""Approved presentation feedback; reuse evidence, not model calculations."""
import json
import re
from copy import deepcopy
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from brand_pptx import add_themed_slide
from brand_configs import vopak as cfg
from supply_review_pages import line, table
from storage_footprint import inventory
from provincial_demand_map import sales
from storage_sensitivity_page import add_storage_sensitivity_page
from scr_editorial import replace, apply_confidentiality, apply_divider_markers
from footer_layout import finish_footer_and_markers


def text(s, value, x, y, w, h, size=12, bold=False, color=None):
    q = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    q.text = value
    tf = q.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for p in tf.paragraphs:
        p.font.name = cfg.THEME_FONT
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = color or RGBColor.from_string(cfg.THEME_COLOURS['accent4'])
        p.space_after = Pt(3)
    return q


def clear_body(s, left_only=False):
    for q in list(s.shapes):
        if Inches(2.3) <= q.top < Inches(7.0) and (not left_only or q.left < Inches(7.6)):
            q._element.getparent().remove(q._element)


def bar(s, x, y, w, h, color, name):
    q = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    q.fill.solid(); q.fill.fore_color.rgb = color; q.line.fill.background(); q.name = name
    return q


def regional_graph(s, root, brand):
    from terminal_turnover_page import add_turnover_graph
    add_turnover_graph(s, root, brand)


def penetration_flow(s, root, brand, map_slide):
    clear_body(s)
    for q in list(s.shapes):
        if Inches(1.7)<=q.top<Inches(2.3):q._element.getparent().remove(q._element)
    for q in s.shapes:
        if q.name == 'Title 1': replace(q, 'R6. Reach and commercial access narrow the illustrative customer opportunity')
    text(s,'Illustrative reach and volume bridge | bn litres/year; customer capture unverified',.5,1.78,11.65,.35,14,True)
    line(s,(.5,2.13),(12.15,2.13),brand.ink,.55)
    text(s,'Durban and Lesedi: illustrative road reach',.5,2.43,4.65,.35,12,True)
    # Reuse the editable geographic exhibit; no new catchment or cost calculation.
    scale=4.55/7.05
    ns='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
    for q in map_slide.shapes:
        if not (Inches(.5)<=q.left<Inches(7.55) and Inches(2.38)<=q.top<Inches(6.70)):
            continue
        if q.name.startswith('Transnet lease overlay:') or (q.has_text_frame and 'Lease offers' in q.text):continue
        el=deepcopy(q._element)
        for node in el.iter():
            for attr,value in list(node.attrib.items()):
                if attr.startswith(ns):
                    rel=map_slide.part.rels[value]
                    node.set(attr,s.part.relate_to(rel.target_ref if rel.is_external else rel.target_part,rel.reltype,is_external=rel.is_external))
        s.shapes._spTree.insert_element_before(el,'p:extLst')
        dest=s.shapes[-1]
        dest.left=int(Inches(.5)+(q.left-Inches(.5))*scale)
        dest.top=int(Inches(3.03)+(q.top-Inches(2.38))*scale)
        dest.width=int(q.width*scale);dest.height=int(q.height*scale)
        if dest.has_text_frame:
            for p in dest.text_frame.paragraphs:
                for font in [p.font]+[r.font for r in p.runs]:
                    if font.size:font.size=Pt(max(7,font.size.pt*scale))
    text(s,'Darker shading = lower example road cost. Physical and commercial access remain unverified.',.5,6.04,4.6,.48,10)
    import csv
    rows=list(csv.DictReader((root/'story/illustrative_market_catchments.csv').open(encoding='utf-8-sig')))
    assessed=[r for r in rows if r['commercial_envelope_bn_l']]
    total,reachable,envelope,current=[sum(float(r[k]) for r in assessed) for k in ['demand_bn_l','feasible_service_bn_l','commercial_envelope_bn_l','current_unique_vopak_bn_l']]
    candidate=envelope-current
    stages=[('Illustrative\nmarket',total,0,total),('Outside\nfeasible reach',total-reachable,reachable,total),('Fails price /\nservice / access',reachable-envelope,envelope,reachable),('Assumed\nalready served',current,candidate,envelope),('Additional\nopportunity to test',candidate,0,candidate)]
    text(s,'Illustrative volume waterfall',5.30,2.43,6.85,.35,12,True)
    x0,ybottom,height,width=5.55,5.76,2.52,.68
    for i,(label,value,bottom,top) in enumerate(stages):
        x=x0+i*1.31; yy=ybottom-height*top/total; hh=height*value/total
        colour=brand.accent_primary if i==4 else (brand.accent_secondary if i==0 else brand.grey_fill)
        bar(s,x,yy,width,hh,colour,f'Illustrative waterfall {label}: {value} bn L/year')
        text(s,('−' if i in (1,2,3) else '')+f'{value:.1f}',x-.13,yy-.35,.95,.28,12)
        text(s,label,x-.22,5.96,1.25,.56,9)
        if i<4:
            level=[total,reachable,envelope,candidate][i]
            line(s,(x+width,ybottom-height*level/total),(x+1.31,ybottom-height*level/total),brand.ink,.6)
    text(s,f'All volumes illustrative. Assumed already served is not verified throughput; the {candidate:.1f} bn L/year remainder is an opportunity to test.',.5,6.63,11.65,.35,11)
    # Keep authored volume examples in notes, rather than presenting them as measured penetration.
    s.notes_slide.notes_text_frame.text += '\nVIS-04: unquantified market-penetration flow. Earlier authored milestones remain illustrations, not measured current or captured volumes. L/M/H cost, reach, service, rights and capacity settings feed the SCN-01 task list.'
    s.notes_slide.notes_text_frame.text+='\nWaterfall uses only existing authored Eastern coastal/inland catchment values. Commercial-screen loss combines commercial constraints; it is not a measured price elasticity or separate rights effect. Current example is not verified Vopak share. All withdrawals/screens are illustrative, not observed lost customers. The inset is the existing page-10 road-cost illustration, with schematic routes and no verified catchment.'


def scenario_framework(s, root, brand):
    clear_body(s)
    for q in s.shapes:
        if q.name == 'Title 1': replace(q, 'S/C3 / C4. L/M/H assumptions define coherent demand, supply and customer-access worlds')
        elif q.has_text_frame and q.top == Inches(1.78): replace(q, 'Scenario design | all key levers and assumptions')
    rows = [
        ['Input family', 'L/M/H settings to agree', 'Outputs and decision'],
        ['Demand', 'Growth, mileage, fleet efficiency/EVs, freight/passenger rail, grid/private generation, sector activity and price response', 'Petrol/diesel demand by year and region'],
        ['Supply and trade', 'Plant output, yields, downtime/compliance, imports, neighbouring-country exports and stocks', 'Domestic supply, trade and transit throughput; residuals explicit'],
        ['Customer access', 'Delivered price, service, feasible routes, rights and switching', 'Reachable and competitively accessible customer litres'],
        ['Capacity and operations', 'Usable tanks, receipt/dispatch, inventory policy, peaks and spare space', 'Unique Vopak flows and any usable-capacity gap'],
    ]
    table(s, rows, .5, 2.42, [2.0, 5.45, 4.20], 2.90, brand, 11)
    text(s, 'Combine settings into coherent worlds', .5, 5.60, 11.65, .30, 14, True)
    for x, heading, body in [(.5, 'Baseline', 'Agreed reference assumptions'), (4.45, 'Ample supply', 'Supply and access comfortably meet demand'), (8.40, 'Tight supply', 'Demand tests available supply and delivery routes')]:
        text(s, heading, x, 6.02, 3.7, .28, 12)
        text(s, body, x, 6.34, 3.7, .46, 10.5)
    s.notes_slide.notes_text_frame.text += '\nSCN-01 design only. L/M/H settings remain proposed/unquantified, with linked assumptions and incompatible combinations to record. Medium demand/medium domestic supply is a proposed reference, not a calibrated forecast. A 3x3 demand/supply matrix summarizes worlds; every key underlying lever needs its own settings. Imports are one output. See feedback_focus_2026-10-06.md SCN-01.1-8.'


def scope_and_appendix(prs, root, brand):
    data = json.loads((root/'story/convergence_document_scope_2026_10_06.json').read_text(encoding='utf-8'))
    new=[]
    for title in ['Appendix', 'About this document']:
        s=add_themed_slide(prs, 'Header only', brand=brand, title=title)
        # Inherit logo and footer from the named corporate layout; no agenda chevrons.
        text(s, 'Source: Week 1 Convergence scope and evidence status, 6 October 2026.', .5, 7.10, 10.2, .22, 7.5)
        if title == 'Appendix':
            text(s, 'The main story ends on page 17.', .5, 2.48, 11.65, .55, 24, True)
            text(s, 'Document scope · Henry storyboard responses · supporting presentation palette', .5, 3.30, 11.65, .90, 19)
            text(s, 'Use the supporting material to trace the evidence, assumptions and remaining work behind the outlook.', .5, 5.40, 10.8, .70, 15)
        else:
            for x, heading, items in [(.5, 'What it covers', data['covers']), (6.60, 'What it does not establish', data['does_not_establish'])]:
                text(s, heading, x, 1.95, 5.55, .35, 17, True)
                line(s, (x, 2.40), (x+5.55, 2.40), brand.ink, .55)
                for i, item in enumerate(items):
                    text(s, item, x, 2.70+i*.82, 5.55, .63, 13)
            text(s, data['status'], .5, 6.34, 11.65, .55, 11)
        s.notes_slide.notes_text_frame.text=json.dumps(data, ensure_ascii=False, indent=2)
        new.append(prs.slides._sldIdLst[-1])
    ids=list(prs.slides._sldIdLst)
    for item in new: ids.remove(item)
    ids[17:17]=new
    for item in list(prs.slides._sldIdLst): prs.slides._sldIdLst.remove(item)
    for item in ids: prs.slides._sldIdLst.append(item)
    for i,s in enumerate(prs.slides,1):
        for q in s.shapes:
            if q.has_text_frame and ('Every Henry storyboard prompt' in q.text):
                replace(q, q.text.replace('18–20', '20–22'))
        s.notes_slide.notes_text_frame.text=s.notes_slide.notes_text_frame.text.replace('pages 18–20', 'pages 20–22')
    # The corporate layout uses a live page-number field; existing literal numbers are refreshed.
    for i,s in enumerate(prs.slides,1):
        for q in s.shapes:
            if q.has_text_frame and q.left>Inches(12) and q.top>Inches(7) and q.text.strip().isdigit(): replace(q,str(i))


def apply_feedback(prs, root, brand):
    assert len(prs.slides)==22
    grey=RGBColor.from_string(cfg.THEME_COLOURS['accent4'])
    verdicts=json.loads((root/'story/overview_story_verdicts_2026_10_06.json').read_text(encoding='utf-8'))
    overview_table=next(q.table for q in prs.slides[1].shapes if q.has_table)
    for col,key in [(2,'evidence'),(3,'verdict')]:
        cell=overview_table.cell(3,col);cell.text=verdicts['rows'][2][key]
        for p in cell.text_frame.paragraphs:
            p.font.name=cfg.THEME_FONT;p.font.size=Pt(10.5);p.font.color.rgb=brand.ink;p.space_after=Pt(0)
    for col,key in [(2,'evidence'),(3,'verdict')]:
        cell=overview_table.cell(6,col);cell.text=verdicts['rows'][5][key]
        for p in cell.text_frame.paragraphs:
            p.font.name=cfg.THEME_FONT;p.font.size=Pt(10.5);p.font.color.rgb=brand.ink;p.space_after=Pt(0)
    regional_graph(prs.slides[12], root, brand)
    from terminal_turnover_page import link_storage_page
    link_storage_page(prs.slides[14], root, brand)
    penetration_flow(prs.slides[13], root, brand, prs.slides[9])
    scenario_framework(prs.slides[8], root, brand)
    inventory_slide=prs.slides[16]
    add_storage_sensitivity_page(inventory_slide, text, root, brand)
    replace(next(q for q in inventory_slide.shapes if q.name=='Title 1'),
            'R7. Inventory policy determines the working stock needed for additional flows')
    for s in prs.slides:
        for q in s.shapes:
            if q.has_text_frame and Inches(2.25)<=q.top<Inches(7.0):
                for p in q.text_frame.paragraphs:
                    for font in [p.font]+[r.font for r in p.runs]:
                        try:
                            if font.color.rgb==brand.accent_primary: font.color.rgb=grey
                        except (AttributeError, TypeError): pass
                        if q.left<Inches(7.6) and font.size and font.size<=Pt(12.5): font.bold=False
            if q.has_chart:
                for plot in q.chart.plots:
                    if plot.has_data_labels: plot.data_labels.font.bold=False
    scope_and_appendix(prs, root, brand)
    finalise_story(prs,root,brand)
    apply_divider_markers(prs, brand)
    apply_confidentiality(prs)
    finish_footer_and_markers(prs, brand)
    assert len(prs.slides)==24
    from convergence_story_order import apply_story_order
    apply_story_order(prs, root, brand)


def finalise_story(prs,root,brand):
    """End the narrative with the outlook; keep inventory in supporting material."""
    ids=list(prs.slides._sldIdLst)
    # Move former story page 17 behind the appendix divider and scope.
    ids=ids[:16]+ids[17:19]+[ids[16]]+ids[19:]
    for item in list(prs.slides._sldIdLst):prs.slides._sldIdLst.remove(item)
    for item in ids:prs.slides._sldIdLst.append(item)
    for page in (0,22):
        for q in prs.slides[page].shapes:
            if q.has_text_frame and q.left<Inches(6.6):
                for p in q.text_frame.paragraphs:
                    p.font.color.rgb=brand.white
                    for r in p.runs:r.font.color.rgb=brand.white
    for q in prs.slides[16].shapes:
        if q.has_text_frame and 'main story ends on page 17' in q.text:replace(q,q.text.replace('page 17','page 16'))
    for q in list(prs.slides[18].shapes):
        if q.name.startswith('Section navigation '):q._element.getparent().remove(q._element)
    overview=next(q.table for q in prs.slides[1].shapes if q.has_table)
    for p in overview.cell(7,4).text_frame.paragraphs:
        for r in p.runs:r.text=r.text.replace('17','19')
    for s in prs.slides:
        for q in s.shapes:
            if q.has_text_frame and q.top>Inches(7) and q.left>Inches(12) and q.text.strip().isdigit():
                replace(q,str(list(prs.slides).index(s)+1))
            if q.has_table:
                for row in q.table.rows:
                    for cell in row.cells:
                        if cell.text.strip()=='15 / 16 / 17':
                            for p in cell.text_frame.paragraphs:
                                for r in p.runs:r.text=r.text.replace('17','19')
    history=prs.slides[4]
    for q in history.shapes:
        if q.has_text_frame and q.text.startswith('The analyst branch corrects'):
            replace(q,'Manish fixed the 2013 parser and traced 2015 to a source revision. Decisions remain on 2014 conflicts and incomplete 2018 coverage.')
    history.notes_slide.notes_text_frame.text+='\nManish handback 4e64c8c: 2013 parser fixed; 2015 revision traced; 2014/2018 treatment still needs Nigel. Provincial GDP supports a held-share estimate but is not observed fuel sales.'


if __name__=='__main__':
    import sys
    from pptx import Presentation
    from brand_pptx import BrandStyle
    root=Path(__file__).resolve().parents[1]
    source, output=map(Path, sys.argv[1:3])
    if source.resolve()==output.resolve(): raise ValueError('Build a separate candidate first')
    prs=Presentation(source)
    apply_feedback(prs, root, BrandStyle.from_module(cfg))
    output.parent.mkdir(parents=True, exist_ok=True)
    for i,s in enumerate(prs.slides,1):
        for q in s.shapes:
            assert q.left>=0 and q.top>=0 and q.left+q.width<=prs.slide_width+10 and q.top+q.height<=prs.slide_height+10,(i,q.name)
    prs.save(output)
    print(output)
