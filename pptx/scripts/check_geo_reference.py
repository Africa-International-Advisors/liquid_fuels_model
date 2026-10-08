"""Verify geometry provenance and uniform map fitting, independent of slide layout."""
import hashlib
import json
import math
from pyproj import Transformer
from shapely.geometry import shape
from geo_reference import ROOT, REFERENCE, map_transform

catalog=json.loads((ROOT/REFERENCE['catalog']).read_text())
for item in catalog['layers']:
    path=ROOT/item['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'], item['id']
    data=json.loads(path.read_text(encoding='utf-8'))
    assert len(data['features'])==item['features']
    assert all(not shape(f['geometry']).is_empty for f in data['features'])
assert next(v['features'] for v in catalog['layers'] if v['id']=='zaf_provinces')==9
project=Transformer.from_crs('EPSG:4326', REFERENCE['display_crs'], always_xy=True)
for viewport in [(25,30,530,270),(0,0,300,600)]:
    xy,scale=map_transform(*viewport)
    origin=(25,-29)
    for endpoint in [(26,-29),(25,-28),(31,-30),(14.5,-23)]:
        projected=math.dist(project.transform(*origin), project.transform(*endpoint))
        drawn=math.dist(xy(*origin),xy(*endpoint))
        assert math.isclose(drawn/projected,scale,rel_tol=1e-10)
print('Geospatial reference: hashes, feature counts, nonempty geometries, nine provinces and uniform scale pass.')
