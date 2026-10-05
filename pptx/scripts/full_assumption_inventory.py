"""Present every register entry without introducing model calculations.

Identical successive annual values are losslessly represented as year ranges.
Duplicate CSV observations are retained through multiplicities, not discarded.
"""
import csv
import ast
import json
import re
from collections import defaultdict, Counter
from pptx.util import Inches, Pt
from brand_pptx import add_themed_slide


FUEL = {
    'vehicles': 'Petrol and road diesel', 'aviation': 'Jet A1',
    'generation': 'Diesel for power', 'industrial': 'Diesel 50 ppm',
    'agriculture': 'Diesel 50 ppm', 'marine': 'Marine diesel and supplementary fuel oil',
    'supply': 'Domestic petrol, diesel and jet production',
    'macro': 'Shared drivers / conversions; use depends on module',
}


def value(raw):
    decoded = json.loads(raw)
    return 'Missing (null)' if decoded is None else str(decoded)


def inventory_pages(root):
    with (root.parent / 'governance/assumption_register.csv').open(encoding='utf-8-sig', newline='') as f:
        register = list(csv.DictReader(f))
    groups = defaultdict(list)
    for row in register:
        groups[row['register_group']].append(row)
    pages = []
    covered = []
    for group, entries in groups.items():
        module = entries[0]['assumption'].split('.')[0]
        series = '.csv[' in entries[0]['assumption']
        records = []
        if series:
            observations = defaultdict(lambda: defaultdict(list))
            for entry in entries:
                match = re.search(r'csv\[\d+:(.*)\]$', entry['assumption'])
                dims = json.loads(match[1])
                observations[(dims['country'], int(dims['period']))][dims['scenario']].append(entry)
            by_country = defaultdict(list)
            for (country, year), scenarios in sorted(observations.items()):
                cells = []
                ids = []
                for scenario in ('shared', 'high_demand', 'low_demand'):
                    items = scenarios.get(scenario, [])
                    counts = Counter(value(item['value']) for item in items)
                    cells.append('; '.join(v + (f' [x{n}]' if n > 1 else '') for v, n in counts.items()) or '—')
                    ids.extend(item['id'] for item in items)
                by_country[country].append((year, cells, ids))
            for country, yearly in by_country.items():
                start = end = None
                last = None
                ids = []
                def emit():
                    if start is not None:
                        period = str(start) if start == end else f'{start}–{end}'
                        records.append(([country, period, *last], list(ids)))
                for year, cells, row_ids in yearly:
                    if last == cells and year == end + 1:
                        end = year
                        ids.extend(row_ids)
                    else:
                        emit()
                        start = end = year
                        last = cells
                        ids = list(row_ids)
                emit()
            headers = ['Country / asset', 'Year(s)', 'Shared', 'High demand', 'Low demand']
            widths = [1.6, 1.05, 3.0, 3.0, 3.0]
            if group == 'REG-SUPPLY-REFINERY_UTILISATION':
                # Malformed source rows have several raw alternatives per year.
                # Give these the space they need rather than wrapping into footers.
                headers = ['Country / asset', 'Year(s)', 'Shared', 'High demand: raw alternatives', 'Low']
                widths = [1.6, 1.05, .8, 6.95, 1.25]
        else:
            # Collapse only identical leaf/value declarations across countries.
            scalar_groups = defaultdict(list)
            for entry in entries:
                tail = entry['assumption'].split('.', 2)[-1]
                match = re.match(r'by_country\.([^.]+)(.*)', tail)
                if match:
                    country, parameter = match[1], match[2].lstrip('.') or 'value'
                else:
                    country, parameter = 'Shared', tail
                scalar_groups[(parameter, entry['value'])].append((country, entry))
            for (parameter, raw), items in scalar_groups.items():
                countries = ', '.join(country for country, _ in items)
                records.append(([parameter.replace('by_scenario.', ''), countries, value(raw)],
                                [item['id'] for _, item in items]))
            headers = ['Parameter / scenario', 'Coverage', 'Declared value']
            widths = [5.35, 2.6, 3.7]
        for offset in range(0, len(records), 16):
            chunk = records[offset:offset + 16]
            ids = [identifier for _, row_ids in chunk for identifier in row_ids]
            covered.extend(ids)
            pages.append(dict(group=group, module=module, headers=headers, widths=widths,
                              rows=[cells for cells, _ in chunk], ids=ids, entries=entries,
                              part=offset // 16 + 1, parts=(len(records) + 15) // 16,
                              series=series))
    assert Counter(covered) == Counter(row['id'] for row in register), 'Incomplete inventory coverage'
    return pages, register


def add_inventory(prs, root, brand, cfg, text, table):
    pages, register = inventory_pages(root)
    index_page = len(prs.slides) + 1
    slide = add_themed_slide(prs, 'Header only', brand=brand,
                             title='Full assumption inventory: scope and navigation', slide_number_idx=12)
    shape = slide.shapes.title
    shape.left, shape.top = Inches(.5), Inches(.64)
    shape.width, shape.height = Inches(11.55), Inches(.9)
    for p in shape.text_frame.paragraphs:
        p.font.name = cfg.THEME_FONT
        p.font.size = Pt(29)
        p.font.bold = True
        p.font.color.rgb = brand.ink
    text(slide, 'REFERENCE  |  Complete registered model inputs', .5, .12, 11.5, .35, 13, True)
    text(slide, f'{len(register):,} entries | 39 groups | exact declared values, including missing inputs and duplicate records',
         .55, 1.8, 11.5, .35, 14)
    lines = ['| Input family | Fuel / calculation affected | PDF pages |']
    for module in dict.fromkeys(page['module'] for page in pages):
        positions = [index_page + 1 + i for i, page in enumerate(pages) if page['module'] == module]
        lines.append(f'| {module.title()} | {FUEL[module]} | {min(positions)}–{max(positions)} |')
    lines.append(f'| Calculation conventions | Embedded constants and implementation rules | {index_page + len(pages) + 1} |')
    shape = table(slide, lines, y=2.35, height=3.4, widths=[2.1, 7.4, 2.15], size=13)
    for row in shape.table.rows:
        for cell in row.cells:
            for p in cell.text_frame.paragraphs:
                p.space_after = Pt(0)
    text(slide, 'Scope: every registered scalar and CSV observation in the current 2026 draft. Declared inputs can be unused; inclusion is not validation.',
         .55, 6.2, 11.5, .5, 12)
    text(slide, 'M, available imports and WS5 capacity/access inputs remain to build. Embedded conventions follow the register inventory; EXC-CODE remains open.',
         .55, 6.72, 11.5, .3, 11)
    text(slide, 'Source: governance/assumption_register.csv; assumptions/2026; CLAUDE.md; GATE_CHECKLIST.md. Draft, unreviewed.',
         .5, 7.17, 11.0, .2, 8)
    slide.notes_slide.notes_text_frame.text = 'Coverage is checked by register ID. No engine formulas or assumptions changed.'
    manifest = []
    for page in pages:
        group = page['group']
        label = group.removeprefix('REG-').replace('-', ' · ').replace('_', ' ').title()
        title = f'Assumption inventory: {label}'
        slide = add_themed_slide(prs, 'Header only', brand=brand, title=title, slide_number_idx=12)
        shape = slide.shapes.title
        shape.left, shape.top = Inches(.5), Inches(.64)
        shape.width, shape.height = Inches(11.55), Inches(.9)
        for p in shape.text_frame.paragraphs:
            p.font.name = cfg.THEME_FONT
            p.font.size = Pt(27)
            p.font.bold = True
            p.font.color.rgb = brand.ink
        text(slide, 'REFERENCE  |  Complete registered model inputs', .5, .12, 11.5, .35, 13, True)
        text(slide, f"2026 draft | {FUEL[page['module']]} | {group} | {page['part']}/{page['parts']}",
             .55, 1.7, 11.5, .4, 12)
        units = '; '.join(dict.fromkeys(row['unit'] or 'Not recorded' for row in page['entries']))
        text(slide, 'Units: ' + units, .55, 2.13, 11.5, .42, 11)
        lines = ['| ' + ' | '.join(page['headers']) + ' |']
        lines += ['| ' + ' | '.join(cell.replace('|', '/') for cell in row) + ' |' for row in page['rows']]
        shape = table(slide, lines, y=2.7, height=min(3.7, .24 * len(lines)),
                      widths=page['widths'], size=11)
        for row in shape.table.rows:
            for cell in row.cells:
                cell.margin_top = cell.margin_bottom = Inches(.015)
                cell.margin_left = cell.margin_right = Inches(.08)
                for p in cell.text_frame.paragraphs:
                    p.space_after = Pt(0)
                    p.line_spacing = 1.0
        dates = '; '.join(dict.fromkeys(row['source_date'] or 'Not recorded' for row in page['entries']))
        text(slide, 'Source date: ' + dates + ' | Owner: Nigel | Review: unreviewed | Confidence: unassessed',
             .55, 6.43, 11.5, .28, 10)
        note = ('Year ranges repeat the exact value shown. [xN] retains duplicate records per year; — means no declaration.'
                if page['series'] else 'Missing regional values are declarations, not zeroes. Coverage combines only identical leaf/value entries.')
        text(slide, note, .55, 6.77, 11.5, .25, 10)
        source = '; '.join(dict.fromkeys(row['source'] for row in page['entries']))
        text(slide, 'Source: governance/assumption_register.csv; assumptions/2026. ' + source,
             .5, 7.17, 11.0, .2, 7)
        slide.notes_slide.notes_text_frame.text = json.dumps(page, ensure_ascii=False, indent=2)
        manifest.append({'page': len(prs.slides), 'group': group, 'register_ids': page['ids']})
    def constant(relative_path, name):
        tree = ast.parse((root.parent / relative_path).read_text(encoding='utf-8'))
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
                return ast.literal_eval(node.value)
        raise ValueError(f'Missing code constant: {name}')
    time_path = 'src/lfm/model/core/time.py'
    vehicles_path = 'src/lfm/model/demand/vehicles.py'
    supply_path = 'src/lfm/model/supply/flows.py'
    generation_path = 'src/lfm/model/demand/generation.py'
    slide = add_themed_slide(prs, 'Header only', brand=brand,
                             title='Calculation conventions outside the input register', slide_number_idx=12)
    shape = slide.shapes.title
    shape.left, shape.top = Inches(.5), Inches(.64)
    shape.width, shape.height = Inches(11.55), Inches(.9)
    for p in shape.text_frame.paragraphs:
        p.font.name = cfg.THEME_FONT
        p.font.size = Pt(29)
        p.font.bold = True
        p.font.color.rgb = brand.ink
    text(slide, 'REFERENCE  |  Implementation choices and constants', .5, .12, 11.5, .35, 13, True)
    text(slide, 'These choices also affect results. They are current code behaviour, not approved assumptions.',
         .55, 1.8, 11.5, .4, 14)
    rows = [
        ['Convention', 'Current implementation / value', 'Fuel affected'],
        ['Forecast horizon', f"{constant(time_path, 'START_YEAR')}–{constant(time_path, 'END_YEAR')}; inclusive annual/monthly dimensions", 'All products'],
        ['Vehicle opening stock', f"Empty cohort book at {constant(vehicles_path, 'HISTORY_START')}; fleet accumulated from regression-based additions", 'Petrol, road diesel'],
        ['Vehicle efficiency', 'Cumulative improvement sets consumption of new cohorts; held fixed for cohort life', 'Petrol, road diesel'],
        ['Missing / negative drivers', 'Vehicles use zero for missing GDP-year additions; vehicle and jet regression outputs clamped at zero', 'Petrol, diesel, jet'],
        ['Held sector method', 'Industry, agriculture and marine scale baseline volume with GDP per capita and elasticity', 'Diesel, marine fuel oil'],
        ['Power conversions', f"{constant(generation_path, 'HOURS_PER_DAY')} hours/day; {constant(generation_path, 'MWH_TO_MJ')} MJ/MWh", 'Power diesel'],
        ['Domestic supply conversions', f"{constant(supply_path, 'DAYS_PER_YEAR')} days/year; {constant(supply_path, 'KBPD_TO_BPD')} bpd/kbpd", 'Petrol, diesel, jet'],
        ['Duplicate production records', 'First non-null value per asset/year is selected; raw alternatives remain in the inventory', 'Domestic production'],
        ['Balance and monthly allocation', 'Balance is demand less domestic production; core annual demand flat-allocated across 12 months', 'All current products'],
    ]
    shape = table(slide, ['| ' + ' | '.join(row) + ' |' for row in rows], y=2.35,
                  height=4.0, widths=[2.6, 6.85, 2.2], size=12)
    for row in shape.table.rows:
        for cell in row.cells:
            cell.margin_top = cell.margin_bottom = Inches(.025)
            for p in cell.text_frame.paragraphs:
                p.space_after = Pt(0)
    text(slide, 'Source behaviour is documented here; no code, registered assumption or calculation has been changed.',
         .55, 6.77, 11.5, .25, 11)
    text(slide, 'Source: src/lfm/model/core/time.py; demand/vehicles.py, aviation.py, generation.py, _held.py; supply/flows.py. EXC-CODE / EXC-LOGIC open.',
         .5, 7.17, 11.0, .2, 8)
    slide.notes_slide.notes_text_frame.text = 'Numeric constants extracted from source AST; implementation descriptions checked against current engine.'
    out = root / 'qa/pdf-review'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'assumption-inventory-coverage.json').write_text(json.dumps({
        'register_entries': len(register), 'groups': len({r['register_group'] for r in register}),
        'inventory_pages': len(pages), 'coverage': manifest,
        'scope': 'Every current registered scalar and CSV observation. This does not certify code constants or future WS5 inputs.'
    }, indent=2), encoding='utf-8')
    return len(pages) + 2
