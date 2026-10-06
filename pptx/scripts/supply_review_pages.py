"""Consume staged public evidence and explicit illustrative reporting contracts."""
import csv
import json
import yaml
from pptx.util import Inches, Pt
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.text import MSO_ANCHOR
from pyproj import CRS, Transformer
from shapely.geometry import shape, box
from brand_pptx import add_themed_chart, _strip_table_style, cell_bottom_rule
from brand_configs import vopak as cfg
from scr_structure import panel


def read(path):
    return list(csv.DictReader(path.open(encoding='utf-8-sig',newline='')))


def frame(s, title, heading, source, text, brand):
    for q in list(s.shapes):
        if Inches(1.7)<=q.top<Inches(7.05):q._element.getparent().remove(q._element)
        elif q.has_text_frame and q.top==Inches(7.16):
            q.text_frame.paragraphs[0].text='Source: '+source
        elif q.is_placeholder and q.has_text_frame and 'Title' in q.name:
            q.text_frame.paragraphs[0].runs[0].text=title
    text(s,heading,.5,1.78,7.05,.42,15,True)
    for a,b in [((.5,2.13),(7.55,2.13)),((7.88,1.99),(7.88,6.86)),((8.12,2.13),(12.15,2.13))]:
        line(s,a,b,brand.ink,.55)


def line(s,a,b,color,width=.6,dash=None):
    q=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(a[0]),Inches(a[1]),Inches(b[0]),Inches(b[1]))
    q.line.color.rgb=color;q.line.width=Pt(width)
    if dash:q.line.dash_style=dash
    return q


def table(s,rows,x,y,widths,h,brand,size=11):
    q=s.shapes.add_table(len(rows),len(widths),Inches(x),Inches(y),Inches(sum(widths)),Inches(h))
    t=q.table;_strip_table_style(t)
    for c,w in zip(t.columns,widths):c.width=Inches(w)
    for i,row in enumerate(rows):
        for j,value in enumerate(row):
            cell=t.cell(i,j);cell.text=str(value)
            cell.margin_left=cell.margin_right=Inches(.055);cell.margin_top=cell.margin_bottom=Inches(.045)
            cell.vertical_anchor=MSO_ANCHOR.MIDDLE
            cell.fill.solid();cell.fill.fore_color.rgb=brand.white
            for p in cell.text_frame.paragraphs:
                p.font.name=cfg.THEME_FONT;p.font.size=Pt(size);p.font.bold=i==0
                p.font.color.rgb=brand.ink;p.space_after=Pt(0)
            cell_bottom_rule(cell,color=brand.grey_fill,w_pt=.5)
    return q


def populate_review_exhibits(prs,text,root,brand):
    from demand_driver_page import add_driver_page
    add_driver_page(prs.slides[6],text,root,brand)
    national_page(prs.slides[4],text,root,brand)
    capacity_page(prs.slides[7],text,root,brand)
    corridor_page(prs.slides[9],text,root,brand)
    volume_page(prs.slides[12],text,root,brand)


def national_page(s,text,root,brand):
    base=root.parent/'assumptions/2026/timeseries'
    trade=read(base/'fuel_trade_department_review.csv')
    sales=read(base/'fuel_sales_fiasa.csv')
    old=read(base/'fuel_trade_fiasa.csv')
    lookup={(int(r['period']),r['product'],r['flow']):float(r['value'])/1e9 for r in trade}
    demand={r['product']:float(r['value'])/1e9 for r in sales if r['period']=='2024'}
    frame(s,'Collect the national fuel balance and expose source disagreements',
          'National petrol/diesel | 2024, billion litres',
          'Government Energy Trade Report 2024, printed pp.12–13; FIASA 2025, pp.47–49; energy balance 2021. Rounded trade figures.',text,brand)
    text(s,'COLLECTED | trade and sales; production/stock reconciliation remains open',.5,2.38,7.05,.32,11,True,brand.accent_primary)
    rows=[['Product','Reported\nsales','Imports','Exports','Net imports']]
    for product in ('petrol','diesel'):
        imp=lookup[2024,product,'import'];exp=lookup[2024,product,'export']
        rows.append([product.title(),f'{demand[product]:.3f}',f'{imp:.3f}',f'{exp:.3f}',f'{imp-exp:.3f}'])
    products=('petrol','diesel')
    total_imports=sum(lookup[2024,p,'import'] for p in products)
    total_exports=sum(lookup[2024,p,'export'] for p in products)
    rows.append(['Combined',f'{sum(demand[p] for p in products):.3f}',f'{total_imports:.3f}',f'{total_exports:.3f}',f'{total_imports-total_exports:.3f}'])
    table(s,rows,.5,2.91,[1.35,1.40,1.40,1.40,1.50],1.37,brand,12)
    text(s,'Source flag | 2024 diesel imports',.5,4.53,7.05,.34,14,True,brand.accent_primary)
    staged=float(next(r['value'] for r in old if r['period']=='2024' and r['product']=='diesel' and r['flow']=='import'))/1e9
    text(s,f'FIASA staged: {staged:.3f}  |  Government report: 10.800\nDifference: {10.8-staged:+.3f} bn L. Preserve both; investigate scope and vintage.',.5,4.95,7.05,.63,12)
    text(s,'Domestic production remains a dated observation',.5,5.86,7.05,.34,14,True,brand.accent_primary)
    production={r['product']:float(r['value'])/1e9 for r in read(base/'energy_balance_department.csv') if r['period']=='2021' and r['flow_key']=='production'}
    text(s,f'Latest staged balance: 2021 petrol {production["petrol"]:.2f}; diesel {production["diesel"]:.2f} bn L.\nDo not combine 2021 output with 2024 sales/trade to close a balance.',.5,6.26,7.05,.54,12)
    panel(s,text,brand,[('Public figures are collectable','2024 petrol/diesel imports total 14.8 bn L in the government report. Exports total 1.71 bn L; these are rounded reported figures.'),
        ('The sources disagree','FIASA reports 14.793 bn L of diesel imports for 2024 versus 10.8 bn L in the government report. Neither value has been silently replaced.'),
        ('Port cargo has wider coverage','TNPA publishes liquid-bulk cargo by port, but it includes crude and other liquids. It does not establish petrol/diesel import allocation.')],
        'Manish: reconcile raw SARS product codes and units, then source matched-year production and stocks. Nigel: confirm access to product-specific port data.')
    s.notes_slide.notes_text_frame.text+='\n'+(base/'supply_review.sources.json').read_text()+'\nTrade source flag: '+str(rows)


def capacity_page(s,text,root,brand):
    base=root.parent/'assumptions/2026'
    observations=read(base/'timeseries/refinery_capacity_reported.csv')
    settings=yaml.safe_load((base/'review_capacity_scenarios.yaml').read_text())['capacity_comparison']['value']
    years=list(range(2016,settings['horizon_year']+1))
    hist={year:sum(float(r['value']) for r in observations if int(r['period'])==year)/1000 for year in range(2016,2026)}
    baseline=[hist.get(year,hist[2025]) for year in years]
    completion=settings['illustrative_fid_year']+settings['construction_months']//12
    extra=[settings['proposed_addition_bpd']/1000 if year>=completion else 0 for year in years]
    frame(s,'Compare the capacity history with a conditional redevelopment case',
          'Published footprint + illustrative scenarios | thousand bbl/day',
          'FIASA Annual Report 2025, p.49; CEF statement 23 Sep 2026. Nameplate / crude-equivalent capacity; not actual fuel output.',text,brand)
    text(s,'History 2016–2025 is sourced; 2026 onward is illustrative, not a forecast',.5,2.38,7.05,.32,11,True,brand.accent_primary)
    for i,(heading,addition) in enumerate([('A | No new refinery capacity',[0]*len(years)),('B | Conditional CEF redevelopment',extra)]):
        x=.5+i*3.64
        text(s,heading,x,2.87,3.40,.47,12,True,brand.accent_primary)
        chart=add_themed_chart(s,XL_CHART_TYPE.AREA_STACKED,Inches(x),Inches(3.36),Inches(3.40),Inches(2.57),
                              [str(y) for y in years],[('Reported footprint / held flat',baseline),('Conditional addition',addition)],
                              show_legend=False,value_axis_format='0',axis_font_size=11,brand=brand)
        chart.value_axis.minimum_scale=0;chart.value_axis.maximum_scale=800;chart.value_axis.major_unit=200
        chart.category_axis.tick_label_spacing=4
        for series,color in zip(chart.series,(brand.accent_primary,brand.grey_fill)):
            series.format.fill.solid();series.format.fill.fore_color.rgb=color
            series.format.line.color.rgb=color
        text(s,f'{settings["horizon_year"]}: {baseline[-1]+addition[-1]:.0f} thousand bbl/day',x,6.01,3.40,.30,12,True,brand.accent_primary)
    text(s,'718 → 538 → 358: published footprint; idle nameplate and synthetic crude-equivalent included.',.5,6.46,7.05,.42,11)
    text(s,f'B assumes illustrative FID {settings["illustrative_fid_year"]} + {settings["construction_months"]} months; no sanctioned date. Both hold existing capacity flat.',.5,6.80,7.05,.22,9)
    panel(s,text,brand,[('History shows a structural decline','Published total falls from 718 in 2016–2020 to 538 in 2021 and 358 from 2022–2025. Capacity does not measure realised output.'),
        ('Redevelopment is conditional','CEF proposes approximately 400 thousand bbl/day after FID. Construction is approximately 48 months; the 2029 FID here is authored for comparison.'),
        ('Product output still needs modelling','Source utilisation, downtime and product yields before translating capacity into domestic supply. Secunda/Natref cases remain open.')],
        'Nigel: agree scenario timing. Manish: reconcile plant capacity and output/yields. Henry: review technical feasibility and the Sasol gas-to-liquids mechanism.')
    s.notes_slide.notes_text_frame.text+='\nCapacity series: '+str(hist)+'\nIllustrative assumptions: '+json.dumps(settings)+'\nCEF proposal is not FID or a committed restart. FIASA Enref 135k differs from workbook/Engen 120k; no engine parameter changed.'


def corridor_page(s,text,root,brand):
    config=json.loads((root/'story/corridor_comparison_2026_10_06.json').read_text())
    frame(s,'Locate alternative gateways to the same inland customers',
          'Durban, Matola and Walvis Bay | schematic corridor comparison',
          'WBCG Trans-Kalahari; TRAC N4/Maputo corridor; kickoff NMPP schematic; Natural Earth 1:50m. Locations approximate.',text,brand)
    project=Transformer.from_crs('EPSG:4326',CRS.from_proj4(config['projection']),always_xy=True)
    ext=config['extent'];bounds=[project.transform(lon,lat) for lon in (ext[0],ext[2]) for lat in (ext[1],ext[3])]
    xmin=min(p[0] for p in bounds);xmax=max(p[0] for p in bounds);ymin=min(p[1] for p in bounds);ymax=max(p[1] for p in bounds)
    factor=min(6.85/(xmax-xmin),3.85/(ymax-ymin));ox=.5+(7.05-(xmax-xmin)*factor)/2;oy=2.39+(4-(ymax-ymin)*factor)/2
    def xy(lon,lat):
        x,y=project.transform(lon,lat);return ox+(x-xmin)*factor,oy+(ymax-y)*factor
    bg=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(.5),Inches(2.39),Inches(7.05),Inches(4.0));bg.fill.solid();bg.fill.fore_color.rgb=brand.white;bg.line.color.rgb=brand.grey_fill
    countries=json.loads((root/'assets/maps/ne_50m_admin_0_countries.geojson').read_text(encoding='utf-8'))
    for feature in countries['features']:
        geo=shape(feature['geometry']).intersection(box(*ext))
        if geo.is_empty:continue
        polygons=list(geo.geoms) if geo.geom_type=='MultiPolygon' else [geo]
        for polygon in polygons:
            if polygon.geom_type!='Polygon':continue
            coords=[(int(Inches(a)),int(Inches(b))) for a,b in [xy(lon,lat) for lon,lat,*_ in polygon.exterior.coords]]
            fb=s.shapes.build_freeform(*coords[0]);fb.add_line_segments(coords[1:],close=True);q=fb.convert_to_shape()
            q.fill.solid();q.fill.fore_color.rgb=brand.grey_fill;q.line.color.rgb=brand.white;q.line.width=Pt(.7)
    for label,lon,lat in [('NAMIBIA',17.0,-19.7),('BOTSWANA',23.6,-20.0),('SOUTH AFRICA',24.2,-30.0),('MOZAMBIQUE',32.4,-20.0)]:
        x,y=xy(lon,lat);text(s,label,x-.4,y,1.45,.25,9,True)
    colors={'vopak':brand.accent_primary,'pipe':brand.accent_primary,'east':brand.ink,'west':brand.accent_secondary if hasattr(brand,'accent_secondary') else brand.ink}
    for route in config['routes']:
        for a,b in zip(route['waypoints'],route['waypoints'][1:]):
            line(s,xy(*a),xy(*b),colors[route['style']],1.6 if route['style']!='pipe' else 1,
                 MSO_LINE_DASH_STYLE.DASH if route['style'] in ('west','pipe') else None)
    offsets={'Walvis Bay':(-1.25,.1),'Windhoek':(-.4,-.32),'Gaborone':(-.65,-.35),
             'Matola / Maputo':(.10,-.05),'Mbombela':(-.4,-.4),'Gauteng':(-1.1,.0),'Lesedi*':(-.2,.30),'Durban':(.1,-.03)}
    for name,(lon,lat) in config['points'].items():
        if name not in offsets:continue
        x,y=xy(lon,lat);kind=MSO_SHAPE.DIAMOND if name in ('Lesedi*','Durban') else MSO_SHAPE.OVAL
        q=s.shapes.add_shape(kind,Inches(x-.04),Inches(y-.04),Inches(.08),Inches(.08));q.fill.solid();q.fill.fore_color.rgb=brand.accent_primary;q.line.fill.background()
        dx,dy=offsets[name];w=1.55 if name=='Matola / Maputo' else 1.12
        q=text(s,name,x+dx,y+dy,w,.28,11,True,brand.accent_primary);q.fill.solid();q.fill.fore_color.rgb=brand.white
    text(s,'N',.67,2.60,.22,.23,11,True);line(s,(.78,3.12),(.78,2.9),brand.ink,1)
    line(s,(.78,2.9),(.74,2.98),brand.ink,1);line(s,(.78,2.9),(.82,2.98),brand.ink,1)
    width=500000*factor;line(s,(.7,6.15),(.7+width,6.15),brand.ink,1.5)
    text(s,'0',.7,5.92,.2,.22,9);text(s,'500 km',.7+width-.15,5.92,.65,.22,9)
    text(s,'Solid: Durban / N4 candidates   |   Dashed: Trans-Kalahari / NMPP',.5,6.54,7.05,.32,11)
    text(s,'LAEA / WGS84; routes schematic. No cost, available capacity, fuel rights or catchment is inferred.',.5,6.82,7.05,.20,9)
    panel(s,text,brand,[('Compare the same inland destination','Gauteng is the common comparison market. Lesedi is a Vopak facility, not a destination every competing route must pass through.'),
        ('Matola approaches from the east','N4/Maputo connects Mozambique to Gauteng via Komatipoort and Mpumalanga. Fuel-compatible terminal access and road/rail service need testing.'),
        ('Walvis is an inland comparator','Trans-Kalahari links Walvis Bay via Namibia and Botswana to Gauteng. Its competitiveness for specific inland customers is unassessed.')],
        'Nigel: select the customer destination. Manish: compare handling, transport, border/FX costs and access on the same R/litre basis; keep unevidenced routes unassessed.')
    s.notes_slide.notes_text_frame.text+='\n'+json.dumps(config,indent=2)


def volume_page(s,text,root,brand):
    rows=read(root/'story/illustrative_market_catchments.csv')
    current=sum(float(r['current_unique_vopak_bn_l']) for r in rows if r['current_unique_vopak_bn_l'])
    coastal=sum(float(r['additional_candidate_bn_l']) for r in rows if r['region']=='Eastern coastal')
    inland=sum(float(r['additional_candidate_bn_l']) for r in rows if r['region']=='Inland')
    frame(s,'Show what must hold to reach each candidate volume',
          'Accessibility gates and volume milestones | illustrative bn L/year',
          'Existing illustrative catchment CSV; conditions authored for review. No actual Vopak share, cost threshold or forecast capture established.',text,brand)
    text(s,'ILLUSTRATIVE | each increment requires evidence; not cumulative terminal receipts',.5,2.38,7.05,.30,11,True,brand.accent_primary)
    targets=[('Current example',current),('+ coastal candidate',current+coastal),('+ inland candidate',current+coastal+inland)]
    for i,(label,value) in enumerate(targets):
        y=2.97+i*.61;text(s,label,.5,y,2.02,.29,12,True)
        w=4.2*value/(current+coastal+inland)
        q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(2.60),Inches(y+.04),Inches(w),Inches(.27));q.fill.solid();q.fill.fore_color.rgb=brand.accent_primary;q.line.fill.background()
        text(s,f'{value:.1f}',2.6+w+.07,y, .6,.29,12,True)
    text(s,'What must be true for the additional volume?',.5,4.91,7.05,.33,14,True,brand.accent_primary)
    table(s,[['Gate','Coastal +1.5','Inland +4.0'],
        ['Delivered cost','≤ agreed customer threshold','Competitive full route R/litre'],
        ['Physical access','Compatible receipt / dispatch','NMPP or alternative route capacity'],
        ['Commercial rights','Customer access / switching','Destination / contract access'],
        ['Volume accounting','Unique final deliveries','Remove shared Durban–Lesedi transfers']],
        .5,5.37,[1.6,2.55,2.9],1.48,brand,10.5)
    panel(s,text,brand,[('Reach is necessary, not sufficient','Accessibility map p9 and competing routes p10 locate candidate access. Neither currently links a verified cost threshold to customer litres.'),
        ('Example milestones are conditional',f'The current example is {current:.1f}. Coastal candidate {coastal:.1f} raises it to {current+coastal:.1f}; inland candidate {inland:.1f} raises it to {current+coastal+inland:.1f}. These are authored volumes.'),
        ('Every increment needs four gates','Evidence cost, route/tank capacity, customer rights and unique deliveries for the same product and period. Unassessed litres remain explicit.')],
        'Nigel: agree destinations and acceptable delivered cost. Manish: build a customer-by-route gate table; record passed, failed and unassessed litres, with sources and conditions.')
    s.notes_slide.notes_text_frame.text+='\nVolume milestones derive only from the existing illustrative catchment CSV. Gates specify required evidence, not calculated allocation. No threshold assigned and no new model volume invented.'
