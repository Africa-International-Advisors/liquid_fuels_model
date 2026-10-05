"""Editable country map from Natural Earth, with sourced evidence locations."""
import json
from pathlib import Path

from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.text import PP_ALIGN


def clipped(points, axis, bound, greater):
    result = []
    for a, b in zip(points[-1:] + points[:-1], points):
        ina = a[axis] >= bound if greater else a[axis] <= bound
        inb = b[axis] >= bound if greater else b[axis] <= bound
        if ina != inb:
            t = (bound-a[axis])/(b[axis]-a[axis])
            result.append([a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])])
        if inb:
            result.append(b)
    return result


def draw_coverage_map(slide, root, brand, cfg, text):
    features = json.loads((root/'assets/maps/ne_110m_admin_0_countries.geojson').read_text(encoding='utf-8'))['features']
    sacu={'South Africa','Namibia','Botswana','Lesotho','eSwatini'}
    other_sadc={'Angola','Democratic Republic of the Congo','Madagascar','Malawi',
                'Mozambique','United Republic of Tanzania','Zambia','Zimbabwe',
                'Comoros','Mauritius','Seychelles'}

    def group(properties):
        name=properties['ADMIN']
        if name in sacu: return 'SACU'
        if name in other_sadc: return 'SADC excluding SACU'
        return {'Eastern Africa':'East Africa','Western Africa':'West Africa',
                'Northern Africa':'North Africa','Middle Africa':'Central Africa'}.get(properties['SUBREGION'])

    def line(a, b):
        s = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(a[0]), Inches(a[1]), Inches(b[0]), Inches(b[1]))
        s.line.color.rgb = cfg.DIVIDER_HEADER
        s.line.width = Pt(.65)
        return s

    def overview(lon, lat):
        return .95+(lon+18)*.062, 2.15+(38-lat)*.058

    def inset(lon, lat):
        return 7.0+(lon-14)*.205, 3.65+(-22-lat)*.205

    def countries(transform, bounds, prefix):
        west,east,south,north = bounds
        for feature in features:
            if feature['properties']['CONTINENT'] != 'Africa':
                continue
            name = feature['properties']['ADMIN']
            g = feature['geometry']
            polygons = g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
            for polygon in polygons:
                points=polygon[0]
                for axis,bound,greater in [(0,west,True),(0,east,False),(1,south,True),(1,north,False)]:
                    if points: points=clipped(points,axis,bound,greater)
                if len(points)<3: continue
                coords=[(int(Inches(x)),int(Inches(y))) for x,y in [transform(*p) for p in points]]
                builder=slide.shapes.build_freeform(*coords[0])
                builder.add_line_segments(coords[1:],close=True)
                s=builder.convert_to_shape(); s.name=prefix+name
                s.fill.solid()
                s.fill.fore_color.rgb=cfg.MAP_REGION_COLOURS.get(group(feature['properties']),brand.grey_fill)
                s.line.color.rgb=brand.ink if name=='South Africa' else brand.white
                s.line.width=Pt(1.1 if name=='South Africa' else .65)

    text(slide,'Africa: agreed regional scope',.6,1.82,5.8,.35,18,True)
    countries(overview,(-26,58,-36,39),'Africa overview: ')
    # Small island members absent at 110m scale: schematic point symbols.
    for name,lon,lat,region in [('Comoros',43.3,-11.7,'SADC excluding SACU'),
                               ('Mauritius',57.5,-20.2,'SADC excluding SACU'),
                               ('Seychelles',55.45,-4.6,'SADC excluding SACU'),
                               ('Cabo Verde',-23.6,15.1,'West Africa')]:
        x,y=overview(lon,lat)
        marker=slide.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x-.03),Inches(y-.03),Inches(.06),Inches(.06))
        marker.name='Island location: '+name
        marker.fill.solid(); marker.fill.fore_color.rgb=cfg.MAP_REGION_COLOURS[region]
        marker.line.fill.background()
    # An outline locates the enlarged South African area on the continental map.
    a=overview(14,-22); b=overview(34,-35.5)
    box=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(a[0]),Inches(a[1]),Inches(b[0]-a[0]),Inches(b[1]-a[1]))
    box.fill.background(); box.line.color.rgb=cfg.DIVIDER_HEADER; box.line.width=Pt(.75)
    line((b[0],a[1]),(6.65,3.45)); line((b[0],b[1]),(6.65,6.55))
    # Full continent labels establish the scope without claiming model coverage.
    for label,lon,lat in [('NORTH AFRICA',12,25),('WEST AFRICA',-3,9),('EAST AFRICA',37,6),('SADC excluding SACU',22,-12),('CENTRAL AFRICA',14,1),('SACU',22,-26)]:
        x,y=overview(lon,lat)
        shown='SADC\nexcluding SACU' if label=='SADC excluding SACU' else label
        if label=='SADC excluding SACU':
            line((2.32,5.27),overview(22,-12))
            x,y=1.4,5.0
        q=text(slide,shown,x-.85,y,1.8,.55,9,True,brand.white if label=='SACU' else brand.ink)
        for p in q.text_frame.paragraphs:
            p.space_after=Pt(0)
            p.alignment=PP_ALIGN.CENTER

    text(slide,'South Africa: current model coverage',6.65,1.82,5.5,.4,20,True)
    text(slide,'South African results appear on pp. 38–40 and 47–51. National demand and six production assets are covered; port allocations remain to build.',6.65,2.32,5.5,.95,16)
    frame=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(6.65),Inches(3.45),Inches(5.5),Inches(3.1))
    frame.fill.solid(); frame.fill.fore_color.rgb=brand.white
    frame.line.color.rgb=cfg.DIVIDER_HEADER; frame.line.width=Pt(.65)
    countries(inset,(14,34,-35.5,-22),'South Africa detail: ')
    for label,lon,lat in [('NAMIBIA',17,-26),('BOTSWANA',24,-23),('SOUTH AFRICA',23.8,-29)]:
        x,y=inset(lon,lat)
        q=text(slide,label,x-.65,y,1.5,.25,9,True,brand.white)
        q.text_frame.paragraphs[0].alignment=PP_ALIGN.CENTER
    ports=[('Walvis Bay',14.5,-22.95,7.1,3.48),
           ('Durban',31.03,-29.87,11.05,5.55),
           ('Cape Town',18.43,-33.91,7.0,6.27),
           ('Saldanha Bay',17.95,-33.03,6.78,5.52)]
    for name,lon,lat,lx,ly in ports:
        x,y=inset(lon,lat)
        line((x,y),(lx+.5,ly+.12))
        s=slide.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x-.065),Inches(y-.065),Inches(.13),Inches(.13))
        s.fill.solid(); s.fill.fore_color.rgb=brand.white
        s.line.color.rgb=brand.ink; s.line.width=Pt(1)
        text(slide,name,lx,ly,1.5,.25,11,True)
    # Scope colours and data readiness are deliberately separate.
    items=[('SACU',.6,6.58),('SADC excluding SACU',2.0,6.58),
           ('East Africa',4.45,6.58),('West Africa',.6,6.86),('North Africa',2.0,6.86),('Central Africa',4.45,6.86)]
    for label,x,y in items:
        swatch=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(.14),Inches(.14))
        swatch.fill.solid(); swatch.fill.fore_color.rgb=cfg.MAP_REGION_COLOURS[label]; swatch.line.fill.background()
        text(slide,label,x+.2,y-.025,2.2,.2,9)
    text(slide,'Colours = scope, not data readiness. SADC takes precedence over East/Central subregions; grey = other markets.',6.65,6.66,5.5,.37,10)
