"""Airports Company South Africa (ACSA) group traffic statistics.

ACSA publishes two one-page PDFs at fixed addresses, covering its nine
airports combined, by month, for each financial year since 2012/13:

    passengers          ACSA AERONAUTICAL PASSENGER GROUP STATS.pdf
    aircraft movements  ACSA AERONAUTICAL MOVEMENT  GROUP STATS.pdf

Each has five sections (International, Regional, Domestic, Unscheduled and
Total). Every section has twelve month rows, April to March, and a year
total. Every row has three blocks of one figure per financial year:
arrivals, departures, and the two together.

The figures cover ACSA airports only. Lanseria and other non-ACSA airports
are not included, and neither file reports cargo.

Reading the tables. Thousands are printed with a space, and in places two
neighbouring figures run together ("11 935 88611 666 804"). Each row checks
itself: arrivals plus departures must equal the total for every year. A row
is used only if it splits into the right number of figures and passes that
check; otherwise it is reported and left out. Nothing is estimated.
"""
from __future__ import annotations

import hashlib
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path

URLS = {
    "passengers": "https://www.airports.co.za/StatisticsLib/"
                  "ACSA%20AERONAUTICAL%20PASSENGER%20GROUP%20STATS.pdf",
    "aircraft_movements": "https://www.airports.co.za/StatisticsLib/"
                          "ACSA%20AERONAUTICAL%20MOVEMENT%20%20GROUP%20STATS.pdf",
}
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) lfm source fetcher"

SECTIONS = ("international", "regional", "domestic", "unscheduled", "total")
DIRECTIONS = ("arrival", "departure", "total")
# Rows run April (01) to March (12): the first nine months fall in the
# financial year's first calendar year, the last three in its second.
MONTH_OF_ROW = {1: 4, 2: 5, 3: 6, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11, 9: 12, 10: 1, 11: 2, 12: 3}

_FINANCIAL_YEAR = re.compile(r"FY(\d{2})/(\d{2})")
_MONTH_ROW = re.compile(r"(\d{2})-[A-Za-z]+\s{2,}(\S.*)$")
_CELL_SPLIT = re.compile(r"\s{2,}")


@dataclass(frozen=True)
class SourceFile:
    measure: str
    url: str
    path: Path | None = None
    sha256: str | None = None


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:
        return response.read()


def download(measure: str, raw_dir: Path, *, refresh: bool = True) -> SourceFile:
    """Download a file. The address never changes, so it is fetched afresh each time."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"acsa-group-{measure}.pdf"
    if refresh:
        data = fetch(URLS[measure])
        if not data.startswith(b"%PDF"):
            raise ValueError(f"{URLS[measure]} did not return a PDF")
        path.write_bytes(data)
    if not path.exists():
        raise FileNotFoundError(path)
    return SourceFile(measure=measure, url=URLS[measure], path=path,
                      sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def pdf_layout_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            'Reading the PDFs needs pypdf. Install with: pip install -e ".[data]"'
        ) from exc

    import logging

    logging.getLogger("pypdf").setLevel(logging.ERROR)
    return "\n".join(
        page.extract_text(extraction_mode="layout") or "" for page in PdfReader(str(path)).pages
    )


# --------------------------------------------------------------------------- #

def parse(text: str) -> tuple[list[dict], list[str]]:
    """Monthly figures: ``(rows, warnings)``.

    Each row is ``{"period": "2025-04", "financial_year": "FY25/26",
    "flight_type", "direction", "value"}``.
    """
    years = _financial_years(text)
    if not years:
        return [], ["financial year headings not found"]
    n = len(years)

    rows: list[dict] = []
    warnings: list[str] = []
    section = -1
    previous_row = 13
    for line in text.splitlines():
        match = _MONTH_ROW.search(line)
        if not match:
            continue
        row_number = int(match.group(1))
        if row_number not in MONTH_OF_ROW:
            continue
        if row_number < previous_row:
            section += 1        # the months have started again: next section
        previous_row = row_number
        if section >= len(SECTIONS):
            warnings.append("more sections than expected; extra rows ignored")
            break
        flight_type = SECTIONS[section]
        figures = _figures(match.group(2))
        label = f"{flight_type} row {row_number:02d}"
        if figures is None or len(figures) != 3 * n:
            warnings.append(f"{label}: could not be split into {3 * n} figures")
            continue
        arrivals, departures, totals = figures[:n], figures[n:2 * n], figures[2 * n:]
        if any(a + d != t for a, d, t in zip(arrivals, departures, totals)):
            warnings.append(f"{label}: arrivals and departures do not add up to the total")
            continue
        month = MONTH_OF_ROW[row_number]
        for i, (start_year, name) in enumerate(years):
            calendar_year = start_year if month >= 4 else start_year + 1
            for direction, block in zip(DIRECTIONS, (arrivals, departures, totals)):
                rows.append({
                    "period": f"{calendar_year}-{month:02d}", "financial_year": name,
                    "flight_type": flight_type, "direction": direction, "value": block[i],
                })
    if section + 1 < len(SECTIONS):
        warnings.append(f"only {section + 1} of {len(SECTIONS)} sections found")
    return rows, warnings


def drop_unreported_months(rows: list[dict]) -> tuple[list[dict], str | None]:
    """Remove the months ACSA has not yet filled in.

    The current financial year is printed with zeros for months still to
    come. Everything after the last month with any traffic is dropped.
    Returns ``(rows, last_reported_month)``.
    """
    reported = [r["period"] for r in rows
                if r["flight_type"] == "total" and r["direction"] == "total" and r["value"] > 0]
    if not reported:
        return [], None
    last = max(reported)
    return [r for r in rows if r["period"] <= last], last


def calendar_years(rows: list[dict]) -> list[dict]:
    """Calendar-year sums, for years with all twelve months."""
    sums: dict[tuple, list] = {}
    for row in rows:
        key = (int(row["period"][:4]), row["flight_type"], row["direction"])
        entry = sums.setdefault(key, [0, set()])
        entry[0] += row["value"]
        entry[1].add(row["period"])
    return [
        {"period": year, "flight_type": flight_type, "direction": direction, "value": total}
        for (year, flight_type, direction), (total, months) in sorted(sums.items())
        if len(months) == 12
    ]


def _financial_years(text: str) -> list[tuple[int, str]]:
    """Financial years in heading order, as (first calendar year, label)."""
    for line in text.splitlines():
        found = _FINANCIAL_YEAR.findall(line)
        if len(found) >= 6 and len(found) % 3 == 0:
            n = len(found) // 3
            return [(2000 + int(a), f"FY{a}/{b}") for a, b in found[:n]]
    return []


def _figures(text: str) -> list[int] | None:
    """Figures from a row whose columns are two or more spaces apart.

    Within a cell, a figure is up to three digits followed by groups of
    exactly three. A longer group means two figures have run together: its
    first three digits end one figure and the rest begins the next.
    """
    out: list[int] = []
    for cell in _CELL_SPLIT.split(text.strip()):
        tokens = cell.split()
        if not tokens or not all(t.isdigit() for t in tokens):
            return None
        current = tokens[0]
        if len(current) > 3:
            return None
        for token in tokens[1:]:
            if len(token) < 3:
                return None
            current += token[:3]
            if len(token) > 3:
                out.append(int(current))
                current = token[3:]
                if len(current) > 3:
                    return None
        out.append(int(current))
    return out
