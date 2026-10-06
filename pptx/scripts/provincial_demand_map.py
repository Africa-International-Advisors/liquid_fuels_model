"""Report existing provincial sales with explicit spatial aggregation and coverage."""
import csv
import hashlib
import json
from collections import defaultdict
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from shapely.geometry import shape,box
from shapely.ops import transform,unary_union
from pptx.enum.shapes import MSO_SHAPE
from storage_footprint import draw_storage_footprint,storage_notes

NAMES={'Eastern Cape':'EC','Free State':'FS','Gauteng':'GP','KwaZulu-Natal':'KZN',
       'Limpopo':'LP','Mpumalanga':'MP','North West':'NW','Nothern Cape':'NC','Northern Cape':'NC','Western Cape':'WC'}
LABELS={'EC':(26.4,-32.5),'FS':(26.5,-28.6),'GP':(26.6,-24.7),'KZN':(30.1,-28.6),
        'LP':(29.2,-23.85),'MP':(30.25,-25.9),'NW':(25.9,-26.45),'NC':(21.55,-29.8),'WC':(20.6,-33.0)}
COLOURS=['E3EBF6','BACCE4','809CC7','3D619D','0A2373']
CLASSES=[1,2,4,6]

def add_page(slide,exhibit_layout,Map,text,marker,line,root,project,brand):
    observed,_,_=sales(root)
    top_share=sum(observed[p] for p in ('GP','KZN','WC'))/sum(observed.values())
    s=slide('Locate fuel demand alongside the infrastructure serving it',
        'DMPR 2022 sales; geoBoundaries/OCHA/MDB 2020 provinces (CC BY 3.0 IGO); operator sources on slide 7.',
        'Observed historical sales, separate from the illustrative market figures on slides 6-7.')
    exhibit_layout(s,'Petrol + diesel sales by province | 2022, bn litres/year',[
        ('Demand concentrates in three provinces',f"Gauteng {observed['GP']:.2f}, KwaZulu-Natal {observed['KZN']:.2f} and Western Cape {observed['WC']:.2f} bn litres represent {top_share:.1%} of reported sales."),
        ('Regions have explicit boundaries','Eastern coast = EC + KZN; inland = GP, FS, LP, MP and NW; western coast = WC; other = NC. These are working groupings.'),
        ('Storage sits alongside demand','Vopak, Bidvest, Sasol, Transnet and Burgan Cape provide the mapped storage context. Inland facilities are clustered.'),
        ('Sales do not establish accessible volume','All four quarters of 2022 reconcile to national sales. Current demand, delivered cost and customer rights need separate evidence.'),
    ])
    m=Map(s,.5,2.38,7.05,4.0)
    values,totals,notes=draw(m,text,root,project,brand)
    m.context(labels=False,storage_labels=False)
    draw_storage_footprint(m,text,line,marker,root,brand,inland_position=(.65,3.18))
    province_labels(m,text,values,brand)
    s.notes_slide.notes_text_frame.text += '\n'+storage_notes(root)+'\n'+notes
    for i,(label,colour) in enumerate(zip(['<1','1-2','2-4','4-6','6+'],COLOURS)):
        x=.55+i*.94
        marker(s,x+.06,6.55,.055,RGBColor.from_string(colour),MSO_SHAPE.RECTANGLE)
        text(s,label,x+.20,6.45,.62,.20,8.5)
    text(s,'bn L/year; darker = more sales',5.22,6.45,2.31,.20,8)
    for x,label,kind in [(.55,'Production',MSO_SHAPE.OVAL),(1.83,'Port',MSO_SHAPE.RECTANGLE),(2.60,'Vopak',MSO_SHAPE.DIAMOND),(3.5,'Other storage',MSO_SHAPE.HEXAGON)]:
        marker(s,x+.05,6.82,.045,brand.accent_primary if kind in (MSO_SHAPE.DIAMOND,MSO_SHAPE.HEXAGON) else brand.ink,kind,hollow=kind==MSO_SHAPE.HEXAGON)
        text(s,label,x+.15,6.72,1.23,.20,8)
    text(s,'Lines: road / pipe / rail; heavy outlines: working regions',4.91,6.72,2.66,.26,7.5)
    text(s,'Province totals, not within-province hotspots. Sites approximate; access unverified. Jet excluded.',.5,6.99,7.1,.14,7.5)
    return s

def sales(root):
    path=root.parent/'assumptions/2026/timeseries/fuel_sales_department_by_province_quarterly.csv'
    rows=list(csv.DictReader(path.open(encoding='utf-8-sig',newline='')))
    periods=defaultdict(set); totals=defaultdict(float); seen=set(); sources=set()
    for r in rows:
        if not r['period'].startswith('2022-') or r['product'] not in ('petrol','diesel'):continue
        key=(r['province'],r['product'],r['period'])
        assert key not in seen,'Duplicate provincial sales key'
        seen.add(key); assert r['unit']=='litres'
        periods[(r['province'],r['product'])].add(r['period'])
        totals[r['province']]+=float(r['value'])
        sources.add(r['source_file'])
    assert len(periods)==18 and all(q=={'2022-Q1','2022-Q2','2022-Q3','2022-Q4'} for q in periods.values())
    national=root.parent/'assumptions/2026/timeseries/fuel_sales_department.csv'
    n=sum(float(r['value']) for r in csv.DictReader(national.open(encoding='utf-8-sig'))
          if r['period']=='2022' and r['product'] in ('petrol','diesel'))
    assert abs(sum(totals.values())-n)<1,'Provincial/national sales reconciliation failed'
    return {k:v/1e9 for k,v in totals.items()},path,sources

def draw(m,text,root,project,brand):
    values,path,sources=sales(root)
    regions={r['province_code']:r['region'] for r in csv.DictReader((root/'story/demand_map_regions_2026_10_06.csv').open())}
    data=json.loads((root/'assets/maps/geoboundaries_zaf_adm1_simplified.geojson').read_text())
    geometries={}
    for f in data['features']:
        code=NAMES[f['properties']['shapeName']]
        geometries[code]=transform(project.transform,shape(f['geometry']).intersection(box(16,-35.3,33.8,-22))).simplify(1500,preserve_topology=True)
        colour=RGBColor.from_string(COLOURS[sum(values[code]>=limit for limit in CLASSES)])
        _polygon(m,geometries[code],colour,brand.white,.65,'2022 provincial petrol/diesel sales: '+code)
    # Regional envelopes are province unions, not proximity circles or commercial catchments.
    for region in sorted(set(regions.values())):
        geom=unary_union([g for p,g in geometries.items() if regions[p]==region])
        _polygon(m,geom,None,brand.accent_primary,1.5,'Working geographic region: '+region)
    # Mask the landlocked neighbouring country; provincial polygon interiors
    # must never imply that Lesotho's demand is included in South Africa.
    countries=json.loads((root/'assets/maps/ne_50m_admin_0_countries.geojson').read_text(encoding='utf-8'))
    for f in countries['features']:
        if f['properties'].get('ADMIN')=='Lesotho':
            _polygon(m,transform(project.transform,shape(f['geometry'])),brand.grey_fill,brand.white,.6,'Lesotho: outside South African demand')
    totals={r:sum(values[p] for p in regions if regions[p]==r) for r in set(regions.values())}
    notes=('Historical sales are a demand-location proxy, not 2026 demand or customer delivery destinations. '
           'All 18 province/product series have four quarters in 2022; provincial sum matches national sales within 1 litre. '
           'No district-level smoothing or within-province hotspot is inferred. Colour measures total annual provincial volume, '
           'not litres per km2. Region borders use the authored province membership, not a service area. '
           'Eastern coastal=EC+KZN; Inland=GP+FS+LP+MP+NW; Western coastal=WC; Other=NC. '
           'The observed totals and regions are separate from the illustrative market/share figures on slides 6-7. '
           f'Source CSV {path}; SHA256 {hashlib.sha256(path.read_bytes()).hexdigest()}; original workbook(s) {sorted(sources)}. '
           'Department index: https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/media_SAVolumes.html. '
           'Boundary metadata/source/license: assets/maps/geoboundaries_zaf_adm1_metadata.json. '
           'Reporting evidence remains provisional pending analyst review; owner Manish, Nigel review. '
           'Refresh when the source supplies a later complete year; check every province/product quarter and reconcile national totals.')
    return values,totals,notes

def province_labels(m,text,values,brand):
    # Gauteng is small and crowded with storage; displace its label with a leader.
    m.route([(27.9,-26.0),LABELS['GP']],brand.accent_primary,.6)
    for code,(lon,lat) in LABELS.items():
        x,y=m.xy(lon,lat)
        q=text(m.s,f'{code}\n{values[code]:.2f}',x-.30,y-.17,.60,.36,9,True,brand.accent_primary)
        q.fill.solid();q.fill.fore_color.rgb=brand.white

def _polygon(m,geom,fill,stroke,width,name):
    parts=list(geom.geoms) if geom.geom_type=='MultiPolygon' else [geom]
    for p in parts:
        if p.geom_type!='Polygon' or p.area<1e6:continue
        points=[(int(Inches(x)),int(Inches(y))) for x,y in [m.projected(*q) for q in p.exterior.coords]]
        fb=m.s.shapes.build_freeform(*points[0]);fb.add_line_segments(points[1:],close=True)
        q=fb.convert_to_shape();q.name=name
        if fill is None:q.fill.background()
        else:q.fill.solid();q.fill.fore_color.rgb=fill
        q.line.color.rgb=stroke;q.line.width=Pt(width)
