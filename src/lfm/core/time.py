"""Monthly time index and annual-to-monthly expansion.

The model is monthly internally (jet seasonality, agri cycles, holiday
driving). Most assumptions arrive annually. This module owns the
expansion: each assumption declares an ``expand`` rule (``flat``,
``linear``, or ``seasonal:<index_name>``) and the engine applies it here.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

START_YEAR = 2024
END_YEAR = 2050


def monthly_index(start_year: int = START_YEAR, end_year: int = END_YEAR) -> pd.PeriodIndex:
    """Inclusive month-end PeriodIndex covering the model horizon."""
    return pd.period_range(start=f"{start_year}-01", end=f"{end_year}-12", freq="M")


def annual_index(start_year: int = START_YEAR, end_year: int = END_YEAR) -> pd.PeriodIndex:
    return pd.period_range(start=str(start_year), end=str(end_year), freq="Y")


@dataclass(frozen=True)
class ExpansionRule:
    """How an annual assumption series is expanded onto the monthly index.

    kind:
      - ``flat``     : repeat the annual value across all 12 months
      - ``linear``   : interpolate linearly between consecutive annual points
      - ``seasonal`` : apply a multiplicative seasonal index named in ``seasonal_index``
    """

    kind: str
    seasonal_index: str | None = None


def expand_annual_to_monthly(
    annual: pd.Series,
    rule: ExpansionRule,
    seasonal_indices: dict[str, pd.Series] | None = None,
) -> pd.Series:
    """Expand an annual series onto a month-end PeriodIndex.

    Args:
        annual: Series with an annual ``PeriodIndex`` (freq "Y") and numeric values.
        rule: ExpansionRule selecting flat / linear / seasonal.
        seasonal_indices: required when rule.kind == "seasonal". A dict mapping
            index name -> pd.Series of length 12 with month numbers as index.

    Returns:
        Series with a monthly ``PeriodIndex`` (freq "M") covering each annual
        period's 12 months.
    """
    if not isinstance(annual.index, pd.PeriodIndex) or annual.index.freqstr not in {"Y-DEC", "A-DEC"}:
        # Pandas changed the canonical alias from A-DEC to Y-DEC; accept either.
        raise ValueError(
            f"expected annual PeriodIndex (freq Y-DEC/A-DEC); got {annual.index.freqstr!r}"
        )

    months = pd.period_range(
        start=f"{annual.index.min().year}-01",
        end=f"{annual.index.max().year}-12",
        freq="M",
    )

    if rule.kind == "flat":
        # Each annual value repeats across its 12 months.
        repeated = np.repeat(annual.values, 12)
        return pd.Series(repeated, index=months, name=annual.name)

    if rule.kind == "linear":
        # Anchor each annual value at the mid-month of the year (June=index 6),
        # then linearly interpolate. End-of-series tails get flat fill.
        s = pd.Series(np.nan, index=months, name=annual.name)
        for period, value in zip(annual.index, annual.values):
            june = pd.Period(year=period.year, month=6, freq="M")
            if june in s.index:
                s.loc[june] = value
        s = s.interpolate(method="linear", limit_direction="both")
        return s

    if rule.kind == "seasonal":
        if rule.seasonal_index is None or seasonal_indices is None:
            raise ValueError("seasonal expand requires seasonal_index name + seasonal_indices dict")
        idx = seasonal_indices.get(rule.seasonal_index)
        if idx is None:
            raise KeyError(f"seasonal index {rule.seasonal_index!r} not provided")
        # Multiplicative seasonal pattern on top of flat-expanded annual.
        flat = np.repeat(annual.values, 12)
        # Tile the 12-month index across each year.
        monthly_factors = np.tile(idx.reindex(range(1, 13)).values, len(annual))
        return pd.Series(flat * monthly_factors, index=months, name=annual.name)

    raise ValueError(f"unknown expansion kind: {rule.kind!r}")
