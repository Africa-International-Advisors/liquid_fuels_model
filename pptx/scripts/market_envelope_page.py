"""Build a presentation-only data-shape example; no forecast or allocation engine.

All volumes are authored illustrative rows, not model assumptions or Vopak actuals.
Uses kickoff appendix geography; tabulates and checks supplied example identities.
"""
from pathlib import Path
import csv
import html
import json
import math
import shutil

ROOT=Path(__file__).resolve().parents[2]
STORY=ROOT/'pptx'/'story'
OUT=ROOT/'pptx'/'output'/'delivered'/'supporting'

def read(name):
    with (STORY/name).open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))

def total(rows,key,**filters):
    return sum(float(r[key]) for r in rows if r.get(key) and all(r.get(k)==v for k,v in filters.items()))

def main():
    national=read('illustrative_national_balance.csv')
    market=read('illustrative_market_catchments.csv')
    routes=read('illustrative_terminal_routes.csv')
    for r in national:
        p=r['product']
        assert math.isclose(total(market,'demand_bn_l',product=p),float(r['demand_bn_l']))
        assert math.isclose(total(market,'required_imports_bn_l',product=p),float(r['required_imports_bn_l']))
        assert math.isclose(float(r['demand_bn_l'])+float(r['exports_bn_l'])+float(r['stock_build_bn_l'])-float(r['domestic_supply_bn_l']),float(r['required_imports_bn_l']))
    for r in market:
        if r['commercial_envelope_bn_l']:
            assert float(r['demand_bn_l'])>=float(r['feasible_service_bn_l'])>=float(r['commercial_envelope_bn_l'])>=float(r['current_unique_vopak_bn_l'])
            assert math.isclose(float(r['additional_candidate_bn_l'])+float(r['current_unique_vopak_bn_l']),float(r['commercial_envelope_bn_l']))
    durban=total(routes,'volume_bn_l',origin='Durban')
    lesedi=total(routes,'volume_bn_l',destination='Lesedi')
    shared=total(routes,'volume_bn_l',origin='Durban',destination='Lesedi')
    unique=total(market,'current_unique_vopak_bn_l')
    assert math.isclose(durban+lesedi-shared,unique)
    assert math.isclose(lesedi,total(routes,'volume_bn_l',origin='Lesedi'))

    def fmt(v): return f'{float(v):.1f}'
    def table(headers,rows,cls=''):
        return '<table class="'+cls+'"><thead><tr>'+''.join('<th>'+html.escape(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join(('<tr class="total">' if row[0]=='Total' else '<tr>')+''.join('<td>'+html.escape(str(c))+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table>'
    balance=table(['Fuel','Demand','Domestic','Imports'],[[r['product'].title(),fmt(r['demand_bn_l']),fmt(r['domestic_supply_bn_l']),fmt(r['required_imports_bn_l'])] for r in national]+[['Total','21.0','7.0','14.0']])
    regions=['Eastern coastal','Inland','Western coastal','Other regions']
    regiontable=table(['Market','Demand','Imports','Role'],[[reg,fmt(total(market,'demand_bn_l',region=reg)),fmt(total(market,'required_imports_bn_l',region=reg)),{'Eastern coastal':'Durban example','Inland':'Lesedi example'}.get(reg,'Unassessed')] for reg in regions])
    bounds=table(['Catchment','Demand','Feasible','Access','Current','Additional'],[[reg,fmt(total(market,'demand_bn_l',region=reg)),fmt(total(market,'feasible_service_bn_l',region=reg)),fmt(total(market,'commercial_envelope_bn_l',region=reg)),fmt(total(market,'current_unique_vopak_bn_l',region=reg)),fmt(total(market,'additional_candidate_bn_l',region=reg))] for reg in regions[:2]]+[['Total','14.5','12.0','8.5','3.0','5.5']])
    def bar(label,value,color,width=300):
        w=value/21*width
        return f'<div class="barrow"><span>{label}</span><svg viewBox="0 0 {width+55} 29" aria-label="{label}: {value} billion litres"><rect x="0" y="5" width="{w}" height="18" fill="{color}"/><text x="{w+8}" y="20">{value:.1f}</text></svg></div>'
    bars=''.join(bar(l,v,c) for l,v,c in [('SA demand',21,'#B9C6D6'),('Catchment demand',14.5,'#879CBC'),('Feasible service',12,'#566E9D'),('Commercial access',8.5,'#102574')])
    bars+='<div class="barrow"><span>Within access</span><svg viewBox="0 0 355 36"><rect y="5" width="42.86" height="18" fill="#102574"/><rect x="42.86" y="5" width="78.57" height="18" fill="#41A6A0"/><text x="129" y="20">3.0 current + 5.5 candidate</text></svg></div>'

    # Existing appendix outline and node coordinates; envelopes are conceptual.
    geo=json.loads((ROOT/'pptx/assets/maps/ne_110m_admin_0_countries.geojson').read_text(encoding='utf-8'))
    def xy(lon,lat):return 24+(lon-16)*21,30+(-22-lat)*21
    polygons=[]
    for f in geo['features']:
        if f['properties']['ADMIN']!='South Africa':continue
        g=f['geometry']
        for poly in g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]:
            pts=' '.join(f'{xy(*p)[0]:.1f},{xy(*p)[1]:.1f}' for p in poly[0])
            polygons.append(f'<polygon points="{pts}" fill="#F0F3F7" stroke="#AAB7C9"/>')
    dx,dy=xy(31.03,-29.88);lx,ly=xy(28.39,-26.44);cx,cy=xy(18.43,-33.91)
    map_svg=f'''<svg class="map" viewBox="0 0 420 355" role="img" aria-label="Conceptual Durban and inland catchments over South Africa">
    {''.join(polygons)}<ellipse cx="{lx}" cy="{ly}" rx="75" ry="46" fill="#102574" fill-opacity=".12" stroke="#102574" stroke-dasharray="5 4"/>
    <ellipse cx="{dx-12}" cy="{dy+5}" rx="44" ry="56" fill="#41A6A0" fill-opacity=".12" stroke="#41A6A0" stroke-dasharray="5 4"/>
    <path d="M {dx} {dy} L {lx} {ly}" stroke="#102574" stroke-width="4" fill="none"/>
    <circle cx="{dx}" cy="{dy}" r="5" fill="#102574"/><circle cx="{lx}" cy="{ly}" r="5" fill="#102574"/>
    <text x="{lx-93}" y="{ly-54}" class="maphead">Inland demand 10.0</text><text x="{lx-88}" y="{ly-34}">Lesedi / Jameson Park area</text>
    <text x="{dx-92}" y="{dy+77}" class="maphead">Eastern demand 4.5</text><text x="{dx-26}" y="{dy+26}">Durban</text>
    <circle cx="{cx}" cy="{cy}" r="4" fill="#8B97A8"/><text x="{cx-14}" y="{cy+23}">Cape Town / west</text><text x="{cx-14}" y="{cy+42}">Demand 4.0; access unassessed</text>
    <text x="{lx+12}" y="{(ly+dy)/2+4}">Corridor concept</text></svg>'''
    facility=table(['Facility','Receipt throughput','Shared flow'],[['Durban','2.8','1.8 to Lesedi'],['Lesedi','2.0','Includes that 1.8']])
    schemas=table(['Data table','One row represents','Key fields','Example'],[
        ['National balance','Fuel × period × scenario','Demand; domestic supply; exports; stock change; imports','Petrol: 9.0 demand − 4.0 supply = 5.0 imports'],
        ['Catchment demand','Region × fuel × period × scenario','Demand; imported/domestic supply; catchment membership','Eastern petrol: 1.8 demand; 0.9 imports'],
        ['Route flows','Origin × destination × fuel × period × scenario','Route ID; volume; capacity/access evidence; overlap ID','Durban → Lesedi: 0.6 petrol + 1.2 diesel'],
        ['Commercial envelope','Catchment/customer × fuel × period × scenario','Feasible volume; access exclusions; current unique flow; additional candidate','Inland: 8.2 feasible → 6.0 accessible; 2.0 current'],
        ['Evidence and status','Each observation or assumption','Actual / modelled / illustrative / unknown; source; owner; date','All values on this page: illustrative only']])
    html_page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Illustrative South Africa fuel market envelope</title><style>
    *{box-sizing:border-box}body{font:16px Arial,sans-serif;color:#172B3A;background:#eef1f5;margin:0}.page{max-width:1540px;margin:24px auto;background:white;padding:34px 42px}h1{font-size:34px;line-height:1.15;margin:8px 0 10px;max-width:1250px}h2{font-size:20px;color:#102574;margin:0 0 15px}h3{font-size:17px;margin:14px 0 7px}.kicker{color:#102574;font-size:14px;letter-spacing:.4px}.sub{margin:0 0 18px;color:#536171}.disclosure{padding:11px 0;border-top:1px solid #AAB7C9;border-bottom:1px solid #AAB7C9;color:#914D00;font-size:15px;font-weight:bold}.analysis{display:grid;grid-template-columns: .9fr 1.1fr 1.2fr;gap:30px;margin-top:24px}.section+.section{border-left:1px solid #D8DFE8;padding-left:26px}table{width:100%;border-collapse:collapse;font-size:14px}th{text-align:left;color:#536171;font-weight:bold;border-bottom:2px solid #102574;padding:8px 5px}td{padding:9px 5px;border-bottom:1px solid #D8DFE8;vertical-align:top}tr:last-child td{font-weight:bold}.note{font-size:13px;line-height:1.45;color:#536171}.map{width:100%;height:300px}.map text{font:13px Arial;fill:#172B3A}.map .maphead{font-weight:bold;font-size:15px}.barrow{display:grid;grid-template-columns:140px 1fr;align-items:center;margin:5px 0;font-size:13px}.barrow svg{width:100%}.barrow svg text{font:14px Arial;fill:#172B3A}.equation{font-size:21px;color:#102574;margin:18px 0 8px;font-weight:bold}.candidates{font-size:20px;color:#187A76;line-height:1.3;margin:14px 0}.bottom{margin-top:24px;border-top:1px solid #AAB7C9;padding-top:14px}.evidence{display:grid;grid-template-columns:1fr 1fr;gap:36px;font-size:14px;line-height:1.45}.details{max-width:1540px;margin:24px auto;padding:30px 42px;background:white}.details table{font-size:15px}.details tr:last-child td{font-weight:normal}a{color:#102574}.legend{font-size:12px;color:#536171} @media(max-width:1000px){.analysis{grid-template-columns:1fr}.section+.section{border-left:0;padding-left:0}.evidence{grid-template-columns:1fr}}@media print{body{background:white}.page{margin:0;padding:16px;max-width:none}.details{break-before:page}.analysis{grid-template-columns:.9fr 1.1fr 1.2fr}h1{font-size:26px}table{font-size:12px}.map{height:245px}.note{font-size:11px}@page{size:A3 landscape;margin:12mm}}
    </style></head><body><main class="page"><div class="kicker">SOUTH AFRICA LIQUID FUELS OUTLOOK · PETROL AND DIESEL</div><h1>Demand, regional catchments and the market Vopak could serve</h1><p class="sub">Analytical data shape · example annual period · billion litres per year · jet excluded from client totals</p><div class="disclosure">ILLUSTRATIVE ONLY — all volumes and access assumptions are fabricated to show the analysis. Current Vopak actuals have not been supplied.</div><div class="analysis">
    <section class="section"><h2>01 National demand–supply balance</h2>BALANCE<div class="equation">21.0 demand − 7.0 domestic = 14.0 imports</div><p class="note">Exports and stock changes are zero in this example. The real balance includes both. Import requirement is distinct from available imports and unmet demand.</p><h3>Demand belongs to markets</h3>REGIONS<p class="note">Regional demands sum to 21.0 and import allocations to 14.0. Regional imported/domestic splits are illustrative.</p></section>
    <section class="section"><h2>02 Durban and inland catchments</h2>MAP<p class="legend">Dashed envelopes are conceptual screening areas, not verified boundaries. The corridor uses the kickoff appendix geography; route access/capacity still needs evidence.</p><h3>Catchments are defined by routes</h3><p class="note">Eastern and inland demand totals 14.5. Other markets remain outside the first assessment; they are not assumed inaccessible. Competitor routes, product compatibility and delivery economics determine the real envelope.</p></section>
    <section class="section"><h2>03 Current service and capture envelope</h2>BARS<p class="note">The catchment contains domestic and imported fuel. It is not a subset of imports alone. Feasible volumes respect routes; commercial access further reflects customers, contracts and competitors.</p><h3>Illustrative facility receipts</h3>FACILITY<div class="equation">2.8 + 2.0 − 1.8 overlap = 3.0</div><p class="note">Unique demand served is 3.0, although facility receipts total 4.8. Fuel passing through Durban and then Lesedi is counted once as market demand.</p><p class="candidates">8.5 accessible − 3.0 current = 5.5 additional candidate volume</p><p class="note">An assumed opportunity envelope, not a forecast of wins or guaranteed throughput.</p></section></div>
    <div class="bottom">BOUNDS<div class="evidence"><p><strong>Populate actual demand and current flows:</strong> validated provincial/product demand; domestic production and trade; Vopak receipts/dispatch by product, customer and destination; transfer IDs linking Durban to Lesedi.</p><p><strong>Evidence for potential capture:</strong> feasible routes and shared capacity, competing terminals/flows, customer access and contracts. Detailed storage sizing is optional. The same fields extend across periods and demand/supply scenarios.</p></div><p class="note">Reference: Analyst Kickoff appendix pp. 31–38, especially storage/corridor pages 36–38; Natural Earth outline. Existing storage capacities are not converted into throughput. Volumes: authored illustrative CSVs, not model results or published actuals.</p></div></main>
    <section class="details"><h2>The underlying data tables</h2><p>These linked tables are the intended analytical structure. Every numeric example is illustrative. Regional allocations, access and actual throughput require separate evidence.</p>SCHEMAS<p>Example rows: <a href="illustrative_national_balance.csv">national balance</a> · <a href="illustrative_market_catchments.csv">catchments and market envelope</a> · <a href="illustrative_terminal_routes.csv">terminal route flows</a></p></section></body></html>'''
    for key,value in [('BALANCE',balance),('REGIONS',regiontable),('MAP',map_svg),('BARS',bars),('FACILITY',facility),('BOUNDS',bounds),('SCHEMAS',schemas)]:
        html_page=html_page.replace(key,value)
    OUT.mkdir(parents=True,exist_ok=True)
    html_page=html_page.replace('tr:last-child td{font-weight:bold}', 'tr.total td{font-weight:bold}')
    target=OUT/'Vopak_market_envelope_illustrative_2026_10_06.html'
    target.write_text(html_page,encoding='utf-8')
    for name in ['illustrative_national_balance.csv','illustrative_market_catchments.csv','illustrative_terminal_routes.csv']:
        shutil.copy2(STORY/name,OUT/name)
    print(target)
    print('Example identities reconciled; page uses no model outputs or actual terminal volumes.')

if __name__=='__main__': main()
