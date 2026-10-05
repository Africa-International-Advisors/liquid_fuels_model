"""Refresh passengers and aircraft movements from Airports Company South Africa.

Downloads ACSA's two group statistics PDFs (fixed addresses, updated in
place each month) into ``data/raw/acsa/`` and writes:

    assumptions/<vintage>/timeseries/air_traffic_acsa.csv
    assumptions/<vintage>/timeseries/air_traffic_acsa_annual.csv
    assumptions/<vintage>/timeseries/acsa.sources.yaml

CSV schemas:
    air_traffic_acsa.csv            (monthly)
        country,period,scenario,measure,flight_type,direction,value,unit,financial_year
        ZAF,2025-04,shared,passengers,international,departure,455258,passengers,FY25/26
    air_traffic_acsa_annual.csv     (calendar years with all twelve months)
        country,period,scenario,measure,flight_type,direction,value,unit

    measure       passengers | aircraft_movements
    flight_type   international | regional | domestic | unscheduled | total
    direction     arrival | departure | total

Coverage: ACSA's nine airports combined. Non-ACSA airports (Lanseria and
others) are not included. Neither file reports cargo.

Run (any time — it picks up whatever months ACSA has added):
    python scripts/fetch_acsa.py --vintage 2026

Options:
    --offline    re-read the PDFs already in data/raw/acsa/
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

import yaml

from lfm.config import Paths
from lfm.sources import acsa

UNIT = {"passengers": "passengers", "aircraft_movements": "aircraft movements"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    paths = Paths.default()
    raw_dir = paths.data_dir / "raw" / "acsa"
    out_dir = paths.vintage_dir(args.vintage) / "timeseries"
    if not out_dir.exists():
        sys.exit(f"vintage directory not found: {out_dir}")

    monthly: list[dict] = []
    annual: list[dict] = []
    warnings: list[str] = []
    files: list[dict] = []
    for measure in acsa.URLS:
        try:
            source = acsa.download(measure, raw_dir, refresh=not args.offline)
        except Exception as exc:  # noqa: BLE001 - one file failing must not stop the other
            warnings.append(f"{measure}: could not obtain the file ({exc})")
            continue
        rows, problems = acsa.parse(acsa.pdf_layout_text(source.path))
        warnings += [f"{measure}: {p}" for p in problems]
        rows, last = acsa.drop_unreported_months(rows)
        base = {"country": "ZAF", "scenario": "shared", "measure": measure,
                "unit": UNIT[measure]}
        monthly += [{**base, **row} for row in rows]
        annual += [{**base, **row} for row in acsa.calendar_years(rows)]
        files.append({"measure": measure, "url": source.url, "file": source.path.name,
                      "sha256": source.sha256, "last_month_reported": last})
        print(f"[fetch] {measure}: {len(rows):,} monthly figures to {last}", file=sys.stderr)
    if not monthly:
        sys.exit("no ACSA figures could be read — check the addresses or layout")

    _write(out_dir / "air_traffic_acsa.csv", monthly, [
        "country", "period", "scenario", "measure", "flight_type", "direction",
        "value", "unit", "financial_year"])
    _write(out_dir / "air_traffic_acsa_annual.csv", annual, [
        "country", "period", "scenario", "measure", "flight_type", "direction",
        "value", "unit"])

    doc = {
        "publisher": "Airports Company South Africa, group aeronautical statistics",
        "retrieved": date.today().isoformat(),
        "coverage": "ACSA's nine airports combined; non-ACSA airports are not included",
        "not_reported": "cargo tonnage and freighter movements are not in these files",
        "check_applied": "every row: arrivals + departures = total, for every year",
        "full_calendar_years": sorted({r["period"] for r in annual}),
        "warnings": warnings,
        "files": files,
    }
    (out_dir / "acsa.sources.yaml").write_text(
        yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
    for warning in warnings:
        print(f"[fetch]   WARNING {warning}", file=sys.stderr)
    return 0


def _write(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
