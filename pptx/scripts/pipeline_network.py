"""Sourced schematic liquid-pipeline connectivity; no implied geographic precision."""
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.util import Inches, Pt


def draw_pipeline_network(slide,brand,cfg,text):
    text(slide,'Liquid-pipeline connections | network schematic, not geographic routing',.55,1.81,11.5,.4,17)
    nodes={'Durban':(.65,5.56),'Jameson Park':(3.25,4.13),'Secunda':(3.25,2.55),'Sasolburg / NATREF':(.65,4.13),'Klerksdorp':(.65,2.55),'Kendal':(5.85,2.55),'Waltloo':(8.45,2.55),'Alrode':(5.85,4.13),'Langlaagte':(8.45,4.13),'OR Tambo':(5.85,5.56)}
    def line(a,b,kind='product'):
        x,y=nodes[a];xx,yy=nodes[b]
        s=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x+1),Inches(y+.24),Inches(xx+1),Inches(yy+.24))
        s.line.color.rgb=brand.ink if kind=='crude' else cfg.MAP_REGION_COLOURS['SADC excluding SACU'] if kind=='jet' else brand.accent_primary;s.line.width=Pt(1.5)
        if kind=='crude':s.line.dash_style=MSO_LINE_DASH_STYLE.DASH
        if kind=='jet':s.line.dash_style=MSO_LINE_DASH_STYLE.ROUND_DOT
    for a,b in [('Durban','Jameson Park'),('Sasolburg / NATREF','Klerksdorp'),('Sasolburg / NATREF','Jameson Park'),('Secunda','Kendal'),('Secunda','Jameson Park'),('Jameson Park','Kendal'),('Jameson Park','Alrode'),('Alrode','Langlaagte'),('Kendal','Waltloo')]:line(a,b)
    line('Durban','Sasolburg / NATREF','crude');line('Sasolburg / NATREF','OR Tambo','jet')
    for name,(x,y) in nodes.items():
        s=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(2.0),Inches(.48));s.fill.solid();s.fill.fore_color.rgb=brand.white;s.line.color.rgb=cfg.DIVIDER_HEADER;s.line.width=Pt(.5)
        text(slide,name,x+.06,y+.08,1.9,.3,12,True)
    text(slide,'Secunda - Kendal includes parallel 12-inch and 20-inch lines.',8.35,3.2,3.7,.55,10)
    text(slide,'Durban - Jameson Park: NMPP trunk',.65,6.16,4.2,.28,11)
    text(slide,'Further documented delivery points',8.35,5.05,3.75,.36,14,True)
    text(slide,'Witbank, Tarlton, Rustenburg; OR Tambo also served ex-Jameson Park. Detailed branch routing to reconcile.',8.35,5.52,3.7,.77,12)
    text(slide,'Western Cape: Saldanha - Astron refinery crude pipeline',.55,6.56,7.3,.26,12,True)
    for x,label,color,dash in [(.55,'Products',brand.accent_primary,None),(2.7,'Crude',brand.ink,MSO_LINE_DASH_STYLE.DASH),(4.65,'Jet',cfg.MAP_REGION_COLOURS['SADC excluding SACU'],MSO_LINE_DASH_STYLE.ROUND_DOT)]:
        sample=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x),Inches(6.96),Inches(x+.5),Inches(6.96))
        sample.line.color.rgb=color;sample.line.width=Pt(1.5)
        if dash:sample.line.dash_style=dash
        text(slide,label,x+.6,6.85,1.4,.2,10)
    text(slide,'Gas: see ROMPCO / Sasol / Lilly page.',6.6,6.85,5.3,.2,10)
