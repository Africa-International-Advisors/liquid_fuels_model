"""Read Stats SA's monthly activity releases: mining, manufacturing, land transport and prices.

Stats SA refuses scripted downloads, so the release zips are placed by hand (or
through a browser) in ``external/data/raw/statssa/`` from
statssa.gov.za > Time series data > Excel:

    P2041 Mining Production and sales(<yyyymm>).zip
    P3041.2 Manufacturing_ Production and sales(<yyyymm>).zip
    P7162 Land transport survey(<yyyymm>).zip
    P0141 - CPI(COICOP) from Jan 2008 (<yyyymm>).zip

The newest zip of each is read in place and written to:

    assumptions/<vintage>/timeseries/activity_statssa_monthly.csv
    assumptions/<vintage>/timeseries/activity_statssa_monthly.sources.yaml

CSV schema:
    country,period,scenario,series,value,unit,code,source_file
    ZAF,2026-07,shared,mining_volume_total,91.4,"index, 2019=100",FMP20000,P2041 ....zip

Series are listed in ``lfm.sources.statssa.MONTHLY_RELEASES``. They are activity
measures (output volume indices, tonnes carried, journeys, a price index), not
fuel volumes. Values are not seasonally adjusted.

Run:
    python -m lfm.scripts.fetch_statssa_monthly --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from datetime import date

import yaml

from lfm.config import Paths
from lfm.sources import statssa


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--offline", action="store_true",
                        help="accepted for symmetry with the other fetchers; this one never downloads")
    args = parser.parse_args()

    paths = Paths.default()
    raw_dir = paths.data_dir / "raw" / "statssa"
    out_dir = paths.vintage_dir(args.vintage) / "timeseries"
    if not out_dir.exists():
        sys.exit(f"vintage directory not found: {out_dir}")

    warnings: list[str] = []
    rows: list[dict] = []
    files: list[dict] = []
    for release, (pattern, member, wanted) in statssa.MONTHLY_RELEASES.items():
        path = statssa.latest_release_file(raw_dir, pattern) if raw_dir.exists() else None
        if path is None:
            warnings.append(f"{release}: no file matching '{pattern}' in external/data/raw/statssa/")
            continue
        try:
            series, problems = statssa.parse_monthly_series(
                statssa.read_release_zip(path, member), wanted)
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"{release}: could not read {path.name} ({exc})")
            continue
        warnings += [f"{release}: {p}" for p in problems]
        months = sorted({m for s in series for m in s["values"]})
        files.append({"release": release, "file": path.name,
                      "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                      "first_month": months[0] if months else None,
                      "latest_month": months[-1] if months else None,
                      "series": [s["name"] for s in series]})
        for s in series:
            for month in sorted(s["values"]):
                rows.append({"country": "ZAF", "period": month, "scenario": "shared",
                             "series": s["name"], "value": s["values"][month], "unit": s["unit"],
                             "code": s["code"], "source_file": path.name})
    if not rows:
        sys.exit("no Stats SA monthly release could be read: " + "; ".join(warnings))

    with (out_dir / "activity_statssa_monthly.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, lineterminator="\n", fieldnames=[
            "country", "period", "scenario", "series", "value", "unit", "code", "source_file"])
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "activity_statssa_monthly.sources.yaml").write_text(yaml.safe_dump({
        "publisher": "Statistics South Africa, monthly statistical releases",
        "page": "https://www.statssa.gov.za/?page_id=1847",
        "read_on": date.today().isoformat(),
        "how_obtained": "release zips placed by hand or through a browser; the site refuses "
                        "scripted downloads",
        "kept_in": "external/data/raw/statssa/",
        "not_fuel_volumes": "activity measures only; none is litres of fuel",
        "seasonal_adjustment": "none (actual indices and actual values)",
        "files": files,
        "warnings": warnings,
    }, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")

    for item in files:
        print(f"[fetch] Stats SA {item['release']}: {item['first_month']} to {item['latest_month']}; "
              f"{len(item['series'])} series", file=sys.stderr)
    for warning in warnings:
        print(f"[fetch]   WARNING {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
