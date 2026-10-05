"""Energy department statistics: fuel sales volumes and energy balances.

The department's energy pages moved when the department was split; the old
address (energy.gov.za) is often unavailable. The same pages are served from
the address in ``BASE_URL``. If that changes again, change it here only.

Two publications are read:

  - SA Fuel Sales Volume, "National Aggregated" workbook, one per year:
    litres sold per quarter for petrol, diesel, jet fuel, paraffin, furnace
    oil, LPG and aviation gasoline. This is the primary record of demand.
  - Commodity Flow and Energy Balance workbook, one per year: for each
    product, how much was produced, imported, exported and used by each
    sector, in kilolitres. This is the only official split of diesel between
    road, mining, industry, agriculture and the rest.

The workbooks have changed layout over the years. The readers below find the
rows and columns by their labels and codes, not by position, and report what
they could not read. Nothing is estimated.
"""
from __future__ import annotations

import hashlib
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

BASE_URL = "https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/"
SALES_INDEX = BASE_URL + "media_SAVolumes.html"
BALANCE_INDEX = BASE_URL + "Energy_Balances.html"
USER_AGENT = "Mozilla/5.0 (lfm source fetcher)"

LITRES_PER_KILOLITRE = 1000

# Product rows in the sales workbook, matched on the start of the row label.
SALES_PRODUCTS = {
    "petrol": re.compile(r"^petrol", re.IGNORECASE),
    "diesel": re.compile(r"^diesel", re.IGNORECASE),
    "jet": re.compile(r"^jet", re.IGNORECASE),
    "paraffin": re.compile(r"^paraffin", re.IGNORECASE),
    "fuel_oil": re.compile(r"^(furnace|fuel) oil", re.IGNORECASE),
    "lpg": re.compile(r"^lpg", re.IGNORECASE),
    "aviation_gasoline": re.compile(r"^aviation gas", re.IGNORECASE),
}

# Product columns in the energy balance, by the code printed above each column.
# Older workbooks (to 2020) and newer ones (2021 on) use different codes.
BALANCE_CODES = {
    "MOTORGAS": "petrol", "NONBIOGASO": "petrol",
    "GASDIES": "diesel", "NONBIODIES": "diesel",
    "JETKERO": "jet", "NONBIOJETK": "jet",
    "OTHKERO": "paraffin",
    "AVGAS": "aviation_gasoline",
}

# Flow rows we give a stable name to, so years with different wording line up.
# First match wins; a row that matches nothing keeps only its printed label.
BALANCE_FLOWS = (
    ("production", re.compile(r"^production", re.IGNORECASE)),
    ("imports", re.compile(r"^imports?\b", re.IGNORECASE)),
    ("exports", re.compile(r"^exports?\b", re.IGNORECASE)),
    ("statistical_difference", re.compile(r"^statistical diff", re.IGNORECASE)),
    ("electricity_plants", re.compile(
        r"^(electricity plant|main activity producer electricity)", re.IGNORECASE)),
    ("final_consumption", re.compile(r"^final consumption", re.IGNORECASE)),
    ("industry", re.compile(r"^industry", re.IGNORECASE)),
    ("mining", re.compile(r"^mining and quarrying", re.IGNORECASE)),
    ("construction", re.compile(r"^construction", re.IGNORECASE)),
    ("transport", re.compile(r"^transport( sector)?$", re.IGNORECASE)),
    ("road", re.compile(r"^road", re.IGNORECASE)),
    ("rail", re.compile(r"^rail", re.IGNORECASE)),
    ("commercial_public", re.compile(r"^commerc", re.IGNORECASE)),
    ("agriculture", re.compile(r"^agriculture", re.IGNORECASE)),
    ("residential", re.compile(r"^residential", re.IGNORECASE)),
)

_SALES_LINK = re.compile(r'href="([^"]+\.xlsx?)"', re.IGNORECASE)
_DISTRICT = re.compile(r"magisterial|dis+agg?|quaterly|quarterly-dis", re.IGNORECASE)
_BALANCE_LINK = re.compile(
    r'href="([^"]*?((?:19|20)\d{2})-Commodity-Flow-and-Energy-Balance\.xls[xm])"',
    re.IGNORECASE,
)
_FOOTNOTE = re.compile(r"\s*\(\d+\)\s*$")


@dataclass(frozen=True)
class SourceFile:
    """One downloaded workbook."""

    year: int
    url: str
    path: Path | None = None
    sha256: str | None = None


# --------------------------------------------------------------------------- #
# Finding and downloading

def discover_sales_files(index_html: str) -> list[SourceFile]:
    """National (not district-level) sales workbooks linked from the index page."""
    found: dict[int, str] = {}
    for href in _SALES_LINK.findall(index_html):
        name = href.rsplit("/", 1)[-1]
        year = re.match(r"((?:19|20)\d{2})", name)
        if not year or _DISTRICT.search(name):
            continue
        found.setdefault(int(year.group(1)), _absolute(href))
    return [SourceFile(year=y, url=found[y]) for y in sorted(found)]


def discover_balance_files(index_html: str) -> list[SourceFile]:
    """Energy balance workbooks linked from the index page."""
    found = {int(year): _absolute(href) for href, year in _BALANCE_LINK.findall(index_html)}
    return [SourceFile(year=y, url=found[y]) for y in sorted(found)]


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=240) as response:
        return response.read()


def download(source: SourceFile, raw_dir: Path) -> SourceFile:
    """Download a workbook into ``raw_dir`` unless it is already there."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    name = urllib.parse.unquote(source.url.rsplit("/", 1)[-1])
    path = raw_dir / name
    if not path.exists():
        data = fetch(source.url)
        if data[:2] not in (b"PK", b"\xd0\xcf"):  # xlsx/xlsm zip, or legacy xls
            raise ValueError(f"{source.url} did not return an Excel workbook")
        path.write_bytes(data)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return SourceFile(year=source.year, url=source.url, path=path, sha256=digest)


def _absolute(href: str) -> str:
    if href.startswith("http"):
        return href
    return BASE_URL + urllib.parse.quote(href.lstrip("./"))


# --------------------------------------------------------------------------- #
# Reading workbooks

def read_workbook(path: Path) -> dict[str, list[list]]:
    """Every sheet as rows of cell values. Handles .xls, .xlsx and .xlsm."""
    if path.suffix.lower() == ".xls":
        try:
            import xlrd
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise ImportError(
                'Reading .xls files needs xlrd. Install with: pip install -e ".[data]"'
            ) from exc
        book = xlrd.open_workbook(str(path))
        return {
            sheet.name: [sheet.row_values(r) for r in range(sheet.nrows)]
            for sheet in book.sheets()
        }

    import warnings

    import openpyxl

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        book = openpyxl.load_workbook(path, read_only=True, data_only=True)
        return {ws.title: [list(row) for row in ws.iter_rows(values_only=True)] for ws in book}


def parse_sales(sheets: dict[str, list[list]]) -> dict[str, list[float | None]]:
    """Quarterly litres per product: ``{product: [q1, q2, q3, q4]}``.

    Uses the first sheet that carries the product rows. A quarter with no
    figure comes back as ``None`` so a part-year file is visible as such.
    """
    for rows in sheets.values():
        found: dict[str, list[float | None]] = {}
        for row in rows:
            label = next((c for c in row if isinstance(c, str) and c.strip()), None)
            if label is None:
                continue
            product = _match(SALES_PRODUCTS, label.strip())
            if product is None or product in found:
                continue
            after = row[row.index(label) + 1:]
            numbers = [c for c in after if isinstance(c, (int, float)) and not isinstance(c, bool)]
            quarters: list[float | None] = [float(n) for n in numbers[:4]]
            quarters += [None] * (4 - len(quarters))
            found[product] = quarters
        if len(found) >= 3:
            return found
    return {}


def parse_balance(sheets: dict[str, list[list]]) -> tuple[list[dict], list[str]]:
    """Flows per product from an energy balance, in kilolitres.

    Returns ``(rows, warnings)``; each row is
    ``{"flow": printed label, "flow_key": stable name or "", "product", "value"}``.
    """
    for rows in sheets.values():
        header = _code_row(rows)
        if header is None:
            continue
        index, columns = header
        warnings: list[str] = []
        if not _unit_is_kilolitres(rows, index, columns):
            warnings.append("unit not confirmed as kilolitres")

        out: list[dict] = []
        used_keys: set[str] = set()
        for row in rows[index + 1:]:
            label = next((c for c in row[:4] if isinstance(c, str) and c.strip()), None)
            if label is None:
                continue
            flow = _FOOTNOTE.sub("", label.strip())
            key = _match(dict(BALANCE_FLOWS), flow) or ""
            if key in used_keys:
                key = ""  # a later row with the same wording is a sub-total elsewhere
            values = {
                product: row[col] for col, product in columns.items()
                if col < len(row) and isinstance(row[col], (int, float)) and row[col]
            }
            if not values:
                continue
            if key:
                used_keys.add(key)
            for product, value in values.items():
                out.append({
                    "flow": flow, "flow_key": key, "product": product, "value": float(value),
                })
        return out, warnings
    return [], ["no sheet with product codes found"]


def _code_row(rows: list[list]) -> tuple[int, dict[int, str]] | None:
    for index, row in enumerate(rows[:12]):
        columns = {
            col: BALANCE_CODES[cell.strip().upper()]
            for col, cell in enumerate(row)
            if isinstance(cell, str) and cell.strip().upper() in BALANCE_CODES
        }
        if "diesel" in columns.values():
            return index, columns
    return None


def _unit_is_kilolitres(rows: list[list], code_index: int, columns: dict[int, str]) -> bool:
    diesel_col = next(col for col, product in columns.items() if product == "diesel")
    for row in rows[:code_index]:
        if diesel_col < len(row) and isinstance(row[diesel_col], str):
            if row[diesel_col].strip().lower() == "kl":
                return True
        # Newer layout: one merged heading "Oil Products (Kl)" to the left of the column.
        headings = [
            (col, cell) for col, cell in enumerate(row)
            if isinstance(cell, str) and re.search(r"\((kl|kt)\)", cell, re.IGNORECASE)
        ]
        left = [cell for col, cell in headings if col <= diesel_col]
        if left and "(kl)" in left[-1].lower():
            return True
    return False


def _match(patterns: dict, label: str) -> str | None:
    for name, pattern in patterns.items():
        if pattern.search(label):
            return name
    return None


# --------------------------------------------------------------------------- #
# Fuel sales by province (district-level workbooks)
#
# The department also publishes sales by magisterial district. From 2013 the
# workbooks have one sheet per quarter in which each province appears as a
# row above its districts, so provincial totals can be read directly. Before
# 2013 the workbooks list districts only, with no province; those years are
# not read.

PROVINCES = {
    "easterncape": "EC", "freestate": "FS", "gauteng": "GP", "kwazulunatal": "KZN",
    "limpopo": "LP", "mpumalanga": "MP", "northwest": "NW", "northerncape": "NC",
    "westerncape": "WC",
}
FIRST_PROVINCIAL_YEAR = 2013

_DISTRICT_LINK = re.compile(r'href="([^"]+\.xlsx?)"', re.IGNORECASE)
_QUARTER_SHEET = re.compile(r"((?:19|20)\d{2})\s*Q\s*([1-4])", re.IGNORECASE)


def discover_district_files(index_html: str) -> list[SourceFile]:
    """Quarterly district-level workbooks from the years that carry province rows."""
    found: dict[int, str] = {}
    for href in _DISTRICT_LINK.findall(index_html):
        name = href.rsplit("/", 1)[-1]
        year = re.match(r"((?:19|20)\d{2})", name)
        if not year or not _DISTRICT.search(name) or int(year.group(1)) < FIRST_PROVINCIAL_YEAR:
            continue
        # A year can have an annual and a quarterly workbook; the quarterly one is wanted.
        if int(year.group(1)) in found and not re.search(r"quart|quat|q4", name, re.IGNORECASE):
            continue
        found[int(year.group(1))] = _absolute(href)
    return [SourceFile(year=y, url=found[y]) for y in sorted(found)]


def parse_provincial_sales(sheets: dict[str, list[list]]) -> tuple[list[dict], list[str]]:
    """Litres sold by province, product and quarter.

    Returns ``(rows, warnings)``; each row is
    ``{"year", "quarter", "province", "product", "value"}``. A sheet is used
    only if all nine provinces are found on it.
    """
    out: list[dict] = []
    warnings: list[str] = []
    for title, rows in sheets.items():
        match = _QUARTER_SHEET.search(title)
        if not match or "raw" in title.lower():
            continue
        year, quarter = int(match.group(1)), int(match.group(2))
        columns = _product_columns(rows)
        if not columns:
            warnings.append(f"sheet {title!r}: product headings not found")
            continue
        found: dict[str, list] = {}
        for row in rows:
            label = next((c for c in row[:3] if isinstance(c, str) and c.strip()), None)
            code = PROVINCES.get(_province_key(label)) if label else None
            if code and code not in found:
                found[code] = row
        if len(found) != len(PROVINCES):
            missing = sorted(set(PROVINCES.values()) - set(found))
            warnings.append(f"sheet {title!r}: provinces not found ({', '.join(missing)})")
            continue
        for code, row in found.items():
            for col, product in columns.items():
                value = row[col] if col < len(row) else None
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    out.append({"year": year, "quarter": quarter, "province": code,
                                "product": product, "value": float(value)})
    return out, warnings


def _product_columns(rows: list[list]) -> dict[int, str]:
    """Column positions of the products, from the row that names diesel and petrol."""
    for row in rows[:12]:
        columns: dict[int, str] = {}
        for col, cell in enumerate(row):
            if isinstance(cell, str):
                product = _match(SALES_PRODUCTS, cell.strip())
                if product is None and cell.strip().lower() == "aviation":
                    product = "jet"            # 2013 annual layout
                if product and product not in columns.values():
                    columns[col] = product
        if {"diesel", "petrol"} <= set(columns.values()):
            return columns
    return {}


# --------------------------------------------------------------------------- #
# Fuel price history
#
# One PDF per year, "Fuel Price History", with a row per month giving, in
# cents per litre: petrol 93 inland, petrol 95 coast, petrol 95 inland (retail),
# diesel 0.05% sulphur inland and coast (wholesale), illuminating paraffin
# coast and inland.

PRICE_INDEX = BASE_URL.replace("/media/", "/esources/petroleum/") + "petroleum_arch.html"
PRICE_SERIES = (
    "petrol_93_inland_retail", "petrol_95_coast_retail", "petrol_95_inland_retail",
    "diesel_005_inland_wholesale", "diesel_005_coast_wholesale",
    "paraffin_coast", "paraffin_inland",
)
_PRICE_LINK = re.compile(r'href="([^"]*?((?:19|20)\d{2})/[^"/]*history[^"]*\.pdf)"', re.IGNORECASE)
_MONTHS = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")
_MONTH_WORD = re.compile(
    r"\b(Jan|Feb|Mar|Apr|May|Jun|July|Jul|Aug|Sept|Sep|Oct|Nov|Dec)[a-z]*\b", re.IGNORECASE)
# A price in cents: "1936.00", "2295,00", and occasionally with no decimals ("1482").
_PRICE = re.compile(r"(?<![\d.,])\d{3,4}(?:[.,]\d{1,3})?(?![\d%])")


def discover_price_files(index_html: str) -> list[SourceFile]:
    found: dict[int, str] = {}
    base = PRICE_INDEX.rsplit("/", 1)[0] + "/"
    for href, year in _PRICE_LINK.findall(index_html):
        # Older links point at the retired address; the folder and file name still apply.
        tail = "/".join(href.rsplit("/", 2)[-2:])
        found[int(year)] = base + urllib.parse.quote(tail)
    return [SourceFile(year=y, url=found[y]) for y in sorted(found)]


def parse_price_history(text: str) -> tuple[dict[int, list[float]], list[str]]:
    """Monthly prices in cents per litre: ``({month number: [seven prices]}, warnings)``.

    The seven prices are in the order of ``PRICE_SERIES``. A month the
    department has not yet filled in is left out; a month with some other
    number of prices is reported and left out.
    """
    body = text[text.lower().find("jan"):] if "jan" in text.lower() else ""
    marks = [m for m in _MONTH_WORD.finditer(body)]
    out: dict[int, list[float]] = {}
    warnings: list[str] = []
    for i, mark in enumerate(marks):
        month = _MONTHS.index(mark.group(1).lower()[:3]) + 1
        if month in out:
            continue
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        chunk = body[mark.end():end]
        if "ytd" in chunk.lower():
            chunk = chunk[:chunk.lower().find("ytd")]
        prices = [float(p.replace(",", ".")) for p in _PRICE.findall(chunk)]
        if not prices:
            continue
        if len(prices) != len(PRICE_SERIES):
            warnings.append(f"month {month}: {len(prices)} prices found, expected "
                            f"{len(PRICE_SERIES)}")
            continue
        out[month] = prices
    return out, warnings


def _province_key(label: str) -> str:
    """'Limpopo Province' / 'KwaZulu Natal' / 'NorthWest' -> a key of PROVINCES."""
    return re.sub(r"[^a-z]", "", label.lower()).replace("province", "")
