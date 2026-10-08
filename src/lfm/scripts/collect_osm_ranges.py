"""Download immutable dated country extracts in checked, retryable byte ranges."""
import requests,json,hashlib,time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'external/sources/geospatial/2026_10_08/osm'
def country(name):
    path=OUT/f'{name}.osm.pbf';meta=OUT/f'{name}.json'
    if path.exists() and meta.exists():return json.loads(meta.read_text())
    url=f'https://download.geofabrik.de/africa/{name}-261006.osm.pbf'
    r=requests.get(url,headers={'Range':'bytes=0-0'},timeout=40);r.raise_for_status()
    total=int(r.headers['Content-Range'].split('/')[-1]);chunk=4*1024*1024
    cache=OUT/(name+'_chunks');cache.mkdir(exist_ok=True)
    def part(start):
        end=min(total-1,start+chunk-1);p=cache/str(start)
        if p.exists() and p.stat().st_size==end-start+1:return p
        for attempt in range(4):
            try:
                resp=requests.get(url,headers={'Range':f'bytes={start}-{end}'},timeout=50)
                resp.raise_for_status()
                assert resp.status_code==206 and resp.headers['Content-Range']==f'bytes {start}-{end}/{total}'
                assert len(resp.content)==end-start+1
                p.write_bytes(resp.content);return p
            except Exception:
                if attempt==3:raise
                time.sleep(1)
    with ThreadPoolExecutor(max_workers=8) as pool:parts=list(pool.map(part,range(0,total,chunk)))
    with path.open('wb') as f:
        for p in parts:f.write(p.read_bytes())
    with path.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    item={'country':name,'url':url,'retrieved_at':datetime.now(timezone.utc).isoformat(),'path':path.relative_to(ROOT).as_posix(),'bytes':total,'sha256':digest,'licence':'ODbL 1.0','attribution':'OpenStreetMap contributors; Geofabrik','download':'HTTP byte ranges checked against Content-Range'}
    meta.write_text(json.dumps(item,indent=2));print(name,total,flush=True);return item
if __name__=='__main__':
    result=[country(n) for n in ['south-africa','namibia','botswana','mozambique']]
    (OUT/'manifest.json').write_text(json.dumps(result,indent=2))
