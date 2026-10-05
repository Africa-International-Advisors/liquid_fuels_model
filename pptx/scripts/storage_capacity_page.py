"""Rank published gross storage from the dated evidence inventory, not throughput."""
from collections import defaultdict
from pptx.util import Inches,Pt
from pptx.enum.shapes import MSO_SHAPE,MSO_CONNECTOR
from pptx.dml.color import RGBColor
from storage_footprint import inventory,storage_notes

def add_storage_capacity_page(slide,exhibit_layout,text,root,brand):
    rows=[r for r in inventory(root) if r['map_include']=='yes' and r['gross_capacity_m3']]
    locations=defaultdict(list)
    for r in rows:locations[r['site']].append(r)
    totals={site:sum(float(r['gross_capacity_m3']) for r in data)/1000 for site,data in locations.items()}
    order=sorted(totals,key=totals.get,reverse=True)
    assert len(rows)==6 and len(order)==5
    colours={'Vopak':brand.accent_primary,'Bidvest Tank Terminals':RGBColor.from_string('809CC7'),
             'VTTI Burgan Cape Terminal':RGBColor.from_string('BACCE4')}
    s=slide('Compare published storage capacity by location',
        'Vopak Durban/Lesedi terminal pages; Bidvest site page; VTTI Burgan Cape. Checked 6 Oct 2026; gross capacity.',
        storage_notes(root)+'\nBar totals sum only the published records shown. No missing site is assigned zero. '
        'Durban combines separate Vopak and Bidvest gross stocks. Richards Bay includes gases. '
        'Different product scopes and undisclosed publication dates prevent a like-for-like fuel-only ranking. '
        'Vopak HTML capacity extraction uses data-end-number in the Capacity block with cbm selector; '
        'the alternate visible values are barrels. Original HTML retained under external/data/raw/vopak_storage_20261006/.')
    exhibit_layout(s,'Published gross storage | partial inventory, thousand m³',[
        ('Durban leads this evidenced subset',f"Published Vopak and Bidvest capacity totals {totals['Durban']:.1f} thousand m³. Other operators may add further capacity."),
        ('Product scope changes the comparison','Bidvest includes mixed liquids and Richards Bay gases. These bars are gross storage, not usable petrol/diesel capacity.'),
        ('Missing capacity remains unknown','Sasol depots and Transnet Tarlton/Jameson Park are identified, but capacities are not quantified in this inventory.'),
        ('Capacity supports the access question','Storage is a stock. Deliverable fuel volume also depends on utilisation, turnover, routes, compatible tanks and commercial access.'),
    ])
    x0=2.22; width=4.63; ymax=850
    # Shared quantitative axis; editable stacked bars distinguish contributing operators.
    for v in [0,200,400,600,800]:
        x=x0+width*v/ymax
        q=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x),Inches(2.71),Inches(x),Inches(5.30))
        q.line.color.rgb=brand.grey_fill;q.line.width=Pt(.5)
        text(s,str(v),x-.15,2.40,.42,.20,9)
    for i,site in enumerate(order):
        y=2.90+i*.49
        text(s,site,.5,y+.03,1.65,.25,12,True)
        x=x0
        for r in sorted(locations[site],key=lambda r:r['operator']!='Vopak'):
            w=width*(float(r['gross_capacity_m3'])/1000)/ymax
            q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(.29))
            q.name=f"Published gross capacity: {r['operator']} {site}: {r['gross_capacity_m3']} m3"
            q.fill.solid();q.fill.fore_color.rgb=colours[r['operator']];q.line.fill.background()
            x+=w
        text(s,f'{totals[site]:,.1f}',x+.08,y+.03,.62,.25,11,True)
    for x,name,operator in [( .5,'Vopak','Vopak'),(2.4,'Bidvest','Bidvest Tank Terminals'),(4.4,'Burgan Cape','VTTI Burgan Cape Terminal')]:
        q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(5.65),Inches(.13),Inches(.13))
        q.fill.solid();q.fill.fore_color.rgb=colours[operator];q.line.fill.background()
        text(s,name,x+.20,5.60,1.70,.23,10)
    text(s,'Unquantified: Sasol Alrode, Pretoria West, Waltloo and Sasolburg;\nTransnet Tarlton and Jameson Park. Missing values are not zero.',.5,6.02,7.05,.56,11)
    text(s,'Partial public inventory. Mixed products / source vintages; no fuel-only or national-capacity share inferred.',.5,6.78,7.05,.31,9)
    return s
