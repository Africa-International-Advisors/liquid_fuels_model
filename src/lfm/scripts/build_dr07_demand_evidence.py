"""Build the DR07 demand evidence table from the registered inputs.

DR07 asks for the evidence that calibrates the demand levers: reported Eskom
diesel litres, the vehicle fleet by province and class, efficiency history,
independent producers' plant, and the rail and electric vehicle assumptions.
This writes one row per fact, each with its value, period, status, source and
open gap:

    workstreams/WS1_data_validation/dr07_demand_evidence_2026-10-08.csv

Every value is read or calculated from a file already in the vintage, so the
table can be rebuilt. Status is ``observed`` (read from a source),
``inferred`` (calculated here), or ``not available``. FIASA and JODI are not
used.

Run:
    python -m lfm.scripts.build_dr07_demand_evidence --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from lfm.config import Paths

OUT = Path("workstreams/WS1_data_validation/dr07_demand_evidence_2026-10-08.csv")
FIELDS = ["request", "part", "item", "asset_or_route", "value", "unit", "period", "status", "source", "original_file", "page",
          "unresolved_gap", "scope"]
PARTS = ["Power generation", "Vehicle fleet", "New vehicles and electric share", "Vehicle efficiency and distance",
         "Freight and rail", "Sector activity"]
LITRES_PER_KWH = 0.31
ESKOM_REPORT = "external/data/refresh_20261005/raw/eskom/eskom-integrated-report-2025.pdf"
PROVINCES = {"GP": "Gauteng", "KZN": "KwaZulu-Natal", "WC": "Western Cape", "EC": "Eastern Cape", "MP": "Mpumalanga",
             "LP": "Limpopo", "NW": "North West", "FS": "Free State", "NC": "Northern Cape"}


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load(vintage: Path) -> dict:
    ts, ref = vintage / "timeseries", vintage / "reference"
    d: dict = {}
    d["eskom"] = {(r["series"], int(r["period"])): float(r["value"]) for r in _read(ts / "eskom_fuel_eaf_review_2026_10_07.csv")}
    d["ocgt"] = {(r["series"], int(r["period"])): float(r["value"]) for r in _read(ts / "ocgt_generation_eskom.csv")}
    d["fleet"] = [r for r in _read(vintage / "infrastructure" / "power_fleet_diesel.csv")]
    natis = _read(ts / "vehicle_population_natis.csv")
    d["natis_month"] = max(r["period"] for r in natis)
    d["natis"] = {(r["province"], r["vehicle_class"]): float(r["value"]) for r in natis if r["period"] == d["natis_month"]}
    d["by_fuel"] = {r["fuel_type"]: float(r["vehicles"]) for r in _read(ref / "vehicle_population_by_fuel_dot2023.csv")}
    d["new_sales"] = {(r["segment"], int(r["period"])): float(r["value"]) for r in _read(ts / "new_vehicle_market_naamsa.csv") if r["basis"] == "actual"}
    d["nev"] = {(r["drivetrain"], int(r["period"])): float(r["value"]) for r in _read(ts / "nev_sales_naamsa.csv")}
    d["stone"] = {r["vehicle_type"]: r for r in _read(ref / "vehicle_parameters_stone2018.csv")}
    d["freight"] = {(r["mode"], int(r["period"])): float(r["value"]) for r in _read(ts / "freight_payload_statssa_review.csv")}
    d["efficiency"] = {(name, r["scenario"]): float(r["value"]) for name in ("diesel", "gasoline")
                       for r in _read(ts / f"efficiency_improvement_{name}.csv") if r["period"] == "2030"}
    return d


def implied_litres_per_kwh(d: dict) -> dict[int, float]:
    """Eskom's reported turbine fuel over its turbine generation, for the years both are reported."""
    return {year: d["eskom"][("eskom_ocgt_diesel_and_kerosene", year)] / d["ocgt"][("eskom_ocgt", year)]
            for year in range(2016, 2027)
            if ("eskom_ocgt_diesel_and_kerosene", year) in d["eskom"] and ("eskom_ocgt", year) in d["ocgt"]}


def build(d: dict) -> list[dict]:
    rows: list[dict] = []

    def add(part, item, subject, value, unit, period, status, source, original="", page="", gap=""):
        rows.append(dict(request="DR07", part=part, item=item, asset_or_route=subject, value=value, unit=unit, period=period, status=status,
                         source=source, original_file=original, page=page, unresolved_gap=gap, scope="petrol and diesel"))

    # --- power generation ---------------------------------------------------
    fuel_years = sorted(y for (s, y) in d["eskom"] if s == "eskom_ocgt_diesel_and_kerosene")
    recent = fuel_years[-5:]
    add("Power generation", "Fuel burned at Eskom's turbines, as reported", "Eskom: Ankerlig, Gourikwa, Acacia, Port Rex",
        "; ".join(f"{d['eskom'][('eskom_ocgt_diesel_and_kerosene', y)]:,.1f}" for y in recent), "million litres",
        "years to March " + "; ".join(str(y) for y in recent), "observed", "Eskom Integrated Report 2025, technical statistics",
        ESKOM_REPORT, "PDF p.141",
        "Eskom reports diesel and kerosene together. Acacia and Port Rex burn kerosene and are 342 MW of Eskom's 2,426 MW, so "
        "nearly all of it is diesel. Ten years (2016-2025) are on the DR07 power diesel sheet. 2026 is not yet reported.")
    gen_years = sorted(y for (s, y) in d["ocgt"] if s == "eskom_ocgt")
    add("Power generation", "Electricity generated at Eskom's turbines", "Eskom",
        "; ".join(f"{d['ocgt'][('eskom_ocgt', y)]:,.0f}" for y in gen_years), "GWh", "years to March " + "; ".join(str(y) for y in gen_years),
        "observed", "Eskom data portal and reports", "assumptions/2026/timeseries/ocgt_generation_eskom.csv")
    implied = implied_litres_per_kwh(d)
    matched = [y for y in sorted(implied) if d["ocgt"][("eskom_ocgt", y)] > 0][-3:]
    add("Power generation", "Litres burned per kWh, implied", "Eskom",
        "; ".join(f"{implied[y]:.3f}" for y in matched), "litres per kWh", "years to March " + "; ".join(str(y) for y in matched), "inferred",
        "Reported fuel divided by reported generation", ESKOM_REPORT, "",
        f"Confirms the {LITRES_PER_KWH} litres per kWh used on the Power fleet sheet.")
    ipp_years = sorted(y for (s, y) in d["ocgt"] if s == "ipp_ocgt")
    add("Power generation", "Electricity generated at independent diesel plants", "Avon and Dedisa",
        "; ".join(f"{d['ocgt'][('ipp_ocgt', y)]:,.0f}" for y in ipp_years), "GWh", "years to March " + "; ".join(str(y) for y in ipp_years),
        "observed", "Eskom data portal and reports", "assumptions/2026/timeseries/ocgt_generation_eskom.csv")
    add("Power generation", "Diesel burned at independent plants, estimated", "Avon and Dedisa",
        "; ".join(f"{d['ocgt'][('ipp_ocgt', y)] * LITRES_PER_KWH:,.0f}" for y in ipp_years), "million litres",
        "years to March " + "; ".join(str(y) for y in ipp_years), "inferred", f"Generation x {LITRES_PER_KWH} litres per kWh", "", "",
        "The producers do not report litres. Uses Eskom's implied rate.")
    add("Power generation", "Diesel burned in private backup generators", "Businesses and households", "", "million litres", "", "not available",
        "None found", "", "", "No source measures it. It is inside recorded diesel sales and cannot be separated.")
    stations = [r for r in d["fleet"] if r["group"] == "diesel_station"]
    add("Power generation", "Diesel stations and capacity", "; ".join(r["station"] for r in stations),
        "; ".join(f"{float(r['capacity_mw']):,.0f}" for r in stations), "MW", "current", "observed", "Eskom fact sheet GX 0001 (July 2024); African Energy (2015)",
        "assumptions/2026/infrastructure/power_fleet_diesel.csv", "", "Avon began in July 2016 and Dedisa in October 2015; their agreements end in 2031 and 2030.")
    coal = [r for r in d["fleet"] if r["group"] == "coal_retiring"]
    add("Power generation", "Coal stations retiring", "; ".join(r["station"] for r in coal),
        "; ".join(r["last_full_year"] for r in coal), "last full year", "", "observed", "Eskom statements and press reports named in the file",
        "assumptions/2026/infrastructure/power_fleet_diesel.csv", "", "Eskom's decision on five of them, due end September 2026, had not been announced by 8 October.")
    add("Power generation", "New gas or diesel plant: commissioning dates", "Independent producers and Eskom", "", "MW by year", "", "not available",
        "None found with dates", "", "", "The Integrated Resource Plan gives totals, not plant dates. Needed to place diesel backup at new gas plant.")

    # --- vehicle fleet --------------------------------------------------------
    month = d["natis_month"]
    classes = (("cars", "cars"), ("light_commercial", "light commercial"), ("trucks", "trucks"), ("buses", "buses"), ("minibuses", "minibuses"))
    add("Vehicle fleet", "Registered vehicles by class", "South Africa",
        "; ".join(f"{label} {d['natis'][('ZAF', key)]:,.0f}" for key, label in classes), "vehicles", month, "observed",
        "eNaTIS live vehicle population by class and province", "assumptions/2026/timeseries/vehicle_population_natis.csv", "",
        "By province on the DR07 fleet by province sheet. Monthly from February 2021.")
    top = sorted(PROVINCES, key=lambda p: -d["natis"][(p, "total_self_propelled")])[:3]
    total = d["natis"][("ZAF", "total_self_propelled")]
    add("Vehicle fleet", "Largest provinces, share of registered vehicles", "; ".join(PROVINCES[p] for p in top),
        "; ".join(f"{d['natis'][(p, 'total_self_propelled')] / total * 100:.1f}" for p in top), "%", month, "inferred",
        "Calculated from eNaTIS", "assumptions/2026/timeseries/vehicle_population_natis.csv")
    add("Vehicle fleet", "Registered vehicles by fuel", "South Africa", f"petrol {d['by_fuel']['petrol']:,.0f}; diesel {d['by_fuel']['diesel']:,.0f}",
        "vehicles", "December 2023", "observed", "Department of Transport, Transport Statistics Bulletin 2023",
        "assumptions/2026/reference/vehicle_population_by_fuel_dot2023.csv", "", "National only, and not split by class. No later edition found.")
    add("Vehicle fleet", "Vehicles by fuel within each class, and by province", "South Africa", "", "vehicles", "", "not available", "None found", "", "",
        "Needed to say how many diesel bakkies or petrol cars each province has. eNaTIS publishes class and province, not fuel.")
    add("Vehicle fleet", "Vehicles by age", "South Africa", "", "vehicles", "", "not available", "None found", "", "",
        "Needed for fleet replacement. Only apparent retirements can be calculated (Vehicle history sheet).")

    # --- new vehicles and electric share --------------------------------------
    year = max(y for (s, y) in d["new_sales"] if s == "total")
    add("New vehicles and electric share", "New vehicles sold, by segment", "South Africa",
        "; ".join(f"{label} {d['new_sales'][(key, year)]:,.0f}" for key, label in (("cars", "cars"), ("light_commercial", "light commercial"),
                                                                                  ("medium_heavy_commercial", "medium and heavy commercial"))),
        "vehicles", str(year), "observed", "naamsa, industry vehicle sales", "assumptions/2026/timeseries/new_vehicle_market_naamsa.csv")
    nev_year = max(y for (s, y) in d["nev"] if s == "total")
    kinds = (("battery_electric", "battery electric"), ("plug_in_hybrid", "plug-in hybrid"), ("traditional_hybrid", "conventional hybrid"))
    add("New vehicles and electric share", "Electric and hybrid vehicles sold", "South Africa",
        "; ".join(f"{label} {d['nev'][(key, nev_year)]:,.0f}" for key, label in kinds), "vehicles", str(nev_year), "observed",
        "naamsa, new energy vehicle sales", "assumptions/2026/timeseries/nev_sales_naamsa.csv")
    add("New vehicles and electric share", "Share of new vehicles sold", "South Africa",
        "; ".join(f"{label} {d['nev'][(key, nev_year)] / d['new_sales'][('total', nev_year)] * 100:.2f}" for key, label in kinds), "%", str(nev_year),
        "inferred", "Calculated from the two naamsa series", "", "", "Battery electric sales fell from 2024 to 2025.")
    add("New vehicles and electric share", "Electric trucks and electric light commercial vehicles sold", "South Africa", "", "vehicles", "", "not available",
        "None found", "", "", "naamsa does not report electric sales by segment. Benchmarks from other countries are on the HML response sheet.")

    # --- efficiency and distance ----------------------------------------------
    for key, label in (("CarGasoline", "Petrol cars"), ("CarDiesel", "Diesel cars")):
        s = d["stone"][key]
        add("Vehicle efficiency and distance", f"Fuel use and distance, {label.lower()}", label,
            f"{s['l_per_100km_fleet_average']} fleet average; {s['l_per_100km_new']} new; {float(s['km_per_year_fleet_average']):,.0f} km a year",
            "litres per 100 km; km", "2010 fleet", "observed", "Stone et al. (2018), vehicle parc model", "assumptions/2026/reference/vehicle_parameters_stone2018.csv",
            "", "One year only. All 24 vehicle types are in the file and on the Vehicle history sheet.")
    add("Vehicle efficiency and distance", "Efficiency of new vehicles, by year", "South Africa", "", "litres per 100 km", "", "not available", "None found", "", "",
        "No annual series of new-vehicle fuel use was found, so there is no efficiency history.")
    add("Vehicle efficiency and distance", "Efficiency gain assumed in the model", "New diesel and petrol vehicles",
        "; ".join(f"{'petrol' if name == 'gasoline' else name} {d['efficiency'][(name, case)] * 100:.1f} ({case.replace('_', ' ')})"
                  for name in ("diesel", "gasoline") for case in ("high_demand", "low_demand") if (name, case) in d["efficiency"]),
        "% a year", "2030", "observed", "Reatile workbook (model input)", "assumptions/2026/timeseries/efficiency_improvement_diesel.csv", "",
        "A model setting with no source behind it. Nothing was found to confirm or replace it.")

    # --- freight and rail -----------------------------------------------------
    f_years = sorted({y for (_, y) in d["freight"]})
    for mode in ("road", "rail"):
        add("Freight and rail", f"Freight carried by {mode}", "South Africa", "; ".join(f"{d['freight'][(mode, y)] / 1000:,.0f}" for y in f_years),
            "million tonnes", "; ".join(str(y) for y in f_years), "observed", "Statistics South Africa, Land transport survey (P7162), December 2025",
            "assumptions/2026/timeseries/freight_payload_statssa_review.csv", "PDF p.7", "Tonnes, not tonne-kilometres.")
    add("Freight and rail", "Rail's share of road and rail tonnes", "South Africa",
        "; ".join(f"{d['freight'][('rail', y)] / (d['freight'][('rail', y)] + d['freight'][('road', y)]) * 100:.1f}" for y in f_years), "%",
        "; ".join(str(y) for y in f_years), "inferred", "Calculated from the survey", "")
    add("Freight and rail", "Road freight in tonne-kilometres, by year", "South Africa", "", "billion tonne-km", "", "not available",
        "None found as an annual series", "", "", "Needed to size freight that could move to rail. Only single-year figures exist in published studies.")
    add("Freight and rail", "Diesel used by rail locomotives", "Transnet Freight Rail", "", "million litres", "", "not available", "None found", "", "",
        "Needed so that freight moving to rail is not counted as diesel saved in full.")

    # --- sector activity ------------------------------------------------------
    add("Sector activity", "Mining, manufacturing and agriculture: activity and diesel per unit", "South Africa", "On the Sector history sheet", "", "2012-2025",
        "observed", "Statistics South Africa (P2041, P3041.2, P0441); department energy balances", "assumptions/2026/timeseries/activity_statssa_monthly.csv", "",
        "Diesel by sector is observed to 2021 only, the last energy balance.")
    order = {part: i for i, part in enumerate(PARTS)}
    assert {r["part"] for r in rows} <= set(PARTS)
    return sorted(rows, key=lambda r: order[r["part"]])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    args = parser.parse_args()
    rows = build(load(Paths.default().vintage_dir(args.vintage)))
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(f"wrote {len(rows)} rows -> {OUT}; {counts}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
