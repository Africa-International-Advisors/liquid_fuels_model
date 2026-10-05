"""Refresh published fuel sales and trade history from the FIASA annual reports.

Finds the annual reports on the association's website, downloads any that
are not already in ``external/data/raw/fiasa/``, reads the consumption and trade
tables, and writes:

    assumptions/<vintage>/timeseries/fuel_sales_fiasa.csv
    assumptions/<vintage>/timeseries/fuel_trade_fiasa.csv
    assumptions/<vintage>/timeseries/fuel_sales_fiasa.sources.yaml

CSV schema:
    country,period,scenario,product,value,unit,source_report
    ZAF,2024,shared,petrol,9029000000.0,litres,2025
(the trade file adds a ``flow`` column: import / export)

The sources file records, for every report used, its URL, download date and
SHA-256, plus every figure that was revised between reports and every year
that a report carried over instead of reporting.

Run (this year, or any later year — it picks up whatever is newest):
    python -m lfm.scripts.fetch_fuel_sales --vintage 2026

Options:
    --since-report 2021   oldest report to use (older layouts are not readable)
    --offline             use only the PDFs already in external/data/raw/fiasa/

Idempotent: re-running rewrites the three files from the PDFs on disk.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path

import yaml

from lfm.config import Paths
from lfm.sources import fiasa


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True, help="Assumption vintage, e.g. 2026")
    parser.add_argument("--since-report", type=int, default=2021)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    paths = Paths.default()
    raw_dir = paths.data_dir / "raw" / "fiasa"
    out_dir = paths.vintage_dir(args.vintage) / "timeseries"
    if not out_dir.exists():
        sys.exit(f"vintage directory not found: {out_dir}")

    reports = _reports(raw_dir, args.since_report, args.offline)
    if not reports:
        sys.exit("no annual reports found — check the website address or external/data/raw/fiasa/")

    # Oldest report first, so its rows can help place the columns of the next one.
    tables = {
        "consumption": (fiasa.CONSUMPTION_HEADING, len(fiasa.CONSUMPTION_PRODUCTS)),
        "trade": (fiasa.TRADE_HEADING, len(fiasa.TRADE_COLUMNS)),
    }
    read: dict[str, dict[int, dict]] = {name: {} for name in tables}
    seen: dict[str, dict[int, list]] = {name: {} for name in tables}
    problems: dict[str, list[str]] = {name: [] for name in tables}
    for report in reports:
        pages = fiasa.pdf_pages(report.path)
        for name, (heading, n_values) in tables.items():
            rows, warnings = fiasa.read_table(pages, heading, n_values, seen[name])
            read[name][report.year] = rows
            seen[name].update(rows)
            problems[name] += [f"{report.year} report: {w}" for w in warnings]

    sales = fiasa.combine(read["consumption"], fiasa.CONSUMPTION_PRODUCTS)
    flows = fiasa.combine(read["trade"], fiasa.TRADE_COLUMNS)
    sales.warnings += problems["consumption"]
    flows.warnings += problems["trade"]
    if not sales.rows:
        sys.exit("consumption table could not be read from any report — layout changed?")

    _write_sales(out_dir / "fuel_sales_fiasa.csv", sales)
    _write_trade(out_dir / "fuel_trade_fiasa.csv", flows)
    _write_sources(out_dir / "fuel_sales_fiasa.sources.yaml", reports, sales, flows)

    _summarise("Consumption", sales)
    _summarise("Imports and exports", flows)
    return 0


# --------------------------------------------------------------------------- #

def _reports(raw_dir: Path, since: int, offline: bool) -> list[fiasa.Report]:
    if offline:
        found = []
        for path in sorted(raw_dir.glob("annual-report-*.pdf")):
            year = int(re.search(r"(\d{4})", path.stem).group(1))
            if year >= since:
                found.append(fiasa.download(fiasa.Report(year=year, url="(offline)"), raw_dir))
        return found

    listed = [r for r in fiasa.discover_reports(fiasa.fetch_index()) if r.year >= since]
    print(f"[fetch] {len(listed)} report(s) listed from {since}: "
          f"{', '.join(str(r.year) for r in listed)}", file=sys.stderr)
    return [fiasa.download(r, raw_dir) for r in sorted(listed, key=lambda r: r.year)]


def _write_sales(path: Path, extraction: fiasa.Extraction) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["country", "period", "scenario", "product", "value", "unit", "source_report"])
        for row in extraction.rows:
            writer.writerow([
                "ZAF", row["period"], "shared", row["column"],
                row["value"] * fiasa.MILLION, "litres", row["source_report"],
            ])


def _write_trade(path: Path, extraction: fiasa.Extraction) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "country", "period", "scenario", "flow", "product",
            "value", "unit", "source_report",
        ])
        rows = sorted(extraction.rows, key=lambda r: (r["column"], r["period"]))
        for row in rows:
            flow, product = row["column"]
            # The report gives LPG trade in kilotonnes, everything else in million litres.
            if product == "lpg":
                value, unit = row["value"], "kilotonnes"
            else:
                value, unit = row["value"] * fiasa.MILLION, "litres"
            writer.writerow([
                "ZAF", row["period"], "shared", flow, product,
                value, unit, row["source_report"],
            ])


def _write_sources(
    path: Path, reports: list[fiasa.Report],
    sales: fiasa.Extraction, flows: fiasa.Extraction,
) -> None:
    def clean(items: list[dict]) -> list[dict]:
        return [
            {k: ("/".join(v) if isinstance(v, tuple) else v) for k, v in item.items()}
            for item in items
        ]

    doc = {
        "publisher": "Fuels Industry Association of South Africa (formerly SAPIA)",
        "index_page": fiasa.INDEX_URL,
        "retrieved": date.today().isoformat(),
        "tables": {
            "consumption": {
                "heading": fiasa.CONSUMPTION_HEADING,
                "report_unit": "million litres",
                "attributed_to": "energy department (as stated in each report)",
                "latest_year_reported": sales.latest_year,
                "carried_over_rows_dropped": clean(sales.carried_over),
                "revisions_between_reports": clean(sales.revisions),
                "warnings": sales.warnings,
            },
            "imports_exports": {
                "heading": fiasa.TRADE_HEADING,
                "report_unit": "million litres (LPG in kilotonnes)",
                "attributed_to": "SARS / energy department (as stated in each report)",
                "note": "kerosene = illuminating paraffin + jet fuel + dual purpose kerosene",
                "latest_year_reported": flows.latest_year,
                "carried_over_rows_dropped": clean(flows.carried_over),
                "revisions_between_reports": clean(flows.revisions),
                "warnings": flows.warnings,
            },
        },
        "reports": [
            {"report_year": r.year, "url": r.url, "file": r.path.name, "sha256": r.sha256}
            for r in reports
        ],
    }
    path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _summarise(label: str, extraction: fiasa.Extraction) -> None:
    years = sorted({r["period"] for r in extraction.rows})
    span = f"{years[0]}–{years[-1]}" if years else "none"
    print(f"[fetch] {label}: {span}; latest year reported {extraction.latest_year}",
          file=sys.stderr)
    for item in extraction.carried_over:
        print(f"[fetch]   dropped {item['period']} from the {item['report']} report "
              "(row repeats the year before)", file=sys.stderr)
    print(f"[fetch]   {len(extraction.revisions)} figure(s) revised between reports",
          file=sys.stderr)
    for warning in extraction.warnings:
        print(f"[fetch]   WARNING {warning}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
