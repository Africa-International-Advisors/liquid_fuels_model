"""Industrial / mining diesel demand. v1 status: HELD (ZAF only).

Compute (HELD pattern, see ``_held.py``):

    volume(t) = base_year_volume * (gdp_pc(t) / gdp_pc(base_year)) ** elasticity

v1 lumps mining + manufacturing + construction into a single ZAF bucket.
Sub-segment detail is a future enhancement once sector-level data is sourced.

Inputs come from ``industrial.yaml``:
  - base_year_volume (provisional placeholder — needs sourcing)
  - elasticity (provisional ~1.0 vs GDP/capita)
"""
from __future__ import annotations

import pandas as pd

from ..assumptions import AssumptionProvider
from ..core.geography import ISO3_LIST
from ..core.time import END_YEAR, START_YEAR, ExpansionRule, expand_annual_to_monthly
from ..run import Run
from ._held import gdp_per_capita_series, held_trajectory
from .base import DemandResult, SegmentStatus

name = "industrial"
status = SegmentStatus.HELD


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


def compute_country_annual(
    provider: AssumptionProvider, run: Run, iso3: str, *,
    start_year: int = START_YEAR,
) -> pd.DataFrame | None:
    base_block = provider.get("industrial", "base_year_volume", run).value.get(iso3) or {}
    base_volume = base_block.get("value")
    base_year = base_block.get("year")
    elasticity = provider.get("industrial", "elasticity", run).value.get(iso3)

    if base_volume is None or base_year is None or elasticity is None:
        return None

    gdp_pc = gdp_per_capita_series(provider, run, iso3)
    series = held_trajectory(
        base_volume=float(base_volume),
        base_year=int(base_year),
        elasticity=float(elasticity),
        gdp_pc=gdp_pc,
        start_year=start_year,
        end_year=END_YEAR,
    )
    if series.empty:
        return None
    return pd.DataFrame({"diesel_50ppm": series.values}, index=series.index).rename_axis("year")


def _to_monthly_long(annual: pd.DataFrame, iso3: str) -> pd.DataFrame:
    rule = ExpansionRule(kind="flat")
    annual_series = pd.Series(
        annual["diesel_50ppm"].values,
        index=pd.PeriodIndex([str(y) for y in annual.index], freq="Y"),
        name="volume",
    )
    monthly = expand_annual_to_monthly(annual_series, rule) / 12.0
    return pd.DataFrame({
        "country": iso3,
        "product": "diesel_50ppm",
        "period": monthly.index,
        "volume": monthly.values,
    })
