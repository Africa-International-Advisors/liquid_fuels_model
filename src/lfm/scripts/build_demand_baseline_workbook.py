"""Extend Nigel's demand baseline workshop workbook with the sourced history from 2012.

Opens ``output/delivered/Demand_baseline_workshop_2026_10_07_compact.xlsx`` (kept
unchanged) and writes a copy with four sheets added, following the table drawn
at the 7 October check-in:

    History          department sales by province, customs trade, refinery
                     output and the balance, 2012-2025, million litres
    Sector history   mining, manufacturing and agriculture diesel beside their
                     activity measures, with litres per unit of activity
    Checks           the workbook's Evidence rows compared with the registered
                     inputs, and what was changed in the copy
    History sources  publisher, link, original file and extract for each dataset

Observations are written as values read from ``assumptions/<vintage>/``; totals,
balances and intensities are Excel formulas, so the arithmetic can be followed in
the workbook. Nothing here is an accepted input.

Run:
    python -m lfm.scripts.build_demand_baseline_workbook --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import sys

import yaml
from collections import defaultdict
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from lfm.config import Paths
from lfm.scripts import backtest_provincial_shares as shares

SOURCE = Path("output/delivered/Demand_baseline_workshop_2026_10_07_compact.xlsx")
OUT = Path("output/delivered/Demand_baseline_workshop_2026_10_08_history.xlsx")
TRACE = Path("workstreams/WS1_data_validation/source_trace_2026-10-06.csv")
YEARS = list(range(2012, 2026))
FIRST = 6                                  # column F holds the first year, as in the other sheets
PROVINCES = ("GP", "KZN", "WC", "EC", "MP", "FS", "NW", "LP", "NC")
PROVINCE_NAMES = {"GP": "Gauteng", "KZN": "KwaZulu-Natal", "WC": "Western Cape", "EC": "Eastern Cape",
                  "MP": "Mpumalanga", "FS": "Free State", "NW": "North West", "LP": "Limpopo", "NC": "Northern Cape"}
HEAD = ["Driver / output", "Unit", "Role", "Scalar / latest value", "Definition / period"]
TAIL = ["Coverage / status", "Source", "Missing evidence / next action"]

INK = "FF243B53"
FILL = {"header": "FF243B53", "section": "FFEAF0F5", "observation": "FFEDF3FA", "formula": "FFFFFFFF",
        "comparison": "FFF4F4F4", "estimate": "FFFFF2CC"}
ML = "million L/year"


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def col(year: int) -> str:
    return get_column_letter(FIRST + YEARS.index(year))


# --- data --------------------------------------------------------------------
def load(ts: Path, ref: Path) -> dict:
    d: dict = {}
    d["dept"] = {(r["product"], int(r["period"])): float(r["value"]) / 1e6
                 for r in _read(ts / "fuel_sales_department.csv") if int(r["quarters_reported"]) == 4}
    d["province"] = {(r["product"], r["province"], int(r["period"])): float(r["value"]) / 1e6
                     for r in _read(ts / "fuel_sales_department_by_province.csv")}
    latest: dict = {}
    for r in _read(ts / "fuel_sales_fiasa.csv"):
        key = (r["product"], int(r["period"]))
        if key not in latest or r["source_report"] > latest[key][1]:
            latest[key] = (float(r["value"]) / 1e6, r["source_report"])
    d["fiasa_sales"] = {k: v[0] for k, v in latest.items()}
    latest = {}
    for r in _read(ts / "fuel_trade_fiasa.csv"):
        key = (r["flow"], r["product"], int(r["period"]))
        if key not in latest or r["source_report"] > latest[key][1]:
            latest[key] = (float(r["value"]) / 1e6, r["source_report"])
    d["fiasa_trade"] = {k: v[0] for k, v in latest.items()}
    d["sars"] = {(r["flow"], r["product"], int(r["period"])): float(r["value"]) / 1e6
                 for r in _read(ts / "fuel_trade_sars.csv")
                 if r["unit"] == "litres" and int(r["months_reported"]) == 12}
    d["balance"] = {(r["flow_key"], r["product"], int(r["period"])): float(r["value"]) / 1e6
                    for r in _read(ts / "energy_balance_department.csv") if r["flow_key"]}
    d["operators"] = {(r["plant"], int(r["period"])): (float(r["value"]), r["unit"], r["period_basis"])
                      for r in _read(ref / "refinery_output_operators.csv")}
    raf = {(r["measure"], int(r["period"])): float(r["value"]) for r in _read(ref / "fuel_levy_revenue_raf.csv")}
    d["raf_litres"] = {y: raf[("gross_fuel_levies", y)] * 1000 / (raf[("levy_rate", y)] / 100) / 1e6 for y in (2024, 2025)}
    monthly = defaultdict(list)
    for r in _read(ts / "activity_statssa_monthly.csv"):
        monthly[(r["series"], int(r["period"][:4]))].append(float(r["value"]))
    d["index"] = {k: sum(v) / len(v) for k, v in monthly.items() if len(v) == 12}
    # Estimated provincial shares after the last full year of provincial data (2022).
    observed = shares.load(ts)
    d["estimated_share"] = {}
    for product in ("petrol", "diesel"):
        y2023 = shares.share(observed["quarter1"][(product, 2023)])
        y2024 = shares.moved(y2023, shares.share(observed["gdp"][2023]), shares.share(observed["gdp"][2024]))
        d["estimated_share"][product] = {2023: y2023, 2024: y2024, 2025: y2024}
    # Vehicle block.
    d["stock"] = {(r["vehicle_class"], int(r["period"][:4])): float(r["value"])
                  for r in _read(ts / "vehicle_population_natis.csv")
                  if r["province"] == "ZAF" and r["period"].endswith("-12")}
    d["new_sales"] = {(r["segment"], int(r["period"])): float(r["value"])
                      for r in _read(ts / "new_vehicle_market_naamsa.csv") if r["basis"] == "actual"}
    d["nev"] = {(r["drivetrain"], int(r["period"])): float(r["value"]) for r in _read(ts / "nev_sales_naamsa.csv")}
    d["by_fuel_2023"] = {r["fuel_type"]: float(r["vehicles"]) for r in _read(ref / "vehicle_population_by_fuel_dot2023.csv")}
    d["stone"] = {r["vehicle_type"]: r for r in _read(ref / "vehicle_parameters_stone2018.csv")}
    model = yaml.safe_load((ts.parent / "vehicles.yaml").read_text(encoding="utf-8"))
    d["model_vehicles"] = {key: model[key]["by_country"]["ZAF"] for key in (
        "annual_km_per_vehicle", "fuel_consumption", "petrol_diesel_split", "scrappage_rate", "new_vehicle_segment_split")}
    d["macro"] = {(r["series"], int(r["period"])): float(r["value"]) / 1e9
                  for r in _read(ts / "macro_statssa.csv") if r["basis"] == "actual" and r["unit"].startswith("rand")}
    return d


# --- sheet writer -------------------------------------------------------------
class Sheet:
    def __init__(self, wb, title: str, heading: str, sub: str):
        self.ws = wb.create_sheet(title)
        self.row = 4
        self.ws["A1"] = heading
        self.ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
        self.ws["A2"] = sub
        self.ws["A2"].font = Font(name="Arial", size=10, color=INK)
        for i, label in enumerate(HEAD + YEARS + TAIL, start=1):
            cell = self.ws.cell(row=4, column=i, value=label)
            cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
            cell.fill = PatternFill("solid", fgColor=FILL["header"])
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        widths = [34, 14, 17, 15, 44] + [11.5] * len(YEARS) + [26, 44, 44]
        for i, width in enumerate(widths, start=1):
            self.ws.column_dimensions[get_column_letter(i)].width = width
        self.ws.freeze_panes = "B5"

    def section(self, title: str) -> None:
        self.row += 2 if self.row > 4 else 1
        for i in range(1, len(HEAD) + len(YEARS) + len(TAIL) + 1):
            cell = self.ws.cell(row=self.row, column=i, value=title if i == 1 else None)
            cell.font = Font(name="Arial", size=10, bold=True, color=INK)
            cell.fill = PatternFill("solid", fgColor=FILL["section"])

    def line(self, label, unit, role, definition, values=None, formula=None, kind="observation", scalar=None,
             status="", source="", action="", fmt="#,##0.0") -> int:
        """Write one row. ``values`` is ``{year: number}``; ``formula`` is ``f(year) -> str | None``."""
        self.row += 1
        cells = [label, unit, role, scalar, definition]
        for year in YEARS:
            if formula is not None:
                cells.append(formula(year))
            else:
                cells.append((values or {}).get(year))
        cells += [status, source, action]
        for i, value in enumerate(cells, start=1):
            cell = self.ws.cell(row=self.row, column=i, value=value)
            cell.font = Font(name="Arial", size=10, color=INK)
            cell.fill = PatternFill("solid", fgColor=FILL[kind])
            cell.alignment = Alignment(wrap_text=i in (1, 5, 20, 21, 22), vertical="top")
            if i == 4 or FIRST <= i < FIRST + len(YEARS):
                cell.number_format = fmt
        return self.row


def both(a: int, b: int, expression: str):
    """Formula that stays blank unless both referenced cells hold numbers."""
    return lambda year: f'=IF(COUNT({col(year)}{a},{col(year)}{b})<2,"",{expression.format(c=col(year), a=a, b=b)})'


def history_sheet(wb, d: dict) -> dict:
    s = Sheet(wb, "History", "Historical baseline, 2012-2025",
              "Layout follows the table drawn at the 7 October check-in. Observations are values from the registered "
              "inputs; totals and balances are formulas. Million litres a year, calendar years unless a row says otherwise.")
    rows: dict = {}
    dept_src = "Department of Mineral and Petroleum Resources, sales volumes"
    for product in ("petrol", "diesel"):
        s.section(f"1. Department sales by province: {product}")
        first = s.row + 1
        for code in PROVINCES:
            s.line(f"{PROVINCE_NAMES[code]} {product}", ML, "Source observation",
                   "District-level sales summed to province. Shows where fuel was sold, not where it was used.",
                   {y: d["province"].get((product, code, y)) for y in YEARS},
                   status="2013-2022 full years; 2023 has quarter 1 only", source=dept_src + ", district workbooks")
        last = s.row
        rows[f"{product}_provinces"] = s.line(
            f"Sum of nine provinces, {product}", ML, "Reporting formula", "Sum of the nine rows above.",
            formula=lambda y, a=first, b=last: f'=IF(COUNT({col(y)}{a}:{col(y)}{b})<9,"",SUM({col(y)}{a}:{col(y)}{b}))',
            kind="formula")
        rows[f"{product}_dept"] = s.line(
            f"Department national file, {product}", ML, "Source observation",
            "National annual workbook, years with four quarters reported.",
            {y: d["dept"].get((product, y)) for y in YEARS},
            status="2012-2023; nothing published for 2024 or 2025", source=dept_src + ", national workbooks",
            action="2024 national sales: source to be agreed (Nigel)")
        s.line(f"Provinces less national, {product}", ML, "Reporting formula",
               "Difference between the department's two files. 2013 and 2015 traced; 2014 and 2018 for decision.",
               formula=both(rows[f"{product}_provinces"], rows[f"{product}_dept"], "{c}{a}-{c}{b}"), kind="formula",
               action="See integrity_flag_log_2026-10-06.md")

    s.section("2. Customs trade (SARS)")
    sars_src = "South African Revenue Service, trade statistics by tariff line"
    for flow, name in (("import", "Imports"), ("export", "Exports")):
        for product in ("diesel", "petrol"):
            rows[f"{flow}_{product}"] = s.line(
                f"{name}, {product}", ML, "Source observation",
                "Complete years reported in litres. Before 2014 customs is in kilograms or mixed units and is not used.",
                {y: d["sars"].get((flow, product, y)) for y in YEARS},
                status="2014-2025 (2026 to August, not shown)", source=sars_src)
        rows[f"{flow}_total"] = s.line(
            f"{name}, diesel and petrol", ML, "Reporting formula", "Sum of the two rows above.",
            formula=both(rows[f"{flow}_diesel"], rows[f"{flow}_petrol"], "{c}{a}+{c}{b}"), kind="formula")
    for product in ("diesel", "petrol", "total"):
        rows[f"net_{product}"] = s.line(
            f"Net imports, {'diesel and petrol' if product == 'total' else product}", ML, "Reporting formula",
            "Imports less exports.", formula=both(rows[f"import_{product}"], rows[f"export_{product}"], "{c}{a}-{c}{b}"),
            kind="formula")
    for flow, name in (("import", "Imports"), ("export", "Exports")):
        for product in ("diesel", "petrol"):
            s.line(f"FIASA {name.lower()}, {product}", ML, "Comparison only",
                   "FIASA annual report, latest edition for each year. Not used in the balance.",
                   {y: d["fiasa_trade"].get((flow, product, y)) for y in YEARS}, kind="comparison",
                   status="2024 diesel imports is a suspected misprint (14,793 for 10,793)" if (flow, product) == ("import", "diesel") else "",
                   source="Fuels Industry Association of South Africa, annual reports")

    s.section("3. Refinery production")
    for product in ("petrol", "diesel"):
        rows[f"production_{product}"] = s.line(
            f"Production reported, {product}", ML, "Source observation",
            "National production line of the department's energy balance. The only production by product.",
            {y: d["balance"].get(("production", product, y)) for y in YEARS},
            status="2012-2021; no balance published after 2021", source="Department energy balances",
            action="Production by product after 2021 is not published by any source found")
    for plant, label in (("Secunda", "Secunda, all refined products"), ("Natref", "Natref, Sasol's 63.64% share"),
                         ("Astron Energy (Cape Town)", "Astron (Cape Town), all refined products")):
        sample = next(v for (p, _), v in d["operators"].items() if p == plant)
        s.line(label, sample[1], "Reported units; not converted",
               f"As reported by the operator; {sample[2]}. All products together, so not comparable with the rows above "
               "without assumptions.",
               {y: d["operators"][(plant, y)][0] for y in YEARS if (plant, y) in d["operators"]}, kind="comparison",
               status="Operator reports; no split by product",
               source="Sasol production metrics; Glencore annual reports", fmt="#,##0.0")

    s.section("4. Balance: consumption = imports - exports + production + stock change")
    for product in ("petrol", "diesel"):
        fiasa = s.line(f"FIASA sales, {product}", ML, "Comparison only",
                       "FIASA annual report, latest edition. Attributed by FIASA to the department.",
                       {y: d["fiasa_sales"].get((product, y)) for y in YEARS}, kind="comparison",
                       status="2024 differs between FIASA's 2024 and 2025 editions",
                       source="Fuels Industry Association of South Africa, annual reports")
        sales = s.line(f"Sales used, {product}", ML, "Reporting formula",
                       "Department national file where published; otherwise FIASA, which is unverified.",
                       formula=lambda y, a=rows[f"{product}_dept"], b=fiasa:
                       f'=IF(ISNUMBER({col(y)}{a}),{col(y)}{a},IF(ISNUMBER({col(y)}{b}),{col(y)}{b},""))', kind="formula",
                       status="Department to 2023; FIASA for 2024", action="Agree the 2024 source (Nigel)")
        rows[f"sales_{product}"] = sales
        net = s.line(f"Net imports used, {product}", ML, "Reporting formula",
                     "SARS customs from 2014 (section 2).",
                     formula=lambda y, a=rows[f"net_{product}"]: f'=IF(ISNUMBER({col(y)}{a}),{col(y)}{a},"")', kind="formula")
        slni = s.line(f"Sales less net imports, {product}", ML, "Reporting formula",
                      "What production, stock changes and gaps in sales coverage must together supply. Not a "
                      "measurement of production.", formula=both(sales, net, "{c}{a}-{c}{b}"), kind="formula")
        rows[f"slni_{product}"] = slni
        s.line(f"Unexplained after reported production, {product}", ML, "Reporting formula",
               "Sales less net imports less reported production: stock change plus anything the sources do not cover.",
               formula=both(slni, rows[f"production_{product}"], "{c}{a}-{c}{b}"), kind="formula",
               status="Only where production is reported (to 2021)",
               action="No usable stock series exists; JODI's carries its lowest reliability code")

    s.section("5. Independent count of litres: Road Accident Fund levy (new evidence, 7 October)")
    raf = s.line("Litres levied, petrol and diesel", ML, "Comparison only",
                 "Gross levies divided by 218 cents a litre. Fiscal year to 31 March of the following year, shown under "
                 "the calendar year it mostly covers.",
                 {2023: d["raf_litres"][2024], 2024: d["raf_litres"][2025]}, kind="comparison",
                 status="Both fuels together; accrual basis; not reconciled with SARS's statement",
                 source="Road Accident Fund Annual Report 2024/25, note 16 (p.183)")
    recorded = s.line("Recorded sales used, petrol and diesel", ML, "Reporting formula", "Sum of the two 'sales used' rows.",
                      formula=both(rows["sales_petrol"], rows["sales_diesel"], "{c}{a}+{c}{b}"), kind="formula")
    s.line("Litres levied less recorded sales", ML, "Reporting formula",
           "An indication that recorded sales may undercount. A hypothesis to test; not added to demand.",
           formula=both(raf, recorded, "{c}{a}-{c}{b}"), kind="formula")

    for product in ("petrol", "diesel"):
        s.section(f"6. Estimated sales by province, 2023-2025: {product} (estimates, not observations)")
        share_rows = {}
        for code in PROVINCES:
            share_rows[code] = s.line(
                f"{PROVINCE_NAMES[code]} share of {product}", "% of national", "Proposed estimate",
                "2023: the province's share of quarter 1 2023 sales, as observed. 2024: the 2023 share moved with the "
                "province's share of real GDP. 2025: 2024 held.",
                {y: d["estimated_share"][product][y][code] * 100 for y in (2023, 2024, 2025)}, kind="estimate",
                status="Estimate", source="Department district data, quarter 1 2023; Stats SA P0441.2", fmt="0.0")
        for code in PROVINCES:
            s.line(f"{PROVINCE_NAMES[code]} {product}, estimated", ML, "Proposed estimate",
                   "Estimated share times national sales used (section 4). Blank where no national figure exists.",
                   formula=lambda y, a=share_rows[code], b=rows[f"sales_{product}"]:
                   (f'=IF(COUNT({col(y)}{a},{col(y)}{b})<2,"",{col(y)}{a}/100*{col(y)}{b})' if y >= 2023 else None),
                   kind="estimate", status="Estimate; 2024 also carries the unverified national total",
                   action="Replace when the department publishes district data after 2023 quarter 1")
    return rows


def sector_sheet(wb, d: dict) -> None:
    s = Sheet(wb, "Sector history", "Mining, manufacturing and agriculture: diesel beside activity, 2012-2025",
              "Diesel is from the department's energy balances (to 2021). The balance attributes fuel to the sector "
              "that bought it. Intensities and the indicative rows are formulas.")

    def eb(key: str) -> dict:
        return {y: d["balance"].get((key, "diesel", y)) for y in YEARS}

    eb_src = "Department energy balances, diesel"

    def block(title, diesel_label, diesel_values, diesel_formula, activity_label, activity_unit, activity, activity_src,
              intensity_unit, note):
        s.section(title)
        if diesel_formula is None:
            fuel = s.line(diesel_label, ML, "Source observation", note, diesel_values, status="2012-2021", source=eb_src)
        else:
            fuel = s.line(diesel_label, ML, "Reporting formula", note, formula=diesel_formula, kind="formula")
        act = s.line(activity_label, activity_unit, "Source observation",
                     "Annual mean of twelve monthly indices." if "index" in activity_unit else "Annual real value added.",
                     activity, status="2012-2025", source=activity_src)
        intensity = s.line(f"Diesel per unit of activity ({intensity_unit})", intensity_unit, "Reporting formula",
                           "Diesel divided by the activity measure, each year both exist.",
                           formula=both(fuel, act, "{c}{a}/{c}{b}"), kind="formula", fmt="#,##0.00")
        a, b = col(2018), col(2021)
        average = f"=AVERAGE({a}{intensity}:{b}{intensity})"
        s.line(f"Indicative diesel at observed activity ({diesel_label.split(',')[0].lower()})", ML, "Proposed estimate",
               "Average 2018-2021 intensity (column D) times the activity measure. An indication for years without a "
               "balance; not an observation and not an accepted input.",
               formula=lambda y, r=act, me=s.row + 1: f'=IF(ISNUMBER({col(y)}{r}),$D${me}*{col(y)}{r},"")',
               kind="estimate", scalar=average, status="Estimate for discussion",
               action="Agree base year, driver and whether intensity is held constant (Nigel)")
        return fuel

    mining = block("Mining", "Mining and quarrying diesel, energy balance", eb("mining"), None,
                   "Mining production volume", "index 2019=100", {y: d["index"].get(("mining_volume_total", y)) for y in YEARS},
                   "Statistics South Africa P2041", "million L per index point",
                   "Includes unregistered haul trucks and mines' road vehicles; the balance does not separate them.")
    s.section("Industry other than mining")
    industry = s.line("Industry diesel, energy balance (parent line)", ML, "Source observation",
                      "Parent 'industry' line: mining, construction, manufacturing sub-sectors and non-specified.",
                      eb("industry"), status="2012-2021", source=eb_src)
    construction = s.line("Construction diesel, energy balance", ML, "Source observation",
                          "Reported construction line; too small to be all construction plant.", eb("construction"),
                          status="2012-2021; blank where not reported", source=eb_src)

    def rest(y: int) -> str:
        return (f'=IF(COUNT({col(y)}{industry},{col(y)}{mining})<2,"",{col(y)}{industry}-{col(y)}{mining}'
                f'-IF(ISNUMBER({col(y)}{construction}),{col(y)}{construction},0))')

    block("Manufacturing and non-specified industry", "Manufacturing and other industry diesel, by difference", None, rest,
          "Manufacturing production volume", "index 2019=100",
          {y: d["index"].get(("manufacturing_volume_total", y)) for y in YEARS},
          "Statistics South Africa P3041.2", "million L per index point",
          "Industry less mining less construction. Small (0.1-0.3 bn litres), so it moves with reclassification in "
          "the balance more than with output.")
    block("Agriculture", "Agriculture and forestry diesel, energy balance", eb("agriculture"), None,
          "Agriculture, forestry and fishing real value added", "bn 2015 rand",
          {y: d["macro"].get(("agriculture_forestry_and_fishing", y)) for y in YEARS},
          "Statistics South Africa P0441", "million L per bn rand",
          "2016 and 2017 are about double the other years in the balance and look like reclassification.")


def vehicle_sheet(wb, d: dict, history_rows: dict) -> None:
    s = Sheet(wb, "Vehicle history", "Vehicle block: what is observed beside what the model assumes",
              "Stock, new sales, scrapping, drivetrain, fuel split and use. Observations are values from the registered "
              "inputs; the model's settings are in column D; shares, retirements and cross-checks are formulas.")
    m = d["model_vehicles"]
    natis, naamsa = "NaTIS live vehicle population, December", "naamsa industry vehicle sales"

    s.section("1. Registered vehicles at December")
    stock = {}
    for key, label in (("cars", "Cars"), ("light_commercial", "Light commercial vehicles"), ("trucks", "Trucks"),
                       ("buses", "Buses"), ("minibuses", "Minibuses"), ("motorcycles", "Motorcycles")):
        stock[key] = s.line(label, "vehicles", "Source observation", "Live (licensed) vehicles, all fuels together.",
                            {y: d["stock"].get((key, y)) for y in YEARS}, status="2021-2025", source=natis, fmt="#,##0",
                            action="No split by fuel or by age in this source")

    s.section("2. New vehicle sales")
    sales = {}
    for key, label, model_key in (("cars", "Cars", "passenger"), ("light_commercial", "Light commercial vehicles", "lcv"),
                                  ("medium_heavy_commercial", "Medium and heavy commercial vehicles", "hcv")):
        sales[key] = s.line(f"{label}, new sales", "vehicles/year", "Source observation", "Actual new sales, all drivetrains.",
                            {y: d["new_sales"].get((key, y)) for y in YEARS}, status="2017-2025", source=naamsa, fmt="#,##0")
    total = s.line("All segments, new sales", "vehicles/year", "Source observation", "Total market as reported.",
                   {y: d["new_sales"].get(("total", y)) for y in YEARS}, status="2017-2025", source=naamsa, fmt="#,##0")
    for key, label, model_key in (("cars", "Cars", "passenger"), ("light_commercial", "Light commercial", "lcv"),
                                  ("medium_heavy_commercial", "Medium and heavy commercial", "hcv")):
        s.line(f"{label} share of new sales", "%", "Reporting formula",
               "Observed share. Column D is the model's fixed split of new vehicles.",
               formula=both(sales[key], total, "{c}{a}/{c}{b}*100"), kind="formula",
               scalar=m["new_vehicle_segment_split"][model_key] * 100, fmt="0.0",
               status="Model setting in column D", source="assumptions/2026/vehicles.yaml: new_vehicle_segment_split")

    s.section("3. Apparent retirements: last December's stock plus this year's sales less this December's stock")
    for key, sale, label, model_key in (("cars", "cars", "Cars", "passenger"),
                                        ("light_commercial", "light_commercial", "Light commercial vehicles", "lcv"),
                                        ("trucks", "medium_heavy_commercial", "Trucks", "hcv")):
        def retired(y, a=stock[key], b=sales[sale]):
            if y - 1 not in YEARS:
                return None
            prev, now = col(y - 1), col(y)
            return f'=IF(COUNT({prev}{a},{now}{a},{now}{b})<3,"",{prev}{a}+{now}{b}-{now}{a})'
        gone = s.line(f"{label} retired", "vehicles/year", "Reporting formula",
                      "Includes deregistration, export and write-off; used imports and re-registration would lower it.",
                      formula=retired, kind="formula", fmt="#,##0")
        s.line(f"{label} retirement rate", "% of last December's stock", "Reporting formula",
               "Retired divided by last December's stock. Column D is the model's scrappage rate.",
               formula=lambda y, a=gone, b=stock[key]: (None if y - 1 not in YEARS else
                                                       f'=IF(ISNUMBER({col(y)}{a}),{col(y)}{a}/{col(y - 1)}{b}*100,"")'),
               kind="formula", scalar=m["scrappage_rate"][model_key] * 100, fmt="0.0",
               status="Model setting in column D", source="assumptions/2026/vehicles.yaml: scrappage_rate")

    s.section("4. Electrified new sales (all segments)")
    for key, label in (("battery_electric", "Battery electric"), ("plug_in_hybrid", "Plug-in hybrid"),
                       ("traditional_hybrid", "Conventional hybrid")):
        row = s.line(f"{label}, new sales", "vehicles/year", "Source observation", "Total market, not passenger cars only.",
                     {y: d["nev"].get((key, y)) for y in YEARS}, status="2019-2025", source="naamsa new-energy vehicle sales",
                     fmt="#,##0")
        s.line(f"{label} share of new sales", "%", "Reporting formula", "Share of all new vehicles sold in the year.",
               formula=both(row, total, "{c}{a}/{c}{b}*100"), kind="formula", fmt="0.00",
               action="Share of the fleet is not observed after December 2023")

    s.section("5. Fuel split of the registered fleet")
    fuel = d["by_fuel_2023"]
    petrol = s.line("Petrol vehicles registered", "vehicles", "Source observation", "All classes, December 2023.",
                    {2023: fuel["petrol"]}, status="One date only", source="Department of Transport, 2023", fmt="#,##0")
    diesel = s.line("Diesel vehicles registered", "vehicles", "Source observation", "All classes, December 2023.",
                    {2023: fuel["diesel"]}, status="One date only", source="Department of Transport, 2023", fmt="#,##0")
    s.line("Electric vehicles registered", "vehicles", "Source observation", "All classes, December 2023.",
           {2023: fuel["electricity"]}, status="One date only", source="Department of Transport, 2023", fmt="#,##0")
    split = m["petrol_diesel_split"]
    implied = s.line("Diesel vehicles implied by the model's split", "vehicles", "Reporting formula",
                     f"Cars x {split['passenger']['diesel']:.0%} plus light commercial x {split['lcv']['diesel']:.0%} plus "
                     "trucks and buses. The model's split is for new sales; applied here to stock as a test.",
                     formula=lambda y: (f'=IF(COUNT({col(y)}{stock["cars"]},{col(y)}{stock["light_commercial"]})<2,"",'
                                        f'{col(y)}{stock["cars"]}*{split["passenger"]["diesel"]}+'
                                        f'{col(y)}{stock["light_commercial"]}*{split["lcv"]["diesel"]}+'
                                        f'{col(y)}{stock["trucks"]}+{col(y)}{stock["buses"]})'),
                     kind="formula", fmt="#,##0", source="assumptions/2026/vehicles.yaml: petrol_diesel_split")
    s.line("Implied less registered diesel vehicles", "vehicles", "Reporting formula",
           "Positive means the model's split puts more diesel vehicles on the road than are registered. Minibuses and "
           "motorcycles are left out of the implied figure.",
           formula=both(implied, diesel, "{c}{a}-{c}{b}"), kind="formula", fmt="#,##0")

    s.section("6. Distance and fuel use: model settings beside the published study")
    stone, km, use = d["stone"], m["annual_km_per_vehicle"], m["fuel_consumption"]
    for label, model_value, study_key, column, unit in (
            ("Passenger cars, distance", km["passenger"], "CarGasoline", "km_per_year_fleet_average", "km/vehicle/year"),
            ("Light commercial, distance", km["lcv"], "LCVDiesel", "km_per_year_fleet_average", "km/vehicle/year"),
            ("Heavy commercial, distance", km["hcv"], "HCV5Diesel", "km_per_year_fleet_average", "km/vehicle/year"),
            ("Petrol cars, fuel use", use["passenger"]["ice_petrol"], "CarGasoline", "l_per_100km_fleet_average", "L/100 km"),
            ("Diesel light commercial, fuel use", use["lcv"]["ice_diesel"], "LCVDiesel", "l_per_100km_fleet_average", "L/100 km"),
            ("Heavy commercial, fuel use", use["hcv"]["ice_diesel"], "HCV5Diesel", "l_per_100km_fleet_average", "L/100 km")):
        s.line(label, unit, "Model setting", f"Column D is the model's value. The study gives {float(stone[study_key][column]):,.1f} "
               f"for {study_key} (fleet average, 2014 base).", scalar=model_value, kind="comparison", fmt="#,##0.0",
               status="Model value is a placeholder with no source", source="Stone et al. (2018); assumptions/2026/vehicles.yaml",
               action="The heavy class in the study spans nine weight classes; HCV5 is shown as a mid-point")
    per_vehicle = s.line("Petrol sold per registered petrol vehicle", "litres/vehicle/year", "Reporting formula",
                         "National petrol sales used (History) divided by registered petrol vehicles.",
                         formula=lambda y: f'=IF(COUNT(History!{col(y)}{history_rows["sales_petrol"]},{col(y)}{petrol})<2,"",'
                                           f'History!{col(y)}{history_rows["sales_petrol"]}*1000000/{col(y)}{petrol})',
                         kind="formula", fmt="#,##0")
    study_use = float(stone["CarGasoline"]["l_per_100km_fleet_average"])
    s.line("Distance implied by petrol sales", "km/vehicle/year", "Reporting formula",
           f"Litres per vehicle divided by {study_use} L/100 km (the study's petrol car average). Column D is the model's "
           "passenger distance.", formula=lambda y: f'=IF(ISNUMBER({col(y)}{per_vehicle}),{col(y)}{per_vehicle}/{study_use}*100,"")',
           kind="formula", scalar=km["passenger"], fmt="#,##0",
           action="If the model's distance and fuel use both held, petrol sales would be far above what is recorded")

    s.section("7. Not available from any source held")
    for label, why in (
            ("Stock by age (year of first registration)", "Needed for the cohort calculation; NaTIS publishes totals by class only."),
            ("Stock by fuel within each class", "Only an all-class fuel count exists, for December 2023."),
            ("Electric and hybrid vehicles in the fleet by year", "Sales are known from 2019; stock only for December 2023."),
            ("Distance driven after 2014", "The study's figures are a 2014 base; no later survey is held."),
            ("Petrol and diesel split of new sales by segment", "naamsa reports drivetrain for the total market only.")):
        s.line(label, "", "Missing input", why, kind="estimate", status="Gap", action="Source to be found or assumption agreed")


def checks_sheet(wb, d: dict, changes: list[str]) -> int:
    ws = wb.create_sheet("Checks")
    ws["A1"] = "Checks on the workshop workbook, 7 October 2026"
    ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
    ws["A2"] = ("Each Evidence row that can be traced to a registered input is recomputed from that input. "
                "Differences above 0.05% are listed as 'differs'.")
    header = ["Evidence row", "Series", "Year", "Workbook value", "Recomputed from inputs", "Result", "Input file"]
    for i, label in enumerate(header, start=1):
        cell = ws.cell(row=4, column=i, value=label)
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
        cell.fill = PatternFill("solid", fgColor=FILL["header"])
    for i, width in enumerate([12, 40, 8, 18, 22, 14, 48], start=1):
        ws.column_dimensions[get_column_letter(i)].width = width

    def expected(series: str, year: int):
        product = {"petrol": "petrol", "diesel": "diesel", "jet": "jet", "fuel_oil": "fuel_oil"}
        if series.startswith("sales_") and series[6:] in product:
            return d["fiasa_sales"].get((series[6:], year)), "fuel_sales_fiasa.csv"
        if series.startswith("dept_") and series[5:] in product:
            return d["dept"].get((series[5:], year)), "fuel_sales_department.csv"
        if series in ("manufacturing_volume_total", "mining_volume_total"):
            return d["index"].get((series, year)), "activity_statssa_monthly.csv"
        if series.startswith("macro_") and (series[6:], year) in d["macro"]:
            # Value added is shown in billions of rand; GDP per person is in rand.
            scale = 1e9 if series == "macro_gdp_per_capita" else 1
            return d["macro"][(series[6:], year)] * scale, "macro_statssa.csv"
        if series.startswith("Provincial: "):
            code, fuel = series.split()[1], series.split()[2]
            return d["province"].get((fuel, code, year)), "fuel_sales_department_by_province.csv"
        return None, ""

    evidence = wb["Evidence"]
    years = {c.column: c.value for c in evidence[4] if isinstance(c.value, int)}
    row, checked, differs = 4, 0, 0
    for cells in evidence.iter_rows(min_row=5):
        series = cells[0].value
        if not isinstance(series, str):
            continue
        for cell in cells:
            if cell.column in years and isinstance(cell.value, (int, float)):
                # The Evidence sheet shortens long provincial labels; recover province and fuel from the label.
                want, source = expected(series, years[cell.column])
                if want is None:
                    continue
                checked += 1
                ok = abs(cell.value - want) <= 0.0005 * max(abs(want), 1)
                differs += not ok
                row += 1
                for i, value in enumerate([cell.coordinate, series, years[cell.column], cell.value, want,
                                           "matches" if ok else "differs", source], start=1):
                    c = ws.cell(row=row, column=i, value=value)
                    c.font = Font(name="Arial", size=10, color=INK)
                    if i in (4, 5):
                        c.number_format = "#,##0.000"
    row += 2
    notes = [f"{checked} values recomputed; {differs} differ.",
             "Not recomputed: vehicle sales and stock, electric vehicle sales, freight, power and airport rows "
             "(vehicle block is next), and every 'Model run' row, which is a frozen engine run on main.",
             "The model run in this workbook was made on main, where industry starts at 2.5 bn litres and agriculture "
             "at 0.7 (2024). manish-branch proposes 1.50 and 1.06 (2021 energy balance); see sector_baselines_2026-10-07.md."]
    for text in notes + ["Changes made in this copy:"] + changes:
        ws.cell(row=row, column=1, value=text).font = Font(name="Arial", size=10, color=INK)
        row += 1
    return differs


def sources_sheet(wb) -> None:
    wanted = {
        "fuel_sales_department": "History sections 1 and 4: national sales",
        "fuel_sales_department_by_province": "History section 1: sales by province",
        "fuel_trade_sars": "History section 2: imports and exports",
        "fuel_trade_fiasa": "History section 2: FIASA comparison rows",
        "fuel_sales_fiasa": "History section 4: FIASA comparison row",
        "energy_balance_department": "History section 3 and Sector history: production and diesel by sector",
        "refinery_output_operators": "History section 3: operators' reported output",
        "fuel_levy_revenue_raf": "History section 5: litres levied",
        "activity_statssa_monthly": "Sector history: mining and manufacturing volume indices",
        "macro_statssa": "Sector history: agriculture real value added",
    }
    trace = {r["dataset"]: r for r in _read(TRACE)}
    ws = wb.create_sheet("History sources")
    ws["A1"] = "Sources for the History and Sector history sheets"
    ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
    header = ["Used for", "Publisher", "Link", "Original file", "Where the original is kept", "Extract in the repository",
              "Refresh command", "Periods", "Limits"]
    for i, label in enumerate(header, start=1):
        cell = ws.cell(row=4, column=i, value=label)
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
        cell.fill = PatternFill("solid", fgColor=FILL["header"])
    for i, width in enumerate([44, 40, 52, 46, 40, 52, 46, 14, 60], start=1):
        ws.column_dimensions[get_column_letter(i)].width = width
    for n, (dataset, use) in enumerate(wanted.items(), start=5):
        r = trace[dataset]
        values = [use, r["publisher"], r["source_url"], r["original_file"], r["original_location"], r["extract_path"],
                  r["refresh_command"], f'{r["first_period"]}-{r["last_period"]}', r["issue"]]
        for i, value in enumerate(values, start=1):
            c = ws.cell(row=n, column=i, value=value)
            c.font = Font(name="Arial", size=10, color=INK)
            c.alignment = Alignment(wrap_text=True, vertical="top")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--out", default=str(OUT), help="where to write the extended workbook")
    args = parser.parse_args()
    vintage = Paths.default().vintage_dir(args.vintage)
    d = load(vintage / "timeseries", vintage / "reference")
    wb = load_workbook(SOURCE)

    changes = []
    selection = wb["Source selection"]
    for cells in selection.iter_rows(min_row=5, max_row=24):
        if cells[4].value == "FIASA" and cells[1].value in (2022, 2023):
            cells[4].value = "Department"
            changes.append(f"Source selection!{cells[4].coordinate}: {cells[0].value} {cells[1].value} FIASA -> Department "
                           "(official series; the two agree to within rounding in these years).")
    changes.append("Source selection: 2024 left on FIASA, which is unverified; the department has published no 2024 figure.")
    changes.append("Sheets added: History, Sector history, Vehicle history, Checks, History sources. No other cell changed.")

    history_rows = history_sheet(wb, d)
    sector_sheet(wb, d)
    vehicle_sheet(wb, d, history_rows)
    differs = checks_sheet(wb, d, changes)
    sources_sheet(wb)
    wb.save(args.out)
    print(f"wrote {args.out}; evidence values that differ from the inputs: {differs}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
