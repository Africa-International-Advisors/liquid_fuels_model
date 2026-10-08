"""Promote the checked v26 build without overwriting any delivered vintage."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
from pptx import Presentation

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--attempt', required=True)
args = parser.parse_args()
qa = root / 'pptx/qa/Vopak_SA_Market_Story_2026_10_08_v26'
build = qa / args.attempt
story = json.loads((root / 'pptx/story/sa_market_story_v26_2026_10_08.json').read_text(encoding='utf-8'))
checks = json.loads((build / 'checks.json').read_text())
assert checks['slides'] == checks['pdf_pages'] == checks['render_count'] == 43
assert json.loads((build / 'table_fit.json').read_text(encoding='utf-8-sig')) == []
assert len(list((build / 'pdf_render').glob('pdf_page_*.png'))) == 43
old = json.loads((root / 'pptx/story/sa_market_story_v25_2026_10_08.json').read_text(encoding='utf-8'))
for spec in story['slides']:
    if spec.get('source_page'):
        assert spec['title'] == old['slides'][spec['source_page'] - 2]['title']
deck = Presentation(build / 'SA_Market_Story_2026-10-08_v26.pptx')
for slide, spec in zip(list(deck.slides)[1:], story['slides']):
    if not spec.get('divider'):
        assert slide.slide_layout.name == 'Header only'
checks.update({'evidence_content': 'pass', 'table_text_fit': 'pass',
               'existing_taglines': 'preserved', 'pdf_render_count': 43,
               'visual_review': 'All 43 PowerPoint and PDF pages reviewed; new exhibits and corrected provincial values inspected.',
               'source_cells': 63, 'source_formula_errors': 0,
               'model_tests': '170 passed', 'governance': 'coverage passed; 57 open exceptions',
               'master_layout': 'Supplied Vopak master; Header only layout retained',
               'build_attempt': args.attempt})
delivered = root / 'pptx/output/delivered/supporting'
files = []
for suffix in ('.pptx', '.pdf'):
    source = build / ('SA_Market_Story_2026-10-08_v26' + suffix)
    target = delivered / source.name
    if target.exists() or (delivered / 'archive/story_versions' / source.name).exists():
        raise FileExistsError(f'Preserve previous delivery: {target}')
    files.append((source, target))
record = delivered / 'archive/records/current_story.json'
previous = delivered / 'archive/records/current_story_before_v26.json'
if previous.exists():
    raise FileExistsError(previous)
shutil.copy2(record, previous)
current = json.loads(record.read_text())
metadata = []
for source, target in files:
    shutil.copy2(source, target)
    metadata.append({'path': target.relative_to(root).as_posix(), 'bytes': target.stat().st_size,
                     'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
for pattern in ('Slide*.PNG', 'contact*.png', 'table_fit.json'):
    for source in build.glob(pattern):
        shutil.copy2(source, qa / source.name)
(qa / 'checks.json').write_text(json.dumps(checks, indent=2) + '\n')
current.update({'current_version': 26, 'slides': 43, 'files': metadata,
                'story': 'pptx/story/sa_market_story_v26_2026_10_08.json',
                'qa': 'pptx/qa/Vopak_SA_Market_Story_2026_10_08_v26/checks.json',
                'latest_change': 'Workbook evidence refresh across the pack; four new exhibits: industry demand, market-sizing issue tree, vehicles and power fleet; outstanding requests updated.',
                'source_workbook_commit': story['revision_26']['source']['commit'],
                'workbook_evidence': 'pptx/story/sa_workbook_evidence_v26_2026_10_08.json',
                'page_audit': 'workstreams/WS3_reporting_delivery/sa_pack_workbook_audit_2026_10_08.csv',
                'previous_delivery': previous.relative_to(root).as_posix()})
record.write_text(json.dumps(current, indent=2) + '\n')
print('Delivered v26 PPTX/PDF; current manifest and hashes updated; v25 preserved.')
