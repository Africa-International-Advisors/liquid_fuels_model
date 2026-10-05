"""Refresh every published source the model uses, in one go.

Runs each fetcher in turn. A fetcher that fails (website down, report
layout changed) does not stop the others; the failures are listed at the
end and the exit code is non-zero.

    fetch_energy_dept.py   fuel sales (primary) and energy balances
    fetch_fuel_sales.py    FIASA annual reports: sales and trade tables
    fetch_eskom.py         Eskom gas turbine output
    fetch_natis.py         vehicles on the road and new registrations
    fetch_naamsa.py        hybrid and electric sales; new vehicle market and outlook
    fetch_economy.py       GDP, GDP per capita, population; Treasury growth forecast
    fetch_acsa.py          air passengers and aircraft movements

After fetching, department and FIASA sales are compared year by year and
any difference above 1% is printed. Both are kept; neither is altered.

Run once a year, or whenever a new report is out:
    pip install -e ".[data]"
    python -m lfm.scripts.refresh_sources --vintage 2026

Options:
    --offline    re-read the files already downloaded; no internet needed
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

from lfm.config import Paths

FETCHERS = (
    "fetch_energy_dept.py", "fetch_fuel_sales.py", "fetch_eskom.py",
    "fetch_natis.py", "fetch_naamsa.py", "fetch_economy.py", "fetch_acsa.py",
)
CORE_PRODUCTS = ("petrol", "diesel", "jet")
TOLERANCE = 0.01


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    failed: list[str] = []
    for name in FETCHERS:
        command = [sys.executable, "-m", f"lfm.scripts.{Path(name).stem}", "--vintage", args.vintage]
        if args.offline:
            command.append("--offline")
        print(f"\n=== {name}", file=sys.stderr)
        if subprocess.run(command, check=False).returncode != 0:
            failed.append(name)

    _compare_sales(Paths.default().vintage_dir(args.vintage) / "timeseries")

    if failed:
        print(f"\nFAILED: {', '.join(failed)} — the other sources were refreshed.",
              file=sys.stderr)
        return 1
    print("\nAll sources refreshed.", file=sys.stderr)
    return 0


def _compare_sales(folder: Path) -> None:
    department = _annual(folder / "fuel_sales_department.csv")
    association = _annual(folder / "fuel_sales_fiasa.csv")
    if not department or not association:
        return
    print("\n=== department vs FIASA sales (million litres; differences above 1%)",
          file=sys.stderr)
    shown = 0
    for key in sorted(set(department) & set(association)):
        a, b = department[key], association[key]
        if abs(a - b) / a > TOLERANCE:
            year, product = key
            print(f"  {year} {product:<7} department {a / 1e6:>8,.0f}   FIASA {b / 1e6:>8,.0f}",
                  file=sys.stderr)
            shown += 1
    if not shown:
        print("  none", file=sys.stderr)
    only = sorted({y for y, _ in association} - {y for y, _ in department})
    if only:
        print(f"  years in FIASA only: {', '.join(map(str, only))}", file=sys.stderr)


def _annual(path: Path) -> dict[tuple[int, str], float]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        return {
            (int(row["period"]), row["product"]): float(row["value"])
            for row in csv.DictReader(fh) if row["product"] in CORE_PRODUCTS
        }


if __name__ == "__main__":
    sys.exit(main())
