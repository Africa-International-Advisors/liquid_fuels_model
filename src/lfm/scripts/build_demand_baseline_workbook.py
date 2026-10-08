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
LEVERS = Path("workstreams/WS2_model_development/fuel_lever_response_2026-10-07.csv")
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
FUTURE = list(range(2022, 2036))           # the power fleet block looks forward, like Nigel's sheets
IRP_GAS_MW_2030 = 6000                     # IRP 2025: about 6 GW of gas by 2030 (TechCentral, 22 April 2026)
GAS_SWITCH_YEAR = 2028                     # first full year after Eskom's stated December 2027 target
LITRES_PER_KWH = 0.31          # reported Eskom burn over generation in three years; see driver_evidence note
# Stats SA, Transport and storage industry 2023 (Report 71-02-01), Table 20: fuel bought by road freight
# transport enterprises, R million, with the twelve months each survey's reference year mostly covers.
ROAD_FREIGHT_FUEL_RAND = {2019: (41640, "2018-07", "2019-06"), 2023: (71468, "2022-07", "2023-06")}
# Vehicle classes of Stone et al. (2018) grouped for the diesel split.
VEHICLE_GROUPS = {
    "Heavy vehicles": ("HCV1", "HCV2", "HCV3", "HCV4", "HCV5", "HCV6", "HCV7", "HCV8", "HCV9"),
    "Light vehicles": ("LCV",),
    "Passenger vehicles": ("Car", "SUV", "Bus", "MBT", "Moto"),
}


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
    # Diesel by use: the study's split of road diesel, power generation and the road freight survey.
    d["study_diesel"], d["study_classes"] = {}, {}
    for group, prefixes in VEHICLE_GROUPS.items():
        members = [r for r in d["stone"].values()
                   if r["fuel"].startswith("diesel") and r["vehicle_type"].startswith(prefixes)]
        d["study_classes"][group] = [r["vehicle_type"] for r in members]
        d["study_diesel"][group] = sum(float(r["vehicles_2010"]) * float(r["km_per_year_fleet_average"])
                                       * float(r["l_per_100km_fleet_average"]) / 100 for r in members) / 1e6
    d["ocgt_gwh"] = {int(r["period"]): float(r["value"]) for r in _read(ts / "ocgt_generation_eskom.csv")
                     if r["series"] == "eskom_and_ipp_ocgt"}
    price = {r["period"]: float(r["value"]) / 100 for r in _read(ts / "fuel_prices_department.csv")
             if r["series"] == "diesel_005_inland_wholesale" and r["value"]}
    d["freight_floor"] = {}
    for year, (rand_million, first, last) in ROAD_FREIGHT_FUEL_RAND.items():
        months = [v for k, v in price.items() if first <= k <= last]
        d["freight_floor"][year] = (rand_million / (sum(months) / len(months)), sum(months) / len(months))
    d["movements"] = {int(r["period"]): float(r["value"]) for r in _read(ts / "air_traffic_acsa_annual.csv")
                      if (r["measure"], r["flight_type"], r["direction"]) == ("aircraft_movements", "total", "total")}
    d["power_fleet"] = _read(ts.parent / "infrastructure" / "power_fleet_diesel.csv")
    d["model_power"] = {}
    for r in _read(Path("workstreams/WS1_data_validation/sector_baselines_2026-10-07.csv")):
        if r["segment"] == "generation":
            d["model_power"][(r["scenario"], int(r["period"]))] = float(r["with_sourced_baselines"]) / 1e6
    d["macro"] = {(r["series"], int(r["period"])): float(r["value"]) / 1e9
                  for r in _read(ts / "macro_statssa.csv") if r["basis"] == "actual" and r["unit"].startswith("rand")}
    return d


# --- sheet writer -------------------------------------------------------------
class Sheet:
    def __init__(self, wb, title: str, heading: str, sub: str, years: list[int] | None = None):
        self.ws = wb.create_sheet(title)
        self.years = years or YEARS
        self.row = 4
        self.ws["A1"] = heading
        self.ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
        self.ws["A2"] = sub
        self.ws["A2"].font = Font(name="Arial", size=10, color=INK)
        for i, label in enumerate(HEAD + self.years + TAIL, start=1):
            cell = self.ws.cell(row=4, column=i, value=label)
            cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
            cell.fill = PatternFill("solid", fgColor=FILL["header"])
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        widths = [34, 14, 17, 15, 44] + [11.5] * len(self.years) + [26, 44, 44]
        for i, width in enumerate(widths, start=1):
            self.ws.column_dimensions[get_column_letter(i)].width = width
        self.ws.freeze_panes = "B5"

    def section(self, title: str) -> None:
        self.row += 2 if self.row > 4 else 1
        for i in range(1, len(HEAD) + len(self.years) + len(TAIL) + 1):
            cell = self.ws.cell(row=self.row, column=i, value=title if i == 1 else None)
            cell.font = Font(name="Arial", size=10, bold=True, color=INK)
            cell.fill = PatternFill("solid", fgColor=FILL["section"])

    def line(self, label, unit, role, definition, values=None, formula=None, kind="observation", scalar=None,
             status="", source="", action="", fmt="#,##0.0") -> int:
        """Write one row. ``values`` is ``{year: number}``; ``formula`` is ``f(year) -> str | None``."""
        self.row += 1
        cells = [label, unit, role, scalar, definition]
        for year in self.years:
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
            if i == 4 or FIRST <= i < FIRST + len(self.years):
                cell.number_format = fmt
        return self.row

    def col(self, year: int) -> str:
        return get_column_letter(FIRST + self.years.index(year))


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
            rows[f"{product}_{code}"] = s.line(
                f"{PROVINCE_NAMES[code]} {product}", ML, "Observation to 2022; estimate after",
                "District-level sales summed to province, 2013-2022. Shows where fuel was sold, not where it was used. "
                "2023-2025 (yellow, italic) are ESTIMATES from section 6, not department data.",
                {y: d["province"].get((product, code, y)) for y in YEARS},
                status="2013-2022 observed; 2023-2025 estimated",
                source=dept_src + ", district workbooks; estimates: see section 6",
                action="Replace the estimates when the department publishes district data after 2023 quarter 1")
        last = s.row
        rows[f"{product}_provinces"] = s.line(
            f"Sum of nine provinces, {product}", ML, "Reporting formula",
            "Sum of the nine rows above. From 2023 it sums estimates, which add to the national figure by construction.",
            formula=lambda y, a=first, b=last: f'=IF(COUNT({col(y)}{a}:{col(y)}{b})<9,"",SUM({col(y)}{a}:{col(y)}{b}))',
            kind="formula")
        rows[f"{product}_dept"] = s.line(
            f"Department national file, {product}", ML, "Source observation",
            "National annual workbook, years with four quarters reported.",
            {y: d["dept"].get((product, y)) for y in YEARS},
            status="2012-2023; nothing published for 2024 or 2025", source=dept_src + ", national workbooks",
            action="2024 national sales: source to be agreed (Nigel)")
        s.line(f"Provinces less national, {product}", ML, "Reporting formula",
               "Difference between the department's two files. 2013 and 2015 traced; 2014 and 2018 for decision. "
               "Zero from 2023 only because the estimates are shares of the national figure.",
               formula=both(rows[f"{product}_provinces"], rows[f"{product}_dept"], "{c}{a}-{c}{b}"), kind="formula",
               action="See integrity_flag_log_2026-10-06.md")
        s.line(f"Why 2025 is blank, {product}", "", "Note",
               f"No national {product} sales figure exists for 2025. The department's national series ends at 2023, and "
               "FIASA's 2025 report repeats its 2024 row for 2025, so that row was dropped. Without a national total "
               "there is nothing to apply the provincial shares to. The estimated 2025 shares are in section 6; the "
               "volumes fill in by formula once a 2025 figure is added to the department or FIASA sales row.",
               kind="comparison", status="2025 not estimated",
               action="Add the 2025 national figure when the department or FIASA publishes it")

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
            rows[f"{product}_{code}_estimate"] = s.line(f"{PROVINCE_NAMES[code]} {product}, estimated", ML, "Proposed estimate",
                   "Estimated share times national sales used (section 4). Blank where no national figure exists.",
                   formula=lambda y, a=share_rows[code], b=rows[f"sales_{product}"]:
                   (f'=IF(COUNT({col(y)}{a},{col(y)}{b})<2,"",{col(y)}{a}/100*{col(y)}{b})' if y >= 2023 else None),
                   kind="estimate", status="Estimate; 2024 also carries the unverified national total",
                   action="Replace when the department publishes district data after 2023 quarter 1")

    s.section("7. Jet fuel: sales, trade, production and aircraft movements")
    jet_dept = s.line("Department national file, jet", ML, "Source observation",
                      "National annual workbook, years with four quarters reported.",
                      {y: d["dept"].get(("jet", y)) for y in YEARS}, status="2012-2023", source=dept_src + ", national workbooks")
    jet_fiasa = s.line("FIASA sales, jet", ML, "Comparison only", "FIASA annual report, latest edition.",
                       {y: d["fiasa_sales"].get(("jet", y)) for y in YEARS}, kind="comparison",
                       status="2024: 1,754 in FIASA's 2024 edition, 1,955 in its 2025 edition",
                       source="Fuels Industry Association of South Africa, annual reports")
    jet_sales = s.line("Sales used, jet", ML, "Reporting formula", "Department where published; otherwise FIASA, unverified.",
                       formula=lambda y: f'=IF(ISNUMBER({col(y)}{jet_dept}),{col(y)}{jet_dept},IF(ISNUMBER({col(y)}{jet_fiasa}),{col(y)}{jet_fiasa},""))',
                       kind="formula")
    jet_in = s.line("Imports, jet", ML, "Source observation", "Complete years reported in litres.",
                    {y: d["sars"].get(("import", "jet", y)) for y in YEARS},
                    status="From 2014; 2019 blank because one month is missing", source=sars_src)
    jet_out = s.line("Exports, jet", ML, "Source observation",
                     "Complete years reported in litres. Whether fuel loaded onto international flights is recorded as an "
                     "export is not established.",
                     {y: d["sars"].get(("export", "jet", y)) for y in YEARS}, status="From 2014", source=sars_src)
    jet_net = s.line("Net imports, jet", ML, "Reporting formula", "Imports less exports.",
                     formula=both(jet_in, jet_out, "{c}{a}-{c}{b}"), kind="formula")
    jet_made = s.line("Production reported, jet", ML, "Source observation", "National production line of the energy balance.",
                      {y: d["balance"].get(("production", "jet", y)) for y in YEARS}, status="2012-2021",
                      source="Department energy balances")
    jet_gap = s.line("Sales less net imports, jet", ML, "Reporting formula",
                     "What production and stock changes must supply. Not a measurement of production.",
                     formula=both(jet_sales, jet_net, "{c}{a}-{c}{b}"), kind="formula")
    s.line("Unexplained after reported production, jet", ML, "Reporting formula",
           "Sales less net imports less reported production.", formula=both(jet_gap, jet_made, "{c}{a}-{c}{b}"), kind="formula")
    moves = s.line("Aircraft movements at ACSA airports", "movements/year", "Source observation",
                   "Arrivals and departures, all flight types, nine ACSA airports. Non-ACSA airports (Lanseria and others) "
                   "are not covered.", {y: d["movements"].get(y) for y in YEARS}, status="2013-2025",
                   source="Airports Company South Africa, traffic statistics", fmt="#,##0")
    s.line("Jet sold per aircraft movement", "litres/movement", "Reporting formula",
           "Sales used divided by movements. "
           f"{d['dept'][('jet', 2023)] * 1e6 / d['movements'][2023]:,.0f} litres in 2023 against "
           f"{d['dept'][('jet', 2019)] * 1e6 / d['movements'][2019]:,.0f} in 2019; the reason for the fall is not "
           "established. Driver proposed for jet: movements times this intensity.",
           formula=both(jet_sales, moves, "{c}{a}*1000000/{c}{b}"), kind="formula", fmt="#,##0",
           action="Cargo, aircraft mix and route length are not separated; no source held gives jet by airport")

    # Bring the estimates into the province rows of section 1, marked as estimates.
    for product in ("petrol", "diesel"):
        for code in PROVINCES:
            observed, estimate = rows[f"{product}_{code}"], rows[f"{product}_{code}_estimate"]
            for year in (2023, 2024, 2025):
                cell = s.ws[f"{col(year)}{observed}"]
                cell.value = f'=IF(ISNUMBER({col(year)}{estimate}),{col(year)}{estimate},"")'
                cell.fill = PatternFill("solid", fgColor=FILL["estimate"])
                cell.font = Font(name="Arial", size=10, italic=True, color=INK)
                cell.number_format = "#,##0.0"
    return rows


def sector_sheet(wb, d: dict) -> dict:
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
        indicative = s.line(f"Indicative diesel at observed activity ({diesel_label.split(',')[0].lower()})", ML, "Proposed estimate",
               "Average 2018-2021 intensity (column D) times the activity measure. An indication for years without a "
               "balance; not an observation and not an accepted input.",
               formula=lambda y, r=act, me=s.row + 1: f'=IF(ISNUMBER({col(y)}{r}),$D${me}*{col(y)}{r},"")',
               kind="estimate", scalar=average, status="Estimate for discussion",
               action="Agree base year, driver and whether intensity is held constant (Nigel)")
        return fuel, indicative

    out = {}
    out["mining"] = block("Mining", "Mining and quarrying diesel, energy balance", eb("mining"), None,
                   "Mining production volume", "index 2019=100", {y: d["index"].get(("mining_volume_total", y)) for y in YEARS},
                   "Statistics South Africa P2041", "million L per index point",
                   "Includes unregistered haul trucks and mines' road vehicles; the balance does not separate them.")
    mining = out["mining"][0]
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

    out["manufacturing"] = block("Manufacturing and non-specified industry",
                                 "Manufacturing and other industry diesel, by difference", None, rest,
          "Manufacturing production volume", "index 2019=100",
          {y: d["index"].get(("manufacturing_volume_total", y)) for y in YEARS},
          "Statistics South Africa P3041.2", "million L per index point",
          "Industry less mining less construction. Small (0.1-0.3 bn litres), so it moves with reclassification in "
          "the balance more than with output.")
    out["agriculture"] = block("Agriculture", "Agriculture and forestry diesel, energy balance", eb("agriculture"), None,
          "Agriculture, forestry and fishing real value added", "bn 2015 rand",
          {y: d["macro"].get(("agriculture_forestry_and_fishing", y)) for y in YEARS},
          "Statistics South Africa P0441", "million L per bn rand",
          "2016 and 2017 are about double the other years in the balance and look like reclassification.")
    return out


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


def diesel_by_use_sheet(wb, d: dict, history_rows: dict, sector_rows: dict) -> None:
    s = Sheet(wb, "Diesel by use", "Diesel by use: the six branches drawn at the 7 October check-in",
              "Mining, manufacturing, agriculture and power are taken from sources; road diesel is what remains of "
              "recorded sales and is split with the shares of a published vehicle study (approach A). Million litres a year.")
    quote = "'Sector history'!"

    def sector(key):
        fuel, indicative = sector_rows[key]
        return lambda y: (f'=IF(ISNUMBER({quote}{col(y)}{fuel}),{quote}{col(y)}{fuel},'
                          f'IF(ISNUMBER({quote}{col(y)}{indicative}),{quote}{col(y)}{indicative},""))')

    s.section("1. Sales and the uses taken from sources")
    sales = s.line("Diesel sales used", ML, "Reporting formula",
                   "From History: department national file to 2023, FIASA (unverified) for 2024.",
                   formula=lambda y: f'=IF(ISNUMBER(History!{col(y)}{history_rows["sales_diesel"]}),History!{col(y)}{history_rows["sales_diesel"]},"")',
                   kind="formula", status="2012-2024")
    mining = s.line("Mining", ML, "Observation, then estimate",
                    "Energy balance to 2021; from 2022 the indicative figure on Sector history. Driver: mining production index.",
                    formula=sector("mining"), kind="formula", status="Observed to 2021; estimated after",
                    source="Department energy balances; Stats SA P2041")
    manufacturing = s.line("Manufacturing and other industry", ML, "Observation, then estimate",
                           "Energy balance industry less mining and construction to 2021; indicative after. "
                           "Driver: manufacturing production index.",
                           formula=sector("manufacturing"), kind="formula", status="Zero before 2016 in the balance",
                           source="Department energy balances; Stats SA P3041.2")
    agriculture = s.line("Agriculture", ML, "Observation, then estimate",
                         "Energy balance to 2021; indicative after. Driver: agricultural real value added.",
                         formula=sector("agriculture"), kind="formula", status="Observed to 2021; estimated after",
                         source="Department energy balances; Stats SA P0441")
    gwh = s.line("Diesel power generation, Eskom and independent plants", "GWh", "Source observation",
                 "Year to 31 March of the following year, shown under the calendar year it mostly covers.",
                 {y - 1: v for y, v in d["ocgt_gwh"].items() if y - 1 in YEARS}, status="2022-2025", source="Eskom",
                 fmt="#,##0")
    balance_power = s.line("Power generation diesel, energy balance", ML, "Source observation",
                           "Electricity plants line of the energy balance.",
                           {y: d["balance"].get(("electricity_plants", "diesel", y)) for y in YEARS},
                           status="2012-2021; near zero from 2017", source="Department energy balances")
    power = s.line("Power", ML, "Observation, then estimate",
                   "Energy balance to 2021; from 2022 generation times litres per kWh (column D). Driver: turbine output.",
                   formula=lambda y, me=s.row + 1: (f'=IF(ISNUMBER({col(y)}{gwh}),{col(y)}{gwh}*$D${me},'
                                                    f'IF(ISNUMBER({col(y)}{balance_power}),{col(y)}{balance_power},""))'),
                   kind="formula", scalar=LITRES_PER_KWH, fmt="#,##0.00",
                   status="Estimated from 2022 at 0.31 litres per kWh",
                   source="Eskom; parliamentary replies on diesel burn",
                   action="The 0.31 factor is a proposal awaiting review")

    s.section("2. Road diesel, by difference")
    road = s.line("Road vehicles and uses not listed above", ML, "Reporting formula",
                  "Sales less mining, manufacturing, agriculture and power. Includes rail, construction plant, private "
                  "generators and ships' diesel, which no source separates.",
                  formula=lambda y: (f'=IF(COUNT({col(y)}{sales},{col(y)}{mining},{col(y)}{agriculture})<3,"",{col(y)}{sales}'
                                     f'-{col(y)}{mining}-N({col(y)}{manufacturing})-{col(y)}{agriculture}-N({col(y)}{power}))'),
                  kind="formula", action="The balance counts mining and farm diesel by buyer, so some of it is burned on public roads")

    s.section("3. Road diesel split by vehicle group (approach A: the study's shares held)")
    total = sum(d["study_diesel"].values())
    split = {}
    drivers = {"Heavy vehicles": "Driver: freight activity, road-to-rail shift, electric share of new trucks.",
               "Light vehicles": "Driver: fleet and distance, electric share of new sales.",
               "Passenger vehicles": "Driver: fleet and distance, electric share of new sales."}
    for group in VEHICLE_GROUPS:
        split[group] = s.line(group, ML, "Proposed estimate",
                              f"Road diesel times the group's share in the study (column D, %). {drivers[group]}",
                              formula=lambda y, me=s.row + 1: f'=IF(ISNUMBER({col(y)}{road}),{col(y)}{road}*$D${me}/100,"")',
                              kind="estimate", scalar=d["study_diesel"][group] / total * 100,
                              status="Estimate; shares are for the 2010 fleet",
                              source="Stone et al. (2018), vehicles x distance x fuel use by class",
                              action="Diesel vehicles have doubled since 2010 while trucks grew about a quarter, so "
                                     "today's heavy share is probably lower")

    s.section("3b. Heavy vehicle diesel against road freight carried")
    tonnes = s.line("Road freight payload", "million tonnes/year", "Source observation",
                    "Tonnes carried by road, calendar years. Tonnes, not tonne-kilometres.",
                    {y: d["index"].get(("freight_payload_road", y), 0) * 12 / 1000 or None for y in YEARS},
                    status="2012-2025", source="Statistics South Africa P7162")
    s.line("Heavy vehicle diesel per tonne of road freight", "litres/tonne", "Reporting formula",
           "Heavy vehicle diesel divided by road freight payload. This is the link from freight activity to litres: "
           "road freight grows or shifts to rail in tonnes, and diesel follows at this intensity.",
           formula=both(split["Heavy vehicles"], tonnes, "{c}{a}/{c}{b}"), kind="formula", fmt="0.00",
           action="A tonne-kilometre series would be better; only 2013 is published (221 bn)")

    s.section("4. Checks")
    s.line("Sum of the six branches", ML, "Reporting formula", "Should equal diesel sales used.",
           formula=lambda y: (f'=IF(ISNUMBER({col(y)}{road}),{col(y)}{mining}+N({col(y)}{manufacturing})+{col(y)}{agriculture}'
                              f'+N({col(y)}{power})+' + "+".join(f"{col(y)}{r}" for r in split.values()) + ',"")'),
           kind="formula")
    floor = s.line("Fuel bought by road freight businesses", ML, "Source observation, converted",
                   "Stats SA rand figure divided by the average inland wholesale diesel price over the survey year "
                   f"(R{d['freight_floor'][2019][1]:.2f} and R{d['freight_floor'][2023][1]:.2f} a litre). Hire-and-reward "
                   "operators only; may include some petrol and lubricants.",
                   {y: v[0] for y, v in d["freight_floor"].items()}, kind="comparison", status="2019 and 2023 only",
                   source="Stats SA, Transport and storage industry 2023 (Report 71-02-01), Table 20")
    s.line("Heavy vehicles less the road freight figure", ML, "Reporting formula",
           "Should be positive: the survey leaves out trucks run by firms for their own goods.",
           formula=both(split["Heavy vehicles"], floor, "{c}{a}-{c}{b}"), kind="formula")
    s.line("Land freight share of diesel in a second study", "% of diesel demand", "Comparison only",
           "Merven, Hartley and Ahjum (2019): land freight took 60.5% of domestic diesel demand in 2012. Same research "
           "group as the vehicle study.", scalar=60.5, kind="comparison", fmt="0.0",
           source="SA-TIED Working Paper 60, p.10")

    s.section("5. Which classes of the study fall in each group")
    for group, prefixes in VEHICLE_GROUPS.items():
        every = sorted(r["vehicle_type"] for r in d["stone"].values() if r["vehicle_type"].startswith(prefixes))
        petrol_only = [c for c in every if c not in d["study_classes"][group]]
        s.line(f"{group}: classes", "", "Note",
               "Diesel classes counted: " + ", ".join(d["study_classes"][group]) + ". "
               + ("Other classes in the group, not diesel: " + ", ".join(petrol_only) + "." if petrol_only else ""),
               scalar=d["study_diesel"][group], kind="comparison", fmt="#,##0",
               status="Column D is the group's diesel in the study, million litres, 2010 fleet",
               source="assumptions/2026/reference/vehicle_parameters_stone2018.csv")
    s.line("Reading the class names", "", "Note",
           "Car and SUV are private passenger vehicles; Bus is buses; MBT is minibus taxis; Moto is motorcycles; LCV is "
           "light commercial vehicles (bakkies and vans); HCV1 to HCV9 are trucks in nine weight classes, lightest to "
           "heaviest.", kind="comparison")


def _table(wb, title: str, heading: str, sub_heading: str, header: list[str], widths: list[float], body: list[list]):
    ws = wb.create_sheet(title)
    ws["A1"] = heading
    ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
    ws["A2"] = sub_heading
    ws["A2"].font = Font(name="Arial", size=10, color=INK)
    for i, label in enumerate(header, start=1):
        cell = ws.cell(row=4, column=i, value=label)
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
        cell.fill = PatternFill("solid", fgColor=FILL["header"])
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        ws.column_dimensions[get_column_letter(i)].width = widths[i - 1]
    for n, values in enumerate(body, start=5):
        for i, value in enumerate(values, start=1):
            cell = ws.cell(row=n, column=i, value=value)
            cell.font = Font(name="Arial", size=10, color=INK)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "B5"
    return ws


GAP_STATUS = [
    ("G01", "National fuel balance", "Narrowed",
     "Balance rebuilt on customs trade for 2014-2025; Road Accident Fund levy found as an independent count.",
     "2024 sales source; no 2025 sales figure; production by product after 2021; stocks.", "History, sections 2-5"),
    ("G02", "Fleet and new sales", "Narrowed",
     "Registered vehicles by class 2021-2025, new sales 2017-2025 and apparent retirements lined up against the model.",
     "Stock by age and by fuel within each class is in no source held.", "Vehicle history"),
    ("G03", "Passenger electrification", "Narrowed",
     "Battery electric, plug-in and conventional hybrid sales and shares, 2019-2025.",
     "Passenger-only denominators; electric vehicles in the fleet after 2023; fuel saved by hybrids.", "Vehicle history, section 4"),
    ("G04", "Road freight activity", "Narrowed",
     "Heavy vehicle diesel is estimated for every year and set against road freight tonnes, giving litres per tonne. "
     "Stats SA fuel purchases by road freight firms give a floor of about 2.9 bn litres (2019) and 3.2 bn (2023).",
     "An annual tonne-kilometre series (only 2013 is published); distance, payload and empty running; light "
     "commercial freight scope.", "Diesel by use, sections 3, 3b and 4"),
    ("G05", "Freight electrification", "Proposed",
     "No South African data on electric trucks exists, so the gap cannot be closed with observation. Benchmarks for "
     "2025: Brazil 0.4% of new truck sales, India well under 1%, Europe 3%, world 9%, China 25%. Low / medium / high "
     "proposed from Brazil and Europe; even the high case electrifies about 2.5% of trucks by 2035.",
     "South African sales of electric trucks by size; duty cycles that could switch first; charging at depots.",
     "HML response"),
    ("G06", "Manufacturing", "Narrowed",
     "Manufacturing and other industry diesel by difference, 2016-2021 (0.16-0.23 bn litres), with litres per index point.",
     "Sub-sector detail; the balance has no manufacturing lines before 2016.", "Sector history"),
    ("G07", "Mining and construction", "Narrowed",
     "Mining diesel 2012-2021 with litres per index point (11-17 million); indicative 2022-2025.",
     "Observed fuel after 2021; site and commodity split; on-road boundary.", "Sector history"),
    ("G08", "Agriculture", "Narrowed",
     "Agriculture diesel 2012-2021 with litres per rand of value added; indicative 2022-2025. Rebated diesel across all "
     "rebate sectors is 1.46 bn litres (year to March 2025).",
     "A fuel baseline after 2021; crop and irrigation activity.", "Sector history"),
    ("G09", "Generation", "Narrowed",
     "Generation to the year ending March 2026; 0.31 litres per kWh in three reported years. The model's 2024 figure "
     "(3.58 bn litres) is at least 2 bn above reported burn.",
     "Matched fuel burn by calendar year; private backup generation has no measured volume.", "Diesel by use, section 1"),
    ("G10", "Aviation", "Narrowed",
     "Jet sales, trade, production and aircraft movements lined up; jet sold per movement computed.",
     "Cargo, aircraft and route mix; airports outside ACSA; jet by airport.", "History, section 7"),
    ("G11", "Provincial demand", "Narrowed",
     "2013-2022 observed; 2023 and 2024 estimated with the best of six methods back-tested.",
     "District data after 2023 quarter 1, which the department has not published; 2025 national total.", "History, sections 1 and 6"),
    ("G12", "Marine and other coverage", "Open", "Nothing new. The model's marine placeholder equals the 2007 balance figure.",
     "Everything listed.", ""),
    ("G13", "Ranges and annual forecast paths", "Proposed",
     "Baseline, rationale and source for all 20 levers; 39 of 120 values with a proposed replacement; nine levers added.",
     "Agreement on the reference case and annual paths.", "HML response"),
]


def gap_status_sheet(wb) -> None:
    _table(wb, "Gap status", "Status against the 13 data gaps on the Data gaps sheet, 8 October 2026",
           "The Data gaps sheet is unchanged. Statuses are the analyst's reading; closure is for the owner named there.",
           ["ID", "Demand component", "Status", "What has been added", "What is still missing", "Where to look"],
           [7, 28, 12, 70, 60, 28], [list(row) for row in GAP_STATUS])


def lever_response_sheet(wb) -> None:
    rows = _read(LEVERS)
    levers = list(dict.fromkeys((r["fuel"], r["lever"]) for r in rows))
    body = []
    for fuel, lever in levers:
        mine = {(r["period"], r["case"]): r for r in rows if (r["fuel"], r["lever"]) == (fuel, lever)}
        first = next(iter(mine.values()))

        def trio(year, column):
            return " / ".join(mine[(year, case)][column] or "-" for case in ("low", "medium", "high"))

        state = {"added"} if first["changed"] == "added" else {r["changed"] for r in mine.values()}
        body.append([fuel, lever, first["unit"], first["baseline"], first["baseline_basis"],
                     trio("2030", "proposed_by_nigel"), trio("2030", "analyst_value"),
                     trio("2035", "proposed_by_nigel"), trio("2035", "analyst_value"),
                     "added lever" if state == {"added"} else "replacement proposed" if "yes" in state else "no change",
                     first["evidence"]])
    _table(wb, "HML response", "Analyst response to the proposed low / medium / high inputs",
           "The HML sheet is unchanged. Values are low / medium / high. Replacements and added levers are proposals for "
           "review; source: fuel_lever_response_2026-10-07.csv.",
           ["Fuel", "Lever", "Unit", "Baseline", "Baseline basis", "2030 proposed (Nigel)", "2030 analyst",
            "2035 proposed (Nigel)", "2035 analyst", "Result", "Evidence and rationale"],
           [11, 30, 22, 13, 44, 22, 22, 22, 22, 20, 110], body)


def power_fleet_sheet(wb, d: dict) -> None:
    s = Sheet(wb, "Power fleet", "Diesel for power: the fleet, the coal retirements and what each could burn",
              "A block by station and year, as asked on 7 October. Capacities are from Eskom's fact sheet; retirement "
              "dates from press reports; everything about repowering with gas is a scenario. Yellow rows are assumptions.",
              years=FUTURE)
    c = s.col
    fleet = d["power_fleet"]
    litres = s.row + 2                       # the two assumption rows sit first so that every formula can point at them

    s.section("Assumptions used below")
    s.line("Diesel burned per kWh generated", "litres/kWh", "Assumption", "Reported Eskom burn over generation in three "
           "years. A proposal awaiting review.", scalar=LITRES_PER_KWH, kind="estimate", fmt="0.00",
           source="Parliamentary replies on Eskom diesel burn; Eskom generation")
    backup = s.line("Share of output on diesel once gas is the main fuel", "%", "Assumption",
                    "Applies to Ankerlig and Gourikwa after the gas switch and to any repowered site. NO SOURCE: Eskom's "
                    "tender says only that gas will be 'supplemented by diesel as and when it's required'.",
                    scalar=10, kind="estimate", fmt="0", action="Agree a value (Nigel, Henry)")
    gas_lf = s.line("Load factor of gas plants at repowered sites", "%", "Assumption",
                    "NO SOURCE. Eskom describes the gas it needs as dispatchable baseload, so well above a peaker.",
                    scalar=40, kind="estimate", fmt="0", action="Agree a value (Nigel, Henry)")

    s.section("1. Stations that burn diesel today")
    diesel_rows = {}
    for r in fleet:
        if r["group"] == "diesel_station":
            diesel_rows[r["station"]] = s.line(
                f'{r["station"]} ({r["owner"]})', "MW", "Source observation", f'{r["note"]}. {r["event"]}.',
                {y: float(r["capacity_mw"]) for y in FUTURE}, status="Installed capacity, held flat", source=r["source"], fmt="#,##0")
    first, last = min(diesel_rows.values()), max(diesel_rows.values())
    total_mw = s.line("Diesel stations, total", "MW", "Reporting formula", "Sum of the four stations.",
                      formula=lambda y: f"=SUM({c(y)}{first}:{c(y)}{last})", kind="formula", fmt="#,##0")
    kerosene = []
    for r in fleet:
        if r["group"] == "kerosene_station":
            kerosene.append(s.line(f'{r["station"]} ({r["owner"]})', "MW", "Not counted", f'{r["note"]}.',
                                   {y: float(r["capacity_mw"]) for y in FUTURE}, kind="comparison", source=r["source"], fmt="#,##0"))

    s.section("2. What the peaking stations have generated and burned")
    gwh = s.line("Generation, Eskom and independent peaking stations", "GWh", "Source observation",
                 "Year to 31 March of the following year, shown under the calendar year it mostly covers. Includes the "
                 "two kerosene stations.", {y - 1: v for y, v in d["ocgt_gwh"].items() if y - 1 in FUTURE},
                 status="2022-2025", source="Eskom", fmt="#,##0")
    s.line("Observed load factor", "%", "Reporting formula",
           "Generation divided by what all six stations would produce running all year.",
           formula=lambda y: (f'=IF(ISNUMBER({c(y)}{gwh}),{c(y)}{gwh}/(({c(y)}{total_mw}+{c(y)}{kerosene[0]}+{c(y)}{kerosene[1]})'
                              f'*8.76)*100,"")'), kind="formula", fmt="0.0")
    burned = s.line("Diesel burned, estimated", ML, "Reporting formula", "Generation times litres per kWh.",
                    formula=lambda y: f'=IF(ISNUMBER({c(y)}{gwh}),{c(y)}{gwh}*$D${litres},"")', kind="formula",
                    status="Estimate; slightly high because some output is kerosene")
    for scenario, label in (("high_demand", "high demand"), ("low_demand", "low demand")):
        s.line(f"Model today, {label} scenario", ML, "Comparison only",
               "The engine's power generation diesel on manish-branch. It runs six stations, two of them placeholders "
               "of 1,000 and 2,000 MW, at 55-70% load factor.",
               {y: v for (sc, y), v in d["model_power"].items() if sc == scenario}, kind="comparison",
               status="2024, 2030 and 2035 shown", source="sector_baselines_2026-10-07.csv")

    s.section("3. What today's diesel stations could burn")
    share = s.line("Share of Ankerlig and Gourikwa output on diesel", "%", "Assumption",
                   "100% until Eskom's stated gas switch (December 2027), then the backup share above. Set every year to "
                   "100 to see the case where the switch does not happen.",
                   formula=lambda y: "=100" if y < GAS_SWITCH_YEAR else f"=$D${backup}", kind="estimate", fmt="0",
                   status="Whether the switch is on schedule is not established",
                   source="Eskom gas supply tender, as reported by News24, 12 June 2023")
    observed_lf = {y: d["ocgt_gwh"][y] / (3431 * 8.76) * 100 for y in (2024, 2025, 2026)}
    cases = (("low", observed_lf[2026], "year to March 2026"), ("medium", observed_lf[2025], "year to March 2025"),
             ("high", observed_lf[2024], "year to March 2024, the peak of load-shedding"))
    today = {}
    for name, factor, basis in cases:
        today[name] = s.line(
            f"Diesel at a {name} load factor", ML, "Proposed estimate",
            f"Load factor in column D (%): the fleet's observed figure for the {basis}. Avon and Dedisa wholly on diesel; "
            "Ankerlig and Gourikwa at the share above.",
            formula=lambda y, me=s.row + 1: (
                f'=({c(y)}{diesel_rows["Avon"]}+{c(y)}{diesel_rows["Dedisa"]}+({c(y)}{diesel_rows["Ankerlig"]}'
                f'+{c(y)}{diesel_rows["Gourikwa"]})*{c(y)}{share}/100)*8.76*$D${me}/100*$D${litres}'),
            kind="estimate", scalar=factor, status="Estimate", source="Eskom generation; Eskom fact sheet GX 0001")
    ceiling_today = s.line("Ceiling: all four stations on diesel all year", ML, "Reporting formula",
                           "Total capacity times 8,760 hours times litres per kWh. A physical limit, not a forecast.",
                           formula=lambda y: f"={c(y)}{total_mw}*8.76*$D${litres}", kind="formula")

    s.section("4. Coal stations being retired: capacity still operating")
    coal = []
    for r in fleet:
        if r["group"] == "coal_retiring":
            last_year = int(r["last_full_year"])
            coal.append(s.line(
                r["station"], "MW", "Evidence" if r["basis"] == "evidence" else "To confirm", f'{r["event"]}.',
                {y: float(r["capacity_mw"]) if y <= last_year else 0 for y in FUTURE},
                kind="observation" if r["basis"] == "evidence" else "estimate",
                status="Capacity shown to the last full year of operation", source=r["source"], fmt="#,##0"))
    operating = s.line("Coal capacity operating, these eight stations", "MW", "Reporting formula", "Sum of the rows above.",
                       formula=lambda y: f"=SUM({c(y)}{coal[0]}:{c(y)}{coal[-1]})", kind="formula", fmt="#,##0")
    s.line("Coal capacity retired since 2022", "MW", "Reporting formula", "2022 total less this year's.",
           formula=lambda y: f"={c(2022)}{operating}-{c(y)}{operating}", kind="formula", fmt="#,##0",
           action="Eskom was to decide by end September 2026 between shutdown, repowering and repurposing; outcome not found")

    s.section("5. If retired sites are repowered with gas turbines that can burn diesel (scenario)")
    gas = {}
    for name, megawatts, basis in (("low", 0, "none of the retired sites gets a gas plant"),
                                   ("medium", IRP_GAS_MW_2030 / 2, "half of the IRP 2025 gas requirement is built at these sites"),
                                   ("high", IRP_GAS_MW_2030, "all 6 GW of the IRP 2025 gas requirement is built at these sites")):
        gas[name] = s.line(f"Gas capacity at repowered sites, {name}", "MW", "Scenario",
                           f"From 2030: {basis}. Which sites, if any, is not decided.",
                           {y: megawatts if y >= 2030 else 0 for y in FUTURE}, kind="estimate", fmt="#,##0",
                           status="Scenario, not a plan", source="IRP 2025 gas requirement, as reported by TechCentral, 22 April 2026")
    repower = {}
    for name in ("low", "medium", "high"):
        repower[name] = s.line(f"Diesel as backup fuel at repowered sites, {name}", ML, "Scenario",
                               "Gas capacity times load factor times the share of output on diesel times litres per kWh.",
                               formula=lambda y, r=gas[name]: f"={c(y)}{r}*8.76*$D${gas_lf}/100*$D${backup}/100*$D${litres}",
                               kind="estimate", status="Scenario")
    ceiling_gas = s.line("Ceiling: high case with no gas all year", ML, "Reporting formula",
                         "High-case gas capacity at its load factor, wholly on diesel. What the sites could draw if gas "
                         "supply failed.", formula=lambda y: f"={c(y)}{gas['high']}*8.76*$D${gas_lf}/100*$D${litres}", kind="formula")

    s.section("6. Diesel for power, all sites")
    for name in ("low", "medium", "high"):
        s.line(f"Total, {name}", ML, "Proposed estimate", "Today's stations plus repowered sites, same case.",
               formula=lambda y, a=today[name], b=repower[name]: f"={c(y)}{a}+{c(y)}{b}", kind="estimate")
    s.line("Ceiling, all sites", ML, "Reporting formula", "The two ceilings added: how much the fleet could consume.",
           formula=lambda y: f"={c(y)}{ceiling_today}+{c(y)}{ceiling_gas}", kind="formula")
    s.line("For reference: diesel burned, estimated", ML, "Reporting formula", "From section 2.",
           formula=lambda y: f'=IF(ISNUMBER({c(y)}{burned}),{c(y)}{burned},"")', kind="formula")

    s.section("7. Not established")
    for label, why in (
            ("Outcome of Eskom's September 2026 decision", "Whether Camden, Grootvlei, Hendrina, Arnot and Kriel shut, are repowered or run on."),
            ("Which sites get gas plants, and how large", "Section 5 uses the national gas requirement as a stand-in."),
            ("Whether Ankerlig and Gourikwa switch to gas on time", "Eskom's stated target was December 2027."),
            ("Share of output on diesel when gas is the main fuel", "No source; 10% is a placeholder."),
            ("Private generators at firms and homes", "Not in this block; no measured volume exists."),
            ("Komati's shutdown date, and the 2034 date for Duvha and Matla", "Marked 'to confirm' in the input file.")):
        s.line(label, "", "Gap", why, kind="estimate", status="Open")


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
        "air_traffic_acsa_annual": "History section 7: aircraft movements",
        "fuel_sales_department_by_province_quarterly": "History section 6: quarter 1 2023 provincial shares",
        "gdp_by_province_statssa": "History section 6: provincial GDP used to move the 2024 shares",
        "ocgt_generation_eskom": "Diesel by use and Power fleet: power generation",
        "power_fleet_diesel": "Power fleet: stations, capacities and retirement dates",
        "ocgt_diesel_burn_reported": "Diesel by use: the 0.31 litres per kWh factor",
        "fuel_prices_department": "Diesel by use: price used to convert road freight fuel spending to litres",
        "vehicle_parameters_stone2018": "Diesel by use and Vehicle history: vehicle classes, distance and fuel use",
        "vehicle_population_natis": "Vehicle history: registered vehicles by class",
        "new_vehicle_market_naamsa": "Vehicle history: new sales by segment",
        "nev_sales_naamsa": "Vehicle history: electrified new sales",
        "vehicle_population_by_fuel_dot2023": "Vehicle history: fuel split of the registered fleet",
    }
    documents = [
        ["Diesel by use: fuel bought by road freight businesses", "Statistics South Africa",
         "https://www.statssa.gov.za/?page_id=1854&PPN=Report-71-02-01", "Report-71-02-012023.pdf, Table 20 (p.33)",
         "on manish-branch (external/data/raw/statssa/statssa-transport-and-storage-industry-2023.pdf)",
         "typed into build_demand_baseline_workbook.py (ROAD_FREIGHT_FUEL_RAND)", "none", "2019, 2023",
         "Hire-and-reward operators only; 2023 preliminary"],
        ["Diesel by use: land freight share of diesel", "Merven, Hartley and Ahjum (2019), SA-TIED Working Paper 60",
         "https://sa-tied.wider.unu.edu/sites/default/files/pdf/SATIED_WP60_Merven_Hartley_Ahjum_April_2019.pdf",
         "p.10", "on manish-branch (external/data/raw/literature/)", "quoted on the sheet", "none", "2012",
         "Modelled; same research group as the vehicle study"],
        ["Vehicle history and Diesel by use: the model's settings", "AIA (Reatile workbook, March 2025)", "",
         "assumptions/2026/vehicles.yaml", "in the repository", "assumptions/2026/vehicles.yaml", "none", "",
         "Placeholders without a published source"],
        ["HML response", "AIA (analyst), from the sources named in each row", "",
         "workstreams/WS2_model_development/fuel_lever_response_2026-10-07.csv", "in the repository",
         "same file", "python -m lfm.scripts.build_fuel_lever_response --vintage 2026", "2030, 2035", "Proposals"],
    ]
    trace = {r["dataset"]: r for r in _read(TRACE)}
    ws = wb.create_sheet("History sources")
    ws["A1"] = "Sources for the sheets added to the workshop workbook"
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
    for n, values in enumerate(documents, start=5 + len(wanted)):
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
    changes.append("Sheets added: History, Sector history, Diesel by use, Power fleet, Vehicle history, HML response, Gap status, "
                   "Checks, History sources. No other cell changed.")

    history_rows = history_sheet(wb, d)
    sector_rows = sector_sheet(wb, d)
    diesel_by_use_sheet(wb, d, history_rows, sector_rows)
    power_fleet_sheet(wb, d)
    vehicle_sheet(wb, d, history_rows)
    lever_response_sheet(wb)
    gap_status_sheet(wb)
    differs = checks_sheet(wb, d, changes)
    sources_sheet(wb)
    wb.save(args.out)
    print(f"wrote {args.out}; evidence values that differ from the inputs: {differs}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
