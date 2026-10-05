"""NaTIS (National Traffic Information System) vehicle statistics.

The Road Traffic Management Corporation publishes two monthly one-page PDFs:

  - Live vehicle population: registered vehicles by class and province at
    month end. Each file carries the month before as well.
  - New vehicle registrations: vehicles registered for the first time during
    the month, by class and province. Each file carries the same month a
    year earlier as well.

Neither splits vehicles by fuel. NaTIS does not publish petrol / diesel /
electric counts, so the fuel split of the fleet cannot come from here.

Reading the tables. Thousands are printed with a space ("3 473 498") and the
PDF text does not separate columns reliably. Every row ends with a national
total that equals the sum of the provinces, so the columns are placed by
finding the one way of grouping the digits for which that sum holds. A row
where no grouping, or more than one, satisfies the sum is reported and left
out. Nothing is estimated.
"""
from __future__ import annotations

import calendar
import difflib
import hashlib
import html
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path

HOME_URL = "https://www.natis.gov.za/"
FILES_URL = "https://www.natis.gov.za/media/com_natisdownloads/files/"
USER_AGENT = "Mozilla/5.0 (lfm source fetcher)"

PROVINCES = ("GP", "KZN", "WC", "EC", "FS", "MP", "NW", "LP", "NC")

KINDS = {
    "population": ("live-vehicle-population", "LiveVehPopPerClassProv"),
    "new_registrations": ("new-vehicle-registrations", "NewVehicleRegistration"),
}

# Row labels as printed, up to the first figure. Trailer rows are not read.
CLASSES = {
    "cars": re.compile(r"^Motor cars and station wagons\s+"),
    "minibuses": re.compile(r"^Minibuses\s+"),
    "buses": re.compile(r"^Buses, bus trains, midibuses\s+"),
    "motorcycles": re.compile(r"^Motorcycles, quadrucycles, tricycles\s+"),
    "light_commercial": re.compile(r"^LDV's, panel vans, other light load veh's GVM <= 3500kg\s+"),
    "trucks": re.compile(r"^Trucks \(Heavy load vehicles GVM > 3500kg\)\s+"),
    "other_self_propelled": re.compile(r"^Other self-propelled vehicles\s+"),
    "total_self_propelled": re.compile(r"^Total self-propelled vehicles\s+"),
}

_BLOCK = re.compile(
    r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s*-\s*(Live vehicle population|New vehicle registrations)"
)
_PERCENT = re.compile(r"\s*\d+(?:[.,]\d+)?%\s*$")


@dataclass(frozen=True)
class SourceFile:
    kind: str
    period: str            # month the file is published for, "2026-06"
    url: str
    path: Path | None = None
    sha256: str | None = None


# --------------------------------------------------------------------------- #
# Finding and downloading

def category_pages(home_html: str, kind: str) -> list[str]:
    """Addresses of the yearly listing pages for ``kind``, from the site menu."""
    slug = KINDS[kind][0]
    pattern = re.compile(r'href="([^"]*' + slug + r"/" + slug + r'-(?:19|20)\d{2}[^"]*)"')
    pages = {html.unescape(html.unescape(h)) for h in pattern.findall(home_html)}
    return sorted(HOME_URL.rstrip("/") + p if p.startswith("/") else p for p in pages)


def discover_files(listing_html: str, kind: str) -> list[SourceFile]:
    """Monthly PDFs linked from one yearly listing page."""
    stem = KINDS[kind][1]
    pattern = re.compile(r'href="[^"]*/(' + stem + r'((?:19|20)\d{2})(\d{2})\d{2}[^"/]*\.pdf)"')
    found: dict[str, SourceFile] = {}
    for name, year, month in pattern.findall(listing_html):
        period = f"{year}-{month}"
        # Some links on the site point at "localhost"; the file name is what matters.
        found[period] = SourceFile(kind=kind, period=period, url=FILES_URL + name)
    return [found[p] for p in sorted(found)]


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:
        return response.read()


def download(source: SourceFile, raw_dir: Path) -> SourceFile:
    """Download a PDF into ``raw_dir`` unless that month is already there."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{KINDS[source.kind][1]}-{source.period}.pdf"
    if not path.exists():
        data = fetch(source.url)
        if not data.startswith(b"%PDF"):
            raise ValueError(f"{source.url} did not return a PDF")
        path.write_bytes(data)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return SourceFile(kind=source.kind, period=source.period, url=source.url,
                      path=path, sha256=digest)


# --------------------------------------------------------------------------- #
# Reading

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


def parse(text: str) -> tuple[list[dict], list[str]]:
    """Every table in a file as ``(rows, warnings)``.

    Each row is ``{"period": "2026-06", "vehicle_class", "province", "value"}``
    with province ``"ZAF"`` for the national total. Provincial figures are
    given only when all nine provinces are printed; a row with blank cells
    yields the national total alone.
    """
    rows: list[dict] = []
    warnings: list[str] = []
    marks = list(_BLOCK.finditer(text))
    periods = [_period(mark.group(1)) for mark in marks]
    # A file that prints the same date on two different tables has a typing
    # error in one of them. Which one is unknowable, so neither is used; the
    # month is picked up from another file that carries it.
    repeated = {p for p in periods if p is not None and periods.count(p) > 1}
    for period in sorted(repeated):
        warnings.append(f"{period}: date printed on two tables, both left out")
    for i, mark in enumerate(marks):
        period = periods[i]
        if period is None:
            warnings.append(f"date not understood: {mark.group(1)!r}")
            continue
        if period in repeated:
            continue
        block = text[mark.end(): marks[i + 1].start() if i + 1 < len(marks) else len(text)]
        seen: set[str] = set()
        for line in block.splitlines():
            line = line.strip()
            for vehicle_class, label in CLASSES.items():
                match = label.match(line)
                if not match:
                    continue
                if vehicle_class in seen:
                    break  # some files repeat the labels in a second, different table
                seen.add(vehicle_class)
                values = _place_columns(_PERCENT.sub("", line[match.end():]).split())
                if values is None:
                    warnings.append(f"{period} {vehicle_class}: columns could not be placed")
                    break
                *provinces, total = values
                rows.append({"period": period, "vehicle_class": vehicle_class,
                             "province": "ZAF", "value": total})
                if len(provinces) == len(PROVINCES):
                    rows += [
                        {"period": period, "vehicle_class": vehicle_class,
                         "province": code, "value": value}
                        for code, value in zip(PROVINCES, provinces)
                    ]
                break
    return rows, warnings


def _period(printed_date: str) -> str | None:
    """'30 November 2018' -> '2018-11'. Tolerates the misspelt months in some files."""
    _, month_name, year = printed_date.split()
    close = difflib.get_close_matches(month_name.capitalize(), calendar.month_name[1:], n=1)
    if not close:
        return None
    return f"{year}-{list(calendar.month_name).index(close[0]):02d}"


def _place_columns(tokens: list[str]) -> list[int] | None:
    """Read digit groups as provincial figures followed by their total.

    Returns the figures when exactly one grouping makes the last number the
    sum of the others; prefers the reading with the most provinces.
    """
    if not tokens or not all(t.isdigit() for t in tokens):
        return None
    for n in range(len(PROVINCES) + 1, 1, -1):
        valid = [g for g in _groupings(tokens, n) if sum(g[:-1]) == g[-1]]
        if len(valid) == 1:
            return valid[0]
        if len(valid) > 1:
            return None
    return None


def _groupings(tokens: list[str], n: int) -> list[list[int]]:
    """Every way to read ``tokens`` as ``n`` numbers of up to three digit groups."""
    out: list[list[int]] = []

    def walk(i: int, acc: list[int]) -> None:
        if len(acc) > n:
            return
        if i == len(tokens):
            if len(acc) == n:
                out.append(acc)
            return
        first = tokens[i]
        if len(first) > 3 or (len(first) > 1 and first[0] == "0"):
            return
        text = first
        walk(i + 1, acc + [int(text)])
        for extra in (1, 2):
            if i + extra >= len(tokens) or len(tokens[i + extra]) != 3:
                break
            text += tokens[i + extra]
            walk(i + extra + 1, acc + [int(text)])

    walk(0, [])
    return out
