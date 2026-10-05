"""Economy: GDP, GDP per capita, population and the official growth forecast.

History and population outlook come from the World Bank's data service,
which republishes Statistics South Africa's national accounts and the United
Nations' population estimates and projections in a stable, machine-readable
form. The growth forecast comes from the National Treasury's Budget Review
or Medium Term Budget Policy Statement, whichever is more recent.

    World Bank indicator        what it is
    NY.GDP.MKTP.KN              GDP, constant local currency (rand)
    NY.GDP.MKTP.CN              GDP, current rand (used only to find the base year)
    NY.GDP.PCAP.KN              GDP per capita, constant rand
    SP.POP.TOTL                 population; with source 40, projections

The constant-price base year is not stated by the service, so it is found
from the data: it is the year in which constant and current GDP coincide.

Treasury publishes three forecast years. Nothing here extends the forecast
beyond what is published; any later years are a model assumption.
"""
from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path

WORLD_BANK_URL = (
    "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
    "?format=json&per_page=200&date={start}:{end}"
)
PROJECTIONS_SOURCE = 40   # World Bank "Population estimates and projections"
PROJECTIONS_LAST_YEAR = 2050
TREASURY_URLS = (
    # (label, address); {year} is the publication year. Later in the year wins.
    ("mtbps", "https://www.treasury.gov.za/documents/mtbps/{year}/mtbps/Chapter%202.pdf"),
    ("budget-review",
     "https://www.treasury.gov.za/documents/national%20budget/{year}/review/Chapter%202.pdf"),
)
USER_AGENT = "Mozilla/5.0 (lfm source fetcher)"

SERIES = {
    "gdp": ("NY.GDP.MKTP.KN", "rand, constant prices"),
    "gdp_per_capita": ("NY.GDP.PCAP.KN", "rand per person, constant prices"),
    "population": ("SP.POP.TOTL", "persons"),
}
CURRENT_PRICE_GDP = "NY.GDP.MKTP.CN"

_TABLE_TITLE = "Macroeconomic performance and projections"
_GROWTH_ROW = re.compile(r"Real GDP growth\s+((?:-?\d+(?:\.\d+)?\s+){2,}-?\d+(?:\.\d+)?)")
_YEAR_ROW = re.compile(r"((?:20\d{2}\s+){2,}20\d{2})")


@dataclass(frozen=True)
class TreasuryDocument:
    label: str
    year: int
    url: str
    path: Path | None = None
    sha256: str | None = None


# --------------------------------------------------------------------------- #
# World Bank

def world_bank_url(indicator: str, start: int, end: int, *, country: str = "ZAF",
                   source: int | None = None) -> str:
    url = WORLD_BANK_URL.format(country=country, indicator=indicator, start=start, end=end)
    return url + (f"&source={source}" if source else "")


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def parse_world_bank(payload: bytes | str) -> tuple[dict[int, float], str | None]:
    """``({year: value}, last_updated)`` from a World Bank indicator response.

    Years the service has no figure for are left out.
    """
    data = json.loads(payload)
    if not isinstance(data, list) or len(data) < 2 or not data[1]:
        return {}, None
    values = {
        int(row["date"]): float(row["value"])
        for row in data[1] if row.get("value") is not None
    }
    return values, data[0].get("lastupdated")


def base_year(constant: dict[int, float], current: dict[int, float],
              *, tolerance: float = 0.001) -> int | None:
    """The year constant-price and current-price GDP coincide, if exactly one does."""
    matches = [
        year for year in sorted(set(constant) & set(current))
        if abs(constant[year] - current[year]) <= tolerance * current[year]
    ]
    return matches[0] if len(matches) == 1 else None


# --------------------------------------------------------------------------- #
# National Treasury

def treasury_candidates(this_year: int) -> list[TreasuryDocument]:
    """Documents to try, most recent first: this year's, then last year's."""
    out = []
    for year in (this_year, this_year - 1):
        for label, pattern in TREASURY_URLS:
            out.append(TreasuryDocument(label=label, year=year, url=pattern.format(year=year)))
    return out


def download_treasury(document: TreasuryDocument, raw_dir: Path) -> TreasuryDocument | None:
    """Download a chapter if it exists; ``None`` if Treasury has not published it."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{document.label}-{document.year}-chapter-2.pdf"
    if not path.exists():
        try:
            data = fetch(document.url)
        except Exception:  # noqa: BLE001 - not published yet is the normal case
            return None
        if not data.startswith(b"%PDF"):
            return None   # the site answers missing documents with an error page
        path.write_bytes(data)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return TreasuryDocument(label=document.label, year=document.year, url=document.url,
                            path=path, sha256=digest)


def pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            'Reading the PDFs needs pypdf. Install with: pip install -e ".[data]"'
        ) from exc

    import logging

    logging.getLogger("pypdf").setLevel(logging.ERROR)
    return "\n".join((page.extract_text() or "") for page in PdfReader(str(path)).pages)


def parse_treasury_growth(text: str, publication_year: int) -> tuple[list[dict], list[str]]:
    """Real GDP growth by year from the macroeconomic projections table.

    Returns ``(rows, warnings)``; each row is ``{"period", "value", "basis"}``
    with growth in per cent. Years before the publication year are "actual"
    or "estimate" as Treasury labels them (the last of them is the estimate);
    the publication year onward is "forecast".
    """
    start = text.find(_TABLE_TITLE)
    if start < 0:
        return [], ["macroeconomic projections table not found"]
    table = text[start:start + 2500]
    years_match = _YEAR_ROW.search(table)
    growth_match = _GROWTH_ROW.search(table)
    if not years_match or not growth_match:
        return [], ["macroeconomic projections table: growth row not understood"]
    years = [int(y) for y in years_match.group(1).split()]
    values = [float(v) for v in growth_match.group(1).split()]
    if len(years) != len(values):
        return [], [f"macroeconomic projections table: {len(years)} years "
                    f"but {len(values)} growth figures"]

    earlier = [y for y in years if y < publication_year]
    rows = []
    for year, value in zip(years, values):
        if year >= publication_year:
            basis = "forecast"
        elif year == max(earlier):
            basis = "estimate"
        else:
            basis = "actual"
        rows.append({"period": year, "value": value, "basis": basis})
    return rows, []
