"""Shared HELD-pattern compute used by industrial, marine, agriculture.

A HELD segment doesn't model its sub-dynamics from first principles. It
anchors on an observed base-year volume and scales forward by a driver
(here: GDP/capita) at a sector-specific elasticity:

    volume(t) = base_year_volume * (driver(t) / driver(base_year)) ** elasticity

Per-cohort tracking, S-curves, scrappage etc. live in MODELLED segments.
The HELD helper stays small and predictable so segments differ only in
the assumption shape they pass in.
"""
from __future__ import annotations

import pandas as pd

from ..assumptions import AssumptionProvider
from ..core.time import END_YEAR, START_YEAR
from ..run import Run


def gdp_per_capita_series(provider: AssumptionProvider, run: Run, iso3: str) -> pd.Series:
    """Annual GDP/capita for a country and the active scenario."""
    df = provider.get("macro", "gdp_per_capita", run).value
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.Series(dtype=float)
    sub = df[df["country"] == iso3].copy()
    if sub.empty:
        return pd.Series(dtype=float)
    sub["period"] = sub["period"].astype(int)
    return sub.set_index("period")["value"].astype(float).sort_index()


def held_trajectory(
    base_volume: float,
    base_year: int,
    elasticity: float,
    gdp_pc: pd.Series,
    *,
    start_year: int = START_YEAR,
    end_year: int = END_YEAR,
) -> pd.Series:
    """Compute annual volumes for a HELD segment.

    Uses GDP/capita as the driver. Years where GDP/capita is missing produce
    NaN (caller drops or fills as appropriate). The base year must have a
    GDP/capita observation; otherwise returns an empty series.
    """
    if gdp_pc.empty or base_year not in gdp_pc.index or pd.isna(gdp_pc.loc[base_year]):
        return pd.Series(dtype=float)

    base_gdp = float(gdp_pc.loc[base_year])
    if base_gdp <= 0:
        return pd.Series(dtype=float)

    years = list(range(start_year, end_year + 1))
    out: dict[int, float] = {}
    for year in years:
        g = gdp_pc.get(year)
        if g is None or pd.isna(g):
            continue
        ratio = float(g) / base_gdp
        out[year] = base_volume * (ratio ** elasticity)
    return pd.Series(out).sort_index()
