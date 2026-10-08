"""Preserve full Geofabrik country extracts for repeatable local network builds."""
import hashlib,json,shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'external/sources/geospatial/2026_10_08/osm'
OUT.mkdir(parents=True,exist_ok=True)
def download(country):
    url=f'https://download.geofabrik.de/africa/{country}-latest.osm.pbf'
    path=OUT/f'{country}.osm.pbf'; meta=OUT/f'{country}.json'
    if path.exists() and meta.exists():return json.loads(meta.read_text())
    with urlopen(Request(url,headers={'User-Agent':'SA-Fuels-Geospatial-Reference/1.0'}),timeout=120) as response:
        headers=dict(response.headers)
        with path.with_suffix('.part').open('wb') as dest:shutil.copyfileobj(response,dest,1024*1024)
    path.with_suffix('.part').rename(path)
    with path.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
    item={'country':country,'url':url,'retrieved_at':datetime.now(timezone.utc).isoformat(),'http_headers':headers,'path':path.relative_to(ROOT).as_posix(),'bytes':path.stat().st_size,'sha256':digest,'licence':'ODbL 1.0','attribution':'OpenStreetMap contributors; Geofabrik'}
    meta.write_text(json.dumps(item,indent=2));print(country,path.stat().st_size,flush=True)
    return item
with ThreadPoolExecutor(max_workers=2) as pool:result=list(pool.map(download,['south-africa','namibia','botswana','mozambique']))
(OUT/'manifest.json').write_text(json.dumps(result,indent=2))
