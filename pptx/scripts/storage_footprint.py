"""Dated presentation evidence, not an operational-capacity or routing input."""
import csv
from pptx.enum.shapes import MSO_SHAPE
from exhibit_typography import MAP_CALLOUT

def inventory(root):
    with (root/'story/storage_operator_inventory_2026_10_06.csv').open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def storage_notes(root):
    return ('Storage footprint is a public-evidence starting inventory, not a complete census. '
            'Coordinates are approximate except Tarlton and five Transnet RFP briefing coordinates. Lease symbols indicate offers, not operating assets. Magdala RFP location narrative is inconsistent; verify independently. Symbols do not encode capacity. '
            'Lesedi and Transnet Jameson Park are distinct assets represented by the same approximate area; '
            'the national map cannot separate their actual boundaries. '
            'Capacity is a stock, not throughput. Mixed-product tanks cannot establish petrol/diesel share.\n'+
            '\n'.join(f"{r['site_id']} {r['operator']} / {r['site']}: {r['source_url']} | {r['source_date']} | "
                       f"{r['operating_evidence']} | {r['access_flag']} | owner {r['owner']} | next: {r['next_action']}"
                       for r in inventory(root)))

def draw_storage_footprint(m,text,line,marker,root,brand,inland_position=(5.15,2.60)):
    for r in inventory(root):
        if r['map_include']!='yes' or r['operator']=='Vopak' or r['site_id'].startswith('X'):continue
        x,y=m.xy(float(r['longitude']),float(r['latitude']))
        marker(m.s,x,y,.055,brand.accent_primary,MSO_SHAPE.HEXAGON,hollow=True)
    # Grouped callouts keep tightly clustered inland assets legible at national scale.
    callouts=[
        (31.03,-29.88,'Durban\nVopak / Bidvest',5.47,4.55,1.65,.55),
        (32.06,-28.8,'Richards Bay\nBidvest',5.63,3.95,1.7,.55),
        (18.43,-33.91,'Cape Town\nBurgan Cape',.62,5.18,1.65,.54),
        (28.2,-26.2,'Lesedi / inland storage\nVopak / Bidvest\nSasol / Transnet',*inland_position,2.20,.76),
    ]
    for lon,lat,label,x,y,w,h in callouts:
        anchor=m.xy(lon,lat)
        line(m.s,anchor,(x,y+h/2),brand.accent_primary,.65)
        q=text(m.s,label,x,y,w,h,MAP_CALLOUT,True,brand.accent_primary)
        q.fill.solid();q.fill.fore_color.rgb=brand.white


def draw_transnet_leases(m,text,line,marker,root,brand,box=(.65,4.04)):
    """Separate lease-offer layer; exact RFP points, displaced identifiers at national scale."""
    before=len(m.s.shapes)
    offsets={'X1':(.08,.03),'X2':(.08,-.12),'X3':(-.40,-.12),'X4':(-.15,.07),'X5':(-.22,-.16)}
    for r in inventory(root):
        if not r['site_id'].startswith('X'):continue
        x,y=m.xy(float(r['longitude']),float(r['latitude']))
        marker(m.s,x,y,.040,brand.ink,MSO_SHAPE.ISOSCELES_TRIANGLE,hollow=True)
        dx,dy=offsets[r['site_id']]
        line(m.s,(x,y),(x+dx+.07,y+dy+.07),brand.ink,.55)
        q=text(m.s,r['site_id'][1:],x+dx,y+dy,.15,.17,8,True,brand.ink)
        q.fill.solid();q.fill.fore_color.rgb=brand.white
    x,y=box
    q=text(m.s,'   Transnet lease offers\n1 Ladysmith | 2 Standerton\n3 Kroonstad | 4 Bethlehem\n5 Magdala*',x,y,2.22,1.02,MAP_CALLOUT,True,brand.ink)
    q.fill.solid();q.fill.fore_color.rgb=brand.white
    marker(m.s,x+.06,y+.075,.040,brand.ink,MSO_SHAPE.ISOSCELES_TRIANGLE,hollow=True)
    for q in list(m.s.shapes)[before:]:q.name='Transnet lease overlay: '+q.name
