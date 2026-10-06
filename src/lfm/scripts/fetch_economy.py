"""Refresh GDP, GDP per capita, population and Treasury's growth forecast.

Pulls the national accounts and population series from the World Bank's data
service and the latest macroeconomic forecast table from the National
Treasury, and writes:

    assumptions/<vintage>/timeseries/macro_worldbank.csv
    assumptions/<vintage>/timeseries/gdp_growth_treasury.csv
    assumptions/<vintage>/timeseries/economy.sources.yaml

CSV schemas:
    macro_worldbank.csv
        country,period,scenario,series,value,unit,basis
        ZAF,2025,shared,gdp_per_capita,72846.27,"rand per person, constant prices",actual
        (series: gdp, gdp_per_capita, population. basis is "projection" only
         for population in years after the last actual; GDP is never projected.)
    gdp_growth_treasury.csv
        country,period,scenario,value,unit,basis,source_file
        (real GDP growth in per cent; basis: actual, estimate or forecast)

The raw responses and the Treasury chapter are kept in ``external/data/raw/economy/``
and ``external/data/raw/treasury/``.

Run (any year — it picks up the latest data and the latest Treasury document):
    python -m lfm.scripts.fetch_economy --vintage 2026

Options:
    --offline    use only what is already in external/data/raw/
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
from lfm.sources import economy, statssa

END_OF_HORIZON = 2050
FIRST_YEAR = 1990
OUTLOOK_YEARS = 25


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    paths = Paths.default()
    out_dir = paths.vintage_dir(args.vintage) / "timeseries"
    if not out_dir.exists():
        sys.exit(f"vintage directory not found: {out_dir}")
    today = date.today()
    warnings: list[str] = []

    # --- World Bank -------------------------------------------------------- #
    raw_wb = paths.data_dir / "raw" / "economy"
    raw_wb.mkdir(parents=True, exist_ok=True)
    end = today.year + OUTLOOK_YEARS
    responses: dict[str, dict] = {}

    def get(name: str, indicator: str, source: int | None = None) -> dict[int, float]:
        path = raw_wb / f"worldbank-{name}.json"
        # The projections database stops at 2050; asking beyond it makes the
        # service answer from the history database instead, without saying so.
        last = min(end, economy.PROJECTIONS_LAST_YEAR) if source else end
        url = economy.world_bank_url(indicator, FIRST_YEAR, last, source=source)
        if not args.offline:
            try:
                path.write_bytes(economy.fetch(url))
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"World Bank {name}: download failed ({exc})")
        if not path.exists():
            warnings.append(f"World Bank {name}: no data on disk")
            return {}
        payload = path.read_bytes()
        values, updated = economy.parse_world_bank(payload)
        responses[name] = {"indicator": indicator, "url": url, "file": path.name,
                           "last_updated_by_world_bank": updated,
                           "sha256": hashlib.sha256(payload).hexdigest()}
        if not values:
            warnings.append(f"World Bank {name}: response had no figures")
        return values

    series = {name: get(name, indicator) for name, (indicator, _) in economy.SERIES.items()}
    current_gdp = get("gdp_current_prices", economy.CURRENT_PRICE_GDP)
    population_outlook = get("population_projection", economy.SERIES["population"][0],
                             economy.PROJECTIONS_SOURCE)
    if not series["gdp"]:
        sys.exit("no GDP series could be read — check the World Bank address")

    price_base = economy.base_year(series["gdp"], current_gdp)
    if price_base is None:
        warnings.append("constant-price base year could not be identified")

    rows: list[dict] = []
    for name, values in series.items():
        unit = economy.SERIES[name][1]
        for year in sorted(values):
            rows.append(_macro_row(year, name, values[year], unit, "actual"))
    last_actual = max(series["population"], default=None)
    if last_actual is not None and max(population_outlook, default=0) <= last_actual:
        warnings.append("population projection: no years beyond the last actual were returned")
    for year in sorted(population_outlook):
        if last_actual is not None and year > last_actual:
            rows.append(_macro_row(year, "population", population_outlook[year],
                                   economy.SERIES["population"][1], "projection"))
    rows.sort(key=lambda r: (r["series"], r["period"]))
    _write(out_dir / "macro_worldbank.csv", rows,
           ["country", "period", "scenario", "series", "value", "unit", "basis"])

    # --- Statistics South Africa (primary for GDP; read from disk) --------- #
    statssa_info = _statssa(paths.data_dir / "raw" / "statssa", out_dir, series["gdp"], warnings)

    # --- National Treasury ------------------------------------------------- #
    raw_treasury = paths.data_dir / "raw" / "treasury"
    document, growth = _treasury(raw_treasury, today.year, args.offline, warnings)
    _write(out_dir / "gdp_growth_treasury.csv", [
        {"country": "ZAF", "period": g["period"], "scenario": "shared", "value": g["value"],
         "unit": "per cent a year, real", "basis": g["basis"],
         "source_file": document.path.name}
        for g in growth
    ], ["country", "period", "scenario", "value", "unit", "basis", "source_file"])

    doc = {
        "retrieved": today.isoformat(),
        "statistics_south_africa": statssa_info,
        "world_bank": {
            "role": "cross-check for GDP; source of GDP per capita and population "
                    "until the Stats SA population file is read",
            "publisher": "World Bank, World Development Indicators and Population "
                         "estimates and projections (data service)",
            "original_sources": "Statistics South Africa national accounts; United Nations "
                                "population estimates and projections (as stated by the World Bank)",
            "constant_price_base_year": price_base,
            "latest_gdp_year": max(series["gdp"]),
            "latest_population_actual": last_actual,
            "population_projected_to": max(population_outlook, default=None),
            "responses": responses,
        },
        "treasury": None if document is None else {
            "publisher": "National Treasury",
            "document": f"{document.label} {document.year}, chapter 2, table "
                        f"'{economy._TABLE_TITLE}'",
            "url": document.url, "file": document.path.name, "sha256": document.sha256,
            "forecast_to": max((g["period"] for g in growth), default=None),
            "note": "Treasury publishes three forecast years. Later years are not "
                    "published and are a model assumption.",
        },
        "warnings": warnings,
    }
    (out_dir / "economy.sources.yaml").write_text(
        yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")

    print(f"[fetch] GDP and GDP per capita to {max(series['gdp'])} "
          f"(constant {price_base} prices); population to {last_actual}, "
          f"projected to {max(population_outlook, default='n/a')}", file=sys.stderr)
    if document is not None:
        shown = ", ".join(f"{g['period']} {g['value']}%" for g in growth)
        print(f"[fetch] Treasury {document.label} {document.year}: {shown}", file=sys.stderr)
    for warning in warnings:
        print(f"[fetch]   WARNING {warning}", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------- #

def _statssa(raw_dir: Path, out_dir: Path, world_bank_gdp: dict[int, float],
             warnings: list[str]) -> dict | None:
    """Write GDP and industry value added from the Stats SA workbook, if present.

    Stats SA cannot be downloaded by script (see lfm/sources/statssa.py); the
    workbook has to be placed in ``external/data/raw/statssa/`` by hand.
    """
    path = statssa.latest_gdp_file(raw_dir) if raw_dir.exists() else None
    if path is None:
        warnings.append(
            "no Stats SA GDP workbook in external/data/raw/statssa/ — download the P0441 "
            "'GDP Time series' file from statssa.gov.za in a browser")
        return None
    series, problems = statssa.parse_constant_price_series(statssa.read_annual_sheet(path))
    warnings += [f"Stats SA {path.name}: {p}" for p in problems]
    rows = [
        {"country": "ZAF", "period": year, "scenario": "shared",
         "series": _slug(s["name"]), "value": s["values"][year],
         "unit": f"rand, {s['price_basis'].lower()}", "code": s["code"],
         "source_file": path.name}
        for s in series for year in sorted(s["values"])
    ]
    for row in rows:
        row["basis"] = "actual"
    gdp = next((s["values"] for s in series if s["name"] == "gdp"), {})
    population_info = _statssa_population(raw_dir, out_dir, gdp, rows, warnings)
    _write(out_dir / "macro_statssa.csv", rows,
           ["country", "period", "scenario", "series", "value", "unit", "basis", "code",
            "source_file"])

    quarterly_info = _statssa_quarterly(path, out_dir, series, warnings)
    provincial_info = _statssa_provincial(raw_dir, out_dir, gdp, warnings)

    differences = {
        year: round((world_bank_gdp[year] / gdp[year] - 1) * 100, 3)
        for year in sorted(set(gdp) & set(world_bank_gdp))
        if abs(world_bank_gdp[year] / gdp[year] - 1) > 0.001
    }
    if differences:
        warnings.append(f"World Bank GDP differs from Stats SA by more than 0.1% in "
                        f"{len(differences)} year(s): {differences}")
    print(f"[fetch] Stats SA GDP {min(gdp)}–{max(gdp)} from {path.name}; "
          f"{len(series) - 1} industry series; World Bank cross-check: "
          f"{'agrees' if not differences else 'DIFFERS'}", file=sys.stderr)
    return {
        "publisher": "Statistics South Africa, Gross domestic product (P0441)",
        "file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "how_obtained": "downloaded by hand in a browser; the Stats SA site refuses "
                        "scripted downloads",
        "latest_year": max(gdp, default=None),
        "series_written": sorted({r["series"] for r in rows}),
        "world_bank_gdp_differences_pct": differences,
        "population": population_info,
        "quarterly": quarterly_info,
        "provincial": provincial_info,
    }


def _statssa_provincial(raw_dir: Path, out_dir: Path, national_gdp: dict[int, float],
                        warnings: list[str]) -> dict | None:
    """Write GDP by province and industry from the P0441.2 release zip, if present."""
    path = statssa.latest_provincial_gdp_file(raw_dir)
    if path is None:
        warnings.append("no Stats SA provincial GDP zip (P0441.2) in external/data/raw/statssa/")
        return None
    try:
        rows, problems = statssa.parse_provincial_gdp(statssa.read_zip_sheets(path))
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"Stats SA provincial GDP: could not read {path.name} ({exc})")
        return None
    warnings += [f"Stats SA {path.name}: {p}" for p in problems]
    if not rows:
        return None
    _write(out_dir / "gdp_by_province_statssa.csv", [
        {"country": "ZAF", "period": r["year"], "scenario": "shared", "province": r["province"],
         "series": _slug(r["industry"]), "value": r["value"], "unit": "rand, constant 2015 prices",
         "source_file": path.name}
        for r in rows
    ], ["country", "period", "scenario", "province", "series", "value", "unit", "source_file"])

    # The nine provinces should add to the national figure in the annual GDP workbook.
    totals: dict[int, float] = {}
    for r in rows:
        if _slug(r["industry"]) == "gdpr_at_market_prices":
            totals[r["year"]] = totals.get(r["year"], 0.0) + r["value"]
    off = {year: round((totals[year] / national_gdp[year] - 1) * 100, 3)
           for year in sorted(set(totals) & set(national_gdp))
           if abs(totals[year] / national_gdp[year] - 1) > 0.005}
    if off:
        warnings.append(f"Stats SA provincial GDP: provinces differ from national GDP by more than "
                        f"0.5% in {len(off)} year(s): {off}")
    years = sorted({r["year"] for r in rows})
    return {"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "first_year": years[0], "latest_year": years[-1],
            "provinces": sorted({r["province"] for r in rows}),
            "industries": sorted({_slug(r["industry"]) for r in rows}),
            "years_differing_from_national_gdp_pct": off}


def _statssa_quarterly(path: Path, out_dir: Path, annual: list[dict],
                       warnings: list[str]) -> dict | None:
    """Write the quarterly series and check that complete years add to the annual ones."""
    try:
        rows = statssa.read_sheet(path, statssa.QUARTERLY_SHEET)
    except ValueError as exc:
        warnings.append(f"Stats SA quarterly: {exc}")
        return None
    series, problems = statssa.parse_quarterly_constant_price_series(rows)
    warnings += [f"Stats SA {path.name} quarterly: {p}" for p in problems]
    if not series:
        return None
    out = [
        {"country": "ZAF", "period": quarter, "scenario": "shared",
         "series": _slug(s["name"]), "value": s["values"][quarter],
         "unit": f"rand, {s['price_basis'].lower()}, not seasonally adjusted",
         "code": s["code"], "source_file": path.name}
        for s in series for quarter in sorted(s["values"])
    ]
    _write(out_dir / "macro_statssa_quarterly.csv", out,
           ["country", "period", "scenario", "series", "value", "unit", "code", "source_file"])

    yearly = {_slug(s["name"]): s["values"] for s in annual}
    mismatches = []
    for s in series:
        name = _slug(s["name"])
        by_year: dict[int, list[float]] = {}
        for quarter, value in s["values"].items():
            by_year.setdefault(int(quarter[:4]), []).append(value)
        for year, values in by_year.items():
            whole = yearly.get(name, {}).get(year)
            if len(values) == 4 and whole and abs(sum(values) / whole - 1) > 0.001:
                mismatches.append(f"{name} {year}")
    if mismatches:
        warnings.append(f"Stats SA quarterly: four quarters differ from the annual figure by "
                        f"more than 0.1% for {len(mismatches)} series-year(s): {mismatches[:6]}")
    periods = sorted({r["period"] for r in out})
    return {"first_quarter": periods[0], "latest_quarter": periods[-1],
            "series": len(series), "series_years_not_matching_annual": len(mismatches)}


def _statssa_population(raw_dir: Path, out_dir: Path, gdp: dict[int, float],
                        rows: list[dict], warnings: list[str]) -> dict | None:
    """Add Stats SA population and GDP per capita, and continue population forward."""
    path = statssa.latest_population_file(raw_dir)
    if path is None:
        warnings.append(
            "no Stats SA population workbook in external/data/raw/statssa/ — download the P0302 "
            "'Country projection by population group, sex and age' file in a browser")
        return None
    population, problems = statssa.parse_population(statssa.read_sheet(path))
    warnings += [f"Stats SA {path.name}: {p}" for p in problems]
    if not population:
        return None

    # The release's own summary table gives the national total; it must agree.
    summary_path = statssa.latest_summary_file(raw_dir)
    printed = None
    if summary_path is not None:
        printed = statssa.parse_summary_total(
            statssa.read_sheet(summary_path, statssa.SUMMARY_SHEET))
        if printed is not None and abs(population[max(population)] - printed) > 1:
            warnings.append(
                f"Stats SA population {max(population)}: rows add to "
                f"{population[max(population)]:,.0f} but the summary table prints {printed:,.0f}")

    base = {"country": "ZAF", "scenario": "shared", "code": "", "source_file": path.name}
    for year in sorted(population):
        rows.append({**base, "period": year, "series": "population",
                     "value": population[year], "unit": "persons", "basis": "actual"})
        if year in gdp:
            rows.append({**base, "period": year, "series": "gdp_per_capita",
                         "value": gdp[year] / population[year],
                         "unit": "rand per person, constant 2015 prices", "basis": "actual"})

    # Beyond the last Stats SA year: continue its own recent growth rate.
    rule = _macro_rule(out_dir.parent)
    span = int(rule.get("years", 5))
    rate, first, last = statssa.average_growth(population, span)
    value = population[last]
    for year in range(last + 1, END_OF_HORIZON + 1):
        value *= 1 + rate
        rows.append({**base, "period": year, "series": "population", "value": value,
                     "unit": "persons",
                     "basis": f"projection: Stats SA {first}-{last} average growth continued"})
    print(f"[fetch] Stats SA population {min(population)}–{last} ({population[last]:,.0f}); "
          f"continued at {rate:.2%} a year ({first}–{last} average)", file=sys.stderr)
    return {
        "publisher": "Statistics South Africa, Mid-year population estimates (P0302)",
        "file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "summary_file": summary_path.name if summary_path else None,
        "summary_total_agrees": None if printed is None
        else abs(population[last] - printed) <= 1,
        "latest_year": last,
        "projection_rule": f"average annual growth over the last {span} years of the "
                           f"Stats SA series ({first}-{last}), continued",
        "projection_rate": round(rate, 6),
        "note": "Stats SA publishes no population figures beyond the release year; "
                "later years are a base-case assumption.",
    }


def _macro_rule(vintage_dir: Path) -> dict:
    doc = yaml.safe_load((vintage_dir / "macro.yaml").read_text(encoding="utf-8")) or {}
    return (doc.get("population_growth_beyond_official_estimates", {}) or {}).get("value", {})


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _treasury(raw_dir: Path, this_year: int, offline: bool, warnings: list[str]):
    """The most recent Treasury chapter whose growth table can be read."""
    if offline:
        candidates = []
        for path in raw_dir.glob("*-chapter-2.pdf"):
            match = re.match(r"(mtbps|budget-review)-(\d{4})-chapter-2", path.name)
            if match:
                candidates.append(economy.TreasuryDocument(
                    label=match.group(1), year=int(match.group(2)), url="(offline)", path=path,
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        candidates.sort(key=lambda d: (d.year, d.label == "mtbps"), reverse=True)
    else:
        candidates = [economy.download_treasury(d, raw_dir)
                      for d in economy.treasury_candidates(this_year)]
    for document in candidates:
        if document is None:
            continue
        growth, problems = economy.parse_treasury_growth(
            economy.pdf_text(document.path), document.year)
        if growth:
            return document, growth
        warnings += [f"Treasury {document.label} {document.year}: {p}" for p in problems]
    warnings.append("no Treasury forecast table could be read")
    return None, []


def _macro_row(year: int, series: str, value: float, unit: str, basis: str) -> dict:
    return {"country": "ZAF", "period": year, "scenario": "shared", "series": series,
            "value": value, "unit": unit, "basis": basis}


def _write(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
