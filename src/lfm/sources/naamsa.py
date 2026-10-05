"""naamsa (the Automotive Business Council) quarterly publications.

Two documents are listed together on the association's quarterly reviews page:

  - Quarterly Review of Business Conditions: carries a table of new energy
    vehicle sales by drivetrain (traditional hybrid, plug-in hybrid, electric)
    for each full year since 2020.
  - Industry Vehicle Sales, Actual and Projections: one page giving the local
    market by segment (cars, light commercials, medium and heavy commercials)
    for about ten years, the last two being the association's projections.

naamsa does not publish sales split by petrol and diesel in either document.

Both tables carry their own check: the three drivetrains add up to the
printed total, and the three segments add up to the aggregate market. A
column that fails its check is reported and left out. Nothing is estimated.
"""
from __future__ import annotations

import hashlib
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

INDEX_URL = "https://naamsa.net/quarterly-reviews/"
USER_AGENT = "Mozilla/5.0 (lfm source fetcher)"

DRIVETRAINS = {
    "traditionalhybrid": "traditional_hybrid",
    "plug-inhybrid": "plug_in_hybrid",
    "electric": "battery_electric",
    "totalnevs": "total",
}
SEGMENTS = {
    "TOTAL LOCAL CAR MARKET": "cars",
    "TOTAL LOCAL LCV MARKET": "light_commercial",
    "TOTAL LOCAL MCV/HCV MARKET": "medium_heavy_commercial",
    "TOTAL AGGREGATE MARKET": "total",
}

_LINK = re.compile(r'href="(https?://naamsa\.net/wp-content/uploads/(\d{4})/(\d{2})/([^"/]+\.pdf))"',
                   re.IGNORECASE)
_PROJECTIONS = re.compile(r"actual|projection|industry-?vehicle-?sales|IndustryVehi", re.IGNORECASE)
_REVIEW = re.compile(r"review", re.IGNORECASE)
_NUMBER = re.compile(r"\d[\d,]*")
_MARKET_TOLERANCE = 0.0005   # 0.05% of the aggregate market
_YEAR_ROW = re.compile(r"^\s*((?:19|20)\d{2}(?:\s+(?:19|20)\d{2}){4,})\s*$", re.MULTILINE)


@dataclass(frozen=True)
class SourceFile:
    kind: str              # "review" or "projections"
    uploaded: str          # "2026-08", from the address the file sits at
    url: str
    path: Path | None = None
    sha256: str | None = None


# --------------------------------------------------------------------------- #
# Finding and downloading

def discover(index_html: str) -> list[SourceFile]:
    """Reviews and projection files linked from the page, oldest upload first."""
    found: dict[str, SourceFile] = {}
    for url, year, month, name in _LINK.findall(index_html):
        if _PROJECTIONS.search(name):
            kind = "projections"
        elif _REVIEW.search(name):
            kind = "review"
        else:
            continue
        found[url] = SourceFile(kind=kind, uploaded=f"{year}-{month}", url=url)
    return sorted(found.values(), key=lambda f: (f.uploaded, f.url))


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=240) as response:
        return response.read()


def download(source: SourceFile, raw_dir: Path) -> SourceFile:
    raw_dir.mkdir(parents=True, exist_ok=True)
    name = urllib.parse.unquote(source.url.rsplit("/", 1)[-1])
    path = raw_dir / f"{source.uploaded}_{name}"
    if not path.exists():
        data = fetch(source.url)
        if not data.startswith(b"%PDF"):
            raise ValueError(f"{source.url} did not return a PDF")
        path.write_bytes(data)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return SourceFile(kind=source.kind, uploaded=source.uploaded, url=source.url,
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


# --------------------------------------------------------------------------- #
# New energy vehicle table (quarterly review)

def parse_nev(text: str) -> tuple[dict[int, dict[str, int]], list[str]]:
    """Full-year sales by drivetrain: ``({year: {drivetrain: units}}, warnings)``.

    Quarter columns in the same table are ignored; only complete years are read.
    """
    start = text.find("Plug-in hybrid")
    alt = re.search(r"T\s*r\s*a\s*d\s*i\s*t\s*i\s*o\s*n\s*a\s*l\s+h\s*y\s*b\s*r\s*i\s*d", text)
    if start < 0 and not alt:
        return {}, ["new energy vehicle table not found"]
    first_row = min(p for p in (start, alt.start() if alt else -1) if p >= 0)

    # Column headings sit just above the first row: "Year 2020 ... Q2:2025".
    heading = text[max(0, first_row - 400):first_row]
    heading = heading[heading.rfind("landscape") + 1:] if "landscape" in heading else heading
    # The sentence above the table ends "... through to Q1:2025", which is not a column.
    heading = re.sub(r"through to[^\n]*\n", "\n", heading)
    columns = re.findall(r"(Q\d\s*:\s*20\d{2}|(?:FY|Year\s*)20\d{2})", heading)
    if not columns:
        return {}, ["new energy vehicle table: column headings not understood"]
    years = [int(c[-4:]) if not c.upper().startswith("Q") else None for c in columns]

    rows: dict[str, list[int]] = {}
    for line in text[first_row:first_row + 900].splitlines():
        match = re.match(r"^(\D+?)\s+(\d[\d,\s]*)$", line.strip())
        if not match:
            continue
        key = DRIVETRAINS.get(re.sub(r"\s+", "", match.group(1)).lower())
        values = [int(n.replace(",", "")) for n in _NUMBER.findall(match.group(2))]
        if key and len(values) == len(columns):
            rows[key] = values
        if len(rows) == len(DRIVETRAINS):
            break
    if len(rows) < len(DRIVETRAINS):
        missing = sorted(set(DRIVETRAINS.values()) - set(rows))
        return {}, [f"new energy vehicle table: rows not read ({', '.join(missing)})"]

    out: dict[int, dict[str, int]] = {}
    warnings: list[str] = []
    for i, year in enumerate(years):
        if year is None:
            continue
        parts = {k: rows[k][i] for k in ("traditional_hybrid", "plug_in_hybrid", "battery_electric")}
        if sum(parts.values()) != rows["total"][i]:
            warnings.append(f"new energy vehicles {year}: drivetrains do not add up to the total")
            continue
        out[year] = {**parts, "total": rows["total"][i]}
    return out, warnings


# --------------------------------------------------------------------------- #
# Market by segment (actual and projections)

def parse_market(text: str) -> tuple[dict[int, dict[str, int]], list[str]]:
    """Local market by segment: ``({year: {segment: units}}, warnings)``."""
    header = _YEAR_ROW.search(text)
    if not header:
        return {}, ["market table: year headings not found"]
    years = [int(y) for y in header.group(1).split()]

    rows: dict[str, list[int]] = {}
    for line in text.splitlines():
        squeezed = re.sub(r"\s+", " ", line).strip()
        for label, segment in SEGMENTS.items():
            if squeezed.upper().startswith(label):
                values = _units(squeezed[len(label):].split())
                if values is not None and len(values) == len(years):
                    rows[segment] = values
    missing = sorted(set(SEGMENTS.values()) - set(rows))
    if missing:
        return {}, [f"market table: rows not read ({', '.join(missing)})"]

    out: dict[int, dict[str, int]] = {}
    warnings: list[str] = []
    for i, year in enumerate(years):
        parts = {k: rows[k][i] for k in ("cars", "light_commercial", "medium_heavy_commercial")}
        # naamsa's printed aggregate is sometimes a few units off the sum of its
        # own segments. That is accepted; a larger gap means a misread row.
        if abs(sum(parts.values()) - rows["total"][i]) > _MARKET_TOLERANCE * rows["total"][i]:
            warnings.append(f"market {year}: segments do not add up to the aggregate")
            continue
        out[year] = {**parts, "total": rows["total"][i]}
    return out, warnings


def _units(tokens: list[str]) -> list[int] | None:
    """Vehicle counts printed as "26272" or "27 449"; every count is 1 000 or more."""
    out: list[int] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if not token.isdigit():
            return None
        if len(token) >= 4:
            out.append(int(token))
            i += 1
        elif i + 1 < len(tokens) and tokens[i + 1].isdigit() and len(tokens[i + 1]) == 3:
            out.append(int(token + tokens[i + 1]))
            i += 2
        else:
            return None
    return out
