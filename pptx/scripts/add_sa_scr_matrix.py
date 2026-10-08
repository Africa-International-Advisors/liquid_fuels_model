"""Add the agreed SCR synthesis and nine-world decision framework to story copy."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
folder=root/'pptx/story'
story=json.loads((folder/'sa_market_story_reorganised_2026_10_07.json').read_text(encoding='utf-8'))
scr=dict(title='Five arguments connect the market evidence to Vopak’s investment choice',section=4,sub='',
    headers=['Argument','Situation','Complication','Resolution / decision'],column_widths=[120,239,239,240.8],font_size=12,
    rows=[
        ['Transport demand','Subdued aggregate growth masks different product trends. Road freight supports diesel use.','Sector growth, rail recovery, EVs and efficiency change fuel demand.','Define L/M/H demand paths and translate activity into fuel volumes.'],
        ['Power demand','Power shortages supported diesel use; Eskom consumption has recently fallen.','Recovery may persist or reverse through outages and replacement delays.','Include explicit power assumptions in the same L/M/H demand paths.'],
        ['Domestic supply','Reduced local production has increased reliance on imports.','SAPREF, Natref and Secunda can change domestic fuel output materially.','Define L/M/H domestic supply paths. Cross with demand to create nine import worlds.'],
        ['Corridor competition','Durban connects imported fuel to inland customers.','Alternative gateways, delivered costs, reliability and access alter flows.','Translate each world into Durban-accessible volumes using explicit routing assumptions.'],
        ['Vopak investment','Durban and Lesedi provide a coastal–inland asset position.','Capture, usable capacity and commercial returns determine expansion needs.','Compare existing capacity, debottlenecking and expansion across the matrix. M/M is baseline.'],
    ],note='SCR synthesis of the preceding evidence and agreed scenario design. L/M/H = Low/Medium/High. Medium is the baseline; numerical calibration and commercial inputs remain open.')
matrix=dict(title='Nine demand–supply worlds frame the choice, with Medium / Medium as baseline',section=4,sub='',
    headers=['Fuel demand / domestic supply','HIGH supply','MEDIUM supply','LOW supply'],column_widths=[120,239,239,240.8],font_size=12,body_height=282,header_height=40,matrix=True,
    rows=[
        ['LOW demand','L / H\nLOWEST IMPORT PRESSURE\nTest existing-capacity use before expansion.','L / M\nLower imports than baseline.\nTest utilisation and customer capture.','L / L\nDemand and supply both fall.\nNet import effect depends on their relative change.'],
        ['MEDIUM demand','M / H\nLower imports than baseline.\nSupply recovery reduces import needs.','M / M\nBASELINE\nReference imports, terminal throughput and capacity headroom.','M / L\nHigher imports than baseline.\nSupply losses increase import needs.'],
        ['HIGH demand','H / H\nDemand and supply both rise.\nNet import effect depends on their relative change.','H / M\nHigher imports than baseline.\nDemand growth increases import needs.','H / L\nHIGHEST IMPORT PRESSURE\nTest debottlenecking or expansion if capturable flows exceed capacity.'],
    ],caption='Each cell will report imports, Vopak Durban / Lesedi throughput, capacity headroom and investment choice.',
    note='Qualitative framework, not calculated results. Import directions hold exports and stock movements comparable. The diagonal contrasts investment worlds; routing, capture and returns determine the actual choice. M/M calibration remains open.')
story['slides'][9:9]=[scr,matrix]
story['cover_status']='SCR and nine-world framework; calibration pending'
story['main_story_pages']='2–14'
story['appendix_pages']='15–24'
story['scenario_framework']={'demand':['Low','Medium','High'],'domestic_supply':['High','Medium','Low'],'baseline':'Medium / Medium','diagonal':['Low / High','Medium / Medium','High / Low'],'status':'Framework adopted; quantitative results not yet populated'}
# Refresh existing cross-references after inserting two main-story pages.
for slide in story['slides']:
    note=slide.get('note','')
    for a,b in [('appendix pp14–16','appendix pp16–18'),('appendix pp16, 19–20','appendix pp18, 21–22'),('appendix p21;','appendix p23;'),('pp17–18.','pp19–20.'),('appendix p22.','appendix p24.'),('pages 2–12','pages 2–14')]:
        note=note.replace(a,b)
    note=note.replace('Scenarios remain deferred.','Demand and supply paths require calibration.').replace('Scenarios follow separately.','Nine-world calibration follows the agreed framework.')
    slide['note']=note
    for row in slide.get('rows',[]):
        for i,value in enumerate(row):
            row[i]=value.replace('Scenarios follow separately.','Nine-world calibration follows.').replace('scenarios follow separately.','nine-world calibration follows.')
index=story['slides'][13]
index['rows'][0][2]='Pages 16–18 support situation pages 2–3.'
index['rows'][1][2]='Pages 19–20 support the transport complication on page 7.'
index['rows'][2][2]='Pages 21–22 support situation page 3 and power complication page 8.'
index['rows'][3][2]='Pages 23–24 support corridor and share questions on pages 7, 10 and 13.'
(folder/'sa_market_story_scr_matrix_2026_10_07.json').write_text(json.dumps(story,indent=2,ensure_ascii=False),encoding='utf-8')
assert len(story['slides'])==23
print('Prepared 24 pages; SCR page 11, matrix page 12; appendix starts page 15.')
