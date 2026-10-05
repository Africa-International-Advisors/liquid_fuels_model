"""Refresh vehicle population and new registrations from the NaTIS website.

Finds every monthly PDF listed on the NaTIS statistics pages, downloads any
not already in ``external/data/raw/natis/``, and writes:

    assumptions/<vintage>/timeseries/vehicle_population_natis.csv
    assumptions/<vintage>/timeseries/new_vehicle_registrations_natis.csv
    assumptions/<vintage>/timeseries/new_vehicle_registrations_natis_annual.csv
    assumptions/<vintage>/timeseries/natis.sources.yaml

CSV schemas:
    vehicle_population_natis.csv, new_vehicle_registrations_natis.csv
        country,period,scenario,vehicle_class,province,value,unit,source_file
        ZAF,2026-06,shared,cars,ZAF,8340592,vehicles,LiveVehPopPerClassProv-2026-06.pdf
        (province "ZAF" is the national total; population is at month end,
         registrations are for the month)
    new_vehicle_registrations_natis_annual.csv
        country,period,scenario,vehicle_class,value,unit,months_reported
        (calendar-year sums; years with fewer than twelve months are listed
         in the sources file and left out)

NaTIS does not publish vehicles by fuel type.

Run (any year — it picks up whatever NaTIS has published):
    python -m lfm.scripts.fetch_natis --vintage 2026

Options:
    --offline    use only the PDFs already in external/data/raw/natis/
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
from lfm.sources import natis

OUTPUT = {
    "population": "vehicle_population_natis.csv",
    "new_registrations": "new_vehicle_registrations_natis.csv",
}
REVISIONS: list[dict] = []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    paths = Paths.default()
    raw_dir = paths.data_dir / "raw" / "natis"
    out_dir = paths.vintage_dir(args.vintage) / "timeseries"
    if not out_dir.exists():
        sys.exit(f"vintage directory not found: {out_dir}")

    warnings: list[str] = []
    files_used: list[natis.SourceFile] = []
    tables: dict[str, dict[tuple, dict]] = {}
    for kind in natis.KINDS:
        files = _files(kind, raw_dir, args.offline, warnings)
        files_used += files
        tables[kind] = _read(kind, files, warnings)
    if not any(tables.values()):
        sys.exit("no NaTIS figures could be read — check the website address or layout")

    columns = ["country", "period", "scenario", "vehicle_class", "province",
               "value", "unit", "source_file"]
    for kind, name in OUTPUT.items():
        rows = [tables[kind][key] for key in sorted(tables[kind])]
        _write(out_dir / name, rows, columns)

    annual, part_years = _annual(tables["new_registrations"])
    _write(out_dir / "new_vehicle_registrations_natis_annual.csv", annual,
           ["country", "period", "scenario", "vehicle_class", "value", "unit",
            "months_reported"])

    months = {kind: sorted({key[0] for key in tables[kind]}) for kind in tables}
    doc = {
        "publisher": "Road Traffic Management Corporation, NaTIS statistics",
        "index_page": natis.HOME_URL,
        "retrieved": date.today().isoformat(),
        "note": "NaTIS does not publish vehicles by fuel type.",
        "population_months": _span(months["population"]),
        "new_registration_months": _span(months["new_registrations"]),
        "registration_years_left_out_of_annual_file": part_years,
        "warnings": warnings,
        "figures_restated_in_a_later_file": REVISIONS,
        "files": [
            {"kind": f.kind, "period": f.period, "url": f.url,
             "file": f.path.name, "sha256": f.sha256}
            for f in files_used
        ],
    }
    (out_dir / "natis.sources.yaml").write_text(
        yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")

    print(f"[fetch] vehicle population: {doc['population_months']}", file=sys.stderr)
    print(f"[fetch] new registrations: {doc['new_registration_months']}; "
          f"full years {sorted({r['period'] for r in annual})}", file=sys.stderr)
    print(f"[fetch]   {len(REVISIONS)} figure(s) restated in a later file", file=sys.stderr)
    for warning in warnings[:25]:
        print(f"[fetch]   WARNING {warning}", file=sys.stderr)
    if len(warnings) > 25:
        print(f"[fetch]   ... and {len(warnings) - 25} more (see natis.sources.yaml)",
              file=sys.stderr)
    return 0


# --------------------------------------------------------------------------- #

def _files(kind: str, raw_dir: Path, offline: bool, warnings: list[str]) -> list:
    folder = raw_dir / kind
    stem = natis.KINDS[kind][1]
    if offline:
        found = []
        for path in sorted(folder.glob(f"{stem}-*.pdf")):
            period = re.search(r"(\d{4}-\d{2})", path.stem).group(1)
            found.append(natis.SourceFile(
                kind=kind, period=period, url="(offline)", path=path,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        return found

    home = natis.fetch(natis.HOME_URL).decode("utf-8", "replace")
    listed: dict[str, natis.SourceFile] = {}
    for page in natis.category_pages(home, kind):
        try:
            listing = natis.fetch(page).decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001 - one bad page must not stop the rest
            warnings.append(f"{kind}: could not open {page} ({exc})")
            continue
        for source in natis.discover_files(listing, kind):
            listed[source.period] = source
    print(f"[fetch] {kind}: {len(listed)} monthly file(s) listed", file=sys.stderr)

    downloaded = []
    for period in sorted(listed):
        try:
            downloaded.append(natis.download(listed[period], folder))
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"{kind} {period}: download failed ({exc})")
    return downloaded


def _read(kind: str, files: list, warnings: list[str]) -> dict[tuple, dict]:
    """Rows keyed by (month, class, province); a later file wins for a repeated month."""
    table: dict[tuple, dict] = {}
    for f in files:
        rows, problems = natis.parse(natis.pdf_text(f.path))
        warnings += [f"{kind} file {f.period}: {p}" for p in problems]
        if not rows:
            warnings.append(f"{kind} file {f.period}: no table found")
        for row in rows:
            key = (row["period"], row["vehicle_class"], row["province"])
            earlier = table.get(key)
            if earlier is not None and earlier["value"] != row["value"] and row["province"] == "ZAF":
                # NaTIS restates a month when a later file carries it again
                # (late registrations). The later file is kept; the change is logged.
                REVISIONS.append({
                    "kind": kind, "period": row["period"],
                    "vehicle_class": row["vehicle_class"],
                    "earlier_file": earlier["source_file"], "earlier_value": earlier["value"],
                    "later_file": f.path.name, "later_value": row["value"],
                })
            table[key] = {
                "country": "ZAF", "period": row["period"], "scenario": "shared",
                "vehicle_class": row["vehicle_class"], "province": row["province"],
                "value": row["value"], "unit": "vehicles", "source_file": f.path.name,
            }
    return table


def _annual(table: dict[tuple, dict]) -> tuple[list[dict], list[int]]:
    sums: dict[tuple[int, str], list] = {}
    for (period, vehicle_class, province), row in table.items():
        if province != "ZAF":
            continue
        entry = sums.setdefault((int(period[:4]), vehicle_class), [0, set()])
        entry[0] += row["value"]
        entry[1].add(period)
    annual, part_years = [], set()
    for (year, vehicle_class), (total, months) in sorted(sums.items()):
        if len(months) < 12:
            part_years.add(year)
            continue
        annual.append({"country": "ZAF", "period": year, "scenario": "shared",
                       "vehicle_class": vehicle_class, "value": total,
                       "unit": "vehicles", "months_reported": 12})
    return annual, sorted(part_years)


def _span(months: list[str]) -> str:
    return f"{months[0]} to {months[-1]} ({len(months)} months)" if months else "none"


def _write(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
