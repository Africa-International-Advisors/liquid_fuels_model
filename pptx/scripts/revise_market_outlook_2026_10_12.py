"""Revise the South Africa Market Outlook pack after the 12 October 2026 review with Nigel.

Input   pptx/output/delivered/supporting/12102026_South_Africa_Market_Outlook_v1200.pptx  (Nigel's pack with his review notes)
Output  a new pack; the input is never changed. Slides 1-3, 5-7, 10 and 16 are left exactly as they were.

Slide 4   2025 list on the right becomes a stacked chart of estimated demand by use, 2023-2025
Slide 8   electrified vehicle sales as a 2019-2025 series (naamsa), figures in a table under the chart
Slide 9   the pasted screenshot redrawn in the pack's format; ITS SOURCE IS NOT IDENTIFIED and the slide says so
Slide 11  corridor map with the NMPP trunk line (see add_nmpp_to_corridor_map.py)
Slide 12  capture figure made consistent with slides 13 and 15
Slide 13  sizing table becomes a funnel drawn to scale
Slide 14  baseline demand line added to the import chart
Slide 15  capture is 20% of KwaZulu-Natal plus Gauteng sales
All yellow review notes are removed; one new note on slide 9 asks Nigel for the source.

Chart values are read from the registered files and delivered analytics outputs, with checks that stop the build
if a figure no longer matches. The only typed-in series is slide 9's, measured from the screenshot.
The capture basis here (20% of KwaZulu-Natal and Gauteng sales) differs from assumptions/2026/market_review.yaml
(20% of Durban imports, 50% routed to Lesedi); the model file is NOT changed by this script.

Usage:  python pptx/scripts/revise_market_outlook_2026_10_12.py SRC.pptx OUT.pptx REPO_ROOT MAP.png
Needs python-pptx, lxml and openpyxl.
"""
import copy, csv, sys
from pathlib import Path
from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_TICK_MARK, XL_MARKER_STYLE, XL_LABEL_POSITION
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

SRC, OUT, REPO, MAP = sys.argv[1], sys.argv[2], Path(sys.argv[3]), sys.argv[4]
NAVY, BLUE, GREY = "0A2373", "6782B4", "929292"          # series colours already used in the pack's charts
AXIS, TICK = "D4D4D4", "666666"
rgb = RGBColor.from_string
prs = Presentation(SRC)


# ---------- helpers ----------
def shape(n, name=None, sid=None):
    for s in prs.slides[n - 1].shapes:
        if (name is not None and s.name == name) or (sid is not None and s.shape_id == sid):
            return s
    raise KeyError((n, name, sid))


def remove(n, sid, expect_text=None):
    s = shape(n, sid=sid)
    if expect_text is not None:
        assert expect_text in s.text_frame.text, (n, sid, s.text_frame.text)
    drop(n, s._element)


RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def rel_ids(el):
    return {v for e in el.iter() for k, v in e.attrib.items() if k in (RNS + "id", RNS + "embed", RNS + "link")}


def drop(n, el):
    """Remove an element, then any relationship of the slide that nothing on it still uses."""
    part = prs.slides[n - 1].part
    rids = rel_ids(el)
    el.getparent().remove(el)
    still = rel_ids(part._element)
    for rid in rids - still:
        if rid in part.rels:
            part.rels.pop(rid)


def set_single(s, text, expect=None):
    """Replace the text of a one-run shape (line breaks stay inside the run, as the pack has them)."""
    paras = s.text_frame._txBody.findall(qn("a:p"))
    runs = paras[0].findall(qn("a:r"))
    if expect is not None:
        assert expect in s.text_frame.text, (s.name, s.text_frame.text)
    runs[0].find(qn("a:t")).text = text
    for r in runs[1:]:
        paras[0].remove(r)
    for p in paras[1:]:
        p.getparent().remove(p)


def set_paras(txBody, texts):
    """Rebuild paragraphs from the first text paragraph's formatting; '' gives the pack's blank spacer."""
    ps = txBody.findall(qn("a:p"))
    tmpl = next(p for p in ps if p.findall(qn("a:r")))
    blank = next((p for p in ps if not p.findall(qn("a:r"))), None)
    new = []
    for t in texts:
        if t == "" and blank is not None:
            new.append(copy.deepcopy(blank))
            continue
        n = copy.deepcopy(tmpl)
        rs = n.findall(qn("a:r"))
        rs[0].find(qn("a:t")).text = t
        for r in rs[1:]:
            n.remove(r)
        for br in n.findall(qn("a:br")):
            n.remove(br)
        new.append(n)
    for p in ps:
        txBody.remove(p)
    for n in new:
        txBody.append(n)


def clone(n, src_shape, left, top, width, height, text):
    el = copy.deepcopy(src_shape._element)
    src_shape._element.addnext(el)
    ids = [int(i) for i in prs.slides[n - 1].shapes._spTree.xpath(".//p:cNvPr/@id")]
    el.xpath(".//p:cNvPr")[0].set("id", str(max(ids) + 1))
    new = [s for s in prs.slides[n - 1].shapes if s._element is el][0]
    new.left, new.top, new.width, new.height = Inches(left), Inches(top), Inches(width), Inches(height)
    set_single(new, text)
    return new


def base_style(chart, numfmt, legend=XL_LEGEND_POSITION.BOTTOM, legend_pt=None):
    chart.has_title = False
    chart.font.size = Pt(10)
    chart.font.name = "Lato"
    for ax in (chart.category_axis, chart.value_axis):
        ax.has_major_gridlines = False
        ax.has_minor_gridlines = False
        ax.major_tick_mark = XL_TICK_MARK.NONE
        ax.minor_tick_mark = XL_TICK_MARK.NONE
        ax.format.line.color.rgb = rgb(AXIS)
        ax.format.line.width = Emu(9525)
        ax.tick_labels.font.size = Pt(9)
        ax.tick_labels.font.color.rgb = rgb(TICK)
    chart.value_axis.tick_labels.number_format = numfmt
    chart.value_axis.tick_labels.number_format_is_linked = False
    if legend is None:
        chart.has_legend = False
    else:
        chart.has_legend = True
        chart.legend.position = legend
        chart.legend.include_in_layout = False
        if legend_pt:
            chart.legend.font.size = Pt(legend_pt)
    cs = chart._chartSpace
    for rc in cs.xpath("c:roundedCorners"):
        rc.set("val", "0")


def line_series(chart, colours, width=23813):
    for ser, col in zip(chart.plots[0].series, colours):
        ser.format.line.color.rgb = rgb(col)
        ser.format.line.width = Emu(width)
        ser.smooth = False
        ser.marker.style = XL_MARKER_STYLE.NONE


def add_chart(n, kind, data, left, top, width, height):
    gf = prs.slides[n - 1].shapes.add_chart(kind, Inches(left), Inches(top), Inches(width), Inches(height), data)
    gf.name = "Chart"
    return gf.chart


def read_csv(rel):
    with open(REPO / rel, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


A = "output/delivered/sa_analytics_2026_10_11_v02/"

# ---------- slide 4: 2025 list on the right becomes a stacked chart of estimated demand by use ----------
seg = {r["Segment"]: r for r in read_csv(A + "segments.csv")}
order = [("Petrol road use", "Petrol road", NAVY), ("Other petrol", "Other petrol", "3F5596"),
         ("Road freight diesel", "Freight diesel", BLUE), ("Other road diesel", "Other road diesel", "9DB0D3"),
         ("Mining", "Mining", "404040"), ("Agriculture", "Agriculture", "767676"),
         ("Manufacturing", "Manufacturing", GREY), ("Utility and private power", "Power", "BDBEC1"),
         ("Other diesel / unallocated", "Other diesel", "D9D9D9")]
years = ["2023", "2024", "2025"]
tot = [float(seg["Total"][f"{y} bn L"]) for y in years]
assert all(abs(sum(float(seg[k][f"{y} bn L"]) for k, _, _ in order) - t) < 1e-9 for y, t in zip(years, tot))
cd = CategoryChartData(number_format="0.00")
cd.categories = ["2023E", "2024E", "2025E"]
for key, label, _ in order:
    cd.add_series(f"{label} {float(seg[key]['2025 bn L']):.2f}", [float(seg[key][f"{y} bn L"]) for y in years])
ins = shape(4, "Evidence insights")
assert "Petrol road 8.59 | Freight 4.82" in ins.text_frame.text
ch = add_chart(4, XL_CHART_TYPE.COLUMN_STACKED, cd, 8.02, 2.50, 4.23, 3.46)
base_style(ch, "0", legend=XL_LEGEND_POSITION.RIGHT, legend_pt=9)
ch.plots[0].gap_width = 55
ch.plots[0].overlap = 100
for ser, (_, _, col) in zip(ch.plots[0].series, order):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = rgb(col)
    ser.invert_if_negative = False
ch.value_axis.maximum_scale = 25
ch.value_axis.minimum_scale = 0
ch.value_axis.major_unit = 5
unit4 = shape(4, "Evidence unit")
clone(4, unit4, 8.12, 2.21, 4.03, 0.26, "Billion litres | legend shows 2025 values")
set_paras(ins.text_frame._txBody, [f"Totals: {tot[0]:.2f}, {tot[1]:.2f} and {tot[2]:.2f}bn litres. Allocations are estimates; "
                                    "manufacturing is an industry residual."])
ins.top, ins.height = Inches(6.00), Inches(0.85)
set_single(shape(4, "Vopak exhibit right heading"), "Estimated demand by use, 2023–2025", "2025 estimated demand")
remove(4, 4, "Convert into stacked")

# ---------- slide 8: electrified sales as a time series ----------
nev = read_csv("assumptions/2026/timeseries/nev_sales_naamsa.csv")
yrs = sorted({r["period"] for r in nev})
val = {(r["period"], r["drivetrain"]): int(r["value"]) for r in nev}
for y in yrs:
    assert val[y, "battery_electric"] + val[y, "plug_in_hybrid"] + val[y, "traditional_hybrid"] == val[y, "total"], y
assert (val["2025", "battery_electric"], val["2025", "plug_in_hybrid"], val["2025", "traditional_hybrid"]) == (1088, 2810, 12818)
cd = CategoryChartData(number_format="#,##0")
cd.categories = yrs
for key, label in [("battery_electric", "BEV"), ("plug_in_hybrid", "Plug-in hybrid"), ("traditional_hybrid", "Conventional hybrid")]:
    cd.add_series(label, [val[y, key] for y in yrs])
remove(8, 67)
ch = add_chart(8, XL_CHART_TYPE.COLUMN_CLUSTERED, cd, 0.50, 2.50, 7.05, 3.65)
base_style(ch, "#,##0", legend=None)
ch.plots[0].gap_width = 70
ch.plots[0].overlap = -10
for ser, col in zip(ch.plots[0].series, [GREY, BLUE, NAVY]):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = rgb(col)
    ser.invert_if_negative = False
C = "http://schemas.openxmlformats.org/drawingml/2006/chart"
Ans = "http://schemas.openxmlformats.org/drawingml/2006/main"
dtable = etree.fromstring(
    f'<c:dTable xmlns:c="{C}" xmlns:a="{Ans}"><c:showHorzBorder val="1"/><c:showVertBorder val="0"/><c:showOutline val="0"/>'
    f'<c:showKeys val="1"/><c:spPr><a:noFill/><a:ln w="9525"><a:solidFill><a:srgbClr val="{AXIS}"/></a:solidFill></a:ln></c:spPr>'
    f'<c:txPr><a:bodyPr/><a:lstStyle/><a:p><a:pPr><a:defRPr sz="900"><a:solidFill><a:srgbClr val="{TICK}"/></a:solidFill></a:defRPr></a:pPr>'
    f'<a:endParaRPr lang="en-US"/></a:p></c:txPr></c:dTable>')
ch._chartSpace.xpath("c:chart/c:plotArea/c:valAx")[0].addnext(dtable)
tot25, tot19 = val["2025", "total"], val["2019", "total"]
set_single(shape(8, "Vopak exhibit left heading"), f"Electrified vehicle sales, {yrs[0]}–{yrs[-1]}", "Electrified vehicle sales, 2025")
set_paras(shape(8, "Evidence insights").text_frame._txBody, [
    f"Electrified sales rose from {tot19:,} in {yrs[0]} to {tot25:,} in 2025; conventional hybrids are "
    f"{val['2025', 'traditional_hybrid'] / tot25:.0%} of them.",
    "",
    f"BEV: 1,088 sales in 2025, or 0.18% of all new vehicles, down from {val['2024', 'battery_electric']:,} in 2024.",
    "",
    "PHEVs and conventional hybrids still consume fuel; savings depend on usage.",
    "",
    "New sales are not fleet penetration. Efficiency and mileage must be modelled separately."])
set_single(shape(8, "Unified source footer"),
           "naamsa new energy vehicle sales, 2019–2025 (Quarterly Review of Business Conditions: Q3 2024 for 2019; Q2 2026 for 2020–2025); "
           "master workbook Vehicle history. Analytical workbook v02: efficiency is a planning assumption; avoid double-counting hybrid savings.",
           "naamsa all-market sales 2025")
remove(8, 5, "time series")

# ---------- slide 9: the review screenshot redrawn in the pack's format (user instruction, 12 October 2026) ----------
# SOURCE NOT IDENTIFIED. Miles per US gallon measured from the screenshot's plotted lines at each five-year mark and
# calibrated on its six labelled points (13.5, 20.0, 26.8 petrol; 17.5, 25.5, 31.0 diesel). The US EPA Automotive Trends
# Report (EPA-420-R-26-001) is the nearest real series but has no petrol/diesel split and different values.
mpg = {"Petrol": [13.5, 15.6, 17.5, 18.4, 19.3, 20.0, 21.3, 22.5, 24.3, 25.7, 26.8],
       "Diesel": [17.5, 19.9, 22.2, 23.4, 24.5, 25.5, 27.0, 28.5, 30.0, 30.6, 31.0]}
l100 = {k: [round(235.215 / v, 1) for v in vals] for k, vals in mpg.items()}       # litres per 100 km
print("slide 9 L/100 km", l100)
cd = CategoryChartData(number_format="0.0")
cd.categories = [str(y) for y in range(1975, 2026, 5)]
for name in ("Petrol", "Diesel"):
    cd.add_series(name, l100[name])
remove(9, 9)                                   # the pasted screenshot
remove(9, 4)                                   # the chart hidden beneath it
remove(9, 6, "l/100km")
remove(9, 7, "Replace with timeseries")
ch = add_chart(9, XL_CHART_TYPE.LINE_MARKERS, cd, 0.50, 2.55, 7.05, 3.23)
base_style(ch, "0")
for ser, col, pos in zip(ch.plots[0].series, [NAVY, BLUE], [XL_LABEL_POSITION.ABOVE, XL_LABEL_POSITION.BELOW]):
    ser.format.line.color.rgb = rgb(col)
    ser.format.line.width = Emu(23813)
    ser.smooth = False
    ser.marker.style = XL_MARKER_STYLE.CIRCLE
    ser.marker.size = 5
    ser.marker.format.fill.solid()
    ser.marker.format.fill.fore_color.rgb = rgb(col)
    ser.marker.format.line.color.rgb = rgb(col)
    for idx in (0, 5, 10):                      # the three years the screenshot labels: 1975, 2000, 2025
        lab = ser.points[idx].data_label
        lab.position = pos
        lab.font.size = Pt(9)
        lab.font.color.rgb = rgb("333333")
ch.value_axis.minimum_scale, ch.value_axis.maximum_scale, ch.value_axis.major_unit = 0, 20, 5
set_single(shape(9, "Vopak exhibit left heading"), "Fuel use of petrol and diesel vehicles, 1975–2025", "Activity and efficiency effects by 2030")
set_single(shape(9, "Evidence unit"), "Litres per 100 km | converted from miles per gallon; source to be confirmed", "Billion litres versus 2025")
ins9 = shape(9, "Evidence insights")
old9 = ins9.text_frame.text
first = "Engine and vehicle improvements, fleet renewal and operating practices can lower fuel use per kilometre."
assert old9.startswith(first)
set_single(ins9, f"Fuel use per 100 km has roughly halved since 1975: petrol from {l100['Petrol'][0]:.1f} to {l100['Petrol'][-1]:.1f} litres, "
                 f"diesel from {l100['Diesel'][0]:.1f} to {l100['Diesel'][-1]:.1f}." + old9[len(first):])
set_single(shape(9, "Unified source footer"),
           "Chart: figures taken from the review screenshot of 12 October 2026 (miles per US gallon by model year, converted at 235.2 ÷ MPG). SOURCE NOT IDENTIFIED: "
           "they resemble, but do not match, the US EPA Automotive Trends Report, which has no petrol/diesel split; not South African data. "
           "Analytical workbook v02, Driver bridge (Base): modelled effects, not observed savings.",
           "Analytical workbook v02: Driver bridge (Base)")

# ---------- slide 11: map picture with the NMPP trunk line ----------
pic = shape(11, "Picture 6")
part = prs.slides[10].part
blip = pic._element.xpath(".//a:blip")[0]
old_rid = blip.get(qn("r:embed"))
_, new_rid = part.get_or_add_image_part(MAP)
blip.set(qn("r:embed"), new_rid)
if new_rid != old_rid:
    part.drop_rel(old_rid)
scope = shape(11, "Map scope")
tail = "NMPP is the established inland connection discussed at right."
assert tail in scope.text_frame.text
set_single(scope, scope.text_frame.text.replace(
    tail, "The NMPP trunk line (Durban to Jameson Park, about 560 km) is the established inland connection."))
remove(11, 4, "NMPP pipeline")

# ---------- slides 13 and 15: Durban pool, capture and the Durban / inland split ----------
import json
mr = json.loads((REPO / "output/delivered/market_review_2026_10_10/market_review.json").read_text())
durban = mr["durban_customs"]["total"]                       # SARS customs, Durban office, 2025
kzn = mr["catchments"]["KZN"]["total"]                       # Department sales, KwaZulu-Natal, 2022
capture_frac = 0.20                                          # illustrative; Vopak's actual share is not published
gauteng = mr["catchments"]["Gauteng"]["total"]               # Department sales, Gauteng, 2022
addressable = kzn + gauteng                                  # the two markets the sites serve: Durban and inland
assert addressable < durban                                  # stays inside what lands at Durban, so the funnel narrows
cap_dbn = round(capture_frac * kzn, 2)
cap_inland = round(capture_frac * gauteng, 2)
capture = capture_frac * addressable
assert f"{capture:.2f}" == f"{cap_dbn + cap_inland:.2f}"      # the two parts add to the headline as shown
assert cap_inland <= mr["sites"]["Lesedi"]["handling_bn_l"]["base"] and capture <= mr["sites"]["Durban"]["handling_bn_l"]["base"]
print(f"durban {durban:.3f}  kzn {kzn:.3f}  gauteng {gauteng:.3f}  addressable {addressable:.3f}  capture {capture:.3f}  = {cap_dbn} + {cap_inland}")

# ---------- slide 13: the sizing table becomes a funnel drawn to scale ----------
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
INK = "11151A"
s13 = prs.slides[12]
bal = {r["Measure"]: float(r["Total bn L"]) for r in read_csv(A + "balance.csv")}
demand25, imports25 = bal["2025 demand"], bal["Gross customs imports"]
assert abs(imports25 - mr["gross_imports"]["total"]) < 1e-9
inland = durban - kzn
assert shape(13, "Table 54").table.cell(4, 2).text_frame.text.startswith("Addressable volume")
remove(13, 55)                                               # the table
for gid in (10, 14, 21):                                     # handwritten review marks
    remove(13, gid)
MC = "{http://schemas.openxmlformats.org/markup-compatibility/2006}AlternateContent"
tree13 = s13.shapes._spTree
loose = [el for el in tree13 if el.tag == MC and any(d.tag == qn("p:contentPart") for d in el.iter())]
print("loose ink marks removed from slide 13:", len(loose))
for el in loose:
    drop(13, el)


def tbox(x, y, w, h, text, size=13.5, bold=False, colour=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE, name=None):
    b = s13.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        b.name = name
    tf = b.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    p_ = tf.paragraphs[0]
    p_.alignment = align
    r_ = p_.add_run()
    r_.text = text
    f = r_.font
    f.size, f.bold, f.name = Pt(size), bold, "Lato"
    f.color.rgb = rgb(colour)
    return b


def rule(x1, y, x2, colour, width):
    c = s13.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y), Inches(x2), Inches(y))
    c.line.color.rgb = rgb(colour)
    c.line.width = Emu(width)
    c.name = "Funnel rule"


def bar(x, y, w, h, colour, text, size=15):
    r_ = s13.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    r_.name = "Funnel bar"
    r_.fill.solid()
    r_.fill.fore_color.rgb = rgb(colour)
    r_.line.fill.background()
    r_.shadow.inherit = False
    tf = r_.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.word_wrap = False
    p_ = tf.paragraphs[0]
    p_.alignment = PP_ALIGN.CENTER
    run = p_.add_run()
    run.text = text
    run.font.size, run.font.bold, run.font.name = Pt(size), True, "Lato"
    run.font.color.rgb = rgb("FFFFFF")
    return r_


X0, X1, CX, WMAX = 0.50, 12.15, 5.80, 4.60                    # funnel centred at CX; widest bar = national demand
TOP, PITCH, BH = 2.30, 0.78, 0.54
scale = WMAX / demand25
tbox(X0 + 0.08, 1.84, 2.6, 0.36, "Sizing step", bold=True)
tbox(CX - WMAX / 2, 1.84, WMAX, 0.36, "Billion litres a year, 2025", bold=True, align=PP_ALIGN.CENTER)
tbox(8.55, 1.84, 3.6, 0.36, "Basis", bold=True)
rule(X0, 2.24, X1, "7F7F7F", 12700)
reach = mr["sites"]["Durban"]["handling_bn_l"]             # working tanks x turns a month x 12; registered site assumptions
assert abs(reach["base"] - mr["sites"]["Durban"]["working_m3"] * 2 * 12 / 1e6) < 1e-9
steps = [
    ("1  National demand", demand25, BLUE, "Petrol and diesel, estimated from the Department’s 2023 sales."),
    ("2  Import requirement", imports25, BLUE, f"{imports25 / demand25:.0%} of demand is imported; domestic production is 5.8bn L."),
    ("3  Ports and inland routes", durban, NAVY, f"Landed at Durban: {durban / imports25:.0%} of imports. Other ports and Matola take the rest."),
    ("4  Addressable market", addressable, NAVY, f"The two markets the sites serve: KwaZulu-Natal ({kzn:.1f}) and Gauteng ({gauteng:.1f}). "
     "Department sales, 2022."),
    ("5  Achievable capture", capture, NAVY, f"Illustrative {capture_frac:.0%} of step 4: {cap_dbn:.2f} at Durban, {cap_inland:.2f} through Lesedi. "
     "Vopak’s actual share is not published."),
]
prev = None
for i, (label, value, colour, basis) in enumerate(steps):
    y = TOP + PITCH * i
    w = value * scale
    x = CX - w / 2
    if prev is not None:                                       # light link between one bar and the next gives the funnel outline
        px_, pw_, py_ = prev
        fb = s13.shapes.build_freeform(Inches(px_), Inches(py_ + BH))
        fb.add_line_segments([(Inches(px_ + pw_), Inches(py_ + BH)), (Inches(x + w), Inches(y)), (Inches(x), Inches(y))], close=True)
        link = fb.convert_to_shape()
        link.name = "Funnel link"
        link.fill.solid()
        link.fill.fore_color.rgb = rgb("E3E7F1")
        link.line.fill.background()
        link.shadow.inherit = False
    if i == 3:                                                 # two segments: the Durban market and the inland market
        wk = kzn * scale
        bar(x, y, wk - 0.015, BH, NAVY, f"{kzn:.1f}")
        bar(x + wk + 0.015, y, w - wk - 0.015, BH, "3F5596", f"{gauteng:.1f}")
        tbox(x + w + 0.12, y, 1.0, BH, f"= {addressable:.1f}", size=13.5, bold=True, colour=NAVY, name="Funnel total")
    else:
        bar(x, y, w, BH, colour, f"{value:.1f}")
    tbox(X0 + 0.08, y, 2.9, BH, label, bold=True, name="Funnel step")
    tbox(8.55, y - 0.08, 3.15, BH + 0.16, basis, size=11.5, name="Funnel basis")
    rule(X0, y + BH + (PITCH - BH) / 2, X1, "D0D0D0", 6350)
    prev = (x, w, y)
take = shape(13, "M takeaway")
set_single(take, f"Step 6: Vopak’s Durban tanks handle about {reach['base']:.1f}bn litres a year at two turns a month; volumes above that need new tanks.",
           "Steps 4–5 size Vopak’s opportunity")
set_single(shape(13, "Unified source footer"),
           "Analytical workbook v02 (demand, imports); SARS customs, Durban office, 2025; Department provincial sales 2022; market-sizing workbook. "
           "Bars are drawn to scale. Step 4: 2022 sales beside 2025 imports; Gauteng is also supplied by Secunda, Natref and Matola. "
           "Step 6: 146,000 m³ working fuel tanks (estimate) at Vopak’s stated target of 2–3 turns a month. "
           "Capture is an illustrative 20%, not a contracted share. "
           "Walvis Bay is a route to assess; no diversion volume is assigned.",
           "Framework: analytical workbook v02")
note13 = shape(13, sid=5)                                      # Nigel's open question stays on top
tree13.append(note13._element)

cap = shape(15, "R capture explanation")
assert "Includes 1.32bn litres onward through Lesedi" in cap.text_frame.text
set_paras(cap.text_frame._txBody, [
    f"Assumes 20% of the {addressable:.1f}bn litres sold in KwaZulu-Natal and Gauteng, the markets the two sites serve: "
    f"{cap_dbn:.2f}bn litres at Durban and {cap_inland:.2f}bn litres through Lesedi.",
    "",
    "Illustrative share; no explicit deduction for Matola or Walvis Bay diversion."])
num15 = shape(15, "R capture number")
assert num15.text_frame.text.strip() == "2.63bn L" and len(num15.text_frame.paragraphs[0].runs) == 1
num15.text_frame.paragraphs[0].runs[0]._r.find(qn("a:t")).text = f"{capture:.2f}bn L"
set_single(shape(15, "R capture label"), "Illustrative capture, Durban and Lesedi", "Illustrative Durban capture")
f15 = shape(15, "Unified source footer")
set_single(f15, f15.text_frame.text.rstrip() + f" Capture base: Department sales 2022, KwaZulu-Natal {kzn:.2f}bn L and Gauteng {gauteng:.2f}bn L.")
remove(15, 5, "What is landing in Durban")

# ---------- slide 12: Lesedi's part of the capture made consistent with slide 15 ----------
share12 = shape(12, "Share")
p12 = share12.text_frame.paragraphs[1]
assert p12.text == "Durban 2.63B L, Lesedi 1.32B L" and len(p12.runs) == 1
p12.runs[0]._r.find(qn("a:t")).text = f"Total {capture:.2f}B L: Durban {cap_dbn:.2f}, Lesedi {cap_inland:.2f}"
p12b = share12.text_frame.paragraphs[2]
assert p12b.text == "Lesedi included in Durban flow"
p12b.runs[0]._r.find(qn("a:t")).text = "20% of KZN and Gauteng sales"

# ---------- slide 14: Nigel's import chart with one line added, baseline demand ----------
import io
import openpyxl
from pptx.enum.dml import MSO_LINE
sc = {r["Case / year"]: r for r in read_csv(A + "scenarios.csv")}
yy = [str(y) for y in range(2025, 2031)]
base_dem = [float(sc[f"Base {y}"]["Demand bn L"]) for y in yy]
ch14 = shape(14, sid=4).chart
plot = ch14.plots[0]
assert list(plot.categories) == yy and len(plot.series) == 3
for ser_, case in zip(plot.series, ["Low imports", "Base", "High imports"]):          # the chart already holds the analytics values
    assert all(abs(v - float(sc[f"{case} {y}"]["Gross import need bn L"])) < 5e-3 for v, y in zip(ser_.values, yy)), case
sers = ch14._chartSpace.xpath("c:chart/c:plotArea/c:lineChart/c:ser")
new = copy.deepcopy(sers[-1])
new.xpath("c:idx")[0].set("val", "3")
new.xpath("c:order")[0].set("val", "3")
new.xpath("c:tx/c:v")[0].text = "Base demand"
for u in new.iter("{http://schemas.microsoft.com/office/drawing/2014/chart}uniqueId"):
    u.set("val", "{00000003-3D57-4CA9-AD2A-3657A817E3C7}")
new.xpath("c:val/c:numRef/c:f")[0].text = "'Chart Data'!$E$2:$E$7"
for pt, v in zip(new.xpath("c:val/c:numRef/c:numCache/c:pt"), base_dem):
    pt.xpath("c:v")[0].text = repr(v)
sers[-1].addnext(new)
added = ch14.plots[0].series[3]
added.format.line.color.rgb = rgb("404040")
added.format.line.width = Emu(23813)
added.format.line.dash_style = MSO_LINE.DASH
wbpart = ch14.part.chart_workbook.xlsx_part
wb = openpyxl.load_workbook(io.BytesIO(wbpart.blob))
ws = wb.worksheets[0]
ws["E1"] = "Base demand"
for i, v in enumerate(base_dem):
    ws.cell(row=2 + i, column=5, value=v)
buf = io.BytesIO()
wb.save(buf)
ch14.part.chart_workbook.update_from_xlsx_blob(buf.getvalue())
set_single(shape(14, "Vopak exhibit left heading"), "Gross import requirement and baseline demand, 2025–2030", "Gross import requirement, 2025–2030")
ins14 = shape(14, "Evidence insights")
assert ins14.text_frame.text.startswith("2030 imports: base 16.61bn L")
set_single(ins14, f"Baseline demand stays near 21bn L ({base_dem[-1]:.2f}bn L in 2030).\n\n" + ins14.text_frame.text)
remove(14, 9, "Add demand")

# ---------- review notes: all yellow blocks removed; one new note on slide 9 (user instruction, 12 October 2026) ----------
def is_yellow(sh):
    try:
        return sh.shape_type == 1 and sh.fill.type == 1 and str(sh.fill.fore_color.rgb) == "FFFF00"
    except (AttributeError, TypeError):
        return False


src_note = copy.deepcopy([sh for sh in Presentation(SRC).slides[8].shapes if sh.shape_id == 6][0]._element)
gone = []
for n_, sl in enumerate(prs.slides, 1):
    for sh in [x for x in sl.shapes if is_yellow(x)]:
        gone.append((n_, sh.text_frame.text.strip()))
        sh._element.getparent().remove(sh._element)
print("yellow blocks removed:", gone)
tree9 = prs.slides[8].shapes._spTree
tree9.append(src_note)
src_note.xpath(".//p:cNvPr")[0].set("id", str(max(int(i) for i in tree9.xpath(".//p:cNvPr/@id")) + 1))
note9 = [sh for sh in prs.slides[8].shapes if sh._element is src_note][0]
note9.name = "Review note"
set_single(note9, "Get source from Nigel", "l/100km")
note9.left, note9.top = Inches(10.42), Inches(0.46)

prs.save(OUT)
print("saved", OUT)
