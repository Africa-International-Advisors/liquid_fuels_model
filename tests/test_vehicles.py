"""Vehicles compute — end-to-end against the real 2026 vintage."""
from __future__ import annotations

import pandas as pd
import pytest

from lfm.assumptions import YamlDirectoryProvider
from lfm.core.time import END_YEAR, START_YEAR
from lfm.demand import vehicles
from lfm.demand.base import SegmentStatus
from lfm.run import Run


@pytest.fixture
def provider() -> YamlDirectoryProvider:
    return YamlDirectoryProvider()


def test_status_is_modelled():
    assert vehicles.status == SegmentStatus.MODELLED


def test_compute_returns_long_format_with_zaf_only(provider):
    run = Run(vintage="2026", scenario="high_demand")
    result = vehicles.compute_demand(provider, run)
    assert {"country", "product", "period", "volume"}.issubset(result.frame.columns)
    # BLNS values are null in v1 -> only ZAF emits rows.
    assert set(result.frame["country"].unique()) == {"ZAF"}


def test_volumes_are_positive_and_finite(provider):
    run = Run(vintage="2026", scenario="high_demand")
    df = vehicles.compute_demand(provider, run).frame
    assert (df["volume"] >= 0).all()
    assert df["volume"].notna().all()
    # Vehicles produce both petrol and diesel.
    assert set(df["product"].unique()) == {"petrol_95", "diesel_50ppm"}


def test_horizon_covers_start_to_end_year(provider):
    run = Run(vintage="2026", scenario="high_demand")
    df = vehicles.compute_demand(provider, run).frame
    years = sorted({p.year for p in df["period"]})
    assert years[0] == START_YEAR
    assert years[-1] == END_YEAR


def test_low_demand_yields_less_fuel_than_high_demand(provider):
    """High EV penetration in low_demand should pull total liquid fuel below high_demand
    by some point in the forecast (2050 is far enough past the S-curve midpoint to be
    decisive)."""
    high = vehicles.compute_demand(provider, Run(vintage="2026", scenario="high_demand")).frame
    low = vehicles.compute_demand(provider, Run(vintage="2026", scenario="low_demand")).frame

    def total_2050(df: pd.DataFrame) -> float:
        sub = df[df["period"].apply(lambda p: p.year) == 2050]
        return sub["volume"].sum()

    assert total_2050(low) < total_2050(high)
