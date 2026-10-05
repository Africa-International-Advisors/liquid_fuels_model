"""Proposed infrastructure workstream, explicitly separate from current engine."""
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE


def draw_infrastructure(slide,index,brand,cfg,text,table):
    if index==29:
        text(slide,'WS5 | Liquid-fuel transport demand: allocate petrol, diesel and jet balances to feasible routes',.55,1.83,11.5,.5,17,True)
        blocks=[('01  Fuel and markets','WS2 petrol / diesel / jet\nProduction + feasible imports\nMarket / product / period'),('02  Asset network','Ports / airports, rail / road\nPipelines + power lines\nPower stations + access'),('03  Terminals + tanks','Receipt / dispatch limits\nUsable storage by product\nStock cover + commitments'),('04  Decision outputs','Unmet volumes + bottlenecks\nRequired vs usable storage\nClient-accessible opportunity')]
        for i,(heading,copy) in enumerate(blocks):
            x=.55+i*2.94
            s=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(2.7),Inches(2.72),Inches(2.18));s.fill.solid();s.fill.fore_color.rgb=brand.white;s.line.color.rgb=cfg.DIVIDER_HEADER;s.line.width=Pt(.5)
            text(slide,heading,x+.1,2.87,2.52,.55,15,True);text(slide,copy,x+.1,3.56,2.52,1.12,13)
            if i<3:
                a=slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,Inches(x+2.74),Inches(3.7),Inches(.17),Inches(.13));a.fill.solid();a.fill.fore_color.rgb=brand.accent_primary;a.line.fill.background()
        text(slide,'Transport and handling = flow (m3/year)     |     Storage = stock (m3)',.55,5.13,11.5,.4,18,True)
        text(slide,'Required working storage = annual throughput / days in year x stock-cover days.\nPower lines and power stations inform asset availability and fuel demand; keep MW / MWh separate from fuel volumes.',.55,5.66,11.5,.7,15)
        text(slide,'First release: South Africa inventory + one evidenced Durban-to-Gauteng route. Unknown capacity remains unassessed.',.55,6.6,11.5,.35,13,True)
    else:
        text(slide,'Common acceptance criteria | Manish prepares evidence; Nigel reviews methodology; Henry challenges readiness',.55,1.83,11.5,.55,15,True)
        rows=['| Review gate | Demand and supply | Infrastructure |',
              '| 1 Establish the baseline | Source inputs; reconcile Excel–Python differences; document production and imports | Source asset inventory; identify capacity, connectivity and access gaps |',
              '| 2 Demonstrate calculations | Trace demand drivers and production calculations; check balances | Demonstrate one corridor; check flows, handling limits and storage requirements |',
              '| 3 Test scenarios and outputs | Check scenario responses, import requirements and reproducible outputs | Check feasible flows, bottlenecks and storage needs under those scenarios |']
        table(slide,rows,x=.55,y=2.62,height=3.6,widths=[2.4,4.6,4.65],size=16)
        text(slide,'Record checks, unresolved gaps and review findings at every gate. A passing run is not validation or approval.',.55,6.45,11.5,.45,13,True)
        text(slide,'Timing sits on the Gantt. These are development review gates; formal-use requirements remain in GATE_CHECKLIST.md.',.55,6.91,11.5,.2,10)
