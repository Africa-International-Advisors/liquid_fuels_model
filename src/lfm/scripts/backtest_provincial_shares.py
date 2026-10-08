"""Back-test ways of estimating each province's share of petrol and diesel sales.

Uses the department's provincial sales for 2013-2022 as the truth. For every
base year and horizon of one to three years, each method predicts the shares
and is scored by the share points it puts in the wrong province (the sum over
provinces of the absolute difference between predicted and actual share).

Methods:
    hold      shares of the base year, unchanged
    gdp       base-year shares moved with each province's share of real GDP
    trend3    base-year shares extended along the last three years' trend
    avg3      average of the last three years' shares
    cars      base-year shares moved with each province's share of registered cars
    quarter1  the same year's quarter 1 shares, as observed (available for 2023)

Writes workstreams/WS1_data_validation/provincial_share_backtest_2026-10-08.csv.

Run:
    python -m lfm.scripts.backtest_provincial_shares --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

from lfm.config import Paths

OUT = Path("workstreams/WS1_data_validation/provincial_share_backtest_2026-10-08.csv")
PROVINCES = ("GP", "KZN", "WC", "EC", "MP", "FS", "NW", "LP", "NC")
PRODUCTS = ("petrol", "diesel")
YEARS = range(2013, 2023)


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def share(values: dict) -> dict:
    total = sum(values[p] for p in PROVINCES)
    return {p: values[p] / total for p in PROVINCES}


def moved(base: dict, driver_then: dict, driver_now: dict) -> dict:
    """Base shares scaled by the change in a driver's shares, rescaled to sum to one."""
    return share({p: base[p] * driver_now[p] / driver_then[p] for p in PROVINCES})


def misallocated(predicted: dict, actual: dict) -> float:
    return sum(abs(predicted[p] - actual[p]) for p in PROVINCES) * 100


def load(ts: Path) -> dict:
    d = {"annual": defaultdict(dict), "quarter1": defaultdict(dict), "gdp": defaultdict(dict),
         "cars": defaultdict(lambda: defaultdict(float))}
    for r in _read(ts / "fuel_sales_department_by_province.csv"):
        if r["product"] in PRODUCTS:
            d["annual"][(r["product"], int(r["period"]))][r["province"]] = float(r["value"])
    for r in _read(ts / "fuel_sales_department_by_province_quarterly.csv"):
        if r["product"] in PRODUCTS and r["period"].endswith("-Q1"):
            d["quarter1"][(r["product"], int(r["period"][:4]))][r["province"]] = float(r["value"])
    for r in _read(ts / "gdp_by_province_statssa.csv"):
        if r["series"] == "gdpr_at_market_prices":
            d["gdp"][int(r["period"][:4])][r["province"]] = float(r["value"])
    for r in _read(ts / "vehicle_population_natis.csv"):
        if r["vehicle_class"] == "cars" and r["province"] in PROVINCES and r["period"].endswith("-12"):
            d["cars"][int(r["period"][:4])][r["province"]] += float(r["value"])
    return d


def backtest(d: dict) -> list[dict]:
    rows = []
    for product in PRODUCTS:
        actual = {y: share(d["annual"][(product, y)]) for y in YEARS}
        scores: dict = defaultdict(list)
        for base in YEARS:
            for horizon in (1, 2, 3):
                target = base + horizon
                if target not in actual:
                    continue
                methods = {"hold": actual[base]}
                if base - 3 in actual:
                    methods["trend3"] = share({p: max(actual[base][p] + (actual[base][p] - actual[base - 3][p]) / 3 * horizon, 0)
                                               for p in PROVINCES})
                    methods["avg3"] = share({p: sum(actual[base - k][p] for k in range(3)) for p in PROVINCES})
                if base in d["gdp"] and target in d["gdp"]:
                    methods["gdp"] = moved(actual[base], share(d["gdp"][base]), share(d["gdp"][target]))
                if base in d["cars"] and target in d["cars"]:
                    methods["cars"] = moved(actual[base], share(d["cars"][base]), share(d["cars"][target]))
                for name, predicted in methods.items():
                    worst = max(abs(predicted[p] / actual[target][p] - 1) for p in PROVINCES) * 100
                    scores[(name, horizon)].append((misallocated(predicted, actual[target]), worst))
        for year in YEARS:
            if (product, year) in d["quarter1"]:
                predicted = share(d["quarter1"][(product, year)])
                worst = max(abs(predicted[p] / actual[year][p] - 1) for p in PROVINCES) * 100
                scores[("quarter1", 0)].append((misallocated(predicted, actual[year]), worst))
        for (name, horizon), results in sorted(scores.items()):
            rows.append({"product": product, "method": name, "years_ahead": horizon, "tests": len(results),
                         "mean_share_points_misallocated": round(sum(r[0] for r in results) / len(results), 2),
                         "worst_single_province_error_percent": round(max(r[1] for r in results), 1)})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    args = parser.parse_args()
    rows = backtest(load(Paths.default().vintage_dir(args.vintage) / "timeseries"))
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    for r in rows:
        print(" ".join(f"{v!s:>9}" for v in r.values()), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
