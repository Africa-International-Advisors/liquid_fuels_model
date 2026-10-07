"""Reporting adapter for the registered terminal-turnover sensitivity."""
import csv
import json
from pathlib import Path

import yaml
from pptx.util import Inches
from lfm.model.supply.terminal_handling import annual_handling_m3


def turnover_cases(root):
    return yaml.safe_load((root.parent/'assumptions/2026/terminal_handling.yaml').read_text())['monthly_turns']['value']


def add_turnover_graph(s, root, brand):
    from convergence_feedback import clear_body, text, bar, line, replace, sales, inventory
    from brand_configs.vopak import THEME_COLOURS
    from pptx.dml.color import RGBColor
    demand_colour=RGBColor.from_string(THEME_COLOURS['accent4'])
    clear_body(s)
    rates = turnover_cases(root)
    values, _, _ = sales(root)
    with (root/'story/demand_map_regions_2026_10_06.csv').open(encoding='utf-8-sig') as f:
        members = list(csv.DictReader(f))
    names = ['Eastern coastal', 'Inland', 'Western coastal', 'Other / Northern Cape']
    labels = [('Eastern coast', 'EC/KZN'), ('Inland', 'GP/FS/LP/MP/NW'), ('Western coast', 'WC'), ('Other', 'Northern Cape')]
    locations = [['Durban', 'Richards Bay'], ['Lesedi', 'Isando'], ['Cape Town'], []]
    data = inventory(root)
    for q in s.shapes:
        if not q.has_text_frame: continue
        if q.name == 'Title 1':
            replace(q, 'R6. Compare regional demand with estimated annual handling capacity')
        elif abs(q.top-Inches(1.78))<10 and q.left<Inches(8):
            replace(q, 'Annual demand and gross handling equivalent | million m³/year')
        elif abs(q.top-Inches(1.78))<10:
            replace(q, 'What the estimate means')
        elif q.text.startswith('Source: DMPR'):
            replace(q, 'Source: DMPR 2022 sales; published site inventory; Blackmer/Dover 2013; Wood Mackenzie 2009. Turnover cases authored.')
    text(s, f'Base estimate: {rates["base"]} turns/month; published gross tankage', .5, 2.40, 7.05, .28, 11)
    bar(s,2.1,2.84,.11,.11,demand_colour,'Demand legend')
    text(s, 'Reported demand', 2.26, 2.79, 1.5, .22, 9)
    for x, label, colour in [(4.00, 'Vopak', brand.accent_primary), (5.1, 'Other listed', brand.accent_secondary)]:
        bar(s, x, 2.84, .11, .11, colour, 'Handling legend')
        text(s, label, x+.16, 2.79, 1.4, .22, 9)
    text(s, 'Upper bar: reported demand; lower stack: estimated handling', 2.1, 3.06, 4.9, .23, 9)
    x0=2.1; width=4.30; maximum=35
    for tick in [0,10,20,30]:
        x=x0+width*tick/maximum
        text(s, str(tick), x-.1, 3.33, .4, .2, 9)
        line(s, (x,3.57), (x,6.30), brand.grey_fill,.5)
    output=[]
    for i, (label, provinces) in enumerate(labels):
        y=3.65+i*.65
        demand=sum(values[r['province_code']] for r in members if r['region']==names[i])
        text(s,label,.5,y,1.5,.25,11)
        text(s,provinces,.5,y+.29,1.5,.23,9)
        dw=width*demand/maximum
        bar(s,x0,y,dw,.23,demand_colour,'Reported annual demand '+label)
        text(s,f'{demand:.2f}',x0+dw+.05,y-.035,.6,.23,9)
        parts=[];sx=x0
        for operator_flag in (True,False):
            rows=[r for r in data if r['site'] in locations[i] and (r['operator']=='Vopak')==operator_flag and r.get('gross_capacity_m3')]
            capacity=sum(float(r['gross_capacity_m3']) for r in rows)
            flow=annual_handling_m3(capacity,rates['base'])/1e6 if rows else None
            parts.append(flow)
            if flow is not None:
                w=width*flow/maximum
                bar(s,sx,y+.32,w,.23,brand.accent_primary if operator_flag else brand.accent_secondary,'Estimated base handling '+label)
                sx+=w
        known=[v for v in parts if v is not None]
        if known:
            cap=sum(float(r['gross_capacity_m3']) for r in data if r['site'] in locations[i] and r.get('gross_capacity_m3'))
            cases={k:annual_handling_m3(cap,v)/1e6 for k,v in rates.items()}
            text(s,f'{cases["base"]:.2f}',sx+.07,y+.29,.63,.24,10)
            output.append({'region':label,'demand_2022_million_m3_year':demand,'gross_handling_equivalent_million_m3_year':cases,'base_vopak_other':parts})
        else:
            text(s,'?  inventory incomplete',x0,y+.29,3.8,.25,10)
            output.append({'region':label,'demand_2022_million_m3_year':demand,'gross_handling_equivalent_million_m3_year':None})
    text(s, 'Same annual scale. Gross tankage × monthly turns × 12; not available fuel supply.', .5, 6.57, 7.05, .25, 9)
    text(s, 'Historical 2022 sales vs inventory checked 2026. Mixed products; missing sites; lease offers excluded. No regional shortage or market share is established.', .5, 6.80, 7.05, .24, 8)
    findings=[
        ('01 | Estimate now; replace with site data', 'Use two turns/month for the main comparison. The appendix tests one and three. These are authored estimates; no SA site rate is verified.'),
        ('02 | Operating limits set achievable volume', 'Gross handling equivalents assume the listed tankage can turn. Fuel compatibility, working space, downtime and receipt/dispatch limits still need confirmation.'),
        ('03 | Missing tankage is not a shortage', 'Inland coverage omits material operator capacities. Coastal handling can also serve inland customers. Do not add regional handling as unique national sales.')]
    for y,(heading,body) in zip([2.50,3.69,4.90],findings):
        text(s,heading,8.05,y,4.18,.30,11,True)
        text(s,body,8.05,y+.42,4.18,.74,11)
    line(s,(8.05,6.05),(12.25,6.05),brand.accent_secondary,1)
    text(s,'Next actions',8.05,6.23,4.18,.3,12,True)
    text(s,'Manish: verify dispatch and working capacity at the listed sites. Nigel: obtain client operating data. Replace the common range with site-specific turns.',8.05,6.55,4.18,.48,10.5)
    s.notes_slide.notes_text_frame.text+='\nTURNOVER-SCREEN: '+json.dumps(output)+'\nEvidence: '+(root/'story/terminal_turnover_evidence_2026_10_06.json').read_text(encoding='utf-8')


def link_storage_page(s, root, brand):
    from convergence_feedback import replace
    replacements={
        '01 | Capacity is a stock': '01 | Turnover connects this stock to p13',
        'Published tank volumes are not annual fuel deliveries or market share.':'At 1 / 2 / 3 turns/month, p13 estimates annual handling from this inventory. Actual deliveries and customer share still need evidence.',
        'The inventory is partial':'The inventory is partial',
    }
    for q in s.shapes:
        if not q.has_text_frame:continue
        if q.text in replacements:replace(q,replacements[q.text])
        elif q.text.startswith('01 | Capacity is a stock'):replace(q,'01 | Turnover connects this stock to p13')
        elif q.text.startswith('Published tank volumes are not annual'):replace(q,replacements['Published tank volumes are not annual fuel deliveries or market share.'])
    s.notes_slide.notes_text_frame.text+='\nLinked to registered turnover sensitivity on p13. Same site inventory; lease offers excluded from estimated operating handling. Replace 1/2/3 monthly gross turns with site dispatch and working-capacity evidence.'
