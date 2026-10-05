"""Refresh hybrid / electric sales and the new vehicle market from naamsa.

Finds the Quarterly Reviews of Business Conditions and the "Industry Vehicle
Sales, Actual and Projections" files on naamsa's quarterly reviews page,
downloads any not already in ``external/data/raw/naamsa/``, and writes:

    assumptions/<vintage>/timeseries/nev_sales_naamsa.csv
    assumptions/<vintage>/timeseries/new_vehicle_market_naamsa.csv
    assumptions/<vintage>/timeseries/naamsa.sources.yaml

CSV schemas:
    nev_sales_naamsa.csv
        country,period,scenario,drivetrain,value,unit,source_file
        ZAF,2025,shared,traditional_hybrid,12818,vehicles,...
        (drivetrain: traditional_hybrid, plug_in_hybrid, battery_electric, total;
         full calendar years only)
    new_vehicle_market_naamsa.csv
        country,period,scenario,segment,value,unit,basis,source_file
        (segment: cars, light_commercial, medium_heavy_commercial, total;
         basis: actual, or projection for the publication year and later.
         Projections are naamsa's own.)

Where several files give the same year, the most recently uploaded wins and
any difference is recorded in the sources file.

naamsa does not publish sales by petrol and diesel.

Run (any year — it picks up whatever naamsa has published):
    python -m lfm.scripts.fetch_naamsa --vintage 2026

Options:
    --since 2024   earliest upload year to read (older layouts differ)
    --offline      use only the PDFs already in external/data/raw/naamsa/
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from datetime import date
from pathlib import Path

import yaml

from lfm.config import Paths
from lfm.sources import naamsa


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--since", type=int, default=2024)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    paths = Paths.default()
    raw_dir = paths.data_dir / "raw" / "naamsa"
    out_dir = paths.vintage_dir(args.vintage) / "timeseries"
    if not out_dir.exists():
        sys.exit(f"vintage directory not found: {out_dir}")

    files = _files(raw_dir, args.since, args.offline)
    if not files:
        sys.exit("no naamsa files found — check the quarterly reviews page address")

    warnings: list[str] = []
    revisions: list[dict] = []
    nev: dict[tuple, dict] = {}
    market: dict[tuple, dict] = {}
    for f in files:   # oldest upload first, so later files overwrite
        text = naamsa.pdf_text(f.path)
        if f.kind == "review":
            table, problems = naamsa.parse_nev(text)
            _merge(nev, table, f, "drivetrain", revisions, basis=None)
        else:
            table, problems = naamsa.parse_market(text)
            _merge(market, table, f, "segment", revisions, basis=int(f.uploaded[:4]))
        warnings += [f"{f.path.name}: {p}" for p in problems]
    if not nev and not market:
        sys.exit("no naamsa table could be read — layout changed?")

    _write(out_dir / "nev_sales_naamsa.csv", [nev[k] for k in sorted(nev)],
           ["country", "period", "scenario", "drivetrain", "value", "unit", "source_file"])
    _write(out_dir / "new_vehicle_market_naamsa.csv", [market[k] for k in sorted(market)],
           ["country", "period", "scenario", "segment", "value", "unit", "basis",
            "source_file"])

    doc = {
        "publisher": "naamsa | The Automotive Business Council",
        "index_page": naamsa.INDEX_URL,
        "retrieved": date.today().isoformat(),
        "note": "naamsa does not publish sales by petrol and diesel.",
        "nev_years": sorted({k[0] for k in nev}),
        "market_years": {
            basis: sorted({k[0] for k, row in market.items() if row["basis"] == basis})
            for basis in ("actual", "projection")
        },
        "warnings": warnings,
        "figures_changed_in_a_later_file": revisions,
        "files": [
            {"kind": f.kind, "uploaded": f.uploaded, "url": f.url,
             "file": f.path.name, "sha256": f.sha256}
            for f in files
        ],
    }
    (out_dir / "naamsa.sources.yaml").write_text(
        yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")

    print(f"[fetch] hybrid and electric sales: years {doc['nev_years']}", file=sys.stderr)
    print(f"[fetch] new vehicle market: actual {doc['market_years']['actual']}, "
          f"projection {doc['market_years']['projection']}", file=sys.stderr)
    print(f"[fetch]   {len(revisions)} figure(s) changed in a later file", file=sys.stderr)
    for warning in warnings:
        print(f"[fetch]   WARNING {warning}", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------- #

def _files(raw_dir: Path, since: int, offline: bool) -> list:
    if offline:
        found = []
        for path in sorted(raw_dir.glob("*.pdf")):
            stamp = re.match(r"(\d{4}-\d{2})_", path.name)
            if not stamp or int(stamp.group(1)[:4]) < since:
                continue
            kind = "projections" if naamsa._PROJECTIONS.search(path.name) else "review"
            found.append(naamsa.SourceFile(
                kind=kind, uploaded=stamp.group(1), url="(offline)", path=path,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        return found
    listed = [f for f in naamsa.discover(naamsa.fetch(naamsa.INDEX_URL).decode("utf-8", "replace"))
              if int(f.uploaded[:4]) >= since]
    print(f"[fetch] {len(listed)} naamsa file(s) listed from {since}", file=sys.stderr)
    return [naamsa.download(f, raw_dir) for f in listed]


def _merge(target: dict, table: dict, f, dimension: str, revisions: list, *, basis) -> None:
    for year, values in table.items():
        for name, value in values.items():
            key = (year, name)
            earlier = target.get(key)
            if earlier is not None and earlier["value"] != value:
                revisions.append({
                    "period": year, dimension: name,
                    "earlier_file": earlier["source_file"], "earlier_value": earlier["value"],
                    "later_file": f.path.name, "later_value": value,
                })
            row = {"country": "ZAF", "period": year, "scenario": "shared",
                   dimension: name, "value": value, "unit": "vehicles",
                   "source_file": f.path.name}
            if basis is not None:
                row["basis"] = "actual" if year < basis else "projection"
            target[key] = row


def _write(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
