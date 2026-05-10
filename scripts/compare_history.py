"""Compare model vehicles output against observed historical RSA demand.

The xlsx's `RSA Demand` columns under the per-product DemandSupply sheets are
the authoritative SA fuel-demand history (the original xlsx fits its
product-level regressions against them). We extract those into
``timeseries/historical_demand.csv``; this script compares the model's
historical backfill against them year-by-year.

Caveats — read these BEFORE drawing conclusions:

  - Model output here is **vehicles segment only** (road transport). Total RSA
    historical demand includes industrial, mining, agriculture, marine
    bunkering, generation backup, etc. — none of those are in the model yet.
    So:
        Petrol comparison      : approx like-for-like (gasoline is mostly road)
        Diesel comparison      : model is a SUBSET of historical (the gap
                                 is unmodelled non-road diesel)
        Jet comparison         : not meaningful (no aviation compute yet)
  - Vehicle parameters are PROVISIONAL. Convergence here doesn't validate
    parameter values — it tests whether the cohort engine reproduces the right
    *shape* given whatever parameters are loaded.

Run:
    python scripts/compare_history.py [--scenario high_demand|low_demand]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from lfm.assumptions import YamlDirectoryProvider
from lfm.config import Paths
from lfm.core.geography import ISO3_LIST
from lfm.demand import vehicles
from lfm.run import Run

REPO = Path(__file__).resolve().parent.parent
HISTORY_END = 2024  # last fully-observed year in the xlsx
PRODUCTS_TRACKED = ("petrol_95", "diesel_50ppm")  # jet excluded — no compute yet


def load_history(paths: Paths) -> pd.DataFrame:
    csv_path = paths.assumptions_dir / "2026" / "timeseries" / "historical_demand.csv"
    if not csv_path.exists():
        sys.exit(
            f"missing {csv_path}.\n"
            "Run `python scripts/extract_xlsx_to_assumptions.py` first."
        )
    return pd.read_csv(csv_path)


def model_historical(run: Run, provider: YamlDirectoryProvider) -> pd.DataFrame:
    """Run the cohort engine, return annual petrol+diesel for each country
    over the historical window."""
    frames: list[pd.DataFrame] = []
    for iso3 in ISO3_LIST:
        annual = vehicles.compute_country_annual(
            provider, run, iso3, start_year=vehicles.HISTORY_START,
        )
        if annual is None:
            continue
        df = annual.reset_index().rename(columns={"year": "period"})
        df.insert(0, "country", iso3)
        frames.append(df)
    if not frames:
        return pd.DataFrame(columns=["country", "period", "petrol_95", "diesel_50ppm"])
    return pd.concat(frames, ignore_index=True)


def build_comparison(
    history: pd.DataFrame, model: pd.DataFrame, scenario: str
) -> pd.DataFrame:
    h = (
        history[history["country"] == "ZAF"]
        .pivot_table(index="period", columns="product", values="value", aggfunc="first")
        .rename_axis(columns=None)
        .reset_index()
    )
    m = model[model["country"] == "ZAF"][["period"] + list(PRODUCTS_TRACKED)]

    merged = h.merge(m, on="period", how="inner", suffixes=("_xlsx", "_model"))
    merged = merged[merged["period"] <= HISTORY_END].sort_values("period")

    rows = []
    for _, r in merged.iterrows():
        for p in PRODUCTS_TRACKED:
            xlsx_col = f"{p}_xlsx"
            model_col = f"{p}_model"
            if xlsx_col not in merged.columns or pd.isna(r[xlsx_col]):
                continue
            x = float(r[xlsx_col])
            v = float(r[model_col]) if not pd.isna(r[model_col]) else 0.0
            gap_pct = (v - x) / x * 100 if x != 0 else float("nan")
            rows.append({
                "year": int(r["period"]),
                "product": p,
                "xlsx_RSA_demand_BL": x / 1e9,
                "model_vehicles_BL": v / 1e9,
                "delta_BL": (v - x) / 1e9,
                "gap_pct_of_xlsx": gap_pct,
            })
    out = pd.DataFrame(rows)
    return out


def render(comparison: pd.DataFrame, scenario: str) -> None:
    if comparison.empty:
        print("(no overlapping history found)")
        return

    print(f"\n=== ZAF historical reconciliation, scenario={scenario} ===")
    print("    xlsx_RSA_demand : observed RSA fuel demand from the xlsx (all uses, all sectors)")
    print("    model_vehicles  : current model output for the vehicles segment ONLY (road)")
    print("    delta = model - xlsx (negative = model below xlsx; expected for diesel)")
    print()

    for product in PRODUCTS_TRACKED:
        sub = comparison[comparison["product"] == product]
        if sub.empty:
            continue
        print(f"  --- {product} ---")
        view = sub.set_index("year")[
            ["xlsx_RSA_demand_BL", "model_vehicles_BL", "delta_BL", "gap_pct_of_xlsx"]
        ].round({"xlsx_RSA_demand_BL": 2, "model_vehicles_BL": 2, "delta_BL": 2, "gap_pct_of_xlsx": 1})
        print(view.to_string())
        print()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", default="high_demand",
                        choices=["high_demand", "low_demand"])
    args = parser.parse_args()

    paths = Paths.default()
    provider = YamlDirectoryProvider(paths)
    run = Run(vintage="2026", scenario=args.scenario)

    history = load_history(paths)
    model = model_historical(run, provider)
    comparison = build_comparison(history, model, args.scenario)
    render(comparison, args.scenario)
    return 0


if __name__ == "__main__":
    sys.exit(main())
