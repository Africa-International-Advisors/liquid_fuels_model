"""Lead with the investment thesis, then its SCR logic and scenario framework."""
import copy
import json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
folder=root/'pptx/story'
story=json.loads((folder/'sa_market_story_scr_matrix_2026_10_07.json').read_text(encoding='utf-8'))
old=story['slides']
thesis=copy.deepcopy(old[12])
thesis['title']='Vopak’s investment case rests on capturing imports through its Durban–Gauteng chain'
thesis['headers']=['Investment thesis','Supporting reason','What determines the choice']
thesis['rows']=[
    ['Capture imported fuel','Limited demand growth can coexist with greater import needs as domestic production changes.','Establish how much of that import requirement is accessible through Durban and can be captured by Vopak.'],
    ['Use the coastal–inland position','Durban and Lesedi give Vopak assets along the supply chain into Gauteng.','Delivered cost, reliable access and customer allocation determine throughput at each terminal.'],
    ['Make expansion conditional','The relevant investment is the capacity or handling constraint that prevents profitable customer volumes being served.','Use existing assets, debottleneck or add storage according to capturable flow, usable capacity and incremental returns.'],
    ['Test the thesis in nine worlds','Medium / Medium anchors the baseline. Low demand / High supply and High demand / Low supply frame contrasting import environments.','Choose an option that is justified across the relevant worlds, or phase commitment against explicit volume and return triggers.'],
]
thesis['note']='Working investment thesis, not an approved expansion recommendation. Supporting logic: p3; nine-world framework: p4; evidence and implications: pp5–14. Numerical calibration and commercial inputs remain open.'
scr=copy.deepcopy(old[9])
scr['title']='The investment thesis depends on imports, route access and profitable capacity use'
resolutions=[
    'Demand growth alone cannot establish expansion. L/M/H paths test the product volumes Vopak could serve.',
    'Power recovery can remove diesel support. The same demand paths must include explicit power assumptions.',
    'Domestic supply changes can create import needs even with flat demand. Cross L/M/H supply with demand.',
    'Vopak benefits only from accessible flows. Delivered economics and access translate imports into Durban volumes.',
    'Expand where capturable flows exceed usable capacity at an adequate return. Compare options across the nine worlds.',
]
for row,resolution in zip(scr['rows'],resolutions): row[3]=resolution
scr['note']='SCR synthesis supporting the opening investment thesis. L/M/H = Low/Medium/High; M/M is baseline. Matrix follows on p4. Each resolution is conditional on the evidence and calibration described in the pack.'
story['slides']=[thesis,scr,copy.deepcopy(old[10])]+copy.deepcopy(old[:9])+[copy.deepcopy(old[11])]+copy.deepcopy(old[13:])
story['cover_subtitle']='Investment thesis, scenario worlds and supporting evidence'
story['cover_status']='Top-down review draft; calibration pending'
story['opening_pages']='2: investment thesis; 3: SCR synthesis; 4: nine-world matrix'
story['situation_pages']='5–9'
story['complication_pages']='10–13'
story['share_inference_page']=14
# Main evidence shifts by three pages; appendix numbering stays unchanged.
appendix=story['slides'][13]
appendix['rows'][0][2]='Pages 16–18 support demand arguments on pages 5–6.'
appendix['rows'][1][2]='Pages 19–20 support the transport complication on page 10.'
appendix['rows'][2][2]='Pages 21–22 support historical diesel demand on page 6 and power risk on page 11.'
appendix['rows'][3][2]='Pages 23–24 support corridor and share questions on pages 10, 13 and 14.'
appendix['note']='Opening argument: thesis p2, SCR p3, matrix p4. Supporting analysis: pp5–14. Appendix exhibits provide detail for those arguments.'
story['slides'][3]['takeaway']='Petrol fell 19% and diesel rose 9% over 2013–2023. This supports the opening thesis: import requirements and accessible customer flows must establish the investment case alongside demand growth.'
story['slides'][12]['title']='Capacity proxies establish scale; customer throughput must establish the investment need'
assert len(story['slides'])==23
assert story['slides'][2]['matrix']
(folder/'sa_market_story_top_down_2026_10_07.json').write_text(json.dumps(story,indent=2,ensure_ascii=False),encoding='utf-8')
print('24 pages: investment thesis p2, SCR p3, matrix p4, supporting analysis pp5–14, appendix pp15–24.')
