"""Road-transport liquid fuel demand. v1 status: MODELLED (ZAF only).

Design (locked):
  - Cohort tracking. Each (country, segment, fuel, year_of_manufacture) cohort
    has a fixed L/100km set at year of manufacture and held for the cohort's
    life. Fleet-average L/100km emerges as a stock-weighted sum across cohorts.
    See vehicles.yaml::fuel_consumption application rule and CLAUDE.md decision 4.
  - Backfill 2005 -> START_YEAR-1 from the new-vehicle regression on
    historical GDP/capita, so the START_YEAR fleet has a defensible
    history rather than starting from zero.
  - Forecast START_YEAR -> END_YEAR with EV penetration applied to new
    entries, flat scrappage applied to all cohorts.

Flow per year for ZAF:
  1. new_vehicles_year = max(0, slope * GDP_per_capita_year + intercept)
  2. split into segments via new_vehicle_segment_split
  3. apply EV penetration: new_ICE = segment_total * (1 - pen(year, scenario))
  4. apply petrol/diesel split per segment
  5. add new ICE cohort tagged with year_of_manufacture
  6. apply scrappage to all existing cohorts: stock *= (1 - rate)
  7. compute fleet fuel = sum_over_cohorts(stock * annual_km * L/100km / 100)

Output: long-format ``country, product, period (monthly), volume (litres)``.
For v1 the annual fuel total is flat-expanded across the year's 12 months;
vehicle fuel demand has weak monthly seasonality at this level of aggregation.

BLNS (BWA, LSO, NAM, SWZ) parameters are null and the segment emits an
empty frame for those countries until they are sourced.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from ..assumptions import AssumptionProvider
from ..core.geography import ISO3_LIST
from ..core.time import END_YEAR, START_YEAR, ExpansionRule, expand_annual_to_monthly
from ..run import Run
from .base import DemandResult, SegmentStatus

name = "vehicles"
status = SegmentStatus.MODELLED

# How far back to walk to seed the fleet. The new-vehicle regression's
# explanatory window in the xlsx starts 2010, but historical GDP/capita
# in our extracted timeseries starts 2005 — extra years just give a few
# more cohorts to scrap before START_YEAR.
HISTORY_START = 2005

SEGMENTS = ("passenger", "lcv", "hcv")
FUELS = ("ice_petrol", "ice_diesel")
PRODUCT_BY_FUEL = {"ice_petrol": "petrol_95", "ice_diesel": "diesel_50ppm"}


def compute_demand(provider: AssumptionProvider, run: Run) -> DemandResult:
    monthly_frames: list[pd.DataFrame] = []

    for iso3 in ISO3_LIST:
        annual = compute_country_annual(provider, run, iso3)
        if annual is None or annual.empty:
            continue
        monthly_frames.append(_to_monthly_long(annual, iso3))

    if not monthly_frames:
        frame = pd.DataFrame(columns=["country", "product", "period", "volume"])
    else:
        frame = pd.concat(monthly_frames, ignore_index=True)

    return DemandResult(segment=name, status=status, frame=frame)


# --------------------------------------------------------------------------- #
# Per-country annual compute

def compute_country_annual(
    provider: AssumptionProvider, run: Run, iso3: str, *,
    start_year: int = START_YEAR,
) -> pd.DataFrame | None:
    """Annual ZAF/per-country petrol+diesel volumes from the cohort engine.

    The cohort walk runs HISTORY_START..END_YEAR internally; ``start_year``
    controls only how much of that window is returned. Default truncates to
    the model horizon; pass ``start_year=HISTORY_START`` to get the full
    backfilled history (used by ``scripts/compare_history.py`` to validate
    against observed RSA demand).

    Returns ``None`` when a country's parameters are wholly null (BLNS in v1).
    """
    p = _params(provider, run, iso3)
    if p is None:
        return None

    gdp_pc = _gdp_per_capita_series(provider, run, iso3)
    if gdp_pc.empty:
        return None

    # Cohort book: maps (segment, fuel, year_of_manufacture) -> stock count.
    cohorts: dict[tuple[str, str, int], float] = {}

    # Track per-cohort fixed L/100km so efficiency improvement applies to
    # new entries only.
    cohort_lpk: dict[tuple[str, str, int], float] = {}

    cumulative_eff_diesel: dict[int, float] = {}
    cumulative_eff_gasoline: dict[int, float] = {}
    eff_diesel = _eff_series(provider, run, "diesel")
    eff_gasoline = _eff_series(provider, run, "gasoline")

    annual_records: list[dict] = []

    for year in range(HISTORY_START, END_YEAR + 1):
        # 1) New vehicle demand from regression on GDP/capita.
        gdp_year = gdp_pc.get(year)
        if gdp_year is None or pd.isna(gdp_year):
            new_total = 0.0
        else:
            new_total = max(0.0, p["regression"]["slope"] * gdp_year + p["regression"]["intercept"])

        # 2) Split into segments.
        seg_split = p["new_vehicle_segment_split"]

        # 3) EV penetration for this year and scenario.
        pen = _ev_penetration(p["ev_scurve"], year)

        # 4) Update cumulative efficiency improvement.
        cumulative_eff_diesel[year] = (cumulative_eff_diesel.get(year - 1, 1.0)
                                       * (1.0 - eff_diesel.get(year, 0.0)))
        cumulative_eff_gasoline[year] = (cumulative_eff_gasoline.get(year - 1, 1.0)
                                         * (1.0 - eff_gasoline.get(year, 0.0)))

        # 5) Apply petrol/diesel split, add new cohorts.
        for seg in SEGMENTS:
            seg_share = seg_split.get(seg, 0.0)
            seg_new = new_total * seg_share
            seg_new_ice = seg_new * (1.0 - pen)
            split = p["petrol_diesel_split"][seg]
            for fuel, fuel_label in (("ice_petrol", "petrol"), ("ice_diesel", "diesel")):
                fuel_share = split.get(fuel_label, 0.0) or 0.0
                cohort_size = seg_new_ice * fuel_share
                if cohort_size <= 0:
                    continue
                key = (seg, fuel, year)
                cohorts[key] = cohorts.get(key, 0.0) + cohort_size
                # Cohort L/100km baseline x cumulative efficiency factor.
                base_lpk = (p["fuel_consumption"][seg] or {}).get(fuel)
                if base_lpk is None:
                    continue
                eff_factor = (cumulative_eff_diesel[year] if fuel == "ice_diesel"
                              else cumulative_eff_gasoline[year])
                cohort_lpk[key] = base_lpk * eff_factor

        # 6) Scrappage on every existing cohort.
        scrap = p["scrappage_rate"]
        for key in list(cohorts.keys()):
            seg = key[0]
            rate = scrap.get(seg, 0.0) or 0.0
            cohorts[key] *= (1.0 - rate)

        # 7) Compute fleet fuel = sum over cohorts of stock * km * L/100km / 100.
        petrol_litres = 0.0
        diesel_litres = 0.0
        for key, stock in cohorts.items():
            seg, fuel, _yom = key
            km = (p["annual_km_per_vehicle"].get(seg) or 0.0)
            lpk = cohort_lpk.get(key)
            if lpk is None:
                continue
            litres = stock * km * (lpk / 100.0)
            if fuel == "ice_petrol":
                petrol_litres += litres
            else:
                diesel_litres += litres

        annual_records.append({
            "year": year,
            "petrol_95": petrol_litres,
            "diesel_50ppm": diesel_litres,
        })

    df = pd.DataFrame(annual_records).set_index("year")
    return df.loc[start_year:END_YEAR]


# --------------------------------------------------------------------------- #
# Parameter assembly

def _params(provider: AssumptionProvider, run: Run, iso3: str) -> dict | None:
    """Pull every vehicle parameter the compute needs for one country.
    Returns None if the country's parameters are wholly null (BLNS in v1)."""

    def by_country(domain: str, key: str) -> dict:
        return provider.get(domain, key, run).value

    ev_scurve = by_country("vehicles", "ev_scurve").get(iso3)
    if ev_scurve is None:
        return None

    regression = by_country("vehicles", "new_vehicle_regression").get(iso3) or {}
    if regression.get("slope") is None:
        return None

    annual_km = by_country("vehicles", "annual_km_per_vehicle").get(iso3) or {}
    if not annual_km or all(v is None for v in annual_km.values()):
        return None

    fuel_consumption = by_country("vehicles", "fuel_consumption").get(iso3) or {}
    petrol_diesel_split = by_country("vehicles", "petrol_diesel_split").get(iso3) or {}
    scrappage_rate = by_country("vehicles", "scrappage_rate").get(iso3) or {}
    new_vehicle_segment_split = by_country("vehicles", "new_vehicle_segment_split").get(iso3) or {}

    return {
        "ev_scurve": ev_scurve,
        "regression": regression,
        "annual_km_per_vehicle": annual_km,
        "fuel_consumption": fuel_consumption,
        "petrol_diesel_split": petrol_diesel_split,
        "scrappage_rate": scrappage_rate,
        "new_vehicle_segment_split": new_vehicle_segment_split,
    }


def _gdp_per_capita_series(provider: AssumptionProvider, run: Run, iso3: str) -> pd.Series:
    """Long-format CSV -> a {year: value} Series for the active country and scenario."""
    df = provider.get("macro", "gdp_per_capita", run).value
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.Series(dtype=float)
    sub = df[df["country"] == iso3].copy()
    sub["period"] = sub["period"].astype(int)
    return sub.set_index("period")["value"].astype(float).sort_index()


def _eff_series(provider: AssumptionProvider, run: Run, fuel: str) -> dict[int, float]:
    """Annual fractional efficiency improvement {year: rate}."""
    df = provider.get("vehicles", f"efficiency_improvement.{fuel}", run).value
    if not isinstance(df, pd.DataFrame) or df.empty:
        return {}
    sub = df[df["country"] == "ZAF"].copy()  # v1 ZAF only
    sub["period"] = sub["period"].astype(int)
    return dict(zip(sub["period"], sub["value"].astype(float)))


# --------------------------------------------------------------------------- #
# EV S-curve

def _ev_penetration(scurve: dict, year: int) -> float:
    max_pen = scurve.get("max_penetration")
    midpoint = scurve.get("midpoint")
    slope = scurve.get("slope")
    if max_pen is None or midpoint is None or slope is None:
        return 0.0
    raw = 1.0 / (1.0 + math.exp((midpoint - year) / slope))
    return raw * max_pen


# --------------------------------------------------------------------------- #
# Annual -> monthly long format

def _to_monthly_long(annual: pd.DataFrame, iso3: str) -> pd.DataFrame:
    rule = ExpansionRule(kind="flat")
    out: list[pd.DataFrame] = []
    for product in ("petrol_95", "diesel_50ppm"):
        annual_series = pd.Series(
            annual[product].values,
            index=pd.PeriodIndex([str(y) for y in annual.index], freq="Y"),
            name="volume",
        )
        # Flat expansion repeats the annual value 12x; divide by 12 so that
        # the monthly series sums back to the annual value.
        monthly = expand_annual_to_monthly(annual_series, rule) / 12.0
        df = pd.DataFrame({
            "country": iso3,
            "product": product,
            "period": monthly.index,
            "volume": monthly.values,
        })
        out.append(df)
    return pd.concat(out, ignore_index=True)
