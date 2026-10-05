"""Dated presentation evidence, not an operational-capacity or routing input."""
import csv
from pptx.enum.shapes import MSO_SHAPE

def inventory(root):
    with (root/'story/storage_operator_inventory_2026_10_06.csv').open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def storage_notes(root):
    return ('Storage footprint is a public-evidence starting inventory, not a complete census. '
            'Coordinates are approximate except Tarlton tender coordinates. Symbols do not encode capacity. '
            'Lesedi and Transnet Jameson Park are distinct assets represented by the same approximate area; '
            'the national map cannot separate their actual boundaries. '
            'Capacity is a stock, not throughput. Mixed-product tanks cannot establish petrol/diesel share.\n'+
            '\n'.join(f"{r['site_id']} {r['operator']} / {r['site']}: {r['source_url']} | {r['source_date']} | "
                       f"{r['operating_evidence']} | {r['access_flag']} | owner {r['owner']} | next: {r['next_action']}"
                       for r in inventory(root)))

def draw_storage_footprint(m,text,line,marker,root,brand,inland_position=(5.15,2.60)):
    for r in inventory(root):
        if r['map_include']!='yes' or r['operator']=='Vopak':continue
        x,y=m.xy(float(r['longitude']),float(r['latitude']))
        marker(m.s,x,y,.055,brand.accent_primary,MSO_SHAPE.HEXAGON,hollow=True)
    # Grouped callouts keep tightly clustered inland assets legible at national scale.
    callouts=[
        (31.03,-29.88,'Durban\nVopak / Bidvest',5.47,4.55,1.65,.45),
        (32.06,-28.8,'Richards Bay\nBidvest',5.63,3.95,1.7,.45),
        (18.43,-33.91,'Cape Town\nBurgan Cape',.62,5.00,1.42,.44),
        (28.2,-26.2,'Lesedi / inland storage\nVopak / Bidvest\nSasol / Transnet',*inland_position,2.05,.66),
    ]
    for lon,lat,label,x,y,w,h in callouts:
        anchor=m.xy(lon,lat)
        line(m.s,anchor,(x,y+h/2),brand.accent_primary,.65)
        q=text(m.s,label,x,y,w,h,10,True,brand.accent_primary)
        q.fill.solid();q.fill.fore_color.rgb=brand.white
