"""Translate disclosed client service economics into geographic study questions."""
import json
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE


def draw_client_economics(slide,root,brand,text):
    d=json.loads((root/'story/vopak-h1-2026.json').read_text(encoding='utf-8'))
    text(slide,'Fuel flows matter when they support sustained demand for terminal capacity and services',.55,1.8,11.5,.4,15,True)
    revenue=d['group'][0][1]
    for i,(label,a,b) in enumerate(d['services']):
        x=.55+i*2.95
        text(slide,label,x,2.42,2.8,.32,14,True)
        text(slide,f'EUR {a:.1f}m  |  {a/revenue:.1%}',x,2.85,2.8,.4,19,True,brand.accent_primary)
        text(slide,'H1 2026 consolidated revenue',x,3.34,2.8,.25,9)
    text(slide,'All four categories reconcile to EUR 677.1m; displayed shares total 100.1% because of rounding.',.55,3.62,11.5,.23,10)
    text(slide,'Study implication: connect usable tank capacity and holding time to receipts, dispatch and throughput.',.55,3.83,11.5,.35,13)
    cards=[
        ('South Africa','Assess changing coastal receipts and inland flows across the national system.','Client output: service demand, utilisation pressures and constraints for existing and potential terminals.'),
        ('Walvis Bay / Namibia','Test the customer volumes and corridors that could sustain a storage and handling proposition.','Client output: accessible demand, competing facilities, usable capacity and commercial conditions.'),
        ('Priority African markets','Screen for sustained fuel flows, customer needs and commercially accessible infrastructure.','Client output: markets to prioritise for detailed asset and customer assessment.'),
    ]
    for i,(heading,question,output) in enumerate(cards):
        x=.55+i*3.95
        box=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(4.46),Inches(3.65),Inches(1.94))
        box.fill.background();box.line.color.rgb=brand.grey_fill;box.line.width=Pt(1)
        text(slide,heading,x+.12,4.58,3.4,.32,16,True)
        text(slide,question,x+.12,5.03,3.4,.63,12)
        text(slide,output,x+.12,5.74,3.4,.55,11)
    text(slide,'Commercial test: sustained customer volumes, compatible capacity, handling capability, access and contract terms.',.55,6.72,11.5,.32,12,True)
    credit=text(slide,'Sources: Vopak Half Year Report 2026, p. 39 (all service revenues); AIA proposal, pp. 7–8. Study implications are our framing.',.5,7.17,10.1,.2,8)
    for p in credit.text_frame.paragraphs:
        for r in p.runs:r.hyperlink.address=d['source']+'#page=39'
