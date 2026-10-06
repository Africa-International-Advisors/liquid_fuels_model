"""Refresh fuel sales and energy balances from the energy department's website.

Finds every national fuel sales workbook and every energy balance workbook
listed on the department's pages, downloads any not already in
``external/data/raw/energy_dept/``, and writes:

    assumptions/<vintage>/timeseries/fuel_sales_department.csv
    assumptions/<vintage>/timeseries/fuel_sales_department_quarterly.csv
    assumptions/<vintage>/timeseries/energy_balance_department.csv
    assumptions/<vintage>/timeseries/energy_department.sources.yaml

CSV schemas (values in litres):
    fuel_sales_department.csv
        country,period,scenario,product,value,unit,quarters_reported,source_file
    fuel_sales_department_quarterly.csv
        country,period,scenario,product,value,unit,source_file      (period = 2023-Q4)
    energy_balance_department.csv
        country,period,scenario,product,flow_key,flow,value,unit,source_file

A year with fewer than four quarters is written to the quarterly file but
left out of the annual file, and is listed in the sources file.

Run (any year — it picks up whatever the department has published):
    python -m lfm.scripts.fetch_energy_dept --vintage 2026

Options:
    --offline    use only the workbooks already in external/data/raw/energy_dept/
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from datetime import date
from pathlib import Path

import yaml

from lfm.config import Paths
from lfm.sources import energy_dept as dept


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    paths = Paths.default()
    raw_dir = paths.data_dir / "raw" / "energy_dept"
    out_dir = paths.vintage_dir(args.vintage) / "timeseries"
    if not out_dir.exists():
        sys.exit(f"vintage directory not found: {out_dir}")

    sales_files, balance_files = _files(raw_dir, args.offline)
    if not sales_files and not balance_files:
        sys.exit("no department workbooks found — check BASE_URL in lfm/sources/energy_dept.py")

    warnings: list[str] = []
    annual, quarterly, part_years = _sales(sales_files, warnings)
    balance = _balances(balance_files, warnings)

    _write(out_dir / "fuel_sales_department.csv", annual, [
        "country", "period", "scenario", "product", "value", "unit",
        "quarters_reported", "source_file"])
    _write(out_dir / "fuel_sales_department_quarterly.csv", quarterly, [
        "country", "period", "scenario", "product", "value", "unit", "source_file"])
    _write(out_dir / "energy_balance_department.csv", balance, [
        "country", "period", "scenario", "product", "flow_key", "flow", "value",
        "unit", "source_file"])

    provincial_info = _provincial(raw_dir / "fsv_district", out_dir, annual, args.offline, warnings)
    price_info = _prices(raw_dir / "prices", out_dir, args.offline, warnings)

    doc = {
        "publisher": "Energy department (Department of Mineral and Petroleum Resources site)",
        "fuel_sales_by_province": provincial_info,
        "fuel_prices": price_info,
        "index_pages": [dept.SALES_INDEX, dept.BALANCE_INDEX],
        "retrieved": date.today().isoformat(),
        "fuel_sales": {
            "latest_full_year": max((r["period"] for r in annual), default=None),
            "part_years_left_out_of_annual_file": part_years,
        },
        "energy_balance": {
            "latest_year": max((r["period"] for r in balance), default=None),
            "source_unit": "kilolitres (converted to litres)",
        },
        "warnings": warnings,
        "files": [
            {"kind": kind, "year": f.year, "url": f.url, "file": f.path.name, "sha256": f.sha256}
            for kind, files in (("fuel_sales", sales_files), ("energy_balance", balance_files))
            for f in files
        ],
    }
    (out_dir / "energy_department.sources.yaml").write_text(
        yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")

    print(f"[fetch] fuel sales: {len(sales_files)} file(s); latest full year "
          f"{doc['fuel_sales']['latest_full_year']}", file=sys.stderr)
    print(f"[fetch] energy balances: {len(balance_files)} file(s); latest year "
          f"{doc['energy_balance']['latest_year']}", file=sys.stderr)
    for warning in warnings:
        print(f"[fetch]   WARNING {warning}", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------- #

def _files(raw_dir: Path, offline: bool) -> tuple[list, list]:
    sales_dir, balance_dir = raw_dir / "fsv_national", raw_dir / "energy_balance"
    if offline:
        return _on_disk(sales_dir), _on_disk(balance_dir)
    sales = dept.discover_sales_files(dept.fetch(dept.SALES_INDEX).decode("utf-8", "replace"))
    balances = dept.discover_balance_files(
        dept.fetch(dept.BALANCE_INDEX).decode("utf-8", "replace"))
    return (
        [dept.download(f, sales_dir) for f in sales],
        [dept.download(f, balance_dir) for f in balances],
    )


def _provincial(raw_dir: Path, out_dir: Path, national: list[dict], offline: bool,
                warnings: list[str]) -> dict:
    """Sales by province from the district-level workbooks (2013 onwards)."""
    if offline:
        files = [f for f in _on_disk(raw_dir) if f.year >= dept.FIRST_PROVINCIAL_YEAR]
    else:
        listed = dept.discover_district_files(
            dept.fetch(dept.SALES_INDEX).decode("utf-8", "replace"))
        files = []
        for source in listed:
            try:
                files.append(dept.download(source, raw_dir))
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"provincial sales {source.year}: download failed ({exc})")

    quarterly: dict[tuple, dict] = {}
    for f in files:
        try:
            rows, problems = dept.parse_provincial_sales(dept.read_workbook(f.path))
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"provincial sales {f.year}: could not open {f.path.name} ({exc})")
            continue
        warnings += [f"provincial sales {f.path.name}: {p}" for p in problems]
        for row in rows:
            key = (row["year"], row["quarter"], row["province"], row["product"])
            quarterly[key] = {
                "country": "ZAF", "period": f"{row['year']}-Q{row['quarter']}",
                "scenario": "shared", "province": row["province"], "product": row["product"],
                "value": row["value"], "unit": "litres", "source_file": f.path.name,
            }
    _write(out_dir / "fuel_sales_department_by_province_quarterly.csv",
           [quarterly[k] for k in sorted(quarterly)],
           ["country", "period", "scenario", "province", "product", "value", "unit",
            "source_file"])

    # Calendar years: only where a province and product has all four quarters.
    sums: dict[tuple, list] = {}
    for (year, quarter, province, product), row in quarterly.items():
        entry = sums.setdefault((year, province, product), [0.0, set()])
        entry[0] += row["value"]
        entry[1].add(quarter)
    quarters_by_year: dict[int, set] = {}
    for (year, quarter, _, _) in quarterly:
        quarters_by_year.setdefault(year, set()).add(quarter)
    full_years = sorted(y for y, q in quarters_by_year.items() if q == {1, 2, 3, 4})
    annual_rows = [
        {"country": "ZAF", "period": year, "scenario": "shared", "province": province,
         "product": product, "value": total, "unit": "litres"}
        for (year, province, product), (total, _) in sorted(sums.items()) if year in full_years
    ]
    _write(out_dir / "fuel_sales_department_by_province.csv", annual_rows,
           ["country", "period", "scenario", "province", "product", "value", "unit"])

    # The provinces should add up to the national workbook for the same year.
    national_total = {(r["period"], r["product"]): r["value"] for r in national}
    differences = []
    for year in full_years:
        for product in ("petrol", "diesel", "jet"):
            provincial = sum(r["value"] for r in annual_rows
                             if r["period"] == year and r["product"] == product)
            target = national_total.get((year, product))
            if target and abs(provincial / target - 1) > 0.01:
                differences.append({"period": year, "product": product,
                                    "provinces_vs_national_pct":
                                        round((provincial / target - 1) * 100, 1)})
    part_years = sorted(set(quarters_by_year) - set(full_years))
    print(f"[fetch] sales by province: {len(files)} file(s); full years "
          f"{full_years[0] if full_years else '-'}–{full_years[-1] if full_years else '-'}; "
          f"part years {part_years}", file=sys.stderr)
    return {
        "full_years": full_years,
        "part_years_in_quarterly_file_only": part_years,
        "first_year_with_province_rows": dept.FIRST_PROVINCIAL_YEAR,
        "provinces_differ_from_national_by_more_than_1pct": differences,
        "files": [{"year": f.year, "url": f.url, "file": f.path.name, "sha256": f.sha256}
                  for f in files],
    }


def _prices(raw_dir: Path, out_dir: Path, offline: bool, warnings: list[str]) -> dict:
    """Monthly regulated fuel prices from the yearly 'Fuel Price History' PDFs."""
    if offline:
        files = []
        for path in sorted(raw_dir.glob("fuel-price-history-*.pdf")):
            files.append(dept.SourceFile(
                year=int(re.search(r"(\d{4})", path.stem).group(1)), url="(offline)", path=path,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    else:
        files = []
        try:
            listed = dept.discover_price_files(
                dept.fetch(dept.PRICE_INDEX).decode("utf-8", "replace"))
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"fuel prices: index page not reachable ({exc})")
            listed = []
        raw_dir.mkdir(parents=True, exist_ok=True)
        # Each year has an ordered list of addresses; the first that returns a PDF is kept.
        # The newer monthly folders come first because they hold later months.
        attempts: dict[int, list] = {source.year: [source] for source in listed}
        for year in range(dept.PRICE_RECENT_FROM, date.today().year + 1):
            attempts[year] = dept.recent_price_candidates(year) + attempts.get(year, [])
        for year in sorted(attempts):
            path = raw_dir / f"fuel-price-history-{year}.pdf"
            used = None
            for source in attempts[year]:
                try:
                    data = dept.fetch(source.url)
                    if not data.startswith(b"%PDF"):
                        raise ValueError("not a PDF")
                    path.write_bytes(data)   # the current year's file is updated in place
                    used = source
                    break
                except Exception:  # noqa: BLE001
                    continue
            if used is None:
                if not path.exists():
                    warnings.append(f"fuel prices {year}: no price history file found")
                    continue
                warnings.append(f"fuel prices {year}: download failed; kept the copy on disk")
            files.append(dept.SourceFile(
                year=year, url=used.url if used else "(kept from an earlier run)", path=path,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest()))

    monthly: list[dict] = []
    for f in files:
        try:
            months, problems = dept.parse_price_history(_pdf_text(f.path))
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"fuel prices {f.year}: could not read {f.path.name} ({exc})")
            continue
        warnings += [f"fuel prices {f.year}: {p}" for p in problems]
        for month, prices in sorted(months.items()):
            for series, price in zip(dept.PRICE_SERIES, prices):
                monthly.append({
                    "country": "ZAF", "period": f"{f.year}-{month:02d}", "scenario": "shared",
                    "series": series, "value": price, "unit": "cents per litre",
                    "source_file": f.path.name})
    breakdown_files = _breakdowns(raw_dir, offline, monthly, warnings)
    _write(out_dir / "fuel_prices_department.csv", monthly,
           ["country", "period", "scenario", "series", "value", "unit", "source_file"])

    sums: dict[tuple, list] = {}
    for row in monthly:
        entry = sums.setdefault((int(row["period"][:4]), row["series"]), [0.0, 0])
        entry[0] += row["value"]
        entry[1] += 1
    annual = [
        {"country": "ZAF", "period": year, "scenario": "shared", "series": series,
         "value": round(total / n, 3), "unit": "cents per litre, average of 12 months"}
        for (year, series), (total, n) in sorted(sums.items()) if n == 12
    ]
    _write(out_dir / "fuel_prices_department_annual.csv", annual,
           ["country", "period", "scenario", "series", "value", "unit"])
    months = sorted({r["period"] for r in monthly})
    print(f"[fetch] fuel prices: {len(files)} file(s); months "
          f"{months[0] if months else '-'} to {months[-1] if months else '-'}", file=sys.stderr)
    return {
        "index_page": dept.PRICE_INDEX,
        "months": f"{months[0]} to {months[-1]}" if months else None,
        "full_years": sorted({r["period"] for r in annual}),
        "prices_are": "regulated prices in cents per litre; petrol retail, diesel wholesale",
        "files": [{"year": f.year, "url": f.url, "file": f.path.name, "sha256": f.sha256}
                  for f in files],
        "monthly_breakdown_page": dept.PRICE_ARCHIVE_PAGE,
        "monthly_breakdown_files": breakdown_files,
        "series_with_no_value_in_latest_months": _gaps(monthly),
    }


def _gaps(monthly: list[dict]) -> dict[str, str]:
    """Series that stop before the latest month, with the first month they are missing.

    The monthly breakdown pages do not carry every series of the yearly history
    (coastal diesel is not published there), so a series can end early.
    """
    last: dict[str, str] = {}
    for row in monthly:
        last[row["series"]] = max(last.get(row["series"], ""), row["period"])
    latest = max(last.values(), default="")
    out = {}
    for series, period in sorted(last.items()):
        if period < latest:
            year, month = int(period[:4]), int(period[5:])
            nxt = f"{year + month // 12}-{month % 12 + 1:02d}"
            out[series] = f"not published from {nxt} (latest month in the file is {latest})"
    return out


def _breakdowns(raw_dir: Path, offline: bool, monthly: list[dict], warnings: list[str]) -> list:
    """Add months the yearly history does not cover from the monthly breakdown pages.

    ``monthly`` is extended in place. The latest month the history does cover is
    read from its breakdown page as well and compared, as a check that the two
    documents mean the same prices.
    """
    have = {(r["period"], r["series"]): r["value"] for r in monthly}
    latest = max((r["period"] for r in monthly), default="0000-00")
    listed: list[tuple[int, int, str]] = []
    if offline:
        for path in sorted(raw_dir.glob("price-breakdown-*.pdf")):
            year, month = path.stem.split("-")[-2:]
            listed.append((int(year), int(month), "(offline)"))
    else:
        try:
            listed = dept.discover_price_breakdowns(
                dept.fetch(dept.PRICE_ARCHIVE_PAGE).decode("utf-8", "replace"))
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"fuel prices: monthly archive page not reachable ({exc})")
    files = []
    for year, month, url in listed:
        period = f"{year}-{month:02d}"
        if period < latest:
            continue
        path = raw_dir / f"price-breakdown-{period}.pdf"
        if not offline and not path.exists():
            try:
                data = dept.fetch(url)
                if not data.startswith(b"%PDF"):
                    raise ValueError("not a PDF")
                path.write_bytes(data)
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"fuel prices {period}: breakdown download failed ({exc})")
                continue
        if not path.exists():
            continue
        try:
            prices, problems = dept.parse_price_breakdown(_pdf_text(path))
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"fuel prices {period}: could not read {path.name} ({exc})")
            continue
        warnings += [f"fuel prices {period} breakdown: {p}" for p in problems]
        files.append({"period": period, "url": url, "file": path.name,
                      "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        for series, price in prices.items():
            if (period, series) in have:
                if abs(have[(period, series)] - price) > 0.005:
                    warnings.append(
                        f"fuel prices {period} {series}: history {have[(period, series)]} "
                        f"but breakdown {price}")
                continue
            monthly.append({
                "country": "ZAF", "period": period, "scenario": "shared", "series": series,
                "value": price, "unit": "cents per litre", "source_file": path.name})
    return files


def _pdf_text(path: Path) -> str:
    from pypdf import PdfReader

    import logging

    logging.getLogger("pypdf").setLevel(logging.ERROR)
    return "\n".join((page.extract_text() or "") for page in PdfReader(str(path)).pages)


def _on_disk(folder: Path) -> list:
    found = []
    for path in sorted(folder.glob("*.xls*")):
        year = re.match(r"(\d{4})", path.name)
        if year and not path.name.startswith("~$"):
            found.append(dept.SourceFile(
                year=int(year.group(1)), url="(offline)", path=path,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    return found


def _sales(files: list, warnings: list[str]) -> tuple[list, list, list]:
    annual: list[dict] = []
    quarterly: list[dict] = []
    part_years: list[int] = []
    for f in files:
        readings = dept.sales_readings(dept.read_workbook(f.path))
        if not readings:
            warnings.append(f"fuel sales {f.year}: product rows not found in {f.path.name}")
            continue
        used, products = next(iter(readings.items()))
        differing = [name for name, other in readings.items() if other != products]
        if differing:
            warnings.append(
                f"fuel sales {f.year}: sheets of {f.path.name} disagree; used '{used}', "
                f"not {differing}")
        base = {"country": "ZAF", "scenario": "shared", "unit": "litres",
                "source_file": f.path.name}
        complete = True
        for product, quarters in products.items():
            for number, value in enumerate(quarters, start=1):
                if value is not None:
                    quarterly.append({**base, "period": f"{f.year}-Q{number}",
                                      "product": product, "value": value})
            if any(q is None for q in quarters):
                complete = False
        if not complete:
            part_years.append(f.year)
            continue
        for product, quarters in products.items():
            annual.append({**base, "period": f.year, "product": product,
                           "value": sum(quarters), "quarters_reported": 4})
    return annual, quarterly, part_years


def _balances(files: list, warnings: list[str]) -> list[dict]:
    out: list[dict] = []
    for f in files:
        try:
            rows, problems = dept.parse_balance(dept.read_workbook(f.path))
        except Exception as exc:  # noqa: BLE001 - report and carry on with other years
            warnings.append(f"energy balance {f.year}: could not open {f.path.name} ({exc})")
            continue
        warnings += [f"energy balance {f.year}: {p}" for p in problems]
        for row in rows:
            out.append({
                "country": "ZAF", "period": f.year, "scenario": "shared",
                "product": row["product"], "flow_key": row["flow_key"], "flow": row["flow"],
                "value": row["value"] * dept.LITRES_PER_KILOLITRE, "unit": "litres",
                "source_file": f.path.name,
            })
    return out


def _write(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
