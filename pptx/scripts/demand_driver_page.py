"""Indexed observed drivers; no causal fuel-demand attribution is calculated here."""
import json
from pptx.util import Inches, Pt
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from brand_pptx import add_themed_chart
from supply_review_pages import read, frame
from scr_structure import panel

def index(values,base_year=2024):
    assert base_year in values and values[base_year]>0
    return {year:100*value/values[base_year] for year,value in values.items()}

def add_driver_page(s,text,root,brand):
    base=root.parent/'assumptions/2026/timeseries'
    def series(file,key,value,start,end):
        return {int(r['period']):float(r['value']) for r in read(base/file)
                if r.get(key)==value and start<=int(r['period'])<=end}
    power=series('ocgt_generation_eskom.csv','series','eskom_and_ipp_ocgt',2023,2026)
    road=series('freight_payload_statssa_review.csv','mode','road',2024,2025)
    rail=series('freight_payload_statssa_review.csv','mode','rail',2024,2025)
    bev=series('nev_sales_naamsa.csv','drivetrain','battery_electric',2019,2025)
    hybrid=series('nev_sales_naamsa.csv','drivetrain','traditional_hybrid',2019,2025)
    gdp=series('macro_statssa.csv','series','gdp',2019,2025)
    datasets=[('Power | Eskom + IPP OCGT, FY',[('Generation',power)]),
              ('Freight | all goods payload, CY',[('Road',road),('Rail',rail)]),
              ('Fleet uptake | annual new sales, CY',[('BEV',bev),('Conventional hybrid',hybrid)]),
              ('Activity | real GDP, CY',[('GDP, 2015 prices',gdp)])]
    frame(s,'Compare the observed drivers of petrol and diesel demand',
          'Demand-driver dashboard | every series indexed to 2024 = 100',
          'Eskom integrated reports; Stats SA P7162 Dec 2025 Table 1 and P0441 Q2 2026; naamsa Q2 2026; DMPR price extract. Source cells in notes.',text,brand)
    text(s,'Observed series; common 0–120 scale. FY ends March; CY is calendar year.',.5,2.35,7.05,.28,11,True,brand.accent_primary)
    for i,(heading,raw_series) in enumerate(datasets):
        x=.5+(i%2)*3.64;y=2.78+(i//2)*1.94
        text(s,heading,x,y,3.40,.29,12,True,brand.accent_primary)
        years=sorted(raw_series[0][1])
        assert all(sorted(v)==years for _,v in raw_series)
        chart=add_themed_chart(s,XL_CHART_TYPE.LINE,Inches(x),Inches(y+.34),Inches(3.4),Inches(1.56),
            [str(year) for year in years],[(name,[index(v)[year] for year in years]) for name,v in raw_series],
            show_legend=True,value_axis_format='0',axis_font_size=11,brand=brand)
        chart.value_axis.minimum_scale=0;chart.value_axis.maximum_scale=120;chart.value_axis.major_unit=40
        chart.category_axis.tick_label_spacing=2 if len(years)>4 else 1
        chart.has_legend=True
        chart.legend.position=XL_LEGEND_POSITION.BOTTOM;chart.legend.include_in_layout=False;chart.legend.font.size=Pt(11)
        for line,color in zip(chart.series,(brand.accent_primary,brand.accent_secondary)):
            line.format.line.color.rgb=color;line.format.line.width=Pt(1.8)
    text(s,'Price flag: annual inland petrol-95 ends in 2023 at R23.14/L (nominal); not rebased or extrapolated.',.5,6.75,7.05,.25,10)
    power_change=100*(power[2026]/power[2024]-1)
    rail_change=100*(rail[2025]/rail[2024]-1);road_change=100*(road[2025]/road[2024]-1)
    panel(s,text,brand,[
        ('Power generation has fallen',f'OCGT generation falls from {power[2024]:,.0f} GWh in FY2024 to {power[2026]:,.0f} in FY2026 ({power_change:.0f}%). This is generation, not diesel litres.'),
        ('Freight needs a consistent vintage',f'2025 versus 2024: rail {rail_change:+.1f}%; road {road_change:+.1f}%. Road 2024 was revised from 790.6 to 979.8 million tonnes; no old/new splice.'),
        ('Sales are not fleet penetration',f'2025 sales: {bev[2025]:,.0f} BEVs and {hybrid[2025]:,.0f} conventional hybrids. Hybrids still consume fuel; GDP movement alone does not establish kilometres.')],
        'Manish: translate generation, freight tonne-km, fleet cohorts and real price/activity into sourced litres effects. Nigel: agree alternatives. Refresh prices; calibrate before forecasting.')
    notes={'base_year':2024,'formula':'100 * observed value / own 2024 value','series':datasets,
           'status':'descriptive evidence; not causal contributions or forecast demand',
           'price':'Annual extract stops 2023; no 2024 base available. Diesel prices are wholesale, petrol retail; no real-price elasticity calibrated.',
           'freight_revision':json.loads((base/'freight_payload_statssa_review.sources.json').read_text(encoding='utf-8')),
           'fleet':'BEV and conventional-hybrid new sales; PHEVs omitted from chart; stocks, survival, mileage and efficiency not inferred.'}
    s.notes_slide.notes_text_frame.text+='\n'+json.dumps(notes,indent=2)
