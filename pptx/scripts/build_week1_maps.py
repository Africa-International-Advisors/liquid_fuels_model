"""Week 1 analytical pack; no fuel-model execution.

Geographical evidence stays editable in PowerPoint. LAEA projection uses pyproj;
transport geometry is the existing schematic appendix, not a routable GIS network.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import sys
import io
from copy import deepcopy
from datetime import date
from datetime import datetime
import shutil

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.dml.color import RGBColor
from pptx.opc.packuri import PackURI
from pyproj import CRS, Transformer
from shapely.geometry import shape as geo_shape, box as geo_box
from shapely.ops import transform as geo_transform
from brand_pptx import BrandStyle, add_themed_slide, remove_all_slides_cleanly
from brand_pptx import _strip_table_style, cell_bottom_rule
from network_sequence import PRODUCT, PRODUCTION, PORTS, RAIL, NODES
from road_routes import ROADS
from coverage_map import clipped
from accessibility_cartography import distance_surface
from storage_footprint import draw_storage_footprint, storage_notes, draw_transnet_leases
from competitive_market_page import add_competitive_page
from storage_capacity_page import add_storage_capacity_page
from provincial_sales_pages import add_trend_page,add_supply_page
from partner_story_page import add_partner_story_page
from exhibit_typography import standardise_reused_map_callouts

ROOT = Path(__file__).resolve().parents[1]
# Reuse validated cost-map pages when only reporting evidence/layout changes.
REUSE = Path(sys.argv[2]).resolve() if len(sys.argv)>2 and sys.argv[1]=='--reuse-deck' else None
sys.path.insert(0, str(ROOT))
from brand_configs import vopak as cfg

brand = BrandStyle.from_module(cfg)
BLUE = brand.accent_primary
INK = brand.ink
GREY = cfg.DIVIDER_HEADER
LIGHT = brand.grey_fill
LAND = RGBColor.from_string('F2F1ED')
SEA = RGBColor.from_string('F5F8FB')
DEMAND = RGBColor.from_string('546CA2')  # Vopak theme accent 2
CRS_MAP = CRS.from_proj4('+proj=laea +lat_0=-29 +lon_0=25 +datum=WGS84 +units=m +no_defs')
PROJECT = Transformer.from_crs('EPSG:4326', CRS_MAP, always_xy=True)
REGIONS = {
    'Eastern coastal': (30.0, -30.8),
    'Inland': (27.0, -25.0),
    'Western coastal': (20.1, -32.6),
    'Other regions': (23.7, -29.5),
}
OUT = ROOT / 'output/delivered'
OUT.mkdir(parents=True, exist_ok=True)
PATH = (Path(sys.argv[sys.argv.index('--output')+1]).resolve() if '--output' in sys.argv else OUT / 'Vopak_Week1_Analytical_Pack_2026_10_06.pptx')
if PATH.exists() and PATH.parent == OUT:
    archive=OUT/'archive'/datetime.now().strftime('%Y-%m-%d_%H%M%S')
    archive.mkdir(parents=True,exist_ok=True)
    for old in [PATH,PATH.with_suffix('.pdf')]:
        if old.exists():shutil.copy2(old,archive/old.name)

def text(s, value, x, y, w, h, size=14, bold=False, color=INK, align=None):
    q = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    f = q.text_frame
    f.word_wrap = True
    f.margin_left = f.margin_right = Inches(.025)
    f.margin_top = f.margin_bottom = 0
    for i, line in enumerate(value.split('\n')):
        p = f.paragraphs[0] if i == 0 else f.add_paragraph()
        p.text = line
        p.font.name = cfg.THEME_FONT
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = color
        p.space_after = Pt(3)
        if align is not None:
            p.alignment = align
    return q

def line(s, a, b, color=GREY, width=.6, dash=None):
    q = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,
        Inches(a[0]), Inches(a[1]), Inches(b[0]), Inches(b[1]))
    q.line.color.rgb = color
    q.line.width = Pt(width)
    if dash:
        q.line.dash_style = dash
    return q

def marker(s, x, y, radius=.05, color=BLUE, kind=MSO_SHAPE.OVAL, hollow=False):
    q = s.shapes.add_shape(kind, Inches(x-radius), Inches(y-radius), Inches(radius*2), Inches(radius*2))
    if hollow:
        q.fill.background()
    else:
        q.fill.solid()
        q.fill.fore_color.rgb = color
    q.line.color.rgb = color if hollow else brand.white
    q.line.width = Pt(1 if hollow else .5)
    return q

def table(s, rows, x, y, widths, height, size=14):
    q = s.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(sum(widths)), Inches(height))
    t = q.table
    _strip_table_style(t)
    for c, w in zip(t.columns, widths):
        c.width = Inches(w)
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = t.cell(r, c)
            cell.text = str(value)
            cell.margin_left = cell.margin_right = Inches(.10)
            cell.margin_top = cell.margin_bottom = Inches(.07)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = brand.white
            cell_bottom_rule(cell, color=cfg.DIVIDER_HEADER if r == 0 else cfg.DIVIDER_BODY, w_pt=.35)
            for p in cell.text_frame.paragraphs:
                p.font.name = cfg.THEME_FONT
                p.font.size = Pt(size)
                p.font.bold = r == 0 or r == len(rows)-1
                p.font.color.rgb = INK
                if c > 0 and str(value).replace('.', '').isdigit():
                    p.alignment = PP_ALIGN.RIGHT
    return q

def load(name):
    with (ROOT / 'story' / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

regional = load('illustrative_market_catchments.csv')
national = load('illustrative_national_balance.csv')
routes = load('illustrative_terminal_routes.csv')
groups = {}
fields = ['demand_bn_l', 'feasible_service_bn_l', 'commercial_envelope_bn_l',
          'current_unique_vopak_bn_l', 'additional_candidate_bn_l']
for row in regional:
    g = groups.setdefault(row['region'], {k: 0.0 for k in fields})
    for k in fields:
        if row[k]:
            g[k] += float(row[k])
        else:
            g[k] = None
for r in national:
    assert math.isclose(float(r['required_imports_bn_l']), float(r['demand_bn_l']) +
        float(r['exports_bn_l']) + float(r['stock_build_bn_l']) - float(r['domestic_supply_bn_l']))
assert math.isclose(sum(g['demand_bn_l'] for g in groups.values()), sum(float(r['demand_bn_l']) for r in national))
for name in ['Eastern coastal', 'Inland']:
    g = groups[name]
    assert g['current_unique_vopak_bn_l'] <= g['commercial_envelope_bn_l'] <= g['feasible_service_bn_l'] <= g['demand_bn_l']
    assert math.isclose(g['additional_candidate_bn_l'], g['commercial_envelope_bn_l']-g['current_unique_vopak_bn_l'])

features = json.loads((ROOT/'assets/maps/ne_50m_admin_0_countries.geojson').read_text(encoding='utf-8'))['features']
access_settings=json.loads((ROOT/'story/illustrative_accessibility_settings.json').read_text())
sa_geometry=geo_transform(PROJECT.transform,geo_shape(next(f['geometry'] for f in features if f['properties'].get('ADMIN')=='South Africa')).intersection(geo_box(16,-35.3,33.8,-22)))
surface=[] if REUSE else distance_surface(ROADS,PROJECT,sa_geometry,access_settings)
SURFACE_COLOURS=[RGBColor.from_string(c) for c in ['0A2373','375798','728BBB','A9BDDC','DDE6F2']]
polys = []
for feature in features:
    name = feature['properties'].get('ADMIN')
    if name not in {'South Africa', 'Namibia', 'Botswana', 'Lesotho', 'eSwatini', 'Swaziland', 'Mozambique', 'Zimbabwe'}:
        continue
    geom = feature['geometry']
    for poly in geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]:
        pts = poly[0]
        for ax,b,gt in [(0,16,True),(0,33.8,False),(1,-35.3,True),(1,-22,False)]:
            if pts:
                pts = clipped(pts,ax,b,gt)
        if len(pts) > 2:
            polys.append((name, [PROJECT.transform(p[0],p[1]) for p in pts]))
box = [PROJECT.transform(lon,lat) for lon in [16+i*.2 for i in range(90)] for lat in [-35.3,-22]]
box += [PROJECT.transform(lon,lat) for lon in [16,33.8] for lat in [-35.3+i*.2 for i in range(68)]]
XMIN, XMAX = min(p[0] for p in box), max(p[0] for p in box)
YMIN, YMAX = min(p[1] for p in box), max(p[1] for p in box)

class Map:
    def __init__(self, s, x, y, w, h, draw_base=True):
        self.s,self.x,self.y,self.w,self.h = s,x,y,w,h
        self.factor = min((w-.2)/(XMAX-XMIN), (h-.2)/(YMAX-YMIN))
        self.ox = x+(w-(XMAX-XMIN)*self.factor)/2
        self.oy = y+(h-(YMAX-YMIN)*self.factor)/2
        if not draw_base: return
        bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        bg.name = 'Map frame; common geographic extent'
        bg.fill.solid(); bg.fill.fore_color.rgb = SEA
        bg.line.color.rgb = LIGHT; bg.line.width = Pt(.5)
        for name, pts in polys:
            points = [(int(Inches(a)),int(Inches(b))) for a,b in [self.projected(*p) for p in pts]]
            fb = s.shapes.build_freeform(*points[0]); fb.add_line_segments(points[1:],close=True)
            q = fb.convert_to_shape(); q.name = 'Natural Earth 1:50m boundary: '+name
            q.fill.solid(); q.fill.fore_color.rgb = LAND if name=='South Africa' else LIGHT
            q.line.color.rgb = brand.white; q.line.width = Pt(.5)
        # Geographic reference grid; labels avoid implying a survey coordinate accuracy.
        for lon in [20,25,30]:
            self.route([(lon,lat) for lat in [-35+i*.25 for i in range(53)]], LIGHT,.3,MSO_LINE_DASH_STYLE.ROUND_DOT)
        for lat in [-25,-30,-35]:
            self.route([(lon,lat) for lon in [16+i*.25 for i in range(72)]], LIGHT,.3,MSO_LINE_DASH_STYLE.ROUND_DOT)
        # N follows the local projected meridian, not an assumed screen-up arrow.
        a = self.xy(17,-24); b = self.xy(17,-23.4)
        line(s,a,b,INK,1); text(s,'N',b[0]-.08,b[1]-.23,.2,.2,9,True)
        line(s,b,(b[0]-.04,b[1]+.09),INK,1); line(s,b,(b[0]+.04,b[1]+.09),INK,1)
        width = 500000*self.factor
        xx,yy=x+.2,y+h-.22
        line(s,(xx,yy),(xx+width,yy),INK,1.7)
        for dist in [0,250000,500000]:
            dx=dist*self.factor
            line(s,(xx+dx,yy-.035),(xx+dx,yy+.035),INK,.7)
        text(s,'0',xx-.02,yy-.23,.18,.18,8)
        text(s,'500 km',xx+width-.16,yy-.23,.55,.18,8)
    def projected(self,x,y):
        return self.ox+(x-XMIN)*self.factor,self.oy+(YMAX-y)*self.factor
    def xy(self,lon,lat):
        return self.projected(*PROJECT.transform(lon,lat))
    def route(self,coords,color=GREY,width=.65,dash=None):
        pts = [self.xy(*p) for p in coords]
        for a,b in zip(pts,pts[1:]):
            if all(self.x<=p[0]<=self.x+self.w and self.y<=p[1]<=self.y+self.h for p in (a,b)):
                line(self.s,a,b,color,width,dash)
    def pin(self,name,lon,lat,kind,color=GREY,dx=.1,dy=-.12,label=True):
        x,y=self.xy(lon,lat); marker(self.s,x,y,.045,color,kind)
        if label:
            q=text(self.s,name,x+dx,y+dy,1.15,.25,9,color=color)
            q.fill.solid(); q.fill.fore_color.rgb=brand.white
    def context(self,labels=False,storage_labels=True):
        for points in ROADS.values(): self.route(points,GREY,.65)
        for points in PRODUCT: self.route(points,brand.accent_secondary if hasattr(brand,'accent_secondary') else DEMAND,1.15)
        for names in RAIL: self.route([NODES[n] for n in names],GREY,.55,MSO_LINE_DASH_STYLE.DASH_DOT)
        for name,lon,lat,*_ in PRODUCTION:
            dx,dy={'NATREF':(-1.02,.12),'Sasol CTL':(.12,-.48),'Astron':(-.9,-.26)}.get(name,(-.9,-.26))
            self.pin(name,lon,lat,MSO_SHAPE.OVAL,INK,label=labels and name in {'Astron','NATREF','Sasol CTL'},dx=dx,dy=dy)
        for name,lon,lat,*_ in PORTS:
            if name!='Port Nolloth*': self.pin(name,lon,lat,MSO_SHAPE.RECTANGLE,GREY,label=labels and name in ({'Cape Town','Richards Bay','Gqeberha'} if storage_labels else {'Gqeberha'}),dx=.1,dy=.05)
        for name,lon,lat in [('Durban',31.03,-29.88),('Lesedi*',28.39,-26.44)]:
            self.pin(name,lon,lat,MSO_SHAPE.DIAMOND,BLUE,dx=.13,dy=-.16,label=storage_labels)
    def demand(self):
        for name,(lon,lat) in REGIONS.items():
            total = groups[name]['demand_bn_l']; x,y=self.xy(lon,lat)
            radius=.08*math.sqrt(total)
            marker(self.s,x,y,radius,DEMAND,hollow=True)
            if name=='Eastern coastal': dx,dy=-.85,.17
            elif name=='Inland': dx,dy=-1.2,-.52
            elif name=='Western coastal': dx,dy=-.4,-.65
            else: dx,dy=-1.75,-.58
            label={'Eastern coastal':'Eastern / coastal','Western coastal':'Western / coastal','Other regions':'Other regions','Inland':'Inland'}[name]
            q=text(self.s,f'{label}\n{total:.1f} bn L',x+dx,y+dy,1.55,.48,11,True,DEMAND)
            q.fill.solid(); q.fill.fore_color.rgb=brand.white
    def surface(self):
        for geometry,category,origin in surface:
            color=LIGHT if category is None else SURFACE_COLOURS[category]
            polygons=list(geometry.geoms) if geometry.geom_type=='MultiPolygon' else [geometry]
            for polygon in polygons:
                if polygon.geom_type!='Polygon' or polygon.area<1000000:
                    continue
                coords=[(int(Inches(x)),int(Inches(y))) for x,y in [self.projected(*p) for p in polygon.exterior.coords]]
                fb=self.s.shapes.build_freeform(*coords[0]);fb.add_line_segments(coords[1:],close=True)
                q=fb.convert_to_shape();q.name=f'Illustrative delivered road transport cost class {category}; reference terminal {origin}'
                q.fill.solid();q.fill.fore_color.rgb=color;q.line.fill.background()
    def access(self,terminal,road_color=BLUE):
        if terminal=='Durban':
            self.route(list(reversed(ROADS['N3'])),road_color,2.3)
            self.route(PRODUCT[0],DEMAND,1.7,MSO_LINE_DASH_STYLE.DASH)
            coast=[p for p in ROADS['N2'] if p[0]>=28.7]
            self.route(coast,road_color,2.3)
            self.route([NODES['Durban'],NODES['Gauteng']],INK,1.1,MSO_LINE_DASH_STYLE.DASH_DOT)
            lon,lat=31.03,-29.88
        else:
            self.route(PRODUCT[0],DEMAND,1.7,MSO_LINE_DASH_STYLE.DASH)
            self.route([ (28.39,-26.44),(28.05,-26.2),(28.19,-25.75)],road_color,2.3)
            self.route(ROADS['N4'],road_color,2.0)
            self.route([p for p in ROADS['N1'] if p[1]>-28],INK,1.1,MSO_LINE_DASH_STYLE.DASH_DOT)
            lon,lat=28.39,-26.44
        x,y=self.xy(lon,lat); marker(self.s,x,y,.09,BLUE,MSO_SHAPE.DIAMOND)

prs = Presentation(REUSE or ROOT/cfg.SOURCE_TEMPLATE)
if REUSE:
    assert len(prs.slides) in (5,6,7,9,10,16), 'Reuse requires a prior Week 1 pack'
    # Remove only the infrastructure/evidence pages; preserve expensive cost exhibits.
    positions={5:[1],6:[1,4],7:[1,4,5],9:[1,2,3,6,7],10:[1,2,3,6,7,8],16:[i for i in range(16) if i not in (0,8,10,15)]}[len(prs.slides)]
    for i in reversed(positions):
        sid=prs.slides._sldIdLst[i]
        prs.part.drop_rel(sid.rId)
        prs.slides._sldIdLst.remove(sid)
    # python-pptx names new slide parts by slide count. Compact retained names
    # before appending, otherwise the old closing slide6 collides with new slide6.
    for i,retained in enumerate(prs.slides,1):
        retained.part.partname=PackURI(f'/ppt/slides/slide{i}.xml')
else:
    remove_all_slides_cleanly(prs)
for master in prs.slide_masters:
    for q in master.shapes:
        if q.has_text_frame and ('Click to edit' in q.text or q.name=='Text Placeholder 6'):
            q.text_frame.clear()

reference = Presentation(ROOT/'output/delivered/Vopak_Analyst_Kickoff.pptx')

def bookend(source, closing=False):
    """Reuse the delivered kickoff cover/closing composition and its original photos."""
    s=add_themed_slide(prs,'1_Title',brand=brand)
    for q in list(s.shapes):
        if q.is_placeholder:
            q._element.getparent().remove(q._element)
    for q in source.shapes:
        if q.shape_type==13:
            dest=s.shapes.add_picture(io.BytesIO(q.image.blob),q.left,q.top,q.width,q.height)
            dest.crop_left,dest.crop_right=q.crop_left,q.crop_right
            dest.crop_top,dest.crop_bottom=q.crop_top,q.crop_bottom
            dest.name=q.name
        else:
            element=deepcopy(q._element)
            # The reference's photo credit link must be re-related to this new slide.
            for node in element.iter():
                for key,value in list(node.attrib.items()):
                    if key.startswith('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'):
                        rel=source.part.rels[value]
                        if rel.is_external:
                            node.set(key,s.part.rels.get_or_add_ext_rel(rel.reltype,rel.target_ref))
            s.shapes._spTree.insert_element_before(element,'p:extLst')
    replacements={
        'Analyst kickoff':'Week 1 analytical pack',
        'Coverage: SACU + priority African regions':'South Africa | Petrol and diesel',
        '2 October 2026':'6 October 2026',
        'Discussion':'Confirm demand, routes and access',
    }
    for q in s.shapes:
        if q.has_text_frame:
            for p in q.text_frame.paragraphs:
                for r in p.runs:
                    if r.text in replacements:
                        r.text=replacements[r.text]
    s.notes_slide.notes_text_frame.text=source.notes_slide.notes_text_frame.text+'\nWeek 1 analytical pack, 6 October 2026. Existing kickoff cover/closing reused at user request.'
    return s

if not REUSE: bookend(reference.slides[0])

def section_chevrons(s,active=1):
    labels=['1  About','2  Analytical specifications','3  Model build','4  Delivery approach']
    for i,label in enumerate(labels):
        q=s.shapes.add_shape(MSO_SHAPE.CHEVRON,Inches(.5+i*2.93),Inches(.08),Inches(2.86),Inches(.42))
        q.name=f'Section navigation {i+1}'
        q.adjustments[0]=.12
        q.fill.solid();q.fill.fore_color.rgb=BLUE if i==active else LIGHT
        q.line.fill.background()
        f=q.text_frame;f.clear();f.word_wrap=False
        f.margin_left=f.margin_right=Inches(.18)
        f.margin_top=f.margin_bottom=0
        f.vertical_anchor=MSO_ANCHOR.MIDDLE
        p=f.paragraphs[0];p.text=label;p.alignment=PP_ALIGN.CENTER
        p.font.name=cfg.THEME_FONT;p.font.size=Pt(13);p.font.bold=i==active
        p.font.color.rgb=brand.white if i==active else BLUE

def slide(title,source,notes):
    s=add_themed_slide(prs,'Header only',brand=brand,title=title)
    s.shapes.turbo_add_enabled=True
    section_chevrons(s)
    text(s,'Source: '+source,.5,7.16,10.6,.23,7.6)
    s.notes_slide.notes_text_frame.text=notes
    return s

method = ('Map uses WGS84 / Lambert azimuthal equal-area, centred 25°E, 29°S. '
    'Natural Earth 1:50m countries; schematic transport from the kickoff appendix. '
    'Scale is nominal at map centre. Facility points are approximate, inherited from '
    'the appendix, not surveyed GPS. Lesedi uses the inherited Jameson Park-area point. '
    'No operational service-area polygon or evidence-calibrated cost/time threshold is computed. '
    'Demand positions are regional annotations, not provincial centroids. '
    'All numerical volumes are illustrative and are not model outputs or actual Vopak flows. '
    'The graduated surface is illustrative delivered road transport cost: R0.15/litre dispatch plus '
    'R0.002/litre/km times shortest schematic-road distance and straight-line terminal/grid connections. '
    'These are authored example parameters, not carrier quotes or validated cost evidence. '
    '25 km cells; cost classes <=0.75, 0.75-1.25, 1.25-1.75, 1.75-2.25 and >2.25 R/litre. '
    'Cells more than 100 km from the sampled road geometry or without a connected path remain unassessed. '
    'Fuel purchase price, tax, storage and pipeline tariffs are excluded. Operational speeds, '
    'capacity, permissions and commercial access are not evaluated. '
    'Natural Earth source: https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_50m_admin_0_countries.geojson')

def exhibit_layout(s, heading, takeaways):
    """Reference structure: analytical exhibit left, numbered interpretation right."""
    text(s,heading,.5,1.78,7.05,.34,15,True)
    line(s,(.5,2.13),(7.55,2.13),INK,.65)
    line(s,(7.88,1.99),(7.88,6.86),INK,.55)
    text(s,'Key takeaways',8.12,1.78,4.03,.34,18,True)
    line(s,(8.12,2.13),(12.15,2.13),INK,.65)
    for i,(heading,body) in enumerate(takeaways):
        y=2.39+i*1.10
        text(s,f'{i+1:02d} · {heading}',8.12,y,4.05,.41,14,True,BLUE)
        text(s,body,8.12,y+.43,4.05,.64,12.5)

from provincial_demand_map import add_page as add_demand_page
add_demand_page(slide,exhibit_layout,Map,text,marker,line,ROOT,PROJECT,brand)
add_trend_page(slide,exhibit_layout,text,line,ROOT,brand)
add_supply_page(slide,exhibit_layout,text,ROOT,brand)

if not REUSE:
    s=slide('Map conditional market access from Durban and Lesedi',
        'Existing appendix routes; illustrative candidate connections, not verified catchments. Natural Earth 1:50m.',method)
    exhibit_layout(s,'Road-delivery accessibility | illustrative transport cost, R/litre',[
     ('Durban: coastal and inland links','Road candidates connect coastal customers and inland transfers. Pipelines are separate supply connections.'),
     ('Lesedi: inland dispatch','Test receipt, dispatch, tanker cycles and customer destinations for connected inland markets.'),
     ('Lower cost means higher accessibility','Darker cells show lower example road-delivery cost from either facility. Pipe and rail lines remain context.'),
     ('Customer access is unverified','Contracts and competitors define the commercial envelope. Actual customer catchments are not supplied.'),
    ])
    m=Map(s,.5,2.38,7.05,4.0);m.surface();m.context();m.access('Durban');m.access('Lesedi',DEMAND)
    for i,(name,color) in enumerate(zip(['≤0.75','0.75–1.25','1.25–1.75','1.75–2.25','>2.25'],SURFACE_COLOURS)):
        x=.55+i*1.02
        marker(s,x+.06,6.58,.055,color,MSO_SHAPE.RECTANGLE);text(s,name,x+.2,6.47,1.05,.22,8.5)
    marker(s,5.8,6.58,.055,LIGHT,MSO_SHAPE.RECTANGLE);text(s,'Unassessed',5.94,6.47,.8,.22,8)
    text(s,'R/litre',6.84,6.47,.7,.22,8)
    text(s,'Example rate: R0.15/L dispatch + R0.002/L/km. Grey = unassessed.',.5,6.73,7.05,.21,10)
    text(s,'Illustrative road cost only. Pipeline/rail access and commercial rights are not priced.',.5,6.99,7.15,.14,7.5)

    s=slide('Separate demand, accessible volume and Vopak flows',
        'Illustrative CSVs and road transport rates; no actual Vopak throughput or quoted transport costs supplied.',method)
    exhibit_layout(s,'Cost accessibility and market volumes | illustrative',[
     ('National balance sets import needs','Demand of 21.0 less domestic production of 7.0 gives required imports of 14.0 in this illustration.'),
     ('Count unique customer demand once','Receipts of 2.8 at Durban and 2.0 at Lesedi include a shared 1.8 transfer. Unique demand served is 3.0.'),
     ('Candidate opportunity is conditional','The example commercial envelope is 8.5; current unique demand served is 3.0, leaving a candidate 5.5.'),
     ('Replace examples with evidence','Match regional demand, route constraints, customer flows and contracts by product, period and units.'),
    ])
    m=Map(s,.5,2.38,7.05,4.0);m.surface();m.context()
    for value,x,y in [
     ('Inland market | illustrative\nDemand 10.0 | envelope 6.0\nCurrent 2.0 | candidate 4.0',.8,2.72),
     ('Eastern/coastal | illustrative\nDemand 4.5 | envelope 2.5\nCurrent 1.0 | candidate 1.5',4.75,5.52),
    ]:
        q=text(s,value,x,y,2.7,.73,11,True,BLUE);q.fill.solid();q.fill.fore_color.rgb=brand.white
    byroute={r:sum(float(q['volume_bn_l']) for q in routes if q['route_id']==r) for r in ['R1','R2','R3','R4']}
    durban=byroute['R1']+byroute['R2'];lesedi=byroute['R2']+byroute['R3']; unique=byroute['R1']+byroute['R4']
    assert math.isclose(durban+lesedi-byroute['R2'],unique)
    for i,(name,color) in enumerate(zip(['≤0.75','0.75–1.25','1.25–1.75','1.75–2.25','>2.25'],SURFACE_COLOURS)):
        x=.55+i*1.02
        marker(s,x+.06,6.58,.055,color,MSO_SHAPE.RECTANGLE);text(s,name,x+.2,6.47,1.05,.22,8.5)
    marker(s,5.8,6.58,.055,LIGHT,MSO_SHAPE.RECTANGLE);text(s,'Unassessed',5.94,6.47,.8,.22,8)
    text(s,'R/litre',6.84,6.47,.7,.22,8)
    text(s,f"Receipts {durban:.1f} + {lesedi:.1f} − transfer {byroute['R2']:.1f} = unique demand {unique:.1f}",.5,6.72,7.05,.23,12,True,BLUE)
    text(s,'Example rates: R0.15/L + R0.002/L/km. Grey = unassessed. Volumes: bn L/year.',.5,6.99,7.1,.14,7.5)

add_competitive_page(slide,exhibit_layout,Map,text,table,ROOT,brand,regional)
add_storage_capacity_page(slide,exhibit_layout,text,ROOT,brand)
add_partner_story_page(slide,exhibit_layout,text,ROOT,brand)
if not REUSE:
    bookend(reference.slides[-1],closing=True)
else:
    ids=list(prs.slides._sldIdLst)
    for sid in ids: prs.slides._sldIdLst.remove(sid)
    for i in [0,4,5,6,1,2,7,8,9,3]: prs.slides._sldIdLst.append(ids[i])
# Refresh context on retained cost maps without recomputing their illustrative surfaces.
for s in [prs.slides[4],prs.slides[5]]:
    standardise_reused_map_callouts(s)
    for q in list(s.shapes):
        if q.name.startswith('Transnet lease overlay:'):
            q._element.getparent().remove(q._element)
    m=Map(s,.5,2.38,7.05,4.0,draw_base=False)
    draw_transnet_leases(m,text,line,marker,ROOT,brand,box=(.65,4.13))
    lease_note='\nTransnet lease offers are context only, not cost-model origins or available supply.\n'
    s.notes_slide.notes_text_frame.text=s.notes_slide.notes_text_frame.text.split(lease_note)[0]+lease_note+storage_notes(ROOT)
from scr_structure import structure_scr
structure_scr(prs,slide,text,ROOT,brand)
assert len(prs.slides)==16
for index,s in enumerate(prs.slides,1):
    for q in s.shapes:
        assert q.left>=0 and q.top>=0 and q.left+q.width<=prs.slide_width+10 and q.top+q.height<=prs.slide_height+10,(index,q.name)
prs.core_properties.title='South Africa liquid fuels: Week 1 analytical maps'
prs.core_properties.author=cfg.AUTHOR
prs.core_properties.subject='Illustrative demand geography and conditional Vopak market access'
prs.save(PATH)
qa=ROOT/'qa/week1_maps';qa.mkdir(parents=True,exist_ok=True)
(qa/'build_manifest.json').write_text(json.dumps({
 'output':str(PATH),'slides':len(prs.slides),'template':str(cfg.SOURCE_TEMPLATE),
 'template_sha256':hashlib.sha256((ROOT/cfg.SOURCE_TEMPLATE).read_bytes()).hexdigest(),
 'projection':CRS_MAP.to_proj4(),'volumes':'Illustrative only',
 'boundary_source':'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson',
 'boundary_sha256':hashlib.sha256((ROOT/'assets/maps/ne_50m_admin_0_countries.geojson').read_bytes()).hexdigest(),
 'transport':'Inherited schematic appendix; no service-area calculation',
 'template_aware':True,'reused_cost_pages_from':str(REUSE) if REUSE else None,
 'province_boundary_sha256':hashlib.sha256((ROOT/'assets/maps/geoboundaries_zaf_adm1_simplified.geojson').read_bytes()).hexdigest(),
 'provincial_sales_sha256':hashlib.sha256((ROOT.parent/'assumptions/2026/timeseries/fuel_sales_department_by_province_quarterly.csv').read_bytes()).hexdigest(),
 'demand_layer':'2022 reported provincial petrol/diesel sales; separate from illustrative market scenarios'},indent=2),encoding='utf-8')
print(PATH)
