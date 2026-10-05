"""Draw accounting bridges from the existing reconciliation report."""
from pptx.util import Inches,Pt
from pptx.enum.shapes import MSO_SHAPE,MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN

def draw_waterfalls(slide,text,brand,cfg,data):
    text(slide,'2024 | billion litres | Excel recorded total → reconciliation components → Python total',.55,1.8,11.5,.4,14)
    labels={
     'petrol':['Excel\nrecorded','Fleet /\ncoverage','Use per\nvehicle','Python'],
     'diesel':['Excel\nrecorded','Power\nbasis','Industry\nanchor','Agri.\nanchor','Road vs\nrest','Python'],
     'jet':['Excel\nrecorded','Regression /\nrecorded','Translation\n(no gap)','Python']}
    notes={
     'petrol':'Fewer vehicles: −6.31 bn L.\nHigher use per vehicle: +5.19 bn L.\nCheck fleet coverage, mileage and economy.',
     'diesel':'Power and sector anchors increase demand.\nRoad/non-power definitions partly offset this.\nValidate dispatch and possible overlap.',
     'jet':'Python matches Excel’s calculated demand.\nThe gap is against recorded demand.\nReview regression fit and fuel definitions.'}
    def line(a,b,colour,width=.5):
        s=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(a[0]),Inches(a[1]),Inches(b[0]),Inches(b[1]));s.line.color.rgb=colour;s.line.width=Pt(width)
    for i,key in enumerate(['petrol','diesel','jet']):
        x=.55+i*4.0;r=data[key];start=r['observed']/1e9;finish=r['python']/1e9
        changes=[v/1e9 for v in r['effects'].values()]
        amounts=[start];current=start
        for v in changes:current+=v;amounts.append(current)
        assert abs(current-finish)<1e-6
        maximum=max(amounts)*1.16
        text(slide,key.title(),x,2.38,3.7,.3,19,True)
        text(slide,f'Net difference: {finish-start:+.2f} bn L',x,2.81,3.7,.3,15,True)
        top=3.4;bottom=5.2;height=bottom-top
        def yy(v):return bottom-v/maximum*height
        line((x+.05,bottom),(x+3.72,bottom),cfg.DIVIDER_HEADER)
        entries=[(0,start,start)];current=start
        for v in changes:entries.append((current,current+v,v));current+=v
        entries.append((0,finish,finish))
        step=3.68/len(entries);bw=min(.48,step*.7)
        for j,(a,b,v) in enumerate(entries):
            bx=x+j*step+(step-bw)/2;total=j in (0,len(entries)-1)
            if abs(b-a)>.0001:
                s=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(bx),Inches(yy(max(a,b))),Inches(bw),Inches(abs(b-a)/maximum*height))
                s.fill.solid();s.fill.fore_color.rgb=brand.accent_primary if total else cfg.MAP_REGION_COLOURS['SADC excluding SACU'] if v>0 else cfg.MAP_REGION_COLOURS['North Africa'];s.line.fill.background()
            else:line((bx,yy(b)),(bx+bw,yy(b)),cfg.DIVIDER_HEADER,1.3)
            value=f'{v:.2f}' if total else f'{v:+.2f}'
            t=text(slide,value,bx-.16,yy(max(a,b))-.26,bw+.32,.22,10,True)
            t.text_frame.paragraphs[0].alignment=PP_ALIGN.CENTER
            t=text(slide,labels[key][j],x+j*step,5.31,step,.56,8.5 if key=='diesel' else 9, total)
            for p in t.text_frame.paragraphs:p.space_after=Pt(0);p.alignment=PP_ALIGN.CENTER
            if j<len(entries)-1:line((bx+bw,yy(b)),(x+(j+1)*step+(step-bw)/2,yy(b)),cfg.DIVIDER_HEADER)
        note=text(slide,notes[key],x,6.05,3.75,.74,11)
        for p in note.text_frame.paragraphs:p.space_after=Pt(0)
    text(slide,'Bar labels show totals or signed changes; + adds demand, − reduces it. Each fuel has its own scale. Bridges reconcile totals; they do not prove causation.',.55,6.9,11.5,.2,9)
