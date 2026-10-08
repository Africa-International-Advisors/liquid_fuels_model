"""Preserve online cartographic sources and build a catalogued regional GeoJSON library."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from shapely.geometry import shape, box

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT/'external/sources/geospatial/2026_10_07'
OUT = ROOT/'output/delivered/geospatial/2026_10_07'
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

def fetch(url, path):
    if not path.exists():
        with urlopen(Request(url, headers={'User-Agent': 'SA-market-cartographic-reference/1.0'}), timeout=120) as response:
            data = response.read()
        json.loads(data)
        path.write_bytes(data)
    return json.loads(path.read_bytes())

commit = fetch('https://api.github.com/repos/nvkelso/natural-earth-vector/commits/master', RAW/'natural_earth_commit.json')['sha']
names = ['ne_50m_admin_0_countries', 'ne_10m_roads', 'ne_10m_railroads', 'ne_10m_ports', 'ne_10m_populated_places']
region = box(10, -36, 36, -16)

def collect(name):
    url = f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{commit}/geojson/{name}.geojson'
    path = RAW/f'{name}.geojson'
    data = fetch(url, path)
    features = [f for f in data['features'] if f.get('geometry') and shape(f['geometry']).intersects(region)]
    target = OUT/f'{name}_southern_africa.geojson'
    target.write_text(json.dumps({'type':'FeatureCollection','features':features}, ensure_ascii=False), encoding='utf-8')
    return {'id':name, 'url':url, 'source_commit':commit, 'licence':'Public domain',
            'raw_path':str(path.relative_to(ROOT)), 'path':str(target.relative_to(ROOT)),
            'sha256_raw':hashlib.sha256(path.read_bytes()).hexdigest(),
            'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'features':len(features), 'status':'cartographic reference; no operational validation',
            'selection':'whole features intersecting [10,-36,36,-16]; not clipped'}

with ThreadPoolExecutor(max_workers=5) as pool:
    entries = list(pool.map(collect, names))
api = 'https://www.geoboundaries.org/api/current/gbOpen/ZAF/ADM1/'
meta = fetch(api, RAW/'geoboundaries_zaf_adm1_metadata.json')
path = RAW/'geoboundaries_zaf_adm1.geojson'
data = fetch(meta['gjDownloadURL'], path)
target = OUT/path.name
target.write_bytes(path.read_bytes())
entries.append({'id':'zaf_provinces', 'url':meta['gjDownloadURL'], 'metadata_url':api,
                'licence':meta.get('boundaryLicense'), 'boundary_year':meta.get('boundaryYearRepresented'),
                'attribution':meta.get('boundarySource'), 'licence_source':meta.get('licenseSource'),
                'raw_path':str(path.relative_to(ROOT)), 'path':str(target.relative_to(ROOT)),
                'sha256':hashlib.sha256(target.read_bytes()).hexdigest(), 'features':len(data['features'])})
catalog = {'retrieved_at':datetime.now(timezone.utc).isoformat(), 'storage_crs':'EPSG:4326; longitude, latitude',
           'owner':'Nigel / analyst team', 'refresh_trigger':'new mapping vintage or material boundary/network correction',
           'layers':entries, 'limitations':'Reference geography only. Roads/rail do not establish operating service, fuel compatibility or access. Facility coordinates and pipeline alignment need separate validation.'}
(OUT/'catalog.json').write_text(json.dumps(catalog, indent=2), encoding='utf-8')
print(json.dumps({e['id']:e['features'] for e in entries}))
