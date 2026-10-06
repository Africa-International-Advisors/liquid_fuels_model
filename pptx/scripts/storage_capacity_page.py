"""Published storage stocks and separately scaled Transnet lease opportunities."""
from collections import defaultdict
from pptx.util import Inches,Pt
from pptx.enum.shapes import MSO_SHAPE,MSO_CONNECTOR
from pptx.dml.color import RGBColor
from storage_footprint import inventory,storage_notes

def add_storage_capacity_page(slide,exhibit_layout,text,root,brand):
    data=inventory(root)
    rows=[r for r in data if r['map_include']=='yes' and r['gross_capacity_m3']]
    leases=[r for r in data if r['site_id'].startswith('X') and r['lease_capacity_m3']]
    locations=defaultdict(list)
    for r in rows:locations[r['site']].append(r)
    totals={site:sum(float(r['gross_capacity_m3']) for r in entries)/1000 for site,entries in locations.items()}
    order=sorted(totals,key=totals.get,reverse=True)
    assert len(rows)==6 and len(order)==5 and len(leases)==3
    colours={'Vopak':brand.accent_primary,'Bidvest Tank Terminals':RGBColor.from_string('809CC7'),
             'VTTI Burgan Cape Terminal':RGBColor.from_string('BACCE4')}
    s=slide('Compare published storage capacity by location',
        'Vopak; Bidvest; VTTI Burgan Cape; Transnet lease RFPs (5 Oct 2026), pp. 2–3. Checked 6 Oct 2026.',
        storage_notes(root)+'\nMain panel gross stocks; separate lease panel has an enlarged 0–10 thousand m3 axis. '
        'Ladysmith: 8540 m3 petrol/diesel working capacity; excluded intermixture 474 m3; total working 9014 m3. '
        'Standerton: (1350000 + 220000 + 783000)/1000 = 2353 m3; gross/working basis unstated. '
        'Kroonstad: approximately 3300 m3; gross/working basis unstated. Bethlehem/Magdala have no quantified petroleum tank capacity. '
        'Lease assets are not added to operating supply, gross totals or accessibility cost-model origins. '
        'Vopak HTML data-end-number uses cbm, not the alternate displayed barrels. '
        'Primary RFPs retained under external/data/raw/transnet_leasing_20261006/. '
        'https://www.transnet.net/TPL-Leasing-Opportunities')
    exhibit_layout(s,'Storage stocks and lease opportunities | thousand m³',[
        ('Durban leads this evidenced subset',f"Published Vopak and Bidvest gross capacity totals {totals['Durban']:.1f} thousand m³. Mixed products limit the fuel-only comparison."),
        ('Five Transnet lease opportunities','Ladysmith, Standerton and Kroonstad have stated capacities. Bethlehem and Magdala remain unquantified, not zero.'),
        ('Capacity bases must stay visible','Ladysmith shows petrol/diesel working capacity. Kroonstad and Standerton have RFP-stated tank capacities; gross/working basis is unspecified.'),
        ('Lease offers require reactivation','Do not count these tanks as operating supply. Test refurbishment, receipt/dispatch, licensing and lease award. RFP close: 4 Dec 2026.'),
    ])
    x0=2.22;width=4.63
    def axis(maximum,ticks,top,bottom,label_y):
        for v in ticks:
            x=x0+width*v/maximum
            q=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x),Inches(top),Inches(x),Inches(bottom))
            q.line.color.rgb=brand.grey_fill;q.line.width=Pt(.5)
            text(s,str(v),x-.15,label_y,.42,.20,8.5)
    text(s,'Published gross capacity | mixed product scopes',.5,2.37,7.05,.23,10,True)
    axis(850,[0,200,400,600,800],2.86,4.62,2.63)
    for i,site in enumerate(order):
        y=2.92+i*.34
        text(s,site,.5,y,1.65,.24,11,True)
        x=x0
        for r in sorted(locations[site],key=lambda r:r['operator']!='Vopak'):
            w=width*(float(r['gross_capacity_m3'])/1000)/850
            q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(.23))
            q.name=f"Published gross capacity: {r['operator']} {site}: {r['gross_capacity_m3']} m3"
            q.fill.solid();q.fill.fore_color.rgb=colours[r['operator']];q.line.fill.background();x+=w
        text(s,f'{totals[site]:,.1f}',x+.08,y,.62,.24,10.5,True)
    for x,name,operator in [(.5,'Vopak','Vopak'),(2.4,'Bidvest','Bidvest Tank Terminals'),(4.4,'Burgan Cape','VTTI Burgan Cape Terminal')]:
        q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(4.78),Inches(.11),Inches(.11))
        q.fill.solid();q.fill.fore_color.rgb=colours[operator];q.line.fill.background()
        text(s,name,x+.18,4.72,1.7,.23,9)
    text(s,'Transnet lease opportunities | enlarged scale; not operating supply',.5,5.03,7.05,.24,10,True,brand.accent_primary)
    axis(10,[0,2,4,6,8,10],5.57,6.51,5.32)
    for i,r in enumerate(sorted(leases,key=lambda r:float(r['lease_capacity_m3']),reverse=True)):
        y=5.60+i*.29;v=float(r['lease_capacity_m3'])/1000
        text(s,r['site']+('*' if r['site_id']=='X1' else ''),.5,y,1.65,.24,10,True)
        q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x0),Inches(y),Inches(width*v/10),Inches(.20))
        q.name=f"Transnet lease offer: {r['site']}: {r['lease_capacity_m3']} m3; {r['capacity_basis']}"
        q.fill.solid();q.fill.fore_color.rgb=RGBColor.from_string('E3EBF6');q.line.color.rgb=brand.accent_primary;q.line.width=Pt(.8)
        text(s,f'{v:.2f}',x0+width*v/10+.08,y,.62,.23,10,True)
    text(s,'*Ladysmith: petrol/diesel working; excludes 0.474 intermixture. Other lease tank bases unspecified.',.5,6.58,7.05,.25,8)
    text(s,'Unquantified: Bethlehem, Magdala, Sasol depots, Tarlton and Jameson Park. Stock ≠ throughput.',.5,6.86,7.05,.24,8)
    return s
