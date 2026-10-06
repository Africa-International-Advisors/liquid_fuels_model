"""Simplify an existing illustrative road surface into a reach diagram.

This is a cartographic adapter, not a new catchment or volume calculation.
Connected cells retain the source map's schematic connection rule. The authored
volume deduction is not inferred from coloured area or provincial sales.
"""
import csv
import json

from pyproj import CRS, Transformer
from shapely.geometry import Polygon, shape, box
from shapely.ops import transform, unary_union
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from provincial_demand_map import NAMES


def freeform_polygon(q):
    path=q._element.xpath('.//a:custGeom/a:pathLst/a:path')[0]
    points=path.xpath('./a:moveTo/a:pt | ./a:lnTo/a:pt')
    sx=q.width/int(path.get('w'));sy=q.height/int(path.get('h'))
    return Polygon([(q.left+int(p.get('x'))*sx,q.top+int(p.get('y'))*sy) for p in points])


def draw_reach_map(dest, source, root, brand, text):
    frame=next(q for q in source.shapes if q.name.startswith('Map frame'))
    scale=4.55/7.05
    def xy(x,y):return Inches(.5)+(x-frame.left)*scale,Inches(3.03)+(y-frame.top)*scale
    def draw_polygon(geometry, fill, stroke=None, width=.6, name='Reach diagram'):
        polys=list(geometry.geoms) if geometry.geom_type=='MultiPolygon' else [geometry]
        for poly in polys:
            if poly.geom_type!='Polygon' or poly.is_empty:continue
            points=[tuple(int(v) for v in xy(*p)) for p in poly.exterior.coords]
            fb=dest.shapes.build_freeform(*points[0]);fb.add_line_segments(points[1:],close=True)
            q=fb.convert_to_shape();q.name=name
            if fill is None:q.fill.background()
            else:q.fill.solid();q.fill.fore_color.rgb=fill
            if stroke is None:q.line.fill.background()
            else:q.line.color.rgb=stroke;q.line.width=Pt(width)
            # Retain holes such as Lesotho when a union creates an interior ring.
            for interior in poly.interiors:
                pts=[tuple(int(v) for v in xy(*p)) for p in interior.coords]
                fb=dest.shapes.build_freeform(*pts[0]);fb.add_line_segments(pts[1:],close=True)
                hole=fb.convert_to_shape();hole.fill.solid();hole.fill.fore_color.rgb=brand.white;hole.line.fill.background();hole.name=name+' interior'
    q=dest.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(.5),Inches(3.03),Inches(4.55),int(frame.height*scale))
    q.fill.solid();q.fill.fore_color.rgb=brand.white;q.line.fill.background();q.name='Reach map frame'
    countries=json.loads((root/'assets/maps/ne_50m_admin_0_countries.geojson').read_text(encoding='utf-8'))
    sa=next(f for f in countries['features'] if f['properties']['ADMIN']=='South Africa')
    proj=Transformer.from_crs('EPSG:4326',CRS.from_proj4('+proj=laea +lat_0=-29 +lon_0=25 +datum=WGS84 +units=m +no_defs'),always_xy=True)
    projected_sa=transform(proj.transform,shape(sa['geometry']).intersection(box(16,-35.3,33.8,-22)))
    sa_shape=next(q for q in source.shapes if q.name=='Natural Earth 1:50m boundary: South Africa')
    xmin,ymin,xmax,ymax=projected_sa.bounds
    fx=sa_shape.width/(xmax-xmin);fy=sa_shape.height/(ymax-ymin)
    def source_xy(x,y,z=None):return sa_shape.left+(x-xmin)*fx,sa_shape.top+(ymax-y)*fy
    # Regional market selection comes from the same declared reporting groups.
    with (root/'story/demand_map_regions_2026_10_06.csv').open(encoding='utf-8-sig') as f:
        selected_codes={r['province_code'] for r in csv.DictReader(f) if r['region'] in ('Eastern coastal','Inland')}
    provinces=json.loads((root/'assets/maps/geoboundaries_zaf_adm1_simplified.geojson').read_text(encoding='utf-8'))
    market=unary_union([transform(source_xy,transform(proj.transform,shape(f['geometry']))) for f in provinces['features'] if NAMES[f['properties']['shapeName']] in selected_codes])
    # Neutral national context; no sales heatmap or transport-cost legend.
    draw_polygon(freeform_polygon(sa_shape),brand.white,brand.grey_fill,.6,'South Africa context')
    draw_polygon(market,brand.grey_fill,None,name='Selected market outside illustrated road reach')
    connected=[]
    for q in source.shapes:
        if q.name.startswith('Illustrative delivered road transport cost class ') and 'class None;' not in q.name:
            connected.append(freeform_polygon(q))
    reach=unary_union(connected).intersection(market)
    draw_polygon(reach,brand.accent_secondary,None,name='Illustrated road connection within selected market')
    draw_polygon(market,None,brand.accent_secondary,1.25,'Selected eastern and inland market outline')
    # Only Vopak origins remain; production, port and lease symbols belong elsewhere.
    with (root/'story/storage_operator_inventory_2026_10_06.csv').open(encoding='utf-8-sig') as f:
        sites=[r for r in csv.DictReader(f) if r['site_id'] in ('V1','V2')]
    for r in sites:
        px,py=proj.transform(float(r['longitude']),float(r['latitude']));xx,yy=xy(*source_xy(px,py));x=xx/Inches(1);y=yy/Inches(1)
        q=dest.shapes.add_shape(MSO_SHAPE.DIAMOND,Inches(x-.045),Inches(y-.045),Inches(.09),Inches(.09));q.name='Reach origin '+r['site'];q.fill.solid();q.fill.fore_color.rgb=brand.accent_primary;q.line.color.rgb=brand.white;q.line.width=Pt(.5)
        text(dest,r['site'],x+.08,y-.05,.74,.23,9,True)
    # Minimal geographic orientation, adapted from the source map.
    from convergence_feedback import line
    line(dest,(.72,3.60),(.72,3.34),brand.ink,.7)
    line(dest,(.72,3.34),(.68,3.43),brand.ink,.7);line(dest,(.72,3.34),(.76,3.43),brand.ink,.7)
    text(dest,'N',.65,3.12,.22,.18,8)
    for x,label,col in [(.5,'Illustrated road reach',brand.accent_secondary),(2.58,'Outside illustrated reach',brand.grey_fill)]:
        q=dest.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(5.89),Inches(.12),Inches(.12));q.fill.solid();q.fill.fore_color.rgb=col;q.line.fill.background()
        text(dest,label,x+.18,5.84,2.0,.26,9)
    text(dest,'Outline = selected eastern + inland market',.5,6.13,4.55,.23,9)
    text(dest,'Spatial illustration only. The volume deduction is authored; it is not calculated from the shaded area.',.5,6.40,4.55,.35,8.5)
    dest.notes_slide.notes_text_frame.text+='\nREACH-MAP: source cells with a non-None cost class are collapsed into one illustrated road-connection layer and clipped to the selected Eastern coastal/Inland province union. No new cost cutoff or operating feasibility is inferred. Original 100 km schematic connection rule retained; original cost detail remains on the earlier transport page. Selected market outline uses declared reporting regions, not a verified terminal catchment. The 14.5/2.5/12.0 volume example is independent of the spatial classification; no area-to-litres or measured reach claim.'
