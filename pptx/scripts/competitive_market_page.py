"""Competitive footprint and contestability exhibit using dated public evidence."""
import csv
from pptx.util import Pt,Inches
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

def compact_table(table,s,rows,x,y,widths,height,size):
    q=table(s,rows,x,y,widths,height,size)
    for row in q.table.rows:
        for cell in row.cells:
            cell.margin_top=cell.margin_bottom=Pt(2)
    return q

def add_competitive_page(slide,exhibit_layout,Map,text,table,root,brand,regional):
    with (root/'story/competitive_market_evidence_2026_10_06.csv').open(encoding='utf-8-sig',newline='') as f:
        evidence=list(csv.DictReader(f))
    notes='Public evidence reviewed 6 October 2026. Competitor list is a starting inventory, not exhaustive. '
    notes+='Actual petrol/diesel throughput share remains unknown. Capacity is a stock and may include chemicals/gases. '
    notes+='Bidvest site capacities: Durban 439306 + Richards Bay 483797 + Isando 32500 = 955603 m3; homepage instead states 868000 m3. Reconcile dates and products. '
    notes+='Burgan Cape Terminal publishes 122000 m3 and a 2025-2026 uncommitted-capacity download; confirm the current period before treating it as available. '
    notes+='Market volume illustration uses the authored regional CSV, not public company volumes. '
    notes+='Current unique demand served / matched catchment demand; additional candidate / matched catchment demand. '
    notes+='National, catchment, eligible-throughput and capacity denominators must not be interchanged. '
    notes+='\n'.join(f"[{r['source_id']}] {r['operator']}: {r['source_url']} | {r['source_date']} | {r['limitation']}" for r in evidence)
    s=slide('Define Vopak’s current share and the market it can contest',
        'Operator sites/reports and NERSA [1–7], checked 6 Oct 2026; site inventory in slide 2 notes; shares illustrative.',notes)
    exhibit_layout(s,'Competitive footprint and share | petrol/diesel focus',[
        ('Actual Vopak share is not established','Need unique petrol/diesel deliveries divided by matched catchment demand, for the same period.'),
        ('Contestability requires customer access','Test cost, compatible capacity, contracts and switching. Other operators’ volume is not automatically available.'),
        ('Storage has different commercial roles','Bidvest and Burgan offer terminal services; Sasol depots and Transnet accumulation need separate access tests.'),
        ('Capacity share is a separate measure','Exclude chemicals, gas, jet and unusable tanks. Reconcile dates; do not convert storage capacity into fuel throughput.'),
    ])
    rows=[['Operator / public source','Locations / role','Key evidence gap'],
        ['Vopak [1]','Durban; Lesedi\nStorage and handling','Actual unique fuel deliveries\nand usable fuel capacity'],
        ['Bidvest [2]','Durban; Richards Bay; Isando\nMixed-product terminals','Petrol/diesel scope; conflicting\ntotals 955,603 vs 868,000 m³'],
        ['Sasol [6]','Alrode; Pretoria West; Waltloo;\nSasolburg blending/logistics','Current access; linked 2025/26\nnotice ends March 2026'],
        ['Transnet [7]','Tarlton bulk storage;\nJameson Park accumulation','Usable tanks / third-party terms;\nnot all depots are operating'],
        ['Burgan Cape [3]','Cape Town petrol/diesel terminal\nPublished capacity 122,000 m³','Current available capacity;\nCape overlap unassessed']]
    q=compact_table(table,s,rows,.5,2.38,[1.35,2.90,2.80],2.55,10.5)
    for cell in q.table.rows[len(q.table.rows)-1].cells:
        for p in cell.text_frame.paragraphs:p.font.bold=False
    text(s,'Shell [4] and NERSA [5]: extend the inventory through site notices and allocation mechanisms.',.5,5.03,7.05,.30,9)
    fields=['demand_bn_l','current_unique_vopak_bn_l','additional_candidate_bn_l']
    totals={k:sum(float(r[k]) for r in regional if r['region'] in ['Eastern coastal','Inland']) for k in fields}
    demand=totals['demand_bn_l'];current=totals['current_unique_vopak_bn_l'];additional=totals['additional_candidate_bn_l']
    rows=[['Illustrative catchment','Current share','Additional candidate'],
          ['Eastern/coastal',f"{sum(float(r['current_unique_vopak_bn_l']) for r in regional if r['region']=='Eastern coastal')/sum(float(r['demand_bn_l']) for r in regional if r['region']=='Eastern coastal'):.1%}",f"{sum(float(r['additional_candidate_bn_l']) for r in regional if r['region']=='Eastern coastal')/sum(float(r['demand_bn_l']) for r in regional if r['region']=='Eastern coastal')*100:.1f} pp"],
          ['Inland',f"{sum(float(r['current_unique_vopak_bn_l']) for r in regional if r['region']=='Inland')/sum(float(r['demand_bn_l']) for r in regional if r['region']=='Inland'):.1%}",f"{sum(float(r['additional_candidate_bn_l']) for r in regional if r['region']=='Inland')/sum(float(r['demand_bn_l']) for r in regional if r['region']=='Inland')*100:.1f} pp"],
          ['Combined example',f'{current/demand:.1%}',f'{additional/demand*100:.1f} pp']]
    text(s,'Illustrative share of each regional market | % of demand',.5,5.36,7.05,.22,11,True)
    colours=[brand.accent_primary,RGBColor.from_string('809CC7'),RGBColor.from_string('E5E5E5')]
    for i,region in enumerate(['Eastern coastal','Inland']):
        data=[r for r in regional if r['region']==region]
        d=sum(float(r['demand_bn_l']) for r in data)
        c=sum(float(r['current_unique_vopak_bn_l']) for r in data)/d
        a=sum(float(r['additional_candidate_bn_l']) for r in data)/d
        y=5.68+i*.31
        text(s,'Eastern coast' if i==0 else region,.5,y-.02,1.65,.22,10)
        x=2.2
        for j,value in enumerate([c,a,1-c-a]):
            w=4.85*value
            q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(.23))
            q.name=f'Illustrative {region} share segment {j+1}: {value:.3%}'
            q.fill.solid();q.fill.fore_color.rgb=colours[j];q.line.fill.background()
            text(s,f'{value:.1%}',x,y+.02,w,.18,9,True,brand.white if j==0 else brand.ink,PP_ALIGN.CENTER)
            x+=w
    for i,region in enumerate(['Western coast','Other / NC']):
        y=6.30+i*.23
        text(s,region,.5,y,1.65,.20,9)
        q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(2.2),Inches(y),Inches(4.85),Inches(.18))
        q.fill.solid();q.fill.fore_color.rgb=brand.grey_fill;q.line.fill.background()
        text(s,'Unassessed - no share estimate',2.2,y,4.85,.18,8.5,False,brand.ink,PP_ALIGN.CENTER)
    for x,label,colour in zip([.5,2.3,4.95],['Current Vopak','Additional candidate','Outside envelope'],colours):
        q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(6.82),Inches(.11),Inches(.11))
        q.fill.solid();q.fill.fore_color.rgb=colour;q.line.fill.background()
        text(s,label,x+.15,6.78,2.45,.18,8)
    s.notes_slide.notes_text_frame.text += ('\nStacked bars are authored illustration only; not actual market share. '
        'Eastern coast current 22.2%, additional candidate 33.3%, outside envelope 44.4%; '
        'inland 20%, 40%, 40%. Candidate volume is conditional, not forecast capture. '
        'Regions use the working province definitions on slide 2, but the bar denominators '
        'remain the illustrative 4.5/10.0 bn L, not observed 2022 sales. Western/other unassessed.')
    for i,r in enumerate(evidence):
        label=f"[{r['source_id']}] "+['Vopak','Bidvest','Burgan','Shell','NERSA','Sasol','Transnet'][i]
        q=text(s,label,.5+i*.98,6.96,.97,.17,7.5,color=brand.accent_primary)
        for p in q.text_frame.paragraphs:
            for run in p.runs:run.hyperlink.address=r['source_url']
    return s
