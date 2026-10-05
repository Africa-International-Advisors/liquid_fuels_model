"""Fuels Industry Association of South Africa (FIASA, formerly SAPIA) annual reports.

The statistics section of each annual report carries two tables we use:

  - "Consumption of petroleum products in South Africa" (million litres):
    petrol, diesel, paraffin, jet fuel, fuel oil, LPG. Attributed by the
    report to the energy department.
  - "Petroleum products imports and exports" (million litres; LPG in
    kilotonnes): petrol, diesel, kerosene, LPG. Attributed to SARS and the
    energy department. Kerosene = illuminating paraffin + jet fuel + dual
    purpose kerosene, so it is NOT a jet fuel series.

Each report covers roughly the last ten years, so consecutive reports
overlap. That overlap is used here rather than thrown away:

  - the most recent report wins for any year it covers;
  - a year whose value differs between reports is logged as a REVISION;
  - a final-year row that is identical to the year before across every
    product is treated as CARRIED OVER (not actually reported) and dropped.
    The 2025 report does this: its 2025 consumption row repeats 2024.

Nothing here is tuned to model output. If a table or a row cannot be read
it is reported as a warning; a value is never guessed.
"""
from __future__ import annotations

import hashlib
import math
import re
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

INDEX_URL = "https://fuelsindustry.org.za/publications/annual-reports/"
USER_AGENT = "Mozilla/5.0 (lfm source fetcher)"

CONSUMPTION_HEADING = "Consumption of petroleum products"
TRADE_HEADING = "Petroleum products imports and exports"

CONSUMPTION_PRODUCTS = ("petrol", "diesel", "paraffin", "jet", "fuel_oil", "lpg")
TRADE_PRODUCTS = ("petrol", "diesel", "kerosene", "lpg")
TRADE_COLUMNS = tuple(
    (flow, product) for flow in ("import", "export") for product in TRADE_PRODUCTS
)

MILLION = 1_000_000

# The report year appears in every report link, whatever folder it sits in.
_REPORT_LINK = re.compile(
    r'href="([^"]*annual-report-((?:19|20)\d{2})\.pdf)"', re.IGNORECASE,
)
# A table row with column gaps preserved: a year, then cells two or more spaces apart.
_LAYOUT_ROW = re.compile(r"^\s*((?:19|20)\d{2})\s{2,}(\S.*?)\s*$")
_CELL_SPLIT = re.compile(r"\s{2,}")
# The same row in plain text: a year, then single-spaced digit groups or dashes.
_PLAIN_ROW = re.compile(
    r"^\s*((?:19|20)\d{2})((?:\s+(?:\d+(?:[.,]\d+)?|[-–—]))+)\s*\*?\s*$"
)
_DECIMAL = re.compile(r"^\d+[.,]\d+$")
_MISSING = {"-", "–", "—", ""}
# How much closer (summed log-ratio) the best column grouping must be than the next best.
_MARGIN = 2.0


@dataclass(frozen=True)
class Report:
    """One annual report: which year it is for and where it lives."""

    year: int
    url: str
    path: Path | None = None
    sha256: str | None = None


@dataclass(frozen=True)
class PageText:
    """One PDF page read two ways (see "Reading tables" below)."""

    plain: str
    layout: str


@dataclass
class Extraction:
    """Result of combining the tables from several reports."""

    rows: list[dict] = field(default_factory=list)
    revisions: list[dict] = field(default_factory=list)
    carried_over: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def latest_year(self) -> int | None:
        return max((r["period"] for r in self.rows), default=None)


# --------------------------------------------------------------------------- #
# Finding and downloading reports

def discover_reports(index_html: str) -> list[Report]:
    """Every annual report linked from the index page, newest first."""
    found: dict[int, str] = {}
    for href, year in _REPORT_LINK.findall(index_html):
        url = href if href.startswith("http") else "https://fuelsindustry.org.za" + href
        found[int(year)] = url
    return [Report(year=y, url=found[y]) for y in sorted(found, reverse=True)]


def fetch_index(url: str = INDEX_URL) -> str:
    return _get(url).decode("utf-8", errors="replace")


def download(report: Report, raw_dir: Path) -> Report:
    """Download a report into ``raw_dir`` unless it is already there."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"annual-report-{report.year}.pdf"
    if not path.exists():
        data = _get(report.url)
        if not data.startswith(b"%PDF"):
            raise ValueError(f"{report.url} did not return a PDF")
        path.write_bytes(data)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return Report(year=report.year, url=report.url, path=path, sha256=digest)


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=240) as response:
        return response.read()


# --------------------------------------------------------------------------- #
# Reading tables out of a report
#
# The reports print thousands with a space ("12 946"), and PDF text
# extraction gives no reliable way to tell that space from the gap between
# two columns. So each row is read twice:
#
#   plain  : "2021 9 302 12 946 1 078 1 048 491 308" — digits always right,
#            column boundaries unknown;
#   layout : column gaps preserved as runs of spaces — boundaries usually
#            right, but some reports break digits apart ("1  07 8").
#
# A row is accepted from the layout reading only when it has the expected
# number of cells AND its digits equal the plain reading's digits. Otherwise
# the plain digits are grouped into columns by picking the grouping closest
# to a reference row: the same year in another report, or the nearest year
# already read. If two groupings are about equally close the row is dropped
# with a warning.

def pdf_pages(path: Path) -> list[PageText]:
    """Text of every page, in both extraction modes (needs ``pypdf``)."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            'Reading the reports needs pypdf. Install with: pip install -e ".[data]"'
        ) from exc

    import logging

    logging.getLogger("pypdf").setLevel(logging.ERROR)
    pages: list[PageText] = []
    for page in PdfReader(str(path)).pages:
        texts = []
        for mode in ("plain", "layout"):
            try:
                texts.append(page.extract_text(extraction_mode=mode) or "")
            except Exception:  # noqa: BLE001 - one unreadable page must not stop the rest
                texts.append("")
        pages.append(PageText(plain=texts[0], layout=texts[1]))
    return pages


def read_table(
    pages: list[PageText], heading: str, n_values: int,
    reference: dict[int, list] | None = None,
) -> tuple[dict[int, list], list[str]]:
    """Rows of the table under ``heading`` as ``({year: [values]}, warnings)``.

    Values are in the report's own units; a dash comes back as ``None``.
    ``reference`` holds rows already read from other reports. It is used only
    to place column boundaries, never to supply a value.
    """
    reference = dict(reference or {})
    warnings: list[str] = []
    for page in pages:
        start = page.plain.find(heading)
        if start < 0:
            continue
        tokens = _plain_rows(page.plain[start:], n_values)
        if not tokens:
            continue  # the contents page also carries the heading
        layout = _layout_rows(page.layout[max(page.layout.find(heading), 0):], n_values)

        rows: dict[int, list] = {}
        pending: list[int] = []
        for year, row_tokens in tokens.items():
            cells = layout.get(year)
            if cells is not None and _digits(cells) == "".join(row_tokens):
                rows[year] = [_number(c) for c in cells]
            else:
                pending.append(year)

        for year in pending:
            anchor = reference.get(year) or _nearest({**reference, **rows}, year)
            if anchor is None:
                warnings.append(f"{year}: columns could not be placed (no reference row)")
                continue
            choice = _closest_grouping(tokens[year], n_values, anchor)
            if choice is None:
                warnings.append(f"{year}: columns could not be placed unambiguously")
                continue
            rows[year] = choice
        return rows, warnings
    return {}, ["table not found"]


def _plain_rows(text: str, n_values: int) -> dict[int, list[str]]:
    """Consecutive ``year token token ...`` lines following the heading."""
    rows: dict[int, list[str]] = {}
    for line in text.splitlines():
        match = _PLAIN_ROW.match(line.replace(" ", " "))
        if not match:
            continue
        year = int(match.group(1))
        tokens = match.group(2).split()
        if rows and year <= max(rows):
            break  # the years start again: that is the next table
        if not _groupings(tokens, n_values):
            if rows:
                break
            continue
        rows[year] = tokens
    return rows


def _layout_rows(text: str, n_values: int) -> dict[int, list[str]]:
    rows: dict[int, list[str]] = {}
    for line in text.splitlines():
        match = _LAYOUT_ROW.match(line)
        if not match:
            continue
        cells = _CELL_SPLIT.split(match.group(2))
        year = int(match.group(1))
        if len(cells) == n_values and year not in rows:
            rows[year] = cells
    return rows


def _digits(cells: list[str]) -> str:
    return "".join(c.replace(" ", "") for c in cells)


def _groupings(tokens: list[str], n_values: int) -> list[list]:
    """Every way to read ``tokens`` as ``n_values`` numbers.

    A number is one token of up to three digits, optionally followed by one
    three-digit token (the thousands group), or a single longer token.
    """
    out: list[list] = []

    def walk(i: int, acc: list) -> None:
        if len(acc) > n_values:
            return
        if i == len(tokens):
            if len(acc) == n_values:
                out.append(acc)
            return
        token = tokens[i]
        if token in _MISSING:
            walk(i + 1, acc + [None])
            return
        if _DECIMAL.match(token):
            walk(i + 1, acc + [float(token.replace(",", "."))])
            return
        if not token.isdigit():
            return
        if len(token) > 1 and token[0] == "0":
            return  # a number cannot start with a zero-padded group
        walk(i + 1, acc + [float(token)])
        if len(token) <= 3 and i + 1 < len(tokens):
            nxt = tokens[i + 1]
            if nxt.isdigit() and len(nxt) == 3:
                walk(i + 2, acc + [float(token + nxt)])

    walk(0, [])
    return out


def _closest_grouping(tokens: list[str], n_values: int, anchor: list) -> list | None:
    """The grouping nearest ``anchor`` in ratio terms, if it is clearly nearest."""
    scored = sorted(
        ((_distance(candidate, anchor), candidate)
         for candidate in _groupings(tokens, n_values)),
        key=lambda item: item[0],
    )
    if not scored:
        return None
    if len(scored) > 1 and scored[1][0] - scored[0][0] < _MARGIN:
        return None
    return scored[0][1]


def _distance(candidate: list, anchor: list) -> float:
    total = 0.0
    for value, ref in zip(candidate, anchor):
        if value is None or ref is None or value <= 0 or ref <= 0:
            continue
        total += abs(math.log(value / ref))
    return total


def _nearest(rows: dict[int, list], year: int) -> list | None:
    if not rows:
        return None
    return rows[min(rows, key=lambda y: abs(y - year))]


def _number(cell: str) -> float | None:
    cell = cell.strip().rstrip("*")
    if cell in _MISSING:
        return None
    return float(cell.replace(" ", "").replace(",", "."))


# --------------------------------------------------------------------------- #
# Combining reports

def combine(
    tables: dict[int, dict[int, list]], columns: tuple, *, tolerance: float = 0.5,
) -> Extraction:
    """Merge one table read from several reports.

    ``tables`` maps report year -> ``{data year: [values]}``; ``columns``
    labels the values. The newest report wins. ``tolerance`` is in the
    table's units (million litres) and only decides what counts as a
    revision worth logging.
    """
    out = Extraction()
    cleaned: dict[int, dict[int, list]] = {}

    for report_year in sorted(tables):
        rows = dict(tables[report_year])
        if not rows:
            continue
        last = max(rows)
        if last - 1 in rows and rows[last] == rows[last - 1]:
            out.carried_over.append({"report": report_year, "period": last})
            del rows[last]
        cleaned[report_year] = rows

    best: dict[tuple, tuple[int, float]] = {}
    for report_year in sorted(cleaned):
        for year, values in cleaned[report_year].items():
            for column, value in zip(columns, values):
                if value is None:
                    continue
                key = (year, column)
                if key in best and abs(best[key][1] - value) > tolerance:
                    out.revisions.append({
                        "period": year,
                        "column": column,
                        "earlier_report": best[key][0],
                        "earlier_value": best[key][1],
                        "later_report": report_year,
                        "later_value": value,
                    })
                best[key] = (report_year, value)

    years = sorted({year for year, _ in best})
    for column in columns:
        have = {year for year, col in best if col == column}
        gaps = [y for y in range(years[0], years[-1] + 1) if y not in have] if years else []
        if gaps:
            label = "/".join(column) if isinstance(column, tuple) else column
            out.warnings.append(f"{label}: no figure for {', '.join(map(str, gaps))}")

    for (year, column), (report_year, value) in sorted(
        best.items(), key=lambda item: (str(item[0][1]), item[0][0]),
    ):
        out.rows.append({
            "period": year, "column": column,
            "value": value, "source_report": report_year,
        })
    return out
