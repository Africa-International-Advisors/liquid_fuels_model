"""Monthly time index and annual-to-monthly expansion.

The model is monthly internally (jet seasonality, agri cycles, holiday
driving). Most assumptions arrive annually. This module owns the
expansion: each assumption declares an ``expand`` rule (``flat``,
``linear``, or ``seasonal:<index_name>``) and the engine applies it here.
"""
from __future__ import annotations

from dataclasses import dataclass

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
    """Expand an annual series onto the model's monthly index.

    Implementation deferred — protocol is fixed so callers and the engine
    can be wired up before the expansion logic is filled in.
    """
    raise NotImplementedError("expansion logic to be implemented in v1 build-out")
