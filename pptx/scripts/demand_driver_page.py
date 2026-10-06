"""Indexed observed drivers; no causal fuel-demand attribution is calculated here."""
import json
from pptx.util import Inches, Pt
from pptx.enum.chart import XL_CHART_TYPE
from pptx.oxml.xmlchemy import OxmlElement
from brand_pptx import add_themed_chart
from supply_review_pages import read, frame, line as rule
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
    agriculture=series('macro_statssa.csv','series','agriculture_forestry_and_fishing',2019,2025)
    manufacturing=series('macro_statssa.csv','series','manufacturing',2019,2025)
    mining=series('macro_statssa.csv','series','mining_and_quarrying',2019,2025)
    stock=read(base/'vehicle_population_natis.csv')
    def december_stock(vehicle_class):
        return {int(r['period'][:4]):float(r['value']) for r in stock
            if r['province']=='ZAF' and r['vehicle_class']==vehicle_class and r['period'].endswith('-12')
            and 2021<=int(r['period'][:4])<=2025}
    cars=december_stock('cars');minibuses=december_stock('minibuses')
    trucks=december_stock('trucks');lcv=december_stock('light_commercial')
    datasets=[('Passenger stock | all fuels; Dec',[('Cars',cars),('Minibuses',minibuses)]),
              ('Freight stock | all fuels; Dec',[('Trucks',trucks),('Light commercial',lcv)]),
              ('Agriculture | real value added, CY',[('Agriculture / forestry / fishing',agriculture)]),
              ('Industry | real value added, CY',[('Manufacturing',manufacturing),('Mining',mining)]),
              ('Power | OCGT generation, FY',[('Eskom + IPP',power)]),
              ('Freight activity | payload, CY',[('Road',road),('Rail',rail)])]
    frame(s,'Track passenger, freight and sector activity driving fuel demand',
          'Demand-driver dashboard | every series indexed to 2024 = 100',
          'NaTIS Dec snapshots; Stats SA P0441 Q2 2026 / P7162 Dec 2025; Eskom integrated reports; naamsa Q2 2026. Series and scope in notes.',text,brand)
    text(s,'Common 0–120 scale. Activity proxies, not fuel litres; vehicle ICE split unresolved.',.5,2.35,7.05,.28,11,True,brand.accent_primary)
    for i,(heading,raw_series) in enumerate(datasets):
        x=.5+(i%2)*3.64;y=2.74+(i//2)*1.32
        text(s,heading,x,y,3.40,.29,12,True,brand.accent_primary)
        years=sorted(raw_series[0][1])
        assert all(sorted(v)==years for _,v in raw_series)
        chart=add_themed_chart(s,XL_CHART_TYPE.LINE,Inches(x),Inches(y+.28),Inches(3.4),Inches(.78),
            [str(year) for year in years],[(name,[index(v)[year] for year in years]) for name,v in raw_series],
            show_legend=False,value_axis_format='0',axis_font_size=11,brand=brand)
        chart.value_axis.minimum_scale=0;chart.value_axis.maximum_scale=120;chart.value_axis.major_unit=100
        chart.has_legend=False
        skip=OxmlElement('c:tickLblSkip');skip.set('val','2' if len(years)>4 else '1')
        chart.category_axis._element.insert_element_before(skip,'c:tickMarkSkip','c:noMultiLvlLbl','c:extLst')
        for curve,color in zip(chart.series,(brand.accent_primary,brand.accent_secondary)):
            curve.format.line.color.rgb=color;curve.format.line.width=Pt(1.8)
        for j,(name,_) in enumerate(raw_series):
            color=(brand.accent_primary,brand.accent_secondary)[j]
            lx=x+.37+j*1.51
            # Native external legend keeps the plot from collapsing on short charts.
            rule(s,(lx,y+1.17),(lx+.22,y+1.17),color,1.8)
            text(s,name,lx+.26,y+1.06,2.77 if len(raw_series)==1 else 1.4,.22,11)
    text(s,'FY ends March; CY is calendar year. Stock is December snapshot. ICE = internal combustion engine.',.5,6.83,7.05,.20,9)
    power_change=100*(power[2026]/power[2024]-1)
    rail_change=100*(rail[2025]/rail[2024]-1);road_change=100*(road[2025]/road[2024]-1)
    panel(s,text,brand,[
        ('Passenger and freight ICE need a split','NaTIS separates cars/minibuses and trucks/light commercial, but not petrol, diesel or electric. Stocks are all fuels; kilometres and efficiency remain open.'),
        ('Sector activity is now explicit',f'2025 versus 2024: agriculture {index(agriculture)[2025]-100:+.1f}%; manufacturing {index(manufacturing)[2025]-100:+.1f}%. Value added is an activity proxy, not direct fuel consumption.'),
        ('Uptake and modal levers remain distinct',f'2025 sales: {bev[2025]:,.0f} BEVs; {hybrid[2025]:,.0f} hybrids. Rail payload {rail_change:+.1f}%; road {road_change:+.1f}%. Hybrids still use fuel; payload is not tonne-km.')],
        'Manish: source ICE fuel splits, vehicle-km, freight tonne-km and sector fuel intensities. Keep the freight revision flag; refresh prices (annual extract ends 2023). Nigel: agree lever alternatives.')
    notes={'base_year':2024,'formula':'100 * observed value / own 2024 value','series':datasets,
           'status':'descriptive evidence; not causal contributions or forecast demand',
           'price':'Annual extract stops 2023; no 2024 base available. Diesel prices are wholesale, petrol retail; no real-price elasticity calibrated.',
           'freight_revision':json.loads((base/'freight_payload_statssa_review.sources.json').read_text(encoding='utf-8')),
           'fleet':'BEV and conventional-hybrid new sales; PHEVs omitted from chart; stocks, survival, mileage and efficiency not inferred.'}
    notes['vehicle_stock_scope']='NaTIS all-fuel national December snapshots. Cars/minibuses do not cover buses/motorcycles; trucks/light-commercial do not establish diesel-only freight usage. No ICE mix or fuel demand is inferred.'
    notes['sector_scope']='Real gross value added: agriculture includes forestry/fishing; industry shows manufacturing and mining separately, not all industrial fuel consumption.'
    notes['power_change_percent']=power_change
    notes['uptake_observations']={'BEV_new_sales':bev,'conventional_hybrid_new_sales':hybrid}
    s.notes_slide.notes_text_frame.text+='\n'+json.dumps(notes,indent=2)
