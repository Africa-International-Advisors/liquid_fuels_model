"""Split-colour purpose and boundaries page using Vopak branding."""
from pptx.util import Inches
from pptx.enum.shapes import MSO_SHAPE


def draw_about(slide,prs,brand,text):
    half=prs.slide_width/2
    for x,color in [(0,brand.accent_primary),(half,brand.white)]:
        s=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,int(x),0,int(half),prs.slide_height)
        s.fill.solid();s.fill.fore_color.rgb=color;s.line.fill.background()
    for x,color,eyebrow,title,items in [
        (.6,brand.white,'ABOUT THIS DOCUMENT','Align scope and delivery expectations',[
            ('A shared starting point','Align the team on the project question, required outputs and six-week priorities.'),
            ('A model and infrastructure build brief','Connect the fuel model with transport, terminal and storage capacity.'),
            ('An evidence-led working discussion','Show inherited data, Python results, discrepancies and the checks still needed.'),
            ('A basis for delivery decisions','Agree the first baseline, workstream interfaces, review gates and responsibilities.')]),
        (6.93,brand.ink,'PURPOSE AND BOUNDARIES','What this document is not',[
            ('A validated market forecast','Current results include provisional assumptions and unresolved differences.'),
            ('An investment recommendation','An import gap alone does not establish an accessible storage opportunity.'),
            ('A completed infrastructure model','Maps show evidence and connectivity; usable capacity and access still need validation.'),
            ('A commitment to equal depth everywhere','Regional screening and detailed country modelling have different evidence requirements.')])]:
        text(slide,eyebrow,x,.52,5.05,.3,11,True,color)
        text(slide,title,x,1.13,5.1,1.0,27,True,color)
        for i,(heading,copy) in enumerate(items):
            y=2.2+i*1.04
            text(slide,heading,x,y,5.0,.35,17,True,color)
            text(slide,copy,x,y+.42,5.0,.6,15,False,color)
    text(slide,'Internal working discussion | 2 October 2026',.6,7.01,5.05,.25,10,False,brand.white)
