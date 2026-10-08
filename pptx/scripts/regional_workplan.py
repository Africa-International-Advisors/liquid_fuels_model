"""Replace the current workplan slide from an editable geographic delivery plan."""
import json
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from convergence_feedback import text, replace
from convergence_story_order import native_table
from analytical_revision import BRAND, BLUE, INK, drop


def main(source, destination):
    root=Path(__file__).resolve().parents[1]
    plan=json.loads((root/'story/regional_delivery_plan_2026_10_07.json').read_text())
    prs=Presentation(source)
    s=prs.slides[11]
    assert s.shapes.title.text.startswith('Baseline reconciliation')
    for q in list(s.shapes):
        if Inches(1.7)<=q.top<Inches(7.04):drop(q)
    replace(s.shapes.title,'Week 1 focuses on the SA baseline; Namibia and Africa have shorter parallel tracks')
    text(s,'Current work and proposed geographic delivery sequence | 7 October 2026',.5,1.78,11.65,.35,14,True,INK)
    rows=[['Workstream / intended output','Lead / support']+plan['weeks']]
    rows += [[r['label']+'\n'+r['output'],r['owner'].replace(' / ',' /\n')]+r['cells'] for r in plan['rows']]
    t=native_table(s,rows,.5,2.35,[4.8,1.45]+[.9]*6,[.5]+[.52]*6,BRAND,9.2)
    for r,entry in enumerate(plan['rows'],1):
        cell=t.cell(r,0)
        cell.text_frame.paragraphs[0].font.bold=True
        cell.text_frame.paragraphs[0].font.color.rgb=BLUE
        cell.text_frame.paragraphs[1].font.size=Pt(8.4)
        for k,value in enumerate(entry['cells'],2):
            c=t.cell(r,k)
            if value:
                c.fill.solid();c.fill.fore_color.rgb=BLUE if value=='ACTIVE' else BRAND.grey_fill
                for p in c.text_frame.paragraphs:
                    p.font.color.rgb=BRAND.white if value=='ACTIVE' else INK
                    p.font.size=Pt(8.5)
    c=t.cell(0,2);c.fill.solid();c.fill.fore_color.rgb=BLUE
    for p in c.text_frame.paragraphs:p.font.color.rgb=BRAND.white
    text(s,'Africa scope: East, West and North Africa; SADC excluding SACU. Screening first, then prioritise countries.',.5,6.14,11.65,.3,10,True,INK)
    text(s,'Shared team: parallel tracks are proposed and depend on SA baseline progress, source access and available effort.',.5,6.49,11.65,.3,10,color=INK)
    text(s,'Blue = active in Week 1. Grey = proposed work, not completion. Weekly review updates scope, owners and timing; 12 Nov remains a target.',.5,6.82,11.65,.21,8.5,color=INK)
    for q in s.shapes:
        if q.name=='Unified source footer':replace(q,'Source: scope_and_roles.md; six_week_plan.md; Nigel\'s Week 1 correction. Proposed geographic sequence; no client dates or business approval inferred.')
    s.notes_slide.notes_text_frame.text=json.dumps(plan,indent=2)
    out=Path(destination)
    if out.exists():raise FileExistsError(out)
    prs.save(out);print(out)


if __name__=='__main__':main(sys.argv[1],sys.argv[2])
