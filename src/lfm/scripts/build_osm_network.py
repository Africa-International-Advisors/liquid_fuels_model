"""Build a local road topology database and sourced road/rail/pipeline GeoJSON."""
import json,sqlite3,hashlib
from pathlib import Path
from lfm.scripts.osm_pbf_reader import collect
from pyproj import Geod
from lfm.model.core.routing import directions,shortest_path
ROOT=Path(__file__).resolve().parents[3]
RAW=ROOT/'external/sources/geospatial/2026_10_08/osm'
OUT=ROOT/'output/delivered/geospatial/2026_10_08'
OUT.mkdir(parents=True,exist_ok=True)
dbpath=OUT/'transport.sqlite'
if dbpath.exists():raise RuntimeError('Preserve database; choose a new build vintage.')
db=sqlite3.connect(dbpath)
db.executescript('''CREATE TABLE ways(id INTEGER PRIMARY KEY,version INTEGER,mode TEXT,tags TEXT,nodes TEXT,geometry TEXT);
CREATE TABLE nodes(id INTEGER PRIMARY KEY,lon REAL,lat REAL);
CREATE TABLE edges(way_id INTEGER,segment INTEGER,u INTEGER,v INTEGER,length_m REAL,PRIMARY KEY(way_id,segment,u,v));
CREATE TABLE restrictions(id INTEGER PRIMARY KEY,tags TEXT,members TEXT);
CREATE TABLE places(id TEXT PRIMARY KEY,tags TEXT,lon REAL,lat REAL,position_basis TEXT);
CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT);''')
highways={'motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link'}
filtered=ROOT/'external/sources/geospatial/2026_10_08/overpass'
if (filtered/'network.json').exists():
    RAW=filtered
    doc=json.loads((RAW/'network.json').read_bytes())
    for e in doc['elements']:
        tags=e.get('tags',{})
        if e['type']=='way' and e.get('geometry'):
            mode='road' if tags.get('highway') in highways else 'rail' if tags.get('railway')=='rail' else 'pipeline' if tags.get('man_made')=='pipeline' else None
            coords=[[p['lon'],p['lat']] for p in e['geometry']]
            if mode:db.execute('INSERT OR IGNORE INTO ways VALUES(?,?,?,?,?,?)',(e['id'],e.get('version',0),mode,json.dumps(tags),json.dumps(e['nodes']),json.dumps(coords)))
            if any(k in tags.get('name','').lower() for k in ['vopak','natref','secunda']):db.execute('INSERT OR IGNORE INTO places VALUES(?,?,?,?,?)',(f'way/{e["id"]}',json.dumps(tags),sum(p[0] for p in coords)/len(coords),sum(p[1] for p in coords)/len(coords),'vertex mean; entrance unverified'))
        elif e['type']=='node':db.execute('INSERT OR IGNORE INTO places VALUES(?,?,?,?,?)',(f'node/{e["id"]}',json.dumps(tags),e['lon'],e['lat'],'OSM point; entrance unverified'))
        elif e['type']=='relation' and tags.get('type')=='restriction':db.execute('INSERT OR IGNORE INTO restrictions VALUES(?,?,?)',(e['id'],json.dumps(tags),json.dumps(e.get('members',[]))))
    db.commit();print('Filtered OSM extract loaded',flush=True)
else:
    for country in ['south-africa','namibia','botswana','mozambique']:
        collect(RAW/f'{country}.osm.pbf',highways,db)
        db.commit();print('Extracted',country,flush=True)
geod=Geod(ellps='WGS84');counts={}
for mode in ['road','rail','pipeline']:
    path=OUT/f'{mode}s.geojson';count=0
    with path.open('w',encoding='utf-8') as f:
        f.write('{"type":"FeatureCollection","features":[')
        for way_id,version,tags_raw,ids_raw,geom_raw in db.execute('SELECT id,version,tags,nodes,geometry FROM ways WHERE mode=?',(mode,)):
            tags=json.loads(tags_raw);ids=json.loads(ids_raw);coords=json.loads(geom_raw)
            if count:f.write(',')
            f.write(json.dumps({'type':'Feature','id':f'way/{way_id}','properties':{'osm_id':way_id,'osm_version':version,'mode':mode,**tags},'geometry':{'type':'LineString','coordinates':coords}}));count+=1
            if mode=='road':
                db.executemany('INSERT OR IGNORE INTO nodes VALUES(?,?,?)',[(n,*p) for n,p in zip(ids,coords)])
                orient=directions(tags)
                for i,(a,b) in enumerate(zip(coords,coords[1:])):
                    length=geod.inv(*a,*b)[2]
                    for direction in orient:
                        u,v=(ids[i],ids[i+1]) if direction==1 else (ids[i+1],ids[i])
                        db.execute('INSERT OR IGNORE INTO edges VALUES(?,?,?,?,?)',(way_id,i,u,v,length))
        f.write(']}')
    counts[mode]=count;db.commit()
db.executescript('CREATE INDEX edges_from ON edges(u); CREATE INDEX edges_to ON edges(v);')
places=[{'type':'Feature','id':pid,'properties':{'osm_id':pid,'position_basis':basis,**json.loads(tags)},'geometry':{'type':'Point','coordinates':[lon,lat]}} for pid,tags,lon,lat,basis in db.execute('SELECT * FROM places')]
(OUT/'places.geojson').write_text(json.dumps({'type':'FeatureCollection','features':places}),encoding='utf-8')
graph={}
for u,v,length in db.execute('SELECT u,v,length_m FROM edges'):graph.setdefault(u,[]).append((v,length))
nodes={n:(lon,lat) for n,lon,lat in db.execute('SELECT * FROM nodes')}
points=json.loads((ROOT/'pptx/story/corridor_comparison_2026_10_06.json').read_text())['points']
def snap(point):
    n=min(graph,key=lambda n:geod.inv(*point,*nodes[n])[2])
    return n,geod.inv(*point,*nodes[n])[2]
end,end_offset=snap(points['Gauteng']);routes=[];checks=[]
for origin in ['Durban','Matola / Maputo','Walvis Bay']:
    start,offset=snap(points[origin]);length,path=shortest_path(graph,start,end)
    check={'origin':origin,'destination':'Gauteng reference point','origin_snap_m':offset,'destination_snap_m':end_offset,'length_m':length,'connected':bool(path),'status':'major-road connectivity only; no truck/turn-restriction/border-cost profile'}
    checks.append(check)
    if path:routes.append({'type':'Feature','properties':check,'geometry':{'type':'LineString','coordinates':[nodes[n] for n in path]}})
(OUT/'connectivity_routes.geojson').write_text(json.dumps({'type':'FeatureCollection','features':routes}),encoding='utf-8')
(OUT/'route_checks.json').write_text(json.dumps(checks,indent=2))
manifest=json.loads((RAW/'manifest.json').read_text())
summary={'counts':counts,'nodes':len(nodes),'directed_edges':db.execute('SELECT count(*) FROM edges').fetchone()[0],'turn_restrictions_preserved':db.execute('SELECT count(*) FROM restrictions').fetchone()[0],'sources':manifest,'crs':'EPSG:4326','licence':'ODbL 1.0; OpenStreetMap contributors','network_scope':'Motorway/trunk/primary/secondary and links; '+('filtered extract only' if RAW==filtered else 'full PBF retained for local streets and future routing-engine ingestion'),'limitations':['Road-only geometric smoke test, not tanker navigation','Turn restrictions preserved but not applied by smoke test','Conditional/HGV/hazmat/weight/height rules require a vehicle profile','Rail and pipeline layers are source geometry, not operating services or usable capacity','Facility labels remain approximate; road snapping is not terminal access','No travel time or delivered cost inferred'],'owner':'Manish; Nigel review','expiry_trigger':'Before freight cost modelling, routing deployment or investment reliance'}
for path in OUT.glob('*.geojson'):summary.setdefault('layers',[]).append({'path':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
db.execute('INSERT INTO metadata VALUES(?,?)',('build',json.dumps(summary)));db.commit();db.close()
(OUT/'catalog.json').write_text(json.dumps(summary,indent=2));print(json.dumps({'counts':counts,'checks':checks}),flush=True)
