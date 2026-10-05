"""Sourced company context, separate from fuel-model assumptions and outputs."""
import json
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR


def compact(shape):
    for row in shape.table.rows:
        for cell in row.cells:
            cell.margin_top=cell.margin_bottom=Inches(.02)
            for p in cell.text_frame.paragraphs:
                p.space_after=Pt(0);p.line_spacing=1.0


def draw_financials(slide,index,root,brand,text,table):
    d=json.loads((root/'story/vopak-h1-2026.json').read_text(encoding='utf-8'))
    text(slide,'Vopak H1 2026 | six months to 30 June | EUR million unless stated'+(' | rounded to whole numbers' if index==53 else ''),.55,1.8,11.5,.35,14)
    if index==53:
        text(slide,'Group income and cash flows',.55,2.32,6.5,.35,17,True)
        for x,label,color in [(.55,'H1 2026',brand.accent_primary),(2.15,'H1 2025',brand.grey_fill)]:
            swatch=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(2.83),Inches(.27),Inches(.11))
            swatch.fill.solid();swatch.fill.fore_color.rgb=color;swatch.line.fill.background()
            text(slide,label,x+.38,2.78,1.15,.24,10)
        zero=4.22;scale=2.1/700
        axis=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(zero),Inches(3.12),Inches(zero),Inches(5.78))
        axis.line.color.rgb=brand.ink;axis.line.width=Pt(.5)
        metrics=[('Revenue',0),('EBITDA*',1),('EBIT',2),('Net profit (ordinary holders)',3),('Operating cash (gross)',5),('Investing cash',6),('Financing cash',7)]
        for i,(label,idx) in enumerate(metrics):
            y=3.17+i*.37
            text(slide,label,.55,y,2.65,.3,11)
            for j,(v,color) in enumerate([(d['group'][idx][1],brand.accent_primary),(d['group'][idx][2],brand.grey_fill)]):
                yy=y+j*.145
                bar=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(zero+min(v,0)*scale),Inches(yy),Inches(abs(v)*scale),Inches(.10))
                bar.fill.solid();bar.fill.fore_color.rgb=color;bar.line.fill.background()
                xx=zero+v*scale+.05 if v>=0 else zero+v*scale-.55
                text(slide,f'{v:.0f}',xx,yy-.035,.6,.2,9)
        text(slide,'0',zero-.05,5.81,.22,.17,8)
        text(slide,f"EPS, EUR/share: {d['group'][4][1]:.0f} / {d['group'][4][2]:.0f} (2026 / 2025; rounded)",.55,5.85,6.5,.25,11,True)
        text(slide,'Revenue by service',7.4,2.32,4.7,.35,17,True)
        for i,(label,a,b) in enumerate(d['services']):
            y=2.95+i*.66
            text(slide,label,7.4,y,4.55,.22,12,True)
            bar=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(7.4),Inches(y+.29),Inches(3.3*a/677.1),Inches(.12))
            bar.fill.solid();bar.fill.fore_color.rgb=brand.accent_primary;bar.line.fill.background()
            text(slide,f'{a:.0f}  |  {a/677.1:.0%}',10.7,y+.23,1.5,.25,11)
        text(slide,'Service mix is revenue, not profit. Storage and handling earnings are not disclosed separately.',7.4,5.82,4.65,.6,11)
        text(slide,'*EBITDA excludes exceptional items (APM). EBIT and net profit include them. H1 2025 profit included the AVTL listing gain.',.55,6.18,6.5,.5,11)
        text(slide,'Study implication: assess contracted capacity, handling demand and costs in South Africa; test customer commitments at Walvis Bay; screen commercially accessible African flows.',.55,6.72,11.5,.4,10,True)
    elif index==54:
        text(slide,'Proportional results, excluding exceptional items | common scale within each panel',.55,2.32,11.5,.35,13)
        for x,label,color in [(9.0,'H1 2026',brand.accent_primary),(10.65,'H1 2025',brand.grey_fill)]:
            bar=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(2.08),Inches(.28),Inches(.12))
            bar.fill.solid();bar.fill.fore_color.rgb=color;bar.line.fill.background()
            text(slide,label,x+.38,2.03,1.1,.23,10)
        text(slide,'Business unit',.55,2.88,2.5,.3,13,True)
        text(slide,'Revenue',3.2,2.88,3.4,.3,15,True)
        text(slide,'EBITDA',7.3,2.88,4.7,.3,15,True)
        text(slide,'Storage occupancy',11.0,2.82,1.2,.5,10,True)
        rev0=3.2; revscale=3.2/300
        ebit0=8.03; ebitscale=3.65/240
        zero=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(ebit0),Inches(3.25),Inches(ebit0),Inches(6.06))
        zero.line.color.rgb=brand.ink;zero.line.width=Pt(.5)
        for i,(label,revenue,a,b,occ) in enumerate(d['regions'][:-1]):
            y=3.29+i*.39
            text(slide,label.replace('Global functions / corporate','Corporate / global'),.55,y,2.55,.32,11)
            text(slide,occ,11.55,y+.035,.6,.25,10)
            for j,(r,e,color) in enumerate([(revenue,a,brand.accent_primary),(d['regional_revenue_2025'][i],b,brand.grey_fill)]):
                yy=y+j*.145
                bar=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(rev0),Inches(yy),Inches(r*revscale),Inches(.10))
                bar.fill.solid();bar.fill.fore_color.rgb=color;bar.line.fill.background()
                text(slide,f'{r:.1f}',rev0+r*revscale+.05,yy-.035,.6,.19,9)
                bar=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(ebit0+min(e,0)*ebitscale),Inches(yy),Inches(abs(e)*ebitscale),Inches(.10))
                bar.fill.solid();bar.fill.fore_color.rgb=color;bar.line.fill.background()
                text(slide,f'{e:.1f}',ebit0+e*ebitscale+.05 if e>=0 else ebit0+e*ebitscale-.57,yy-.035,.6,.19,9)
        text(slide,'Group: revenue 969.0 / 982.1; EBITDA 600.3 / 615.3 (2026 / 2025); 2026 occupancy 91%.',.55,6.17,11.5,.27,12,True)
        text(slide,'Study implication: assess South African terminal utilisation and access; test Walvis Bay customer economics; compare priority African markets using local evidence, not group margins.',.55,6.51,11.5,.42,11)
        text(slide,'Storage occupancy = average capacity rented / average storage capacity, weighted by ownership. Other business units is not a separate African result.',.55,6.97,11.5,.17,8.5)
    else:
        draw_cash_flow(slide,d,brand,text)
    credit=text(slide,'Source: Royal Vopak, Half Year Report 2026; '+('pp. 16–18, 29, 32–33, 39.' if index==53 else 'pp. 23–25, 56–57. Interpretation is our analytical framing.' if index==54 else 'pp. 32, 57. Consolidated cash balances include bank overdrafts; proportional free cash flow is a separate APM.'),.5,7.17,10.1,.2,8)
    for p in credit.text_frame.paragraphs:
        for r in p.runs:r.hyperlink.address=d['source']+('#page=39' if index==53 else '#page=56' if index==54 else '#page=32')


def draw_cash_flow(slide,d,brand,text):
    c=d['cash_flows']
    text(slide,'Net operating cash flow = 466.6 gross + 5.4 interest received − 53.4 tax paid = 418.6',.55,2.32,11.5,.4,14,True)
    text(slide,'Net operating: EUR 418.6m / 454.9m. Proportional operating free cash flow: EUR 444.2m / 450.5m (2026 / 2025; separate APM).',.55,2.78,11.5,.25,10.5)
    values=[('Operating\n(net)',c['net_operating'],True),('Investing',c['investing'],False),('Financing',c['financing'],False),('Net cash\nflows',c['net_cash_flows'],True),('Exchange\ndifferences',c['exchange'],False),('Change in\ncash balance',c['net_change'],True)]
    top=3.12;height=2.55
    def yp(v):return top+(450-v)/480*height
    zero=yp(0)
    axis=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(.75),Inches(zero),Inches(12),Inches(zero))
    axis.line.color.rgb=brand.ink;axis.line.width=Pt(.6)
    text(slide,'0',.55,zero-.1,.25,.22,9)
    running=0
    for i,(label,v,total) in enumerate(values):
        x=1.1+i*1.83
        start=0 if total else running
        end=v if total else start+v
        running=end
        hi=max(start,end);lo=min(start,end)
        bar=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(yp(hi)),Inches(.98),Inches(max(.012,yp(lo)-yp(hi))))
        bar.fill.solid();bar.fill.fore_color.rgb=brand.accent_primary if total else brand.grey_fill;bar.line.fill.background()
        text(slide,f'{v:+.1f}',x-.15,yp(hi)-.32,1.35,.27,14,True)
        text(slide,label,x-.28,5.85,1.58,.58,12,True)
        if i<5 and i!=3:
            connector=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x+.98),Inches(yp(end)),Inches(x+1.83),Inches(yp(end)))
            connector.line.color.rgb=brand.ink;connector.line.width=Pt(.5)
    text(slide,'Study implication: test service cash generation in South Africa, investment and customer commitments at Walvis Bay, and funding requirements in priority African markets.',.55,6.53,11.5,.34,12,True)
    text(slide,'Group operating cash is positive; total cash flow is −8.1m. Exchange +3.0m gives a −5.1m change: 98.8m opening → 93.7m closing.',.55,6.94,11.5,.21,9.5)
