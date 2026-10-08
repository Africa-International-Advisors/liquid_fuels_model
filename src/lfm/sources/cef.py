"""Regulated inland fuel prices from the Central Energy Fund's daily basic fuel price sheets.

CEF posts a one-page PDF every working day. Its first lines restate the
regulated prices in force, with the date they took effect:

    GAUTENG PUMP PRICE AS FROM 04/02/2026 2,010.000 1,999.000 - - -
    WHOLESALE PRICE AS FROM 04/02/2026 - - 1,791.830 1,795.230 1,210.098

in the column order petrol 95, petrol 93, diesel 0.05%, diesel 0.005%,
illuminating paraffin, all in cents per litre. The department's own pages have
lagged since early 2026, so these sheets carry the series forward. They give
Gauteng (inland) prices only; no coastal price is printed.

    cefgroup.co.za > Petrol Price > Daily Basic Fuel Price > <year>

One sheet a month is enough: prices change once a month, on the first
Wednesday. The sheet nearest the 15th is used so that it shows that month's
price and not the next month's, which appears a few days before it takes effect.
"""
from __future__ import annotations

import re
import urllib.parse
import urllib.request
from datetime import date

INDEX_URL = "https://cefgroup.co.za/daily-basic-fuel-price/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

_YEAR_PAGE = re.compile(r'href="(https://cefgroup\.co\.za/((?:19|20)\d{2})-\d+/)"')
_SHEET = re.compile(r'href="([^"]*/Daily-(\d{2})-(\d{2})-((?:19|20)\d{2})[^"/]*\.pdf)"', re.IGNORECASE)
_NUMBER = r"(-|\d{1,3}(?:,\d{3})*(?:\.\d+)?)"
_ROW = r"\s+AS FROM\s+(\d{2})/(\d{2})/((?:19|20)\d{2})\s+" + r"\s+".join([_NUMBER] * 5)
_PUMP = re.compile(r"GAUTENG PUMP PRICE" + _ROW)
_WHOLESALE = re.compile(r"(?<!\S)WHOLESALE PRICE" + _ROW)


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def discover_year_pages(index_html: str) -> dict[int, str]:
    """``{year: address}`` of the yearly listing pages linked from the index."""
    return {int(year): url for url, year in _YEAR_PAGE.findall(index_html)}


def discover_daily_sheets(year_html: str) -> list[tuple[date, str]]:
    """``(date, address)`` of each daily sheet on a yearly page, oldest first."""
    found: dict[date, str] = {}
    for href, day, month, year in _SHEET.findall(year_html):
        try:
            when = date(int(year), int(month), int(day))
        except ValueError:
            continue
        found.setdefault(when, urllib.parse.urljoin(INDEX_URL, href))
    return sorted(found.items())


def pick_monthly(sheets: list[tuple[date, str]]) -> dict[tuple[int, int], tuple[date, str]]:
    """For each month, the sheet dated nearest the 15th."""
    chosen: dict[tuple[int, int], tuple[date, str]] = {}
    for when, url in sheets:
        key = (when.year, when.month)
        if key not in chosen or abs(when.day - 15) < abs(chosen[key][0].day - 15):
            chosen[key] = (when, url)
    return chosen


def parse_daily_sheet(text: str) -> tuple[date | None, dict[str, float], list[str]]:
    """``(effective date, prices by series, warnings)`` from one daily sheet.

    Series names match ``energy_dept.PRICE_SERIES``. Only the four inland
    series are returned; the sheet prints no coastal price.
    """
    page = " ".join(text.split())
    warnings: list[str] = []
    pump, wholesale = _PUMP.search(page), _WHOLESALE.search(page)
    if not pump or not wholesale:
        return None, {}, ["price lines not found"]
    if pump.group(1, 2, 3) != wholesale.group(1, 2, 3):
        warnings.append("pump and wholesale prices carry different effective dates")
    day, month, year = (int(g) for g in pump.group(1, 2, 3))
    cells = {
        "petrol_95_inland_retail": pump.group(4), "petrol_93_inland_retail": pump.group(5),
        "diesel_005_inland_wholesale": wholesale.group(6), "paraffin_inland": wholesale.group(8),
    }
    prices = {}
    for series, cell in cells.items():
        if cell == "-":
            warnings.append(f"{series}: no figure printed")
        else:
            prices[series] = float(cell.replace(",", ""))
    return date(year, month, day), prices, warnings
