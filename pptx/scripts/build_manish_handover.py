"""Render the agreed analyst handover with the supplied Vopak master.

The editable intermediate stays in QA. Only the exported PDF is delivered.
No model inputs, calculations or fetches are changed by this builder.
"""
from pathlib import Path
from copy import deepcopy
import io
import sys

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from brand_pptx import BrandStyle, add_themed_slide, remove_all_slides_cleanly
from brand_pptx import _strip_table_style, cell_bottom_rule

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from brand_configs import vopak as cfg

brand = BrandStyle.from_module(cfg)
source = Presentation(ROOT/'output/delivered/Vopak_Week1_Convergence_2026_10_06.pptx')
prs = Presentation(ROOT/'output/delivered/Vopak_Week1_Convergence_2026_10_06.pptx')
remove_all_slides_cleanly(prs)
REPO_URL = 'https://github.com/Africa-International-Advisors/liquid_fuels_model/blob/main/'
QA = ROOT/'qa/manish_handover'
QA.mkdir(parents=True, exist_ok=True)


def text(s, value, x, y, w, h, size=12, bold=False, color=None, url=None):
    q = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = q.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(.025)
    tf.margin_top = tf.margin_bottom = 0
    for i, value in enumerate(value.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = value
        p.font.name = cfg.THEME_FONT
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = color or brand.ink
        p.space_after = Pt(3)
        if url:
            for run in p.runs:
                run.hyperlink.address = url
    return q


def line(s, x1, y1, x2, y2, color=None):
    q = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    q.line.color.rgb = color or cfg.DIVIDER_HEADER
    q.line.width = Pt(.6)


def bookend(original, replacements):
    s = add_themed_slide(prs, '1_Title', brand=brand)
    for q in list(s.shapes):
        if q.is_placeholder:
            q._element.getparent().remove(q._element)
    for q in original.shapes:
        if q.shape_type == 13:
            dest = s.shapes.add_picture(io.BytesIO(q.image.blob), q.left, q.top, q.width, q.height)
            dest.crop_left, dest.crop_right = q.crop_left, q.crop_right
            dest.crop_top, dest.crop_bottom = q.crop_top, q.crop_bottom
        else:
            element = deepcopy(q._element)
            for node in element.iter():
                for key, value in list(node.attrib.items()):
                    if key.startswith('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'):
                        rel = original.part.rels[value]
                        assert rel.is_external
                        node.set(key, s.part.rels.get_or_add_ext_rel(rel.reltype, rel.target_ref))
            s.shapes._spTree.insert_element_before(element, 'p:extLst')
    for q in s.shapes:
        if q.has_text_frame:
            for p in q.text_frame.paragraphs:
                for run in p.runs:
                    run.text = replacements.get(run.text, run.text)
    return s


def page(title, subtitle):
    s = add_themed_slide(prs, 'Header only', brand=brand, title=title)
    text(s, subtitle, .5, 1.78, 11.65, .38, 14, True)
    line(s, .5, 2.13, 12.15, 2.13)
    text(s, 'Source: 6 October agreed handover; source profile and audit; candidate data remain subject to review.',
         .5, 7.16, 10.6, .22, 8)
    return s


def table(s, rows, widths, y=2.50, height=3.9, size=12):
    q = s.shapes.add_table(len(rows), len(widths), Inches(.5), Inches(y), Inches(sum(widths)), Inches(height))
    t = q.table
    _strip_table_style(t)
    for col, width in zip(t.columns, widths):
        col.width = Inches(width)
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            c = t.cell(i, j)
            c.text = value
            c.margin_left = c.margin_right = Inches(.07)
            c.margin_top = Inches(.08)
            c.margin_bottom = Inches(.035)
            c.vertical_anchor = MSO_ANCHOR.TOP
            c.fill.solid()
            c.fill.fore_color.rgb = brand.white
            cell_bottom_rule(c, color=cfg.DIVIDER_BODY, w_pt=.4)
            for p in c.text_frame.paragraphs:
                p.font.name = cfg.THEME_FONT
                p.font.size = Pt(size)
                p.font.bold = i == 0 or j == 0
                p.font.color.rgb = brand.accent_primary if j == 0 else brand.ink
                p.space_after = Pt(2)
    return t


bookend(source.slides[0], {'Week 1 analytical pack': 'Manish handover',
                          'South Africa | Petrol and diesel': '6 October focus | Source and reconcile the data'})

s = page('Source the data before quantifying the fuel levers',
         'Today: integrity, traceability, provincial update and a matched fuel balance')
table(s, [
    ['Priority', 'Manish does', 'Return for review'],
    ['1 Data integrity', 'Investigate incomplete provincial totals, duplicate refinery/history keys and unsupported baselines.',
     'Flag; old value; source page/cell; proposed value; reason; resolved or open.'],
    ['2 Traceability', 'Trace priority data from publisher to original file, extract and consuming function.',
     'Exact paths; API/download/manual; units; coverage; used, staged or reporting-only.'],
    ['3 Provincial update', 'Verify newer observed provincial petrol/diesel sales, then seek 2025 and latest 2026 coverage.',
     'Province/product/period; observed versus estimated; national tie; missing periods.'],
    ['4 Production and trade', 'Reconcile production, imports, exports and stock movements for the same product and period.',
     'Matched litres; source definitions; stock treatment; unexplained residual.'],
    ['5 Driver evidence', 'Source agriculture, manufacturing, mining, passenger/freight, power, EV and plant series.',
     'Original evidence and extracts for each chart; revisions and coverage. Scenario settings follow.'],
], [1.65, 5.1, 4.9], height=4.08)
text(s, 'Ways of working: Nigel on main; Manish on a named branch from current origin/main. Nigel reviews changes before integration.',
     .5, 6.72, 11.65, .30, 11, True, brand.accent_primary)

s = page('Open the exact files and follow their data trail',
         'All paths are relative to your clone of liquid_fuels_model')
paths_table = table(s, [
    ['Start here', 'Exact path beneath the project folder', 'What to check'],
    ['Audit and direction', 'output/delivered/\nLiquid_fuels_source_audit_2026_10_05.xlsx\nsource_profile_2026_10_05.html',
     'Direction, Provincial gaps, Repeated keys; input access and consuming functions.'],
    ['Provincial demand', 'assumptions/2026/timeseries/\nfuel_sales_department_by_province.csv\nfuel_sales_department_by_province_quarterly.csv',
     'Incomplete quarters and annual totals; source_file identifies the original workbook.'],
    ['Production and trade', 'assumptions/2026/timeseries/\nenergy_balance_department.csv\nfuel_trade_fiasa.csv\nfuel_trade_department_review.csv',
     'Same product/period/units; 2024 diesel imports: 14.793 versus 10.8 bn litres remains a source disagreement.'],
    ['Duplicate records', 'assumptions/2026/timeseries/\nrefinery_production.csv\nhistorical_demand.csv',
     '558 extra refinery rows and 15 extra historical rows. refinery_production.csv feeds utilisation, despite its name.'],
    ['Baseline parameters', 'assumptions/2026/\nvehicles.yaml; agriculture.yaml\nindustrial.yaml; marine.yaml',
     'Source of mileage, fuel mix, baselines and elasticities. Activity indices cannot silently replace parameters.'],
], [1.65, 5.3, 4.7], y=2.35, height=4.2, size=11)
for row, height in zip(paths_table.rows, [.4, .72, .72, .92, .72, .72]):
    row.height = Inches(height)
    for cell in row.cells:
        cell.margin_top = Inches(.04)
        cell.margin_bottom = Inches(.025)
        for paragraph in cell.text_frame.paragraphs:
            paragraph.space_after = Pt(0)
text(s, 'Raw = original PDF, Excel or API response in external/. Extract = CSV in assumptions/. Calculation = src/lfm/model/.',
     .5, 6.80, 11.65, .22, 10.5, True, brand.accent_primary)

s = page('Run one fetch command for each priority dataset',
         'Use the staging setup on the next page before running these commands')
text(s, "$py = '.\\.venv\\Scripts\\python.exe'", .5, 2.36, 11.65, .28, 11, True, brand.accent_primary)
table(s, [
    ['Dataset', 'PowerShell command', 'Main extract'],
    ['Department', '& $py -m lfm.scripts.fetch_energy_dept --vintage 2026', 'Sales, provinces, balances, prices'],
    ['FIASA', '& $py -m lfm.scripts.fetch_fuel_sales --vintage 2026', 'Sales, imports and exports'],
    ['Economy', '& $py -m lfm.scripts.fetch_economy --vintage 2026', 'GDP, population, Treasury; Stats SA workbook on disk'],
    ['NaTIS', '& $py -m lfm.scripts.fetch_natis --vintage 2026', 'Fleet stock and registrations'],
    ['naamsa', '& $py -m lfm.scripts.fetch_naamsa --vintage 2026', 'BEV, PHEV, hybrid and market sales'],
    ['Eskom', '& $py -m lfm.scripts.fetch_eskom --vintage 2026', 'Eskom and IPP OCGT generation'],
], [1.25, 7.55, 2.85], y=2.84, height=3.32, size=11)
text(s, 'Combined refresh: & $py -m lfm.scripts.refresh_sources --vintage 2026', .5, 6.28, 11.65, .29, 12, True, brand.accent_primary)
text(s, 'Runs the six fetchers plus ACSA. Logs failed commands and compares sales; it does not collect every missing source.\nAppend --offline only to reread originals already on disk. Capture each exit code and warnings.',
     .5, 6.57, 11.65, .40, 10.5)

s = page('Keep candidate refreshes separate and test each source',
         'Candidate files first; reviewed promotion into the vintage follows later')
text(s, 'PowerShell setup', .5, 2.38, 7.0, .30, 14, True, brand.accent_primary)
setup = '''$stage = "runs/manish_fetch_$(Get-Date -Format yyyyMMdd_HHmmss)"
New-Item -ItemType Directory "$stage/assumptions" -Force | Out-Null
Copy-Item assumptions/2026 "$stage/assumptions/2026" -Recurse
$oldA = $env:LFM_ASSUMPTIONS_DIR
$oldD = $env:LFM_DATA_DIR
$env:LFM_ASSUMPTIONS_DIR = (Resolve-Path "$stage/assumptions").Path
$env:LFM_DATA_DIR = Join-Path (Get-Location) "$stage/data"
New-Item -ItemType Directory "$stage/data/raw" -Force | Out-Null'''
text(s, setup, .5, 2.86, 7.10, 2.32, 11)
text(s, 'Stats SA manual prerequisite', .5, 5.34, 7.1, .30, 14, True, brand.accent_primary)
text(s, 'Download the GDP Time series workbook into $stage/data/raw/statssa/ before the economy command. The reader uses the Annual sheet; quarterly 2026 extraction needs support. Existing raw caches may be copied into the candidate raw folder.',
     .5, 5.78, 7.1, 1.05, 12)
line(s, 7.88, 2.37, 7.88, 6.9)
text(s, 'Checks and restoration', 8.12, 2.38, 4.03, .30, 14, True, brand.accent_primary)
text(s, 'Compare old/new values, dates, units, duplicates and completeness. Preserve prior data on failed or partial fetches. Add tests for new parser support.',
     8.12, 2.85, 4.03, 1.22, 12)
text(s, 'Restore in finally if scripted:', 8.12, 4.20, 4.03, .29, 12, True)
text(s, '$env:LFM_ASSUMPTIONS_DIR = $oldA\n$env:LFM_DATA_DIR = $oldD', 8.12, 4.61, 4.03, .69, 11)
text(s, 'Then run:', 8.12, 5.46, 4.03, .28, 12, True)
text(s, '& $py -m lfm check --vintage 2026\n& $py -m pytest -q', 8.12, 5.87, 4.03, .67, 11)
text(s, 'A successful command is not numerical verification or adoption.', 8.12, 6.68, 4.03, .35, 11, True, brand.accent_primary)

s = page('Return five distinct work packages for review',
         'Checklist | Manish owns evidence collection and checks; Nigel reviews integration')
table(s, [
    ['Work package', 'Checklist: required evidence', 'Completion test'],
    ['[ ] 1 Integrity', 'Resolve provincial completeness/ties and duplicate refinery/history keys against original cells.',
     'Flag log: old/new value, reason; resolved or open with owner.'],
    ['[ ] 2 Traceability', 'Map publisher -> original -> extract -> consuming function; list originals absent from main.',
     'Exact paths and links; units, dates and engine-use status.'],
    ['[ ] 3 Demand update', 'Collect petrol/diesel sales by province after 2022; verify 2024 chart evidence and seek 2025/2026.',
     'Province/product/period; national tie; observed/estimated; gaps.'],
    ['[ ] 4 Fuel balance', 'Match actual production, imports, exports and stock movements. Resolve competing trade definitions.',
     'Same-year/product litres; balance residual explained or open.'],
    ['[ ] 5 Driver evidence', 'Complete the seven driver rows on the next page. Add and test missing retrieval/parsers.',
     'One source record per series; coverage and revisions explicit.'],
], [1.7, 6.15, 3.8], height=3.75, size=12)
text(s, 'Today: evidence and tests. After review: Nigel integrates approved changes and updates the SCR pack; lever quantification follows.',
     .5, 6.43, 11.65, .43, 12, True, brand.accent_primary)
text(s, 'Open detailed instructions and source links', .5, 6.89, 8.2, .24, 10.5, url=REPO_URL+'workstreams/WS0_governance/workplan/feedback_focus_2026-10-06.md', color=brand.accent_primary)

s = page('Collect driver evidence with one checklist row per category',
         'Data first | Record each row as sourced, partial or open; do not infer fuel litres from activity')
table(s, [
    ['Driver', 'Collect / public source', 'Keep explicit'],
    ['Passenger vehicles', 'NaTIS passenger stock/registrations; petrol/diesel split, mileage and efficiency evidence.',
     'ICE stock split and mileage may remain open.'],
    ['Freight', 'NaTIS goods-vehicle stock; Stats SA P7162 road/rail payload and available tonne-km.',
     'One revision vintage; tonnes are not tonne-km.'],
    ['Agriculture', 'Stats SA P0441 agricultural activity; sector diesel-use/intensity evidence separately.',
     'National activity; no provincial litres inferred.'],
    ['Industry', 'Stats SA P3041.2 manufacturing and P2041 mining output; separate series.',
     'Indices measure output, not fuel consumption.'],
    ['Power generation', 'Eskom and IPP OCGT generation; reported diesel burn where available.',
     'FY versus CY; GWh and litres stay separate.'],
    ['Electrification', 'naamsa BEV, PHEV and conventional hybrid new sales; fleet-stock evidence if available.',
     'Sales are a flow; HEV/PHEV still use fuel.'],
    ['Economic context', 'Stats SA real GDP; department petrol/diesel prices, latest monthly observations.',
     'Real versus nominal; no elasticity calibrated today.'],
], [1.7, 6.15, 3.8], y=2.38, height=4.0, size=11.5)
text(s, 'For every series: original file + source URL/table + extracted CSV + period/units + revision check. Missing evidence: owner and next retrieval action.',
     .5, 6.56, 11.65, .43, 11.5, True, brand.accent_primary)

bookend(source.slides[-1], {'Agree priorities': 'Return sourced data',
                           'and next steps': 'and explicit gaps',
                           'Confirm demand, routes and access': 'Review evidence before setting lever scenarios'})

# Four clickable handover sections preserve the approved chevron geometry.
sections = [('1  Priorities', 2), ('2  Files and sources', 3),
            ('3  Fetch and test', 4), ('4  Handback', 6)]
for page_number, s in enumerate(prs.slides, 1):
    if page_number in (1, len(prs.slides)):
        continue
    active = 0 if page_number == 2 else 1 if page_number == 3 else 2 if page_number <= 5 else 3
    for i, (label, target) in enumerate(sections):
        q = s.shapes.add_shape(MSO_SHAPE.CHEVRON, Inches(.5+i*2.93), Inches(.08), Inches(2.86), Inches(.42))
        q.adjustments[0] = .12
        q.fill.solid()
        q.fill.fore_color.rgb = brand.accent_primary if i == active else brand.grey_fill
        q.line.fill.background()
        tf = q.text_frame
        tf.margin_left = tf.margin_right = Inches(.12)
        tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = label
        p.alignment = PP_ALIGN.CENTER
        p.font.name = cfg.THEME_FONT
        p.font.size = Pt(13)
        p.font.bold = i == active
        p.font.color.rgb = brand.white if i == active else brand.accent_primary
        q.click_action.target_slide = prs.slides[target-1]

for s in prs.slides:
    for q in s.shapes:
        assert q.left >= 0 and q.top >= 0
        assert q.left+q.width <= prs.slide_width+5 and q.top+q.height <= prs.slide_height+5, q.name
out = QA/'Vopak_Manish_Handover_2026_10_06.pptx'
prs.save(out)
print(out)
