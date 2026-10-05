"""Editable South African port and schematic corridor inventory."""
import json
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from coverage_map import clipped
from road_routes import draw_roads


def draw_logistics_map(slide, root, brand, cfg, text, roads_only=False):
    def xy(lon, lat): return .7+(lon-15)*.29, 2.12+(-22-lat)*.29
    def line(a,b,color,width=1,dash=False):
        s=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(a[0]), Inches(a[1]), Inches(b[0]), Inches(b[1]))
        s.line.color.rgb=color; s.line.width=Pt(width)
        if dash: s.line.dash_style=MSO_LINE_DASH_STYLE.DASH
    for f in json.loads((root/'assets/maps/ne_110m_admin_0_countries.geojson').read_text(encoding='utf-8'))['features']:
        if f['properties']['ADMIN'] not in {'South Africa','Namibia','Botswana','Lesotho','eSwatini','Mozambique','Zimbabwe'}: continue
        g=f['geometry']
        for poly in g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]:
            pts=poly[0]
            for ax,b,gt in [(0,15,True),(0,34,False),(1,-35.5,True),(1,-22,False)]:
                if pts: pts=clipped(pts,ax,b,gt)
            if len(pts)<3: continue
            coords=[(int(Inches(x)),int(Inches(y))) for x,y in [xy(*p) for p in pts]]
            builder=slide.shapes.build_freeform(*coords[0]); builder.add_line_segments(coords[1:],close=True)
            s=builder.convert_to_shape();s.fill.solid()
            s.fill.fore_color.rgb=cfg.MAP_REGION_COLOURS['North Africa'] if f['properties']['ADMIN']=='South Africa' else brand.grey_fill
            s.line.color.rgb=brand.white;s.line.width=Pt(.6)
    nodes={'Gauteng':(28.05,-26.2),'Durban':(31.03,-29.88),'Cape Town':(18.43,-33.91),'Saldanha':(17.95,-33.03),'Sishen':(23,-27.78),'De Aar':(24.01,-30.65),'Kimberley':(24.77,-28.73),'Bloemfontein':(26.21,-29.12),'Gqeberha':(25.63,-33.96),'Ngqura':(25.69,-33.80),'East London':(27.91,-33.03),'Richards Bay':(32.06,-28.8),'Ermelo':(29.98,-26.53)}
    draw_roads(xy,line,cfg.MAP_REGION_COLOURS['SADC excluding SACU'],1.5 if roads_only else .7)
    routes=[['Gauteng','Durban'],['Gauteng','Kimberley','De Aar','Cape Town'],['Gauteng','Bloemfontein','East London'],['Bloemfontein','De Aar','Gqeberha'],['De Aar','Ngqura'],['Sishen','Saldanha'],['Sishen','Kimberley','De Aar'],['Gauteng','Ermelo','Richards Bay']]
    for route in ([] if roads_only else routes):
        for a,b in zip(route,route[1:]):line(xy(*nodes[a]),xy(*nodes[b]),brand.accent_primary,1.5)
    # Selected product and crude pipelines; offset geometry is illustrative only.
    for a,b in [((31.03,-29.88),(28.39,-26.44)),((28.39,-26.44),(29.17,-26.55)),((28.39,-26.44),(27.85,-26.81)),((31.03,-29.88),(27.85,-26.81)),((17.95,-33.03),(18.52,-33.87))]:
        if not roads_only: line(xy(*a),xy(*b),brand.ink,1.1,True)
    if not roads_only:
        for label,lon,lat,lx,ly in [('NATREF',27.85,-26.81,3.38,3.54),('Sasol CTL',29.17,-26.55,4.5,3.38),('Astron',18.52,-33.87,1.65,5.75),('PetroSA',21.94,-34.15,2.8,6.16),('ENREF / SAPREF',31.03,-29.88,4.45,4.95)]:
            x,y=xy(lon,lat)
            s=slide.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x-.055),Inches(y-.055),Inches(.11),Inches(.11))
            s.fill.solid();s.fill.fore_color.rgb=brand.white;s.line.color.rgb=brand.accent_primary;s.line.width=Pt(1.5)
            line((x,y),(lx+.35,ly+.12),cfg.DIVIDER_HEADER,.5)
            text(slide,label,lx,ly,1.65,.23,8,True)
    ports=[('1 Port Nolloth*',16.87,-29.25,.52,3.62),('2 Saldanha',17.95,-33.03,.5,5.1),('3 Cape Town',18.43,-33.91,.6,6.1),('4 Mossel Bay',22.14,-34.18,2.15,6.35),('5 Gqeberha',25.63,-33.96,3.9,6.06),('6 Ngqura',25.69,-33.8,4.82,5.69),('7 East London',27.91,-33.03,5.08,5.28),('8 Durban',31.03,-29.88,5.35,4.65),('9 Richards Bay',32.06,-28.8,5.12,3.68)]
    for label,lon,lat,lx,ly in ports:
        x,y=xy(lon,lat);line((x,y),(lx+.5,ly+.12),cfg.DIVIDER_HEADER,.6)
        s=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x-.045),Inches(y-.045),Inches(.09),Inches(.09));s.fill.solid();s.fill.fore_color.rgb=brand.ink;s.line.fill.background()
        text(slide,label,lx,ly,1.65,.27,10,True)
    for name,lx,ly in [('Gauteng',3.46,2.67),('Sishen',1.85,3.48),('Ermelo',4.65,2.98)]:
        x,y=xy(*nodes[name]);s=slide.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x-.04),Inches(y-.04),Inches(.08),Inches(.08));s.fill.solid();s.fill.fore_color.rgb=brand.accent_primary;s.line.fill.background()
        line((x,y),(lx+.45,ly+.2),cfg.DIVIDER_HEADER,.5);text(slide,name,lx,ly,1.3,.27,10)
    text(slide,'Road layer: national corridors and coastal ports' if roads_only else 'Production + liquid pipelines + ports + roads + rail | schematic infrastructure layers',.55,1.77,11.5,.35,15)
    line((7.05,2.2),(7.05,6.65),cfg.DIVIDER_FRAME,.35)
    text(slide,'Road links for the infrastructure model' if roads_only else 'Major rail corridor families',7.32,2.22,4.65,.4,19,True)
    items=[('Gauteng - coastal ports','Durban, Cape Town and Eastern Cape ports'),('Northern Cape - Saldanha','Iron-ore corridor from Sishen'),('Northern Cape - Nelson Mandela Bay','Manganese corridor to Gqeberha / Ngqura'),('Mpumalanga / northern hinterland - Richards Bay','Bulk-freight corridor via the eastern network')]
    if roads_only:
        items=[('N1 / N3 / N4: inland and cross-border','Cape Town - Gauteng - Zimbabwe; Durban - Gauteng; Botswana - Gauteng - Mozambique'),('N2 / N6 / N7: coastal and regional','Southern/eastern coast; East London - Bloemfontein; Cape Town - Namibia'),('N10 / N12 / N14 / N18: inland links','Northern Cape, Gauteng and Botswana connections'),('N17: eastern industrial corridor','Gauteng - Mpumalanga - Eswatini border')]
        for label,lon,lat in [('N1',25.3,-30.2),('N2',24,-34),('N3',29.1,-28),('N4',28.7,-25.35),('N6',26.4,-31.2),('N7',18.1,-31.5),('N10',21.9,-29.8),('N12',25.6,-27.7),('N14',21.5,-28),('N17',30.2,-26.1),('N18',24.7,-25.9)]:
            x,y=xy(lon,lat); t=text(slide,label,x,y,.4,.22,9,True);t.fill.solid();t.fill.fore_color.rgb=brand.white
    for i,(h,b) in enumerate(items):
        y=2.83+i*.76;text(slide,h,7.32,y,4.75,.4,13,True);text(slide,b,7.32,y+.33,4.7,.47,11)
    text(slide,'Eight commercial ports + Port Nolloth*',7.32,5.93,4.7,.3,13,True)
    text(slide,'*Port Nolloth is non-commercial. Major corridors shown; route presence does not establish tanker access or fuel capacity.',7.32,6.32,4.7,.55,11)
    line((.65,6.83),(1.0,6.83),cfg.MAP_REGION_COLOURS['SADC excluding SACU'],1.3);text(slide,'National roads',1.08,6.7,1.3,.25,10)
    if not roads_only:
        line((2.6,6.83),(2.95,6.83),brand.accent_primary,1.5);text(slide,'Rail',3.03,6.7,.6,.25,10)
        line((3.8,6.83),(4.15,6.83),brand.ink,1.1,True);text(slide,'Pipeline trunks',4.23,6.7,1.6,.25,10)
        s=slide.shapes.add_shape(MSO_SHAPE.OVAL,Inches(5.8),Inches(6.76),Inches(.12),Inches(.12));s.fill.solid();s.fill.fore_color.rgb=brand.white;s.line.color.rgb=brand.accent_primary;s.line.width=Pt(1.5)
        text(slide,'Production',6.0,6.7,1.15,.25,9)
    else:
        text(slide,'Selected national corridors; schematic, not navigation geometry.',2.6,6.7,4.25,.3,9)
