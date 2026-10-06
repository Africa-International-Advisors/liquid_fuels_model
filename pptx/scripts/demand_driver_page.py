"""Indexed observed drivers; no causal fuel-demand attribution is calculated here."""
import json
from pptx.util import Inches, Pt
from pptx.enum.chart import XL_CHART_TYPE
from pptx.oxml.xmlchemy import OxmlElement
from brand_pptx import add_themed_chart
from supply_review_pages import read, frame, line as rule

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
    phev=series('nev_sales_naamsa.csv','drivetrain','plug_in_hybrid',2019,2025)
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
    prices=read(base/'fuel_prices_department.csv')
    price_series=[]
    for key,label in [('petrol_95_inland_retail','Petrol retail'),('diesel_005_inland_wholesale','Diesel wholesale')]:
        groups={}
        for r in prices:
            year=int(r['period'][:4])
            if r['series']==key and 2019<=year<=2023:
                groups.setdefault(year,[]).append(float(r['value'])/100)
        price_series.append((label,{year:sum(vals)/len(vals) for year,vals in groups.items() if len(vals)==12}))
    datasets=[('Passenger travel | all-fuel stock, Dec',[('Cars',cars),('Minibuses',minibuses)]),
              ('Freight demand | payload, CY',[('Road',road),('Rail',rail)]),
              ('Agriculture | real value added, CY',[('Agriculture / forestry / fishing',agriculture)]),
              ('Manufacturing | real value added, CY',[('Manufacturing',manufacturing)]),
              ('Mining | real value added, CY',[('Mining',mining)]),
              ('Diesel power | OCGT generation, FY',[('Eskom + IPP',power)]),
              ('Electrification | annual new sales, CY',[('BEV',bev),('Plug-in hybrid',phev),('Hybrid',hybrid)]),
              ('Price response | annual nominal R/litre',price_series)]
    frame(s,'Compare observed evidence for potential demand levers',
          None,'NaTIS; Stats SA P0441 / P7162; Eskom; naamsa; Department fuel-price history. Scope and observations in notes.',text,brand)
    # A full-width, even grid replaces the asymmetric evidence sidebar.
    for q in list(s.shapes):
        if Inches(1.7)<=q.top<Inches(7.05):q._element.getparent().remove(q._element)
    text(s,'Potential demand levers | 2024 = 100; price panel uses nominal R/litre',.5,1.78,11.65,.32,14,True)
    rule(s,(.5,2.13),(12.15,2.13),brand.ink,.55)
    text(s,'Observed proxies, not fuel-volume effects. Activity axes 0–120; EV 0–400; prices 0–30 R/L.',.5,2.20,11.65,.22,10,True,brand.accent_primary)
    colors=(brand.accent_primary,brand.accent_secondary,brand.ink)
    for i,(heading,raw_series) in enumerate(datasets):
        x=.5+(i%2)*6.0;y=2.51+(i//2)*1.08
        text(s,heading,x,y,5.65,.22,12,True,brand.accent_primary)
        years=sorted(set().union(*(v.keys() for _,v in raw_series)))
        assert years,heading
        values=[(name,[v.get(year) for year in years]) if i==7 else
                (name,[index(v).get(year) for year in years]) for name,v in raw_series]
        chart=add_themed_chart(s,XL_CHART_TYPE.LINE,Inches(x),Inches(y+.22),Inches(5.65),Inches(.65),
            [str(year) for year in years],values,show_legend=False,value_axis_format='0',axis_font_size=10,brand=brand)
        chart.value_axis.minimum_scale=0
        chart.value_axis.maximum_scale=30 if i==7 else 400 if i==6 else 120
        chart.value_axis.major_unit=15 if i==7 else 200 if i==6 else 100
        plot=chart._chartSpace.chart.plotArea
        layout=plot.find("{http://schemas.openxmlformats.org/drawingml/2006/chart}layout")
        if layout is None:
            layout=OxmlElement("c:layout");plot.insert(0,layout)
        manual=OxmlElement("c:manualLayout")
        for tag,val in [("layoutTarget","inner"),("xMode","factor"),("yMode","factor"),("wMode","factor"),("hMode","factor"),("x","0.09"),("y","0.06"),("w","0.89"),("h","0.62")]:
            node=OxmlElement("c:"+tag);node.set("val",val);manual.append(node)
        layout.append(manual)
        skip=OxmlElement('c:tickLblSkip');skip.set('val','2' if len(years)>4 else '1')
        chart.category_axis._element.insert_element_before(skip,'c:tickMarkSkip','c:noMultiLvlLbl','c:extLst')
        for j,(curve,color) in enumerate(zip(chart.series,colors)):
            curve.format.line.color.rgb=color;curve.format.line.width=Pt(1.8)
            lx=x+.32+j*1.78
            rule(s,(lx,y+.96),(lx+.20,y+.96),color,1.8)
            text(s,raw_series[j][0],lx+.24,y+.87,3.9 if len(raw_series)==1 else 1.50,.20,10)
    text(s,'To quantify: mileage × fleet/fuel mix × litres/km; sector fuel intensity; OCGT litres/kWh; price elasticity. FY ends March. Price 2024 incomplete.',
         .5,6.92,11.65,.18,8.5)
    power_change=100*(power[2026]/power[2024]-1)
    rail_change=100*(rail[2025]/rail[2024]-1);road_change=100*(road[2025]/road[2024]-1)
    notes={'base_year':2024,'formula':'100 * observed value / own 2024 value','series':datasets,
           'status':'descriptive evidence; not causal contributions or forecast demand',
           'price':'Annual extract stops 2023; no 2024 base available. Diesel prices are wholesale, petrol retail; no real-price elasticity calibrated.',
           'freight_revision':json.loads((base/'freight_payload_statssa_review.sources.json').read_text(encoding='utf-8')),
           'fleet':'BEV, plug-in hybrid and conventional-hybrid new sales shown separately; stocks, survival, mileage and efficiency not inferred. Uptake chart uses 0–400 to include the PHEV increase; six activity charts use 0–120.'}
    notes['vehicle_stock_scope']='NaTIS all-fuel national December snapshots. Cars/minibuses do not cover buses/motorcycles; trucks/light-commercial do not establish diesel-only freight usage. No ICE mix or fuel demand is inferred.'
    notes['sector_scope']='Real gross value added: agriculture includes forestry/fishing; industry shows manufacturing and mining separately, not all industrial fuel consumption.'
    notes['power_change_percent']=power_change
    notes['uptake_observations']={'BEV_new_sales':bev,'plug_in_hybrid_new_sales':phev,'conventional_hybrid_new_sales':hybrid}
    notes['sector_changes_percent']={'agriculture':index(agriculture)[2025]-100,'manufacturing':index(manufacturing)[2025]-100}
    notes['freight_changes_percent']={'rail':rail_change,'road':road_change}
    s.notes_slide.notes_text_frame.text+='\n'+json.dumps(notes,indent=2)
