"""Apply the approved editorial review after the canonical 26-page ordering.

Typography uses explicit roles rather than shrinking individual exhibits.
The only rebuilt exhibit counts existing illustrative terminal transfers once.
"""
import csv
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from pptx.util import Inches, Pt
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.dml.color import RGBColor
from brand_configs import vopak as cfg
from convergence_feedback import text, bar, line, clear_body, replace


def style(q, size, bold=None, color=None):
    tf=q.text_frame
    tf.auto_size=MSO_AUTO_SIZE.NONE
    for p in tf.paragraphs:
        for font in [p.font]+[r.font for r in p.runs]:
            font.name=cfg.THEME_FONT; font.size=Pt(size)
            if bold is not None:font.bold=bold
            if color is not None:font.color.rgb=color


def rewrite_panel(s, copy, brand):
    for q in list(s.shapes):
        if q.left>=Inches(8) and Inches(1.7)<=q.top<Inches(7):
            q._element.getparent().remove(q._element)
    text(s,'Implication for Vopak',8.12,1.78,4.03,.34,14,True,color=brand.ink)
    line(s,(8.12,2.13),(12.15,2.13),brand.ink,.55)
    for i,(heading,body) in enumerate(copy['findings']):
        y=2.39+i*1.08
        text(s,f'{i+1:02d} | {heading}',8.12,y,4.03,.32,12,True)
        text(s,body,8.12,y+.38,4.03,.72,12)
    line(s,(8.12,5.78),(12.15,5.78),brand.accent_primary,.8)
    text(s,'Next action',8.12,5.92,4.03,.30,14,True,color=brand.ink)
    text(s,copy['action'],8.12,6.30,4.03,.60,12)


def unique_deliveries(s, root, brand):
    """Editorial display of the existing transfer example, no new input."""
    clear_body(s,True)
    rows=list(csv.DictReader((root/'story/illustrative_terminal_routes.csv').open(encoding='utf-8-sig')))
    byroute={k:sum(float(r['volume_bn_l']) for r in rows if r['route_id']==k) for k in ['R1','R2','R3','R4']}
    durban=byroute['R1']+byroute['R2'];lesedi=byroute['R2']+byroute['R3']
    total=durban+lesedi;shared=byroute['R2'];unique=total-shared
    assert abs(unique-(byroute['R1']+byroute['R4']))<1e-8
    for q in s.shapes:
        if q.has_text_frame and q.left<Inches(8) and abs(q.top-Inches(1.78))<10:
            replace(q,'Unique customer deliveries | illustrative bn litres/year')
    text(s,f'{durban:.1f} + {lesedi:.1f} − {shared:.1f} = {unique:.1f} bn litres counted once',.5,2.42,7.05,.34,14,True)
    text(s,'Illustrative receipts and shared transfer; actual Vopak flows unverified',.5,2.89,7.05,.30,11)
    stages=[('Durban\nreceipts',durban,0,durban),('Lesedi\nreceipts',lesedi,durban,total),('Remove shared\ntransfer',shared,unique,total),('Unique customer\ndeliveries',unique,0,unique)]
    base=6.05;height=2.38;width=.90;x0=.95;step=1.65
    charcoal=RGBColor.from_string(cfg.THEME_COLOURS['accent4'])
    for i,(label,value,bottom,top) in enumerate(stages):
        x=x0+i*step;y=base-height*top/total
        col=brand.accent_primary if i==3 else (charcoal if i==2 else brand.accent_secondary)
        bar(s,x,y,width,height*value/total,col,'Unique delivery illustration '+label)
        sign='−' if i==2 else ('+' if i==1 else '')
        text(s,sign+f'{value:.1f}',x-.02,y-.35,.94,.30,12)
        text(s,label,x-.12,6.23,1.35,.46,11)
        if i<3:
            level=[durban,total,unique][i]
            line(s,(x+width,base-height*level/total),(x+step,base-height*level/total),charcoal,.6)
    text(s,'Use unique served demand in the additional-opportunity screen on page 15.',.5,6.80,7.05,.20,9)
    s.notes_slide.notes_text_frame.text+='\nPARTNER-REVIEW: p14 now has one job: remove the existing shared-transfer example. Market screens remain on p15. Values read from illustrative_terminal_routes.csv; no actual terminal throughput inferred.'


def apply_partner_review(prs, root, brand):
    assert len(prs.slides)==26
    review=json.loads((root/'story/partner_review_2026_10_07.json').read_text(encoding='utf-8'))
    trade_layout(prs.slides[3],brand)
    refinery_layout(prs.slides[8],brand)
    unique_deliveries(prs.slides[13],root,brand)
    inventory_layout(prs.slides[16],brand)
    for page,title in review['titles'].items():
        s=prs.slides[int(page)-1]
        q=next(q for q in s.shapes if q.name=='Title 1');replace(q,title)
    for page,copy in review['panels'].items():rewrite_panel(prs.slides[int(page)-1],copy,brand)
    # Standard title/subtitle/body roles; compact map/dashboard labels are intentional.
    for page,s in enumerate(prs.slides,1):
        if not 2<=page<=19:continue
        for q in s.shapes:
            if q.has_text_frame:
                if q.name=='Title 1':style(q,24,True,brand.ink)
                elif abs(q.top-Inches(1.78))<Inches(.06):style(q,14,True)
                elif q.name.startswith('Section navigation '):style(q,10.5)
                elif q.top>=Inches(7):continue
                elif page==7 and q.left<Inches(7.8):
                    v=q.text.strip()
                    if q.top>=Inches(6.5):style(q,9)
                    elif v.replace('.','',1).isdigit():style(q,10 if q.top<Inches(2.8) else 12,False)
                    else:style(q,11,False)
                elif page in (13,16) and q.left<Inches(7.8):
                    v=q.text.strip()
                    if q.top>=Inches(6.5):style(q,9)
                    elif v.replace('.','',1).isdigit() and q.top>=Inches(3.5):style(q,12,False)
                    elif q.top<Inches(3.5) and v.replace('.','',1).isdigit():style(q,10,False)
                    elif v in ['EC/KZN','GP/FS/LP/MP/NW','WC','NC','Northern Cape']:style(q,9,False)
                    else:style(q,11)
                elif page==15 and q.top>=Inches(5.9) and q.top<Inches(6.6) and q.left>=Inches(5.2):style(q,11,False)
            if q.has_chart:
                c=q.chart;axis_size=9 if page==8 else 10
                for attr in ('category_axis','value_axis'):
                    try:getattr(c,attr).tick_labels.font.size=Pt(axis_size);getattr(c,attr).tick_labels.font.name=cfg.THEME_FONT
                    except (ValueError,AttributeError):pass
                if c.has_legend:c.legend.font.size=Pt(11);c.legend.font.name=cfg.THEME_FONT
                for plot in c.plots:
                    if plot.has_data_labels:
                        plot.data_labels.font.size=Pt(12);plot.data_labels.font.name=cfg.THEME_FONT;plot.data_labels.font.bold=False
                for node in c._chartSpace.xpath('.//c:dLbl//a:defRPr'):
                    node.set('sz','1200')
        s.notes_slide.notes_text_frame.text+='\nEDITORIAL-REVIEW 7 Oct: evidence-led title and implication/action copy. Fixed type roles: title24, subtitle14, panel/body12, chart labels11, values12, axes10; compact map/dashboard9, source7.5. Existing input vintage and uncertainty remain unchanged.'
    # Match the overview narrative to the revised jobs without changing its links.
    t=next(q.table for q in prs.slides[2].shapes if q.has_table)
    for col,value in [(2,'Footprint → unique deliveries → opportunity → handling\nAnchor Durban/Lesedi, remove shared transfers, screen customers and test annual handling.'),(3,'Prioritise accessible customer flows.\nVerify usable fuel space, cost/service, rights and unique deliveries before claiming share.')]:
        c=t.cell(6,col);c.text=value
        for p in c.text_frame.paragraphs:p.font.name=cfg.THEME_FONT;p.font.size=Pt(10.5);p.font.color.rgb=brand.ink
    # Fix references that were left behind by the earlier reordering.
    for q in prs.slides[4].shapes:
        if q.has_text_frame and q.name=='Unified source footer':
            replace(q,'Note: Provincial totals, not density. Operator footprint on p13; handling on p16. Jet excluded.\nSource: DMPR 2022 sales; geoBoundaries/OCHA/MDB 2020 provinces; operator inventory and evidence in notes.')
    for q in prs.slides[12].shapes:
        if not q.has_text_frame:continue
        if q.text=='NC':q.top=Inches(6.34);q.height=Inches(.18)
        elif q.text.startswith('Partial inventory;'):q.top=Inches(6.56);q.height=Inches(.18)
        elif q.name=='Unified source footer':replace(q,'Source: Vopak; Bidvest; Burgan Cape; Transnet lease RFPs (5 Oct 2026). Operator sources and capacity bases in notes.')
    for q in prs.slides[15].shapes:
        if q.has_text_frame and q.text.startswith('Historical 2022 sales vs inventory'):
            replace(q,'2022 demand vs 2026 mixed-product inventory; incomplete coverage. No shortage or share conclusion.')
            q.top=Inches(6.78);q.height=Inches(.18);style(q,9)
    from footer_layout import finish_footer_and_markers
    finish_footer_and_markers(prs,brand)
    from driver_split import split_drivers
    split_drivers(prs,root,brand)
    from fuel_lever_pages import add_fuel_lever_pages
    add_fuel_lever_pages(prs,root,brand)


def refinery_layout(s,brand):
    removed=[]
    for q in list(s.shapes):
        if q.has_text_frame and q.left<Inches(8):
            if q.text.startswith(('History 2016','Reported FY2024 output:')):
                removed.append(q.text);q._element.getparent().remove(q._element)
            elif q.text.startswith(('A |','B |')):q.top=Inches(2.45);q.height=Inches(.35)
            elif q.text.startswith('2036:'):q.top=Inches(6.17);q.height=Inches(.30)
        if q.has_chart:
            q.top=Inches(2.95);q.height=Inches(3.05)
            for axis in (q.chart.value_axis,q.chart.category_axis):
                axis.has_major_gridlines=False;axis.has_minor_gridlines=False
    if removed:s.notes_slide.notes_text_frame.text+='\nRefinery exhibit caveats moved to speaker notes:\n'+'\n'.join(removed)


def trade_layout(s,brand):
    """Remove the duplicate lower accounting prose; let the trade chart speak."""
    removed=[]
    for q in list(s.shapes):
        if q.left<Inches(7.8) and Inches(5.7)<=q.top<Inches(7):
            if q.has_text_frame and q.text.startswith('Net imports:'):continue
            if q.has_text_frame:removed.append(q.text)
            q._element.getparent().remove(q._element)
    q=next(q for q in s.shapes if q.has_chart)
    q.height=Inches(3.30)
    for axis in (q.chart.value_axis,q.chart.category_axis):
        axis.has_major_gridlines=False;axis.has_minor_gridlines=False
    for item in s.shapes:
        if item.has_text_frame and item.text.startswith('Net imports:'):
            item.top=Inches(6.66);item.height=Inches(.26);style(item,11,False)
    trade_legend(s,brand)
    if removed:s.notes_slide.notes_text_frame.text+='\nLower duplicate accounting blocks moved to notes:\n'+'\n'.join(removed)
    s.notes_slide.notes_text_frame.text+='\n7 Oct trade layout: enlarge the grouped trade/sales chart, remove gridlines and retain one net-import summary. Source selection and residual are explained once in the RHS panel. Chart values unchanged.'


def trade_legend(s,brand):
    """Editable compact key in the exhibit header; swatches match chart fills."""
    for q in list(s.shapes):
        legacy=q.left<Inches(7.8) and Inches(2.9)<=q.top<Inches(3.17)
        if legacy or q.name.startswith('Trade custom legend '):
            q._element.getparent().remove(q._element)
    for q in s.shapes:
        if q.has_text_frame and q.left<Inches(8) and abs(q.top-Inches(1.78))<10:
            replace(q,'Petrol + diesel | 2024, bn litres');q.width=Inches(3.60)
    c=next(q.chart for q in s.shapes if q.has_chart)
    c.has_legend=False
    export_colour=RGBColor.from_string('D9D9D9')
    for series,colour in zip(c.series,[brand.accent_primary,brand.accent_secondary,export_colour]):
        series.format.fill.solid();series.format.fill.fore_color.rgb=colour
        series.format.line.fill.background()
    for x,label,width,colour in [(4.24,'Sales proxy',1.08,brand.accent_primary),(5.63,'Imports',.70,brand.accent_secondary),(6.65,'Exports',.70,export_colour)]:
        bar(s,x,1.895,.12,.12,colour,'Trade custom legend swatch '+label)
        q=text(s,label,x+.18,1.82,width,.24,11,False,color=brand.ink)
        q.name='Trade custom legend label '+label
    s.notes_slide.notes_text_frame.text+='\nCustom legend: editable header key, Sales proxy / Imports / Exports. Exports darkened to #D9D9D9 for visibility; bar and swatch match. Reported sales remain an unverified consumption proxy; series values unchanged.'


def inventory_layout(s,brand):
    """Chart left, evidence right; keep the native sensitivity data unchanged."""
    q=next(q for q in s.shapes if q.has_chart)
    q.left=Inches(.5);q.top=Inches(2.72);q.width=Inches(7.05);q.height=Inches(3.52)
    for axis in (q.chart.value_axis,q.chart.category_axis):
        axis.has_major_gridlines=False;axis.has_minor_gridlines=False
    for item in list(s.shapes):
        if not item.has_text_frame:continue
        if item.text.startswith('Illustrative 5.5'):
            item.left=Inches(.5);item.top=Inches(2.40);item.width=Inches(7.05);item.height=Inches(.27)
            replace(item,'Illustrative 5.5 bn litres/year; uniform daily flow');style(item,11,False)
        elif item.text=='Working inventory, thousand m³':item.width=Inches(7.05)
        elif item.text=='Inventory days':item.width=Inches(7.05);style(item,11,False)
        elif item.text.startswith('Working stock, not new capacity:'):
            item._element.getparent().remove(item._element)
    # Match the filled brand divider used by the surrounding evidence pages.
    from pptx.enum.shapes import MSO_SHAPE
    for item in list(s.shapes):
        if item.name.startswith('Inventory evidence divider'):
            item._element.getparent().remove(item._element)
    d=line(s,(7.80,2.13),(7.80,6.90),RGBColor.from_string(cfg.THEME_COLOURS['accent4']),.55)
    d.name='Inventory evidence divider line'
    circle=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(7.66),Inches(1.99),Inches(.28),Inches(.28))
    circle.fill.solid();circle.fill.fore_color.rgb=brand.accent_primary;circle.line.fill.background();circle.name='Inventory evidence divider circle'
    for a,b in [((7.77,2.07),(7.83,2.13)),((7.83,2.13),(7.77,2.19))]:
        arrow=line(s,a,b,brand.white,.9);arrow.name='Inventory evidence divider arrow'
    line(s,(.5,2.13),(7.55,2.13),brand.ink,.55).name='Inventory evidence divider header'
    s.notes_slide.notes_text_frame.text+='\n7 Oct inventory layout: chart narrowed into the standard left exhibit, all major/minor gridlines removed. Evidence/implication and action panel added on the right. Values and 14-day highlight unchanged.'


if __name__=='__main__':
    import sys
    from pptx import Presentation
    from brand_pptx import BrandStyle
    root=Path(__file__).resolve().parents[1]
    p=Presentation(sys.argv[1]);apply_partner_review(p,root,BrandStyle.from_module(cfg))
    p.save(sys.argv[2]);print(f'Reviewed {len(p.slides)}-page canonical storyline and typography')
