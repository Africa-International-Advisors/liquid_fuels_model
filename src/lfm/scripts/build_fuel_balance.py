"""Line up petrol and diesel sales and trade by year, from the registered inputs.

Reads only files already in the vintage and writes one row per product and year:

    workstreams/WS1_data_validation/fuel_balance_petrol_diesel_2009_2025_2026-10-06.csv

Inputs (all under ``assumptions/<vintage>/timeseries/``):

    fuel_sales_department.csv          department sales, complete years only
    fuel_sales_fiasa.csv               FIASA annual report sales, latest edition per year
    fuel_trade_sars.csv                SARS customs imports and exports
    fuel_trade_fiasa.csv               FIASA annual report trade, latest edition per year
    fuel_trade_department_review.csv   department trade report, rounded narrative figures
    energy_balance_department.csv      department energy balances
    oil_balance_jodi.csv               South Africa's JODI submissions, complete years only

Selection:
    Sales   department where all four quarters are reported; otherwise blank.
    Trade   SARS customs from ``SARS_PRIMARY_FROM`` where the year is complete and
            in litres; otherwise blank.
    FIASA is never selected, not even where the department or customs has no
    figure. It and every other source stay in their own columns for comparison.

    Production  department energy balance to 2021, the last one published;
            JODI refinery output after that, where all twelve months are reported.

``sales_less_net_imports`` is sales minus (imports minus exports). It is the
volume that domestic production, stock changes and differences in what "sales"
covers would have to supply for the selected figures to balance. It is not a
measurement of production.

``supply_less_sales`` is reported production plus net imports minus sales. It
is the stock change and statistical difference together: no usable stock
series exists to separate them. It is never used to adjust sales or production.

Run:
    python -m lfm.scripts.build_fuel_balance --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from lfm.config import Paths

PRODUCTS = ("petrol", "diesel")
FIRST_YEAR, LAST_YEAR = 2009, 2025
SARS_PRIMARY_FROM = 2014
DEFAULT_OUT = "workstreams/WS1_data_validation/fuel_balance_petrol_diesel_2009_2025_2026-10-06.csv"
RESIDUAL_BASIS = "sales less net imports; production, stocks and coverage unresolved"
SUPPLY_BASIS = "reported production plus net imports less sales; stock change and statistical difference together"

FIELDS = [
    "period", "country", "product",
    "sales_department", "sales_fiasa", "sales_fiasa_edition",
    "imports_sars", "exports_sars", "sars_months_reported",
    "imports_fiasa", "exports_fiasa", "trade_fiasa_edition",
    "imports_trade_report", "exports_trade_report",
    "imports_energy_balance", "exports_energy_balance", "production_energy_balance",
    "final_consumption_energy_balance", "statistical_difference_energy_balance",
    "sales_used", "sales_used_source", "imports_used", "exports_used", "trade_used_source",
    "net_imports_used", "sales_less_net_imports", "sales_less_net_imports_basis",
    "sales_less_net_imports_minus_energy_balance_production",
    "production_jodi", "stock_change_jodi", "closing_stock_jodi", "imports_jodi", "exports_jodi", "demand_jodi",
    "production_used", "production_used_source", "supply_less_sales", "supply_less_sales_basis", "unit",
]
JODI_COLUMNS = {"refinery_output": "production_jodi", "stock_change": "stock_change_jodi",
                "closing_stock": "closing_stock_jodi", "imports": "imports_jodi", "exports": "exports_jodi",
                "demand": "demand_jodi"}


def _read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _latest_edition(rows: list[dict], keys: tuple[str, ...]) -> dict[tuple, tuple[float, str]]:
    """``{key: (value, edition)}`` keeping the most recent report for each key."""
    out: dict[tuple, tuple[float, str]] = {}
    for row in rows:
        key = tuple(row[k] for k in keys)
        edition = row["source_report"]
        if key not in out or edition > out[key][1]:
            out[key] = (float(row["value"]), edition)
    return out


def sars_annual(rows: list[dict]) -> dict[tuple[str, str, str], tuple[float, int]]:
    """``{(year, flow, product): (litres, months)}`` for complete years reported in litres."""
    out = {}
    for row in rows:
        if row["unit"] == "litres" and int(row["months_reported"]) == 12:
            out[(row["period"], row["flow"], row["product"])] = (float(row["value"]), 12)
    return out


def build(inputs: dict[str, list[dict]]) -> list[dict]:
    """Balance rows from the input tables, keyed by file stem."""
    department = {(r["period"], r["product"]): float(r["value"])
                  for r in inputs["fuel_sales_department"] if int(r["quarters_reported"]) == 4}
    fiasa_sales = _latest_edition(inputs["fuel_sales_fiasa"], ("period", "product"))
    fiasa_trade = _latest_edition(inputs["fuel_trade_fiasa"], ("period", "flow", "product"))
    sars = sars_annual(inputs["fuel_trade_sars"])
    review = {(r["period"], r["flow"], r["product"]): float(r["value"])
              for r in inputs["fuel_trade_department_review"]}
    balance = {(r["period"], r["flow_key"], r["product"]): float(r["value"])
               for r in inputs["energy_balance_department"] if r["flow_key"]}
    jodi = {(r["period"], r["flow"], r["product"]): float(r["value"])
            for r in inputs.get("oil_balance_jodi", []) if int(r["months_reported"]) == 12}

    rows = []
    for product in PRODUCTS:
        for year in range(FIRST_YEAR, LAST_YEAR + 1):
            y = str(year)
            row: dict = dict.fromkeys(FIELDS, "")
            row.update(period=year, country="ZAF", product=product, unit="litres")

            row["sales_department"] = department.get((y, product), "")
            if (y, product) in fiasa_sales:
                row["sales_fiasa"], row["sales_fiasa_edition"] = fiasa_sales[(y, product)]
            for flow, name in (("import", "imports"), ("export", "exports")):
                if (y, flow, product) in sars:
                    row[f"{name}_sars"], row["sars_months_reported"] = sars[(y, flow, product)]
                if (y, flow, product) in fiasa_trade:
                    row[f"{name}_fiasa"], row["trade_fiasa_edition"] = fiasa_trade[(y, flow, product)]
                row[f"{name}_trade_report"] = review.get((y, flow, product), "")
            for key in ("imports", "exports", "production", "final_consumption", "statistical_difference"):
                value = balance.get((y, key, product))
                row[f"{key}_energy_balance"] = "" if value is None else abs(value) if key == "exports" else value

            for flow, column in JODI_COLUMNS.items():
                row[column] = jodi.get((y, flow, product), "")

            if row["sales_department"] != "":
                row["sales_used"], row["sales_used_source"] = row["sales_department"], "department"

            if year >= SARS_PRIMARY_FROM and row["imports_sars"] != "" and row["exports_sars"] != "":
                row["imports_used"], row["exports_used"] = row["imports_sars"], row["exports_sars"]
                row["trade_used_source"] = "SARS customs"
                row["net_imports_used"] = row["imports_used"] - row["exports_used"]

            if row["sales_used"] != "" and row["net_imports_used"] != "":
                row["sales_less_net_imports"] = row["sales_used"] - row["net_imports_used"]
                row["sales_less_net_imports_basis"] = RESIDUAL_BASIS
                if row["production_energy_balance"] != "":
                    row["sales_less_net_imports_minus_energy_balance_production"] = (
                        row["sales_less_net_imports"] - row["production_energy_balance"])

            if row["production_energy_balance"] != "":
                row["production_used"], row["production_used_source"] = row["production_energy_balance"], "energy balance"
            elif row["production_jodi"] != "":
                row["production_used"], row["production_used_source"] = row["production_jodi"], "JODI"
            if row["production_used"] != "" and row["sales_less_net_imports"] != "":
                row["supply_less_sales"] = row["production_used"] - row["sales_less_net_imports"]
                row["supply_less_sales_basis"] = SUPPLY_BASIS
            rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args()

    folder = Paths.default().vintage_dir(args.vintage) / "timeseries"
    stems = ["fuel_sales_department", "fuel_sales_fiasa", "fuel_trade_sars", "fuel_trade_fiasa",
             "fuel_trade_department_review", "energy_balance_department", "oil_balance_jodi"]
    inputs = {stem: _read(folder / f"{stem}.csv") for stem in stems}
    missing = [stem for stem, rows in inputs.items() if not rows]
    if missing:
        sys.exit(f"missing or empty in {folder}: {', '.join(missing)}")

    rows = build(inputs)
    out = Path(args.out)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: round(v) if isinstance(v, float) else v for k, v in row.items()})
    used = [r for r in rows if r["trade_used_source"] == "SARS customs"]
    print(f"wrote {len(rows)} rows -> {out}; SARS trade selected in {len(used)} product-years, "
          f"department sales in {sum(r['sales_used_source'] == 'department' for r in rows)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
