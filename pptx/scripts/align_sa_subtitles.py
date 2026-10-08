"""Move exhibit subtitles onto the native PowerPoint panel alignment grid."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/delivered/sa_subtitles_2026_10_08_v17'
OUT.mkdir(parents=True,exist_ok=True)
ET.register_namespace('','http://www.w3.org/2000/svg')
story=json.loads((ROOT/'pptx/story/sa_market_story_v16_2026_10_08.json').read_text(encoding='utf-8'))
for page,split in [(6,590),(8,590),(9,560),(10,510),(12,None),(13,325)]:
    s=story['slides'][page-2];p=ROOT/Path(s['custom_chart']).with_suffix('.svg');tree=ET.parse(p);heads=[]
    for parent in tree.getroot().iter():
        for e in list(parent):
            if e.tag.endswith('text') and e.get('y')=='20':heads.append(e.text);parent.remove(e)
    starts=[36,55+(split+11)*800/880] if split else [36,55+304*800/880,55+596*800/880]
    s['panel_subtitles']=[{'text':text,'x':x,'width':(starts[i+1]-x-22 if i+1<len(starts) else 874.8-x)} for i,(text,x) in enumerate(zip(heads,starts))]
    tree.write(OUT/p.name,encoding='utf-8',xml_declaration=True)
    s['custom_chart']=(OUT/p.with_suffix('.png').name).relative_to(ROOT).as_posix()
(ROOT/'pptx/story/sa_market_story_v17_2026_10_08.json').write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
