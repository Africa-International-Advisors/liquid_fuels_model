"""Add explicit net-import series and align paired panels in the review deck."""
import sys
from copy import deepcopy
from pathlib import Path
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.util import Inches, Pt
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.chart import XL_MARKER_STYLE
from analytical_revision import BLUE, SECOND, INK, drop
from convergence_feedback import text, replace
from supply_review_pages import line
from annotated_layout import size


def main(source, destination):
    prs = Presentation(source)
    s = prs.slides[3]
    for i, q in enumerate([q for q in s.shapes if q.has_chart]):
        c = q.chart
        data = CategoryChartData(); data.categories = [v.label for v in c.plots[0].categories]
        values = [(r.name, list(r.values)) for r in c.series]
        for name, vals in values: data.add_series(name, vals)
        imports = dict(values)['Imports']; exports = dict(values)['Exports']
        data.add_series('Net imports', [a-b for a,b in zip(imports,exports)])
        c.replace_data(data)
        sr = c.series[-1]
        sr.format.line.color.rgb = BLUE; sr.format.line.width = Pt(1.8)
        sr.format.line.dash_style = MSO_LINE_DASH_STYLE.DASH
        sr.marker.style = XL_MARKER_STYLE.NONE
    for q in list(s.shapes):
        if Inches(2.3) <= q.top < Inches(2.7): drop(q)
    for start in [.5, 6.45]:
        for offset,label,col in [(0,'Sales',BLUE),(1.2,'Imports',SECOND),(2.55,'Exports',INK),(3.95,'Net imports',BLUE)]:
            l=line(s,(start+offset,2.55),(start+offset+.23,2.55),col,1.8)
            if label=='Net imports':l.line.dash_style=MSO_LINE_DASH_STYLE.DASH
            text(s,label,start+offset+.3,2.43,1.18,.25,9,color=INK)
    for q in s.shapes:
        if q.name=='Unified source footer':
            replace(q,'Sources: departmental sales 2019-2023; FIASA 2024 sales (diamond; revisions unresolved); SARS trade 2019-2025. Net imports = imports minus exports.\nComparable national petrol/diesel production is not yet available: operator output mixes products, periods and ownership shares. No production residual inferred.')

    s=prs.slides[4]
    # Leave a real gutter around the divider, including legends and explanatory text.
    for q in s.shapes:
        if Inches(1.7)<=q.top<Inches(7.04):
            if q.left < Inches(6.02):
                q.left=Inches(.5)+int((q.left-Inches(.5))*.95)
                q.width=int(q.width*.95)
            else:
                q.left+=Inches(.1)
                if q.width>Inches(5.9):q.width=Inches(5.9)
    line(s,(.5,2.13),(5.7,2.13),INK,.6)
    line(s,(6.15,2.13),(12.15,2.13),INK,.6)
    line(s,(5.93,2.13),(5.93,6.87),INK,.6)
    for q in prs.slides[8].shapes:
        if q.name.startswith('SCR divider marker:'):
            el=deepcopy(q._element);s.shapes._spTree.insert_element_before(el,'p:extLst')
            added=s.shapes[-1];added.left+=Inches(5.93-7.88)
            for node in el.xpath('.//p:cNvPr'):node.set('id',str(max(sh.shape_id for sh in s.shapes)+1))

    for n in [10,11]:
        s=prs.slides[n-1]
        for q in s.shapes:
            if q.has_text_frame and q.text.startswith(('Regional footprint |','Annual demand and gross handling','Implication for Vopak')):
                q.top=Inches(1.78);q.height=Inches(.35);size(q,13.5)
            elif q.name in ['Footprint legend','Demand legend','Handling legend']:
                q.top=Inches(2.25)
            elif q.has_text_frame and q.text in ['Vopak','Other listed','Reported demand'] and q.left<Inches(7.7):
                q.top=Inches(2.19)
            elif q.name.startswith('SCR divider marker:'):
                q.top+=Inches(.37)
            elif q.shape_type==9 and q.width>Inches(3) and q.top<Inches(2.6) and q.top>Inches(2):
                q.top=Inches(2.50)
            elif q.shape_type==9 and q.height>Inches(4) and abs(q.left-Inches(7.88))<10:
                q.top=Inches(2.50);q.height=Inches(4.36)
            elif q.left>=Inches(8) and Inches(2.39)<=q.top<Inches(7):
                q.top=Inches(2.74)+int((q.top-Inches(2.39))*.90)
            elif n==10 and q.has_text_frame and q.text in ['Region / provinces','Storage location','Published tank capacity']:
                q.top=Inches(2.72)
            elif n==11 and q.has_text_frame and q.text.startswith('Base estimate:'):
                q.top=Inches(2.78)
    out=Path(destination)
    if out.exists():raise FileExistsError(out)
    prs.save(out);print(out)


if __name__=='__main__':main(sys.argv[1],sys.argv[2])
