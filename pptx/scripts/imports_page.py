"""Present imported-volume evidence without treating residual demand as availability."""
from pptx.util import Inches
from lfm.reporting.imports_evidence import imports_evidence


def draw_imports(slide, root, text, table):
    records = imports_evidence(root.parent / 'external/sources/Liquid Fuels Model - Supply Demand, 2025 - Reatile Copy.xlsx')
    text(slide, 'South Africa | billion litres | workbook imports and Python import requirements', .55, 1.8, 11.5, .4, 16)
    rows = ['| Fuel | 2022 recorded imports | Excel 2030 H | Excel 2030 L | Python 2030 H | Python 2030 L |']
    for r in records:
        rows.append('| ' + r['fuel'] + ' | ' + ' | '.join(f'{r[k]/1e9:.2f}' for k in ['historical','excel_h','excel_l','high_demand','low_demand']) + ' |')
    shape = table(slide, rows, y=2.45, height=1.7, widths=[1.1,2.15,2.05,2.05,2.05,2.05], size=15)
    for row in shape.table.rows:
        for cell in row.cells:
            cell.margin_top = cell.margin_bottom = Inches(.025)
    text(slide, 'H/L identify demand cases with linked production assumptions; import volumes can move differently by fuel.', .55, 4.35, 11.5, .5, 13, True)
    comparisons=['| Fuel | Python minus Excel: H | Python minus Excel: L | Comparison in both cases |']
    for r in records:
        comparisons.append(f"| {r['fuel']} | {(r['high_demand']-r['excel_h'])/1e9:+.2f} | {(r['low_demand']-r['excel_l'])/1e9:+.2f} | {'Python higher' if r['fuel']=='Diesel' else 'Excel higher'} |")
    shape=table(slide,comparisons,y=4.95,height=1.12,widths=[1.1,3.15,3.15,4.05],size=12)
    for row in shape.table.rows:
        for cell in row.cells:
            cell.margin_top=cell.margin_bottom=Inches(.015)
    text(slide, 'Differences use unrounded values. Python shows demand less domestic production, including both diesel grades. Exports, stock changes and deliverable import limits remain to add. Neither model yet runs the independent nine-case matrix.', .55, 6.2, 11.5, .5, 11.5)
    text(slide, 'Workbook history is unverified; Notes B7 flags partial 2023 coverage, so 2022 is shown. Excel forecasts contain external workbook links.', .55, 6.85, 11.5, .2, 9)
