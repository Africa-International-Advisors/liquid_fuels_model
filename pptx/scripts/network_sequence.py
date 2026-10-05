"""Cumulative schematic geography for review; does not calculate route capacity."""
import json
import openpyxl
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from coverage_map import clipped
from road_routes import ROADS

PRODUCTION=[('ENREF / SAPREF',31.03,-29.88,5.12,4.85),('NATREF',27.85,-26.81,3.0,4.12),('Sasol CTL',29.17,-26.55,4.32,3.4),('Astron',18.52,-33.87,.65,6.0),('PetroSA',21.94,-34.15,2.2,6.3)]
PORTS=[('Port Nolloth*',16.87,-29.25,.55,4.42),('Saldanha',17.95,-33.03,.5,5.5),('Cape Town',18.43,-33.91,.62,6.02),('Mossel Bay',22.14,-34.18,2.2,6.27),('Gqeberha',25.63,-33.96,3.72,6.25),('Ngqura',25.69,-33.8,4.5,5.83),('East London',27.91,-33.03,5.03,5.6),('Durban',31.03,-29.88,5.15,4.77),('Richards Bay',32.06,-28.8,5.08,4.13)]
NODES={'Gauteng':(28.05,-26.2),'Durban':(31.03,-29.88),'Cape Town':(18.43,-33.91),'Saldanha':(17.95,-33.03),'Sishen':(23,-27.78),'De Aar':(24.01,-30.65),'Kimberley':(24.77,-28.73),'Bloemfontein':(26.21,-29.12),'Gqeberha':(25.63,-33.96),'Ngqura':(25.69,-33.8),'East London':(27.91,-33.03),'Richards Bay':(32.06,-28.8),'Ermelo':(29.98,-26.53)}
RAIL=[['Gauteng','Durban'],['Gauteng','Kimberley','De Aar','Cape Town'],['Gauteng','Bloemfontein','East London'],['Bloemfontein','De Aar','Gqeberha'],['De Aar','Ngqura'],['Sishen','Saldanha'],['Sishen','Kimberley','De Aar'],['Gauteng','Ermelo','Richards Bay']]
PRODUCT=[[(31.03,-29.88),(28.39,-26.44)],[(28.39,-26.44),(27.85,-26.81),(26.66,-26.85)],[(28.39,-26.44),(29.17,-26.55),(28.98,-26.08),(28.32,-25.71)],[(28.39,-26.44),(28.13,-26.32),(28.00,-26.20)]]
CRUDE=[[(31.03,-29.88),(28.7,-28.5),(27.85,-26.81)],[(17.95,-33.03),(18.52,-33.87)]]
GAS=[[(35.1,-21.7),(31.95,-25.43),(29.17,-26.55)],[(29.17,-26.55),(27.85,-26.81)],[(29.17,-26.55),(28.05,-26.2)],[(29.17,-26.55),(29.94,-27.75),(31.9,-28.75),(32.06,-28.8)],[(31.9,-28.75),(31,-29.95)]]

def draw_network_stage(slide,stage,root,brand,cfg,text,table):
    blue=brand.accent_primary;muted=cfg.DIVIDER_HEADER
    def xy(lon,lat):return .82+(lon-15)*.26,2.23+(-20-lat)*.26
    def line(a,b,color,width=1,dash=None):
        s=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(a[0]),Inches(a[1]),Inches(b[0]),Inches(b[1]));s.line.color.rgb=color;s.line.width=Pt(width)
        if dash:s.line.dash_style=dash
    def route(points,color,width,dash=None):
        for a,b in zip(points,points[1:]):line(xy(*a),xy(*b),color,width,dash)
    features=json.loads((root/'assets/maps/ne_110m_admin_0_countries.geojson').read_text(encoding='utf-8'))['features']
    for f in features:
        if f['properties']['ADMIN'] not in {'South Africa','Namibia','Botswana','Lesotho','eSwatini','Mozambique','Zimbabwe'}:continue
        g=f['geometry']
        for poly in g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]:
            pts=poly[0]
            for ax,b,gt in [(0,15,True),(0,36,False),(1,-35.5,True),(1,-20,False)]:
                if pts:pts=clipped(pts,ax,b,gt)
            if len(pts)<3:continue
            coords=[(int(Inches(x)),int(Inches(y))) for x,y in [xy(*p) for p in pts]]
            builder=slide.shapes.build_freeform(*coords[0]);builder.add_line_segments(coords[1:],close=True);s=builder.convert_to_shape()
            s.fill.solid();s.fill.fore_color.rgb=cfg.MAP_REGION_COLOURS['North Africa'] if f['properties']['ADMIN']=='South Africa' else brand.grey_fill;s.line.color.rgb=brand.white;s.line.width=Pt(.6)
    labels=['Production','Pipelines','Ports','Roads','Rail','Storage','Corridors']
    for i,label in enumerate(labels):
        text(slide,f'{i+1} {label}',.6+i*1.67,1.83,1.62,.3,10.5,i==stage,blue if i==stage else brand.ink)
    if stage>=1:
        c=blue if stage==1 else muted
        for points in PRODUCT:route(points,c,1.5 if stage==1 else .7)
        for points in CRUDE:route(points,brand.ink if stage==1 else muted,1.2 if stage==1 else .65,MSO_LINE_DASH_STYLE.DASH)
        for points in GAS:route(points,c,1.1 if stage==1 else .6,MSO_LINE_DASH_STYLE.ROUND_DOT)
    if stage>=3:
        for points in ROADS.values():route(points,blue if stage==3 else muted,1.3 if stage==3 else .65)
    if stage>=4:
        for names in RAIL:route([NODES[n] for n in names],blue if stage==4 else muted,1.6 if stage==4 else .8,MSO_LINE_DASH_STYLE.DASH_DOT)
    def marker(label,lon,lat,lx,ly,kind,color,show_label=True):
        x,y=xy(lon,lat);s=slide.shapes.add_shape(kind,Inches(x-.055),Inches(y-.055),Inches(.11),Inches(.11))
        s.fill.solid();s.fill.fore_color.rgb=color;s.line.color.rgb=brand.white;s.line.width=Pt(.5)
        if show_label:
            line((x,y),(lx+.35,ly+.1),muted,.5)
            width=max(.8,min(1.65,len(label)*.075))
            t=text(slide,label,lx,ly,width,.25,9,True)
            t.fill.solid();t.fill.fore_color.rgb=brand.white
    for label,lon,lat,lx,ly in PRODUCTION:marker(label,lon,lat,lx,ly,MSO_SHAPE.OVAL,blue if stage==0 else muted,stage==0)
    if stage>=2:
        for label,lon,lat,lx,ly in PORTS:marker(label,lon,lat,lx,ly,MSO_SHAPE.RECTANGLE,blue if stage==2 else muted,stage!=5)
    for label,lon,lat,lx,ly in [('Gauteng',28.05,-26.2,3.6,3.15),('Jameson Park',28.39,-26.44,3.18,3.65)]:
        if stage>=1:marker(label,lon,lat,lx,ly,MSO_SHAPE.DIAMOND,blue,stage in (1,3,4,6))
    if stage==1:
        for label,lon,lat,lx,ly in [('Temane',35.1,-21.7,5.0,2.5),('Komatipoort',31.95,-25.43,5.0,3.3),('Sasolburg',27.85,-26.81,2.75,4.12),('Secunda',29.17,-26.55,4.32,3.4),('Durban',31.03,-29.88,5.12,4.92),('Saldanha',17.95,-33.03,.55,5.53),('Astron',18.52,-33.87,.65,6.0)]:marker(label,lon,lat,lx,ly,MSO_SHAPE.OVAL,blue)
        text(slide,'ROMPCO',4.8,2.94,.85,.2,9,True)
        text(slide,'Lilly',5.1,4.35,.6,.2,9,True)
    if stage==3:
        for label,lon,lat in [('N1',25.2,-30),('N2',24,-34),('N3',29.6,-28.5),('N4',29.5,-25.4),('N7',18.2,-30.5),('N12',25.5,-28)]:
            x,y=xy(lon,lat);t=text(slide,label,x,y,.42,.2,9,True);t.fill.solid();t.fill.fore_color.rgb=brand.white
    if stage>=5:
        provinces=[('Western Cape',20,-33.2,.55,6.16),('Northern Cape',21,-29.8,.55,4.72),('Eastern Cape',26,-32.2,3.1,6.18),('Free State',26.5,-28.9,2.7,4.95),('North West',25,-26.7,1.7,3.72),('Gauteng',28.2,-26.2,3.5,3.35),('Limpopo',29.4,-23.7,4.3,2.8),('Mpumalanga',30,-26,4.92,3.5),('KwaZulu-Natal',30.3,-28.5,4.67,4.65)]
        for label,lon,lat,lx,ly in provinces:
            x0,y0=xy(lon,lat)
            s=slide.shapes.add_shape(MSO_SHAPE.DIAMOND,Inches(x0-.055),Inches(y0-.055),Inches(.11),Inches(.11))
            s.fill.background();s.line.color.rgb=brand.ink if stage==5 else muted;s.line.width=Pt(.8)
            if stage==5:
                line((x0,y0),(lx+.35,ly+.1),muted,.5)
                text(slide,label,lx,ly,1.8,.24,9)
        marker('Vopak Lesedi',28.39,-26.44,3.35,4.03,MSO_SHAPE.OVAL,blue,stage==5)
        marker('Vopak Durban',31.03,-29.88,4.75,5.25,MSO_SHAPE.OVAL,blue,stage==5)
    if stage==6:
        # Show the full national corridor families already introduced in the build-up.
        for pts in ROADS.values(): route(pts,blue,1.25)
        route([NODES['Saldanha'],(18.97,-32.59)],blue,1.25)
        for names in RAIL: route([NODES[n] for n in names],blue,1.0,MSO_LINE_DASH_STYLE.DASH_DOT)
        for pts in PRODUCT: route(pts,blue,1.8)
        for pts in CRUDE: route(pts,blue,1.3,MSO_LINE_DASH_STYLE.DASH)
        route([NODES['Durban'],(28.39,-26.44),NODES['Gauteng']],blue,2.7)
    line((6.9,2.25),(6.9,6.6),muted,.4)
    if stage==5:
        text(slide,'Add storage and handling to the network',7.1,2.3,5,.5,18,True)
        text(slide,'Workbook provincial capacity (2024), thousand m3',7.1,2.82,5,.3,11)
        wb=openpyxl.load_workbook(root.parent/'external/sources/Liquid Fuels Model - Supply Demand, 2025 - Reatile Copy.xlsx',data_only=True,read_only=True)
        sheet=wb['Deficit Calculations']
        rows=['| Province | Petrol | Diesel | Jet | D/P* |']
        for rn in range(2,11):
            rows.append('| '+str(sheet.cell(rn,38).value)+' | '+' | '.join(f'{float(sheet.cell(rn,c).value)/1000:.1f}' for c in [41,42,40,43])+' |')
        wb.close()
        shape=table(slide,rows,x=7.1,y=3.22,height=2.6,widths=[2.0,.75,.75,.65,.8],size=10.5)
        for row in shape.table.rows:
            for cell in row.cells:cell.margin_top=cell.margin_bottom=Inches(.01)
        text(slide,'*D/P is shared petrol/diesel capacity; allocate once. Gross tank capacity does not establish usable storage or handling throughput.',7.1,6.02,4.95,.55,10)
    elif stage==6:
        text(slide,'National corridor families to assess',7.1,2.3,4.95,.55,18,True)
        families=[
            ('Durban - Gauteng','N3, NMPP and rail; first corridor to test.'),
            ('Richards Bay - eastern hinterland','Ermelo / Mpumalanga and Gauteng connections.'),
            ('Cape Town / Saldanha - inland','N1, N7 and rail; Saldanha - Astron crude link.'),
            ('Mossel Bay - coast and inland','N2 / N12 connections; validate product service.'),
            ('Gqeberha / Ngqura - inland','N10 and rail towards Northern Cape / Free State.'),
            ('East London - Free State / Gauteng','N6 and rail connections; validate fuel service.'),
            ('Northern and border approaches','N1 north; N4 / N17 east-west; N7 / N14 / N18 west.'),
        ]
        for i,(head,body) in enumerate(families):
            y=3.02+i*.46
            text(slide,head,7.1,y,4.95,.24,12,True)
            text(slide,body,7.1,y+.24,4.95,.22,10)
        text(slide,'All eight commercial ports are represented. These are national screening families, not validated fuel flows or an exhaustive local-route inventory.',7.1,6.35,4.95,.42,10)
    elif stage==0:
        text(slide,'Establish the domestic supply points',7.1,2.3,5,.5,18,True)
        wb=openpyxl.load_workbook(root.parent/'external/sources/Liquid Fuels Model - Supply Demand, 2025 - Reatile Copy.xlsx',data_only=True,read_only=True);s=wb['Assumptions']
        rows=['| Asset | kbpd | Petrol | Diesel | Jet |']
        for col in range(13,19):rows.append(f'| {s.cell(93,col).value.upper()} | {s.cell(94,col).value:g} | {s.cell(95,col).value:.0%} | {s.cell(96,col).value:.0%} | {s.cell(97,col).value:.0%} |')
        table(slide,rows,x=7.1,y=3.0,height=2.6,widths=[1.7,.7,.85,.85,.85],size=12);wb.close()
        text(slide,'Workbook capacity and yield assumptions. Inclusion does not establish current operation; utilisation and availability determine model output.',7.1,5.83,4.95,.72,12)
    else:
        copy={
          1:('Connect supply points to inland markets',[('Liquid products','Durban–Jameson Park; Sasolburg and Secunda branches; inland depots.'),('Crude','Durban–NATREF and Saldanha–Astron supply links.'),('Gas dependencies','ROMPCO: Temane–Secunda. Sasolburg/Gauteng connections and Lilly to KwaZulu-Natal.'),('Capacity is a separate input','Connectivity does not prove availability, access rights or spare capacity.')]),
          2:('Add the coastal import entry points',[('Eight commercial ports','Saldanha, Cape Town, Mossel Bay, Gqeberha, Ngqura, East London, Durban and Richards Bay.'),('Port Nolloth shown separately','Non-commercial port; inclusion does not imply fuel import service.'),('Test handling capability','Berths, draft, product compatibility, receipt rates, storage connections and access.'),('Allocate imports explicitly','National import requirements are not yet assigned to ports.')]),
          3:('Extend connections by road',[('Coastal to inland','N3 connects Durban with Gauteng; N1 links Cape Town and inland markets.'),('Regional and border links','N2, N4, N7 and other selected national corridors extend market reach.'),('Translate roads into fuel capacity','Tanker fleet, cycles, permissions, loading slots and receiving capacity are required.'),('Earlier layers remain context','Production, pipes and ports are subdued; selected roads are highlighted.')]),
          4:('Add rail and test actual fuel service',[('Coastal–Gauteng routes','Durban, Cape Town and Eastern Cape connections.'),('Other major network families','Sishen–Saldanha; Northern Cape–Nelson Mandela Bay; eastern hinterland–Richards Bay.'),('Network presence is not fuel service','Confirm fuel wagons, slots, sidings, service reliability and terminal interfaces.'),('Avoid treating bulk routes as fuel routes','Iron ore and manganese corridors illustrate the network, not available fuel capacity.')]),
          6:('Select corridors for feasibility tests',[('First candidate: Durban–Gauteng','Link coastal receipts, inland transport, Jameson Park and customer delivery; agree asset pairing.'),('Other candidates to screen','Cape Town–inland and Richards Bay–eastern hinterland. Highlighted paths are candidates, not validated flows.'),('Include handling and storage','Receipt/dispatch rates, compatible tanks, working stock and commercial commitments.'),('Calculate a feasible corridor','Reconcile product volumes, shared capacity, access and constraints; separate unmet from unassessed demand.')]),
        }[stage]
        text(slide,copy[0],7.1,2.3,4.95,.55,18,True)
        for i,(head,body) in enumerate(copy[1]):
            y=3.05+i*.87;text(slide,head,7.1,y,4.95,.3,13,True);text(slide,body,7.1,y+.32,4.95,.53,11)
    # Graphic legends use the same symbols as the network.
    x=.65;y=6.79
    if stage==5:
        text(slide,'Vopak workbook, thousand m3: Durban 2024 P76 / D251.7; Lesedi 2026 P40 / D100.',.65,6.34,6.05,.23,8.5)
        text(slide,'Hollow diamonds: provincial coverage, not tank sites. Blue circles: identified Vopak terminals.',.65,6.61,6.05,.48,9)
        text(slide,'Other operator sites, usable capacity and handling rates remain to source.',7.1,6.8,4.95,.3,9)
        return
    if stage==0:
        s=slide.shapes.add_shape(MSO_SHAPE.OVAL,Inches(.65),Inches(6.83),Inches(.1),Inches(.1));s.fill.solid();s.fill.fore_color.rgb=blue;s.line.fill.background()
        text(slide,'Production assets | approximate site locations',.83,6.78,5.8,.25,10)
    elif stage==1:
        for xx,label,dash in [(.65,'Products',None),(2.3,'Crude',MSO_LINE_DASH_STYLE.DASH),(3.7,'Gas',MSO_LINE_DASH_STYLE.ROUND_DOT)]:
            line((xx,y+.1),(xx+.35,y+.1),blue,1.5,dash);text(slide,label,xx+.43,y-.02,1.2,.25,10)
    else:
        for xx,label,dash in [(.65,'Pipelines',None),(2.3,'Roads',None),(3.7,'Rail',MSO_LINE_DASH_STYLE.DASH_DOT)]:
            if (label=='Roads' and stage<3) or (label=='Rail' and stage<4):continue
            colour=blue if stage==6 or (label=='Roads' and stage==3) or (label=='Rail' and stage==4) else muted
            line((xx,y+.1),(xx+.35,y+.1),colour,1.4,dash);text(slide,label,xx+.43,y-.02,1.2,.25,10)
        if stage==2:text(slide,'Squares: ports; circles: production',2.3,y-.02,4,.25,10)
        if stage==6:
            line((5.1,y+.1),(5.45,y+.1),blue,2.7)
            text(slide,'First test',5.52,y-.02,1.25,.25,10)
    text(slide,'Same map extent on all seven pages. Connections are schematic; no route-capacity or fuel-service claim.',7.1,6.8,4.95,.3,9)
