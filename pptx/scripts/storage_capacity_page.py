"""One shared-scale storage comparison, with lease status and capacity basis explicit."""
from collections import defaultdict
from pptx.util import Inches,Pt
from pptx.enum.shapes import MSO_SHAPE,MSO_CONNECTOR
from pptx.dml.color import RGBColor
from storage_footprint import inventory,storage_notes
from exhibit_typography import CHART_LABEL, CHART_SECONDARY, LEGEND


def add_storage_capacity_page(slide,exhibit_layout,text,root,brand):
    data=inventory(root)
    gross=[r for r in data if r['map_include']=='yes' and r['gross_capacity_m3']]
    leases=[r for r in data if r['site_id'].startswith('X') and r['lease_capacity_m3']]
    locations=defaultdict(list)
    for r in gross+leases: locations[r['site']].append(r)
    def capacity(r):return float(r['lease_capacity_m3'] or r['gross_capacity_m3'])/1000
    totals={site:sum(capacity(r) for r in rows) for site,rows in locations.items()}
    order=sorted(totals,key=totals.get,reverse=True)
    assert len(gross)==6 and len(leases)==3 and len(order)==8
    colours={'Vopak':brand.accent_primary,'Bidvest Tank Terminals':RGBColor.from_string('809CC7'),
             'VTTI Burgan Cape Terminal':RGBColor.from_string('BACCE4'),'Transnet Pipelines':RGBColor.from_string('E3EBF6')}
    notes=(storage_notes(root)+'\nAll eight locations use one linear axis, 0-850 thousand m3; no enlarged inset, '
           'axis break or minimum visual bar width. Location/value labels all use 12pt; ticks and legend 11pt. '
           'Gross stocks and RFP-stated lease tanks are not like-for-like usable operating capacity; no national total is inferred. '
           'Ladysmith: 8540 m3 petrol/diesel working, excluding 474 m3 intermixture; total working 9014 m3. '
           'Standerton: (1350000+220000+783000)/1000=2353 m3, basis unspecified. Kroonstad: approximately 3300 m3, basis unspecified. '
           'Bethlehem/Magdala petroleum storage is unquantified. Lease offers are excluded from operating supply and cost-model origins. '
           'Primary RFPs retained under external/data/raw/transnet_leasing_20261006/. '
           'https://www.transnet.net/TPL-Leasing-Opportunities')
    s=slide('Compare published storage capacity by location',
            'Vopak; Bidvest; VTTI Burgan Cape; Transnet lease RFPs (5 Oct 2026), pp. 2-3. Checked 6 Oct 2026.',notes)
    exhibit_layout(s,'Published storage by location | thousand m³; mixed capacity bases',[
        ('Durban leads this evidenced subset',f"Published Vopak and Bidvest gross capacity totals {totals['Durban']:.1f} thousand m³. Mixed products limit the fuel-only comparison."),
        ('Transnet tanks are much smaller','Lease tankage: Ladysmith 8.54, Kroonstad 3.30, Standerton 2.35 thousand m³. Bethlehem and Magdala remain unquantified.'),
        ('Capacity bases must stay visible','Gross stocks elsewhere; Ladysmith* uses petrol/diesel working capacity. Kroonstad/Standerton basis is unspecified.'),
        ('Lease offers require reactivation','Do not count these tanks as operating supply. Test refurbishment, receipt/dispatch, licensing and lease award. RFP close: 4 Dec 2026.'),
    ])
    x0=2.22;width=4.63;maximum=850
    text(s,'One shared scale for every location',.5,2.38,7.05,.27,12,True,brand.accent_primary)
    for v in [0,200,400,600,800]:
        x=x0+width*v/maximum
        q=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x),Inches(2.97),Inches(x),Inches(6.00))
        q.line.color.rgb=brand.grey_fill;q.line.width=Pt(.5)
        text(s,str(v),x-.15,2.70,.45,.24,CHART_SECONDARY)
    for i,site in enumerate(order):
        y=3.04+i*.38
        label=site+('*' if site=='Ladysmith' else '')
        q=text(s,label,.5,y,1.65,.29,CHART_LABEL,True);q.name='Storage location label: '+site
        x=x0
        for r in sorted(locations[site],key=lambda r:r['operator']!='Vopak'):
            w=width*capacity(r)/maximum
            q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y+.01),Inches(w),Inches(.27))
            lease=bool(r['lease_capacity_m3'])
            q.name=f"{'Lease offer' if lease else 'Published gross'} capacity: {r['operator']} {site}: {capacity(r)*1000} m3; shared scale"
            q.fill.solid();q.fill.fore_color.rgb=colours[r['operator']]
            if lease:q.line.color.rgb=brand.accent_primary;q.line.width=Pt(.8)
            else:q.line.fill.background()
            x+=w
        q=text(s,f'{totals[site]:,.2f}',x+.09,y,.72,.29,CHART_LABEL,True)
        q.name='Storage value label: '+site
    for x,name,operator in [(.5,'Vopak','Vopak'),(2.00,'Bidvest','Bidvest Tank Terminals'),(3.48,'Burgan Cape','VTTI Burgan Cape Terminal'),(5.35,'Transnet (lease)','Transnet Pipelines')]:
        q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(6.19),Inches(.13),Inches(.13))
        q.fill.solid();q.fill.fore_color.rgb=colours[operator]
        if operator=='Transnet Pipelines':q.line.color.rgb=brand.accent_primary;q.line.width=Pt(.8)
        else:q.line.fill.background()
        text(s,name,x+.19,6.14,1.98,.26,LEGEND)
    text(s,'Small lease bars reflect smaller tank volumes; they are not operating supply.',.5,6.53,7.05,.30,11,True,brand.accent_primary)
    text(s,'*Ladysmith excludes 0.474 intermixture. Unquantified: Bethlehem, Magdala, Sasol, Tarlton, Jameson Park.',.5,6.91,7.05,.22,9)
    return s
