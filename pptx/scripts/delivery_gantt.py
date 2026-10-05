"""Presentation-only integrated workplan; proposed durations, not commitments."""
from pptx.util import Inches,Pt
from pptx.enum.shapes import MSO_SHAPE

def draw_gantt(slide,text,brand,cfg):
    text(slide,'Proposed six-week programme | fuel model, infrastructure and client storyline progress together',.55,1.8,11.5,.35,15)
    x0=5.5;cw=1.08;y0=2.52;rh=.48
    text(slide,'Activity / workstream',.65,2.23,4.8,.3,15,True)
    for w in range(6):text(slide,f'W{w+1}',x0+w*cw+.25,2.23,.7,.3,14,True)
    tasks=[
      ('WS1/2  Baseline and Excel reconciliation',0,2),
      ('WS2  Drivers, imports and H/M/L scenarios',1,4),
      ('WS5  Asset inventory and usable capacity',0,3),
      ('WS5  First route, handling and tank limits',1,4),
      ('WS2/5  Integrated flows and sensitivities',3,5),
      ('WS3  Walvis Bay, competitors, market screening',0,5),
      ('WS3  Partner-led storyline and evidence',0,6),
      ('WS0/3  Review and board pack / handover',4,6),
    ]
    for i,(label,start,end) in enumerate(tasks):
        y=y0+i*rh;text(slide,label,.65,y+.07,4.7,.31,13)
        for w in range(6):
            b=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x0+w*cw),Inches(y+.07),Inches(cw-.08),Inches(.3))
            b.fill.solid();b.fill.fore_color.rgb=brand.accent_primary if start<=w<end else brand.grey_fill;b.line.fill.background()
    text(slide,'W1 gate: reproducible baseline + sourced infrastructure inventory + first corridor agreed',.65,6.5,11.4,.3,13,True)
    text(slide,'W3: first route calculation  |  W4: integrated draft  |  W5: review findings  |  W6: board pack',.65,6.87,11.4,.24,11)
