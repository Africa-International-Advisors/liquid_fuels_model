from pathlib import Path
import json,hashlib
from pptx import Presentation
from pypdf import PdfReader
root=Path(__file__).resolve().parents[2];base=root/'pptx/output/delivered/supporting';storypath=root/'pptx/story/sa_market_story_v25_2026_10_08.json'
s=json.loads(storypath.read_text(encoding='utf-8'));ppt=base/'SA_Market_Story_2026-10-08_v25.pptx';pdf=ppt.with_suffix('.pdf')
d=Presentation(ppt);r=PdfReader(pdf);assert len(d.slides)==len(r.pages)==39
for i,x in enumerate(s['slides'],1):assert ''.join(x['title'].split()) in ''.join(r.pages[i].extract_text().split()),i
assert 'No spare capacity is claimed' in r.pages[9].extract_text()
p=base/'archive/records/current_story.json';m=json.loads(p.read_text(encoding='utf-8-sig'))
prior=base/'archive/records/current_story_before_v25.json'
if not prior.exists():prior.write_text(json.dumps(m,indent=2),encoding='utf-8')
m.update(current_version=25,slides=39,story=storypath.relative_to(root).as_posix(),qa='pptx/qa/Vopak_SA_Market_Story_2026_10_08_v25/checks.json',latest_change='Page 10 establishes reported asset position and operating evidence gaps; illustrative turnover chart retained in investment appendix p39.')
m['files']=[dict(path=f.relative_to(root).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in [ppt,pdf]]
p.write_text(json.dumps(m,indent=2),encoding='utf-8')
for p in [base/'README.md',base.parent/'README.md']:
 t=p.read_text(encoding='utf-8').replace('v24','v25').replace('38-page','39-page').replace('38 pages','39 pages')
 if 'Page 39:' not in t:t+='\nPage 10: current asset position and operating data gaps. Page 39: illustrative turnover sensitivity, moved from the situation.\n'
 p.write_text(t,encoding='utf-8')
p=root/'pptx/scripts/check_sa_revision.py';t=p.read_text();t=t.replace('for page in [6,8,9,10,12,13]:','for page in [i+2 for i, spec in enumerate(story["slides"]) if spec.get("panel_subtitles") and spec.get("margin_rules")]:');p.write_text(t)
print('v25: all 39 titles verified; current index updated')
