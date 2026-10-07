"""Build the 7 October hand-back deck from Manish to Nigel.

Follows the five priorities on page 24 of the Convergence pack (Manish's focus,
7 October): national balance, forecast levers, sector baselines, tank handling
and a reviewable hand-back. Sections are added as each output is ready.

Starts from the archived Week 1 pack so the Vopak master, cover and closing
pages are the supplied ones. Uses python-pptx only. Balance figures are read
from the balance file built by ``python -m lfm.scripts.build_fuel_balance``;
figures typed here carry their source in the row. Reads no model input and
changes none.

    python pptx/scripts/build_manish_handback_2026_10_07.py
"""
import csv
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_MARKER_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import nsdecls, qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SOURCE = ROOT / "output/delivered/archive/2026-10-06_storyline/Vopak_Week1_Analytical_Pack_2026_10_06.pptx"
OUT = ROOT / "output/delivered/supporting/Vopak_Manish_Handback_2026_10_07.pptx"
BALANCE = REPO / "workstreams/WS1_data_validation/fuel_balance_petrol_diesel_2009_2025_2026-10-06.csv"

FONT = "Lato"
BLUE = RGBColor.from_string("0A2373")
INK = RGBColor.from_string("11151A")
WHITE = RGBColor.from_string("FFFFFF")
GREY_FILL = RGBColor.from_string("EEEEEE")
GREY_LINE = RGBColor.from_string("7A828C")
RULE_HEAD = RGBColor.from_string("A0A0A0")
LEFT, WIDTH = 0.5, 11.65
NOTE = ("Source: fuel_balance_2026-10-06.md and its table on manish-branch, rebuilt 7 October 2026. "
        "Analyst's position, pending Nigel's review.")

prs = Presentation(SOURCE)


def drop_slide(index: int) -> None:
    ids = prs.slides._sldIdLst
    item = ids[index]
    prs.part.drop_rel(item.rId)
    ids.remove(item)


def text(slide, value, x, y, w, h, size=12, bold=False, color=None):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = Inches(0.025)
    frame.margin_top = frame.margin_bottom = 0
    for i, part in enumerate(value.split("\n")):
        p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        p.text = part
        p.font.name, p.font.size, p.font.bold = FONT, Pt(size), bold
        p.font.color.rgb = color or INK
        p.space_after = Pt(3)
    return box


def rule(slide, y):
    line = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT, Inches(LEFT), Inches(y), Inches(LEFT + WIDTH), Inches(y))
    line.line.color.rgb = RULE_HEAD
    line.line.width = Pt(0.6)


def bottom_rule(cell):
    """No cell borders except a thin grey rule underneath, as in the Week 1 pack."""
    props = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        for old in props.findall(qn(tag)):
            props.remove(old)
    lines = [f'<a:{tag} {nsdecls("a")} w="0"><a:noFill/></a:{tag}>' for tag in ("lnL", "lnR", "lnT")]
    lines.append(f'<a:lnB {nsdecls("a")} w="5080"><a:solidFill><a:srgbClr val="B8B8B8"/></a:solidFill></a:lnB>')
    # The schema wants the four lines first, before any fill.
    for position, xml in enumerate(lines):
        props.insert(position, etree.fromstring(xml))


def table(slide, rows, widths, x=LEFT, y=2.22, height=3.9, size=11, numeric_from=None):
    shape = slide.shapes.add_table(len(rows), len(widths), Inches(x), Inches(y),
                                   Inches(sum(widths)), Inches(height))
    grid = shape.table
    style = shape._element.graphic.graphicData.tbl.tblPr
    style.set("firstRow", "0")
    style.set("bandRow", "0")
    for child in list(style):
        style.remove(child)
    for column, width in zip(grid.columns, widths):
        column.width = Inches(width)
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            cell = grid.cell(i, j)
            cell.text = value
            cell.margin_left = cell.margin_right = Inches(0.07)
            cell.margin_top, cell.margin_bottom = Inches(0.06), Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.TOP
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE
            bottom_rule(cell)
            for p in cell.text_frame.paragraphs:
                p.font.name, p.font.size = FONT, Pt(size)
                p.font.bold = i == 0 or j == 0
                p.font.color.rgb = BLUE if j == 0 else INK
                p.space_after = Pt(1)
                if numeric_from is not None and j >= numeric_from:
                    p.alignment = PP_ALIGN.RIGHT
    return grid


SECTIONS = ("1  National balance", "2  Forecast levers", "3  Sector baselines", "4  Tank handling", "5  Hand-back")
pages: list[tuple] = []          # (slide, section index)


def page(section, title, subtitle):
    layout = next(item for item in prs.slide_layouts if item.name == "Header only")
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = title
    text(slide, subtitle, LEFT, 1.78, WIDTH, 0.3, 13, True)
    rule(slide, 2.10)
    text(slide, NOTE, LEFT, 7.16, 10.6, 0.2, 8)
    text(slide, "Strictly Confidential", LEFT, 7.34, 2.2, 0.14, 7)
    pages.append((slide, section))
    return slide


def line_chart(slide, title, years, series, x, y, w, h):
    """Two-line chart, billion litres. ``series`` is ``[(name, values, colour, dashed)]``."""
    data = CategoryChartData()
    data.categories = [str(year) for year in years]
    for name, values, _, _ in series:
        data.add_series(name, values)
    frame = slide.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(x), Inches(y), Inches(w), Inches(h), data)
    chart = frame.chart
    chart.font.name, chart.font.size = FONT, Pt(10)
    chart.font.color.rgb = INK
    chart.has_title = True
    chart.chart_title.text_frame.text = title
    run = chart.chart_title.text_frame.paragraphs[0].runs[0]
    run.font.size, run.font.bold, run.font.name = Pt(11), True, FONT
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.TOP
    chart.legend.include_in_layout = False
    chart.value_axis.minimum_scale = 0
    chart.value_axis.maximum_scale = 12
    chart.value_axis.major_unit = 3
    chart.value_axis.has_major_gridlines = True
    chart.value_axis.major_gridlines.format.line.color.rgb = GREY_FILL
    chart.value_axis.format.line.fill.background()
    chart.value_axis.tick_labels.number_format = "0"
    chart.value_axis.tick_labels.number_format_is_linked = False
    chart.category_axis.format.line.color.rgb = RULE_HEAD
    for plotted, (_, _, colour, dashed) in zip(chart.plots[0].series, series):
        plotted.smooth = False
        plotted.format.line.color.rgb = colour
        plotted.format.line.width = Pt(2)
        if dashed:
            plotted.format.line.dash_style = 4          # MSO_LINE.DASH
        plotted.marker.style = XL_MARKER_STYLE.CIRCLE
        plotted.marker.size = 6
        plotted.marker.format.fill.solid()
        plotted.marker.format.fill.fore_color.rgb = colour
        plotted.marker.format.line.color.rgb = WHITE
    return chart


# --- data --------------------------------------------------------------------
with BALANCE.open(encoding="utf-8", newline="") as fh:
    ROWS = {(r["product"], int(r["period"])): r for r in csv.DictReader(fh)}


def bn(product, year, column):
    value = ROWS[(product, year)][column]
    return None if value == "" else float(value) / 1e9


def show(product, year, column, places=2):
    value = bn(product, year, column)
    return "—" if value is None else f"{value:.{places}f}"


# --- keep the supplied cover and closing pages, drop the rest ----------------
for index in range(len(prs.slides) - 2, 0, -1):
    drop_slide(index)
cover, closing = prs.slides[0], prs.slides[1]


def retitle(slide, replacements):
    for shape in slide.shapes:
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.text = replacements.get(run.text, run.text)


retitle(cover, {"Week 1 analytical pack": "Manish hand-back",
                "South Africa | Petrol and diesel": "7 October | Baseline, fuel input tables and decision log"})
retitle(closing, {"Agree priorities": "Review the branch", "and next steps": "and decide",
                  "Confirm demand, routes and access": "manish-branch | checks pass | nothing merged to main"})

# --- 1 National balance ------------------------------------------------------
both_2024 = bn("petrol", 2024, "sales_less_net_imports") + bn("diesel", 2024, "sales_less_net_imports")
s = page(0, f"On customs trade, 2024 petrol and diesel sales exceed net imports by {both_2024:.1f} bn litres",
         "Corrected balance | calendar years, billion litres | imports and exports from SARS customs")
header = ["Year", "Sales", "Imports", "Exports", "Sales less\nnet imports", "Sales", "Imports", "Exports",
          "Sales less\nnet imports"]
columns = ["sales_used", "imports_used", "exports_used", "sales_less_net_imports"]
body = [[str(year)] + [show(product, year, column) for product in ("petrol", "diesel") for column in columns]
        for year in range(2019, 2026)]
text(s, "Petrol", LEFT + 1.0, 2.2, 4.4, 0.25, 11.5, True, BLUE)
text(s, "Diesel", LEFT + 5.4, 2.2, 4.4, 0.25, 11.5, True, BLUE)
table(s, [header] + body, [1.0] + [1.1] * 8, y=2.48, height=3.3, size=11, numeric_from=1)
text(s, "Sales less net imports is what production, stock changes and gaps in sales coverage must together supply. "
        "It is not a measurement of production.\n"
        "Sales: department to 2023; 2024 is FIASA's figure and is unverified; none yet for 2025. "
        "Rebuilt by one command from registered inputs; a test checks every year against the customs extract.",
     LEFT, 6.05, WIDTH, 0.9, 11)

s = page(0, "Sources agree on most years; five differences need a recorded choice",
         "Source differences | billion litres | every source is kept in its own column of the balance file")
table(s, [
    ["Item", "What the sources say", "Used in the balance", "Who decides"],
    ["2024 sales",
     f"FIASA 2025 edition, p.47: petrol {show('petrol', 2024, 'sales_fiasa')}, "
     f"diesel {show('diesel', 2024, 'sales_fiasa')}. FIASA 2024 edition, p.32: 8.76 and 11.81. "
     "JODI: 10.14 and 10.04 (lowest reliability code). Department: not published.",
     "FIASA 2025 edition, flagged unverified", "Nigel: agree the 2024 sales source"],
    ["2024 diesel imports",
     f"Customs {show('diesel', 2024, 'imports_sars', 3)}. Department trade report 10.8 (rounded). "
     f"FIASA {show('diesel', 2024, 'imports_fiasa', 3)}, a suspected misprint.",
     "Customs", "Nigel: review"],
    ["2018 and 2019 trade",
     f"2018 diesel: customs {show('diesel', 2018, 'imports_sars')}, FIASA {show('diesel', 2018, 'imports_fiasa')}; "
     f"petrol: {show('petrol', 2018, 'imports_sars')} and {show('petrol', 2018, 'imports_fiasa')}. "
     f"2019 diesel: {show('diesel', 2019, 'imports_sars')} and {show('diesel', 2019, 'imports_fiasa')}. "
     "2018 exports are also lower in customs. Cause not found.",
     "Customs", "Nigel: review; Manish to trace"],
    ["2022 diesel exports",
     f"Customs {show('diesel', 2022, 'exports_sars')}, FIASA {show('diesel', 2022, 'exports_fiasa')}.",
     "Customs", "Nigel: review"],
    ["2019 and 2020 energy balances",
     "Their import and export lines repeat the previous year's figures.",
     "Not used for trade", "Nigel: confirm"],
], [2.3, 5.2, 2.2, 1.95], height=3.6, size=10.5)
text(s, "In the other years from 2014, customs and FIASA differ by 0.2 bn litres or less; the full list is in "
        "the balance note. Before 2014 customs is in kilograms or mixed units, so FIASA is used.",
     LEFT, 6.2, WIDTH, 0.6, 11)

s = page(0, "Production after 2021 and stock changes are missing, so the balance is not closed",
         "Missing production and stocks | sales less net imports against production reported in the energy balance")
years = list(range(2014, 2025))
for i, product in enumerate(("petrol", "diesel")):
    line_chart(s, f"{product.capitalize()}, billion litres", years, [
        ("Sales less net imports", [bn(product, y, "sales_less_net_imports") for y in years], BLUE, False),
        ("Reported production (to 2021)",
         [bn(product, y, "production_energy_balance") for y in years], GREY_LINE, True),
    ], LEFT + i * 3.55, 2.2, 3.5, 3.75)
table(s, [
    ["Missing", "What exists", "Limit"],
    ["Production by product, 2022 on",
     "Sasol, year to June 2024: Secunda 29.1 and Natref 17.8 million barrels. "
     "Glencore, calendar 2024: Astron 166,204 billion Btu.",
     "All refined products; fiscal against calendar years; Natref is Sasol's share only"],
    ["Stock changes", "JODI monthly stocks, 2023 and 2024", "Lowest reliability code; not usable as it stands"],
    ["Sales coverage", "SARS fuel levy volumes, round figures in media releases", "Period is assumed; indicative only"],
], [1.3, 1.8, 1.3], x=LEFT + 7.2, y=2.22, height=3.7, size=9.5)
text(s, "A diesel gap of 3 to 4 bn litres a year remains a hypothesis to test. It is not added to demand. "
        "Needed to close: output by product and plant, a stock series, and matched periods.",
     LEFT, 6.2, WIDTH, 0.6, 11, True, BLUE)

# --- order, navigation, bounds ----------------------------------------------
ids = prs.slides._sldIdLst
closing_id = ids[1]
ids.remove(closing_id)
ids.append(closing_id)

first_of_section = {}
for slide, section in pages:
    first_of_section.setdefault(section, slide)
step = WIDTH / len(SECTIONS)
for slide, section in pages:
    for i, label in enumerate(SECTIONS):
        chevron = slide.shapes.add_shape(MSO_SHAPE.CHEVRON, Inches(LEFT + i * step), Inches(0.08),
                                         Inches(step - 0.06), Inches(0.42))
        chevron.adjustments[0] = 0.12
        chevron.fill.solid()
        chevron.fill.fore_color.rgb = BLUE if i == section else GREY_FILL
        chevron.line.fill.background()
        frame = chevron.text_frame
        frame.margin_top = frame.margin_bottom = 0
        frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = frame.paragraphs[0]
        p.text = label
        p.alignment = PP_ALIGN.CENTER
        p.font.name, p.font.size, p.font.bold = FONT, Pt(11), i == section
        p.font.color.rgb = WHITE if i == section else BLUE
        if i in first_of_section:
            chevron.click_action.target_slide = first_of_section[i]

for slide in prs.slides:
    for shape in slide.shapes:
        assert shape.left >= 0 and shape.top >= 0, shape.name
        assert shape.left + shape.width <= prs.slide_width + 5, shape.name
        assert shape.top + shape.height <= prs.slide_height + 5, shape.name

prs.save(OUT)
print(OUT, len(prs.slides), "slides")
