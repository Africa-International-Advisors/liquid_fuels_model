"""Sequence received and delivered supporting packs; retain a hash-verified name map."""
import json,re,hashlib,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'pptx/output/delivered/supporting'
labels={2:'Initial_market_story',3:'Reorganised_argument',4:'SCR_and_nine_world_matrix',5:'Top_down_investment_story',9:'Evidence_and_levers_feedback',10:'Two_part_executive_summary',11:'Projected_geospatial_reference',12:'Future_supply_capacity_cases',13:'Consistent_exhibit_layouts',14:'Reference_visual_style',15:'SCR_argument_icons',16:'Network_map_icons_and_appendix',17:'Aligned_exhibit_subtitles',18:'Executive_summary_navigation'}
mapping={}
for p in BASE.rglob('Vopak_SA_Market_Story_*.pptx'):
    m=re.fullmatch(r'Vopak_SA_Market_Story_(\d{4}_\d{2}_\d{2})_v(\d+)',p.stem)
    if not m:continue
    date,v=m[1].replace('_','-'),int(m[2])
    for ext in ['pptx','pdf']:
        src=p.with_suffix('.'+ext)
        mapping[src]=BASE/'03_Market_story'/f'V{v:02d}_SA_market_story_{labels[v]}_{date}.{ext}'
groups={
'Vopak_Analyst_Kickoff':('01_Background_and_handover','01_Analyst_kickoff'),
'Vopak_Assumption_Inventory':('01_Background_and_handover','02_Assumption_inventory'),
'Vopak_Manish_Handover_2026_10_06':('01_Background_and_handover','03_Analyst_handover_2026-10-06'),
'Vopak_SA_Review_Signed_Off_2026_10_07_v2':('02_Review_scope','01_Agreed_review_scope_2026-10-07_v02'),
'Vopak_SA_Review_Comments_Applied_2026_10_07_v3':('02_Review_scope','02_Review_scope_comments_applied_2026-10-07_v03'),
'Vopak_market_envelope_illustrative_2026_10_06':('04_Illustrations','Illustrative_market_envelope_2026-10-06')}
for p in BASE.iterdir():
    if p.is_file() and p.stem in groups:
        folder,name=groups[p.stem];mapping[p]=BASE/folder/(name+p.suffix)
    elif p.is_file() and p.name.startswith('illustrative_') and p.suffix=='.csv':mapping[p]=BASE/'04_Illustrations'/p.name
if not mapping:raise RuntimeError('No unsequenced files found; preserve existing name map.')
records=[]
for src,dest in mapping.items():
    assert src.resolve().is_relative_to(ROOT) and dest.resolve().is_relative_to(BASE)
    if dest.exists():raise FileExistsError(dest)
    digest=hashlib.sha256(src.read_bytes()).hexdigest();dest.parent.mkdir(parents=True,exist_ok=True);src.rename(dest)
    assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest
    records.append({'old_path':src.relative_to(ROOT).as_posix(),'new_path':dest.relative_to(ROOT).as_posix(),'sha256':digest,'bytes':dest.stat().st_size})
(BASE/'filename_history.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
# Repair Markdown links by resolving their previous actual destination.
for p in (ROOT/'pptx').rglob('*.md'):
    if 'qa' in p.parts:continue
    s=p.read_text(encoding='utf-8-sig')
    def link(m):
        href=m[1]
        if '://' in href:return m[0]
        old=(p.parent/href).resolve()
        return ']('+os.path.relpath(mapping[old],p.parent).replace('\\','/')+')' if old in mapping else m[0]
    new=re.sub(r'\]\(([^)]+)\)',link,s)
    if new!=s:p.write_text(new,encoding='utf-8')
# Incremental builders resolve the renamed source packs relative to supporting.
for p in (ROOT/'pptx/scripts').glob('*.ps1'):
    s=p.read_text(encoding='utf-8-sig');new=s
    for src,dest in mapping.items():
        new=new.replace("Join-Path $out '"+src.relative_to(BASE).as_posix()+"'","Join-Path $out '"+dest.relative_to(BASE).as_posix()+"'")
    if new!=s:p.write_text(new,encoding='utf-8')
current=BASE/'current_story.json';c=json.loads(current.read_text());c['layout_revision']=2
for item in c['files']:item['path']=mapping[ROOT/item['path']].relative_to(ROOT).as_posix()
current.write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
lines=['# Supporting — review progression','','**Start with the current story: V18.** Folder numbers show the reading sequence; story numbers retain the original revision history.','','| Stage | Purpose |','|---|---|','| 01 · Background and handover | Analyst kickoff, assumption inventory and handover. |','| 02 · Review scope | Agreed work programme, followed by comments applied. |','| 03 · Market story | The developing argument, evidence, scenarios and presentation revisions. |','| 04 · Illustrations | Authored examples and their input tables; not measured market shares. |','','## Story progression','','| Version | What changed | PDF | PowerPoint |','|---|---|---|---|']
for v,label in labels.items():
    p=next((BASE/'03_Market_story').glob(f'V{v:02d}_*.pdf'));rel=p.relative_to(BASE).as_posix()
    lines.append(f'| **V{v:02d}'+(' · CURRENT' if v==18 else '')+f'** | {label.replace("_"," ")} | [PDF]({rel}) | [PowerPoint]({rel[:-4]}.pptx) |')
lines+=['','The preserved delivered sequence has gaps at V01 and V06–V08; those files are not present here. No missing versions have been invented.','','## Background, scope and illustrations','']
for folder in ['01_Background_and_handover','02_Review_scope','04_Illustrations']:
    lines.append('### '+folder.replace('_',' '));lines.append('')
    for p in sorted((BASE/folder).iterdir()):lines.append(f'- [{p.stem.replace("_"," ")} ({p.suffix[1:].upper()})]({p.relative_to(BASE).as_posix()})')
    lines.append('')
lines+=['## Current pack guide','','V18 has 30 pages: executive summary 2–5; situation 6–10; complication 11–14; resolution 15; Appendix cover 16; supporting evidence 17–30. Scenario and commercial calibration remain open.','','[Filename history and hashes](filename_history.json) retain the old-to-new names. The [cleanup manifest](archive/2026-10-08_pre_v18/cleanup_manifest.json) records the earlier archive operation; its paths describe that operation, before this resequencing.']
(BASE/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(BASE/'archive/2026-10-08_pre_v18/README.md').write_text('# Earlier cleanup records\n\nThe packs now appear in the numbered [supporting progression](../../README.md). This folder retains the [cleanup manifest](cleanup_manifest.json) and [former index](prior_index.md). Use the [filename history](../../filename_history.json) to resolve names after resequencing.\n',encoding='utf-8')
print(f'Renamed {len(records)} files; content hashes unchanged.')
