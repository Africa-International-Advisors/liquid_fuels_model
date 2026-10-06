"""Refresh customs imports and exports of refined fuels from SARS.

Downloads one workbook per trade type and year from the SARS trade statistics
portal into ``external/data/raw/sars/`` and writes:

    assumptions/<vintage>/timeseries/fuel_trade_sars.csv
    assumptions/<vintage>/timeseries/fuel_trade_sars_by_office.csv
    assumptions/<vintage>/timeseries/fuel_trade_sars_by_partner.csv
    assumptions/<vintage>/timeseries/fuel_trade_sars.sources.yaml

CSV schema (the two detail files add ``district_office,transport_mode`` or
``partner`` before ``value``):
    country,period,scenario,flow,product,value,unit,months_reported
    ZAF,2024,shared,import,diesel,10792817231.0,litres,12

Quantities are in SARS's own statistical unit and are not converted: litres
from 2014, kilograms to 2012, both in 2013. ``district_office`` is the customs
office that cleared the goods, the nearest public indication of entry port.
``partner`` is the country of origin for imports and of destination for exports.

The three CSVs are declared in ``sources.yaml`` and registered. A refresh
changes recent months, so the register must be reconciled afterwards with
``python -m lfm.scripts.sync_register`` for the three ``sources.fuel_trade_sars*``
blocks. SARS is the primary record of imports and exports from 2014; FIASA's
trade table is kept as a cross-check and for earlier years.

Run:
    python -m lfm.scripts.fetch_sars --vintage 2026

Options:
    --offline       use only the workbooks already in external/data/raw/sars/
    --from-year N   first year to hold (default 2010, the portal's earliest)

Closed years already on disk are kept; the current year and the one before are
downloaded again each run because SARS revises recent months.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from datetime import date
from pathlib import Path

import yaml

from lfm.config import Paths
from lfm.sources import sars


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--from-year", type=int, default=sars.FIRST_YEAR)
    args = parser.parse_args()

    paths = Paths.default()
    raw_dir = paths.data_dir / "raw" / "sars"
    out_dir = paths.vintage_dir(args.vintage) / "timeseries"
    if not out_dir.exists():
        sys.exit(f"vintage directory not found: {out_dir}")
    raw_dir.mkdir(parents=True, exist_ok=True)

    this_year = date.today().year
    warnings: list[str] = []
    files: list[dict] = []
    rows: list[dict] = []
    for trade_type in sars.TRADE_TYPES:
        for year in range(args.from_year, this_year + 1):
            path = raw_dir / f"sars-{trade_type.lower()}-chapter27-fuels-{year}.xlsx"
            refresh = not args.offline and (not path.exists() or year >= this_year - 1)
            if refresh:
                try:
                    path.write_bytes(sars.download_year(trade_type, year))
                except Exception as exc:  # noqa: BLE001
                    kept = "kept the copy on disk" if path.exists() else "no file"
                    warnings.append(f"{trade_type} {year}: download failed ({exc}); {kept}")
            if not path.exists():
                continue
            try:
                rows += sars.read_report(path)
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"{trade_type} {year}: could not read {path.name} ({exc})")
                continue
            files.append({"trade_type": trade_type, "year": year, "file": path.name,
                          "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    if not rows:
        sys.exit("no SARS trade data could be read")

    base = {"country": "ZAF", "scenario": "shared"}
    head = ["country", "period", "scenario", "flow", "product"]
    tail = ["value", "unit", "months_reported"]
    totals = sars.annual(rows)
    _write(out_dir / "fuel_trade_sars.csv", totals, base, head + tail)
    _write(out_dir / "fuel_trade_sars_by_office.csv",
           sars.annual(rows, ("district_office", "transport_mode")), base,
           head + ["district_office", "transport_mode"] + tail)
    _write(out_dir / "fuel_trade_sars_by_partner.csv", sars.annual(rows, ("partner",)), base,
           head + ["partner"] + tail)

    part_years = sorted({r["period"] for r in totals if r["months_reported"] < 12})
    mixed = sorted({r["period"] for r in totals if r["unit"] != "litres"})
    (out_dir / "fuel_trade_sars.sources.yaml").write_text(yaml.safe_dump({
        "publisher": "South African Revenue Service, trade statistics",
        "page": sars.URL,
        "retrieved": date.today().isoformat(),
        "selection": {
            "chapter": sars.CHAPTER, "tariff_lines": {k: list(v) for k, v in
                                                       sars.PRODUCT_TARIFFS.items()},
            "countries": "all", "months": "all",
        },
        "units": "as recorded by SARS; not converted",
        "years_with_fewer_than_12_months": part_years,
        "years_with_quantities_not_in_litres": mixed,
        "kept_in": "external/data/raw/sars/",
        "files": files,
        "warnings": warnings,
    }, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")

    years = sorted({r["period"] for r in totals})
    print(f"[fetch] SARS fuel trade: {len(files)} file(s); years {years[0]} to {years[-1]}; "
          f"{len(rows)} lines", file=sys.stderr)
    for warning in warnings:
        print(f"[fetch]   WARNING {warning}", file=sys.stderr)
    return 0


def _write(path: Path, rows: list[dict], base: dict, fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({**base, **row})


if __name__ == "__main__":
    sys.exit(main())
