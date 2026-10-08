"""Stage the department's regulated transport differentials by fuel pricing zone.

The regulated price of petrol and diesel in each of the Magisterial District
Zones is the coastal basic price plus a zone differential: the allowance for
moving the fuel from the coast to that zone by the pipeline and road networks.
The department publishes the differentials in two places held in
``external/data/raw/routes_access_20261008/``:

    department-diesel-wholesale-by-zone-2024-04.pdf       diesel 0.05%, effective 3 April 2024
    department-transport-cost-by-zone-2014-04-02.xls      petrol and diesel, effective 2 April 2014,
                                                          and the magisterial districts in each zone

Writes, under ``assumptions/<vintage>/reference/``:

    zone_differentials_department.csv     one row per zone, product and effective date, cents a litre
    zone_districts_department.csv         one row per magisterial district: zone and province (2014 list)

A differential is a regulated allowance in the price. It is not what a haulier
or Transnet charges a shipper.

Run:
    python -m lfm.scripts.stage_zone_differentials --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

from lfm.config import Paths

REPO = Path(__file__).resolve().parents[3]
RAW = REPO / "external" / "data" / "raw" / "routes_access_20261008"
DIESEL_2024 = "department-diesel-wholesale-by-zone-2024-04.pdf"
ZONES_2014 = "department-transport-cost-by-zone-2014-04-02.xls"

_ROW = re.compile(r"^\s*(\d{1,2}[ABCJ])\s+(?:[A-Za-z ]+?\s+)?(?:(\d[\d,]*\.\d+)\s+)?(\d+\.\d+)\s+(\d{4}\.\d+)\s*$", re.M)


def zone_code(text: str) -> str:
    """``1A`` and ``01A`` both become ``01A``."""
    return text.strip().upper().zfill(3)


def parse_diesel_2024(text: str) -> list[dict]:
    """Zone differentials from the first product block (diesel 0.05% sulphur) of the April 2024 wholesale price list.

    Each row is checked: the zone's wholesale price must equal the block's basic price plus the differential.
    """
    block = text[: text.index("0.005%")] if "0.005%" in text else text
    out, basic = [], None
    for zone, base, differential, wholesale in _ROW.findall(block):
        if base:
            basic = float(base.replace(",", ""))
        if basic is None:
            raise ValueError(f"no basic price before zone {zone}")
        if abs(basic + float(differential) - float(wholesale)) > 0.06:
            raise ValueError(f"zone {zone}: {basic} + {differential} is not {wholesale}")
        out.append({"zone": zone_code(zone), "product": "diesel", "effective": "2024-04-03", "value": float(differential)})
    return out


def parse_zones_2014(differentials: list[list], districts: list[list]) -> tuple[list[dict], list[dict]]:
    """Rows of the two sheets of the 2014 workbook, as ``(zone differentials, districts by zone)``."""
    rates = []
    for row in differentials:
        row = [cell for cell in row if cell != ""]          # the sheet leaves blank columns between the products
        if len(row) >= 4 and isinstance(row[0], str) and re.fullmatch(r"\d{2}[ABCJ]", row[0].strip()) and isinstance(row[1], float):
            for product, column in (("petrol", 1), ("diesel", 3)):
                if zone_code(row[column - 1]) != zone_code(row[0]):
                    raise ValueError(f"zone columns disagree in row {row[:4]}")
                rates.append({"zone": zone_code(row[0]), "product": product, "effective": "2014-04-02", "value": round(row[column], 1)})
    places = [{"zone": zone_code(row[0]), "magisterial_district": " ".join(str(row[1]).split()), "province": str(row[2]).strip()}
              for row in ([cell for cell in raw if cell != ""] for raw in districts)
              if len(row) >= 3 and isinstance(row[0], str) and re.fullmatch(r"\d{2}[ABCJ]", row[0].strip())]
    return rates, places


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    args = parser.parse_args()
    import xlrd
    from pypdf import PdfReader

    text = "\n".join((page.extract_text() or "") for page in PdfReader(str(RAW / DIESEL_2024)).pages)
    book = xlrd.open_workbook(str(RAW / ZONES_2014))
    sheet = lambda name: [book.sheet_by_name(name).row_values(i) for i in range(book.sheet_by_name(name).nrows)]  # noqa: E731
    rates_2014, places = parse_zones_2014(sheet("Zone differentials"), sheet("MD by Zone"))
    rates = parse_diesel_2024(text) + rates_2014
    for row in rates:
        row.update(country="ZAF", scenario="shared", unit="cents per litre",
                   source_file=DIESEL_2024 if row["effective"].startswith("2024") else ZONES_2014)
    for row in places:
        row.update(country="ZAF", list_date="2014-04-02", source_file=ZONES_2014)
    rates.sort(key=lambda r: (r["effective"], r["product"], r["zone"][-1], r["zone"]))

    reference = Paths.default().vintage_dir(args.vintage) / "reference"
    for name, fields, rows in (
            ("zone_differentials_department.csv", ["country", "zone", "product", "effective", "scenario", "value", "unit", "source_file"], rates),
            ("zone_districts_department.csv", ["country", "zone", "magisterial_district", "province", "list_date", "source_file"], places)):
        with (reference / name).open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    zones_2024 = {r["zone"] for r in rates if r["effective"].startswith("2024")}
    print(f"wrote {len(rates)} differentials ({len(zones_2024)} zones for 2024) and {len(places)} districts -> {reference}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
