"""Transnet National Ports Authority port statistics: liquid bulk handled, by port.

The port authority posts a one-page "Summary of cargo handled at ports of
South Africa" for each month and each calendar year:

    transnet.net/TNPA > Port Statistics   (SubsiteRender.aspx?id=24332214)

The page lists each file in a hidden record with its period and type. Each
summary is a table of eight ports and a total, in metric tons, with blocks for
dry bulk, liquid bulk, breakbulk and so on. Only the liquid bulk block is read.

Liquid bulk is every liquid together: crude oil, fuels, gas and chemicals. The
figures are tons, not litres, and are not split by product.
"""
from __future__ import annotations

import re
import urllib.request

SITE = "https://www.transnet.net/"
INDEX_URL = SITE + "SubsiteRender.aspx?id=24332214"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"

PORTS = ("RICHARDS BAY", "DURBAN", "EAST LONDON", "NGQURA", "PORT ELIZABETH", "MOSSEL BAY", "CAPE TOWN", "SALDANHA", "TOTAL")
PORT_NAMES = {"RICHARDS BAY": "Richards Bay", "DURBAN": "Durban", "EAST LONDON": "East London", "NGQURA": "Ngqura",
              "PORT ELIZABETH": "Port Elizabeth", "MOSSEL BAY": "Mossel Bay", "CAPE TOWN": "Cape Town",
              "SALDANHA": "Saldanha", "TOTAL": "All ports"}
MOVEMENTS = {"IMPORTS": "landed", "EXPORTS": "shipped", "COASTWISE LIQUID BULK CARGO": "coastwise",
             "TRANSHIPMENT LIQUID BULK CARGO": "transhipment", "TOTAL LIQUIDBULK HANDLED": "handled"}
MONTHS = {name: number for number, name in enumerate(
    ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"), start=1)}
ROUNDING = 5  # tons; the printed totals are rounded separately from their parts

_RECORD = re.compile(r'<div class="cargoRecord".*?</div>', re.S)
_NUMBER = re.compile(r"(?<![\d])(\d{1,3}(?: \d{3})*-?|-)(?=\s{2,}|\s*$)")


def _tons(cell: str) -> int:
    """A cell as tons: ``-`` is nil and a trailing minus (``18 823-``) is a negative correction."""
    if cell == "-":
        return 0
    value = int(cell.rstrip("-").replace(" ", ""))
    return -value if cell.endswith("-") else value


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:
        return response.read()


def discover(index_html: str) -> list[dict]:
    """``{"period", "kind", "url"}`` for each total-cargo summary listed on the statistics page."""
    out = []
    for record in _RECORD.findall(index_html):
        def cell(name: str) -> str:
            found = re.search(rf'class="{name}">([^<]*)<', record)
            return found.group(1).strip() if found else ""
        if cell("cargo-doc1") and cell("cargo-date"):
            out.append({"period": cell("cargo-date"), "kind": cell("cargo-type").lower(), "url": SITE + cell("cargo-doc1")})
    return sorted(out, key=lambda r: (r["kind"], r["period"]))


class NotACargoSummary(ValueError):
    """The file is not a cargo summary in metric tons (the page sometimes links another report)."""


def period_of(text: str) -> tuple[str, str, str]:
    """``(period, basis, measure)`` from the summary's heading.

    ``("2026-08", "month", "handled")`` or ``("2025", "calendar year", "handled")``. ``measure`` is
    ``"invoiced"`` where the heading says cargo invoiced instead of cargo handled.
    """
    lines = [line.strip().upper() for line in text.splitlines()[:3]]
    if len(lines) < 3 or "SUMMARY OF CARGO" not in lines[0] or "METRIC TONS" not in lines[2]:
        raise NotACargoSummary(" / ".join(lines))
    title = lines[1]
    year = re.search(r"(19|20)\d{2}", title).group(0)
    measure = "invoiced" if "INVOICED" in lines[0] else "handled"
    if "CALENDAR YEAR" in title:
        return year, "calendar year", measure
    months = [MONTHS[word[:3]] for word in re.findall(r"[A-Z]+", title) if word[:3] in MONTHS]
    if len(months) != 1:
        raise ValueError(f"cannot read one month from {title!r}")
    return f"{year}-{months[0]:02d}", "month", measure


def parse_liquid_bulk(text: str, layout: str) -> list[dict]:
    """Liquid bulk tons by port and movement from one summary.

    ``text`` is the page as plain text and ``layout`` the same page in layout
    mode, which is the only one that carries the port names. Raises if the
    ports are not in the expected order or a row does not add up.
    """
    header = next((line for line in layout.splitlines() if "RICHARDS BAY" in line), "")
    if re.sub(r"\s+", " ", header).strip() != " ".join(PORTS):
        raise ValueError(f"unexpected port columns: {header.strip()!r}")
    period, basis, measure = period_of(text)
    block = text[text.index("LIQUID BULK CARGO HANDLED"): text.index("BREAKBULK CARGO HANDLED")]
    table: dict[str, dict[str, int]] = {}
    for line in block.splitlines():
        for label, movement in MOVEMENTS.items():
            if line.startswith(label + " "):
                cells = _NUMBER.findall(line[len(label):])
                if len(cells) != len(PORTS):
                    raise ValueError(f"{period}: {label} has {len(cells)} cells")
                table[movement] = dict(zip(PORTS, (_tons(c) for c in cells)))
    if set(table) != set(MOVEMENTS.values()):
        raise ValueError(f"{period}: missing rows {set(MOVEMENTS.values()) - set(table)}")
    for movement, row in table.items():
        if abs(sum(v for port, v in row.items() if port != "TOTAL") - row["TOTAL"]) > ROUNDING:
            raise ValueError(f"{period}: {movement} does not add across ports")
    for port in PORTS:
        parts = sum(table[m][port] for m in ("landed", "shipped", "coastwise", "transhipment"))
        if abs(parts - table["handled"][port]) > ROUNDING:
            raise ValueError(f"{period}: movements do not add to handled at {port}")
    return [{"country": "ZAF", "period": period, "period_basis": basis, "scenario": "shared", "port": PORT_NAMES[port],
             "movement": movement, "value": table[movement][port], "unit": "tonnes", "measure": measure}
            for movement in MOVEMENTS.values() for port in PORTS]
