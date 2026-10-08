"""Audit delivered network topology, provenance and diagnostic path geometry."""
import json,sqlite3,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'output/delivered/geospatial/2026_10_08'
catalog=json.loads((OUT/'catalog.json').read_text())
for source in catalog['sources']:
    with (ROOT/source['path']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==source['sha256']
for layer in catalog['layers']:
    path=OUT/layer['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==layer['sha256']
db=sqlite3.connect(OUT/'transport.sqlite')
assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert not db.execute('SELECT 1 FROM edges e LEFT JOIN nodes n ON e.u=n.id WHERE n.id IS NULL LIMIT 1').fetchone()
assert not db.execute('SELECT 1 FROM edges e LEFT JOIN nodes n ON e.v=n.id WHERE n.id IS NULL LIMIT 1').fetchone()
assert not db.execute('SELECT 1 FROM edges WHERE length_m < 0 OR length_m IS NULL LIMIT 1').fetchone()
for ids,geometry in db.execute('SELECT nodes,geometry FROM ways'):
    ids=json.loads(ids);coords=json.loads(geometry);assert len(ids)==len(coords)>=2
    assert all(math.isfinite(x) and math.isfinite(y) and -180<=x<=180 and -90<=y<=90 for x,y in coords)
checks=json.loads((OUT/'route_checks.json').read_text())
result={'database_integrity':'pass','edge_endpoints':'pass','coordinates_and_node_alignment':'pass','source_and_layer_hashes':'pass','route_checks':checks,'routing_readiness':'geometric diagnostic only; restrictions and site access remain unvalidated'}
(OUT/'qa.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
