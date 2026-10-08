import hashlib,json
from pathlib import Path
from pptx import Presentation
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2]
base=ROOT/'pptx/output/delivered/supporting'
storypath=ROOT/'pptx/story/sa_market_story_v24_2026_10_08.json'
story=json.loads(storypath.read_text(encoding='utf-8'))
deck=Presentation(base/'SA_Market_Story_v24.pptx')
pdf=PdfReader(base/'SA_Market_Story_v24.pdf')
assert len(deck.slides)==len(pdf.pages)==38
for i,s in enumerate(story['slides'],1):
    assert ''.join(s['title'].split()) in ''.join(pdf.pages[i].extract_text().split()),i+1
for word in ['NPV','2.806','2.813']:assert word in pdf.pages[3].extract_text()
for word in ['ILLUSTRATIVE','BASELINE','Capture']:assert word in pdf.pages[4].extract_text()
assert 'DR09' in pdf.pages[15].extract_text()
assert 'Appendix' in pdf.pages[16].extract_text()
records=base/'archive/records';current=records/'current_story.json'
prior=json.loads(current.read_text())
if prior['current_version']!=24:
    snapshot=records/'current_story_before_v24.json'
    if not snapshot.exists():snapshot.write_text(json.dumps(prior,indent=2),encoding='utf-8')
prior.update(current_version=24,slides=38,story=storypath.relative_to(ROOT).as_posix(),
 qa='pptx/qa/Vopak_SA_Market_Story_2026_10_08_v24/checks.json',
 latest_change='Official Vopak context and registered illustrative pre-tax economics; numeric investment conditions, nine-world option ranking and downside tests. Worked case pp35–38; not investment approval.')
prior['files']=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [base/'SA_Market_Story_v24.pptx',base/'SA_Market_Story_v24.pdf']]
current.write_text(json.dumps(prior,indent=2),encoding='utf-8')
for p in [base/'README.md',base.parent/'README.md']:
    text=p.read_text(encoding='utf-8').replace('v23','v24').replace('34-page','38-page').replace('34 pages','38 pages')
    text=text.replace('Nigel’s saved taglines are canonical.','Nigel’s taglines form the base; authorised decision-story changes are recorded in v24.')
    text+='\nIllustrative investment case, annual-report context, assumptions and downside tests: pages 35–38. Reported, inferred and illustrative inputs are distinguished; actual commercial calibration remains open.\n'
    p.write_text(text,encoding='utf-8')
print('v24 selected; 38 slide titles and decision content verified')
