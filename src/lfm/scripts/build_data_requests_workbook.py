"""Build the master data book: the sourced data for the South Africa story, by data request (DR01, DR04, DR07, DR08).

This is the one place to look for a sourced figure (decision D25, 9 October 2026). The demand baseline workbook keeps
the model history and the analysis built on it and takes no new sourced data.

    output/delivered/Master_data_book.xlsx

Sheets:
    Contents                  what each sheet holds and how many facts it carries
    DR01 national balance     sales, production, imports and exports by year, billion litres
      DR01 sales by province  petrol and diesel sold in each province by year
      DR01 demand by sector   diesel and petrol used by each sector, to 2021
      DR01 sector activity    activity to 2025 and estimated diesel after 2021, by formula on the sheet above
    DR04 routes and access    pipeline, cost, ports, access and competing routes
      DR04 entry points       petrol and diesel imports by customs office and year
      DR04 transport cost     the Gauteng route by element and every pricing zone
    DR07 demand evidence      power, vehicles, efficiency, freight and rail
      DR07 fleet by province  vehicles by class and by fuel in each province
    DR08 refinery supply      capacity, status, output, yields, utilisation and outlook
    Market sizing             what each Vopak site can reach, from the sizing table
    Not available             everything that could not be found, with the reason

Each request sheet is built from that request's evidence table. A fact reported
for several years is laid out with one column a year; a fact split across
several subjects (stations, provinces) gets one row each; everything else is
one row. Facts that mix in other products are left out, as in the tables.

Run:
    python -m lfm.scripts.build_data_requests_workbook --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from lfm.config import Paths
from lfm.scripts import build_demand_baseline_workbook as base
from lfm.scripts import build_dr08_refinery_evidence as dr08

OUT = Path("output/delivered/Master_data_book.xlsx")
BALANCE = Path("workstreams/WS1_data_validation/fuel_balance_petrol_diesel_2009_2025_2026-10-06.csv")
SIZING = Path("workstreams/WS2_model_development/market_sizing_durban_lesedi_2026-10-09.csv")
INK, FILL = base.INK, base.FILL
STATUS_FILL = {"observed": "observation", "inferred": "formula"}                   # anything else is open: yellow
STATUS_LABEL = {"observed": "From source", "inferred": "Calculated"}
REQUESTS = [
    # sheet, request, evidence table, parts in order, heading, what the second column names
    ("DR04 routes and access", "DR04", base.DR04_EVIDENCE, base.DR04_PARTS, "DR04 Routes and access", "Asset or route"),
    ("DR07 demand evidence", "DR07", base.DR07_EVIDENCE, base.DR07_PARTS, "DR07 Demand evidence", "Covers"),
    ("DR08 refinery supply", "DR08", dr08.OUT, dr08.PARTS, "DR08 Refinery supply", "Plant"),
]
BALANCE_YEARS = list(range(2014, 2026))
DETAIL = {
    "DR04": [(base.dr04_entry_sheet, "DR04 entry points", "Petrol and diesel imports cleared at each customs office, by year"),
             (base.dr04_transport_sheet, "DR04 transport cost",
              "The Durban to Gauteng route by cost element, and the regulated transport differential for all 54 pricing zones")],
    "DR07": [(base.dr07_fleet_sheet, "DR07 fleet by province", "Registered vehicles by class and province, and petrol and diesel vehicles by province")],
    "DR08": [],
}
TEXT_COLUMNS = 6            # single facts spread their value over this many year columns, so long text has room
_NUMBER = re.compile(r"^-?[\d,]+(\.\d+)?$")
_RANGE = re.compile(r"^-?[\d,.]+ to -?[\d,.]+$")
_BARE_PERIOD = re.compile(r"^\d{4}(/\d{2})?$")
_YEAR = re.compile(r"^\d{4}$")
_FISCAL = re.compile(r"^\d{4}/\d{2}$")


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def number(text: str):
    """The text as a number when it is one, so Excel can sum and chart it; otherwise the text."""
    text = text.strip()
    if _NUMBER.match(text):
        return float(text.replace(",", "")) if "." in text else int(text.replace(",", ""))
    return text


def as_series(row: dict) -> tuple[str, list[str], list] | None:
    """``(basis, labels, values)`` when a fact holds one figure for each of several periods."""
    values = [v.strip() for v in row["value"].split(";")]
    periods = [p.strip() for p in row["period"].split(";")]
    if len(values) < 2 or len(values) != len(periods) or not all(_NUMBER.match(v) or _RANGE.match(v) for v in values):
        return None
    basis = ""
    head = periods[0].rsplit(" ", 1)
    if len(head) == 2 and _BARE_PERIOD.match(head[1]) and all(_BARE_PERIOD.match(p) for p in periods[1:]):
        basis, periods = head[0], [head[1]] + periods[1:]          # "years to March 2021; 2022" -> basis and bare years
    return basis, periods, [number(v) for v in values]


def as_breakdown(row: dict) -> list[tuple[str, object]] | None:
    """``[(label, value)]`` when a fact holds one figure for each of several subjects (stations, provinces, classes)."""
    values = [v.strip() for v in row["value"].split(";")]
    if len(values) < 2 or not row["unit"]:
        return None
    subjects = [s.strip() for s in row["asset_or_route"].split(";")]
    if len(subjects) == len(values) and all(_NUMBER.match(v) for v in values):
        return [(s, number(v)) for s, v in zip(subjects, values)]
    named = [re.match(r"^(.+?) (-?[\d,]+(?:\.\d+)?)$", v) for v in values]         # "cars 8,340,592"
    if all(named):
        return [(m.group(1), number(m.group(2))) for m in named]
    leading = [re.match(r"^(-?[\d,]+(?:\.\d+)?) (.+)$", v) for v in values]        # "40,000 diesel"
    if all(leading):
        return [(m.group(2), number(m.group(1))) for m in leading]
    return None


def gauteng_transport_rows(reference: Path) -> list[dict]:
    """The regulated transport cost to Gauteng by year, from the department's yearly price tables."""
    latest: dict[tuple[str, int], tuple[str, float]] = {}
    for r in _read(reference / "transport_cost_gauteng_department.csv"):
        key = (r["product"], int(r["period"][:4]))
        if key not in latest or r["period"] > latest[key][0]:
            latest[key] = (r["period"], float(r["value"]))
    rows = []
    for product in ("diesel", "petrol"):
        years = sorted(y for p, y in latest if p == product)
        rows.append(dict(
            request="DR04", part="Delivered cost", item=f"Regulated transport cost to Gauteng in the {product} price",
            asset_or_route="Coast to Gauteng", value="; ".join(f"{latest[(product, y)][1]:.1f}" for y in years), unit="cents a litre",
            period="year end " + "; ".join(str(y) for y in years), status="observed",
            source="Department of Mineral and Petroleum Resources, yearly price tables (levies, taxes and margins)",
            original_file="assumptions/2026/reference/transport_cost_gauteng_department.csv", page="Transport cost column",
            unresolved_gap="The figure in the last month the department published for each year (April for 2024). It is reset each April. "
                           "A regulated allowance, not a commercial rate. The April 2024 table shows 75.7 while the zone list of the same month shows 82.8."
                           + (" The department's petrol table shows 28.9 throughout 2014, where its diesel table and zone list show 33.1 from April."
                              if product == "petrol" else ""),
            scope="petrol and diesel"))
    return rows


def evidence(path: Path, reference: Path, request: str) -> list[dict]:
    rows = [r for r in _read(path) if r["scope"] != "other products included"]
    if request == "DR04":
        at = max(i for i, r in enumerate(rows) if r["part"] == "Delivered cost" and r["item"].startswith("Regulated transport differential, Gauteng"))
        rows[at:at] = gauteng_transport_rows(reference)
    return rows


class Table:
    """Writes rows down one sheet with a fixed set of columns: four descriptive, ``width`` value columns, four closing."""

    def __init__(self, ws, subject: str, width: int):
        self.ws, self.subject, self.width, self.row = ws, subject, width, 3
        self.first, self.tail = 5, 5 + width
        widths = [36, 30, 20, 16] + [10.5] * width + [13, 46, 16, 62]
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        self.widths = widths

    def _cells(self, values: list, fill: str, bold=False, white=False, wrap=True, height=True, text=False) -> None:
        lines = 1
        for i, value in enumerate(values, start=1):
            cell = self.ws.cell(row=self.row, column=i, value=value)
            cell.font = Font(name="Arial", size=10, bold=bold, color="FFFFFFFF" if white else INK)
            cell.fill = PatternFill("solid", fgColor=FILL[fill])
            numeric = isinstance(value, (int, float))
            cell.alignment = Alignment(wrap_text=wrap, vertical="top", horizontal="right" if numeric and not text else "left")
            if isinstance(value, float):
                cell.number_format = "#,##0.00" if abs(value) < 100 else "#,##0.0"
            elif isinstance(value, int) and self.first <= i < self.tail and not 1900 < value < 2100:
                cell.number_format = "#,##0"
            if isinstance(value, str) and value and not (text and i == self.first):
                lines = max(lines, math.ceil(len(value) / max(self.widths[i - 1] * 1.15, 1)))
        if height:
            self.ws.row_dimensions[self.row].height = 13.5 * lines + 2

    def section(self, title: str) -> None:
        self.row += 2
        self._cells([title] + [None] * (self.tail + 3), "section", bold=True, height=False)

    def header(self, labels: list, value_label: str | None = None) -> None:
        self.row += 1
        middle = [value_label] + [None] * (self.width - 1) if value_label else labels + [None] * (self.width - len(labels))
        self._cells(["Item", self.subject, "Unit", "Period" if value_label else "Basis"] + middle + ["Status", "Source", "Page", "Note"], "header",
                    bold=True, white=True, height=False)
        if value_label:
            self.ws.merge_cells(start_row=self.row, start_column=self.first, end_row=self.row, end_column=self.first + TEXT_COLUMNS - 1)

    def line(self, r: dict, subject: str, unit_period: str, values: list, text: bool = False) -> None:
        self.row += 1
        kind = STATUS_FILL.get(r["status"], "estimate")
        middle = values + [None] * (self.width - len(values))
        self._cells([r["item"], subject, r["unit"], unit_period] + middle
                    + [STATUS_LABEL.get(r["status"], "Not available"), r["source"] or "None found", r["page"], r["unresolved_gap"]], kind, text=text)
        if text:
            self.ws.merge_cells(start_row=self.row, start_column=self.first, end_row=self.row, end_column=self.first + TEXT_COLUMNS - 1)
            value = values[0]
            if isinstance(value, str):
                room = sum(self.widths[self.first - 1:self.first - 1 + TEXT_COLUMNS]) * 1.15
                needed = 13.5 * math.ceil(len(value) / room) + 2
                self.ws.row_dimensions[self.row].height = max(self.ws.row_dimensions[self.row].height, needed)


def request_sheet(wb, title: str, heading: str, subject: str, parts: list[str], rows: list[dict]) -> dict:
    """One request on one sheet: for each part, the yearly tables first, then the single facts."""
    series = {id(r): as_series(r) for r in rows}
    width = max([TEXT_COLUMNS] + [len(s[1]) for s in series.values() if s])
    for pattern in (_YEAR, _FISCAL):                                # a part's table has a column for every period any of its rows reports
        width = max([width] + [len({label for r in rows if r["part"] == part and series[id(r)] and all(pattern.match(x) for x in series[id(r)][1])
                                    for label in series[id(r)][1]}) for part in parts])
    ws = wb.create_sheet(title)
    table = Table(ws, subject, width)
    ws["A1"] = heading
    ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
    counts = {"From source": sum(r["status"] == "observed" for r in rows), "Calculated": sum(r["status"] == "inferred" for r in rows)}
    counts["Not available"] = len(rows) - sum(counts.values())
    ws["A2"] = (f"{counts['From source']} facts from sources (blue), {counts['Calculated']} calculated (white), {counts['Not available']} not available "
                "(yellow). Petrol and diesel only. Figures reported for several years are set out one column a year; every row names its source.")
    ws["A2"].font = Font(name="Arial", size=10, color=INK)
    assert {r["part"] for r in rows} <= set(parts), {r["part"] for r in rows} - set(parts)
    for part in parts:
        part_rows = [r for r in rows if r["part"] == part]
        if not part_rows:
            continue
        table.section(part)
        def kind(r):
            labels = series[id(r)][1] if series[id(r)] else []
            return "year" if labels and all(_YEAR.match(x) for x in labels) else "fiscal" if labels and all(_FISCAL.match(x) for x in labels) else ""

        for wanted in ("year", "fiscal"):                            # one table each, a column for every period any row reports
            members = [r for r in part_rows if kind(r) == wanted]
            if not members:
                continue
            labels = sorted({label for r in members for label in series[id(r)][1]})
            table.header([int(x) if wanted == "year" else x for x in labels])
            for r in members:
                basis, own, values = series[id(r)]
                found = dict(zip(own, values))
                table.line(r, r["asset_or_route"], basis or ("calendar years" if wanted == "year" else "financial years"), [found.get(x) for x in labels])
        single = [r for r in part_rows if not kind(r)]
        if single:
            table.header([], value_label="Value")
            for r in single:
                parts_of = as_breakdown(r)
                if series[id(r)]:                                    # dated figures that are not plain years: one row for each date
                    basis, labels, values = series[id(r)]
                    for label, value in zip(labels, values):
                        table.line(r, r["asset_or_route"], f"{basis} {label}".strip(), [value], text=True)
                elif parts_of:
                    for label, value in parts_of:
                        table.line(r, label, r["period"], [value], text=True)
                else:
                    table.line(r, r["asset_or_route"], r["period"], [number(r["value"]) if r["value"] else "Not available"], text=True)
    ws.freeze_panes = "B3"
    return counts


def balance_sheet(wb) -> dict:
    """DR01: sales, production, imports, exports and the difference, one column a year, billion litres."""
    ws = wb.create_sheet("DR01 national balance")
    ws["A1"] = "DR01 National balance: petrol and diesel"
    ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
    ws["A2"] = ("Billion litres, calendar years. Blank means not published. Sales are the department's figures: provinces added up for 2014 to 2022, the "
                "national total for 2023. FIASA and JODI are not used.")
    ws["A2"].font = Font(name="Arial", size=10, color=INK)
    data = {(r["product"], int(r["period"])): r for r in _read(BALANCE)}
    header = ["Line"] + BALANCE_YEARS + ["Source", "Note"]
    for i, w in enumerate([24] + [8.5] * len(BALANCE_YEARS) + [58, 62], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    lines = [
        ("Sales", "sales_used", "Department of Mineral and Petroleum Resources, fuel sales volumes", "Nothing published after 2023."),
        ("Production", "production_used", "Department of Mineral and Petroleum Resources, energy balances, one file a year",
         "The last balance published is 2021."),
        ("Imports", "imports_used", "SARS customs, trade statistics portal, petrol and diesel tariff lines", "Complete calendar years, in litres."),
        ("Exports", "exports_used", "SARS customs, trade statistics portal, petrol and diesel tariff lines", ""),
        ("Stock change", None, "None", "Not published by any source used."),
        ("Supply less sales", "formula", "Calculated: production + imports - exports - sales",
         "Stock change and statistical difference together. Shown only where all four lines exist."),
    ]
    row, counts = 3, {"From source": 0, "Calculated": 0, "Not available": 0}

    def write(values, fill, bold=False, white=False):
        for i, value in enumerate(values, start=1):
            cell = ws.cell(row=row, column=i, value=value)
            cell.font = Font(name="Arial", size=10, bold=bold, color="FFFFFFFF" if white else INK)
            cell.fill = PatternFill("solid", fgColor=FILL[fill])
            cell.alignment = Alignment(wrap_text=i > len(BALANCE_YEARS) + 1, vertical="top")
            if 1 < i <= len(BALANCE_YEARS) + 1 and not white:
                cell.number_format = base.BN_FORMAT

    for product in ("petrol", "diesel"):
        row += 2
        write([product.capitalize()] + [None] * (len(header) - 1), "section", bold=True)
        row += 1
        write(header, "header", bold=True, white=True)
        at = {}
        for label, key, source, note in lines:
            row += 1
            at[label] = row
            if key is None:
                write([label] + ["" for _ in BALANCE_YEARS] + [source, note], "estimate")
                counts["Not available"] += 1
            elif key == "formula":
                cells = []
                for i, _ in enumerate(BALANCE_YEARS):
                    c = get_column_letter(2 + i)
                    need = ",".join(f"{c}{at[x]}" for x in ("Sales", "Production", "Imports", "Exports"))
                    cells.append(f'=IF(COUNT({need})<4,"",{c}{at["Production"]}+{c}{at["Imports"]}-{c}{at["Exports"]}-{c}{at["Sales"]})')
                write([label] + cells + [source, note], "formula")
                counts["Calculated"] += 1
            else:
                values = [float(data[(product, y)][key]) / 1e9 if data[(product, y)][key] else None for y in BALANCE_YEARS]
                write([label] + values + [source, note], "observation")
                counts["From source"] += 1
    ws.freeze_panes = "B3"
    return counts


PROVINCE_YEARS = list(range(2013, 2026))


def province_sheet(wb, d: dict) -> None:
    """Petrol and diesel sold in each province by year, billion litres; 2023 is an estimate and later years are blank."""
    ws = wb.create_sheet("DR01 sales by province")
    ws["A1"] = "DR01 Sales by province: petrol and diesel"
    ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
    ws["A2"] = ("Billion litres, calendar years. 2013 to 2022 are the department's district data added up by province (blue). 2023 is an estimate "
                "(yellow): the national total split by each province's share of sales in the first quarter of 2023. 2024 and 2025 are blank.")
    ws["A2"].font = Font(name="Arial", size=10, color=INK)
    header = ["Province"] + PROVINCE_YEARS + ["Source", "Note"]
    for i, w in enumerate([24] + [8.5] * len(PROVINCE_YEARS) + [58, 62], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    source = "Department of Mineral and Petroleum Resources, fuel sales volumes by magisterial district"
    row = 3

    def write(values, fill, bold=False, white=False, estimate_at=None):
        for i, value in enumerate(values, start=1):
            cell = ws.cell(row=row, column=i, value=value)
            cell.font = Font(name="Arial", size=10, bold=bold, color="FFFFFFFF" if white else INK)
            cell.fill = PatternFill("solid", fgColor=FILL["estimate" if i == estimate_at else fill])
            cell.alignment = Alignment(wrap_text=i > len(PROVINCE_YEARS) + 1, vertical="top")
            if 1 < i <= len(PROVINCE_YEARS) + 1 and not white:
                cell.number_format = base.BN_FORMAT

    at_2023 = 2 + PROVINCE_YEARS.index(2023)
    for product in ("petrol", "diesel"):
        row += 2
        write([product.capitalize()] + [None] * (len(header) - 1), "section", bold=True)
        row += 1
        write(header, "header", bold=True, white=True)
        first = row + 1
        for code in base.PROVINCES:
            row += 1
            values = [d["province"].get((product, code, y)) for y in PROVINCE_YEARS]
            values = [v / 1e3 if v is not None else None for v in values]
            values[PROVINCE_YEARS.index(2023)] = d["estimated_share"][product][2023][code] * d["dept"][(product, 2023)] / 1e3
            write([base.PROVINCE_NAMES[code]] + values + [source, "2023 is an estimate. Nothing published by province after the first quarter of 2023."],
                  "observation", estimate_at=at_2023)
        row += 1
        total = [f'=IF(COUNT({get_column_letter(2 + i)}{first}:{get_column_letter(2 + i)}{row - 1})=0,"",SUM({get_column_letter(2 + i)}{first}:'
                 f'{get_column_letter(2 + i)}{row - 1}))' for i, _ in enumerate(PROVINCE_YEARS)]
        write(["Nine provinces"] + total + ["Calculated: sum of the rows above", "The sales line on the national balance sheet."], "formula", bold=True)
        row += 1
        national = [d["dept"][(product, y)] / 1e3 if (product, y) in d["dept"] else None for y in PROVINCE_YEARS]
        write(["National file, for comparison"] + national + ["Department of Mineral and Petroleum Resources, national fuel sales volumes",
                                                              "The 2023 estimates add up to this by construction. The two files differ in 2014 and 2018."],
              "comparison")
    row += 2
    ws.cell(row=row, column=1, value="2024 and 2025 are blank: the department has published no sales after 2023. FIASA and JODI carry figures for those years, "
                                     "but they are not used.").font = Font(name="Arial", size=10, color=INK)
    ws.freeze_panes = "B3"


SECTOR_YEARS = list(range(2014, 2022))
SECTORS = [("final_consumption", "All sectors"), ("road", "Road transport"), ("rail", "Rail"), ("industry", "Industry, all"), ("mining", "Mining (part of industry)"),
           ("construction", "Construction (part of industry)"), ("agriculture", "Agriculture"), ("commercial_public", "Commercial and public services"),
           ("residential", "Households"), ("electricity_plants", "Power stations")]


def sector_sheet(wb, timeseries: Path) -> dict[tuple[str, str], int]:
    """Diesel and petrol used by each sector, from the department's energy balances, billion litres.

    Returns the row of each ``(product, sector key)`` so other sheets can point at these cells and not repeat them.
    """
    ws = wb.create_sheet("DR01 demand by sector")
    ws["A1"] = "DR01 Demand by sector: diesel and petrol"
    ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
    ws["A2"] = ("Billion litres, calendar years, as reported in the department's energy balances. The last balance is 2021, so nothing later is published by "
                "sector. Blank means the balance gives no figure.")
    ws["A2"].font = Font(name="Arial", size=10, color=INK)
    header = ["Sector"] + SECTOR_YEARS + ["Source", "Note"]
    for i, w in enumerate([34] + [8.5] * len(SECTOR_YEARS) + [58, 70], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    data = {(r["product"], r["flow_key"], int(r["period"])): float(r["value"]) / 1e9 for r in _read(timeseries / "energy_balance_department.csv")}
    notes = {"commercial_public": "Jumps from almost nothing to several billion litres from 2016: the department moved volumes between sectors, so read with care.",
             "electricity_plants": "The balances record little or none after 2016; Eskom's own reported fuel is on the DR07 sheet.",
             "final_consumption": "The department's total for all sectors. It is not the sales figure on the national balance sheet.",
             "industry": "Mining, construction, manufacturing and industry not specified, together. Manufacturing and other industry is this line less the two below."}
    row, at = 3, {}

    def write(values, fill, bold=False, white=False):
        for i, value in enumerate(values, start=1):
            cell = ws.cell(row=row, column=i, value=value)
            cell.font = Font(name="Arial", size=10, bold=bold, color="FFFFFFFF" if white else INK)
            cell.fill = PatternFill("solid", fgColor=FILL[fill])
            cell.alignment = Alignment(wrap_text=i > len(SECTOR_YEARS) + 1, vertical="top")
            if 1 < i <= len(SECTOR_YEARS) + 1 and not white:
                cell.number_format = base.BN_FORMAT

    for product in ("diesel", "petrol"):
        row += 2
        write([product.capitalize()] + [None] * (len(header) - 1), "section", bold=True)
        row += 1
        write(header, "header", bold=True, white=True)
        for key, label in SECTORS:
            values = [data.get((product, key, y)) for y in SECTOR_YEARS]
            if not any(values):
                continue                                              # a sector that uses none of this fuel
            row += 1
            at[(product, key)] = row
            write([label] + values + ["Department of Mineral and Petroleum Resources, energy balances, one file a year", notes.get(key, "")],
                  "observation", bold=key == "final_consumption")
    ws.freeze_panes = "B3"
    return at


ACTIVITY_YEARS = list(range(2014, 2026))
INTENSITY_YEARS = (2018, 2021)             # the estimate after 2021 uses the average of these years, as on the demand baseline workbook


def activity_sheet(wb, d: dict, at: dict) -> None:
    """Mining, manufacturing and agriculture: activity by year, diesel per unit of activity, and estimated diesel after 2021.

    Diesel itself is not repeated here: every figure that needs it is a formula on the demand by sector sheet.
    """
    ws = wb.create_sheet("DR01 sector activity")
    ws["A1"] = "DR01 Sector activity: mining, manufacturing and agriculture"
    ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
    ws["A2"] = ("Activity is published to 2025; diesel by sector stops at 2021. The estimate for later years is the average diesel per unit of activity in "
                f"{INTENSITY_YEARS[0]} to {INTENSITY_YEARS[1]} times the activity of that year. Diesel is read from the demand by sector sheet, not repeated here.")
    ws["A2"].font = Font(name="Arial", size=10, color=INK)
    header = ["Line", "Unit"] + ACTIVITY_YEARS + ["Source", "Note"]
    for i, w in enumerate([44, 30] + [8.5] * len(ACTIVITY_YEARS) + [50, 66], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    sheet = "'DR01 demand by sector'!"

    def here(year):
        return get_column_letter(3 + ACTIVITY_YEARS.index(year))

    def there(year, key):
        return f"{sheet}{get_column_letter(2 + SECTOR_YEARS.index(year))}{at[('diesel', key)]}"

    blocks = [
        ("Mining", "Mining production volume", "index, 2019 = 100", {y: d["index"].get(("mining_volume_total", y)) for y in ACTIVITY_YEARS},
         "Statistics South Africa, Mining production and sales (P2041)", lambda y: there(y, "mining"),
         "The energy balance's mining line includes mines' haul trucks and road vehicles."),
        ("Manufacturing and other industry", "Manufacturing production volume", "index, 2019 = 100",
         {y: d["index"].get(("manufacturing_volume_total", y)) for y in ACTIVITY_YEARS}, "Statistics South Africa, Manufacturing production and sales (P3041.2)",
         lambda y: f"({there(y, 'industry')}-{there(y, 'mining')}-N({there(y, 'construction')}))",
         "Diesel is industry less mining less construction. It is small (0.1 to 0.3 billion litres), so it moves with reclassification more than with output."),
        ("Agriculture", "Agriculture, forestry and fishing real value added", "billion rand, 2015 prices",
         {y: d["macro"].get(("agriculture_forestry_and_fishing", y)) for y in ACTIVITY_YEARS}, "Statistics South Africa, Gross domestic product (P0441)",
         lambda y: there(y, "agriculture"), "The balance's 2016 and 2017 figures are about double the other years and look like reclassification."),
    ]
    row = 3

    def write(values, fill, bold=False, white=False, fmt=None):
        for i, value in enumerate(values, start=1):
            cell = ws.cell(row=row, column=i, value=value)
            cell.font = Font(name="Arial", size=10, bold=bold, color="FFFFFFFF" if white else INK)
            cell.fill = PatternFill("solid", fgColor=FILL[fill])
            cell.alignment = Alignment(wrap_text=i > len(ACTIVITY_YEARS) + 2 or i == 1, vertical="top")
            if fmt and 2 < i <= len(ACTIVITY_YEARS) + 2:
                cell.number_format = fmt

    first, last = INTENSITY_YEARS
    for title, activity_label, unit, activity, source, diesel, note in blocks:
        row += 2
        write([title] + [None] * (len(header) - 1), "section", bold=True)
        row += 1
        write(header, "header", bold=True, white=True)
        row += 1
        activity_row = row
        write([activity_label, unit] + [activity.get(y) for y in ACTIVITY_YEARS] + [source, "Published to 2025."], "observation", fmt="#,##0.0")
        row += 1
        intensity_row = row
        per = "million litres per " + ("index point" if "index" in unit else "billion rand")
        write(["Diesel per unit of activity", per]
              + [f"={diesel(y)}*1000/{here(y)}{activity_row}" if y in SECTOR_YEARS else None for y in ACTIVITY_YEARS]
              + ["Calculated: diesel on the demand by sector sheet over the activity above", note], "formula", fmt="#,##0.00")
        row += 1
        average = f"AVERAGE({here(first)}{intensity_row}:{here(last)}{intensity_row})"
        write(["Estimated diesel after 2021", "billion litres"]
              + [f"={average}*{here(y)}{activity_row}/1000" if y > SECTOR_YEARS[-1] and activity.get(y) is not None else None for y in ACTIVITY_YEARS]
              + [f"Calculated: average diesel per unit of activity, {first} to {last}, times that year's activity",
                 "An estimate, not an observation and not an accepted model input. Holds diesel per unit of activity constant. For Nigel to agree."],
              "formula", fmt=base.BN_FORMAT)
    ws.freeze_panes = "C3"


def sizing_sheet(wb) -> None:
    """The Durban and Lesedi market sizing: one row a measure, petrol, diesel and both side by side."""
    ws = wb.create_sheet("Market sizing")
    ws["A1"] = "Market sizing: what each Vopak site can reach"
    ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
    ws["A2"] = ("Billion litres a year unless the unit says otherwise. Public data only: no client throughput is assumed. Every litre Lesedi receives by pipeline "
                "lands at Durban first, so the two site markets are never added together.")
    ws["A2"].font = Font(name="Arial", size=10, color=INK)
    header = ["Site", "Measure", "Petrol", "Diesel", "Both", "Unit", "Period", "Status", "Source", "Note"]
    widths = [18, 48, 9, 9, 9, 20, 30, 12, 52, 70]
    for i, (label, w) in enumerate(zip(header, widths), start=1):
        cell = ws.cell(row=4, column=i, value=label)
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
        cell.fill = PatternFill("solid", fgColor=FILL["header"])
        ws.column_dimensions[get_column_letter(i)].width = w
    lines: dict[tuple[str, str], dict] = {}
    for r in _read(SIZING):
        lines.setdefault((r["site"], r["measure"]), {})[r["product"]] = r
    fills = {"observed": "observation", "estimated": "formula", "assumed": "estimate"}
    for n, ((site, measure), by_product) in enumerate(lines.items(), start=5):
        first = next(iter(by_product.values()))
        both = by_product.get("petrol and diesel") or by_product.get("all products")
        values = [site, measure] + [float(by_product[p]["value"]) if p in by_product else None for p in ("petrol", "diesel")] + [
            float(both["value"]) if both else None, first["unit"], first["period"], first["status"].capitalize(), first["source"], first["note"]]
        for i, value in enumerate(values, start=1):
            cell = ws.cell(row=n, column=i, value=value)
            cell.font = Font(name="Arial", size=10, color=INK)
            cell.fill = PatternFill("solid", fgColor=FILL[fills[first["status"]]])
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if isinstance(value, float):
                cell.number_format = "0.00"
        ws.row_dimensions[n].height = 13.5 * max(1, math.ceil(len(first["note"]) / (widths[-1] * 1.15)), math.ceil(len(first["source"]) / (widths[-2] * 1.15))) + 2
    ws.freeze_panes = "C5"


def missing_rows(reference: Path) -> list[tuple[str, str, str, str]]:
    """Everything not found: ``(request, what, covers, why)``."""
    out = [("DR01", "Production after 2021", "South Africa", "The department's last energy balance is 2021. Confirmed not available on 9 October."),
           ("DR01", "Sales for 2024 and 2025", "South Africa", "The department's sales data stops at 2023. Confirmed not available on 9 October."),
           ("DR01", "Stocks, for any year", "South Africa", "Not published by any source used.")]
    for _, request, path, _, _, _ in REQUESTS:
        out += [(request, r["item"], r["asset_or_route"], r["unresolved_gap"]) for r in evidence(path, reference, request)
                if r["status"] not in ("observed", "inferred")]
    return out


def missing_sheet(wb, rows: list) -> None:
    ws = wb.create_sheet("Not available")
    ws["A1"] = "What could not be found"
    ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
    ws["A2"] = f"{len(rows)} items across the four requests. Each was searched for in published sources; the reason is given."
    ws["A2"].font = Font(name="Arial", size=10, color=INK)
    widths = [10, 46, 36, 110]
    for i, (label, w) in enumerate(zip(["Request", "What is missing", "Covers", "Why it is not available"], widths), start=1):
        cell = ws.cell(row=4, column=i, value=label)
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
        cell.fill = PatternFill("solid", fgColor=FILL["header"])
        ws.column_dimensions[get_column_letter(i)].width = w
    for n, values in enumerate(rows, start=5):
        for i, value in enumerate(values, start=1):
            cell = ws.cell(row=n, column=i, value=value)
            cell.font = Font(name="Arial", size=10, color=INK)
            cell.fill = PatternFill("solid", fgColor=FILL["estimate"])
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[n].height = 13.5 * max(math.ceil(len(v) / (w * 1.15)) for v, w in zip(values, widths)) + 2
    ws.freeze_panes = "A5"


def contents_sheet(ws, summary: list[tuple[str, str, dict | None]]) -> None:
    ws.title = "Contents"
    ws["A1"] = "Master data book: sourced data for the South Africa story"
    ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
    ws["A2"] = ("The one place to look for a sourced figure, set out by data request (DR01, DR04, DR07, DR08). Petrol and diesel only. Every figure names its "
                "source. Built by python -m lfm.scripts.build_data_requests_workbook --vintage 2026; do not edit by hand.")
    ws["A2"].font = Font(name="Arial", size=10, color=INK)
    widths = [26, 78, 13, 12, 14]
    for i, (label, w) in enumerate(zip(["Sheet", "What it holds", "From source", "Calculated", "Not available"], widths), start=1):
        cell = ws.cell(row=4, column=i, value=label)
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
        cell.fill = PatternFill("solid", fgColor=FILL["header"])
        ws.column_dimensions[get_column_letter(i)].width = w
    for n, (sheet, holds, counts) in enumerate(summary, start=5):
        values = [sheet, holds] + ([counts["From source"], counts["Calculated"], counts["Not available"]] if counts else [None, None, None])
        for i, value in enumerate(values, start=1):
            cell = ws.cell(row=n, column=i, value=value)
            cell.font = Font(name="Arial", size=10, color=INK, underline="single" if i == 1 else None)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(row=n, column=1).hyperlink = f"#'{sheet}'!A1"
    key = 6 + len(summary)
    ws.cell(row=key, column=1, value="Colours").font = Font(name="Arial", size=10, bold=True, color=INK)
    for n, (fill, text) in enumerate([("observation", "Blue: read from a published source"), ("formula", "White: calculated here from figures on the sheet"),
                                      ("estimate", "Yellow: not available")], start=key + 1):
        cell = ws.cell(row=n, column=1, value=text)
        cell.font = Font(name="Arial", size=10, color=INK)
        cell.fill = PatternFill("solid", fgColor=FILL[fill])
        ws.merge_cells(start_row=n, start_column=1, end_row=n, end_column=2)


def build(vintage: Path) -> Workbook:
    reference = vintage / "reference"
    d = base.load(vintage / "timeseries", reference)
    wb = Workbook()
    summary = [("DR01 national balance", "Sales, production, imports and exports by year, with the difference between supply and sales", balance_sheet(wb))]
    province_sheet(wb, d)
    summary.append(("DR01 sales by province", "Petrol and diesel sold in each of the nine provinces by year; 2023 estimated", None))
    at = sector_sheet(wb, vintage / "timeseries")
    summary.append(("DR01 demand by sector", "Diesel and petrol used by industry, mining, agriculture, transport and other sectors, 2014 to 2021", None))
    activity_sheet(wb, d, at)
    summary.append(("DR01 sector activity", "Mining, manufacturing and agriculture: activity to 2025, diesel per unit of activity, and estimated diesel after 2021", None))
    holds = {"DR04": "Pipeline limit and cost, regulated and published transport costs, port use, access at Durban and Lesedi, competing routes",
             "DR07": "Eskom and independent diesel burn, plant dates, vehicle fleet, new vehicles, efficiency, freight and rail",
             "DR08": "Capacity, status and closure dates, output by plant and nationally, yields, utilisation and outlook"}
    for title, request, path, parts, heading, subject in REQUESTS:
        counts = request_sheet(wb, title, heading, subject, parts, evidence(path, reference, request))
        summary.append((title, holds[request], counts))
        for add, name, text in DETAIL[request]:                      # the fuller tables behind the request, one sheet each
            add(wb, d)
            summary.append((name, text, None))
    sizing_sheet(wb)
    summary.append(("Market sizing", "What Vopak Durban and Vopak Lesedi can reach: site markets, the inland-bound flow, the trunk line and what the tanks allow", None))
    missing = missing_rows(reference)
    missing_sheet(wb, missing)
    summary.append(("Not available", f"The {len(missing)} items that could not be found, with the reason for each", None))
    contents_sheet(wb.worksheets[0], summary)
    return wb


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args()
    wb = build(Paths.default().vintage_dir(args.vintage))
    wb.save(args.out)
    print(f"wrote {args.out}: {', '.join(wb.sheetnames)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
