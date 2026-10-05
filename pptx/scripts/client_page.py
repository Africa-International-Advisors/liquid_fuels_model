"""Client-specific context, distinguishing facts from analytical implications."""
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt


def draw_client(slide,text,table):
    text(slide,'ABOUT VOPAK | Storage and handling infrastructure serving energy and manufacturing',.55,1.82,11.5,.38,16,True)
    rows=[
      '| What matters about the client | Implication for this engagement |',
      '| Business model: storage and handling across oil, gas, chemicals and industrial terminals. [1] | Translate fuel flows into terminal throughput, handling and usable storage needs. |',
      '| Customers: producers, manufacturers, distributors, governments and traders. [1] | Establish whose volumes could use each corridor, access needs and competing options. |',
      '| South Africa: coastal Durban and inland Lesedi connect to the New Multi-Product Pipeline (NMPP). [3] | Assess coastal receipts, inland flows and terminal needs within the national fuel system. |',
      '| Strategy: predictable cash flows, stronger assets and disciplined growth investment. [2] | Test sustained demand, utilisation and commercial access before calling a gap an opportunity. |',
    ]
    for i,label in enumerate(['Receipt','Storage and handling','Onward dispatch','Customer markets']):
        x=.65+i*3.0;cx=x+.86;y=2.42;blue=RGBColor.from_string('0A2373')
        def icon(kind,dx,dy,w,h,filled=False):
            s=slide.shapes.add_shape(kind,Inches(cx+dx),Inches(y+dy),Inches(w),Inches(h));s.fill.solid() if filled else s.fill.background()
            if filled:s.fill.fore_color.rgb=blue
            s.line.color.rgb=blue;s.line.width=Pt(1.3);return s
        if i==0:
            icon(MSO_SHAPE.TRAPEZOID,0,.24,.75,.25).rotation=180
            icon(MSO_SHAPE.RECTANGLE,.18,.04,.35,.2)
            icon(MSO_SHAPE.RECTANGLE,.33,-.02,.12,.08)
        elif i==1:
            for dx in [0,.26,.52]:icon(MSO_SHAPE.CAN,dx,.04,.22,.45)
        elif i==2:
            icon(MSO_SHAPE.RECTANGLE,0,.06,.48,.27);icon(MSO_SHAPE.RECTANGLE,.5,.14,.23,.19)
            for dx in [.12,.55]:icon(MSO_SHAPE.OVAL,dx,.34,.15,.15)
        else:
            icon(MSO_SHAPE.RECTANGLE,0,.2,.72,.29)
            for dx in [.08,.33]:icon(MSO_SHAPE.RECTANGLE,dx,.03,.12,.17)
            for dx in [.12,.36,.58]:icon(MSO_SHAPE.RECTANGLE,dx,.3,.08,.09)
        text(slide,label,x+.1,3.03,2.65,.28,13,True)
        if i<3:
            s=slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,Inches(x+2.2),Inches(2.65),Inches(.48),Inches(.12));s.fill.solid();s.fill.fore_color.rgb=RGBColor.from_string('A0A0A0');s.line.fill.background()
    shape=table(slide,rows,x=.55,y=3.5,height=2.65,widths=[5.8,5.85],size=13)
    for row in shape.table.rows:
        for cell in row.cells:
            cell.margin_top=cell.margin_bottom=Inches(.03)
    text(slide,'This assignment: South Africa outlook | Namibia / Walvis Bay assessment | Priority African market screening. [4]',.55,6.4,11.5,.35,13,True)
    refs=[('[1] Vopak: Services','https://www.vopak.com/who-we-are/services'),('[2] Vopak: Who we are / strategy','https://www.vopak.com/who-we-are'),('[3] Vopak: South Africa expansion','https://www.vopak.com/newsroom/news/vopak-expands-further-south-africa?language_content_entity=en')]
    for x,w,(label,url) in zip([.55,3.45,7.05],[2.8,3.5,4.8],refs):
        shape=text(slide,label,x,6.85,w,.2,9)
        for run in shape.text_frame.paragraphs[0].runs:run.hyperlink.address=url
