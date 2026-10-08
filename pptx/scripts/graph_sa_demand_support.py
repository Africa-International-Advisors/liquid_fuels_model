"""Horizontal comparisons with common zero baselines within each unit panel."""
import json,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/delivered/demand_support_2026_10_08/bars'
OUT.mkdir(parents=True,exist_ok=True)
d=json.loads((OUT.parent/'evidence.json').read_text())
def txt(x,y,t,size=15,color='#222222',anchor='start',bold=False):
    return f'<text x="{x}" y="{y}" font-family="Lato" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{700 if bold else 400}">{html.escape(t)}</text>'
def panel(name,items,maximum,foot=''):
    a=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 135">']
    for key,label,cy in items:
        v=d[key];a.append(txt(0,cy+4,label,14))
        a.append(f'<path d="M110 {cy-17}v32" stroke="#B8B8B8" stroke-width=".8"/>')
        for year,yy,color in [('start',cy-15,'#849BC1'),('end',cy+2,'#0A2373')]:
            width=235*v[year]/maximum
            a.append(f'<rect x="110" y="{yy}" width="{width:.3f}" height="12" fill="{color}"/>')
            a.append(txt(114+width,yy+11,f'{v[year]:,.1f}',14,color))
        a.append(txt(494,cy+5,f"{v['percent_change']:+.1f}%",16,'#0A2373','end',True))
    if foot:a.append(txt(0,124,foot,13,'#595959'))
    a.append('</svg>');(OUT/f'{name}.svg').write_text(''.join(a),encoding='utf-8')
panel('power',[('fuel','OCGT fuel',41)],1200,'EAF: 54.56% → 60.60%   |   Cost*: R23.87bn → R13.32bn')
panel('freight',[('road','Road',32),('rail','Rail',88)],1050)
panel('sector',[('agriculture','Agriculture',24),('mining','Mining',67),('manufacturing','Manufacturing',110)],550)
(OUT/'legend.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 155 20"><rect x="0" y="3" width="12" height="12" fill="#849BC1"/>'+txt(18,15,'2024',14)+'<rect x="80" y="3" width="12" height="12" fill="#0A2373"/>'+txt(98,15,'2025',14)+'</svg>',encoding='utf-8')
s=json.loads((ROOT/'pptx/story/sa_market_story_v20_2026_10_08.json').read_text(encoding='utf-8'));p=s['slides'][5]
p['headers']=['Demand support','2024 vs 2025','Implication for demand']
p['rows'][0][1]='';p['rows'][1][1]='';p['rows'][2][1]=''
p['rows'][0][2]='450m fewer litres in one year.\nD5: test whether Eskom recovery persists as plants retire and new generation arrives.'
p['rows'][1][2]='Road still carries 85.3% of tonnes.\nD2: rail recovery matters where freight can transfer; tonnes alone do not measure diesel savings.'
p['rows'][2][2]='Sector trends diverge.\nD1: agriculture grew; mining was flat and manufacturing declined. Activity is not fuel volume.'
p['comparison_bars']=[{'name':n,'path':(OUT/f'{n}.png').relative_to(ROOT).as_posix(),'unit':u} for n,u in [('power','Own OCGT fuel · million litres · financial years'),('freight','Reported payload · million tonnes · calendar years'),('sector','Real GVA · Rbn, 2015 prices · calendar years')]]
p['note']+=' Bars start at zero; scales are common within each panel, not across different units. Light blue = 2024; navy = 2025.'
(ROOT/'pptx/story/sa_market_story_v21_2026_10_08.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
