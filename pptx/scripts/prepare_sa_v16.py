"""Apply approved row icons, content-margin rules and appendix pagination."""
import json,re
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/delivered/sa_layout_2026_10_08_v16'
OUT.mkdir(parents=True,exist_ok=True)
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
story=json.loads((ROOT/'pptx/story/sa_market_story_row_icons_2026_10_08.json').read_text(encoding='utf-8'))
icons={
'sector':'<path d="M5 42V22l12 6V17l12 8V9h10v33Z M10 35h3 M21 35h3 M32 35h3 M31 9V4h6v5"/>',
'flow':'<path d="M4 14h18l-5-5 M22 14l-5 5 M4 33h18l-5-5 M22 33l-5 5"/><ellipse cx="34" cy="12" rx="8" ry="4"/><path d="M26 12v25c0 6 16 6 16 0V12"/>',
'turnover':'<path d="M9 19a16 16 0 0 1 28-6l4 5 M41 8v10H31 M39 29a16 16 0 0 1-28 6l-4-5 M7 40V30h10"/>',
'headroom':'<ellipse cx="20" cy="9" rx="13" ry="5"/><path d="M7 9v30c0 7 26 7 26 0V9 M7 28c0 7 26 7 26 0 M40 13v14 M37 16l3-3 3 3 M37 24l3 3 3-3"/>',
'return':'<path d="M6 7v34h36 M13 32l9-10 7 4 12-16 M32 10h9v9"/>'}
for name,body in icons.items():
    (OUT/f'icon_{name}.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><g fill="none" stroke="#0A2373" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'+body+'</g></svg>')
for name in ['transport','power']:
    (OUT/f'icon_{name}.svg').write_bytes((ROOT/f'output/delivered/sa_scr_icons_2026_10_08/icon_{name}.svg').read_bytes())
for page,names,labels in [(7,['power','transport','sector'],['Power\ngeneration','Road\nfreight','Sector\ndemand']),(15,['flow','turnover','headroom','return'],['Captured\nthroughput','Required\nturnover','Capacity\nheadroom','Financial\nreturn'])]:
    s=story['slides'][page-2];s['icons']=names;s['icon_dir']=OUT.relative_to(ROOT).as_posix()
    for row,label in zip(s['rows'],labels):row[0]=label
for page in [6,8,9,10,12,13]:
    s=story['slides'][page-2];source=ROOT/Path(s['custom_chart']).with_suffix('.svg')
    tree=ET.parse(source)
    for parent in tree.getroot().iter():
        for c in list(parent):
            if c.tag.endswith('path') and re.match(r'^M[\d.]+ 31[HL]',c.get('d','')):parent.remove(c)
    dest=OUT/source.name;tree.write(dest,encoding='utf-8',xml_declaration=True)
    s['custom_chart']=dest.with_suffix('.png').relative_to(ROOT).as_posix();s['margin_rules']=True
# Shift internal appendix references; never change cited source-document pages.
def renumber(text):
    return re.sub(r'(appendix\s+pp?)([\d,\s–\-]+)',lambda m:m[1]+re.sub(r'\d+',lambda n:str(int(n[0])+(int(n[0])>=16)),m[2]),text,flags=re.I)
def walk(v):
    if isinstance(v,str):return renumber(v)
    if isinstance(v,list):return [walk(x) for x in v]
    if isinstance(v,dict):return {k:walk(x) if k not in ['custom_chart','chart','icon_dir'] else x for k,x in v.items()}
    return v
story=walk(story)
story['slides'].insert(14,{'title':'Appendix','divider':True,'section':0,'subtitle':'Supporting evidence and calibration','note':'Detailed evidence, assumptions and remaining calibration requirements.'})
story['cover_status']='Updated exhibit layout and appendix; scenario and commercial calibration remain open'
(ROOT/'pptx/story/sa_market_story_v16_2026_10_08.json').write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
