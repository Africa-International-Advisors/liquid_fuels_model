"""Restore client governance without modifying the analytical exhibits."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
import hashlib,json,sys
from pptx import Presentation
from pptx.util import Inches
from brand_pptx import BrandStyle, add_themed_slide
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from brand_configs import vopak as cfg
from supply_review_pages import table,line
from pptx.util import Pt

def text(s,value,x,y,w,h,size=14,bold=False,color=None):
    q=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    f=q.text_frame;f.word_wrap=True;f.margin_left=f.margin_right=Inches(.025);f.margin_top=f.margin_bottom=0
    for i,copy in enumerate(value.split("\n")):
        p=f.paragraphs[0] if i==0 else f.add_paragraph();p.text=copy;p.font.name=cfg.THEME_FONT;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=color or brand.ink;p.space_after=Pt(3)
    return q
from scr_editorial import replace
brand=BrandStyle.from_module(cfg)
source=Path(sys.argv[1]).resolve();output=Path(sys.argv[2]).resolve()
if source==output or output.exists():raise ValueError('Use a new output version and preserve the source.')
prs=Presentation(source);before=len(prs.slides);sample=prs.slides[15]
data=json.loads((ROOT/'story/vopak_client_governance_2026_10_06.json').read_text())
s=add_themed_slide(prs,sample.slide_layout.name,brand=brand,title=data['title'])
for q in list(s.shapes):q._element.getparent().remove(q._element)
ns='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
for q in sample.shapes:
    if not (q.top<Inches(1.7) or q.top>=Inches(7.05)):continue
    element=deepcopy(q._element)
    for node in element.iter():
        for attr,value in list(node.attrib.items()):
            if not attr.startswith(ns):continue
            rel=sample.part.rels[value]
            node.set(attr,s.part.relate_to(rel.target_ref if rel.is_external else rel.target_part,rel.reltype,is_external=rel.is_external))
    s.shapes._spTree.insert_element_before(element,'p:extLst')
for q in s.shapes:
    if q.is_placeholder and q.has_text_frame and 'Title' in q.name:replace(q,data['title'])
    elif q.has_text_frame and q.text.startswith('Source:'):replace(q,'Source: Earlier kickoff cadence and agreed internal roles; proposed client roles, names and authority to confirm.')
text(s,'Client governance | counterpart roles and acceptance authority for confirmation',.5,1.78,11.65,.32,14,True)
line(s,(.5,2.13),(12.15,2.13),brand.ink,.55)
text(s,'Client counterparts',.5,2.40,5.6,.30,14,True,brand.accent_primary)
text(s,'Review cadence',6.6,2.40,5.55,.30,14,True,brand.accent_primary)
table(s,data['client_rows'],.5,2.95,[1.7,1.35,2.60],2.90,brand,11)
table(s,data['cadence_rows'],6.6,2.95,[1.3,2.0,2.25],2.90,brand,11)
text(s,data['internal_line'],.5,6.08,11.65,.36,12,True)
text(s,data['acceptance_line'],.5,6.61,11.65,.39,11)
s.notes_slide.notes_text_frame.text=json.dumps(data,indent=2)+'\nDaily internal check-in and written check-out remain as recorded in earlier cadence page. No client appointments, names or delegated approval authority inferred.'
ids=list(prs.slides._sldIdLst);new=ids.pop();ids.insert(before-2,new)
for sid in list(prs.slides._sldIdLst):prs.slides._sldIdLst.remove(sid)
for sid in ids:prs.slides._sldIdLst.append(sid)
for page,slide in enumerate(prs.slides,1):
    for q in slide.shapes:
        if q.has_text_frame and q.left>Inches(12) and q.top>Inches(7) and q.text.strip().isdigit():replace(q,str(page))
    for q in slide.shapes:assert q.left>=0 and q.top>=0 and q.left+q.width<=prs.slide_width+10 and q.top+q.height<=prs.slide_height+10,(page,q.name)
prs.save(output)
qa=ROOT/'qa/vopak_governance';qa.mkdir(parents=True,exist_ok=True)
(qa/'provenance.json').write_text(json.dumps({'created_utc':datetime.now(timezone.utc).isoformat(),'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output':str(output),'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'slide_count':len(prs.slides),'restored_page':before-1,'status':data['status'],'specification_sha256':hashlib.sha256((ROOT/'story/vopak_client_governance_2026_10_06.json').read_bytes()).hexdigest(),'builder_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))
print(output)
