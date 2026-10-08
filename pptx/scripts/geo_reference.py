"""Shared map transform: a single metric scale preserves projected proportions."""
import json
from pathlib import Path
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = json.loads((ROOT/'pptx/assets/maps/reference.json').read_text())

def map_transform(x, y, width, height):
    projection = Transformer.from_crs('EPSG:4326', REFERENCE['display_crs'], always_xy=True)
    west, south, east, north = REFERENCE['extent_lonlat']
    perimeter = []
    for i in range(101):
        lon = west+(east-west)*i/100
        lat = south+(north-south)*i/100
        perimeter.extend([projection.transform(lon,south), projection.transform(lon,north),
                          projection.transform(west,lat), projection.transform(east,lat)])
    xmin, xmax = min(p[0] for p in perimeter), max(p[0] for p in perimeter)
    ymin, ymax = min(p[1] for p in perimeter), max(p[1] for p in perimeter)
    scale = min(width/(xmax-xmin), height/(ymax-ymin))
    left = x+(width-(xmax-xmin)*scale)/2
    top = y+(height-(ymax-ymin)*scale)/2
    def xy(lon,lat):
        px,py = projection.transform(lon,lat)
        return left+(px-xmin)*scale, top+(ymax-py)*scale
    return xy, scale

def layer_path(layer_id):
    catalog=json.loads((ROOT/REFERENCE['catalog']).read_text())
    return ROOT/next(row['path'] for row in catalog['layers'] if row['id']==layer_id)
