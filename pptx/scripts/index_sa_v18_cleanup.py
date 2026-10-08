"""Refresh current and archive entry points without modifying delivered decks."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SUPPORT=ROOT/'pptx/output/delivered/supporting'
if (SUPPORT/'filename_history.json').exists():
    raise RuntimeError('Supporting has been resequenced. Use its current README and current_story.json; do not restore the former layout.')
ARCHIVE=SUPPORT/'archive/2026-10-08_pre_v18'
stem='Vopak_SA_Market_Story_2026_10_08_v18'
old=(SUPPORT/'README.md').read_text(encoding='utf-8')
# Preserve the former index as historical context, with corrected relative links.
if not (ARCHIVE/'prior_index.md').exists():
    old=re.sub(r'\]\(([^)]+)\)',lambda m:']('+ (m[1] if (ARCHIVE/m[1]).exists() else '../../'+m[1])+')',old)
    (ARCHIVE/'prior_index.md').write_text(old,encoding='utf-8')
versions=sorted({p.stem for p in ARCHIVE.glob('*.pptx')},key=lambda x:int(x.rsplit('_v',1)[1]))
(ARCHIVE/'README.md').write_text('# Earlier South Africa story packs\n\nCurrent review: [v18 PDF](../../'+stem+'.pdf) / [PowerPoint](../../'+stem+'.pptx).\n\nAll earlier delivered files below were moved intact and verified by SHA-256.\nSee [cleanup manifest](cleanup_manifest.json) and [previous index](prior_index.md).\n\n| Version | PDF | PowerPoint |\n|---|---|---|\n'+''.join(f'| {v.rsplit("_",1)[1]} | [PDF]({v}.pdf) | [PowerPoint]({v}.pptx) |\n' for v in versions),encoding='utf-8')
support=f'''# South Africa market story — current review

**Version 18 · 8 October 2026 · 30 pages**

- [Read the PDF]({stem}.pdf)
- [Open the editable PowerPoint]({stem}.pptx)
- [Earlier story versions and cleanup manifest](archive/2026-10-08_pre_v18/README.md)

Executive summary: pages 2–5. Situation: 6–10. Complication: 11–14.
Resolution: 15. Appendix cover: 16; supporting evidence: 17–30.
Scenario and commercial calibration remain open; this is the current review pack.

## Supporting material

| Material | Files |
|---|---|
| Agreed review scope | [PDF](Vopak_SA_Review_Signed_Off_2026_10_07_v2.pdf) / [PowerPoint](Vopak_SA_Review_Signed_Off_2026_10_07_v2.pptx) |
| Review comments applied | [PDF](Vopak_SA_Review_Comments_Applied_2026_10_07_v3.pdf) / [PowerPoint](Vopak_SA_Review_Comments_Applied_2026_10_07_v3.pptx) |
| Analyst kickoff | [PDF](Vopak_Analyst_Kickoff.pdf) / [PowerPoint](Vopak_Analyst_Kickoff.pptx) |
| Assumption inventory | [PDF](Vopak_Assumption_Inventory.pdf) |
| Earlier analyst handover | [PDF](Vopak_Manish_Handover_2026_10_06.pdf) |
| Market-envelope illustration | [HTML](Vopak_market_envelope_illustrative_2026_10_06.html) / [PNG](Vopak_market_envelope_illustrative_2026_10_06.png) |
| Illustration inputs | [National balance](illustrative_national_balance.csv), [catchments](illustrative_market_catchments.csv), [routes](illustrative_terminal_routes.csv) |

The illustrations are authored examples, not measured market shares or forecasts.
The earlier [Convergence pack](../Vopak_Convergence_current.pdf) remains a reference.
'''
(SUPPORT/'README.md').write_text(support,encoding='utf-8')
(ROOT/'pptx/output/delivered/README.md').write_text(f'''# Current South Africa review — v18

Updated 8 October 2026. The current market story is the matching **30-page v18** pair:

- [Current PDF](supporting/{stem}.pdf)
- [Current editable PowerPoint](supporting/{stem}.pptx)
- [Supporting material and page guide](supporting/README.md)
- [Earlier South Africa versions](supporting/archive/2026-10-08_pre_v18/README.md)

The Appendix cover is page 16. Scenario calibration, commercial inputs and operational
routing validation remain open.

## Other retained material

- Earlier Convergence reference: [PDF](Vopak_Convergence_current.pdf) / [PowerPoint](Vopak_Convergence_current.pptx).
- [Compact demand-baseline workbook](../../../output/delivered/Demand_baseline_workshop_2026_10_07_compact.xlsx).
- [Earlier Convergence review archive](archive/2026-10-07_review_iterations/).

The Convergence filenames are retained for compatibility; v18 above is the current
South Africa story. Source data, presentation sources and all delivered vintages
are preserved. No validation or business approval is implied by this cleanup.
''',encoding='utf-8')
# Incremental builders still work from archived inputs. Output targets stay unchanged.
for p in (ROOT/'pptx/scripts').glob('*.ps1'):
    if p.name=='cleanup_sa_v18.ps1':continue
    s=p.read_text(encoding='utf-8-sig');new=s
    for v in versions:
        for ext in ['pptx','pdf']:
            name=v+'.'+ext
            new=new.replace("Join-Path $out '"+name+"'","Join-Path $out 'archive/2026-10-08_pre_v18/"+name+"'")
    if new!=s:p.write_text(new,encoding='utf-8')
