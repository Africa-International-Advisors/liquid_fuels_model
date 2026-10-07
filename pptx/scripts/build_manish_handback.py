"""Build the 6 October hand-back deck from Manish to Nigel.

Starts from the delivered Week 1 pack so the Vopak master, layouts, cover and
closing pages are the supplied ones, then replaces the pages in between. Uses
python-pptx only: the brand-pptx toolkit the other builders import is not
installed on the analyst's machine. Figures are typed from the evidence notes
under workstreams/WS1_data_validation/ and workstreams/WS2_model_development/;
this builder reads no model input and changes none.

    python pptx/scripts/build_manish_handback.py
"""
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import nsdecls, qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output/delivered/archive/2026-10-06_storyline/Vopak_Week1_Analytical_Pack_2026_10_06.pptx"
OUT = ROOT / "output/delivered/supporting/Vopak_Manish_Handback_2026_10_06.pptx"

FONT = "Lato"
BLUE = RGBColor.from_string("0A2373")
INK = RGBColor.from_string("11151A")
WHITE = RGBColor.from_string("FFFFFF")
GREY_FILL = RGBColor.from_string("EEEEEE")
RULE_HEAD = RGBColor.from_string("A0A0A0")
RULE_BODY = RGBColor.from_string("B8B8B8")
LEFT, WIDTH = 0.5, 11.65
NOTE = ("Source: evidence notes on manish-branch, 6 October 2026; diesel gap wording corrected 7 October after "
        "Nigel's review. Changes are the analyst's position, pending review.")

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


def table(slide, rows, widths, y=2.22, height=3.9, size=11):
    shape = slide.shapes.add_table(len(rows), len(widths), Inches(LEFT), Inches(y),
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
    return grid


SECTIONS = ("1  Status", "2  Findings", "3  Levers", "4  Decisions")
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


# --- keep the supplied cover and closing pages, drop the rest ----------------
# The base pack ends with a palette reference page; the closing page is the one before it.
closing_index = next(i for i, slide in enumerate(prs.slides)
                     if any(shape.has_text_frame and "Agree priorities" in shape.text_frame.text for shape in slide.shapes))
for index in range(len(prs.slides) - 1, 0, -1):
    if index != closing_index:
        drop_slide(index)
cover, closing = prs.slides[0], prs.slides[1]


def retitle(slide, replacements):
    for shape in slide.shapes:
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.text = replacements.get(run.text, run.text)


retitle(cover, {"Week 1 analytical pack": "Manish hand-back",
                "South Africa | Petrol and diesel": "6 October | Sourced data, explicit gaps and levers"})
retitle(closing, {"Agree priorities": "Review the branch", "and next steps": "and decide",
                  "Confirm demand, routes and access": "manish-branch | checks pass | nothing merged to main"})

# --- 1 Status ---------------------------------------------------------------
s = page(0, "Five packages are back: three complete, two partial with stated gaps",
         "Handback against the 6 October checklist | petrol and diesel; jet tracked separately")
table(s, [
    ["Work package", "What came back", "Status"],
    ["1 Integrity", "Every P1 flag traced to its source cell. Three extraction errors fixed, one of them ours "
     "(2013 sales read from a superseded sheet). Industry and agriculture baselines now sourced.",
     "Complete; decisions with Nigel"],
    ["2 Traceability", "45 datasets mapped from publisher to original, extract and consuming function. "
     "The engine still reads six files, all from the Reatile workbook.", "Complete"],
    ["3 Provincial demand", "Nothing official exists after 2023-Q1; the department's own schedule promised data "
     "to end-2024. Estimate for 2023-24: petrol within 2-3%, diesel 5-11%.", "Partial: no later data exists"],
    ["4 Fuel balance", "SARS customs data fetched by script, 2010 to August 2026. Sales less net imports "
     "computed by product. A diesel gap of 3-4 bn litres a year is a hypothesis to test.",
     "Partial: no product split or stocks"],
    ["5 Driver evidence", "All seven categories sourced or marked. Prices to October 2026, quarterly GDP, "
     "mining, manufacturing, freight and CPI series added.", "Complete; open rows listed"],
], [1.75, 7.3, 2.6], height=3.95)
text(s, "155 tests pass; lfm check passes with 52 open exceptions; both scenarios run. No change is on main.",
     LEFT, 6.55, WIDTH, 0.3, 11.5, True, BLUE)

# --- 2 Findings -------------------------------------------------------------
s = page(1, "Five input changes are applied on the branch; one moves model results",
         "Approved by Manish, awaiting Nigel | register reconciled, every changed row marked unreviewed")
table(s, [
    ["Change", "Evidence", "Effect on the model"],
    ["2013 national sales: diesel 11.89 to 12.14, petrol 11.15 to 11.44 bn litres",
     "Department's published sheet, both district workbooks and the Reatile history agree", "None: reference data"],
    ["Refinery file: 948 rows to 348", "Production_High range ran to row 13,102 and swept in seven other tables",
     "None: supply identical every year"],
    ["Jet history: 72 rows to 57", "Extraction ran into three regional tables below the national one", "None"],
    ["Industry baseline 2.5 to 1.50 bn litres; agriculture 0.7 to 1.06",
     "Department energy balance, 2021. Placeholders had no source", "Diesel demand falls 0.63 bn litres a year"],
    ["New reference data: SARS trade, operator output, prices, quarterly GDP, Stats SA monthly, power diesel",
     "Each with an evidence record and register rows", "None: not read by the engine"],
], [4.2, 4.85, 2.6], height=3.7)
text(s, "Left unchanged for Nigel: marine baseline, elasticities, road parameters, 2014 and 2018 provincial treatment.",
     LEFT, 6.4, WIDTH, 0.3, 11.5, True, BLUE)

s = page(1, "Customs data settles 2024 diesel imports and shows where fuel enters",
         "SARS trade statistics, chapter 27 fuel lines | litres from 2014; fetched by script")
table(s, [
    ["2024, bn litres", "SARS", "FIASA", "Trade report"],
    ["Diesel imports", "10.793", "14.793", "10.8"],
    ["Petrol imports", "4.001", "4.000", "4.0"],
    ["Diesel exports", "0.796", "0.821", "0.79"],
    ["Petrol exports", "0.920", "0.939", "0.92"],
], [2.3, 1.2, 1.2, 1.3], height=1.9, size=11.5)
table(s, [
    ["Imports cleared at", "2024", "Share"],
    ["Durban", "11.84", "80%"],
    ["Cape Town", "1.09", "7%"],
    ["Mossel Bay", "0.62", "4%"],
    ["East London", "0.53", "4%"],
    ["Richards Bay", "0.39", "3%"],
], [2.3, 1.2, 1.2], y=4.3, height=2.25, size=11.5)
text(s, "01 | FIASA's figure is a misprint", 7.1, 2.3, 5.0, 0.3, 13, True, BLUE)
text(s, "FIASA's 14 793 is exactly 4 000 million litres above customs. In 2014-17, 2020 and 2025 the two agree "
        "to within 12 million litres.", 7.1, 2.65, 5.0, 0.9, 11.5)
text(s, "02 | Durban clears four-fifths of imports", 7.1, 3.65, 5.0, 0.3, 13, True, BLUE)
text(s, "Petrol plus diesel, by customs office. This is a public proxy for entry port, not a terminal record. "
        "98% of diesel imports arrive by sea.", 7.1, 4.0, 5.0, 0.9, 11.5)
text(s, "03 | Botswana is sourcing less through South Africa", 7.1, 5.0, 5.0, 0.3, 13, True, BLUE)
text(s, "Its recorded imports from South Africa fell from 1.02 to 0.63 bn litres between 2023 and 2024; "
        "SARS exports show the same direction.", 7.1, 5.35, 5.0, 0.9, 11.5)

s = page(1, "Four indicative comparisons point to a possible diesel gap; none is matched accounting",
         "Hypothesis to test: 3-4 bn litres a year | not added to demand | production and stocks unresolved")
table(s, [
    ["Route", "What it shows", "Size"],
    ["Product balance", "Sales less net imports is 0.9-1.7 bn litres for diesel in 2022-24, beside 4.6-6.0 bn for "
     "petrol. It is a balancing requirement, not output. The plants made 0.85 litres of diesel per litre of "
     "petrol in 2017-19; that ratio need not hold now.",
     "2.2-3.7 bn on that ratio"],
    ["Operators' output", "Secunda, Natref and Astron report 13-14 bn litres of all refined products; the balance needs "
     "8.7 (2023) and 10.6 (2024). Fiscal against calendar years; conversions assumed.", "4.4 and 3.3 bn"],
    ["Customs, both sides", "SARS confirms the import and export figures. Nine neighbours report importing 1.8-2.0 bn "
     "litres from South Africa against 1.6-1.9 recorded as exported.", "Exports do not explain it"],
    ["Fuel levy volumes", "SARS: levy declared on 24 bn litres in the eleven months to February 2024, against about "
     "20 bn of recorded sales for roughly the same months. The period is assumed.", "About 3.9 bn"],
], [2.0, 7.45, 2.2], height=3.55)
text(s, "One reading is that the department's sales series undercounts. Stock changes, plant product mix and "
        "mismatched periods could give the same differences. It stays a hypothesis until production and stocks "
        "are matched.", LEFT, 6.05, WIDTH, 0.55, 11.5, True, BLUE)

s = page(1, "Fuel prices have risen sharply in 2026 and the model has no price response",
         "Regulated inland prices, rand per litre | department to February 2026, Central Energy Fund sheets after")
table(s, [
    ["Effective", "4 Feb", "4 Mar", "1 Apr", "6 May", "3 Jun", "1 Jul", "5 Aug", "2 Sep", "7 Oct"],
    ["Petrol 95, retail", "20.10", "20.30", "23.36", "26.63", "28.06", "26.10", "25.58", "26.92", "30.25"],
    ["Diesel 0.05%, wholesale", "17.92", "18.54", "25.91", "31.18", "27.93", "24.79", "26.17", "29.11", "31.95"],
], [2.65] + [1.0] * 9, height=1.25, size=11.5)
text(s, "01 | Diesel is up 78% and petrol 50% since February", LEFT, 3.85, 5.6, 0.3, 13, True, BLUE)
text(s, "Our price series stopped in April 2024 this morning. It now runs monthly from January 2011 to October 2026.",
     LEFT, 4.2, 5.6, 0.8, 11.5)
text(s, "02 | One South African study gives the response", LEFT, 5.1, 5.6, 0.3, 13, True, BLUE)
text(s, "Boshoff (2012): a 10% rise in the real price lowers petrol demand by about 5% and diesel by about 1% "
        "in the long run.", LEFT, 5.45, 5.6, 0.8, 11.5)
text(s, "03 | Coastal prices are no longer published", 6.55, 3.85, 5.6, 0.3, 13, True, BLUE)
text(s, "Coastal diesel has no value from December 2025; coastal petrol and paraffin none from March 2026. "
        "The fund prints Gauteng prices only.", 6.55, 4.2, 5.6, 0.8, 11.5)
text(s, "04 | Power diesel: 0.31 litres per kWh", 6.55, 5.1, 5.6, 0.3, 13, True, BLUE)
text(s, "Three years of reported burn against turbine output agree. The workbook's efficiency implies 0.244, "
        "a fifth too low. Adoption is left for Nigel.", 6.55, 5.45, 5.6, 0.8, 11.5)

# --- 3 Levers ---------------------------------------------------------------
s = page(2, "The seven levers each have evidence and a proposed base case; none is calibrated",
         "Draft for discussion | base case = things continue as they perform today")
table(s, [
    ["Lever", "Evidence held", "Proposed base case", "Needed to reach litres"],
    ["Road to rail", "Rail 214 Mt (2019), 156 (2022), 168 (2025); road 895 to 975. Target 250 Mt by 2029/30",
     "Rail holds its present share", "Haul distance; diesel per tonne-km"],
    ["Electric vehicles", "2.8% of 2025 sales against a quoted 20% target; 0.2% battery electric. Peers: Brazil 6%, "
     "Southeast Asia near 20%", "Continues from actual sales", "AIA's view of the path; fleet turnover"],
    ["Grid power", "Turbine output FY2022-26; 0.31 litres per kWh", "Eskom's own plan", "Decision on the factor"],
    ["Industry", "Mining and manufacturing volumes 7% below 2019, flat", "Flat, then with GDP",
     "Litres per unit of output"],
    ["Agriculture", "Value added to 2025; diesel use to 2021", "With sector value added", "Choice of driver"],
    ["Vehicle fleet", "12.6 million vehicles, growing 1.4% a year", "Present growth rate",
     "Fuel split by class; distance after 2014"],
    ["Growth", "Treasury 1.6%, 1.8%, 2.0%; then 2%", "As set on 5 October", "Wiring into the model"],
], [1.7, 4.75, 2.6, 2.6], height=4.3, size=10.5)

s = page(2, "Five further levers are proposed, mostly where the model is silent",
         "Additions to the seven | two do not sit on a high-low demand axis and would be shown as variants")
table(s, [
    ["Proposed lever", "Why it belongs", "Proposed base case"],
    ["Fuel price level", "Diesel up 78% and petrol 50% since February; the model has no price response",
     "Prices settle at a stated level"],
    ["Private backup generation", "The power lever covers grid turbines only. SARS attributes a 3 bn litre fall in "
     "levy volumes to increased energy availability", "No return of load-shedding"],
    ["Neighbours' sourcing through South Africa", "Throughput for Vopak, not South African demand. Botswana's "
     "imports via South Africa fell 38% in a year", "Present volumes continue"],
    ["Refinery events", "Petrol and diesel must meet 10 ppm sulphur from 1 July 2027. Natref does not yet comply; "
     "Astron is investing R6 bn. A miss raises imports", "Three plants run and comply"],
    ["Passengers returning to rail", "503 million journeys in 2010, 19 million in 2022, 103 million in 2025. "
     "Probably small", "Recovery continues"],
], [2.75, 6.1, 2.8], height=3.75)
text(s, "Grid turbines and backup generation move together; so do electric vehicles and fuel prices. "
        "A matrix should not treat them as independent.", LEFT, 6.35, WIDTH, 0.55, 11.5, True, BLUE)

# --- 4 Decisions ------------------------------------------------------------
s = page(3, "Decisions for Nigel before integration and lever calibration",
         "Each has evidence in the notes under workstreams/WS1_data_validation and WS2_model_development")
table(s, [
    ["Decision", "Evidence in brief", "Suggestion"],
    ["Confirm the five applied changes", "Slide 3; flag log", "Accept"],
    ["2024 diesel imports and how to report the diesel gap", "Customs 10.793 bn litres; four routes to 3-4 bn",
     "Use 10.79; report the gap as a hypothesis"],
    ["Power diesel factor", "0.31 litres per kWh in three years against 0.244", "Adopt 0.31"],
    ["Marine baseline", "2.2 bn litres equals the department's 2007 figure; trade press now about 1 bn",
     "Hold until an official figure"],
    ["Elasticities and road parameters", "One study for diesel as a whole; 2018 paper for vehicles",
     "Keep 1.0 for industry; review the vehicle mapping"],
    ["Provincial 2023-24 in the pack; 2014 and 2018 treatment", "Estimate and back-test; original cells",
     "Petrol only, labelled; national stands"],
    ["Sales less net imports after 2021; 2019-20 balances for trade", "Balance note",
     "Not a measure of output; stop using them"],
    ["Remaining originals; register layout", "16 datasets held locally", "Nigel's call"],
], [4.1, 4.55, 3.0], height=4.3, size=10.5)

# --- order, navigation, bounds ----------------------------------------------
ids = prs.slides._sldIdLst
closing_id = ids[1]
ids.remove(closing_id)
ids.append(closing_id)

first_of_section = {}
for slide, section in pages:
    first_of_section.setdefault(section, slide)
for slide, section in pages:
    for i, label in enumerate(SECTIONS):
        chevron = slide.shapes.add_shape(MSO_SHAPE.CHEVRON, Inches(LEFT + i * 2.93), Inches(0.08),
                                         Inches(2.86), Inches(0.42))
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
        p.font.name, p.font.size, p.font.bold = FONT, Pt(13), i == section
        p.font.color.rgb = WHITE if i == section else BLUE
        chevron.click_action.target_slide = first_of_section[i]

for slide in prs.slides:
    for shape in slide.shapes:
        assert shape.left >= 0 and shape.top >= 0, shape.name
        assert shape.left + shape.width <= prs.slide_width + 5, shape.name
        assert shape.top + shape.height <= prs.slide_height + 5, shape.name

prs.save(OUT)
print(OUT, len(prs.slides), "slides")
