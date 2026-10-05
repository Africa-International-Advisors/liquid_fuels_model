"""Refresh open-cycle gas turbine output from Eskom's integrated reports.

Finds the integrated reports on Eskom's results page, downloads any not
already in ``data/raw/eskom/``, and writes:

    assumptions/<vintage>/timeseries/ocgt_generation_eskom.csv
    assumptions/<vintage>/timeseries/ocgt_generation_eskom.sources.yaml

CSV schema:
    country,period,scenario,series,value,unit,source_report
    ZAF,2025,shared,eskom_ocgt,2176.0,GWh,2026

``period`` is Eskom's financial year, named by the year it ends (2025 = 1 April
2024 to 31 March 2025). Series:
    eskom_ocgt           Eskom's own turbines
    eskom_and_ipp_ocgt   Eskom's plus the independent producers' turbines
    ipp_ocgt             the difference, where both are reported

Values are electricity sent out in GWh. Converting to litres of diesel is a
model assumption and is not done here.

Run (any year — it picks up whatever Eskom has published):
    python scripts/fetch_eskom.py --vintage 2026

Options:
    --offline    use only the PDFs already in data/raw/eskom/
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
from lfm.sources import eskom, fiasa


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    paths = Paths.default()
    raw_dir = paths.data_dir / "raw" / "eskom"
    out_dir = paths.vintage_dir(args.vintage) / "timeseries"
    if not out_dir.exists():
        sys.exit(f"vintage directory not found: {out_dir}")

    reports = _reports(raw_dir, args.offline)
    if not reports:
        sys.exit("no Eskom integrated reports found — check the results page address")

    tables: dict[int, dict[int, list]] = {}
    warnings: list[str] = []
    for report in reports:
        rows, problems = eskom.parse_report(eskom.pdf_text(report.path))
        tables[report.year] = rows
        warnings += [f"{report.year} report: {p}" for p in problems]

    combined = fiasa.combine(tables, eskom.SERIES)
    rows = _with_ipp(combined.rows)
    if not rows:
        sys.exit("turbine output could not be read from any report — layout changed?")

    with (out_dir / "ocgt_generation_eskom.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["country", "period", "scenario", "series", "value", "unit", "source_report"])
        for row in rows:
            writer.writerow(["ZAF", row["period"], "shared", row["column"],
                             row["value"], "GWh", row["source_report"]])

    doc = {
        "publisher": "Eskom Holdings SOC Ltd, integrated reports",
        "index_page": eskom.INDEX_URL,
        "retrieved": date.today().isoformat(),
        "period_basis": "financial year ending 31 March of the year shown",
        "latest_year_reported": combined.latest_year,
        "revisions_between_reports": combined.revisions,
        "warnings": warnings + combined.warnings,
        "reports": [
            {"report_year": r.year, "url": r.url, "file": r.path.name, "sha256": r.sha256}
            for r in reports
        ],
    }
    (out_dir / "ocgt_generation_eskom.sources.yaml").write_text(
        yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")

    years = sorted({r["period"] for r in rows})
    print(f"[fetch] turbine output: financial years {years[0]}–{years[-1]}; "
          f"{len(combined.revisions)} figure(s) revised between reports", file=sys.stderr)
    for warning in doc["warnings"]:
        print(f"[fetch]   WARNING {warning}", file=sys.stderr)
    return 0


def _reports(raw_dir: Path, offline: bool) -> list[eskom.Report]:
    if offline:
        found = []
        for path in sorted(raw_dir.glob("eskom-integrated-report-*.pdf")):
            year = int(re.search(r"(\d{4})", path.stem).group(1))
            found.append(eskom.download(eskom.Report(year=year, url="(offline)"), raw_dir))
        return found
    listed = eskom.discover_reports(eskom.fetch_index())
    return [eskom.download(r, raw_dir) for r in listed]


def _with_ipp(rows: list[dict]) -> list[dict]:
    """Add independent-producer output where own and combined are both known."""
    by_year: dict[int, dict[str, dict]] = {}
    for row in rows:
        by_year.setdefault(row["period"], {})[row["column"]] = row
    out = list(rows)
    for year, series in by_year.items():
        own, both = series.get("eskom_ocgt"), series.get("eskom_and_ipp_ocgt")
        if own and both:
            out.append({
                "period": year, "column": "ipp_ocgt",
                "value": both["value"] - own["value"],
                "source_report": max(own["source_report"], both["source_report"]),
            })
    return sorted(out, key=lambda r: (r["column"], r["period"]))


if __name__ == "__main__":
    sys.exit(main())
