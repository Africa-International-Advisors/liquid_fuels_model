"""Verify v22 before selecting it as the current delivery."""
import hashlib,json
from pathlib import Path
from pptx import Presentation
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
base=ROOT/'pptx/output/delivered/supporting'
storypath=ROOT/'pptx/story/sa_market_story_v22_2026_10_08.json'
story=json.loads(storypath.read_text(encoding='utf-8'))
deck=Presentation(base/'SA_Market_Story_v22.pptx')
pdf=PdfReader(base/'SA_Market_Story_v22.pdf')
assert len(deck.slides)==len(pdf.pages)==33
for i,s in enumerate(story['slides'],1):
    assert ''.join(s['title'].split()) in ''.join(pdf.pages[i].extract_text().split()),i+1
old=Presentation(base/'SA_Market_Story_v21.pptx')
for i,s in enumerate(old.slides):
    if not s.shapes.title or i in (1,3):continue
    newindex=i if i<15 else i+1
    assert s.shapes.title.text==deck.slides[newindex].shapes.title.text
assert 'DR02 / DR05' in pdf.pages[15].extract_text()
assert 'Appendix' in pdf.pages[16].extract_text()
records=base/'archive/records';current=records/'current_story.json'
prior=json.loads(current.read_text())
if prior['current_version']!=22:
    snapshot=records/'current_story_before_v22.json'
    if not snapshot.exists():snapshot.write_text(json.dumps(prior,indent=2),encoding='utf-8')
prior.update(current_version=22,slides=33,story=storypath.relative_to(ROOT).as_posix(),
    qa='pptx/qa/Vopak_SA_Market_Story_2026_10_08_v22/checks.json',
    latest_change='Agreed titles 2/4; data request p16; baseline diagnostic p32; six-step screening implementation p33. Commercial calibration open.')
prior['files']=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [base/'SA_Market_Story_v22.pptx',base/'SA_Market_Story_v22.pdf']]
current.write_text(json.dumps(prior,indent=2),encoding='utf-8')
for p in [base/'README.md',base.parent/'README.md']:
    text=p.read_text(encoding='utf-8').replace('v21','v22').replace('30-page','33-page').replace('30 pages','33 pages').replace('page 16','page 17')
    if 'Data request: page 16' not in text:
        text+='\nData request: page 16. Baseline reconciliation and implementation status: pages 32–33.\n'
    p.write_text(text,encoding='utf-8')
print('v22 selected: 33 pages; preserved all other canonical titles; request and Appendix placement verified')
