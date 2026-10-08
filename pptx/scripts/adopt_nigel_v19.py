"""Adopt saved Nigel slide titles verbatim into the next canonical story vintage."""
import json,hashlib
from pathlib import Path
from pptx import Presentation
ROOT=Path(__file__).resolve().parents[2]
base=ROOT/'pptx/output/delivered/supporting'
source=base/'SA_Market_Story_v18_nigel.pptx'
deck=Presentation(source)
story=json.loads((ROOT/'pptx/story/sa_market_story_v18_2026_10_08.json').read_text(encoding='utf-8'))
assert len(deck.slides)==len(story['slides'])+1
changes=[]
for page,(slide,spec) in enumerate(zip(list(deck.slides)[1:],story['slides']),2):
    if slide.shapes.title is None:continue
    title=slide.shapes.title.text
    if title!=spec['title']:changes.append({'page':page,'previous':spec['title'],'canonical':title})
    spec['title']=title
story['canonical_edit_source']={'path':source.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'adoption':'User requested Nigel taglines become canonical; new PPTX and PDF version 19.','wording':'Verbatim from saved slide-title placeholders; no copy edits.'}
(ROOT/'pptx/story/sa_market_story_v19_2026_10_08.json').write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(base/'archive/records/nigel_taglines_v19.json').write_text(json.dumps({'source':story['canonical_edit_source'],'changes':changes},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Canonical taglines adopted:',len(changes))
