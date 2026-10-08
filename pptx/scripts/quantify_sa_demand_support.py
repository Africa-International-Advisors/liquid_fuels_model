"""Format historical evidence into the existing demand-support table."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
d=json.loads((ROOT/'output/delivered/demand_support_2026_10_08/evidence.json').read_text())
s=json.loads((ROOT/'pptx/story/sa_market_story_v19_2026_10_08.json').read_text(encoding='utf-8'))
row=s['slides'][5]
def line(label,key,unit,dec=1):
    v=d[key];return f"{label}: {v['start']:,.{dec}f} → {v['end']:,.{dec}f}{unit} ({v['percent_change']:+.1f}%)."
row['headers']=['Demand support','Measured scale and change','What this means for demand']
row['column_widths']=[165,365,308.8]
row['rows']=[
 ['Power\ngeneration','FY2024 → FY2025\n'+line('Own OCGT fuel','fuel','m L')+'\n'+f"EAF: {d['eaf']['start']:.2f}% → {d['eaf']['end']:.2f}% (+{d['eaf']['change']:.2f} pp)."+'\n'+line('Fuel cost*','cost','bn rand',2),f"Eskom used {abs(d['fuel']['change']):.0f}m fewer litres in one year. D5 tests whether recovery persists, against retirements and replacement timing. Private backup is separate."],
 ['Road\nfreight','2024 → 2025 | reported payload\n'+line('Road','road',' Mt')+'\n'+line('Rail','rail',' Mt'),f"Road still carried {d['road_share_2025']:.1f}% of reported tonnes in 2025. D2 tests transferable tonne-km and fuel intensity; payload alone does not establish diesel displacement."],
 ['Sector\nactivity','2024 → 2025 | real GVA, Rbn (2015 prices)\n'+line('Agriculture','agriculture','')+'\n'+line('Mining','mining','')+'\n'+line('Manufacturing','manufacturing',''),'Agriculture grew strongly while mining was flat and manufacturing declined. D1 needs sector-specific activity paths; these output changes are not measured fuel-volume changes.']]
row['note']='Eskom Integrated Report 2025 pp100,141: own-fleet diesel + kerosene; *cost includes storage/demurrage. Stats SA P7162 Dec 2025 p7: both years from the revised vintage. Stats SA P0441 Q2 2026 annual real GVA: agriculture includes forestry/fishing. FY and calendar-year periods shown separately.'
row['evidence_data']='output/delivered/demand_support_2026_10_08/evidence.json'
(ROOT/'pptx/story/sa_market_story_v20_2026_10_08.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
