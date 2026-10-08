"""Render resolved historical/future capacity stacks and update slide copy."""
import json
from html import escape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/delivered/supply_capacity_cases_2026_10_08'
d=json.loads((OUT/'data.json').read_text())
blue='#0A2373'; grey='#767676'
assets=['Astron Energy','Enref','Natref','PetroSA','Sapref','Sasol','SAPREF proposal']
colors=['#0A2373','#546CA2','#8491B2','#BDBEC1','#767676','#404040','#008D80']
def text(x,y,s,size=12,color='#222',bold=False):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}">{escape(str(s))}</text>'
def line(x1,y1,x2,y2,color='#DDD',dash=''):
    return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" stroke-dasharray="{dash}"/>'
def yy(value):return 225-value/1000/800*165
b=text(42,18,'REPORTED HISTORY',13,blue,True)+text(365,18,f'ILLUSTRATIVE {d["horizon_year"]} CAPACITY CASES',13,blue,True)
b+=text(42,38,'thousand bbl/day; nameplate / crude-equivalent footprint',11,grey)
for v in [0,200,400,600,800]:
    y=yy(v*1000);b+=line(42,y,840,y)+text(10,y+4,v,10,grey)
hist=d['history_bpd']; years=sorted(map(int,hist)); bottoms={y:0 for y in years}
for asset,col in zip(assets,colors):
    tops={y:bottoms[y]+hist[str(y)].get(asset,0) for y in years}
    pts=[(48+(y-years[0])/(years[-1]-years[0])*235,yy(tops[y])) for y in years]
    pts += [(48+(y-years[0])/(years[-1]-years[0])*235,yy(bottoms[y])) for y in reversed(years)]
    b+='<polygon points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="{col}"/>'
    bottoms=tops
for y in [years[0],2020,years[-1]]:b+=text(38+(y-years[0])/(years[-1]-years[0])*235,244,y,11,grey)
b+=text(48,yy(sum(hist[str(years[0])].values()))-8,round(sum(hist[str(years[0])].values())/1000),13,blue,True)
b+=text(257,yy(sum(hist[str(years[-1])].values()))-8,round(sum(hist[str(years[-1])].values())/1000),13,blue,True)
b+=line(325,50,325,289,grey,'4 4')
notes={'Low':['Natref unavailable','No SAPREF addition'], 'Medium':['Natref retained','No SAPREF addition'], 'High':['Natref retained','SAPREF +400 kbpd']}
for i,(name,values) in enumerate(d['cases_bpd'].items()):
    x=385+i*160;bottom=0
    for asset,col in zip(assets,colors):
        value=values.get(asset,0)
        if value:
            b+=f'<rect x="{x}" y="{yy(bottom+value)}" width="85" height="{yy(bottom)-yy(bottom+value)}" fill="{col}"/>'
        bottom+=value
    b+=text(x+22,yy(bottom)-8,round(bottom/1000),15,blue,True)
    b+=text(x+15,244,name.upper(),12,blue,True)
    for j,note in enumerate(notes[name]):b+=text(x-14,262+j*16,note,11)
b+=text(42,298,f'High-case timing: assumed {d["fid_year"]} FID + {d["construction_months"]} months → {int(d["addition_year"])} availability; no Natref closure date assumed.',11,grey)
for i,(asset,col) in enumerate(zip(assets,colors)):
    x=42+(i%4)*205;y=316+(i//4)*18
    b+=f'<rect x="{x}" y="{y-9}" width="9" height="9" fill="{col}"/>'+text(x+14,y,asset,11)
(OUT/'future_capacity.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 340"><rect width="880" height="340" fill="white"/><g font-family="Lato,Arial,sans-serif">'+b+'</g></svg>',encoding='utf-8')
story=json.loads((ROOT/'pptx/story/sa_market_story_geospatial_2026_10_07.json').read_text(encoding='utf-8'))
s=story['slides'][11]
assert 'Refinery recovery' in s['title']
s.update(title='SAPREF could expand the supply footprint, while Natref unavailability would reduce it',custom_chart='output/delivered/supply_capacity_cases_2026_10_08/future_capacity.png',
    takeaway='These capacity cases anchor the supply-axis discussion. Translate them into product output, then test imports, corridor capture and required tank turns in each of the nine worlds.',
    note='FIASA 2025 p49; registered review_capacity_scenarios.yaml and review_supply_worlds.yaml. Illustrative 2036 sensitivities, not calibrated production forecasts. Other plants held at 2025 reported values; Secunda gas/MRG and PetroSA restart effects remain unquantified. Low is not a Natref closure prediction.')
appendix=story['slides'][26]
assert 'Plant-level' in appendix['title']
appendix['title']='SAPREF and Natref define capacity sensitivities; plant output must complete the supply paths'
appendix['rows']=[
 ['S1 SAPREF','High illustration adds 400 kbpd: assumed 2029 FID plus 48 months gives 2033 availability. Low/Medium add none.','Separate the import phase from refinery commissioning; establish ramp-up, availability and product yields.'],
 ['S3 Natref','108 kbpd retained in Medium/High; excluded in the Low stress case at 2036. No closure date assumed.','This is a hypothetical availability test. Confirm operating outlook; do not infer closure from an outage.'],
 ['S2 Secunda','150 kbpd reported crude-equivalent footprint held in all three capacity illustrations.','Gas decline and MRG diversion can reduce liquid output without changing nameplate. Quantify the gas balance and liquids penalty.'],
 ['S4 PetroSA','No restart addition included in these three capacity illustrations.','Test funded restart scope, feedstock, timing and yields separately; zero reported contribution is not proof of dismantled capacity.']]
appendix['note']='Illustrative footprint cases: 250 / 358 / 758 kbpd; not a complete low/base/high production range. Owner: Manish; Nigel review. Resolve dates, operating factors, yields and gas effects before nine-world output adoption or investment use.'
story['cover_status']='Future capacity sensitivities added; production and commercial calibration remain open'
story['cover_date']='8 October 2026'
(ROOT/'pptx/story/sa_market_story_future_supply_2026_10_08.json').write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
