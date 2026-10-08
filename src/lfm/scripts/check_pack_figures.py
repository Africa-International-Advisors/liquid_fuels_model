"""Check the figures in the current Convergence pack against the inputs.

Reads the chart data stored in the PowerPoint file and the figures quoted in
the page text (typed below with their page), recomputes each from the
registered inputs, and writes one row per figure:

    workstreams/WS3_reporting_delivery/pack_figure_check_2026-10-08.csv

Columns: page, item, pack_value, recomputed, result, input_file, note. A figure
"matches" when it agrees to the precision the pack shows. Chart series are
recognised by name, so the check follows the pack when pages move.

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

PACK = Path("pptx/output/delivered/Vopak_Convergence_current.pptx")
OUT = Path("workstreams/WS3_reporting_delivery/pack_figure_check_2026-10-08.csv")
PROVINCE = {"Gauteng": "GP", "KwaZulu-Natal": "KZN", "Western Cape": "WC", "Mpumalanga": "MP", "Eastern Cape": "EC",
            "Free State": "FS", "North West": "NW", "Limpopo": "LP", "Northern Cape": "NC"}
MAP_LABELS = {"GP": 6.81, "KZN": 4.28, "WC": 3.93, "MP": 1.76, "EC": 1.74, "FS": 1.37, "NW": 1.07, "LP": 0.50, "NC": 0.45}


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _charts(slide):
    """``(position on slide, series name, {category: value})`` for every chart series."""
    def walk(shapes):
        for shape in shapes:
            if shape.shape_type == 6:
                yield from walk(shape.shapes)
            elif getattr(shape, "has_chart", False) and shape.has_chart:
                yield shape.chart
    for position, chart in enumerate(walk(slide.shapes)):
        categories = [str(c) for c in chart.plots[0].categories]
        for plot in chart.plots:
            for series in plot.series:
                yield position, series.name, dict(zip(categories, series.values))


def load(ts: Path) -> dict:
    d: dict = {}
    d["sars"] = {(r["flow"], r["product"], int(r["period"])): float(r["value"]) / 1e9
                 for r in _read(ts / "fuel_trade_sars.csv") if r["unit"] == "litres" and int(r["months_reported"]) == 12}
    d["fiasa"] = {(r["product"], int(r["period"])): float(r["value"]) / 1e9
                  for r in sorted(_read(ts / "fuel_sales_fiasa.csv"), key=lambda r: r["source_report"])}
    d["dept"] = {(r["product"], int(r["period"])): float(r["value"]) / 1e9
                 for r in _read(ts / "fuel_sales_department.csv") if int(r["quarters_reported"]) == 4}
    province = defaultdict(float)
    for r in _read(ts / "fuel_sales_department_by_province.csv"):
        if r["product"] in ("petrol", "diesel"):
            province[(r["province"], int(r["period"]))] += float(r["value"]) / 1e9
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
    d["site"] = {(r["asset"], int(r["period"])): float(r["value"]) / 1000 for r in _read(ts / "refinery_capacity_reported.csv")}
    return d


def index(series: dict, year: int, base: int = 2024):
    return None if year not in series or base not in series else series[year] / series[base] * 100


def expected_chart(position: int, name: str, category: str, d: dict):
    """``(recomputed value, input file)`` for one chart point, or ``(None, "")`` if not mapped.

    The two trade charts share series names; the first on the slide is petrol and the second diesel.
    """
    if not category.isdigit():
        return None, ""
    year = int(category)

    def by(table: dict, key: str) -> dict:
        return {y: v for (k, y), v in table.items() if k == key}

    product = ("petrol", "diesel")[position] if position < 2 else None
    trade = {"Imports": "import", "Exports": "export"}
    if name in trade and product:
        return d["sars"].get((trade[name], product, year)), "fuel_trade_sars.csv"
    if name == "Net imports" and product and ("import", product, year) in d["sars"]:
        return d["sars"][("import", product, year)] - d["sars"][("export", product, year)], "fuel_trade_sars.csv"
    if name == "Department sales" and product:
        return d["dept"].get((product, year)), "fuel_sales_department.csv"
    if name.startswith("FIASA") and product:
        return d["fiasa"].get((product, year)), "fuel_sales_fiasa.csv"
    if name in PROVINCE:
        return d["province"].get((PROVINCE[name], year)), "fuel_sales_department_by_province.csv"
    if (name, year) in d["site"]:
        return d["site"][(name, year)], "refinery_capacity_reported.csv"
    if name in ("Cars", "Minibuses"):
        return index(by(d["stock"], name.lower()), year), "vehicle_population_natis.csv"
    if name in ("Road", "Rail"):
        return index(by(d["sum"], f"freight_payload_{name.lower()}"), year), "activity_statssa_monthly.csv"
    if name.startswith("Agriculture"):
        return index(by(d["macro"], "agriculture_forestry_and_fishing"), year), "macro_statssa.csv"
    if name == "Manufacturing":
        return index(by(d["mean"], "manufacturing_volume_total"), year), "activity_statssa_monthly.csv"
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
    return None, ""


def quoted(d: dict) -> list[tuple]:
    """Figures quoted in page text: ``(page, item, pack value, recomputed, decimals, input file)``."""
    s, p = d["sars"], d["province"]
    total_2022 = sum(v for (_, year), v in p.items() if year == 2022)

    def net(product: str, year: int) -> float:
        return s[("import", product, year)] - s[("export", product, year)]

    trade, provincial = "fuel_trade_sars.csv", "fuel_sales_department_by_province.csv"
    rows = [
        (4, "Petrol imports 2025, bn litres", 4.45, s[("import", "petrol", 2025)], 2, trade),
        (4, "Petrol exports 2025", 0.80, s[("export", "petrol", 2025)], 2, trade),
        (4, "Petrol net imports 2025", 3.65, net("petrol", 2025), 2, trade),
        (4, "Petrol net imports, change 2024 to 2025, %", 19, (net("petrol", 2025) / net("petrol", 2024) - 1) * 100, 0, trade),
        (4, "Diesel imports 2025, bn litres", 12.25, s[("import", "diesel", 2025)], 2, trade),
        (4, "Diesel exports 2025", 0.75, s[("export", "diesel", 2025)], 2, trade),
        (4, "Diesel net imports 2025", 11.50, net("diesel", 2025), 2, trade),
        (4, "Diesel net imports, change 2024 to 2025, %", 15, (net("diesel", 2025) / net("diesel", 2024) - 1) * 100, 0, trade),
        (5, "Gauteng, KZN and Western Cape share of 2022 sales, %", 69,
         sum(p[(c, 2022)] for c in ("GP", "KZN", "WC")) / total_2022 * 100, 0, provincial),
    ]
    for code, pack in MAP_LABELS.items():
        rows.append((5, f"{code} petrol and diesel 2022, bn litres (map label)", pack, p[(code, 2022)], 2, provincial))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    args = parser.parse_args()
    d = load(Paths.default().vintage_dir(args.vintage) / "timeseries")

    out = []
    for page, item, pack, value, places, source in quoted(d):
        ok = round(value, places) == round(pack, places)
        out.append({"page": page, "item": item, "pack_value": pack, "recomputed": round(value, places + 2),
                    "result": "matches" if ok else "differs", "input_file": source, "note": "quoted in page text"})
    for page, slide in enumerate(Presentation(PACK).slides, start=1):
        for position, name, points in _charts(slide):
            for category, pack in points.items():
                if pack is None:
                    continue
                value, source = expected_chart(position, name, category, d)
                if value is None:
                    out.append({"page": page, "item": f"{name} {category}", "pack_value": round(pack, 2), "recomputed": "",
                                "result": "not checked", "input_file": "",
                                "note": "no observation for this point (forward year or authored series)"})
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
        tally[(r["page"], r["result"])] += 1
    for key in sorted(tally):
        print(key, tally[key], file=sys.stderr)
    for r in out:
        if r["result"] == "differs":
            print("DIFFERS", r["page"], r["item"], r["pack_value"], r["recomputed"], file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
