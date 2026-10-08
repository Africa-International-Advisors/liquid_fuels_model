"""Apply one panel language to the six annotated exhibits; preserve source vintages."""
import json
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/delivered/sa_panel_layout_2026_10_08'
OUT.mkdir(parents=True,exist_ok=True)
BLUE='#0A2373'; SECOND='#546CA2'; GREY='#767676'; RULE='#B4BAC6'
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
def text(x,y,s,size=12,color='#222',bold=False):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}">{escape(str(s))}</text>'
def line(x1,y1,x2,y2,color=RULE):
    return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" stroke-width="0.8" fill="none"/>'
def save(name,body):
    (OUT/f'{name}.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 340"><rect width="880" height="340" fill="white"/><g font-family="Lato,Arial,sans-serif">'+body+'</g></svg>',encoding='utf-8')
def two_panel(source,name,left,right,split,lx,rx,remove):
    root=ET.parse(source).getroot()
    group=root.find(f'{{{NS}}}g')
    for parent in group.iter():
        for child in list(parent):
            if child.tag==f'{{{NS}}}text' and ''.join(child.itertext()) in remove:
                parent.remove(child)
            # Replace the older future-capacity dashed divider.
            elif name=='future_capacity' and child.tag==f'{{{NS}}}path' and child.get('d')=='M325 50L325 289':
                parent.remove(child)
    contents=''.join(ET.tostring(child,encoding='unicode') for child in group)
    if name=='corridor_map':
        # Uniformly fit geographic geometry and its labels; never stretch the map.
        left_items=[];right_items=[]
        for child in group:
            target=right_items if child.tag==f'{{{NS}}}text' and float(child.get('x','0'))>=580 else left_items
            target.append(ET.tostring(child,encoding='unicode'))
        body='<g transform="translate(28 32) scale(0.90)">'+''.join(left_items)+'</g>'
        body+='<g transform="translate(0 32) scale(1 0.90)">'+''.join(right_items)+'</g>'
    else:
        body=f'<g transform="translate(0 32) scale(1 0.90)">{contents}</g>'
    body+=text(lx,20,left,13,BLUE,True)+text(rx,20,right,13,BLUE,True)
    body+=line(25,31,split-13,31)+line(split+13,31,855,31)
    body+=line(split,42,split,287 if name=='future_capacity' else 302)
    body+=f'<path d="M{split-4} 23l7 7-7 7" stroke="{BLUE}" stroke-width="1.5" fill="none"/>'
    save(name,body)

old=ROOT/'output/sa_feedback_2026_10_07'
two_panel(old/'demand_trend.svg','demand_trend','DEMAND TREND','CHANGE OVER 2013–2023',590,55,620,[])
two_panel(old/'imports_change.svg','imports_change','IMPORT TREND','CHANGE SINCE 2020',590,50,620,['IMPORT TREND','CHANGE SINCE 2020'])
two_panel(ROOT/'output/delivered/geospatial/2026_10_07/corridor_map.svg','corridor_map','COMPETING SUPPLY CORRIDORS','SAME PRODUCT, SAME DESTINATION',560,42,580,['SAME PRODUCT, SAME DESTINATION'])
two_panel(old/'turnover.svg','turnover','GROSS HANDLING SENSITIVITY','INVESTMENT TEST',510,30,540,['GROSS HANDLING SENSITIVITY','INVESTMENT TEST'])
two_panel(ROOT/'output/delivered/supply_capacity_cases_2026_10_08/future_capacity.svg','future_capacity','REPORTED HISTORY','ILLUSTRATIVE 2036 CAPACITY CASES',325,42,365,['REPORTED HISTORY','ILLUSTRATIVE 2036 CAPACITY CASES'])

# Three equal columns with an interpretation card aligned beneath each chart.
data=json.loads((old/'data.json').read_text())['series']
panels=[('DIESEL USE','million litres; own fleet',data['05_eskom_fuel'],['Diesel + kerosene'],
         ['D5: dispatch drives fuel use.','Separate Eskom from private backup;','load-shedding and backup histories','are still needed.']),
        ('FLEET AVAILABILITY','EAF %',data['06_eskom_eaf'],['EAF'],
         ['D5: test recovery against outages','and retirement timing. Sustained','availability reduces pressure on','diesel generation.']),
        ('PEAKING GENERATION','OCGT GWh',{k:v for k,v in data['generation'].items() if k!='eskom_and_ipp_ocgt'},['Eskom','IPP'],
         ['D5: wind, solar and gas timing','changes residual peaking needs.','Calibrate dependable generation','before forecasting diesel litres.'])]
b=''
for i,(heading,unit,series,labels,notes) in enumerate(panels):
    left=12+i*292; x=left+38; y=65; w=222; h=137
    b+=text(left,20,heading,13,BLUE,True)+line(left,31,left+270,31)+text(x,50,unit,11,GREY)
    vals=[(int(k),v) for s in series.values() for k,v in s.items()]
    mn=min(k for k,v in vals);mx=max(k for k,v in vals);high=max(v for k,v in vals)*1.15
    xx=lambda year:x+(int(year)-mn)/(mx-mn)*w
    yy=lambda value:y+h-value/high*h
    for j in range(4):
        value=high*j/3;b+=line(x,yy(value),x+w,yy(value),'#DDD')+text(x-38,yy(value)+4,f'{value:,.1f}',10,GREY)
    for year in sorted({mn,mx,(mn+mx)//2}):b+=text(xx(year)-12,y+h+16,year,10,GREY)
    for j,series_values in enumerate(series.values()):
        color=SECOND if i==0 or j==1 else BLUE
        points=' '.join(f'{xx(k)},{yy(v)}' for k,v in sorted(series_values.items(),key=lambda item:int(item[0])))
        b+=f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.5"/>'
        b+=text(x+j*115,236,labels[j],11,color)
    b+=f'<rect x="{left}" y="250" width="270" height="85" fill="#F4F5F7"/>'
    for j,note in enumerate(notes):b+=text(left+10,269+j*17,note,11.5)
save('power_timeseries',b)

story=json.loads((ROOT/'pptx/story/sa_market_story_future_supply_2026_10_08.json').read_text(encoding='utf-8'))
for page,name in {6:'demand_trend',8:'imports_change',9:'corridor_map',10:'turnover',12:'power_timeseries',13:'future_capacity'}.items():
    story['slides'][page-2]['custom_chart']=f'output/delivered/sa_panel_layout_2026_10_08/{name}.png'
story['cover_status']='Panel layouts aligned; scenario and commercial calibration remain open'
(ROOT/'pptx/story/sa_market_story_panel_layout_2026_10_08.json').write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared six annotated exhibits with shared panel rules and aligned commentary.')
