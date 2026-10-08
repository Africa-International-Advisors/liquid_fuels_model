"""Stage liquid bulk handled at each port from the port authority's cargo summaries.

Reads every summary held in ``external/data/raw/tnpa/`` and writes

    assumptions/<vintage>/timeseries/port_liquid_bulk_tnpa.csv

``--fetch`` first downloads the statistics page and every summary it lists
(monthly and calendar year) that is not already held, and writes
``manifest.json`` with each file's address and checksum.

The page is maintained by hand and has mistakes. A link that leads to another
report is skipped, a file that is a copy of another month is skipped, and a
file whose heading disagrees with the page is kept under the page's month with
a note. Each case is printed as a warning and no month is filled in.

Run:
    python -m lfm.scripts.stage_tnpa --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

from lfm.config import Paths
from lfm.sources import tnpa

REPO = Path(__file__).resolve().parents[3]
RAW = REPO / "external" / "data" / "raw" / "tnpa"
FIELDS = ["country", "period", "period_basis", "scenario", "port", "movement", "value", "unit", "note", "source_file"]


def file_name(record: dict) -> str:
    return f"tnpa-cargo-summary-{record['period']}{'-calendar-year' if record['kind'] == 'annual' else ''}.pdf"


def fetch_all() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    index = tnpa.fetch(tnpa.INDEX_URL)
    (RAW / "tnpa-port-statistics-page.html").write_bytes(index)
    records = tnpa.discover(index.decode("utf-8", "replace"))
    for record in records:
        path = RAW / file_name(record)
        if not path.exists():
            path.write_bytes(tnpa.fetch(record["url"]))
    manifest = {"publisher": "Transnet National Ports Authority", "page": tnpa.INDEX_URL,
                "files": [{"file": file_name(r), "listed_as": f"{r['period']} {r['kind']}", "url": r["url"],
                           "sha256": hashlib.sha256((RAW / file_name(r)).read_bytes()).hexdigest()} for r in records]}
    (RAW / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")


def read_summary(path: Path) -> list[dict]:
    from pypdf import PdfReader

    page = PdfReader(str(path)).pages[0]
    return tnpa.parse_liquid_bulk(page.extract_text() or "", page.extract_text(extraction_mode="layout") or "")


def assemble(summaries: list[tuple[str, str, list[dict] | str]]) -> tuple[list[dict], list[str]]:
    """Rows and warnings from ``(file name, period the page lists, parsed rows or the reason it is not a summary)``."""
    rows, problems = [], []
    seen: dict[tuple[str, str], list[int]] = {}
    for name, listed, parsed in summaries:
        if isinstance(parsed, str):
            problems.append(f"{name}: not a cargo summary ({parsed}); {listed} has no figures")
            continue
        titled, basis = parsed[0]["period"], parsed[0]["period_basis"]
        values = [r["value"] for r in parsed]
        note = "" if parsed[0]["measure"] == "handled" else "heading says cargo invoiced, not handled"
        period = titled
        if basis == "month" and titled != listed:
            if seen.get((titled, basis)) == values:
                problems.append(f"{name}: listed as {listed} but is a copy of the {titled} summary; {listed} has no figures")
                continue
            period = listed
            mismatch = f"heading says {titled}; the page lists it as {listed} and the figures differ from {titled}"
            note = "; ".join(filter(None, [note, mismatch]))
            problems.append(f"{name}: {mismatch}; kept as {listed}")
        seen[(period, basis)] = values
        rows += [{**row, "period": period, "note": note, "source_file": name} for row in parsed]
    rows.sort(key=lambda r: (r["period_basis"], r["period"], r["movement"], r["port"]))
    return rows, problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()
    if args.fetch:
        fetch_all()

    summaries = []
    for path in sorted(RAW.glob("tnpa-cargo-summary-*.pdf")):
        listed = path.stem.replace("tnpa-cargo-summary-", "").replace("-calendar-year", "")
        try:
            summaries.append((path.name, listed, read_summary(path)))
        except tnpa.NotACargoSummary as error:
            summaries.append((path.name, listed, str(error)))
    rows, problems = assemble(summaries)
    for problem in problems:
        print("warning:", problem, file=sys.stderr)

    out = Paths.default().vintage_dir(args.vintage) / "timeseries" / "port_liquid_bulk_tnpa.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    months = sorted({r["period"] for r in rows if r["period_basis"] == "month"})
    years = sorted({r["period"] for r in rows if r["period_basis"] == "calendar year"})
    print(f"wrote {len(rows)} rows -> {out}; months {months[0]} to {months[-1]} ({len(months)}); years {years}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
