"""Stage the regulated transport cost to Gauteng from the department's yearly price tables.

Each year the department publishes one page for petrol (95 octane) and one for
diesel (0.05% sulphur) listing, month by month, the elements of the Gauteng
price: basic fuel price, levies, transport cost and margins. The "Transport
cost" column is the regulated allowance for moving the fuel from the coast to
Gauteng. The files are held in ``external/data/raw/fuel_price_margins/``:

    department-petrol-margins-<year>.pdf
    department-diesel-margins-<year>.pdf

``--fetch`` downloads every table listed on the department's archive page and
writes ``manifest.json``. Writes

    assumptions/<vintage>/reference/transport_cost_gauteng_department.csv

A month whose row is incomplete in the department's table is left out and
printed as a warning; nothing is filled in.

Run:
    python -m lfm.scripts.stage_fuel_price_margins --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

from lfm.config import Paths

REPO = Path(__file__).resolve().parents[3]
RAW = REPO / "external" / "data" / "raw" / "fuel_price_margins"
ARCHIVE = "https://www.dmpr.gov.za/Portals/0/Energy_Website/files/esources/petroleum/petroleum_arch.html"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# position of "Transport cost" among the numbers on a month's row
TRANSPORT_COLUMN = {"petrol": 5, "diesel": 6}
# the headings that must run in this order, with spaces removed (the tables break words across lines)
HEADING = {"petrol": "fundlevyroadaccidentfundtransportcost", "diesel": "pipelinelevyroadaccidentfundtransportcost"}
FIELDS = ["country", "period", "product", "scenario", "value", "unit", "source_file"]
_MONTH = re.compile(r"^\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(.*)$")
_NUMBER = re.compile(r"^\d+(\.\d+)?$")


def parse_transport_cost(text: str, product: str) -> tuple[dict[int, float], list[str]]:
    """``{month number: cents a litre}`` and the months that could not be read, from one yearly table."""
    flat = re.sub(r"\s+", "", text).lower()
    if HEADING[product] not in flat:
        raise ValueError("the table's columns are not in the expected order")
    column, out, problems = TRANSPORT_COLUMN[product], {}, []
    for line in text.splitlines():
        match = _MONTH.match(line)
        if not match:
            continue
        tokens = match.group(2).split()
        if len(tokens) > 1 and re.fullmatch(r"\d", tokens[0]) and re.fullmatch(r"\d{3}\.\d+", tokens[1]):
            tokens[:2] = [tokens[0] + tokens[1]]                      # "1 240.630" is 1240.630
        if not tokens:
            continue                                                  # a month not yet published
        month = MONTHS.index(match.group(1)) + 1
        numbers = [t for t in tokens if _NUMBER.match(t)]
        if len(numbers) <= column + 2 or numbers != tokens[:len(numbers)] or not 10 <= float(numbers[column]) <= 150:
            problems.append(match.group(1))
            continue
        out[month] = float(numbers[column])
    return out, problems


def fetch_all() -> None:
    RAW.mkdir(parents=True, exist_ok=True)

    def get(url: str) -> bytes:
        request = urllib.request.Request(url.replace(" ", "%20"), headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=90) as response:
            return response.read()

    page = get(ARCHIVE).decode("utf-8", "replace")
    files = []
    for link in sorted(set(re.findall(r'href="([^"]*[Mm]argin[^"]*\.pdf)"', page))):
        year = re.search(r"(20\d\d)", link)
        if link.startswith("http") or not year:
            continue                                                  # older tables sit on a retired address
        product = "diesel" if "iesel" in link else "petrol"
        name = f"department-{product}-margins-{year.group(1)}.pdf"
        url = ARCHIVE.rsplit("/", 1)[0] + "/" + link
        data = get(url)
        if not data.startswith(b"%PDF"):
            continue
        (RAW / name).write_bytes(data)
        files.append({"file": name, "publisher": "Department of Mineral and Petroleum Resources", "url": url, "bytes": len(data),
                      "sha256": hashlib.sha256(data).hexdigest()})
    manifest = {"purpose": "Regulated transport cost to Gauteng, month by month, from the department's yearly price tables",
                "page": ARCHIVE, "files": files}
    (RAW / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()
    if args.fetch:
        fetch_all()
    from pypdf import PdfReader

    rows = []
    for path in sorted(RAW.glob("department-*-margins-*.pdf")):
        product, year = path.stem.split("-")[1], int(path.stem.split("-")[-1])
        text = "\n".join((page.extract_text() or "") for page in PdfReader(str(path)).pages)
        values, problems = parse_transport_cost(text, product)
        if problems:
            print(f"warning: {path.name}: could not read {', '.join(problems)}; left out", file=sys.stderr)
        rows += [{"country": "ZAF", "period": f"{year}-{month:02d}", "product": product, "scenario": "shared", "value": value,
                  "unit": "cents per litre", "source_file": path.name} for month, value in sorted(values.items())]
    rows.sort(key=lambda r: (r["product"], r["period"]))
    out = Paths.default().vintage_dir(args.vintage) / "reference" / "transport_cost_gauteng_department.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows -> {out}; {rows[0]['period']} to {rows[-1]['period']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
