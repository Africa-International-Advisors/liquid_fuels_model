"""Introduce all workstreams before the model architecture uses their labels."""
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches


def draw_workstreams(slide,brand,text,table):
    band=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(.55),Inches(1.87),Inches(11.65),Inches(.55))
    band.fill.solid();band.fill.fore_color.rgb=brand.accent_primary;band.line.fill.background()
    text(slide,'WS0  Governance: priorities, integration, ownership, review and acceptance',.7,1.98,11.3,.3,15,True,brand.white)
    rows=[
      '| Workstream | Role in the integrated model |',
      '| WS1  Data validation | Source inputs, reconcile history and record evidence quality and gaps |',
      '| WS2  Fuel model | Develop demand, production, imports and the scenario framework |',
      '| WS3  Reporting and delivery | Partner owns the storyline; analyst develops supporting evidence and exhibits |',
      '| WS4  Analyst enablement | Establish a documented working process for repeatable runs and refreshes |',
      '| WS5  Infrastructure and logistics | Model ports, airports, rail, roads, pipelines, storage and power dependencies |',
    ]
    table(slide,rows,x=.55,y=2.65,height=3.15,widths=[3.75,7.9],size=15)
    text(slide,'Integration across WS2 / WS5 / WS3: Nigel leads; Manish builds and reconciles; Henry reviews.',.55,6.02,11.5,.45,13,True)
    text(slide,'Check shared products, geography, periods and units; conserve volumes; avoid double counting; trace every exhibit to its run.',.55,6.57,11.5,.42,12)
