"""Match the supplied black-heading / circular-chevron reference exhibit."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'output/delivered/sa_panel_layout_2026_10_08'
OUT=ROOT/'output/delivered/sa_reference_style_2026_10_08'
OUT.mkdir(parents=True,exist_ok=True)
NS='http://www.w3.org/2000/svg'; ET.register_namespace('',NS)
def node(tag,**attrs):return ET.Element('{'+NS+'}'+tag,{k:str(v) for k,v in attrs.items()})
def txt(group,x,y,value,bold=False,size=12):
    t=node('text',x=x,y=y,fill='#595959',**{'font-size':size,'font-weight':'700' if bold else '400'})
    t.text=value;group.append(t)
splits={'demand_trend':590,'imports_change':590,'corridor_map':560,'turnover':510,'future_capacity':325}
for file in SOURCE.glob('*.svg'):
    root=ET.parse(file).getroot();g=root.find('{'+NS+'}g');name=file.stem
    for parent in g.iter():
        for c in list(parent):
            if c.tag.endswith('path') and c.get('stroke')=='#B4BAC6':c.set('stroke','#555555');c.set('stroke-width','0.6')
            if c.tag.endswith('rect') and c.get('fill')=='#F4F5F7':c.set('fill','#FFFFFF')
            if c.tag.endswith('text') and c.get('y')=='20':
                c.set('fill','#000000')
                c.text=c.text.capitalize().replace('2036 capacity cases','2036 capacity cases')
    if name in splits:
        split=splits[name]
        for c in list(g):
            if c.tag.endswith('path') and c.get('d')==f'M{split-4} 23l7 7-7 7':g.remove(c)
        g.append(node('circle',cx=split,cy=31,r=10,fill='#0A2373'))
        g.append(node('path',d=f'M{split-2} 26l5 5-5 5',stroke='#FFFFFF',fill='none',**{'stroke-width':'1.3'}))
    if name in ['demand_trend','imports_change']:
        for c in g.iter('{'+NS+'}text'):
            if c.get('x')=='620' and c.get('y')!='20':
                c.set('fill','#595959')
                if c.get('font-weight')=='bold':
                    c.text=('01 | ' if c.get('y') in ['65','68'] else '02 | ')+c.text
    if name in ['corridor_map','turnover']:
        rx=580 if name=='corridor_map' else 540
        for parent in g.iter():
            for c in list(parent):
                if c.tag.endswith('text') and float(c.get('x','0'))>=rx and c.get('y')!='20':parent.remove(c)
        blocks=(
          [('01 | Compare delivered cost',['Product, handling, transport, border,','losses and inventory finance.']),
           ('02 | Establish price headroom',['Bearable charge less actual logistics cost.','Capacity and reliability constrain capture.']),
           ('03 | Include domestic sources',['Secunda and Natref also serve inland','demand; routes and access need validation.'])]
          if name=='corridor_map' else
          [('01 | Calculate required turns',['Captured annual throughput divided by','eligible working capacity, then by 12.']),
           ('02 | Test achievable handling',['Check receipt / dispatch, pipeline access,','seasonal peaks and stock policy.']),
           ('03 | Identify the binding constraint',['Use existing assets first; debottleneck or','add tanks where the constraint is profitable.'])])
        for i,(heading,body) in enumerate(blocks):
            y=64+i*65;txt(g,rx,y,heading,True)
            for j,line in enumerate(body):txt(g,rx,y+21+j*16,line,size=11.5)
        g.append(node('path',d=f'M{rx} 260H855',stroke='#546CA2',**{'stroke-width':'.8'}))
        txt(g,rx,280,'Next action',True,13)
        action=['Match route costs and access to the','same product and Gauteng destination.'] if name=='corridor_map' else ['Confirm working tankage and achieved turns','before sizing any additional storage.']
        for j,line in enumerate(action):txt(g,rx,302+j*16,line,size=11.5)
    if name=='power_timeseries':
        leads=['01 | Separate dispatch demand','02 | Test recovery durability','03 | Time replacement generation']
        bodies=[['Separate Eskom from private backup.','Load-shedding and backup histories','are still needed.'],['Test outages and retirement timing.','Sustained availability reduces','pressure on diesel generation.'],['Wind, solar and gas timing matters.','Calibrate dependable generation','before forecasting diesel litres.']]
        for c in g.iter('{'+NS+'}text'):
            y=float(c.get('y',0));x=float(c.get('x',0))
            if y>=269:
                c.set('fill','#595959')
                if y==269:
                    c.text=leads[min(2,int(x//292))];c.set('font-weight','700');c.set('font-size','11.5')
                else:
                    c.text=bodies[min(2,int(x//292))][int((y-286)/17)]
    ET.ElementTree(root).write(OUT/file.name,encoding='utf-8',xml_declaration=True)
story=json.loads((ROOT/'pptx/story/sa_market_story_panel_layout_2026_10_08.json').read_text(encoding='utf-8'))
for page,name in {6:'demand_trend',8:'imports_change',9:'corridor_map',10:'turnover',12:'power_timeseries',13:'future_capacity'}.items():
    story['slides'][page-2]['custom_chart']=f'output/delivered/sa_reference_style_2026_10_08/{name}.png'
story['black_titles']=True
story['cover_status']='Reference exhibit styling applied; scenario and commercial calibration remain open'
(ROOT/'pptx/story/sa_market_story_reference_style_2026_10_08.json').write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
