"""One cached, filtered OSM extract retaining node topology and source tags."""
import json,hashlib
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'external/sources/geospatial/2026_10_08/overpass'
OUT.mkdir(parents=True,exist_ok=True)
url='https://overpass.private.coffee/api/interpreter'
bbox='-35.5,12.5,-20,34'
query=f'''[out:json][timeout:180];(
way[highway~"^(motorway|trunk|primary|secondary)(_link)?$"]({bbox});
way[railway=rail]({bbox});way[man_made=pipeline]({bbox});
relation[type=restriction]({bbox});
nwr[name~"Vopak|Natref|Secunda",i]({bbox});
node[barrier=border_control]({bbox}););out body geom;'''
(OUT/'query.overpassql').write_text(query)
path=OUT/'network.json'
if not path.exists():
    request=Request(url,data=urlencode({'data':query}).encode(),headers={'User-Agent':'SA-Fuels-Geospatial-Reference/1.0'})
    with urlopen(request,timeout=240) as response:raw=response.read()
    doc=json.loads(raw)
    if 'remark' in doc:raise RuntimeError(doc['remark'])
    path.write_bytes(raw)
else:doc=json.loads(path.read_bytes())
manifest=[{'url':url,'retrieved_at':datetime.now(timezone.utc).isoformat(),'osm_base':doc.get('osm3s',{}),'query':query,'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'licence':'ODbL 1.0; OpenStreetMap contributors'}]
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('Cached OSM elements:',len(doc['elements']),flush=True)
