"""Marine bunkering. v1 status: HELD (per-port, ZAF + NAM only).

Compute:
  - For each port in marine.yaml, apply HELD pattern using the port's host
    country's GDP/capita as the driver (low elasticity since marine doesn't
    track national GDP closely).
  - Sum port volumes to country totals.
  - Split into fuel_oil + diesel_500ppm via product_split.

Landlocked SACU members (BWA, LSO, SWZ) emit nothing.

v1 caveat: NAM ports (Walvis Bay, Lüderitz) are scaffolded in marine.yaml but
their compute drops because NAM GDP/capita isn't in our timeseries CSV
(only ZAF is). When BLNS macro data is sourced and added to macro.yaml's
gdp_per_capita.csv, NAM marine will start emitting automatically.
"""
from __future__ import annotations

import pandas as pd

from ..assumptions import AssumptionProvider
from ..core.time import END_YEAR, START_YEAR, ExpansionRule, expand_annual_to_monthly
from ..run import Run
from ._held import gdp_per_capita_series, held_trajectory
from .base import DemandResult, SegmentStatus

name = "marine"
status = SegmentStatus.HELD


def compute_demand(provider: AssumptionProvider, run: Run) -> DemandResult:
    ports_block = provider.get("marine", "base_year_volume", run).value or {}
    ports = ports_block.get("by_port") if isinstance(ports_block, dict) else None
    if not ports:
        # by_port may be returned as the top-level dict if the loader strips meta keys.
        ports = ports_block if isinstance(ports_block, dict) else {}
    elasticities = provider.get("marine", "elasticity", run).value or {}
    split_block = provider.get("marine", "product_split", run).value or {}
    default_split = split_block.get("default") or {"fuel_oil": 1.0, "diesel_500ppm": 0.0}

    # Aggregate port volumes per country.
    by_country_annual: dict[str, pd.Series] = {}
    for port_name, spec in ports.items():
        if not isinstance(spec, dict):
            continue
        iso3 = spec.get("country")
        base_volume = spec.get("value")
        base_year = spec.get("year")
        if iso3 is None or base_volume is None or base_year is None:
            continue
        elasticity = elasticities.get(iso3)
        if elasticity is None:
            continue
        gdp_pc = gdp_per_capita_series(provider, run, iso3)
        series = held_trajectory(
            base_volume=float(base_volume),
            base_year=int(base_year),
            elasticity=float(elasticity),
            gdp_pc=gdp_pc,
        )
        if series.empty:
            continue
        if iso3 in by_country_annual:
            by_country_annual[iso3] = by_country_annual[iso3].add(series, fill_value=0.0)
        else:
            by_country_annual[iso3] = series

    if not by_country_annual:
        return DemandResult(
            segment=name, status=status,
            frame=pd.DataFrame(columns=["country", "product", "period", "volume"]),
        )

    monthly_frames: list[pd.DataFrame] = []
    for iso3, total_annual in by_country_annual.items():
        monthly_frames.extend(_split_to_monthly_long(total_annual, iso3, default_split))

    return DemandResult(
        segment=name, status=status,
        frame=pd.concat(monthly_frames, ignore_index=True) if monthly_frames
        else pd.DataFrame(columns=["country", "product", "period", "volume"]),
    )


def _split_to_monthly_long(
    annual_total: pd.Series, iso3: str, split: dict[str, float],
) -> list[pd.DataFrame]:
    rule = ExpansionRule(kind="flat")
    out: list[pd.DataFrame] = []
    for product, share in split.items():
        if share is None or share == 0:
            continue
        annual_series = pd.Series(
            annual_total.values * float(share),
            index=pd.PeriodIndex([str(y) for y in annual_total.index], freq="Y"),
            name="volume",
        )
        monthly = expand_annual_to_monthly(annual_series, rule) / 12.0
        out.append(pd.DataFrame({
            "country": iso3,
            "product": product,
            "period": monthly.index,
            "volume": monthly.values,
        }))
    return out


def compute_country_annual(
    provider: AssumptionProvider, run: Run, iso3: str, *,
    start_year: int = START_YEAR,
) -> pd.DataFrame | None:
    """Annual marine volumes summed over the country's ports, all products combined.

    Used by the comparison script — the segment-level frame is per-product;
    this helper rolls back up to total marine for that country.
    """
    full = compute_demand(provider, Run(vintage=run.vintage, scenario=run.scenario))
    df = full.frame
    sub = df[df["country"] == iso3]
    if sub.empty:
        return None
    annual = (
        sub.assign(year=lambda x: x["period"].apply(lambda p: p.year))
        .groupby(["year", "product"], as_index=False)["volume"].sum()
    )
    pivoted = annual.pivot(index="year", columns="product", values="volume")
    return pivoted.loc[start_year:END_YEAR] if not pivoted.empty else None
