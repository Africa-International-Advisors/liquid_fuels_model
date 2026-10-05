"""Approved three-page analytical illustration; no model execution or routing engine.

Geographical evidence stays editable in PowerPoint. LAEA projection uses pyproj;
transport geometry is the existing schematic appendix, not a routable GIS network.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import sys
from datetime import date

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.dml.color import RGBColor
from pyproj import CRS, Transformer
from brand_pptx import BrandStyle, add_themed_slide, remove_all_slides_cleanly
from brand_pptx import _strip_table_style, cell_bottom_rule
from network_sequence import PRODUCT, PRODUCTION, PORTS, RAIL, NODES
from road_routes import ROADS
from coverage_map import clipped

ROOT = Path(__file__).resolve().parents[1]
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
PATH = OUT / 'Vopak_Week1_Analytical_Maps_2026_10_06.pptx'
if PATH.exists():
    n = 2
    while PATH.with_stem(PATH.stem + f'_v{n}').exists():
        n += 1
    PATH = PATH.with_stem(PATH.stem + f'_v{n}')

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
    def __init__(self, s, x, y, w, h):
        self.s,self.x,self.y,self.w,self.h = s,x,y,w,h
        self.factor = min((w-.2)/(XMAX-XMIN), (h-.2)/(YMAX-YMIN))
        self.ox = x+(w-(XMAX-XMIN)*self.factor)/2
        self.oy = y+(h-(YMAX-YMIN)*self.factor)/2
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
    def context(self,labels=False):
        for points in ROADS.values(): self.route(points,GREY,.65)
        for points in PRODUCT: self.route(points,brand.accent_secondary if hasattr(brand,'accent_secondary') else DEMAND,1.15)
        for names in RAIL: self.route([NODES[n] for n in names],GREY,.55,MSO_LINE_DASH_STYLE.DASH_DOT)
        for name,lon,lat,*_ in PRODUCTION:
            dx,dy={'NATREF':(-1.02,.12),'Sasol CTL':(.12,-.48),'Astron':(-.9,-.26)}.get(name,(-.9,-.26))
            self.pin(name,lon,lat,MSO_SHAPE.OVAL,INK,label=labels and name in {'Astron','NATREF','Sasol CTL'},dx=dx,dy=dy)
        for name,lon,lat,*_ in PORTS:
            if name!='Port Nolloth*': self.pin(name,lon,lat,MSO_SHAPE.RECTANGLE,GREY,label=labels and name in {'Cape Town','Richards Bay','Gqeberha'},dx=.1,dy=.05)
        for name,lon,lat in [('Durban',31.03,-29.88),('Lesedi*',28.39,-26.44)]:
            self.pin(name,lon,lat,MSO_SHAPE.DIAMOND,BLUE,dx=.13,dy=-.16)
        # Storage layer: identified Vopak sites only. Other operators' sites are not invented.
    def demand(self):
        for name,(lon,lat) in REGIONS.items():
            total = groups[name]['demand_bn_l']; x,y=self.xy(lon,lat)
            radius=.08*math.sqrt(total)
            marker(self.s,x,y,radius,DEMAND,hollow=True)
            if name=='Eastern coastal': dx,dy=-1.3,.17
            elif name=='Inland': dx,dy=-1.2,-.52
            elif name=='Western coastal': dx,dy=-.4,-.65
            else: dx,dy=-.65,-.15
            label={'Eastern coastal':'Eastern / coastal','Western coastal':'Western / coastal','Other regions':'Other regions','Inland':'Inland'}[name]
            q=text(self.s,f'{label}\n{total:.1f} bn L',x+dx,y+dy,1.55,.48,11,True,DEMAND)
            q.fill.solid(); q.fill.fore_color.rgb=brand.white
    def access(self,terminal):
        if terminal=='Durban':
            self.route(list(reversed(ROADS['N3'])),BLUE,2.3)
            self.route(PRODUCT[0],DEMAND,1.7,MSO_LINE_DASH_STYLE.DASH)
            coast=[p for p in ROADS['N2'] if p[0]>=28.7]
            self.route(coast,BLUE,2.3)
            self.route([NODES['Durban'],NODES['Gauteng']],INK,1.1,MSO_LINE_DASH_STYLE.DASH_DOT)
            lon,lat=31.03,-29.88
        else:
            self.route(PRODUCT[0],DEMAND,1.7,MSO_LINE_DASH_STYLE.DASH)
            self.route([ (28.39,-26.44),(28.05,-26.2),(28.19,-25.75)],BLUE,2.3)
            self.route(ROADS['N4'],BLUE,2.0)
            self.route([p for p in ROADS['N1'] if p[1]>-28],INK,1.1,MSO_LINE_DASH_STYLE.DASH_DOT)
            lon,lat=28.39,-26.44
        x,y=self.xy(lon,lat); marker(self.s,x,y,.09,BLUE,MSO_SHAPE.DIAMOND)

prs = Presentation(ROOT/cfg.SOURCE_TEMPLATE)
remove_all_slides_cleanly(prs)
for master in prs.slide_masters:
    for q in master.shapes:
        if q.has_text_frame and ('Click to edit' in q.text or q.name=='Text Placeholder 6'):
            q.text_frame.clear()

def slide(title,source,notes):
    s=add_themed_slide(prs,'Header only',brand=brand,title=title)
    text(s,'WEEK 1  |  South Africa petrol and diesel outlook',.5,.12,11.5,.35,13,True)
    text(s,'Source: '+source,.5,7.16,10.6,.23,7.6)
    s.notes_slide.notes_text_frame.text=notes
    return s

method = ('Map uses WGS84 / Lambert azimuthal equal-area, centred 25°E, 29°S. '
    'Natural Earth 1:50m countries; schematic transport from the kickoff appendix. '
    'Scale is nominal at map centre. Facility points are approximate, inherited from '
    'the appendix, not surveyed GPS. Lesedi uses the inherited Jameson Park-area point. '
    'No network analysis, service-area polygon or measured cost/time threshold is computed. '
    'Demand positions are regional annotations, not provincial centroids. '
    'All numerical volumes are illustrative and are not model outputs or actual Vopak flows. '
    'Natural Earth source: https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_50m_admin_0_countries.geojson')
s=slide('Locate fuel demand alongside the infrastructure serving it',
    'Natural Earth 1:50m; kickoff appendix / schematic networks; illustrative regional CSV. 6 Oct 2026.',method)
text(s,'Consolidated infrastructure + regional demand | illustrative, billion litres/year',.5,1.62,11.6,.3,14)
m=Map(s,.5,2.05,7.75,4.46); m.context(labels=True); m.demand()
text(s,'Demand to assess',8.6,2.1,3.4,.4,20,True)
rows=[['Region','Petrol','Diesel']]
for name in ['Eastern coastal','Inland','Western coastal','Other regions']:
    rr=[r for r in regional if r['region']==name]
    label={'Eastern coastal':'Eastern / coastal','Western coastal':'Western / coastal','Other regions':'Other','Inland':'Inland'}[name]
    rows.append([label]+[f"{sum(float(r['demand_bn_l']) for r in rr if r['product']==p):.1f}" for p in ['petrol','diesel']])
rows.append(['National','9.0','12.0'])
table(s,rows,8.6,2.65,[1.75,.78,.78],2.2,12)
text(s,'Seven infrastructure layers',8.6,5.03,3.5,.28,14,True)
text(s,'Production, pipelines, ports, roads, rail, storage and corridors.',8.6,5.37,3.5,.58,13)
text(s,'Marker area shows illustrative demand, not a catchment. Other operator storage sites remain to locate.',8.6,6.07,3.5,.7,11)
for x,label,kind in [(.55,'Production',MSO_SHAPE.OVAL),(1.95,'Port',MSO_SHAPE.RECTANGLE),(2.92,'Vopak storage*',MSO_SHAPE.DIAMOND)]:
    marker(s,x+.05,6.73,.045,BLUE if kind==MSO_SHAPE.DIAMOND else INK if kind==MSO_SHAPE.OVAL else GREY,kind); text(s,label,x+.17,6.62,1.4,.22,9)
for x,label,dash in [(4.4,'Road',None),(5.5,'Product pipe',None),(7.1,'Rail',MSO_LINE_DASH_STYLE.DASH_DOT)]:
    line(s,(x,6.73),(x+.28,6.73),DEMAND if label=='Product pipe' else GREY,1,dash);text(s,label,x+.34,6.62,1.0,.22,9)
text(s,'*Approximate sites. LAEA / WGS84. Transport is schematic; capacities/access unverified.',.5,6.91,11.5,.2,8.5)

s=slide('Map conditional market access from Durban and Lesedi',
    'Existing appendix routes; illustrative candidate connections, not verified catchments. Natural Earth 1:50m.',method)
text(s,'Durban | coastal deliveries + inland transfers',.55,1.66,5.6,.3,16,True)
text(s,'Lesedi | inland dispatch + connected markets',6.55,1.66,5.6,.3,16,True)
for terminal,x in [('Durban',.5),('Lesedi',6.5)]:
    m=Map(s,x,2.1,5.65,3.43);m.context();m.access(terminal)
    text(s,'Illustrative routes; no service-area boundary',x+2.3,5.27,3.2,.2,8.5)
table(s,[['Condition','Accessibility test'],
 ['Existing road / pipe candidate','Capacity, compatible product, dispatch, access rights and delivered cost'],
 ['Expanded-route candidate','A specified rail/road/pipeline intervention, timing, interfaces and customer access']],
 .5,5.8,[3.05,8.6],.95,12)
for x,label,color,dash in [(.55,'Road candidate',BLUE,None),(2.83,'Pipeline candidate',DEMAND,MSO_LINE_DASH_STYLE.DASH),(5.65,'Intervention to assess',INK,MSO_LINE_DASH_STYLE.DASH_DOT)]:
    line(s,(x,5.64),(x+.35,5.64),color,1.7,dash);text(s,label,x+.43,5.53,2.3,.2,9)
text(s,'Observed customer catchments: not supplied. Physical reach is conditional; contracts and competitors determine commercial access.',.5,6.91,11.55,.2,9)

s=slide('Separate demand, accessible volume and Vopak flows',
    'Three illustrative story CSVs; annual petrol/diesel only. No actual Vopak throughput supplied.',method)
text(s,'ILLUSTRATIVE ONLY  |  billion litres/year  |  petrol + diesel; jet excluded',.5,1.69,11.5,.3,13,True,BLUE)
text(s,'National demand 21.0 − domestic production 7.0 = required imports 14.0',.5,2.13,11.5,.45,22,True)
text(s,'Exports and stock movements are zero in this illustration only.',.5,2.62,11.5,.3,13)
rows=[['Market','Demand','Feasible\nflows','Commercial\nenvelope','Current unique\ndemand served','Additional\ncandidate']]
for name in ['Eastern coastal','Inland']:
    rows.append([name]+[f'{groups[name][k]:.1f}' for k in fields])
rows.append(['Combined']+[f"{sum(groups[n][k] for n in ['Eastern coastal','Inland']):.1f}" for k in fields])
table(s,rows,.5,3.13,[2.35,1.25,1.6,2.05,2.25,2.15],1.9,15)
text(s,'Count customer demand once',.5,5.3,11.5,.36,19,True)
byroute={r:sum(float(q['volume_bn_l']) for q in routes if q['route_id']==r) for r in ['R1','R2','R3','R4']}
durban=byroute['R1']+byroute['R2'];lesedi=byroute['R2']+byroute['R3']; unique=byroute['R1']+byroute['R4']
assert math.isclose(durban+lesedi-byroute['R2'],unique)
text(s,f"Durban receipts {durban:.1f} + Lesedi receipts {lesedi:.1f} − shared transfer {byroute['R2']:.1f} = unique demand served {unique:.1f}",.5,5.8,11.5,.48,19,False,BLUE)
text(s,'Additional candidate volume is conditional, not forecast capture. The envelope includes domestic and imported supply. Western/other access remains unassessed.',.5,6.42,11.5,.55,14)

assert len(prs.slides)==3
for index,s in enumerate(prs.slides,1):
    for q in s.shapes:
        assert q.left>=0 and q.top>=0 and q.left+q.width<=prs.slide_width+10 and q.top+q.height<=prs.slide_height+10,(index,q.name)
prs.core_properties.title='South Africa liquid fuels: Week 1 analytical maps'
prs.core_properties.author=cfg.AUTHOR
prs.core_properties.subject='Illustrative demand geography and conditional Vopak market access'
prs.save(PATH)
qa=ROOT/'qa/week1_maps';qa.mkdir(parents=True,exist_ok=True)
(qa/'build_manifest.json').write_text(json.dumps({
 'output':str(PATH),'slides':3,'template':str(cfg.SOURCE_TEMPLATE),
 'template_sha256':hashlib.sha256((ROOT/cfg.SOURCE_TEMPLATE).read_bytes()).hexdigest(),
 'projection':CRS_MAP.to_proj4(),'volumes':'Illustrative only',
 'boundary_source':'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson',
 'boundary_sha256':hashlib.sha256((ROOT/'assets/maps/ne_50m_admin_0_countries.geojson').read_bytes()).hexdigest(),
 'transport':'Inherited schematic appendix; no service-area calculation',
 'template_aware':True},indent=2),encoding='utf-8')
print(PATH)
