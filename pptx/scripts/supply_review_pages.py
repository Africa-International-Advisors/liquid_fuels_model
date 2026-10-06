"""Consume staged public evidence and explicit illustrative reporting contracts."""
import csv
import json
import yaml
from pptx.util import Inches, Pt
from pptx.enum.chart import XL_CHART_TYPE, XL_DATA_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.text import MSO_ANCHOR
from pptx.oxml.xmlchemy import OxmlElement
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
    if heading:
        text(s,heading,.5,1.78,7.05,.42,15,True)
        line(s,(.5,2.13),(7.55,2.13),brand.ink,.55)
    for a,b in [((7.88,1.99),(7.88,6.86)),((8.12,2.13),(12.15,2.13))]:
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
    market_page(prs.slides[10],text,root,brand)
    volume_page(prs.slides[12],text,root,brand)
    from storage_sensitivity_page import add_storage_sensitivity_page
    add_storage_sensitivity_page(prs.slides[14],text,root,brand)


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
    rows=[['Product','Reported\nsales','Imports','Exports','Net imports']]
    for product in ('petrol','diesel'):
        imp=lookup[2024,product,'import'];exp=lookup[2024,product,'export']
        rows.append([product.title(),f'{demand[product]:.3f}',f'{imp:.3f}',f'{exp:.3f}',f'{imp-exp:.3f}'])
    products=('petrol','diesel')
    total_imports=sum(lookup[2024,p,'import'] for p in products)
    total_exports=sum(lookup[2024,p,'export'] for p in products)
    rows.append(['Combined',f'{sum(demand[p] for p in products):.3f}',f'{total_imports:.3f}',f'{total_exports:.3f}',f'{total_imports-total_exports:.3f}'])
    series_values=[('Reported sales',[demand[p] for p in products]),
                   ('Imports',[lookup[2024,p,'import'] for p in products]),
                   ('Exports',[lookup[2024,p,'export'] for p in products])]
    chart=add_themed_chart(s,XL_CHART_TYPE.BAR_CLUSTERED,
                          Inches(.5),Inches(3.18),Inches(7.05),Inches(2.16),
                          [p.title() for p in products],series_values,
                          show_legend=False,value_axis_format='0',axis_font_size=11,brand=brand)
    chart.value_axis.minimum_scale=0;chart.value_axis.maximum_scale=14;chart.value_axis.major_unit=2
    chart.plots[0].gap_width=55
    chart.plots[0].has_data_labels=True
    labels=chart.plots[0].data_labels
    labels.position=XL_DATA_LABEL_POSITION.OUTSIDE_END
    labels.number_format='0.000';labels.font.name=cfg.THEME_FONT;labels.font.size=Pt(12)
    labels.font.color.rgb=brand.ink
    for i,(series,color) in enumerate(zip(chart.series,[brand.accent_primary,brand.accent_secondary,brand.grey_fill])):
        series.format.fill.solid();series.format.fill.fore_color.rgb=color;series.format.line.fill.background()
        x=.5+i*2.35
        q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(3.03),Inches(.12),Inches(.12))
        q.fill.solid();q.fill.fore_color.rgb=color;q.line.fill.background()
        text(s,series.name,x+.20,2.97,2.1,.28,11)
    text(s,'Production + imports − exports − stock build = consumption',.5,2.35,7.05,.29,12,True,brand.accent_primary)
    text(s,'Compare consumption with reported sales; explain coverage and the residual.',.5,2.68,7.05,.23,10.5)
    text(s,f'Net imports: petrol {rows[1][-1]}, diesel {rows[2][-1]}; combined {total_imports-total_exports:.3f} bn litres.',
         .5,5.44,7.05,.28,11,True,brand.accent_primary)
    staged=float(next(r['value'] for r in old if r['period']=='2024' and r['product']=='diesel' and r['flow']=='import'))/1e9
    residual=sum(demand[p] for p in products)-(total_imports-total_exports)
    text(s,'Source flag | diesel imports',.5,5.97,3.35,.32,14,True,brand.accent_primary)
    text(s,f'FIASA {staged:.3f}; government 10.800.\nDifference {10.8-staged:+.3f} bn L. Preserve both;\ninvestigate scope and vintage.',.5,6.40,3.35,.59,11.5)
    line(s,(4.03,5.96),(4.03,6.99),brand.grey_fill,.7)
    text(s,'2024 accounting remains open',4.22,5.97,3.33,.32,14,True,brand.accent_primary)
    text(s,f'Sales less net imports = {residual:.3f} bn L.\nBalancing requirement, not production.\nProduction, stocks and coverage unresolved.',4.22,6.40,3.33,.59,11.5)
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
        skip=OxmlElement('c:tickLblSkip');skip.set('val','4')
        chart.category_axis._element.insert_element_before(skip,'c:tickMarkSkip','c:noMultiLvlLbl','c:extLst')
        for series,color in zip(chart.series,(brand.accent_primary,brand.accent_secondary)):
            series.format.fill.solid();series.format.fill.fore_color.rgb=color
            series.format.line.color.rgb=color
        text(s,f'{settings["horizon_year"]}: {baseline[-1]+addition[-1]:.0f} thousand bbl/day',x,6.01,3.40,.30,12,True,brand.accent_primary)
    text(s,f'B adds {settings["proposed_addition_bpd"]/1000:.0f} from {completion}; darker navy = existing footprint; lighter blue = conditional addition.',.5,6.46,7.05,.42,11)
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
          'DMPR 2022 sales; NAMCOR NOSF; Galp GIMTL; WBCG / TRAC corridors; Natural Earth. Capacities and URLs in notes.',text,brand)
    project=Transformer.from_crs('EPSG:4326',CRS.from_proj4(config['projection']),always_xy=True)
    ext=config['extent'];bounds=[project.transform(lon,lat) for lon in (ext[0],ext[2]) for lat in (ext[1],ext[3])]
    xmin=min(p[0] for p in bounds);xmax=max(p[0] for p in bounds);ymin=min(p[1] for p in bounds);ymax=max(p[1] for p in bounds)
    factor=min(6.85/(xmax-xmin),3.25/(ymax-ymin));ox=.5+(7.05-(xmax-xmin)*factor)/2;oy=2.39+(3.4-(ymax-ymin)*factor)/2
    def xy(lon,lat):
        x,y=project.transform(lon,lat);return ox+(x-xmin)*factor,oy+(ymax-y)*factor
    bg=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(.5),Inches(2.39),Inches(7.05),Inches(3.4));bg.fill.solid();bg.fill.fore_color.rgb=brand.white;bg.line.color.rgb=brand.grey_fill
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
    from provincial_demand_map import sales, NAMES, COLOURS, CLASSES
    from pptx.dml.color import RGBColor
    observations,_,_=sales(root)
    for feature in json.loads((root/'assets/maps/geoboundaries_zaf_adm1_simplified.geojson').read_text())['features']:
        code=NAMES[feature['properties']['shapeName']]
        geo=shape(feature['geometry'])
        for polygon in list(geo.geoms) if geo.geom_type=='MultiPolygon' else [geo]:
            coords=[(int(Inches(a)),int(Inches(b))) for a,b in [xy(lon,lat) for lon,lat,*_ in polygon.exterior.coords]]
            fb=s.shapes.build_freeform(*coords[0]);fb.add_line_segments(coords[1:],close=True);q=fb.convert_to_shape()
            q.fill.solid();q.fill.fore_color.rgb=RGBColor.from_string(COLOURS[sum(observations[code]>=limit for limit in CLASSES)])
            q.line.color.rgb=brand.white;q.line.width=Pt(.4)
    # Names and verified capacity annotations; circles encode neither share nor throughput.
    capacity=json.loads((root/'story/gateway_storage_2026_10_06.json').read_text())
    for r in capacity['sites']:
        lon,lat=config['points'][r['gateway']];x,y=xy(lon,lat)
        if r['gateway']=='Walvis Bay':px,py=x-1.42,y+.42
        else:px,py=x+.28,y+.28
        q=text(s,f"{r['operator']}\n{r['petrol_diesel_m3']/1000:.0f}k m³ petrol/diesel",px,py,1.72,.43,9,True,brand.accent_primary)
        q.fill.solid();q.fill.fore_color.rgb=brand.white
    text(s,'Shading: provincial petrol + diesel sales, 2022 (bn litres/year)',.5,2.23,7.05,.18,9,True,brand.accent_primary)
    for label,lon,lat in [('NAMIBIA',17.0,-19.7),('BOTSWANA',23.6,-20.0),('SOUTH AFRICA',24.2,-30.0),('MOZAMBIQUE',32.4,-20.0)]:
        x,y=xy(lon,lat);text(s,label,x-.4,y,1.45,.25,9,True)
    colors={'vopak':brand.accent_primary,'pipe':brand.accent_primary,'east':brand.ink,'west':brand.accent_secondary if hasattr(brand,'accent_secondary') else brand.ink}
    for route in config['routes']:
        for a,b in zip(route['waypoints'],route['waypoints'][1:]):
            line(s,xy(*a),xy(*b),colors[route['style']],1.6 if route['style']!='pipe' else 1,
                 MSO_LINE_DASH_STYLE.DASH if route['style'] in ('west','pipe') else None)
    offsets={'Walvis Bay':(-1.25,.1),'Windhoek':(-.4,-.32),'Gaborone':(-.65,-.35),
             'Matola / Maputo':(.10,-.05),'Mbombela':(-.4,-.4),'Gauteng':(-1.1,.0),'Lesedi*':(-.55,.30),'Durban':(.1,.18)}
    for name,(lon,lat) in config['points'].items():
        if name not in offsets:continue
        x,y=xy(lon,lat)
        kind=(MSO_SHAPE.DIAMOND if name in ('Lesedi*','Durban') else
              MSO_SHAPE.RECTANGLE if name in ('Walvis Bay','Matola / Maputo') else MSO_SHAPE.OVAL)
        q=s.shapes.add_shape(kind,Inches(x-.04),Inches(y-.04),Inches(.08),Inches(.08));q.fill.solid();q.fill.fore_color.rgb=brand.accent_primary;q.line.fill.background()
        dx,dy=offsets[name];w=1.55 if name=='Matola / Maputo' else 1.12
        q=text(s,name,x+dx,y+dy,w,.28,11,True,brand.accent_primary);q.fill.solid();q.fill.fore_color.rgb=brand.white
    text(s,'N',.67,2.60,.22,.23,11,True);line(s,(.78,3.12),(.78,2.9),brand.ink,1)
    line(s,(.78,2.9),(.74,2.98),brand.ink,1);line(s,(.78,2.9),(.82,2.98),brand.ink,1)
    width=500000*factor;line(s,(.7,5.61),(.7+width,5.61),brand.ink,1.5)
    text(s,'0',.7,5.38,.2,.22,9);text(s,'500 km',.7+width-.15,5.38,.65,.22,9)
    # Three distinct visual keys: sales shading, facilities, then schematic routes.
    for i,(label,colour) in enumerate(zip(['<1','1–2','2–4','4–6','6+','Unassessed'],COLOURS+[None])):
        x=.5+i*1.13
        q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(5.99),Inches(.15),Inches(.15))
        q.fill.solid();q.fill.fore_color.rgb=RGBColor.from_string(colour) if colour else brand.grey_fill
        q.line.color.rgb=brand.ink;q.line.width=Pt(.3)
        text(s,label,x+.23,5.93,.85 if i<5 else 1.15,.24,10.5)
    for x,label,kind in [(.5,'Vopak facility',MSO_SHAPE.DIAMOND),(2.85,'Port / fuel storage',MSO_SHAPE.RECTANGLE),(5.30,'Route waypoint',MSO_SHAPE.OVAL)]:
        q=s.shapes.add_shape(kind,Inches(x+.03),Inches(6.30),Inches(.10),Inches(.10))
        q.fill.solid();q.fill.fore_color.rgb=brand.accent_primary;q.line.fill.background()
        text(s,label,x+.23,6.23,2.05,.25,10.5)
    for i,(label,style) in enumerate([('Road: Durban–Gauteng','vopak'),('Road: Matola–Gauteng (N4)','east'),
                                    ('Pipeline: NMPP','pipe'),('Walvis–Gauteng (Trans-Kalahari)','west')]):
        x=.5+(i%2)*3.55;y=6.53+(i//2)*.27
        line(s,(x,y+.10),(x+.38,y+.10),colors[style],1.6,
             MSO_LINE_DASH_STYLE.DASH if style in ('west','pipe') else None)
        text(s,label,x+.48,y,3.0,.23,10.5)
    text(s,'Routes schematic; access unverified. Colour measures provincial totals, not density or Vopak share.',.5,7.00,7.05,.14,7.5)
    panel(s,text,brand,[('Compare the same inland destination','Gauteng is the common comparison market. Lesedi is a Vopak facility, not a destination every competing route must pass through.'),
        ('Matola approaches from the east','N4/Maputo connects Mozambique to Gauteng via Komatipoort and Mpumalanga. Fuel-compatible terminal access and road/rail service need testing.'),
        ('Walvis is an inland comparator','Trans-Kalahari links Walvis Bay via Namibia and Botswana to Gauteng. Its competitiveness for specific inland customers is unassessed.')],
        'Nigel: select the customer destination. Manish: compare handling, transport, border/FX costs and access on the same R/litre basis; keep unevidenced routes unassessed.')
    s.notes_slide.notes_text_frame.text+='\n'+json.dumps(config,indent=2)+'\n'+json.dumps(capacity,indent=2)


def volume_page(s,text,root,brand):
    rows=read(root/'story/illustrative_market_catchments.csv')
    current=sum(float(r['current_unique_vopak_bn_l']) for r in rows if r['current_unique_vopak_bn_l'])
    coastal=sum(float(r['additional_candidate_bn_l']) for r in rows if r['region']=='Eastern coastal')
    inland=sum(float(r['additional_candidate_bn_l']) for r in rows if r['region']=='Inland')
    frame(s,'Show what must hold to reach each candidate volume',
          'Accessibility gates and volume milestones | illustrative bn L/year',
          'Existing illustrative catchment CSV; conditions authored for review. No actual Vopak share, cost threshold or forecast capture established.',text,brand)
    text(s,'ILLUSTRATIVE | each increment requires evidence; not cumulative terminal receipts',.5,2.38,7.05,.30,11,True,brand.accent_primary)
    text(s,f'{coastal+inland:.1f} bn L/year additional candidate',.5,2.98,7.05,.50,22,True,brand.accent_primary)
    text(s,f'{current:.1f} current example + {coastal+inland:.1f} additional = {current+coastal+inland:.1f} total envelope',.5,3.56,7.05,.31,12)
    total=current+coastal+inland
    x=.5
    for label,value,color in [('Current',current,brand.accent_primary),('Coastal +',coastal,brand.accent_secondary),('Inland +',inland,brand.grey_fill)]:
        w=7.05*value/total
        q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(4.17),Inches(w),Inches(.65))
        q.fill.solid();q.fill.fore_color.rgb=color;q.line.fill.background()
        text(s,f'{label} {value:.1f}',x+.07,4.34,w-.14,.30,12,True,brand.white if label=='Current' else brand.ink)
        x+=w
    text(s,'What must hold before any additional litres are counted?',.5,5.25,7.05,.33,14,True,brand.accent_primary)
    table(s,[['Competitive cost','Usable capacity','Customer access','Unique deliveries']],.5,5.85,[1.76,1.76,1.76,1.77],.63,brand,11)
    text(s,'Detailed customer-by-route gates belong in the evidence register.\nIllustration only; 5.5 is neither a forecast nor a confirmed capturable market.',.5,6.60,7.05,.40,11)
    panel(s,text,brand,[('Reach is necessary, not sufficient','Accessibility map p9 and competing routes p10 locate candidate access. Neither currently links a verified cost threshold to customer litres.'),
        ('Example milestones are conditional',f'The current example is {current:.1f}. Coastal candidate {coastal:.1f} raises it to {current+coastal:.1f}; inland candidate {inland:.1f} raises it to {current+coastal+inland:.1f}. These are authored volumes.'),
        ('Every increment needs four gates','Evidence cost, route/tank capacity, customer rights and unique deliveries for the same product and period. Unassessed litres remain explicit.')],
        'Nigel: agree destinations and acceptable delivered cost. Manish: build a customer-by-route gate table; record passed, failed and unassessed litres, with sources and conditions.')
    s.notes_slide.notes_text_frame.text+='\nVolume milestones derive only from the existing illustrative catchment CSV. Gates specify required evidence, not calculated allocation. No threshold assigned and no new model volume invented.'


def market_page(s,text,root,brand):
    rows=read(root/'story/illustrative_market_catchments.csv')
    selected=[r for r in rows if r['commercial_envelope_bn_l']]
    totals={key:sum(float(r[key]) for r in selected) for key in ('demand_bn_l','feasible_service_bn_l','commercial_envelope_bn_l','current_unique_vopak_bn_l')}
    frame(s,'Separate demand, accessible volume and unique deliveries',
          'Market screens | illustrative bn litres/year',
          'Existing illustrative market catchment and transfer examples. Not reported sales or actual Vopak flows.',text,brand)
    text(s,'Successive screens; these volumes are illustrative',.5,2.37,7.05,.28,11,True,brand.accent_primary)
    labels=[('Catchment demand','demand_bn_l'),('Physically feasible','feasible_service_bn_l'),('Commercial envelope','commercial_envelope_bn_l'),('Current unique deliveries','current_unique_vopak_bn_l')]
    for i,(label,key) in enumerate(labels):
        y=2.95+i*.63;v=totals[key]
        text(s,label,.5,y,2.25,.32,12,True)
        w=4.05*v/totals['demand_bn_l']
        q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(2.85),Inches(y+.05),Inches(w),Inches(.30))
        q.fill.solid();q.fill.fore_color.rgb=brand.accent_primary if i==3 else brand.accent_secondary;q.line.fill.background()
        text(s,f'{v:.1f}',2.85+w+.06,y,.6,.30,12,True)
    text(s,'Count Durban–Lesedi transfers once',.5,5.70,7.05,.33,14,True,brand.accent_primary)
    # Existing receipt example is retained, not introduced as an observed input.
    text(s,'Durban 2.8 + Lesedi 2.0 − shared transfer 1.8 = unique 3.0',.5,6.16,7.05,.35,12,True)
    text(s,'Demand ≠ terminal receipts ≠ storage capacity. Incremental opportunity is on page 13.',.5,6.70,7.05,.28,10.5)
    s.notes_slide.notes_text_frame.text+='\nSuccessive volumes summed from illustrative_market_catchments.csv for assessed Eastern coastal / Inland rows only. Transfer arithmetic retained from existing pack; replace with matched customer records.'
