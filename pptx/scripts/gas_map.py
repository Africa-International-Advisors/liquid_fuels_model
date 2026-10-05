"""Source-backed gas connectivity, drawn as editable schematic geography."""
import json
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from coverage_map import clipped


def draw_gas_map(slide, root, brand, cfg, text):
    def xy(lon,lat): return .75+(lon-25)*.45,2.12+(-20-lat)*.38
    def line(a,b,color,width=2,dash=None):
        s=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(a[0]),Inches(a[1]),Inches(b[0]),Inches(b[1]))
        s.line.color.rgb=color;s.line.width=Pt(width)
        if dash:s.line.dash_style=dash
    for f in json.loads((root/'assets/maps/ne_110m_admin_0_countries.geojson').read_text(encoding='utf-8'))['features']:
        if f['properties']['ADMIN'] not in {'South Africa','Mozambique','Zimbabwe','Botswana','Lesotho','eSwatini'}:continue
        g=f['geometry']
        for poly in g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]:
            pts=poly[0]
            for ax,b,gt in [(0,25,True),(0,36,False),(1,-31,True),(1,-20,False)]:
                if pts:pts=clipped(pts,ax,b,gt)
            if len(pts)<3:continue
            coords=[(int(Inches(x)),int(Inches(y))) for x,y in [xy(*p) for p in pts]]
            b=slide.shapes.build_freeform(*coords[0]);b.add_line_segments(coords[1:],close=True);s=b.convert_to_shape()
            s.fill.solid();s.fill.fore_color.rgb=cfg.MAP_REGION_COLOURS['North Africa'] if f['properties']['ADMIN']=='South Africa' else brand.grey_fill
            s.line.color.rgb=brand.white;s.line.width=Pt(.6)
    nodes={'Temane':(35.1,-21.7),'Komatipoort':(31.95,-25.43),'Secunda':(29.17,-26.55),'Sasolburg':(27.85,-26.81),'Gauteng':(28.05,-26.2),'Newcastle':(29.93,-27.75),'Empangeni':(31.9,-28.75),'Richards Bay':(32.06,-28.8),'Durban':(31.03,-29.88)}
    styles=[(brand.accent_primary,None),(brand.ink,MSO_LINE_DASH_STYLE.DASH),(cfg.MAP_REGION_COLOURS['SADC excluding SACU'],MSO_LINE_DASH_STYLE.LONG_DASH)]
    for route,style in [(['Temane','Komatipoort','Secunda'],0),(['Secunda','Sasolburg'],1),(['Secunda','Gauteng'],1),(['Secunda','Newcastle','Empangeni','Durban'],2),(['Empangeni','Richards Bay'],2)]:
        color,dash=styles[style]
        for a,b in zip(route,route[1:]):line(xy(*nodes[a]),xy(*nodes[b]),color,2.4,dash)
    labels={'Temane':(4.47,2.39,'Temane CPF\nPande / Temane gas'),'Komatipoort':(4.15,3.69,'Komatipoort'),'Secunda':(3.53,4.33,'Secunda'),'Sasolburg':(.66,5.02,'Sasolburg'),'Gauteng':(.68,4.02,'Inland Gauteng\nindustrial network'),'Newcastle':(2.6,5.25,'Newcastle'),'Empangeni':(4.48,5.35,'Empangeni'),'Richards Bay':(4.63,5.82,'Richards Bay'),'Durban':(3.6,6.21,'Durban South')}
    for name,(lx,ly,label) in labels.items():
        x,y=xy(*nodes[name]);line((x,y),(lx+.3,ly+.15),cfg.DIVIDER_HEADER,.6)
        s=slide.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x-.045),Inches(y-.045),Inches(.09),Inches(.09));s.fill.solid();s.fill.fore_color.rgb=brand.ink;s.line.fill.background()
        text(slide,label,lx,ly,1.8,.6 if '\n' in label else .28,10,True)
    text(slide,'MOZAMBIQUE',3.1,2.58,1.8,.3,10)
    text(slide,'SOUTH AFRICA',.9,5.92,1.8,.3,10)
    text(slide,'Gas infrastructure context | connections shown schematically',.55,1.77,11.5,.35,16)
    line((6.7,2.2),(6.7,6.7),cfg.DIVIDER_FRAME,.35)
    blocks=[('01  ROMPCO: Mozambique - Secunda','Natural gas from the Pande / Temane fields via Temane processing and Komatipoort to Secunda.'),('02  Sasolburg + inland Gauteng','Sasol gas connections link Secunda with Sasolburg and the Gauteng industrial network.'),('03  Lilly: Secunda - KwaZulu-Natal','Methane-rich gas via Newcastle and Empangeni, serving Richards Bay and the Durban corridor.')]
    for i,(head,copy) in enumerate(blocks):
        y=2.28+i*1.23;color,dash=styles[i];line((7.02,y+.13),(7.47,y+.13),color,2.4,dash)
        text(slide,head,7.6,y-.02,4.45,.5,16,True)
        text(slide,copy,7.05,y+.51,5.0,.64,14)
    text(slide,'Model implication',7.05,5.98,4.8,.3,15,True)
    text(slide,'Gas availability can affect production assumptions. These links are not petrol, diesel or jet transport capacity.',7.05,6.32,4.9,.48,11)
    text(slide,'Schematic connectivity, not surveyed routing. Gas capacity and access are not yet integrated into the liquid-fuels engine.',.55,6.83,11.5,.2,10)
