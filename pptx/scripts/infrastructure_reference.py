"""Proposed end-to-end infrastructure calculation and review contract."""
from pptx.util import Inches,Pt
from pptx.enum.shapes import MSO_SHAPE,MSO_CONNECTOR

def draw_infrastructure_reference(slide,text,brand,cfg):
    text(slide,'Target architecture | inputs and source material exist; allocation and constraint engine still to build',.55,1.82,11.5,.4,15)
    steps=[
      ('01 Govern inputs','Asset IDs, source, unit, vintage, owner, status and missing-data flags.'),
      ('02 Build the network','Ports, production, tanks and demand nodes; pipeline, road and rail connections.'),
      ('03 Allocate fuel flows','Link WS2 demand, production and available imports to origins and destinations.'),
      ('04 Apply constraints','Product compatibility, shared capacity, access, reliability, receipt and dispatch.'),
      ('05 Test tank requirements','Working stock, stock-cover days, usable capacity and commitments; keep stock separate from flow.'),
      ('06 Save and report','Feasible, unmet and unassessed volumes; bottlenecks, storage gaps and run provenance.'),
    ]
    for i,(head,body) in enumerate(steps):
        row,col=divmod(i,3);x=.55+col*4.0;y=2.55+row*1.7
        box=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(3.7),Inches(1.42));box.fill.background();box.line.color.rgb=cfg.DIVIDER_HEADER;box.line.width=Pt(.5)
        text(slide,head,x+.12,y+.12,3.44,.37,15,True);text(slide,body,x+.12,y+.58,3.44,.72,12)
        if col<2:
            a=slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,Inches(x+3.74),Inches(y+.62),Inches(.22),Inches(.16));a.fill.solid();a.fill.fore_color.rgb=brand.accent_primary;a.line.fill.background()
    # Wrap the sequence down from the end of the top row to the next row.
    for a,b in [((12.22,3.26),(12.22,4.08)),((12.22,4.08),(.4,4.08)),((.4,4.08),(.4,4.95)),((.4,4.95),(.55,4.95))]:
        line=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(a[0]),Inches(a[1]),Inches(b[0]),Inches(b[1]));line.line.color.rgb=brand.accent_primary;line.line.width=Pt(.8)
    text(slide,'Checks across the chain: node conservation • shared-capacity accounting • manual corridor tie-out • scenario response',.55,6.2,11.5,.4,13,True)
    text(slide,'Power and gas dependencies inform availability; airports and power stations receive fuel-demand allocations. Commercial interpretation remains in WS3.',.55,6.7,11.5,.38,11)
