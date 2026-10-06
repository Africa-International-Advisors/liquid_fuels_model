from exhibit_typography import CHART_LABEL, CHART_SECONDARY, LEGEND
"""Presentation of declared sales, with an explicitly authored supply illustration."""
import csv,json
from collections import defaultdict
from pptx.util import Inches,Pt
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE,MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.dml.color import RGBColor
from brand_pptx import add_themed_chart

NAMES={'GP':'Gauteng','KZN':'KwaZulu-Natal','WC':'Western Cape','MP':'Mpumalanga','EC':'Eastern Cape',
       'FS':'Free State','NW':'North West','LP':'Limpopo','NC':'Northern Cape'}

def annual_sales(root):
    path=root.parent/'assumptions/2026/timeseries/fuel_sales_department_by_province_quarterly.csv'
    totals=defaultdict(float);quarters=defaultdict(set);seen=set()
    for r in csv.DictReader(path.open(encoding='utf-8-sig',newline='')):
        if r['product'] not in ('petrol','diesel'):continue
        year=int(r['period'][:4]); key=(year,r['province'],r['product']); unique=(*key,r['period'])
        assert unique not in seen and r['unit']=='litres';seen.add(unique)
        totals[key]+=float(r['value'])/1e9;quarters[key].add(r['period'][-1])
    complete={k:v for k,v in totals.items() if quarters[k]=={'1','2','3','4'}}
    series={}
    for year in sorted({k[0] for k in totals}):
        series[year]={p:sum(complete[(year,p,product)] for product in ('petrol','diesel'))
                      for p in NAMES if all((year,p,product) in complete for product in ('petrol','diesel'))}
    return series,complete

def add_trend_page(slide,exhibit_layout,text,line,root,brand):
    annual,_=annual_sales(root);years=[y for y in annual if annual[y]]
    assert years[-1]==2022 and len(annual[2022])==9
    national=defaultdict(float)
    for r in csv.DictReader((root.parent/'assumptions/2026/timeseries/fuel_sales_department.csv').open(encoding='utf-8-sig')):
        if r['product'] in ('petrol','diesel'):national[int(r['period'])]+=float(r['value'])/1e9
    differences={y:sum(annual[y].values())-national[y] for y in years if y in national}
    flagged={y:d for y,d in differences.items() if abs(d)>1e-9}
    s=slide('Track petrol and diesel sales by province over time',
        'DMPR quarterly provincial sales extract; complete calendar years only. Petrol + diesel; jet excluded.',
        'Annual reporting sums four quarters separately for each province/product. Missing or incomplete years '
        'are gaps, never zeros or extrapolations. 2023 has Q1 only and is excluded. Source: '
        'assumptions/2026/timeseries/fuel_sales_department_by_province_quarterly.csv. '
        'Reported sales are a demand proxy; historical reporting requires analyst review, not a forecast.')
    exhibit_layout(s,'Annual provincial sales | 2013–2022, bn litres/year',[
        ('One line per province','Compare provincial demand histories on one shared scale. Petrol and diesel are combined; jet is excluded.'),
        ('Keep history separate from outlook','The latest complete year in this extract is 2022. These lines are reported sales, not a current-year forecast.'),
        ('Incomplete periods are excluded','2023 contains Q1 only. A partial year must not appear as a full-year demand collapse.'),
        ('Historical totals need reconciliation',f"Provincial and national series differ in {len(flagged)} years. Largest gaps: 2013 {differences[2013]:+.2f} and 2018 {differences[2018]:+.2f} bn litres. Review the source workbooks."),
    ])
    s.notes_slide.notes_text_frame.text += '\nProvincial sum minus national petrol/diesel sales (bn L), '
    s.notes_slide.notes_text_frame.text += 'mechanical flag tolerance 1 litre, not a materiality or validation threshold:\n'+json.dumps(differences,indent=2)
    chart=add_themed_chart(s,XL_CHART_TYPE.LINE,Inches(.5),Inches(2.37),Inches(7.05),Inches(3.93),
        [str(y) for y in years],[(NAMES[p],[annual[y].get(p) for y in years]) for p in NAMES],
        show_legend=False,value_axis_format='0.0',axis_font_size=CHART_SECONDARY,brand=brand)
    chart.value_axis.minimum_scale=0;chart.value_axis.maximum_scale=8;chart.value_axis.major_unit=2
    colours=['0A2373','546CA2','404040','546CA2','767676','0A2373','404040','767676','BDBEC1']
    dashes=[None,None,None,MSO_LINE_DASH_STYLE.DASH,MSO_LINE_DASH_STYLE.DASH,
            MSO_LINE_DASH_STYLE.ROUND_DOT,MSO_LINE_DASH_STYLE.DASH_DOT,MSO_LINE_DASH_STYLE.ROUND_DOT,MSO_LINE_DASH_STYLE.LONG_DASH]
    for i,(p,series) in enumerate(zip(NAMES,chart.series)):
        colour=RGBColor.from_string(colours[i]);series.format.line.color.rgb=colour
        series.format.line.width=Pt(2 if i<3 else 1.4)
        if dashes[i]:series.format.line.dash_style=dashes[i]
        x=.55+(i%3)*2.30;y=6.36+(i//3)*.26
        line(s,(x,y+.07),(x+.27,y+.07),colour,1.7,dashes[i]);text(s,NAMES[p],x+.34,y,1.95,.26,LEGEND)
    return s

def add_supply_page(slide,exhibit_layout,text,root,brand):
    settings=json.loads((root/'story/provincial_supply_allocation_2026_10_06.json').read_text(encoding='utf-8'))
    annual,products=annual_sales(root);year=settings['demand_year'];actual=annual[year]
    mix=list(csv.DictReader((root/'story/illustrative_national_balance.csv').open(encoding='utf-8-sig')))
    shares={r['product']:float(r['domestic_supply_bn_l'])/float(r['demand_bn_l']) for r in mix}
    values={p:(sum(products[(year,p,f)]*shares[f] for f in ('petrol','diesel')),actual[p]) for p in NAMES}
    s=slide('Shape the provincial split between domestic fuel and imports',
        'DMPR 2022 provincial sales totals; source mix from the existing illustrative national-balance CSV. Not observed origin.',
        json.dumps(settings,indent=2)+'\nNo provincial origin dataset was found in the reviewed source extract. '
        'Demand totals are reported 2022 sales; domestic/import segments are illustrative, not observed 2022 supply. '
        'The same example product-specific shares apply to every province. Imports mean finished products, not imported crude. '
        'Do not infer these flows from refinery locations or customs clearance province.')
    exhibit_layout(s,'2022 sales totals | ILLUSTRATIVE domestic/import allocation',[
        ('Demand totals are reported sales','Each complete bar matches its province’s reported petrol + diesel sales in 2022. The source split is illustrative.'),
        ('Allocate by product, then aggregate','Use the existing example domestic shares separately for petrol and diesel. Provinces differ because their fuel mix differs.'),
        ('Provincial origins remain unverified','National production/imports do not tell us which province received each litre. Obtain refinery, port and onward customer flows.'),
        ('Refined fuel origin is the distinction','Locally refined fuel counts as domestic, including output made from imported crude. Imports here mean finished petrol/diesel.'),
    ])
    x0=2.05;width=4.8;limit=8
    for v in [0,2,4,6,8]:
        x=x0+width*v/limit
        q=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x),Inches(2.70),Inches(x),Inches(6.02))
        q.line.color.rgb=brand.grey_fill;q.line.width=Pt(.5)
        text(s,str(v),x-.09,2.42,.40,.26,CHART_SECONDARY)
    for i,p in enumerate(sorted(NAMES,key=actual.get,reverse=True)):
        y=2.84+i*.34; domestic,total=values[p];assert 0<=domestic<=total
        text(s,NAMES[p],.5,y+.01,1.52,.29,CHART_LABEL,True)
        x=x0
        for value,colour in [(domestic,brand.accent_primary),(total-domestic,RGBColor.from_string('809CC7'))]:
            w=width*value/limit
            q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(.27))
            q.fill.solid();q.fill.fore_color.rgb=colour;q.line.fill.background();x+=w
        text(s,f'{total:.2f}',x+.07,y,.61,.29,CHART_LABEL,True)
    for x,label,colour in [( .5,'Illustrative domestic fuel',brand.accent_primary),(3.55,'Illustrative finished-product imports',RGBColor.from_string('809CC7'))]:
        q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(6.25),Inches(.12),Inches(.12))
        q.fill.solid();q.fill.fore_color.rgb=colour;q.line.fill.background()
        text(s,label,x+.18,6.20,3.5,.27,LEGEND)
    text(s,'Units: bn litres/year. Imported/domestic segments are a scenario illustration, not measured provincial flows.',.5,6.63,7.05,.41,10,True,brand.accent_primary)
    return s
