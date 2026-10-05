"""Stack traced demand components without inventing an Excel sector allocation."""
import csv
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor


def draw_demand_stacks(slide, root, brand, cfg, text, results):
    rows=list(csv.DictReader((root/'output/data/vehicle_diagnostics.csv').open()))
    petrol={r['segment']:float(r['litres'])/1e9 for r in rows if r['year']=='2024' and r['product']=='petrol_95'}
    p,d,j=[results[k] for k in ('petrol','diesel','jet')]
    colors=[RGBColor.from_string(v) for v in ('B7B7B7','0A2373','536598','8491B2','CED3E3')]
    specs=[('Petrol',p,[('Recorded total',p['observed']/1e9,0),('Passenger',0,petrol.get('passenger',0)),('Light commercial',0,petrol.get('lcv',0))],12),
           ('Diesel',d,[('Excel non-power',d['excel_nonpower']/1e9,0),('Road',0,d['python_road']/1e9),('Power',d['excel_power']/1e9,d['python_power']/1e9),('Industrial',0,d['effects']['Industrial placeholder added']/1e9),('Agriculture',0,d['effects']['Agriculture placeholder added']/1e9)],18),
           ('Jet',j,[('Recorded total',j['observed']/1e9,0),('Calculated demand',0,j['python']/1e9)],3)]
    text(slide,'South Africa, 2024 | billion litres | current high_demand configuration',.55,1.82,11.5,.35,16)
    for k,(fuel,r,parts,maximum) in enumerate(specs):
        x=.52+k*2.45
        text(slide,fuel,x,2.3,2.3,.33,18,True)
        text(slide,f"Totals: {r['observed']/1e9:.2f} / {r['python']/1e9:.2f}",x,2.71,2.4,.25,11)
        data=CategoryChartData();data.categories=['Excel','Python']
        for name,a,b in parts:data.add_series(name,[a,b])
        assert abs(sum(v[1] for v in parts)-r['observed']/1e9)<1e-6
        assert abs(sum(v[2] for v in parts)-r['python']/1e9)<1e-6
        chart=slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_STACKED,Inches(x),Inches(3.02),Inches(2.3),Inches(2.45),data).chart
        chart.has_legend=False;chart.value_axis.minimum_scale=0;chart.value_axis.maximum_scale=maximum;chart.value_axis.major_unit=maximum/3
        chart.value_axis.has_major_gridlines=False
        for axis in (chart.value_axis,chart.category_axis):axis.tick_labels.font.size=Pt(10)
        chart.plots[0].gap_width=25
        for n,series in enumerate(chart.series):
            series.format.fill.solid();series.format.fill.fore_color.rgb=colors[n];series.format.line.fill.background()
            for idx,v in enumerate(parts[n][1:]):
                label=series.points[idx].data_label;label.position=XL_LABEL_POSITION.CENTER
                label.text_frame.text=(f'{v:.1f}' if v>=10 else f'{v:.2f}') if v>=.85 else ''
                label.text_frame.word_wrap=False
                label.text_frame.margin_left=label.text_frame.margin_right=0
                for para in label.text_frame.paragraphs:
                    for run in para.runs:run.font.size=Pt(11);run.font.color.rgb=brand.white if n in (1,2) else brand.ink
            # Compact key under each panel, including components too small to label.
            from pptx.enum.shapes import MSO_SHAPE
            s=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x+.04),Inches(5.58+n*.18),Inches(.08),Inches(.08));s.fill.solid();s.fill.fore_color.rgb=colors[n];s.line.fill.background()
            text(slide,parts[n][0],x+.18,5.51+n*.18,2.1,.2,9)
    text(slide,'Assumptions to reconcile',8.05,2.3,4.1,.35,18,True)
    text(slide,'Petrol: fleet and use per vehicle',8.05,2.85,4.1,.35,14,True)
    text(slide,f"Fleet: {p['excel_fleet']/1e6:.2f}m vs {p['python_fleet']/1e6:.2f}m.\nImplied litres/vehicle: {p['excel_litres_per_vehicle']:,.0f} vs {p['python_litres_per_vehicle']:,.0f}.",8.05,3.23,4.1,.68,13)
    text(slide,'Diesel: power + sector baselines',8.05,4.05,4.1,.35,14,True)
    text(slide,'Power: 0.50 vs 3.58 bn litres.\nPython adds industrial 2.50 and agriculture 0.70 bn litres. Excel non-power already includes non-road uses.',8.05,4.43,4.1,1.08,13)
    text(slide,'Jet: recorded vs calculated',8.05,5.66,4.1,.35,14,True)
    text(slide,'Python matches the Excel calculation; the 0.26 gap is against recorded demand.',8.05,6.04,4.1,.6,13)
