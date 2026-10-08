import hashlib,json
from pathlib import Path
from pptx import Presentation
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2]
base=ROOT/'pptx/output/delivered/supporting'
storypath=ROOT/'pptx/story/sa_market_story_v23_2026_10_08.json'
story=json.loads(storypath.read_text(encoding='utf-8'))
deck=Presentation(base/'SA_Market_Story_v23.pptx')
pdf=PdfReader(base/'SA_Market_Story_v23.pdf')
assert len(deck.slides)==len(pdf.pages)==34
for i,s in enumerate(story['slides'],1):
    assert ''.join(s['title'].split()) in ''.join(pdf.pages[i].extract_text().split()),i+1
for word in ['NPV','0.23','0.60']:assert word in pdf.pages[3].extract_text()
for word in ['EV','rail','BASELINE']:assert word in pdf.pages[4].extract_text()
assert 'DR09' in pdf.pages[15].extract_text()
assert 'Appendix' in pdf.pages[16].extract_text()
records=base/'archive/records';current=records/'current_story.json'
prior=json.loads(current.read_text())
if prior['current_version']!=23:
    snapshot=records/'current_story_before_v23.json'
    if not snapshot.exists():snapshot.write_text(json.dumps(prior,indent=2),encoding='utf-8')
prior.update(current_version=23,slides=34,story=storypath.relative_to(ROOT).as_posix(),
 qa='pptx/qa/Vopak_SA_Market_Story_2026_10_08_v23/checks.json',
 latest_change='Opening recommendation and numeric expansion conditions; nine-world investment priorities; emerging gateways; corridor/rail/EV options; priority data request. SCR retained p34.')
prior['files']=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [base/'SA_Market_Story_v23.pptx',base/'SA_Market_Story_v23.pdf']]
current.write_text(json.dumps(prior,indent=2),encoding='utf-8')
for p in [base/'README.md',base.parent/'README.md']:
    text=p.read_text(encoding='utf-8').replace('v22','v23').replace('33-page','34-page').replace('33 pages','34 pages')
    text=text.replace('Nigel’s saved taglines are canonical.','Nigel’s taglines form the base; authorised decision-story changes are recorded in v23.')
    text+='\nInvestment conditions: p4; nine-world investment priorities: p5; options: p15; original SCR synthesis: p34.\n'
    p.write_text(text,encoding='utf-8')
print('v23 selected; 34 slide titles and decision content verified')
