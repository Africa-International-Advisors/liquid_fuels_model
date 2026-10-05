"""South African infrastructure geography and original workbook capacity evidence."""
import json
import openpyxl
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from coverage_map import clipped


def draw_asset_page(slide,index,root,brand,cfg,text,table):
    wb=openpyxl.load_workbook(root.parent/'external/sources/Liquid Fuels Model - Supply Demand, 2025 - Reatile Copy.xlsx',data_only=True,read_only=True)
    def xy(lon,lat): return .75+(lon-15)*.275,2.22+(-22-lat)*.275
    def line(a,b,color=None,dashed=False,width=.7):
        s=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(a[0]),Inches(a[1]),Inches(b[0]),Inches(b[1]))
        s.line.color.rgb=color or cfg.DIVIDER_HEADER; s.line.width=Pt(width)
        if dashed:s.line.dash_style=MSO_LINE_DASH_STYLE.DASH
        return s
    features=json.loads((root/'assets/maps/ne_110m_admin_0_countries.geojson').read_text(encoding='utf-8'))['features']
    for f in features:
        if f['properties']['ADMIN'] not in {'South Africa','Namibia','Botswana','Lesotho','eSwatini','Mozambique','Zimbabwe'}:continue
        g=f['geometry']; polygons=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
        for polygon in polygons:
            pts=polygon[0]
            for ax,b,gt in [(0,15,True),(0,34,False),(1,-35.5,True),(1,-22,False)]:
                if pts:pts=clipped(pts,ax,b,gt)
            if len(pts)<3:continue
            coords=[(int(Inches(x)),int(Inches(y))) for x,y in [xy(*p) for p in pts]]
            builder=slide.shapes.build_freeform(*coords[0]);builder.add_line_segments(coords[1:],close=True)
            s=builder.convert_to_shape();s.name='Asset map: '+f['properties']['ADMIN']
            s.fill.solid();s.fill.fore_color.rgb=cfg.MAP_REGION_COLOURS['North Africa'] if f['properties']['ADMIN']=='South Africa' else brand.grey_fill
            s.line.color.rgb=brand.white;s.line.width=Pt(.6)
    def pin(label,lon,lat,lx,ly,number=None):
        x,y=xy(lon,lat);line((x,y),(lx+.4,ly+.12))
        s=slide.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x-.07),Inches(y-.07),Inches(.14),Inches(.14))
        s.fill.solid();s.fill.fore_color.rgb=brand.accent_primary;s.line.color.rgb=brand.white;s.line.width=Pt(.6)
        text(slide,label,lx,ly,2.4,.3*len(label.split('\n')),11,True)
    if index==23:
        text(slide,'Six assets represented in Excel / Python; selected pipelines shown schematically',.55,1.77,11.5,.35,15)
        durban=(31.03,-29.88);natref=(27.85,-26.81);secunda=(29.17,-26.55);jmp=(28.39,-26.44)
        for a,b in [(durban,jmp),(secunda,jmp),(natref,jmp)]:line(xy(*a),xy(*b),brand.accent_primary,False,1.5)
        line(xy(*durban),xy(28.7,-28.5),brand.ink,True,1.0)
        line(xy(28.7,-28.5),xy(*natref),brand.ink,True,1.0)
        line(xy(17.95,-33.03),xy(18.52,-33.87),brand.ink,True,1.0)
        pin('1-2 Durban\nENREF / SAPREF',*durban,5.0,4.64)
        pin('3 NATREF\nSasolburg',*natref,2.7,3.4)
        pin('4 SASOL\nSecunda (CTL)',*secunda,4.9,2.8)
        pin('5 ASTRON\nCape Town',18.52,-33.87,.55,5.7)
        pin('6 PETROSA\nMossel Bay (GTL)',21.94,-34.15,2.4,5.94)
        x,y=xy(*jmp)
        s=slide.shapes.add_shape(MSO_SHAPE.DIAMOND,Inches(x-.05),Inches(y-.05),Inches(.1),Inches(.1));s.fill.solid();s.fill.fore_color.rgb=brand.ink;s.line.fill.background()
        line((x,y),(3.5,2.84));text(slide,'Jameson Park\nproduct hub',2.9,2.37,1.85,.55,10)
        text(slide,'Saldanha',.55,5.02,1.25,.25,10)
        line(xy(17.95,-33.03),(1.3,5.25))
        text(slide,'Workbook capacity and product-yield assumptions',6.85,2.16,5.4,.55,17,True)
        rows=['| Asset | kbpd | Petrol | Diesel | Jet |']
        s=wb['Assumptions']
        for num,col in enumerate(range(13,19),1):
            rows.append(f'| {num} {s.cell(93,col).value.upper()} | {s.cell(94,col).value:g} | {s.cell(95,col).value:.0%} | {s.cell(96,col).value:.0%} | {s.cell(97,col).value:.0%} |')
        table(slide,rows,x=6.85,y=2.93,height=2.35,widths=[1.65,.75,1,1,.9],size=12)
        text(slide,'kbpd = thousand barrels/day. Percentages are model product yields, not terminal handling limits. Workbook capacities do not establish current operating status.',6.85,5.48,5.3,.87,13)
        line((.6,6.55),(1.0,6.55),brand.accent_primary,False,1.5);text(slide,'Refined products',1.1,6.45,1.8,.3,10)
        line((3.0,6.55),(3.4,6.55),brand.ink,True,1);text(slide,'Crude oil',3.5,6.45,1.5,.3,10)
        text(slide,'Selected connections only; route geometry is schematic. Pipeline capacities are not represented in the Python engine.',.55,6.82,11.5,.2,10)
    else:
        text(slide,'Provincial storage coverage across operators | site-level locations still need to be assembled',.55,1.77,11.5,.35,14)
        # Hollow diamonds locate provincial coverage, never individual tanks.
        provinces=[('Western Cape',20,-33.2,.55,5.7),('Northern Cape',21,-29.8,.55,4.35),('Eastern Cape',26,-32.2,3.2,5.57),('Free State',26.5,-28.9,2.9,4.35),('North West',25,-26.7,1.68,3.29),('Gauteng',28.2,-26.2,3.35,2.9),('Limpopo',29.4,-23.7,4.28,2.38),('Mpumalanga',30,-26,4.75,3.12),('KwaZulu-Natal',30.3,-28.5,4.65,4.12)]
        for label,lon,lat,lx,ly in provinces:
            x,y=xy(lon,lat);s=slide.shapes.add_shape(MSO_SHAPE.DIAMOND,Inches(x-.055),Inches(y-.055),Inches(.11),Inches(.11));s.fill.background();s.line.color.rgb=brand.ink;s.line.width=Pt(1)
            line((x,y),(lx+.45,ly+.1));text(slide,label,lx,ly,1.85,.24,9)
        pin('Vopak Lesedi',28.39,-26.44,4.1,3.6)
        pin('Vopak Durban',31.03,-29.88,4.6,4.76)
        text(slide,'Vopak entries, thousand m3: Durban 2024 P 76 / D 251.7; Lesedi 2026 P 40 / D 100.',.65,5.82,5.8,.28,9)
        text(slide,'Hollow diamonds = provincial coverage, not tank locations.\nBlue circles = Vopak terminal locations identified in the workbook.',.65,6.12,5.8,.56,11)
        text(slide,'Other operators are included in provincial totals; their individual sites, products and usable capacity remain to locate and validate.',.65,6.72,5.8,.32,9)
        text(slide,'Provincial storage recorded in Excel (2024)',6.85,2.16,5.4,.4,17,True)
        text(slide,'Thousand m3 | P = petrol; D = diesel; J = jet',6.85,2.67,5.4,.3,11)
        rows=['| Province | P | D | J | D/P* |']
        s=wb['Deficit Calculations']
        short={'KwaZulu-Natal':'KwaZulu-Natal','Gauteng':'Gauteng','Western Cape':'Western Cape','Eastern Cape':'Eastern Cape','Mpumalanga':'Mpumalanga','Free State':'Free State','North West':'North West','Limpopo':'Limpopo','Northern Cape':'Northern Cape'}
        for rn in range(2,11):
            rows.append('| '+short[s.cell(rn,38).value]+' | '+' | '.join(f'{float(s.cell(rn,c).value)/1000:.1f}' for c in [41,42,40,43])+' |')
        table(slide,rows,x=6.85,y=3.05,height=3.15,widths=[2.15,.8,.8,.8,.75],size=11)
        text(slide,'*D/P: shared diesel/petrol storage; not allocated twice. Provincial entries do not identify individual operators or tank sites. Vopak market share needs matched dates and shared-capacity allocation.',6.85,6.4,5.3,.6,10)
    wb.close()
