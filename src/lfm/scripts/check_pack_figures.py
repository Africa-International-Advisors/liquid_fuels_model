"""Check the figures on the Convergence review pack's baseline, driver and refinery pages against the inputs.

Reads the chart data stored in the PowerPoint file and the figures quoted in
the page text (typed below with their page), recomputes each from the
registered inputs, and writes one row per figure:

    workstreams/WS3_reporting_delivery/pack_figure_check_2026-10-07.csv

Columns: page, item, pack_value, recomputed, result, input_file, note. A figure
"matches" when it agrees to the precision the pack shows.

Run:
    python -m lfm.scripts.check_pack_figures --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

from pptx import Presentation

from lfm.config import Paths

PACK = Path("pptx/output/delivered/Vopak_Week1_Convergence_review_2026_10_07.pptx")
OUT = Path("workstreams/WS3_reporting_delivery/pack_figure_check_2026-10-07.csv")
PROVINCE = {"Gauteng": "GP", "KwaZulu-Natal": "KZN", "Western Cape": "WC", "Mpumalanga": "MP", "Eastern Cape": "EC",
            "Free State": "FS", "North West": "NW", "Limpopo": "LP", "Northern Cape": "NC"}


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _charts(slide):
    def walk(shapes):
        for shape in shapes:
            if shape.shape_type == 6:
                yield from walk(shape.shapes)
            elif getattr(shape, "has_chart", False) and shape.has_chart:
                yield shape.chart
    for chart in walk(slide.shapes):
        categories = [str(c) for c in chart.plots[0].categories]
        for plot in chart.plots:
            for series in plot.series:
                yield series.name, dict(zip(categories, series.values))


def load(ts: Path) -> dict:
    d: dict = {}
    d["sars"] = {(r["flow"], r["product"], int(r["period"])): float(r["value"]) / 1e9
                 for r in _read(ts / "fuel_trade_sars.csv") if r["unit"] == "litres" and int(r["months_reported"]) == 12}
    d["fiasa"] = {(r["product"], int(r["period"])): float(r["value"]) / 1e9
                  for r in sorted(_read(ts / "fuel_sales_fiasa.csv"), key=lambda r: r["source_report"])}
    province = defaultdict(float)
    for r in _read(ts / "fuel_sales_department_by_province.csv"):
        if r["product"] in ("petrol", "diesel"):
            province[(r["province"], int(r["period"]))] += float(r["value"]) / 1e9
            province[(r["province"], r["product"], int(r["period"]))] += float(r["value"]) / 1e9
    d["province"] = province
    monthly = defaultdict(list)
    for r in _read(ts / "activity_statssa_monthly.csv"):
        monthly[(r["series"], int(r["period"][:4]))].append(float(r["value"]))
    d["sum"] = {k: sum(v) for k, v in monthly.items() if len(v) == 12}
    d["mean"] = {k: sum(v) / 12 for k, v in monthly.items() if len(v) == 12}
    d["macro"] = {(r["series"], int(r["period"])): float(r["value"]) for r in _read(ts / "macro_statssa.csv")
                  if r["basis"] == "actual"}
    d["ocgt"] = {int(r["period"]): float(r["value"]) for r in _read(ts / "ocgt_generation_eskom.csv")
                 if r["series"] == "eskom_and_ipp_ocgt"}
    d["nev"] = {(r["drivetrain"], int(r["period"])): float(r["value"]) for r in _read(ts / "nev_sales_naamsa.csv")}
    stock = defaultdict(float)
    for r in _read(ts / "vehicle_population_natis.csv"):
        if r["period"].endswith("-12") and r["province"] == "ZAF":
            stock[(r["vehicle_class"], int(r["period"][:4]))] += float(r["value"])
    d["stock"] = stock
    d["price"] = {(r["series"], int(r["period"])): float(r["value"]) for r in _read(ts / "fuel_prices_department_annual.csv")}
    d["capacity"] = defaultdict(float)
    for r in _read(ts / "refinery_capacity_reported.csv"):
        d["capacity"][int(r["period"])] += float(r["value"]) / 1000
    return d


def index(series: dict, year: int, base: int = 2024):
    return None if year not in series or base not in series else series[year] / series[base] * 100


def expected_chart(page: int, name: str, category: str, d: dict):
    """``(recomputed value, input file)`` for one chart point, or ``(None, "")`` if not mapped."""
    year = int(category)

    def by(table: dict, key: str) -> dict:
        return {y: v for (k, y), v in table.items() if k == key}

    if page == 6 and name in PROVINCE:
        return d["province"].get((PROVINCE[name], year)), "fuel_sales_department_by_province.csv"
    if page == 8:
        if name in ("Cars", "Minibuses"):
            return index(by(d["stock"], name.lower()), year), "vehicle_population_natis.csv"
        if name in ("Road", "Rail"):
            return index(by(d["sum"], f"freight_payload_{name.lower()}"), year), "activity_statssa_monthly.csv"
        if name.startswith("Agriculture"):
            return index(by(d["macro"], "agriculture_forestry_and_fishing"), year), "macro_statssa.csv"
        if name == "Manufacturing":
            return index(by(d["mean"], "manufacturing_volume_total"), year), "activity_statssa_monthly.csv"
    if page == 9:
        if name == "Mining":
            return index(by(d["mean"], "mining_volume_total"), year), "activity_statssa_monthly.csv"
        if name == "Eskom + IPP":
            return index(d["ocgt"], year), "ocgt_generation_eskom.csv"
        kinds = {"BEV": "battery_electric", "Plug-in hybrid": "plug_in_hybrid", "Hybrid": "traditional_hybrid"}
        if name in kinds:
            return index(by(d["nev"], kinds[name]), year), "nev_sales_naamsa.csv"
        prices = {"Petrol retail": "petrol_95_inland_retail", "Diesel wholesale": "diesel_005_inland_wholesale"}
        if name in prices and (prices[name], year) in d["price"]:
            return d["price"][(prices[name], year)] / 100, "fuel_prices_department_annual.csv"
    if page == 10 and name.startswith("Reported footprint") and year in d["capacity"]:
        return d["capacity"][year], "refinery_capacity_reported.csv"
    return None, ""


def quoted(d: dict) -> list[tuple]:
    """Figures quoted in page text: ``(page, item, pack value, recomputed, decimals, input file)``."""
    s, f, p = d["sars"], d["fiasa"], d["province"]
    total_2022 = sum(v for k, v in p.items() if len(k) == 2 and k[1] == 2022)
    petrol_2022 = sum(p[(c, "petrol", 2022)] for c in PROVINCE.values())

    def share(*codes: str) -> float:
        return sum(p[(c, 2022)] for c in codes) / total_2022 * 100

    def held(code: str) -> float:
        return p[(code, "petrol", 2022)] / petrol_2022 * f[("petrol", 2024)]

    rows = [
        (4, "Petrol sales 2024, bn litres", 9.029, f[("petrol", 2024)], 3, "fuel_sales_fiasa.csv"),
        (4, "Diesel sales 2024, bn litres", 11.734, f[("diesel", 2024)], 3, "fuel_sales_fiasa.csv"),
        (4, "Petrol imports 2024", 4.001, s[("import", "petrol", 2024)], 3, "fuel_trade_sars.csv"),
        (4, "Diesel imports 2024", 10.793, s[("import", "diesel", 2024)], 3, "fuel_trade_sars.csv"),
        (4, "Petrol exports 2024", 0.920, s[("export", "petrol", 2024)], 3, "fuel_trade_sars.csv"),
        (4, "Diesel exports 2024", 0.796, s[("export", "diesel", 2024)], 3, "fuel_trade_sars.csv"),
        (4, "Diesel net imports 2024", 9.997, s[("import", "diesel", 2024)] - s[("export", "diesel", 2024)], 3, "fuel_trade_sars.csv"),
        (4, "Petrol net imports 2024", 3.081, s[("import", "petrol", 2024)] - s[("export", "petrol", 2024)], 3, "fuel_trade_sars.csv"),
        (5, "Gauteng share of 2022 sales, %", 31.1, share("GP"), 1, "fuel_sales_department_by_province.csv"),
        (5, "KZN share, %", 19.6, share("KZN"), 1, "fuel_sales_department_by_province.csv"),
        (5, "Western Cape share, %", 17.9, share("WC"), 1, "fuel_sales_department_by_province.csv"),
        (5, "Three provinces combined, %", 68.6, share("GP", "KZN", "WC"), 1, "fuel_sales_department_by_province.csv"),
        (5, "Three provinces combined, bn litres", 15.02, sum(p[(c, 2022)] for c in ("GP", "KZN", "WC")), 2, "fuel_sales_department_by_province.csv"),
        (5, "Gauteng and KZN together, %", 50.7, share("GP", "KZN"), 1, "fuel_sales_department_by_province.csv"),
        (6, "Gauteng petrol 2024, held 2022 shares", 3.47, held("GP"), 2, "fuel_sales_department_by_province.csv"),
        (6, "KZN petrol 2024, held 2022 shares", 1.47, held("KZN"), 2, "fuel_sales_department_by_province.csv"),
        (6, "Western Cape petrol 2024, held 2022 shares", 1.41, held("WC"), 2, "fuel_sales_department_by_province.csv"),
        (10, "Published capacity 2020, thousand bbl/day", 718, d["capacity"][2020], 0, "refinery_capacity_reported.csv"),
        (10, "Published capacity 2022, thousand bbl/day", 358, d["capacity"][2022], 0, "refinery_capacity_reported.csv"),
    ]
    for code in PROVINCE.values():
        pack = {"GP": 6.81, "KZN": 4.28, "WC": 3.93, "MP": 1.76, "EC": 1.74, "FS": 1.37, "NW": 1.07, "LP": 0.50, "NC": 0.45}[code]
        rows.append((5, f"{code} petrol and diesel 2022, bn litres", pack, p[(code, 2022)], 2, "fuel_sales_department_by_province.csv"))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    args = parser.parse_args()
    vintage = Paths.default().vintage_dir(args.vintage)
    d = load(vintage / "timeseries")
    operators = {(r["plant"], r["period"]): float(r["value"]) for r in _read(vintage / "reference" / "refinery_output_operators.csv")}

    out = []
    for page, item, pack, value, places, source in quoted(d) + [
            (10, "Secunda output, year to June 2024, million barrels", 29.1, operators[("Secunda", "2024")], 1, "refinery_output_operators.csv"),
            (10, "Natref (Sasol share), year to June 2024", 17.8, operators[("Natref", "2024")], 1, "refinery_output_operators.csv")]:
        ok = round(value, places) == round(pack, places)
        out.append({"page": page, "item": item, "pack_value": pack, "recomputed": round(value, places + 2),
                    "result": "matches" if ok else "differs", "input_file": source, "note": "quoted in page text"})
    slides = Presentation(PACK).slides
    for page in (6, 8, 9, 10):
        for name, points in _charts(slides[page - 1]):
            for category, pack in points.items():
                if pack is None:
                    continue
                value, source = expected_chart(page, name, category, d)
                if value is None:
                    out.append({"page": page, "item": f"{name} {category}", "pack_value": round(pack, 2), "recomputed": "",
                                "result": "not checked", "input_file": "",
                                "note": "authored scenario point, not an observation" if page == 10
                                else "chart point; no mapped input"})
                    continue
                ok = abs(pack - value) <= 0.005 * max(abs(value), 1)
                out.append({"page": page, "item": f"{name} {category}", "pack_value": round(pack, 2),
                            "recomputed": round(value, 2), "result": "matches" if ok else "differs",
                            "input_file": source, "note": "chart point"})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(out)
    tally = defaultdict(int)
    for r in out:
        tally[r["result"]] += 1
    print(dict(tally), file=sys.stderr)
    for r in out:
        if r["result"] != "matches":
            print(r["page"], r["item"], r["pack_value"], r["recomputed"], r["result"], file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
