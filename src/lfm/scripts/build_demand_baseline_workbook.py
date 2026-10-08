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
    d["jodi_output"] = {(r["product"], int(r["period"])): float(r["value"]) / 1e6
                        for r in _read(ts / "oil_balance_jodi.csv")
                        if r["flow"] == "refinery_output" and int(r["months_reported"]) == 12}
    d["jodi_demand"] = {(r["product"], int(r["period"])): float(r["value"]) / 1e6
                        for r in _read(ts / "oil_balance_jodi.csv")
                        if r["flow"] == "demand" and int(r["months_reported"]) == 12}
    eskom = _read(ts / "eskom_fuel_eaf_review_2026_10_07.csv")
    d["eskom_fuel"] = {int(r["period"]): float(r["value"]) for r in eskom if r["series"] == "eskom_ocgt_diesel_and_kerosene"}
    turbines = _read(ts / "ocgt_generation_eskom.csv")
    d["eskom_gwh"] = {int(r["period"]): float(r["value"]) for r in turbines if r["series"] == "eskom_ocgt"}
    d["ipp_gwh"] = {int(r["period"]): float(r["value"]) for r in turbines if r["series"] == "ipp_ocgt"}
    register = _read(ts / "vehicle_population_natis.csv")
    d["natis_latest"] = max(r["period"] for r in register)
    d["natis_by_province"] = {(r["province"], r["vehicle_class"]): float(r["value"]) for r in register if r["period"] == d["natis_latest"]}
    d["zone_differentials"] = {(r["zone"], r["product"], r["effective"][:4]): float(r["value"])
                               for r in _read(ref / "zone_differentials_department.csv")}
    d["zone_districts"] = [(r["zone"], r["magisterial_district"], r["province"]) for r in _read(ref / "zone_districts_department.csv")]
    d["imports_by_office"] = {}
    for r in _read(ts / "fuel_trade_sars_by_office.csv"):
        # months_reported counts the months an office cleared fuel, so it is not a test of a complete year here
        if r["flow"] == "import" and r["product"] in ("petrol", "diesel") and r["unit"] == "litres" and int(r["period"]) in ENTRY_YEARS:
            key = (int(r["period"]), r["district_office"], r["product"])
            d["imports_by_office"][key] = d["imports_by_office"].get(key, 0.0) + float(r["value"]) / 1e9
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
# Rows that are worked out in the workbook have no publisher; they still say where the number comes from.
FIASA_2024_EDITION = {"petrol": 8763, "diesel": 11807}  # 2024 sales as printed in FIASA's 2024 report, p.32

DEFAULT_SOURCE = {
    "Reporting formula": "Calculated in this workbook from the rows named in the definition",
    "Proposed estimate": "Analyst estimate, calculated in this workbook; method in the definition",
    "Scenario": "Analyst scenario setting; no published source",
    "Assumption": "Analyst assumption; no published source",
}


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
        cells += [status, source or DEFAULT_SOURCE.get(role, "Described in the definition"), action]
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
                "2023 (yellow, italic) holds ESTIMATES from section 6, not department data; 2024 and 2025 are blank.",
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
            action="Add 2024 and 2025 when the department publishes them")
        s.line(f"Provinces less national, {product}", ML, "Reporting formula",
               "Difference between the department's two files. The provincial figures are used as published. 2014: the "
               "district file's third quarter is higher than the national file. 2018: the first-quarter district sheet "
               "lists six fewer districts, so the provincial sum is about 2% low. "
               "Zero from 2023 only because the estimates are shares of the national figure.",
               formula=both(rows[f"{product}_provinces"], rows[f"{product}_dept"], "{c}{a}-{c}{b}"), kind="formula",
               action="See integrity_flag_log_2026-10-06.md")
        fiasa_2024, jodi_2024 = d["fiasa_sales"].get((product, 2024)), d["jodi_demand"].get((product, 2024))
        gaps = [d["jodi_demand"][(product, y)] - d["dept"][(product, y)] for y in (2022, 2023)]
        s.line(f"Why 2024 and 2025 are blank, {product}", "", "Note",
               f"The department has published no {product} sales after 2023, by province or nationally, so there is no "
               f"total to split. FIASA and JODI each have a national 2024 figure ({fiasa_2024:,.0f} and {jodi_2024:,.0f} "
               "million litres) but neither is reliable, so FIASA is not used and JODI is not used. "
               f"FIASA: its 2024 and 2025 annual reports give different figures for 2024 ({FIASA_2024_EDITION[product]:,} in "
               "the 2024 edition), its 2025 row is a copy of its 2024 row, and it attributes its sales to the department, "
               "which has published none. JODI: its demand was "
               f"{min(gaps):,.0f} and {max(gaps):,.0f} million litres above department sales in 2022 and 2023, so it is not "
               "on the same basis, and every entry carries JODI's lowest reliability code. Neither has provincial data, "
               "and neither has a 2025 figure.",
               kind="comparison", status="2024 and 2025 blank",
               source="FIASA annual reports 2024 (p.32) and 2025 (p.47); JODI oil database; department sales volumes page",
               action="Fill in when the department publishes")

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
            "National production line of the department's energy balance for that year.",
            {y: d["balance"].get(("production", product, y)) for y in YEARS},
            status="2012-2021; no balance published after 2021",
            source="Department of Mineral and Petroleum Resources, <year>-Commodity-Flow-and-Energy-Balance.xlsx "
                   "(2021: .xlsm); dmpr.gov.za/Portals/0/Energy_Website/files/media/Energy_Balances.html",
            action="2022 onward: add when the department publishes a balance")
        agreement = ("within 4% of the energy balance in 2017-2021" if product == "diesel" else
                     "12-24% above the energy balance in 2017-2021")
        s.line(f"Refinery output reported to JODI, {product}", ML, "Comparison only",
               "South Africa's monthly submissions to the JODI oil database, added over the calendar year. Not used.",
               {y: d["jodi_output"].get((product, y)) for y in YEARS}, kind="comparison",
               status=f"Not used. 2017-2024; {agreement}",
               source="JODI oil database, secondary products, annual files; jodidata.org; lowest assessment code")
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
                       status="Not used. 2024 differs between FIASA's 2024 and 2025 editions",
                       source="Fuels Industry Association of South Africa, annual reports")
        del fiasa  # shown for comparison; never selected
        sales = s.line(f"Sales used, {product}", ML, "Reporting formula",
                       "The sum of the nine provinces (section 1) where there is one; otherwise the department's "
                       "national file. 2023 is the national total, which the provincial estimates add up to.",
                       formula=lambda y, a=rows[f"{product}_provinces"], b=rows[f"{product}_dept"]:
                       f'=IF(ISNUMBER({col(y)}{a}),{col(y)}{a},IF(ISNUMBER({col(y)}{b}),{col(y)}{b},""))', kind="formula",
                       status="Provinces 2013-2023 (2023 estimated); national file 2012; blank for 2024 and 2025",
                       source="Department district sales summed to province; national file for 2012 and the 2023 total")
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
               status="To 2021, the last energy balance. Negative means reported supply is above recorded sales",
               action="No stock series is published")

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
                   "Estimated share times the department's national total (section 1). Blank where no national figure exists.",
                   formula=lambda y, a=share_rows[code], b=rows[f"{product}_dept"]:
                   (f'=IF(COUNT({col(y)}{a},{col(y)}{b})<2,"",{col(y)}{a}/100*{col(y)}{b})' if y >= 2023 else None),
                   kind="estimate", status="Estimate; 2023 only, the last year with a national total",
                   action="Replace when the department publishes district data after 2023 quarter 1")

    s.section("7. Jet fuel: sales, trade, production and aircraft movements")
    jet_dept = s.line("Department national file, jet", ML, "Source observation",
                      "National annual workbook, years with four quarters reported.",
                      {y: d["dept"].get(("jet", y)) for y in YEARS}, status="2012-2023", source=dept_src + ", national workbooks")
    jet_fiasa = s.line("FIASA sales, jet", ML, "Comparison only", "FIASA annual report, latest edition.",
                       {y: d["fiasa_sales"].get(("jet", y)) for y in YEARS}, kind="comparison",
                       status="Not used. 2024: 1,754 in FIASA's 2024 edition, 1,955 in its 2025 edition",
                       source="Fuels Industry Association of South Africa, annual reports")
    del jet_fiasa  # shown for comparison; never selected
    jet_sales = s.line("Sales used, jet", ML, "Reporting formula", "Department national file. Blank where not published.",
                       formula=lambda y: f'=IF(ISNUMBER({col(y)}{jet_dept}),{col(y)}{jet_dept},"")',
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


def diesel_by_use_sheet(wb, d: dict, history_rows: dict, sector_rows: dict) -> dict:
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
                   "From History: department national file, to 2023.",
                   formula=lambda y: f'=IF(ISNUMBER(History!{col(y)}{history_rows["sales_diesel"]}),History!{col(y)}{history_rows["sales_diesel"]},"")',
                   kind="formula", status="2012-2023")
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
                   action="0.31 is confirmed by Eskom's reported fuel and generation (DR07 power diesel sheet)")

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

    uses = {"Sales": sales, "Power generation": power, "Mining": mining, "Manufacturing and other industry": manufacturing,
            "Agriculture": agriculture, **split}

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
    return uses


BN_FORMAT = "[>=0.005]0.00;[<=-0.005]-0.00;0.00"  # two decimals; a tiny negative shows as 0.00
DR01_YEARS = list(range(2014, 2026))
DR01_LINES = [
    # label, History row key (with {p} for the fuel) or formula kind, source, note
    ("Sales", "sales_{p}", "Department: sales by province added up (2013-2022); national total (2023)",
     "2023 by province is an estimate. Nothing published after 2023."),
    ("Production", "production_{p}", "Department energy balances, one file a year",
     "Last balance published is 2021."),
    ("Imports", "import_{p}", "SARS customs, by tariff line", "Complete calendar years in litres."),
    ("Exports", "export_{p}", "SARS customs, by tariff line", ""),
    ("Supply", "supply", "Calculated: production + imports - exports", ""),
    ("Stock change", None, "None", "Not published by any source used."),
    ("Supply less sales", "difference", "Calculated: supply - sales",
     "Stock change and statistical difference together. Not production."),
]


def dr01_sheet(wb, history_rows: dict) -> None:
    """The DR01 national balance on one page, in billion litres, each cell a formula on the History sheet."""
    ws = wb.create_sheet("DR01 balance")
    ws["A1"] = "DR01 National balance: petrol and diesel"
    ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
    ws["A2"] = ("Billion litres, calendar years. Every number is a formula on the History sheet. Blank means not published. "
                "FIASA and JODI are not used.")
    ws["A2"].font = Font(name="Arial", size=10, color=INK)
    header = ["Line"] + DR01_YEARS + ["Source", "Note"]
    widths = [22] + [8.5] * len(DR01_YEARS) + [52, 58]
    for i, label in enumerate(header, start=1):
        cell = ws.cell(row=4, column=i, value=label)
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
        cell.fill = PatternFill("solid", fgColor=FILL["header"])
        cell.alignment = Alignment(horizontal="right" if isinstance(label, int) else "left", vertical="top")
        ws.column_dimensions[get_column_letter(i)].width = widths[i - 1]
    last = len(header)

    def here(year: int) -> str:
        return get_column_letter(2 + DR01_YEARS.index(year))

    row = 4
    placed: dict = {}
    for fuel, title in (("diesel", "Diesel"), ("petrol", "Petrol"), ("total", "Diesel and petrol")):
        row += 2 if row > 4 else 1
        for i in range(1, last + 1):
            cell = ws.cell(row=row, column=i, value=title if i == 1 else None)
            cell.font = Font(name="Arial", size=10, bold=True, color=INK)
            cell.fill = PatternFill("solid", fgColor=FILL["section"])
        for label, key, source, note in DR01_LINES:
            row += 1
            placed[(fuel, label)] = row
            ws.cell(row=row, column=1, value=label)
            for year in DR01_YEARS:
                c = here(year)
                if key is None:
                    formula = None
                elif fuel == "total":
                    d, g = placed[("diesel", label)], placed[("petrol", label)]
                    formula = f'=IF(COUNT({c}{d},{c}{g})<2,"",{c}{d}+{c}{g})'
                elif key == "supply":
                    m, im, ex = (placed[(fuel, name)] for name in ("Production", "Imports", "Exports"))
                    formula = f'=IF(COUNT({c}{m},{c}{im},{c}{ex})<3,"",{c}{m}+{c}{im}-{c}{ex})'
                elif key == "difference":
                    su, sa = placed[(fuel, "Supply")], placed[(fuel, "Sales")]
                    formula = f'=IF(COUNT({c}{su},{c}{sa})<2,"",{c}{su}-{c}{sa})'
                else:
                    ref = f"History!{col(year)}{history_rows[key.format(p=fuel)]}"
                    formula = f'=IF(ISNUMBER({ref}),{ref}/1000,"")'
                cell = ws.cell(row=row, column=2 + DR01_YEARS.index(year), value=formula)
                cell.number_format = BN_FORMAT
            ws.cell(row=row, column=last - 1, value="Sum of the diesel and petrol rows" if fuel == "total" and key else source)
            ws.cell(row=row, column=last, value=note)
            calculated = fuel == "total" or key in ("supply", "difference")
            for i in range(1, last + 1):
                cell = ws.cell(row=row, column=i)
                cell.font = Font(name="Arial", size=10, color=INK, bold=label in ("Supply", "Supply less sales") and i == 1)
                cell.fill = PatternFill("solid", fgColor=FILL["formula" if calculated else "observation"])
                cell.alignment = Alignment(wrap_text=i >= last - 1, vertical="top",
                                           horizontal="right" if 1 < i < last - 1 else "left")
    ws.freeze_panes = "B5"


USE_YEARS = list(range(2014, 2024))
DIESEL_USES = [
    # label, basis, source, note
    ("Power generation", "Observed to 2021; estimated from 2022",
     "Department energy balances to 2021; Eskom generation x 0.31 litres per kWh from 2022",
     "Eskom and independent diesel turbines. The balance records almost none for 2017-2019 and nothing for "
     "2020-2021; the Eskom generation data held starts in 2022. Eskom's reported litres are on the DR07 power diesel sheet."),
    ("Mining", "Observed to 2021; estimated from 2022",
     "Department energy balances; moved with the Stats SA mining volume index after 2021", ""),
    ("Manufacturing and other industry", "Observed to 2021; estimated from 2022",
     "Department energy balances; moved with the Stats SA manufacturing volume index after 2021",
     "Not reported separately before 2016."),
    ("Agriculture", "Observed to 2021; estimated from 2022",
     "Department energy balances; moved with agricultural real value added after 2021", ""),
    ("Heavy vehicles", "Estimate", "Road diesel x 60.5%, the share in Stone et al. (2018)",
     "Trucks and buses. Shares are for the 2010 fleet."),
    ("Light vehicles", "Estimate", "Road diesel x 27.0%, the share in Stone et al. (2018)", "Bakkies and minibuses."),
    ("Passenger vehicles", "Estimate", "Road diesel x 12.5%, the share in Stone et al. (2018)", "Cars and SUVs."),
]


def demand_by_use_sheet(wb, history_rows: dict, use_rows: dict) -> None:
    """Demand by use on one page, in billion litres, each cell a formula on the sheets behind it."""
    ws = wb.create_sheet("Demand by use")
    ws["A1"] = "Demand by use: who burns the diesel and petrol"
    ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
    ws["A2"] = ("Billion litres, calendar years. Every number is a formula on the Diesel by use and History sheets. Road "
                "diesel is what remains of sales after the four sourced uses, and includes rail, construction and ships' diesel.")
    ws["A2"].font = Font(name="Arial", size=10, color=INK)
    header = ["Use"] + USE_YEARS + ["Basis", "Source", "Note"]
    widths = [32] + [8.5] * len(USE_YEARS) + [30, 62, 44]
    for i, label in enumerate(header, start=1):
        cell = ws.cell(row=4, column=i, value=label)
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
        cell.fill = PatternFill("solid", fgColor=FILL["header"])
        cell.alignment = Alignment(horizontal="right" if isinstance(label, int) else "left", vertical="top")
        ws.column_dimensions[get_column_letter(i)].width = widths[i - 1]
    last, first_text = len(header), len(USE_YEARS) + 2

    def here(year: int) -> str:
        return get_column_letter(2 + USE_YEARS.index(year))

    def write(row, label, formula, basis, source, note, kind, bold=False):
        ws.cell(row=row, column=1, value=label)
        for year in USE_YEARS:
            cell = ws.cell(row=row, column=2 + USE_YEARS.index(year), value=formula(year) if formula else None)
            cell.number_format = BN_FORMAT
        for i, value in enumerate((basis, source, note), start=first_text):
            ws.cell(row=row, column=i, value=value)
        for i in range(1, last + 1):
            cell = ws.cell(row=row, column=i)
            cell.font = Font(name="Arial", size=10, color=INK, bold=bold and i == 1, italic=kind == "estimate" and 1 < i < first_text)
            cell.fill = PatternFill("solid", fgColor=FILL[kind])
            cell.alignment = Alignment(wrap_text=i >= first_text, vertical="top", horizontal="right" if 1 < i < first_text else "left")

    def title(row, text):
        for i in range(1, last + 1):
            cell = ws.cell(row=row, column=i, value=text if i == 1 else None)
            cell.font = Font(name="Arial", size=10, bold=True, color=INK)
            cell.fill = PatternFill("solid", fgColor=FILL["section"])

    def linked(sheet, source_row):
        ref = lambda y: f"'{sheet}'!{col(y)}{source_row}"  # noqa: E731
        return lambda y: f'=IF(ISNUMBER({ref(y)}),{ref(y)}/1000,"")'

    title(5, "Diesel")
    row, first = 5, 6
    for label, basis, source, note in DIESEL_USES:
        row += 1
        write(row, label, linked("Diesel by use", use_rows[label]), basis, source, note,
              "estimate" if basis == "Estimate" else "observation")
    row += 1
    write(row, "Diesel sales", lambda y: f'=IF(COUNT({here(y)}{first}:{here(y)}{row - 1})<{len(DIESEL_USES) - 1},"",SUM({here(y)}{first}:{here(y)}{row - 1}))',
          "Sum of the rows above", "Equals department sales (provinces added up; national total for 2023)",
          "Nothing published after 2023.", "formula", bold=True)
    for share_label, group in (("Road vehicles, share of diesel", ("Heavy vehicles", "Light vehicles", "Passenger vehicles")),):
        row += 1
        rows_of = [first + [u[0] for u in DIESEL_USES].index(g) for g in group]
        ws_formula = lambda y, r=rows_of, t=row - 1: (  # noqa: E731
            f'=IF(ISNUMBER({here(y)}{t}),(' + "+".join(f"{here(y)}{n}" for n in r) + f')/{here(y)}{t},"")')
        write(row, share_label, ws_formula, "Calculated", "Heavy, light and passenger vehicles over diesel sales", "", "formula")
        for year in USE_YEARS:
            ws.cell(row=row, column=2 + USE_YEARS.index(year)).number_format = "0%"

    row += 2
    title(row, "Petrol")
    row += 1
    write(row, "Road vehicles", linked("History", history_rows["sales_petrol"]), "Observed",
          "Department sales (provinces added up; national total for 2023)",
          "No source splits petrol by use; cars and light vehicles burn nearly all of it.", "observation")
    row += 1
    write(row, "Petrol sales", lambda y, r=row - 1: f'=IF(ISNUMBER({here(y)}{r}),{here(y)}{r},"")', "Sum of the row above",
          "Equals department sales", "Nothing published after 2023.", "formula", bold=True)
    ws.freeze_panes = "B5"


DR04_EVIDENCE = Path("workstreams/WS1_data_validation/dr04_routes_access_evidence_2026-10-08.csv")
DR04_PARTS = ["Pipeline limit", "Pipeline use", "Pipeline cost", "Delivered cost", "Port use", "Port limit", "Port cost", "Access",
              "Competing routes"]
DR04_STATUS_FILL = {"observed": "observation", "inferred": "formula"}  # anything else is open and shown in the estimate colour


def _sheet_head(ws, heading: str, sub_heading: str, header: list, widths: list[float], row: int = 4) -> None:
    """Title, one-line description and the header row (at ``row``) of a plain table sheet."""
    ws["A1"] = heading
    ws["A1"].font = Font(name="Arial", size=15, bold=True, color=INK)
    ws["A2"] = sub_heading
    ws["A2"].font = Font(name="Arial", size=10, color=INK)
    for i, label in enumerate(header, start=1):
        cell = ws.cell(row=row, column=i, value=label)
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
        cell.fill = PatternFill("solid", fgColor=FILL["header"])
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        ws.column_dimensions[get_column_letter(i)].width = widths[i - 1]


def evidence_sheet(wb, title: str, path: Path, parts: list[str], heading: str, subject: str, closing: str) -> None:
    """An evidence table grouped by part: one row per fact with its status, source, page and open gap.

    Rows marked "other products included" are left out, so the sheet carries petrol and diesel only.
    """
    ws = wb.create_sheet(title)
    every = _read(path)
    rows = [r for r in every if r["scope"] != "other products included"]
    left_out = len(every) - len(rows)
    done = sum(r["status"].startswith("observed") for r in rows)
    inferred = sum(r["status"] == "inferred" for r in rows)
    header = ["Item", subject, "Value", "Unit", "Period", "Status", "Source", "Page", "Open gap"]
    mixed = f" Petrol and diesel only: {left_out} facts that mix in other products are left out." if left_out else ""
    _sheet_head(ws, heading,
                f"{done} facts read from sources, {inferred} calculated, {len(rows) - done - inferred} not available (yellow). "
                f"Each row gives its source.{mixed} {closing}",
                header, [34, 30, 36, 20, 24, 14, 44, 12, 60])
    assert {r["part"] for r in rows} <= set(parts), {r["part"] for r in rows} - set(parts)
    row = 4
    for part in parts:
        part_rows = [r for r in rows if r["part"] == part]
        if not part_rows:
            continue
        row += 2 if row > 4 else 1
        for i in range(1, len(header) + 1):
            cell = ws.cell(row=row, column=i, value=part if i == 1 else None)
            cell.font = Font(name="Arial", size=10, bold=True, color=INK)
            cell.fill = PatternFill("solid", fgColor=FILL["section"])
        for r in part_rows:
            row += 1
            kind = DR04_STATUS_FILL.get(r["status"], "estimate")
            values = [r["item"], r["asset_or_route"], r["value"] or "Not available", r["unit"], r["period"], r["status"],
                      r["source"] or "None found", r["page"], r["unresolved_gap"]]
            for i, value in enumerate(values, start=1):
                cell = ws.cell(row=row, column=i, value=value)
                cell.font = Font(name="Arial", size=10, color=INK)
                cell.fill = PatternFill("solid", fgColor=FILL[kind])
                cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "B5"


def dr04_routes_sheet(wb) -> None:
    evidence_sheet(wb, "DR04 routes", DR04_EVIDENCE, DR04_PARTS, "DR04 Routes and access: what the documents establish", "Asset or route",
                   "Built from dr04_routes_access_evidence_2026-10-08.csv.")


DR07_EVIDENCE = Path("workstreams/WS1_data_validation/dr07_demand_evidence_2026-10-08.csv")
DR07_PARTS = ["Power generation", "Vehicle fleet", "New vehicles and electric share", "Vehicle efficiency and distance", "Freight and rail",
              "Sector activity"]
POWER_YEARS = list(range(2016, 2027))
FLEET_CLASSES = [("cars", "Cars"), ("light_commercial", "Light commercial"), ("trucks", "Trucks"), ("buses", "Buses"),
                 ("minibuses", "Minibuses"), ("motorcycles", "Motorcycles"), ("total_self_propelled", "All self-propelled")]
FLEET_PROVINCES = [("GP", "Gauteng"), ("KZN", "KwaZulu-Natal"), ("WC", "Western Cape"), ("EC", "Eastern Cape"), ("MP", "Mpumalanga"),
                   ("LP", "Limpopo"), ("NW", "North West"), ("FS", "Free State"), ("NC", "Northern Cape")]


def dr07_evidence_sheet(wb) -> None:
    evidence_sheet(wb, "DR07 evidence", DR07_EVIDENCE, DR07_PARTS, "DR07 Demand evidence: what calibrates the demand levers", "Covers",
                   "Built by python -m lfm.scripts.build_dr07_demand_evidence.")


def dr07_power_sheet(wb, d: dict) -> None:
    """Diesel burned for power: Eskom's reported litres beside its generation, and the independent plants."""
    ws = wb.create_sheet("DR07 power diesel")
    header = ["Line"] + POWER_YEARS + ["Source", "Note"]
    _sheet_head(ws, "DR07 Diesel burned for power generation",
                "Years to 31 March (2025 is April 2024 to March 2025). Volumes in billion litres. Blank means not reported.",
                header, [44] + [8.5] * len(POWER_YEARS) + [56, 60])
    last = len(header)
    eskom_src = "Eskom Integrated Report 2025, technical statistics, PDF p.141"
    portal = "Eskom data portal and reports (ocgt_generation_eskom.csv)"

    def here(year: int) -> str:
        return get_column_letter(2 + POWER_YEARS.index(year))

    def write(row, label, values, formula, fmt, source, note, kind, bold=False):
        ws.cell(row=row, column=1, value=label)
        for year in POWER_YEARS:
            cell = ws.cell(row=row, column=2 + POWER_YEARS.index(year), value=formula(year) if formula else values.get(year))
            cell.number_format = fmt
        ws.cell(row=row, column=last - 1, value=source)
        ws.cell(row=row, column=last, value=note)
        for i in range(1, last + 1):
            cell = ws.cell(row=row, column=i)
            cell.font = Font(name="Arial", size=10, color=INK, bold=bold and i == 1, italic=kind == "estimate" and 1 < i < last - 1)
            cell.fill = PatternFill("solid", fgColor=FILL[kind])
            cell.alignment = Alignment(wrap_text=i >= last - 1, vertical="top", horizontal="right" if 1 < i < last - 1 else "left")

    def band(row, text):
        for i in range(1, last + 1):
            cell = ws.cell(row=row, column=i, value=text if i == 1 else None)
            cell.font = Font(name="Arial", size=10, bold=True, color=INK)
            cell.fill = PatternFill("solid", fgColor=FILL["section"])

    band(5, "Eskom's own turbines (Ankerlig, Gourikwa, Acacia, Port Rex)")
    write(6, "Fuel burned, as reported", {y: v / 1000 for y, v in d["eskom_fuel"].items()}, None, BN_FORMAT, eskom_src,
          "Diesel and kerosene together, as Eskom reports them. Acacia and Port Rex burn kerosene and are 342 of 2,426 MW.", "observation")
    write(7, "Electricity generated by Eskom, GWh", d["eskom_gwh"], None, "#,##0", portal, "Published from the year to March 2022.", "observation")
    write(8, "Litres per kWh, implied", None,
          lambda y: f'=IF(COUNT({here(y)}6,{here(y)}7)<2,"",{here(y)}6*1000/{here(y)}7)', "0.000",
          "Calculated: fuel burned over electricity generated", f"Confirms the {LITRES_PER_KWH} used on the Power fleet sheet.", "formula")
    band(10, "Independent producers (Avon, Dedisa)")
    write(11, "Electricity generated by independent plants, GWh", d["ipp_gwh"], None, "#,##0", portal, "The producers do not report litres.", "observation")
    write(12, "Diesel burned, estimated", None,
          lambda y: f'=IF(ISNUMBER({here(y)}11),{here(y)}11*{LITRES_PER_KWH}/1000,"")', BN_FORMAT,
          f"Calculated: generation x {LITRES_PER_KWH} litres per kWh", "An estimate, at Eskom's implied rate.", "estimate")
    band(14, "All grid turbines")
    write(15, "Diesel burned, Eskom reported plus independent estimated", None,
          lambda y: f'=IF(COUNT({here(y)}6,{here(y)}12)<2,"",{here(y)}6+{here(y)}12)', BN_FORMAT,
          "Sum of the two volume rows above", "Only where both are known. Private backup generators are not in any source.", "formula", bold=True)
    ws.freeze_panes = "B5"


def dr07_fleet_sheet(wb, d: dict) -> None:
    """Registered vehicles by province and class at the latest month published."""
    ws = wb.create_sheet("DR07 fleet by province")
    month = d["natis_latest"]
    header = ["Province"] + [label for _, label in FLEET_CLASSES] + ["Share of all vehicles", "Source"]
    _sheet_head(ws, f"DR07 Registered vehicles by province and class, {month}",
                "Vehicles on the register at month end. The register gives class and province, not fuel: petrol and diesel are not split "
                "by class or province in any source held (nationally, December 2023: 8.56 million petrol and 3.34 million diesel).",
                header, [22] + [16] * len(FLEET_CLASSES) + [14, 62])
    last, total_col = len(header), 1 + len(FLEET_CLASSES)
    source = "eNaTIS live vehicle population by class and province (vehicle_population_natis.csv)"
    row = 4
    for code, name in FLEET_PROVINCES:
        row += 1
        ws.cell(row=row, column=1, value=name)
        for i, (key, _) in enumerate(FLEET_CLASSES, start=2):
            ws.cell(row=row, column=i, value=d["natis_by_province"].get((code, key))).number_format = "#,##0"
        ws.cell(row=row, column=last, value=source)
    top, bottom = 5, row
    row += 1
    ws.cell(row=row, column=1, value="South Africa")
    for i in range(2, total_col + 1):
        c = get_column_letter(i)
        ws.cell(row=row, column=i, value=f"=SUM({c}{top}:{c}{bottom})").number_format = "#,##0"
    ws.cell(row=row, column=last, value="Sum of the nine provinces")
    t = get_column_letter(total_col)
    for r in range(top, row + 1):
        ws.cell(row=r, column=last - 1, value=f"={t}{r}/{t}${row}").number_format = "0.0%"
        for i in range(1, last + 1):
            cell = ws.cell(row=r, column=i)
            cell.font = Font(name="Arial", size=10, color=INK, bold=r == row and i == 1)
            cell.fill = PatternFill("solid", fgColor=FILL["formula" if r == row or i == last - 1 else "observation"])
            cell.alignment = Alignment(wrap_text=i == last, vertical="top", horizontal="right" if 1 < i < last else "left")
    ws.freeze_panes = "B5"


ENTRY_YEARS = list(range(2014, 2026))
ENTRY_POINTS = [("Durban", "Durban", "Sea"), ("Cape Town", "Cape Town", "Sea"), ("Mosselbay", "Mossel Bay", "Sea"),
                ("East London", "East London", "Sea"), ("Port Elizabeth", "Port Elizabeth", "Sea"),
                ("Richards Bay", "Richards Bay", "Sea"), ("Komatipoort", "Komatipoort", "Road, from Mozambique")]
ENTRY_SOURCE = "SARS customs, imports by office of clearance (fuel_trade_sars_by_office.csv)"


def dr04_entry_sheet(wb, d: dict) -> None:
    """Petrol and diesel imports by customs office of entry, in billion litres."""
    ws = wb.create_sheet("DR04 entry points")
    header = ["Entry point", "Route"] + ENTRY_YEARS + ["Source", "Note"]
    _sheet_head(ws, "DR04 Where petrol and diesel imports enter",
                "Billion litres, calendar years. Petrol and diesel only. The office is where the fuel was cleared through customs: the "
                "nearest public record of the entry point, not a berth or terminal record.",
                header, [30, 22] + [8.5] * len(ENTRY_YEARS) + [50, 52])
    first_year, last = 3, len(header)
    named = {office for office, _, _ in ENTRY_POINTS}

    def here(year: int) -> str:
        return get_column_letter(first_year + ENTRY_YEARS.index(year))

    def fill(row, kind, bold=False):
        for i in range(1, last + 1):
            cell = ws.cell(row=row, column=i)
            cell.font = Font(name="Arial", size=10, color=INK, bold=bold and i == 1)
            cell.fill = PatternFill("solid", fgColor=FILL[kind])
            cell.alignment = Alignment(wrap_text=i >= last - 1, vertical="top", horizontal="right" if first_year <= i < last - 1 else "left")

    row = 4
    for product, title in (("diesel", "Diesel"), ("petrol", "Petrol"), (None, "Diesel and petrol")):
        row += 2 if row > 4 else 1
        for i in range(1, last + 1):
            cell = ws.cell(row=row, column=i, value=title if i == 1 else None)
            cell.font = Font(name="Arial", size=10, bold=True, color=INK)
            cell.fill = PatternFill("solid", fgColor=FILL["section"])
        products = (product,) if product else ("diesel", "petrol")
        top = row + 1
        lines = ENTRY_POINTS + [(None, "Other offices", "Land borders and inland offices")]
        for office, label, route in lines:
            row += 1
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=route)
            for year in ENTRY_YEARS:
                if office:
                    value = sum(d["imports_by_office"].get((year, office, pr), 0.0) for pr in products)
                else:
                    value = sum(v for (y, off, pr), v in d["imports_by_office"].items() if y == year and pr in products and off not in named)
                ws.cell(row=row, column=first_year + ENTRY_YEARS.index(year), value=value).number_format = BN_FORMAT
            ws.cell(row=row, column=last - 1, value=ENTRY_SOURCE)
            ws.cell(row=row, column=last, value={"Komatipoort": "The only recorded entry from the Maputo and Matola side.",
                                                 "Durban": "Includes fuel for the inland pipeline and for the coast."}.get(office or "", ""))
            fill(row, "observation")
        row += 1
        ws.cell(row=row, column=1, value="All offices")
        for year in ENTRY_YEARS:
            c = here(year)
            ws.cell(row=row, column=first_year + ENTRY_YEARS.index(year), value=f"=SUM({c}{top}:{c}{row - 1})").number_format = BN_FORMAT
        ws.cell(row=row, column=last - 1, value="Sum of the rows above; equals SARS national imports on the History sheet")
        fill(row, "formula", bold=True)
        row += 1
        ws.cell(row=row, column=1, value="Durban share")
        for year in ENTRY_YEARS:
            c = here(year)
            ws.cell(row=row, column=first_year + ENTRY_YEARS.index(year), value=f'=IF({c}{row - 1}=0,"",{c}{top}/{c}{row - 1})').number_format = "0%"
        ws.cell(row=row, column=last - 1, value="Calculated: Durban over all offices")
        fill(row, "formula")
    ws.freeze_panes = "C5"


ZONE_SOURCE = "Department of Mineral and Petroleum Resources, zone lists effective 2 April 2014 and 3 April 2024"
PROVINCE_ORDER = ["Gauteng", "Mpumalanga", "Free State", "North West", "Limpopo", "KwaZulu Natal", "Eastern Cape", "Western Cape",
                  "Northern Cape"]
GAUTENG_COSTS = [
    # label, {period: cents a litre}, basis, source
    ("Pipeline tariff, Durban to Alrode", {"2024/25": 67.99, "2025/26": 73.22, "2026/27": 77.02},
     "2024/25 as reported; later years calculated by adding NERSA's stated increases",
     "NERSA statements of 15 March 2024 (as quoted by Engineering News) and 15 April 2025"),
    ("Regulated transport differential, Gauteng (zone 9C)", {"2024/25": 82.8, "2026/27": 91.1},
     "Regulated allowance in the petrol and diesel price for transport from the coast",
     "Department zone list, April 2024; Central Energy Fund price composition, 1 April 2026"),
    ("Regulated secondary storage", {"2024/25": 36.6, "2026/27": 39.0}, "Regulated allowance for depot storage; one national figure",
     "Department diesel margins, 2024; Central Energy Fund price composition, 1 April 2026"),
    ("Regulated secondary distribution", {"2024/25": 17.2, "2026/27": 19.1},
     "Regulated allowance for road delivery from depot to service station; one national figure",
     "Department diesel margins, 2024; Central Energy Fund price composition, 1 April 2026"),
    ("Commercial road tanker rate, Durban to Gauteng", {}, "Not published", "None found; needs Vopak or a haulier"),
    ("Rail rate, Durban to Gauteng", {}, "Not published", "None found; needs Transnet or Vopak"),
]
GAUTENG_PERIODS = ["2024/25", "2025/26", "2026/27"]


def dr04_transport_sheet(wb, d: dict) -> None:
    """Regulated cost of moving petrol and diesel: the Gauteng route by element, then the differential for every zone."""
    ws = wb.create_sheet("DR04 transport cost")
    header = ["Zone", "Provinces", "Districts", "Examples", "2014", "2024", "Change", "Source"]
    _sheet_head(ws, "DR04 Regulated cost of moving petrol and diesel",
                "Cents a litre. These are regulated allowances in the fuel price, set by the department and the energy regulator. "
                "They are not what a haulier or Transnet charges a shipper: commercial road and rail rates are not published.",
                header, [44, 34, 10, 58, 9, 9, 9, 62], row=14)
    rates, places = d["zone_differentials"], d["zone_districts"]

    def band(row, text, width):
        for i in range(1, width + 1):
            cell = ws.cell(row=row, column=i, value=text if i == 1 else None)
            cell.font = Font(name="Arial", size=10, bold=True, color=INK)
            cell.fill = PatternFill("solid", fgColor=FILL["section"])

    # block 1: the Durban to Gauteng route, element by element
    band(4, "Durban to Gauteng, by element", len(header))
    labels = ["Element"] + GAUTENG_PERIODS + ["Basis", "", "", "Source"]
    for i, label in enumerate(labels, start=1):
        cell = ws.cell(row=5, column=i, value=label)
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
        cell.fill = PatternFill("solid", fgColor=FILL["header"])
    row = 5
    for label, values, basis, source in GAUTENG_COSTS:
        row += 1
        cells = [label] + [values.get(period) for period in GAUTENG_PERIODS] + [basis, None, None, source]
        kind = "observation" if values else "estimate"
        for i, value in enumerate(cells, start=1):
            cell = ws.cell(row=row, column=i, value=value)
            cell.font = Font(name="Arial", size=10, color=INK, italic=label.startswith("Pipeline") and i in (3, 4))
            cell.fill = PatternFill("solid", fgColor=FILL[kind])
            cell.alignment = Alignment(wrap_text=i in (5, 8), vertical="top", horizontal="right" if 2 <= i <= 4 else "left")
            if 2 <= i <= 4:
                cell.number_format = "0.00"
        ws.merge_cells(start_row=row, start_column=5, end_row=row, end_column=7)
    ws.merge_cells(start_row=5, start_column=5, end_row=5, end_column=7)

    # block 2: every pricing zone
    band(13, "Regulated transport differential by pricing zone (the same for petrol and diesel in 2014; diesel list for 2024)", len(header))
    row = 14

    def order(zone):
        provinces = sorted({p for z, _, p in places if z == zone}, key=PROVINCE_ORDER.index)
        return (PROVINCE_ORDER.index(provinces[0]) if provinces else len(PROVINCE_ORDER), rates.get((zone, "diesel", "2024"), 0))

    for zone in sorted({z for (z, _, _) in rates}, key=order):
        row += 1
        districts = sorted(dist for z, dist, _ in places if z == zone)
        provinces = sorted({p for z, _, p in places if z == zone}, key=PROVINCE_ORDER.index)
        old, new = rates.get((zone, "diesel", "2014")), rates.get((zone, "diesel", "2024"))
        label = zone.lstrip("0") + (" (Gauteng)" if zone == "09C" else " (coast)" if zone == "01A" else "")
        cells = [label, ", ".join(provinces) or "Not in the 2014 district list", len(districts) or None, ", ".join(districts[:6]),
                 old, new, f'=IF(COUNT(E{row},F{row})<2,"",F{row}-E{row})', ZONE_SOURCE]
        for i, value in enumerate(cells, start=1):
            cell = ws.cell(row=row, column=i, value=value)
            cell.font = Font(name="Arial", size=10, color=INK, bold=zone in ("09C", "01A") and i == 1)
            cell.fill = PatternFill("solid", fgColor=FILL["formula" if i == 7 else "observation"])
            cell.alignment = Alignment(wrap_text=i in (2, 4, 8), vertical="top", horizontal="right" if i in (3, 5, 6, 7) else "left")
            if i in (5, 6, 7):
                cell.number_format = "0.0"
    ws.freeze_panes = "B15"


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
     "No sales after 2023; no production after 2021 (the last energy balance); no stock series.", "History, sections 2-5"),
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
     "2013-2022 observed; 2023 estimated with the best of six methods back-tested; 2024 blank (no national total).",
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


def power_case_totals(d: dict) -> dict:
    """The three power cases as numbers, million litres a year, for use outside the workbook.

    Mirrors the formulas on the Power fleet sheet with its default assumptions (0.31 litres per kWh, 10% of
    output on diesel when gas is available, 40% load factor on gas). Returns ``{"low" | "medium" | "high" |
    "ceiling" | "burned": {year: value}}``.
    """
    fleet = d["power_fleet"]
    mw = {r["station"]: float(r["capacity_mw"]) for r in fleet}
    contract = {r["station"]: int(r["last_full_year"]) for r in fleet if r["group"] == "diesel_station" and r["last_full_year"]}
    eskom = mw["Ankerlig"] + mw["Gourikwa"]
    peaking_mw = sum(mw[r["station"]] for r in fleet if r["group"] in ("diesel_station", "kerosene_station"))
    load = {y: d["ocgt_gwh"][y] / (peaking_mw * 8.76) for y in (2024, 2025, 2026)}
    settings = {"low": (False, True, 0, 0.0, 0.0, load[2026]),
                "medium": (True, True, IRP_GAS_MW_2030 / 2, 0.10, 0.40, load[2025]),
                "high": (True, False, IRP_GAS_MW_2030, 1.0, load[2024], load[2024])}
    out: dict = {name: {} for name in settings}
    for name, (keep, switch, gas_mw, gas_on_diesel, gas_load, peaker_load) in settings.items():
        for year in FUTURE:
            independents = sum(mw[st] for st in contract if keep or year <= contract[st])
            share = 0.10 if switch and year >= GAS_SWITCH_YEAR else 1.0
            today = (independents + eskom * share) * 8.76 * peaker_load * LITRES_PER_KWH
            sites = (gas_mw if year >= 2030 else 0) * 8.76 * gas_load * gas_on_diesel * LITRES_PER_KWH
            out[name][year] = today + sites
    diesel_mw = sum(mw[r["station"]] for r in fleet if r["group"] == "diesel_station")
    out["ceiling"] = {y: (diesel_mw + (IRP_GAS_MW_2030 if y >= 2030 else 0)) * 8.76 * LITRES_PER_KWH for y in FUTURE}
    out["burned"] = {y - 1: v * LITRES_PER_KWH for y, v in d["ocgt_gwh"].items() if y - 1 in FUTURE}
    return out


def power_fleet_sheet(wb, d: dict) -> None:
    s = Sheet(wb, "Power fleet", "Diesel for power: the fleet, the coal retirements and three cases",
              "A block by station and year, as asked on 7 October. Capacities are from Eskom's fact sheet; retirement "
              "dates from Eskom and from reports of the environment minister's decisions. The three cases are "
              "scenarios: yellow rows are assumptions for Nigel and Henry to confirm.", years=FUTURE)
    c = s.col
    fleet = d["power_fleet"]
    litres = s.row + 2                       # the assumption rows sit first so that every formula can point at them

    s.section("Assumptions used below")
    s.line("Diesel burned per kWh generated", "litres/kWh", "Assumption", "Reported Eskom burn over generation in three "
           "years. A proposal awaiting review.", scalar=LITRES_PER_KWH, kind="estimate", fmt="0.00",
           source="Parliamentary replies on Eskom diesel burn; Eskom generation", action="Nigel / Henry to confirm")
    backup = s.line("Share of output on diesel when gas is available", "%", "Assumption",
                    "Diesel as the backup fuel of a station whose main fuel is gas. NO SOURCE: Eskom's tender says only "
                    "that gas will be 'supplemented by diesel as and when it's required'.",
                    scalar=10, kind="estimate", fmt="0", action="Nigel / Henry to confirm")
    gas_lf = s.line("Load factor of a gas plant running on gas", "%", "Assumption",
                    "NO SOURCE. Eskom describes the gas it needs as dispatchable baseload, so well above a peaker.",
                    scalar=40, kind="estimate", fmt="0", action="Nigel / Henry to confirm")

    s.section("1. Stations that burn diesel today (installed capacity)")
    station = {}
    for r in fleet:
        if r["group"] == "diesel_station":
            station[r["station"]] = s.line(
                f'{r["station"]} ({r["owner"]})', "MW", "Source observation", f'{r["note"]}. {r["event"]}.',
                {y: float(r["capacity_mw"]) for y in FUTURE}, status="Installed capacity", source=r["source"], fmt="#,##0")
    first, last = min(station.values()), max(station.values())
    total_mw = s.line("Diesel stations, total installed", "MW", "Reporting formula", "Sum of the four stations.",
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

    s.section("3. Coal stations being retired: capacity still operating")
    coal = []
    for r in fleet:
        if r["group"] == "coal_retiring":
            last_year = int(r["last_full_year"])
            coal.append(s.line(r["station"], "MW", "Source observation", f'{r["event"]}.',
                               {y: float(r["capacity_mw"]) if y <= last_year else 0 for y in FUTURE},
                               status="Capacity shown to the last full year of operation", source=r["source"], fmt="#,##0"))
    operating = s.line("Coal capacity operating, these eight stations", "MW", "Reporting formula", "Sum of the rows above.",
                       formula=lambda y: f"=SUM({c(y)}{coal[0]}:{c(y)}{coal[-1]})", kind="formula", fmt="#,##0")
    s.line("Coal capacity retired since 2022", "MW", "Reporting formula", "2022 total less this year's.",
           formula=lambda y: f"={c(2022)}{operating}-{c(y)}{operating}", kind="formula", fmt="#,##0")

    contract = {r["station"]: int(r["last_full_year"]) for r in fleet if r["group"] == "diesel_station" and r["last_full_year"]}
    independents = sum(float(r["capacity_mw"]) for r in fleet if r["station"] in contract)
    observed_lf = {y: d["ocgt_gwh"][y] / (3431 * 8.76) * 100 for y in (2024, 2025, 2026)}
    cases = {
        "low": {
            "story": "Avon and Dedisa stop when their agreements end; Ankerlig and Gourikwa move to gas; no gas plant is "
                     "built at a retired coal site; the peakers run as little as in the year to March 2026.",
            "continue": False, "switch": True, "gas_mw": 0, "gas_diesel": "0", "gas_lf": "0", "lf": observed_lf[2026]},
        "medium": {
            "story": "Avon and Dedisa continue after their agreements; Ankerlig and Gourikwa move to gas; half the IRP "
                     "2025 gas requirement is built at the five coal sites and has gas, with diesel as backup; the "
                     "peakers run as in the year to March 2025.",
            "continue": True, "switch": True, "gas_mw": IRP_GAS_MW_2030 / 2, "gas_diesel": f"$D${backup}",
            "gas_lf": f"$D${gas_lf}", "lf": observed_lf[2025]},
        "high": {
            "story": "Avon and Dedisa continue; gas does not arrive, so Ankerlig and Gourikwa stay on diesel and the gas "
                     "turbines built at Camden, Grootvlei, Hendrina, Arnot and Kriel (all 6 GW of the IRP 2025 "
                     "requirement) run as diesel peakers, as Ankerlig and Gourikwa do today; load factor as at the "
                     "peak of load-shedding.",
            "continue": True, "switch": False, "gas_mw": IRP_GAS_MW_2030, "gas_diesel": "100", "gas_lf": None,
            "lf": observed_lf[2024]},
    }
    totals = {}
    for name, case in cases.items():
        s.section(f"4. {name.capitalize()} case: {case['story']}")
        available = s.line(
            f"Avon and Dedisa available, {name}", "MW", "Scenario",
            "Both stations to 2035." if case["continue"] else
            "Each to the last full year of its agreement (Dedisa 2029, Avon 2030), then zero.",
            {y: independents if case["continue"] else
             sum(float(r["capacity_mw"]) for r in fleet if r["station"] in contract and y <= contract[r["station"]])
             for y in FUTURE},
            kind="estimate", fmt="#,##0", status="What follows the agreements is not known",
            source="African Energy, 9 October 2015 (15-year agreements)", action="Nigel / Henry to confirm")
        share = s.line(
            f"Share of Ankerlig and Gourikwa output on diesel, {name}", "%", "Scenario",
            "100% until Eskom's stated gas switch in December 2027, then the backup share." if case["switch"] else
            "100% throughout: the gas supply does not arrive.",
            formula=lambda y, sw=case["switch"]: f"=$D${backup}" if sw and y >= GAS_SWITCH_YEAR else "=100",
            kind="estimate", fmt="0", source="Eskom gas supply tender, as reported by News24, 12 June 2023",
            action="Nigel / Henry to confirm")
        gas_mw = s.line(f"Gas turbines at the five coal sites, {name}", "MW", "Scenario",
                        "From 2030, when Camden, Grootvlei, Hendrina, Arnot and Kriel are due to stop. Which sites, and "
                        "how large, is not decided; the national gas requirement is used as a stand-in.",
                        {y: case["gas_mw"] if y >= 2030 else 0 for y in FUTURE}, kind="estimate", fmt="#,##0",
                        source="IRP 2025 gas requirement, as reported by TechCentral, 22 April 2026", action="Nigel / Henry to confirm")
        me = s.row + 1
        today = s.line(
            f"Diesel at today's stations, {name}", ML, "Proposed estimate",
            "Load factor in column D (%), an observed figure for the whole peaking fleet. Avon and Dedisa wholly on "
            "diesel; Ankerlig and Gourikwa at the share above.",
            formula=lambda y, me=me, a=available, sh=share: (
                f'=({c(y)}{a}+({c(y)}{station["Ankerlig"]}+{c(y)}{station["Gourikwa"]})*{c(y)}{sh}/100)'
                f'*8.76*$D${me}/100*$D${litres}'),
            kind="estimate", scalar=case["lf"], status="Estimate", action="Nigel / Henry to confirm: the load factor in column D")
        site_lf = case["gas_lf"] or f"$D${me}"            # high case: run as peakers at the fleet's load factor
        sites = s.line(
            f"Diesel at the five coal sites, {name}", ML, "Scenario",
            "Gas turbine capacity times load factor times share of output on diesel times litres per kWh. "
            + ("Run as diesel peakers at the load factor above." if case["gas_lf"] is None else
               "Run on gas at the gas-plant load factor, with the backup share on diesel."),
            formula=lambda y, r=gas_mw, lf=site_lf, sh=case["gas_diesel"]: f"={c(y)}{r}*8.76*{lf}/100*{sh}/100*$D${litres}",
            kind="estimate", status="Scenario", action="Nigel / Henry to confirm")
        totals[name] = s.line(f"Diesel for power, {name} case", ML, "Proposed estimate", "The two rows above added.",
                              formula=lambda y, a=today, b=sites: f"={c(y)}{a}+{c(y)}{b}", kind="estimate")

    s.section("5. Summary and ceiling")
    for name in cases:
        s.line(f"{name.capitalize()} case", ML, "Proposed estimate", cases[name]["story"],
               formula=lambda y, r=totals[name]: f"={c(y)}{r}", kind="estimate", status="Proposed; not agreed",
               action="Nigel / Henry to confirm")
    s.line("Ceiling: four stations and 6 GW of gas turbines on diesel all year", ML, "Reporting formula",
           "Capacity times 8,760 hours times litres per kWh. How much the fleet could consume; a physical limit, not a "
           "forecast.", formula=lambda y: f"=({c(y)}{total_mw}+{IRP_GAS_MW_2030 if y >= 2030 else 0})*8.76*$D${litres}",
           kind="formula")
    s.line("For reference: diesel burned, estimated", ML, "Reporting formula", "From section 2.",
           formula=lambda y: f'=IF(ISNUMBER({c(y)}{burned}),{c(y)}{burned},"")', kind="formula")

    s.section("6. Not established")
    for label, why in (
            ("Eskom's decision on Camden, Grootvlei, Hendrina, Arnot and Kriel",
             "Due by end September 2026. None had been announced by 8 October: Eskom's media statements to 7 October "
             "carry none. If the stations run past 31 March 2030, the gas turbines in the medium and high cases move later."),
            ("Which sites get gas plants, how large, and whether gas reaches them",
             "The medium and high cases use the national gas requirement as a stand-in."),
            ("Whether Ankerlig and Gourikwa switch to gas on time", "Eskom's stated target was December 2027."),
            ("Avon and Dedisa after their agreements end", "The 15-year agreements end in October 2030 and July 2031. "
             "Low ends them; medium and high continue them."),
            ("Share of output on diesel when gas is available", "No source; 10% is a placeholder."),
            ("Private generators at firms and homes", "Not in this block; no measured volume exists.")):
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
        "oil_balance_jodi": "History section 3: refinery output reported to JODI (comparison only, not used)",
        "fuel_trade_sars_by_office": "DR04 entry points: petrol and diesel imports by customs office",
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
    changes.append("Source selection: 2024 is still set to FIASA on Nigel's sheet, because the department has no 2024 "
                   "figure to switch to. The added sheets do not use FIASA for any year. For Nigel to decide.")
    changes.append("Sheets added: History, DR01 balance, Sector history, Diesel by use, Demand by use, DR04 routes, DR04 entry points, DR04 transport cost, DR07 evidence, DR07 power diesel, DR07 fleet by province, Power fleet, Vehicle history, HML response, Gap status, "
                   "Checks, History sources. No other cell changed.")

    history_rows = history_sheet(wb, d)
    dr01_sheet(wb, history_rows)
    sector_rows = sector_sheet(wb, d)
    use_rows = diesel_by_use_sheet(wb, d, history_rows, sector_rows)
    demand_by_use_sheet(wb, history_rows, use_rows)
    dr04_routes_sheet(wb)
    dr04_entry_sheet(wb, d)
    dr04_transport_sheet(wb, d)
    dr07_evidence_sheet(wb)
    dr07_power_sheet(wb, d)
    dr07_fleet_sheet(wb, d)
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
