"""National history, combined provincial exhibit, site capacity and route economics.

Presentation transformations of existing staged evidence only; no forecast engine changes.
"""
import csv
import json
import re
import sys
from pathlib import Path

import yaml
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.chart import XL_CHART_TYPE, XL_MARKER_STYLE, XL_LEGEND_POSITION
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from brand_pptx import BrandStyle, add_themed_chart
from brand_configs import vopak as cfg
from convergence_feedback import text, replace, bar
from convergence_story_order import native_table
from supply_review_pages import line

ROOT = Path(__file__).resolve().parents[1]
BRAND = BrandStyle.from_module(cfg)
INK = BRAND.ink
BLUE = BRAND.accent_primary
SECOND = BRAND.accent_secondary


def read(path):
    return list(csv.DictReader(path.open(encoding='utf-8-sig')))


def drop(q):
    q._element.getparent().remove(q._element)


def clear(s):
    for q in list(s.shapes):
        if Inches(1.7) <= q.top < Inches(7.04): drop(q)


def title(s, value):
    replace(s.shapes.title, value)


def footer(s, value):
    for q in s.shapes:
        if q.name == 'Unified source footer':
            replace(q, value)


def chart(s, kind, x, y, w, h, years, series, maximum, colours):
    c = add_themed_chart(s, kind, Inches(x), Inches(y), Inches(w), Inches(h),
                         [str(v) for v in years], series, show_legend=False,
                         value_axis_format='0', axis_font_size=10, brand=BRAND)
    c.value_axis.minimum_scale = 0
    c.value_axis.maximum_scale = maximum
    for sr, colour in zip(c.series, colours):
        sr.format.line.color.rgb = colour
        sr.format.line.width = Pt(2)
        if kind == XL_CHART_TYPE.AREA_STACKED:
            sr.format.fill.solid(); sr.format.fill.fore_color.rgb = colour
        else:
            sr.marker.style = XL_MARKER_STYLE.CIRCLE
            sr.marker.size = 4
            sr.marker.format.fill.solid(); sr.marker.format.fill.fore_color.rgb = colour
            sr.marker.format.line.color.rgb = colour
    return c


def national(s):
    clear(s)
    years = list(range(2019, 2026))
    ts = ROOT.parent / 'assumptions/2026/timeseries'
    sales = read(ts / 'fuel_sales_department.csv')
    fiasa = read(ts / 'fuel_sales_fiasa.csv')
    trade = read(ROOT / 'story/evidence_2026_10_06/fuel_trade_sars.csv')
    output = {}
    for product in ['petrol', 'diesel']:
        net, imports, exports = [], [], []
        for year in years:
            r = [r for r in trade if int(r['period']) == year and r['product'] == product and r['unit'] == 'litres']
            assert len(r) == 2 and all(int(x['months_reported']) == 12 for x in r)
            net.append(sum(float(x['value']) * (1 if x['flow'] == 'import' else -1) for x in r) / 1e9)
            imports.append(next(float(x['value']) / 1e9 for x in r if x['flow'] == 'import'))
            exports.append(next(float(x['value']) / 1e9 for x in r if x['flow'] == 'export'))
        observed = {int(r['period']): float(r['value']) / 1e9 for r in sales if r['product'] == product and int(r['quarters_reported']) == 4}
        last = [r for r in fiasa if r['product'] == product and r['period'] == '2024']
        selected = max(last, key=lambda r: int(r['source_report']))
        output[product] = {'department_sales': [observed.get(y) for y in years],
                           'fiasa_2024': [float(selected['value']) / 1e9 if y == 2024 else None for y in years],
                           'imports': imports, 'exports': exports,
                           'net_imports': net, 'net_import_change_pct': (net[-1] / net[-2] - 1) * 100}
    title(s, f"Net imports rose in 2025: diesel by {output['diesel']['net_import_change_pct']:.0f}% and petrol by {output['petrol']['net_import_change_pct']:.0f}%")
    text(s, 'National annual volumes | bn litres | complete years only', .5, 1.78, 11.5, .3, 14, True, INK)
    for i, product in enumerate(['petrol', 'diesel']):
        x = .5 + i * 5.95
        text(s, product.capitalize(), x, 2.23, 5.5, .28, 15, True, BLUE)
        d = output[product]
        subtitle = ('Imports reached 4.45 bn L in 2025; exports were 0.80 bn L'
                    if product == 'petrol' else 'Imports reached 12.25 bn L in 2025; exports were 0.75 bn L')
        text(s, subtitle, x, 2.62, 5.5, .38, 11, color=INK)
        for offset, label, col in [(0, 'Sales', BLUE), (1.6, 'Imports', SECOND), (3.2, 'Exports', INK)]:
            line(s, (x + offset, 3.20), (x + offset + .27, 3.20), col, 2)
            text(s, label, x + offset + .36, 3.08, 1.15, .25, 10, color=INK)
        c = chart(s, XL_CHART_TYPE.LINE_MARKERS, x, 3.45, 5.5, 2.90, years,
                  [('Department sales', d['department_sales']), ('FIASA 2024 sales', d['fiasa_2024']),
                   ('Imports', d['imports']), ('Exports', d['exports'])],
                  15, [BLUE, BLUE, SECOND, INK])
        for axis in [c.category_axis, c.value_axis]:
            axis.has_major_gridlines = False
            axis.has_minor_gridlines = False
        c.series[1].marker.style = XL_MARKER_STYLE.DIAMOND
        c.series[1].marker.size = 8
        text(s, f"2025 net imports (imports less exports): {d['net_imports'][-1]:.2f} bn L", x, 6.55, 5.5, .28, 11, True, BLUE)
    footer(s, 'Sources: departmental sales 2019-2023; FIASA 2025 report for 2024 sales (diamond; revisions unresolved); SARS trade 2019-2025.\nSales are a consumption proxy. Production/stocks remain unreconciled; 2025 sales unavailable here. 2026 YTD excluded.')
    s.notes_slide.notes_text_frame.text += '\nNational time-series evidence: ' + json.dumps(output)
    return output


def provincial(s, history):
    # Retain the existing native map and reflow its complete left exhibit.
    for q in list(s.shapes):
        if Inches(1.7) <= q.top < Inches(7.04):
            if q.left >= Inches(7.7) or q.top < Inches(2.2):
                drop(q); continue
            q.left = Inches(.5) + int((q.left - Inches(.5)) * .78)
            # Keep the legends high; shift the larger map into the former blank space below.
            map_shape = q.top >= Inches(2.9)
            q.top = Inches(2.5 if not map_shape else 2.95) + int((q.top - Inches(2.2)) * .78)
            q.width = int(q.width * .78)
            q.height = int(q.height * .78)
            if q.has_text_frame and q.text:
                for p in q.text_frame.paragraphs:
                    if p.font.size: p.font.size = Pt(max(7, p.font.size.pt * .85))
                    for r in p.runs:
                        if r.font.size: r.font.size = Pt(max(7, r.font.size.pt * .85))
    title(s, 'Gauteng leads provincial sales; Gauteng, KZN and Western Cape held 69% in 2022')
    text(s, 'Where demand sits | 2022, bn litres', .5, 1.78, 5.2, .35, 14, True, INK)
    text(s, 'How it changed | 2013-2022, bn litres/year', 6.05, 1.78, 6.0, .35, 14, True, INK)
    old = next(q.chart for q in history.shapes if q.has_chart)
    years = [c.label for c in old.plots[0].categories]
    series = [(r.name, list(r.values)) for r in old.series]
    # Do not draw connected observations across years with unresolved source coverage.
    for _, vals in series:
        for year in ['2014', '2018']: vals[years.index(year)] = None
    cols = [BLUE, SECOND, RGBColor.from_string(cfg.THEME_COLOURS['accent4']),
            RGBColor.from_string('809CC7'), RGBColor.from_string('3D619D'), RGBColor.from_string('767676'),
            RGBColor.from_string('BACCE4'), RGBColor.from_string('A0A0A0'), RGBColor.from_string('BDBEC1')]
    c = chart(s, XL_CHART_TYPE.LINE_MARKERS, 6.05, 2.92, 6.0, 3.24, years, series, 8, cols)
    for axis in [c.category_axis, c.value_axis]:
        axis.has_major_gridlines = False
        axis.has_minor_gridlines = False
    text(s, 'Gaps are withheld observations, not demand declines:', 6.05, 2.25, 6.0, .25, 10, True, BLUE)
    text(s, '2014: source conflict  |  2018: incomplete coverage', 6.05, 2.57, 6.0, .25, 10, color=INK)
    short = ['GP', 'KZN', 'WC', 'MP', 'EC', 'FS', 'NW', 'LP', 'NC']
    for i, (label, col) in enumerate(zip(short, cols)):
        x = 6.1 + (i % 5) * 1.18; y = 6.24 + (i // 5) * .28
        line(s, (x, y + .09), (x + .18, y + .09), col, 2)
        text(s, label, x + .25, y, .75, .22, 9, color=INK)
    text(s, 'Same province codes on map and chart; map shade measures volume.', .5, 6.73, 11.5, .23, 10, color=INK)
    footer(s, 'Sources: departmental provincial petrol/diesel sales; staged 2013-2022 history; 2022 geographic boundaries as previously cited. Jet excluded.\n2014 source conflict and incomplete 2018 coverage are omitted from the trend. No held-share 2024 estimates are shown.')
    s.notes_slide.notes_text_frame.text += '\nCombined with former page 6. Same chart observations; 2014 and 2018 suppressed pending source decisions. Map legend is a volume scale, chart legend identifies provinces.'


def refinery(s):
    clear(s)
    ts = ROOT.parent / 'assumptions/2026'
    rows = read(ts / 'timeseries/refinery_capacity_reported.csv')
    settings = yaml.safe_load((ts / 'review_capacity_scenarios.yaml').read_text())['capacity_comparison']['value']
    addition_year = settings['illustrative_fid_year'] + settings['construction_months'] // 12
    years = list(range(2016, settings['horizon_year'] + 1))
    assets = ['Sasol', 'Natref', 'Astron Energy', 'PetroSA', 'Enref', 'Sapref']
    values = {(r['asset'], int(r['period'])): float(r['value']) / 1000 for r in rows}
    series = [(a, [values[a, min(y, 2025)] for y in years]) for a in assets]
    series.append(('SAPREF / CEF proposal', [settings['proposed_addition_bpd'] / 1000 if y >= addition_year else 0 for y in years]))
    title(s, f'Enref, PetroSA and SAPREF explain the capacity decline; the CEF case adds capacity in {addition_year}')
    text(s, 'Capacity by refinery | thousand bbl/day | all products', .5, 1.78, 11.5, .3, 14, True, INK)
    cols = [BLUE, SECOND, RGBColor.from_string('809CC7'), RGBColor.from_string('E3EBF6'),
            RGBColor.from_string('767676'), RGBColor.from_string('404040'), BRAND.accent_highlight]
    for i, (label, col) in enumerate(zip(assets + ['SAPREF / CEF proposal'], cols)):
        x = .5 + (i % 4) * 2.0; y = 2.27 + (i // 4) * .29
        bar(s, x, y + .03, .13, .13, col, 'Refinery legend ' + label)
        text(s, label, x + .2, y, 1.78, .24, 9, color=INK)
    c = chart(s, XL_CHART_TYPE.AREA_STACKED, .5, 3.0, 8.0, 3.35, years, series, 800, cols)
    skip = OxmlElement('c:tickLblSkip'); skip.set('val', '2'); c.category_axis._element.append(skip)
    text(s, '2016-2025: reported capacity | 2026 onward: held-flat base + conditional addition', .5, 6.51, 8.0, .4, 10, color=INK)
    text(s, '358 → 758', 8.8, 2.63, 3.1, .58, 25, True, BLUE)
    text(s, 'thousand bbl/day in the conditional case', 8.8, 3.22, 3.1, .5, 12, color=INK)
    text(s, f"{settings['illustrative_fid_year']} assumed FID\n+ {settings['construction_months']} months construction\n= {addition_year} assumed availability", 8.8, 3.97, 3.1, 1.0, 13, True, INK)
    text(s, 'No-addition case stays at 358.\nThe CEF project is not committed capacity; timing is an existing reporting assumption.', 8.8, 5.28, 3.1, 1.13, 12, color=INK)
    footer(s, 'Sources: FIASA 2025 p49, refinery_capacity_reported.csv; registered review_capacity_scenarios.yaml; CEF proposal as previously sourced.\nReported nameplate footprint is not actual output or operating availability. Source dashes are excluded from reported totals. No model inputs changed.')
    s.notes_slide.notes_text_frame.text += '\nNamed-site stacking: ' + json.dumps(dict(zip([a for a, _ in series], [v for _, v in series])))
    return {'years': years, 'series': series, 'assumed_addition_year': addition_year}


def economics(s):
    # Preserve the full illustrative map on the left; replace the old prose panel.
    for q in list(s.shapes):
        if Inches(1.7) <= q.top < Inches(7.04) and q.left >= Inches(7.7): drop(q)
    title(s, 'A viable customer route must be competitive and still earn the supplier\'s required margin')
    text(s, 'Two tests for each customer and product', 8.12, 1.78, 4.03, .42, 14, True, INK)
    text(s, '1 | Competitive breakpoint', 8.12, 2.36, 4.03, .29, 13, True, BLUE)
    text(s, 'Delivered cost via Durban / Lesedi\n= lowest feasible alternative delivered cost', 8.12, 2.79, 4.03, .63, 12, True, INK)
    text(s, 'Above this cost, the route loses its cost advantage. Compare the same product, destination and service terms.', 8.12, 3.46, 4.03, .61, 11, color=INK)
    text(s, '2 | Margin breakpoint', 8.12, 4.23, 4.03, .29, 13, True, BLUE)
    text(s, 'Maximum storage + transport cost\n= delivered price − fuel cost\n− other costs − required supplier margin', 8.12, 4.66, 4.03, .82, 12, True, INK)
    text(s, 'Above this allowance, the route fails the margin target even if it is the cheapest option.', 8.12, 5.58, 4.03, .53, 11, color=INK)
    text(s, 'Thresholds not yet quantified', 8.12, 6.24, 4.03, .27, 12, True, BLUE)
    text(s, 'Need customer prices, route quotes, handling, stock costs and required margin. Owner: Nigel / Manish.', 8.12, 6.59, 4.03, .39, 9, color=INK)
    footer(s, 'Map: existing illustrative road costs only; grid cells are not customers. Pipeline/rail costs, tariffs, storage and rights remain unverified.\nBoth tests concern supplier delivered economics, not Vopak terminal margin. No numerical breakpoint or validated catchment is claimed.')
    s.notes_slide.notes_text_frame.text += '\nApproved scope: both competitive and margin tests for each feasible route to the same customer/product. Include acquisition, storage/handling, transport, border costs where relevant, stock financing and losses exactly once. Competitive test requires feasibility and comparable service. Profitability is supplier economics, distinct from Vopak terminal margin. Owner Nigel/Manish; resolve before numerical route breakpoint or customer capture is presented.'


def main(source, destination):
    deck = Presentation(source); assert len(deck.slides) == 31
    original = list(deck.slides)
    national_data = national(original[3])
    provincial(original[4], original[5])
    refinery_data = refinery(original[7])
    economics(original[8])
    # Merged page 6 references now land on page 5, preserving internal hyperlinks.
    old_part = original[5].part; combined = original[4].part
    for s in original:
        for rel in s.part.rels.values():
            if not rel.is_external and rel.target_part == old_part:
                rel._target = combined
                for cached in ('target_part', 'target_partname', 'target_ref'):
                    rel.__dict__.pop(cached, None)
    item = deck.slides._sldIdLst[5]
    deck.part.drop_rel(item.rId); deck.slides._sldIdLst.remove(item)
    mapping = {n: (n if n < 6 else 5 if n == 6 else n - 1) for n in range(1, 32)}
    pages = {s.part: i for i, s in enumerate(deck.slides, 1)}
    for i, s in enumerate(deck.slides, 1):
        frames = [q.text_frame for q in s.shapes if q.has_text_frame] + [c.text_frame for q in s.shapes if q.has_table for r in q.table.rows for c in r.cells]
        for tf in frames:
            for p in tf.paragraphs:
                for r in p.runs:
                    linked = False
                    for h in r._r.xpath('.//a:hlinkClick'):
                        rid = h.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                        if rid and not s.part.rels[rid].is_external:
                            target = s.part.rels[rid].target_part
                            if target in pages and re.fullmatch(r'\s*(?:/\s*)?\d+\s*', r.text):
                                r.text = (' / ' if '/' in r.text else '') + str(pages[target]); linked = True
                    if not linked:
                        r.text = re.sub(r'\b(page |on p)(\d+)\b', lambda m: m[1] + str(mapping.get(int(m[2]), int(m[2]))), r.text)
        for q in s.shapes:
            if q.name == 'Slide Number Placeholder':
                q.text = str(i)
                for p in q.text_frame.paragraphs: p.font.name = cfg.THEME_FONT; p.font.size = Pt(10)
    # Overview's duplicate 5 / 5 reference is collapsed after the merge.
    table = next(q.table for q in deck.slides[2].shapes if q.has_table)
    p = table.cell(2, 4).text_frame.paragraphs[0]
    seen = set()
    for r in list(p.runs):
        if re.fullmatch(r'\s*(?:/\s*)?5\s*', r.text):
            if 5 in seen: r._r.getparent().remove(r._r)
            seen.add(5)
    out = Path(destination)
    if out.exists(): raise FileExistsError(out)
    deck.save(out)
    out.with_suffix('.revision.json').write_text(json.dumps({'source': source, 'old_to_new': mapping, 'national': national_data, 'refinery': refinery_data, 'logistics': 'Both breakpoints specified; numerical thresholds unresolved pending customer economics.'}, indent=2), encoding='utf-8')
    print(out)


if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
