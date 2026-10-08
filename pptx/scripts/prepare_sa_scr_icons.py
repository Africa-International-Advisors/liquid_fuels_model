"""Five matching line icons for the SCR argument rows."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/delivered/sa_scr_icons_2026_10_08'
OUT.mkdir(parents=True,exist_ok=True)
icons={
 'transport':'<path d="M5 12h24v22H5Z M29 20h9l6 8v6H29 M33 21v7h10"/><circle cx="13" cy="36" r="4"/><circle cx="36" cy="36" r="4"/>',
 'power':'<path d="M28 4L10 27h13l-3 17 18-25H25Z"/>',
 'supply':'<path d="M6 42V23l12 7V20l12 9V13h9v29Z M31 13V6h6v7 M11 36h3 M21 36h3 M32 36h3"/>',
 'corridor':'<circle cx="9" cy="12" r="4"/><circle cx="39" cy="12" r="4"/><circle cx="24" cy="39" r="4"/><path d="M9 16v7l15 8v4 M39 16v7l-15 8 M19 27l5 4 5-4"/>',
 'investment':'<ellipse cx="16" cy="14" rx="10" ry="5"/><path d="M6 14v22c0 7 20 7 20 0V14 M6 25c0 7 20 7 20 0 M32 35V13 M27 18l5-5 5 5 M31 39h11"/>'
}
for name,body in icons.items():
    (OUT/f'icon_{name}.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><g fill="none" stroke="#0A2373" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'+body+'</g></svg>',encoding='utf-8')
story=json.loads((ROOT/'pptx/story/sa_market_story_reference_style_2026_10_08.json').read_text(encoding='utf-8'))
s=story['slides'][2]
assert s['headers'][0]=='Argument'
s['icons']=list(icons)
s['icon_dir']='output/delivered/sa_scr_icons_2026_10_08'
for row,label in zip(s['rows'],['Transport\ndemand','Power\ndemand','Domestic\nsupply','Corridor\ncompetition','Vopak\ninvestment']):row[0]=label
(ROOT/'pptx/story/sa_market_story_row_icons_2026_10_08.json').write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
