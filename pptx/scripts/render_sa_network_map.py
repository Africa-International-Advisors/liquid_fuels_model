"""Render source road geometry and topology-derived paths in the shared projection."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from shapely.geometry import shape
from geo_reference import map_transform,layer_path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/delivered/sa_layout_2026_10_08_v16'
DATA=ROOT/'output/delivered/geospatial/2026_10_08'
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
def el(tag,**attrs):return ET.Element('{'+NS+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
tree=ET.parse(OUT/'corridor_map.svg');root=tree.getroot();g=root.find('{'+NS+'}g')
# Replace the old map group only; the approved commentary and panel frame stay.
for child in list(g):
    if child.tag.endswith('g') and child.get('transform') and len(list(child))>10:g.remove(child)
defs=el('defs');clip=el('clipPath',id='mapclip');clip.append(el('rect',x=0,y=42,width=546,height=263));defs.append(clip);root.insert(0,defs)
m=el('g',**{'clip-path':'url(#mapclip)'});g.insert(0,m)
xy,scale=map_transform(5,36,535,275)
def line(coords):return 'M'+'L'.join(f'{x:.2f},{y:.2f}' for x,y in [xy(*p[:2]) for p in coords])
def text(parent,x,y,value,size=10,fill='#595959',bold=False,anchor='start'):
    t=el('text',x=x,y=y,font_size=size,fill=fill,font_weight='700' if bold else '400',text_anchor=anchor);t.text=value;parent.append(t)
countries=json.loads(layer_path('ne_50m_admin_0_countries').read_bytes())
for f in countries['features']:
    geom=f['geometry'];polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
    for polygon in polys:
        m.append(el('path',d=' '.join(line(r)+'Z' for r in polygon),fill='#EEF0F3',stroke='#FFFFFF',stroke_width='.7',fill_rule='evenodd'))
provinces=json.loads(layer_path('zaf_provinces').read_bytes())
for f in provinces['features']:
    if 'Gauteng' not in str(f['properties']):continue
    geom=shape(f['geometry']).simplify(.01).__geo_interface__;polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
    for poly in polys:m.append(el('path',d=' '.join(line(r)+'Z' for r in poly),fill='#D2DCF0',stroke='#879BC2',stroke_width='.6'))
for name,color,width in [('roads','#BCC4CF','.28'),('rails','#7C8D9D','.32')]:
    for f in json.loads((DATA/f'{name}.geojson').read_bytes())['features']:
        if name=='roads' and f['properties'].get('highway') not in ['motorway','trunk','primary']:continue
        coords=shape(f['geometry']).simplify(.008).coords
        attrs={'stroke_dasharray':'1.5 1'} if name=='rails' else {}
        m.append(el('path',d=line(coords),fill='none',stroke=color,stroke_width=width,**attrs))
colors={'Durban':'#0A2373','Matola / Maputo':'#546CA2','Walvis Bay':'#66747F'}
for f in json.loads((DATA/'connectivity_routes.geojson').read_bytes())['features']:
    m.append(el('path',d=line(shape(f['geometry']).simplify(.005).coords),fill='none',stroke='#FFFFFF',stroke_width='3.5'))
    m.append(el('path',d=line(shape(f['geometry']).simplify(.005).coords),fill='none',stroke=colors[f['properties']['origin']],stroke_width='1.8'))
for label,lon,lat in [('NAMIBIA',17.2,-25),('BOTSWANA',24,-22.7),('SOUTH AFRICA',23.5,-31.8),('MOZAMBIQUE',33,-21.8)]:
    x,y=xy(lon,lat);text(m,x,y,label,7.8,'#8B919B',False,'middle')
points=json.loads((ROOT/'pptx/story/corridor_comparison_2026_10_06.json').read_text())['points']
for name,dx,dy,anchor in [('Walvis Bay',-7,-10,'start'),('Matola / Maputo',8,-7,'start'),('Durban',8,11,'start'),('Gauteng',-12,-15,'end'),('Lesedi*',-14,23,'end')]:
    x,y=xy(*points[name]);m.append(el('circle',cx=x,cy=y,r=3.3,fill='#0A2373',stroke='white',stroke_width='.6'))
    if name in ['Gauteng','Lesedi*']:m.append(el('path',d=f'M{x},{y}L{x+dx},{y+dy-4}',fill='none',stroke='#0A2373',stroke_width='.6'))
    text(m,x+dx,y+dy,name.replace('*',''),10,'#0A2373',True,anchor)
places=json.loads((DATA/'places.geojson').read_bytes())['features']
for name,label,dx,dy in [('Natref','Natref',-35,38),('Secunda','Secunda area',27,18)]:
    matches=[f for f in places if f['properties'].get('name')==name and (f['properties'].get('industrial')=='refinery' if name=='Natref' else f['properties'].get('place')=='city')]
    if matches:
        x,y=xy(*matches[0]['geometry']['coordinates'])
        m.append(el('rect',x=x-2.5,y=y-2.5,width=5,height=5,fill='#FFFFFF',stroke='#0A2373',stroke_width=1))
        m.append(el('path',d=f'M{x},{y}L{x+dx},{y+dy-4}',fill='none',stroke='#767676',stroke_width='.55'))
        text(m,x+dx,y+dy,label,8.5,'#595959',False,'end' if dx<0 else 'start')
# A compact key is outside the map clipping frame.
for x,color,label,dash in [(18,'#0A2373','Road connectivity',False),(172,'#7C8D9D','Mapped rail',True)]:
    attrs={'stroke_dasharray':'3 2'} if dash else {}
    g.append(el('path',d=f'M{x} 314h20',stroke=color,stroke_width=1.5,**attrs));text(g,x+26,318,label,9)
text(g,18,337,'OSM geometry; routes test connectivity, not tanker access or operating service.',9)
m.append(el('path',d='M30 277v-20l-3 6m3-6l3 6',fill='none',stroke='#0A2373'))
text(m,26,250,'N',9,'#0A2373',True)
m.append(el('path',d=f'M30 294h{500000*scale}',stroke='#0A2373',stroke_width=1.3));text(m,30,304,'500 km',7.5)
tree.write(OUT/'corridor_map.svg',encoding='utf-8',xml_declaration=True)
storypath=ROOT/'pptx/story/sa_market_story_v16_2026_10_08.json'
story=json.loads(storypath.read_text(encoding='utf-8'))
story['slides'][7]['note']='© OpenStreetMap contributors (ODbL; osm.org/copyright) / Geofabrik; Natural Earth; geoBoundaries. Shared LAEA projection. Paths test road connectivity, not tanker access. Secunda uses a city reference; Natref a mapped site. Terminal access, turn restrictions and operating rail/pipeline services remain unvalidated.'
storypath.write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
