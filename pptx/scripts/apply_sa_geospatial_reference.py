"""Consume the shared map asset and preserve authored overlays as separate GeoJSON."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
folder=ROOT/'output/delivered/geospatial/2026_10_07'
config=json.loads((ROOT/'pptx/story/corridor_comparison_2026_10_06.json').read_text())
points=[{'type':'Feature','properties':{'name':name,'status':'approximate authored location'},'geometry':{'type':'Point','coordinates':coords}} for name,coords in config['points'].items()]
routes=[{'type':'Feature','properties':{'name':r['name'],'style':r['style'],'status':'schematic candidate; not downloaded alignment'},'geometry':{'type':'LineString','coordinates':r['waypoints']}} for r in config['routes']]
catalog=json.loads((folder/'catalog.json').read_text())
for name,features in [('authored_places',points),('authored_corridors',routes)]:
    path=folder/f'{name}.geojson'
    path.write_text(json.dumps({'type':'FeatureCollection','features':features},indent=2),encoding='utf-8')
    catalog['layers']=[r for r in catalog['layers'] if r['id']!=name]
    catalog['layers'].append({'id':name,'path':str(path.relative_to(ROOT)),'source':'pptx/story/corridor_comparison_2026_10_06.json','features':len(features),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'status':'authored schematic; unverified'})
(folder/'catalog.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
(folder/'corridor_map.svg').write_bytes((ROOT/'output/sa_feedback_2026_10_07/corridor_map.svg').read_bytes())
story=json.loads((ROOT/'pptx/story/sa_market_story_executive_2026_10_07.json').read_text(encoding='utf-8'))
slide=story['slides'][7]
assert 'gateways' in slide['title']
slide['custom_chart']='output/delivered/geospatial/2026_10_07/corridor_map.png'
slide['note']='Natural Earth country geometry; shared LAEA projection with uniform scale. GeoJSON source catalogue: output/delivered/geospatial/2026_10_07. Corridor lines and places remain authored approximations; operating routes, facility positions and access require validation.'
(ROOT/'pptx/story/sa_market_story_geospatial_2026_10_07.json').write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
