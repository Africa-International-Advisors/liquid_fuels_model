"""Approved presentation feedback; reuse evidence, not model calculations."""
import json
import re
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
    clear_body(s, True)
    values, _, _ = sales(root)
    import csv
    members = list(csv.DictReader((root/'story/demand_map_regions_2026_10_06.csv').open(encoding='utf-8-sig')))
    names = ['Eastern coastal', 'Inland', 'Western coastal', 'Other / Northern Cape']
    demand = [sum(values[r['province_code']] for r in members if r['region'] == n) for n in names]
    sites = inventory(root)
    locations = [['Durban', 'Richards Bay'], ['Lesedi', 'Isando'], ['Cape Town'], []]
    for q in s.shapes:
        if q.has_text_frame and q.top == Inches(1.78) and q.left < Inches(8):
            replace(q, 'Historical demand and published tanks | separate scales')
        elif q.name == 'Title 1':
            replace(q, 'R6. Vopak’s published tanks sit in the two largest regional demand markets')
    text(s, 'Reported demand\nbn litres/year', 2.05, 2.40, 2.1, .52, 11, True)
    text(s, 'Published storage\nthousand m³', 4.72, 2.40, 2.6, .52, 11, True)
    for x, label, colour in [(4.72, 'Vopak', brand.accent_primary), (5.80, 'Other listed', brand.accent_secondary)]:
        bar(s, x, 3.04, .11, .11, colour, 'Storage legend')
        text(s, label, x+.16, 2.99, 1.3, .24, 9.5)
    for x, width, maximum, ticks in [(2.05, 1.82, 12, [0, 4, 8, 12]), (4.72, 1.70, 1000, [0, 500, 1000])]:
        for tick in ticks:
            xx = x+width*tick/maximum
            text(s, str(tick), xx-.12, 3.26, .5, .22, 9)
            line(s, (xx, 3.57), (xx, 6.12), brand.grey_fill, .5)
    labels = [('Eastern coast', 'EC/KZN'), ('Inland', 'GP/FS/LP/MP/NW'), ('Western coast', 'WC'), ('Other', 'Northern Cape')]
    for i, (label, provinces) in enumerate(labels):
        y = 3.65+i*.63
        text(s, label, .5, y, 1.45, .25, 11)
        text(s, provinces, .5, y+.28, 1.50, .23, 9)
        w = 1.82*demand[i]/12
        bar(s, 2.05, y+.12, w, .23, brand.accent_primary, f'Reported demand {names[i]}: {demand[i]} bn L/year')
        text(s, f'{demand[i]:.2f}', 2.05+w+.05, y+.10, .60, .25, 11)
        for j, is_vopak in enumerate([True, False]):
            selected = [r for r in sites if r['site'] in locations[i] and (r['operator']=='Vopak') == is_vopak and r.get('gross_capacity_m3')]
            yy = y+j*.23
            if selected:
                capacity = sum(float(r['gross_capacity_m3']) for r in selected)/1000
                w = 1.70*capacity/1000
                bar(s, 4.72, yy, w, .17, brand.accent_primary if is_vopak else brand.accent_secondary,
                    f'Published gross {names[i]} {"Vopak" if is_vopak else "other"}: {capacity} thousand m3')
                text(s, f'{capacity:,.1f}', 4.72+w+.07, yy-.04, .70, .25, 10)
            else:
                text(s, '—' if is_vopak else '?', 4.72, yy-.04, .5, .25, 11)
    text(s, '— no listed Vopak site   ? capacity unknown', .5, 6.35, 7.05, .25, 10)
    text(s, f'2022 total {sum(demand):.2f} bn L; petrol + diesel, jet excluded. Partial gross inventory; mixed products and missing Sasol/Transnet values. Tanks do not establish annual deliveries or market share.',
         .5, 6.68, 7.05, .30, 8.5)
    s.notes_slide.notes_text_frame.text += '\nVIS-05: demand and storage have separate linear scales; capacity sums retain the earlier regional inventory selection. No listed site is not zero customer reach; unknown capacity is not zero. No model calculation changed.'


def penetration_flow(s, root, brand):
    clear_body(s, True)
    for q in s.shapes:
        if q.name == 'Title 1': replace(q, 'R6. Greater market penetration depends on reach, price, service and customer access')
        elif q.has_text_frame and q.top == Inches(1.78) and q.left < Inches(8): replace(q, 'From total market to customer volumes | gates to test')
    labels = [
        ('Total market (TAM)', 'Same product, year and customer geography'),
        ('Infrastructure reach', 'Feasible routes; compatible receipt and dispatch'),
        ('Competitive price × service', 'Full delivered cost and service versus alternatives'),
        ('Commercial customer access', 'Contracts, rights and ability to switch'),
        ('Captured unique deliveries', 'Additional customer litres; shared transfers removed'),
    ]
    for i, (heading, body) in enumerate(labels):
        y = 2.43+i*.68
        q = s.shapes.add_shape(MSO_SHAPE.CHEVRON, Inches(.58), Inches(y+.03), Inches(.28), Inches(.26))
        q.fill.solid(); q.fill.fore_color.rgb=brand.accent_primary; q.line.fill.background()
        text(s, heading, 1.02, y, 5.8, .27, 13, True)
        text(s, body, 1.02, y+.30, 6.1, .25, 10.5)
    text(s, 'Today’s served volumes + additional candidates that pass every gate', .5, 6.12, 7.05, .35, 12, True)
    text(s, 'Current share and additional capture remain unquantified. Capacity, delivered cost and customer rights limit the addressable catchment.', .5, 6.62, 7.05, .36, 10)
    # Keep authored volume examples in notes, rather than presenting them as measured penetration.
    s.notes_slide.notes_text_frame.text += '\nVIS-04: unquantified market-penetration flow. Earlier authored milestones remain illustrations, not measured current or captured volumes. L/M/H cost, reach, service, rights and capacity settings feed the SCN-01 task list.'
    for q in s.shapes:
        if not q.has_text_frame or q.left < Inches(8): continue
        if q.text.startswith('01 |'): replace(q, '01 | Reach defines a candidate market')
        elif q.text.startswith('02 |'): replace(q, '02 | Price and service determine competitiveness')
        elif q.text.startswith('03 |'): replace(q, '03 | Customer access determines capture')
        elif q.text.startswith(('Accessibility map', 'Maps locate')): replace(q, 'Routes locate potential customers. Receipt, dispatch and product constraints limit physical reach.')
        elif q.text.startswith(('The current example', '3.0 current')): replace(q, 'Compare full delivered cost and service with alternatives for the same customer, product and period.')
        elif q.text.startswith(('Evidence cost', 'Count an increment')): replace(q, 'Test contracts and switching. Count unique final deliveries; keep unknown and failed gates explicit.')


def scenario_framework(s, root, brand):
    clear_body(s)
    for q in s.shapes:
        if q.name == 'Title 1': replace(q, 'S/C3 / C4. L/M/H assumptions define coherent demand, supply and customer-access worlds')
        elif q.has_text_frame and q.top == Inches(1.78): replace(q, 'Scenario design | all key levers and assumptions')
    rows = [
        ['Input family', 'L/M/H settings to agree', 'Outputs and decision'],
        ['Demand', 'Growth, activity, mileage, fleet efficiency/EVs, freight mode, power diesel use and price response', 'Petrol/diesel demand by year and region'],
        ['Supply and trade', 'Plant output, yields, downtime, restart timing, import availability, exports and stocks', 'Domestic supply and required trade; residuals explicit'],
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
    regional_graph(prs.slides[12], root, brand)
    penetration_flow(prs.slides[13], root, brand)
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
    apply_divider_markers(prs, brand)
    apply_confidentiality(prs)
    finish_footer_and_markers(prs, brand)
    assert len(prs.slides)==24


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
