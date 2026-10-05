"""Statistics South Africa workbooks, read from disk.

Stats SA's website sits behind a bot check that refuses scripted downloads,
so these files cannot be fetched automatically. Once a year someone downloads
them in a browser into ``external/data/raw/statssa/`` and this module reads them:

    Gross domestic product (P0441), "GDP Time series" workbook
        statssa.gov.za > Publications > P0441 > latest quarter
        file name like "GDP P0441 - GDP Time series Q2 2026.xlsx"

The workbook's "Annual" sheet has one row per series. Column H03 is the
series code, H04 and H05 describe it, H15 gives the price basis, H17 the
unit, and the columns named Y1993, Y1994, ... hold the values.
"""
from __future__ import annotations

import re
from pathlib import Path

GDP_FILE_PATTERN = "GDP P0441*Time series*.xlsx"
ANNUAL_SHEET = "Annual"
GDP_CODE = "AR1000"            # GDP at market prices, constant prices, annual
VALUE_ADDED = "Value added at basic prices"

_YEAR_COLUMN = re.compile(r"^Y((?:19|20)\d{2})$")
_QUARTER = re.compile(r"Q([1-4])\s*(20\d{2})")


def latest_gdp_file(folder: Path) -> Path | None:
    """The GDP time-series workbook for the most recent quarter in ``folder``."""
    def key(path: Path) -> tuple[int, int]:
        match = _QUARTER.search(path.name)
        return (int(match.group(2)), int(match.group(1))) if match else (0, 0)

    files = [p for p in folder.glob(GDP_FILE_PATTERN) if not p.name.startswith("~$")]
    return max(files, key=key) if files else None


def read_annual_sheet(path: Path) -> list[list]:
    import warnings

    import openpyxl

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        book = openpyxl.load_workbook(path, read_only=True, data_only=True)
        if ANNUAL_SHEET not in book.sheetnames:
            raise ValueError(f"{path.name}: no sheet named {ANNUAL_SHEET!r}")
        return [list(row) for row in book[ANNUAL_SHEET].iter_rows(values_only=True)]


def parse_constant_price_series(rows: list[list]) -> tuple[list[dict], list[str]]:
    """GDP and industry value added at constant prices, in rand.

    Returns ``(series, warnings)``. Each series is
    ``{"code", "name", "price_basis", "values": {year: rand}}``; ``name`` is
    ``"gdp"`` for total GDP and the industry description for value added.
    The workbook is in R million; values are converted to rand.
    """
    if not rows:
        return [], ["annual sheet is empty"]
    header = [str(cell).strip() if cell is not None else "" for cell in rows[0]]
    try:
        code_col, group_col, name_col = header.index("H03"), header.index("H04"), header.index("H05")
        basis_col, unit_col = header.index("H15"), header.index("H17")
    except ValueError:
        return [], ["annual sheet: expected column headings H03-H05, H15 and H17 not found"]
    years = {i: int(m.group(1)) for i, h in enumerate(header) if (m := _YEAR_COLUMN.match(h))}
    if not years:
        return [], ["annual sheet: no year columns found"]

    out: list[dict] = []
    warnings: list[str] = []
    for row in rows[1:]:
        if len(row) <= max(code_col, basis_col, unit_col):
            continue
        basis = str(row[basis_col] or "")
        if not basis.lower().startswith("constant"):
            continue
        code, group = str(row[code_col] or "").strip(), str(row[group_col] or "").strip()
        if code == GDP_CODE:
            name = "gdp"
        elif group == VALUE_ADDED:
            name = str(row[name_col] or "").strip()
        else:
            continue
        unit = str(row[unit_col] or "").strip().lower()
        if unit != "r million":
            warnings.append(f"{code}: unit is {row[unit_col]!r}, expected R million; skipped")
            continue
        values = {
            year: float(row[i]) * 1_000_000
            for i, year in years.items()
            if i < len(row) and isinstance(row[i], (int, float))
        }
        if values:
            out.append({"code": code, "name": name, "price_basis": basis, "values": values})
    if not any(s["name"] == "gdp" for s in out):
        warnings.append(f"GDP series {GDP_CODE} not found")
    return out, warnings


# --------------------------------------------------------------------------- #
# Mid-year population estimates (P0302)
#
#     statssa.gov.za > Publications > P0302 > latest release
#     "Country projection by population group, sex and age (2002-2026).xlsx"
#         one row per population group x sex x age band, one column per year
#     "MYPE report table website_ 2026.xlsx"
#         the release's summary tables; its national total is used as a check

POPULATION_FILE_PATTERN = "Country projection by population group*.xlsx"
SUMMARY_FILE_PATTERN = "MYPE report table*.xlsx"
SUMMARY_SHEET = "MYPE by pop grp and sex"

_END_YEAR = re.compile(r"\((?:19|20)\d{2}\s*-\s*((?:19|20)\d{2})\)")
_RELEASE_YEAR = re.compile(r"((?:19|20)\d{2})")


def latest_population_file(folder: Path) -> Path | None:
    """The country projection workbook whose year range ends latest."""
    def key(path: Path) -> int:
        match = _END_YEAR.search(path.name)
        return int(match.group(1)) if match else 0

    files = [p for p in folder.glob(POPULATION_FILE_PATTERN) if not p.name.startswith("~$")]
    return max(files, key=key) if files else None


def latest_summary_file(folder: Path) -> Path | None:
    def key(path: Path) -> int:
        years = _RELEASE_YEAR.findall(path.stem)
        return int(years[-1]) if years else 0

    files = [p for p in folder.glob(SUMMARY_FILE_PATTERN) if not p.name.startswith("~$")]
    return max(files, key=key) if files else None


def read_sheet(path: Path, sheet: str | None = None) -> list[list]:
    """Rows of one sheet (the first if ``sheet`` is not given)."""
    import warnings

    import openpyxl

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        book = openpyxl.load_workbook(path, read_only=True, data_only=True)
        if sheet is not None and sheet not in book.sheetnames:
            raise ValueError(f"{path.name}: no sheet named {sheet!r}")
        ws = book[sheet] if sheet is not None else book[book.sheetnames[0]]
        return [list(row) for row in ws.iter_rows(values_only=True)]


def parse_population(rows: list[list]) -> tuple[dict[int, float], list[str]]:
    """Total population by year: ``({year: persons}, warnings)``.

    Adds up every population group, sex and age band. Rows that are already
    totals are left out so nothing is counted twice.
    """
    header_index = next(
        (i for i, row in enumerate(rows)
         if sum(1 for c in row if _is_year(c)) >= 5 and any(_text(c) == "sex" for c in row)),
        None,
    )
    if header_index is None:
        return {}, ["population sheet: heading row with Sex and year columns not found"]
    header = rows[header_index]
    # The sheet carries further tables to the right (by sex and age, then by
    # age only) that repeat the same years. Only the first, most detailed
    # block is read: the label columns and the unbroken run of years after them.
    first_year = next(i for i, c in enumerate(header) if _is_year(c))
    years: dict[int, int] = {}
    for i in range(first_year, len(header)):
        if not _is_year(header[i]):
            break
        years[i] = int(float(header[i]))
    labels = [i for i in range(first_year) if isinstance(header[i], str)]

    totals = dict.fromkeys(years.values(), 0.0)
    counted = 0
    for row in rows[header_index + 1:]:
        words = [_text(row[i]) for i in labels if i < len(row)]
        if not any(words) or any("total" in w or w == "all" for w in words):
            continue
        values = {year: row[i] for i, year in years.items() if i < len(row)}
        if not all(isinstance(v, (int, float)) for v in values.values()):
            continue
        for year, value in values.items():
            totals[year] += float(value)
        counted += 1
    if counted == 0:
        return {}, ["population sheet: no data rows found"]
    return totals, []


def parse_summary_total(rows: list[list]) -> float | None:
    """The national total printed in the release's summary table, if found."""
    for row in rows:
        if row and _text(row[0]) == "total":
            numbers = [c for c in row if isinstance(c, (int, float)) and c > 1_000_000]
            if numbers:
                return float(numbers[-1])
    return None


def average_growth(population: dict[int, float], years: int) -> tuple[float, int, int]:
    """Average annual growth over the last ``years`` years: ``(rate, from, to)``."""
    last = max(population)
    first = last - years
    if first not in population:
        raise ValueError(f"population series does not reach back to {first}")
    return (population[last] / population[first]) ** (1 / years) - 1, first, last


def _is_year(cell) -> bool:
    try:
        return 1900 <= int(float(str(cell).strip())) <= 2100 and len(str(cell).strip()) in (4, 6)
    except (TypeError, ValueError):
        return False


def _text(cell) -> str:
    return str(cell).strip().lower() if isinstance(cell, str) else ""
