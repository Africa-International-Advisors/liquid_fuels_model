"""Native charts of pinned, saved annual balances; no engine calculations here."""
import json
import math
import pandas as pd
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_TICK_MARK
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt


def draw_results(slide, index, root, text):
    manifest=json.loads((root/'story/current-results-runs.json').read_text())
    frames={s:pd.read_csv(root.parent/p).query("country == 'ZAF'") for s,p in manifest.items()}
    for frame in frames.values():
        assert set(frame.refinery_product)=={'gasoline','diesel','jet_a1','fuel_oil'}
        assert frame.period.min()==2024 and frame.period.max()==2050
        assert ((frame.demand_litres-frame.supply_litres-frame.deficit_litres).abs()<.01).all()
        assert not frame.duplicated(['refinery_product','period']).any()
    frames={s:f[f.refinery_product.eq('fuel_oil') if index==48 else f.refinery_product.ne('fuel_oil')] for s,f in frames.items()}
    blue=RGBColor.from_string('0A2373'); light=RGBColor.from_string('8491B2')
    grey=RGBColor.from_string('666666')
    def legend(items,y):
        for x,label,color,dashed in items:
            sample=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x),Inches(y+.12),Inches(x+.55),Inches(y+.12))
            sample.name=f'Legend: {label}'
            sample.line.color.rgb=color
            sample.line.width=Pt(2)
            if dashed:sample.line.dash_style=MSO_LINE_DASH_STYLE.DASH
            text(slide,label,x+.68,y,3.3,.3,13)
    def chart(x,y,w,h,series,maximum=None):
        data=CategoryChartData(); data.categories=[str(v) if v in (2024,2030,2040,2050) else '' for v in range(2024,2051)]
        for label,values,color,dash in series:data.add_series(label,list(values/1e9))
        ch=slide.shapes.add_chart(XL_CHART_TYPE.LINE,Inches(x),Inches(y),Inches(w),Inches(h),data).chart
        ch.has_legend=False
        ch.value_axis.minimum_scale=0
        if maximum:ch.value_axis.maximum_scale=maximum
        ch.value_axis.tick_labels.font.size=Pt(10)
        ch.value_axis.tick_labels.number_format='0.0'
        ch.value_axis.has_major_gridlines=True
        ch.value_axis.major_gridlines.format.line.color.rgb=RGBColor.from_string('DDDDDD')
        ch.value_axis.major_gridlines.format.line.width=Pt(.3)
        ch.category_axis.tick_label_spacing=5
        ch.category_axis.tick_labels.font.size=Pt(10)
        ch.category_axis.major_tick_mark=XL_TICK_MARK.NONE
        for line,(_,_,color,dash) in zip(ch.series,series):
            line.format.line.color.rgb=color;line.format.line.width=Pt(2)
            if dash:line.format.line.dash_style=MSO_LINE_DASH_STYLE.DASH
        return ch
    text(slide,'South Africa | 2024–2050 | billion litres per year | current paired scenarios; provisional',.55,1.8,11.5,.35,15)
    if index in (41,48):
        totals={s:f.groupby('period')[['demand_litres','supply_litres','deficit_litres']].sum().reindex(range(2024,2051)) for s,f in frames.items()}
        text(slide,'Core total: petrol + both diesel grades + jet; excludes fuel oil.' if index==41 else 'Supplementary fuel oil only: provisional marine baseline; no domestic production represented.',.55,6.5,11.5,.25,12)
        maximum=2.0 if index==48 else math.ceil(max(f.demand_litres.max() for f in totals.values())/1e10)*10
        legend([(.55,'Demand',blue,False),(3.1,'Domestic production',grey,False),(7.0,'Deficit',light,True)],2.25)
        for (s,f),x in zip(totals.items(),[.55,6.5]):
            text(slide,s.replace('_',' ').title(),x,2.75,5.5,.3,18,True)
            chart(x,3.12,5.6,2.95,[('Demand',f.demand_litres,blue,False),('Domestic production',f.supply_litres,grey,False),('Deficit',f.deficit_litres,light,True)],maximum)
            text(slide,f'2050 deficit: {f.loc[2050,"deficit_litres"]/1e9:.1f} bn litres',x,6.12,5.6,.3,15,True)
    else:
        metric={42:'demand_litres',43:'supply_litres',44:'deficit_litres'}[index]
        legend([(.55,'High-demand run',blue,False),(4.1,'Low-demand run',light,True)],2.2)
        for (product,label),(x,y) in zip([('gasoline','Petrol'),('diesel','Diesel — both grades'),('jet_a1','Jet')],[(.55,2.65),(6.5,2.65),(.55,4.5),(6.5,4.5)]):
            text(slide,label,x,y,5.6,.3,16,True)
            series=[]
            for s,c,dash in [('high_demand',blue,False),('low_demand',light,True)]:
                values=frames[s].query('refinery_product == @product').set_index('period')[metric].reindex(range(2024,2051))
                assert values.notna().all()
                series.append((s,values,c,dash))
            chart(x,y+.32,5.6,1.52,series)
        text(slide,'Reporting scope',6.5,4.5,5.6,.3,16,True)
        text(slide,'Petrol, diesel (both grades) and jet.\nFuel oil is a separate provisional marine output; see the supplementary page.',6.5,5.0,5.4,1.0,15)
        text(slide,'Axes differ by fuel. Core totals exclude fuel oil; no numerical model assumptions have changed.',.55,6.5,11.5,.27,12)
    text(slide,'Deficit = demand − domestic production; not unmet demand after imports. Trade, stocks and import constraints remain unresolved.',.55,6.86,11.5,.22,10)
