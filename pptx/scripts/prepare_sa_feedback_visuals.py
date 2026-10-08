"""Draw evidence exhibits from resolved results, then revise presentation copy."""
import json
import math
from html import escape
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/sa_feedback_2026_10_07'
DATA=json.loads((OUT/'data.json').read_text())
SER=DATA['series']; BLUE='#0A2373'; SECOND='#546CA2'; GREY='#767676'
def text(x,y,value,size=14,col='#222',bold=False):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}"'+(' font-weight="bold"' if bold else '')+'>'+escape(str(value))+'</text>'
def lines(x,y,values,size=14,step=20,col='#222',bold=False):
    return ''.join(text(x,y+i*step,v,size,col,bold) for i,v in enumerate(values))
def svg(name,body):
    (OUT/(name+'.svg')).write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 340"><rect width="880" height="340" fill="white"/><g font-family="Lato,Arial,sans-serif">'+body+'</g></svg>',encoding='utf-8')
def plot(series,x=55,y=50,w=500,h=220,unit='',dash=False,legend=True):
    vals=[(int(k),v) for s in series.values() for k,v in s.items()]
    mn,mx=min(k for k,v in vals),max(k for k,v in vals)
    high=max(v for k,v in vals)*1.15 or 1
    xx=lambda k:x+(int(k)-mn)/max(mx-mn,1)*w
    yy=lambda v:y+h-v/high*h
    b=text(x,y-17,unit,12,GREY)
    for j in range(4):
        v=high*j/3; ypos=yy(v)
        b+=f'<path d="M{x},{ypos}h{w}" stroke="#ddd"/>'+text(x-40,ypos+4,f'{v:,.1f}',11,GREY)
    for k in sorted(set([mn,mx,(mn+mx)//2])): b+=text(xx(k)-14,y+h+17,k,11,GREY)
    for i,(label,s) in enumerate(series.items()):
        c=[BLUE,SECOND,GREY,'#008477'][i%4]
        if 'petrol' in label.lower(): c=BLUE
        elif 'diesel' in label.lower(): c=SECOND
        elif label=='Road': c=BLUE
        elif label=='Rail': c=SECOND
        pts=' '.join(f'{xx(k)},{yy(v)}' for k,v in sorted(s.items(),key=lambda kv:int(kv[0])))
        b+=f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2.5"'+(' stroke-dasharray="5 4"' if dash else '')+'/>'
        if legend:b+=text(x+(i%2)*w/2,y+h+38+(i//2)*17,label,11,c)
    return b

# Comparable national demand; separate source observations never enter the growth calculation.
d={k.split(':')[0]:v for k,v in SER['01_demand'].items() if 'department' in k}
b=plot(d,w=510,h=205,unit='billion litres / calendar year')
for i,label in enumerate(['Petrol','Diesel']):
    m=DATA['metrics']['01_demand'][label+': department']; yy=65+i*105
    b+=text(620,yy,label+' 2013–2023',16,BLUE if label=='Petrol' else SECOND,True)
    b+=lines(620,yy+26,[f"{m['start']:.2f} to {m['end']:.2f} bn litres",f"{m['change']:+.2f} bn L / {m['change_pct']:+.1f}%",f"CAGR {m['cagr_pct']:+.1f}% per year"],14,22)
b+=text(55,322,'FIASA 2024 observations are excluded from this comparison: source definitions are not reconciled.',12,GREY)
svg('demand_trend',b)

d={k:v for k,v in SER['10_trade'].items() if k.endswith('import')}
b=text(50,22,'IMPORT TREND',14,BLUE,True)+text(620,22,'CHANGE SINCE 2020',14,BLUE,True)
b+=plot(d,y=60,w=500,h=205,unit='billion litres / calendar year')
for i,label in enumerate(['Diesel import','Petrol import']):
    m=DATA['metrics']['10_trade'][label]; yy=68+i*100
    b+=text(620,yy,label,15,BLUE if label.startswith('Petrol') else SECOND,True)
    b+=lines(620,yy+23,[f"{m['start']:.2f} to {m['end']:.2f} bn litres",f"Increase: {m['change']:.2f} bn litres",f"CAGR: {m['cagr_pct']:.1f}% (2020–2025)"],13,20)
b+=text(620,294,'More inland handling opportunity;',12,BLUE)+text(620,312,'capture and turnover determine benefit.',12,BLUE)
svg('imports_change',b)

# Three compact quantitative rows, with forecast diagnostics explicitly differentiated.
b=''
panels=[('Rail recovery',SER['08_freight'],'million tonnes',False,['D2: capacity, reliability, transferable freight','Tonnes require haul distance and traction','before conversion to net diesel savings.']),
('EV uptake',{'BEV sales':SER['ev']['battery_electric'],'Plug-in hybrid sales':SER['ev']['plug_in_hybrid']},'vehicles sold / year',False,['D3: affordability, charging, fleet replacement','Sales history is not fleet penetration.','L/M/H adoption calibration remains open.']),
('Fleet efficiency',SER['12_efficiency'],'L/100 km; draft engine',True,['D4: new-cohort efficiency and mileage','Dashed paths are existing model diagnostics.','OEM history and Medium calibration are open.'])]
for i,(label,data,unit,dash,notes) in enumerate(panels):
    yy=10+i*110
    b+=text(10,yy+17,label,14,BLUE,True)
    b+=text(10,yy+41,unit,11,GREY)
    b+=plot(data,x=185,y=yy+8,w=335,h=65,unit='',dash=dash,legend=False)
    b+=lines(570,yy+31,notes,12,20)
    labels=list(data)
    if label=='Rail recovery': labels=['Road','Rail']
    for j,series_label in enumerate(labels):
        b+=text(185+j*170,yy+105,series_label,10,BLUE if j==0 else SECOND)
svg('transport_timeseries',b)

b=''
for i,(key,unit) in enumerate([('05_eskom_fuel','million litres; own fleet'),('06_eskom_eaf','EAF %'),('generation','OCGT GWh')]):
    data=SER[key]
    if key=='generation':data={k:v for k,v in data.items() if k!='eskom_and_ipp_ocgt'}
    b+=plot(data,x=45+i*292,y=50,w=235,h=155,unit=unit)
b+=lines(35,270,['D5 levers: fleet availability, retirement dates, wind / solar / gas commissioning and diesel dispatch.',
    'Next quantitative layer: demand and generation by technology (GWh), then residual diesel litres.',
    'Load-shedding / private-backup history and calibrated replacement-generation paths remain open.'],13,23)
svg('power_timeseries',b)

# Reuse the reported named-plant capacity history without mislabelling it as production.
cap=SER['capacity']; years=sorted({int(y) for v in cap.values() for y in v}); totals={y:sum(v.get(str(y),0) for v in cap.values())/1000 for y in years}
high=max(totals.values())*1.1; cols=[BLUE,SECOND,'#8491B2','#BDBEC1','#767676','#404040']
b=text(45,20,'REPORTED CAPACITY BY PLANT',14,BLUE,True)+text(600,20,'SUPPLY-WORLD LEVERS',14,BLUE,True)
bottom={y:0 for y in years}
for i,(name,v) in enumerate(cap.items()):
    top={y:bottom[y]+v.get(str(y),0)/1000 for y in years}
    pts=[(45+(y-years[0])/(years[-1]-years[0])*480,250-top[y]/high*195) for y in years]
    pts += [(45+(y-years[0])/(years[-1]-years[0])*480,250-bottom[y]/high*195) for y in reversed(years)]
    b+='<polygon points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="{cols[i%6]}"/>'
    lx=45+(i%3)*175; ly=294+(i//3)*18
    b+=f'<rect x="{lx}" y="{ly-9}" width="10" height="10" fill="{cols[i%6]}"/>'+text(lx+15,ly,name,11,'#404040');bottom=top
for y in [years[0],2020,years[-1]]:b+=text(45+(y-years[0])/(years[-1]-years[0])*480-12,270,y,11,GREY)
b+=text(45,42,'thousand bbl/day; all products',12,GREY)
b+=text(45,64,f'{totals[years[0]]:.0f} in {years[0]} → {totals[years[-1]]:.0f} in {years[-1]}',14,BLUE,True)
b+=lines(600,62,['LOW: slower restarts / output losses','MEDIUM: reference plant paths','HIGH: recovery / additional output'],13,30,BLUE,True)
b+=lines(600,177,['S1 SAPREF: restart, ramp and yield','S2 Secunda: gas availability / MRG','S3 Natref: availability and utilisation','S4 PetroSA: restart and liquid yields'],12,25)
b+=text(45,336,'Historical capacity is not actual production. L/M/H output paths are not yet calibrated.',12,GREY)
svg('supply_stack',b)

# Registered illustrative operational sensitivity, independent of the market-world axes.
b=text(30,22,'GROSS HANDLING SENSITIVITY',14,BLUE,True)+text(540,22,'INVESTMENT TEST',14,BLUE,True)
for j,(site,v) in enumerate(DATA['handling'].items()):
    yy=70+j*120;b+=text(30,yy,site,16,BLUE,True)
    for i,(level,amount) in enumerate(v['annual_bn_litres'].items()):
        x=135+i*115
        b+=f'<rect x="{x}" y="{yy+80-amount/13*75}" width="62" height="{amount/13*75}" fill="{[SECOND,BLUE,GREY][i]}"/>'
        b+=text(x,yy+98,str(DATA['monthly_turns'][level])+' turns/mo',11,GREY)
        b+=text(x,yy+72-amount/13*75,f'{amount:.2f}',13,BLUE,True)
b+=lines(540,65,['Required turns = captured annual throughput','÷ eligible working capacity ÷ 12.',
    '', 'Compare with achievable receipt / dispatch,','pipeline access, peaks and stock policy.',
    '', 'Existing assets first; debottleneck or add','tanks where a profitable constraint remains.'],13,23)
b+=text(30,337,'bn litres/year; 1 / 2 / 3 monthly turns are an existing authored sensitivity, not measured site limits.',12,GREY)
svg('turnover',b)

# Geographic route comparison from the existing authored corridor geometry.
config=json.loads((ROOT/'pptx/story/corridor_comparison_2026_10_06.json').read_text())
from geo_reference import map_transform, layer_path
geo=json.loads(layer_path('ne_50m_admin_0_countries').read_text(encoding='utf-8'))
xy,map_scale=map_transform(25,30,530,270)
b='<defs><clipPath id="map"><rect x="25" y="30" width="530" height="278"/></clipPath></defs><g clip-path="url(#map)">'
for f in geo['features']:
    typ=f['geometry']['type']; coords=f['geometry']['coordinates']; polygons=coords if typ=='MultiPolygon' else [coords]
    for poly in polygons:
        ring=poly[0]
        if not any(10<=p[0]<=38 and -38<=p[1]<=-16 for p in ring):continue
        b+='<polygon points="'+' '.join(f'{xy(p[0],p[1])[0]},{xy(p[0],p[1])[1]}' for p in ring)+'" fill="#ECEEF2" stroke="white"/>'
for r in config['routes']:
    color={'west':GREY,'east':SECOND,'pipe':BLUE,'vopak':BLUE}[r['style']]
    b+='<polyline points="'+' '.join(f'{xy(*p)[0]},{xy(*p)[1]}' for p in r['waypoints'])+f'" fill="none" stroke="{color}" stroke-width="2.5"'+(' stroke-dasharray="5 4"' if r['style']=='pipe' else '')+'/>'
b+='</g>'
for name in ['Walvis Bay','Matola / Maputo','Durban','Lesedi*','Gauteng']:
    x,y=xy(*config['points'][name]);b+=f'<circle cx="{x}" cy="{y}" r="4" fill="{BLUE}"/>'
    dx,dy={'Walvis Bay':(-15,-12),'Matola / Maputo':(6,16),'Durban':(8,12),'Lesedi*':(-26,30),'Gauteng':(-60,-15)}[name]
    b+=text(x+dx,y+dy,name.replace('*',''),12,BLUE,True)
b+=f'<path d="M45 275v-25l-4 8m4-8l4 8" fill="none" stroke="{BLUE}"/>'
b+=text(40,244,'N',10,BLUE,True)
b+=f'<path d="M45 293h{500000*map_scale}" stroke="{BLUE}" stroke-width="2"/>'
b+=text(45,308,'500 km (nominal)',9,GREY)
b+=text(42,330,'LAEA projection; schematic road / pipeline candidates; access unverified.',10,GREY)
b+=text(580,35,'SAME PRODUCT, SAME DESTINATION',13,BLUE,True)
b+=lines(580,68,['Delivered cost = product + handling +','transport + border + losses + finance.',
    '', 'Bearable logistics charge = destination','price less product, other costs and margin.',
    '', 'Headroom = bearable less actual charge.',
    'Capacity and reliability constrain capture.',
    '', 'Domestic origins include Secunda / Natref;',
    'routes, access and tariffs need validation.'],12,22)
svg('corridor_map',b)

# Four consistent monochrome icons for the thesis rows.
icons=[('<path d="M5 30h35l-6 9H13Z M16 15h18v15 M22 9h8v6"/>','ship'),('<path d="M8 10h12v12H8Z M30 28h12v12H30Z M20 16h15v12"/>','route'),('<circle cx="24" cy="25" r="17"/><path d="M24 25l9-10 M9 32h30"/>','turns'),('<path d="M6 6h36v36H6Z M18 6v36 M30 6v36 M6 18h36 M6 30h36"/>','matrix')]
for body,name in icons:
    (OUT/f'icon_{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><g fill="none" stroke="{BLUE}" stroke-width="2.4" stroke-linejoin="round">{body}</g></svg>')
print('Prepared quantitative trend, transport, power, supply, turnover and corridor visuals.')
