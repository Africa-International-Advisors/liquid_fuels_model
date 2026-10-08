"""Stage South Africa's JODI oil submissions as annual figures by product and flow.

Reads every file in ``external/data/raw/jodi/`` (South Africa's rows of JODI's
annual files) and writes

    assumptions/<vintage>/timeseries/oil_balance_jodi.csv

``--fetch 2017 2022`` first downloads those years from JODI and keeps South
Africa's rows as ``jodi-secondary-zaf-<first>-<last>.csv``.

Run:
    python -m lfm.scripts.stage_jodi --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from lfm.config import Paths
from lfm.sources import jodi

REPO = Path(__file__).resolve().parents[3]
RAW = REPO / "external" / "data" / "raw" / "jodi"
FIELDS = ["country", "period", "scenario", "product", "flow", "value", "unit", "basis", "months_reported",
          "assessment_code", "source_file"]


def read_raw(folder: Path) -> list[dict]:
    """All monthly rows held, each tagged with its file. A month in two files is taken from the later file."""
    seen: dict[tuple, dict] = {}
    for path in sorted(folder.glob("*.csv")):
        with path.open(encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                row["source_file"] = path.name
                seen[(row["REF_AREA"], row["TIME_PERIOD"], row["ENERGY_PRODUCT"], row["FLOW_BREAKDOWN"],
                      row["UNIT_MEASURE"])] = row
    return list(seen.values())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--fetch", nargs=2, type=int, metavar=("FIRST", "LAST"))
    args = parser.parse_args()

    if args.fetch:
        first, last = args.fetch
        parts = [jodi.fetch_country_rows(year) for year in range(first, last + 1)]
        text = parts[0] + "".join(part.split("\n", 1)[1] for part in parts[1:])
        (RAW / f"jodi-secondary-zaf-{first}-{last}.csv").write_text(text, encoding="utf-8", newline="\n")

    raw = read_raw(RAW)
    file_of = {(int(r["TIME_PERIOD"][:4])): r["source_file"] for r in raw}
    rows = jodi.annual(raw)
    for row in rows:
        row["source_file"] = file_of[row["period"]]
    out = Paths.default().vintage_dir(args.vintage) / "timeseries" / "oil_balance_jodi.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    years = sorted({r["period"] for r in rows})
    print(f"wrote {len(rows)} rows -> {out}; {years[0]}-{years[-1]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
