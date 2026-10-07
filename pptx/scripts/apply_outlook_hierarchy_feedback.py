"""Rebuild only the three user-reviewed outlook exhibits in an existing source deck."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pptx import Presentation
from pptx.util import Inches, Pt
from brand_pptx import BrandStyle

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from brand_configs import vopak as cfg
from supply_review_pages import volume_page, read
from storage_sensitivity_page import add_storage_sensitivity_page
from market_playbook_page import draw_market_playbook
from scr_editorial import replace
brand=BrandStyle.from_module(cfg)

def text(s,value,x,y,w,h,size=14,bold=False,color=None):
    q=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    f=q.text_frame;f.word_wrap=True
    f.margin_left=f.margin_right=Inches(.025);f.margin_top=f.margin_bottom=0
    for i,copy in enumerate(value.split('\n')):
        p=f.paragraphs[0] if i==0 else f.add_paragraph()
        p.text=copy;p.font.name=cfg.THEME_FONT;p.font.size=Pt(size)
        p.font.bold=bold;p.font.color.rgb=color or brand.ink;p.space_after=Pt(3)
    return q

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

source=Path(sys.argv[1]).resolve();output=Path(sys.argv[2]).resolve()
if source==output:raise ValueError('Preserve the received/source deck; use a new output name.')
if output.exists():raise FileExistsError(output)
original_hash=digest(source)
prs=Presentation(source);changed=[]
for page,s in enumerate(prs.slides,1):
    title=next((q for q in s.shapes if q.is_placeholder and q.has_text_frame and 'Title' in q.name),None)
    if title is None:continue
    old=title.text
    if 'additional opportunity is' in old:
        volume_page(s,text,ROOT,brand);replace(title,old);changed.append(page)
    elif 'Prioritise customer markets' in old:
        for q in list(s.shapes):
            if Inches(1.7)<=q.top<Inches(7.05):q._element.getparent().remove(q._element)
        draw_market_playbook(s,text,ROOT,brand);changed.append(page)
    elif 'preliminary inventory requirement' in old:
        add_storage_sensitivity_page(s,text,ROOT,brand)
        row=read(ROOT/'story/storage_inventory_sensitivity_2026_10_06.csv')[1]
        replace(title,f"R7. Illustrative additional flows require {float(row['working_inventory_thousand_m3']):.0f} thousand m³ at {row['inventory_days']} inventory days")
        changed.append(page)
assert len(changed)==3,changed
for i,s in enumerate(prs.slides,1):
    for q in s.shapes:
        assert q.left>=0 and q.top>=0 and q.left+q.width<=prs.slide_width+10 and q.top+q.height<=prs.slide_height+10,(i,q.name)
output.parent.mkdir(parents=True,exist_ok=True);prs.save(output)
assert digest(source)==original_hash
inputs=[ROOT/'story/illustrative_market_catchments.csv',ROOT/'story/storage_inventory_sensitivity_2026_10_06.csv',ROOT/'story/market_playbook_2026_10_06.json']
manifest={'created_utc':datetime.now(timezone.utc).isoformat(),'source':str(source),'source_sha256':original_hash,'output':str(output),'output_sha256':digest(output),'changed_pages':changed,'slides':len(prs.slides),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT.parent,text=True).strip(),'status':'Provisional illustrative presentation; source volumes and model logic unchanged','inputs':{str(p.relative_to(ROOT)):digest(p) for p in inputs},'builders':{p.name:digest(p) for p in [Path(__file__),ROOT/'scripts/supply_review_pages.py',ROOT/'scripts/storage_sensitivity_page.py',ROOT/'scripts/market_playbook_page.py']}}
qa=ROOT/'qa/outlook_hierarchy_feedback';qa.mkdir(parents=True,exist_ok=True)
(qa/'provenance.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(output),'changed_pages':changed,'slides':len(prs.slides)}))
