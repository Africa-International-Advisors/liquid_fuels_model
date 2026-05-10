"""Aviation compute — exercise the regression against the real 2026 vintage."""
from __future__ import annotations

import pandas as pd
import pytest

from lfm.assumptions import YamlDirectoryProvider
from lfm.core.time import END_YEAR, START_YEAR
from lfm.demand import aviation
from lfm.demand.base import SegmentStatus
from lfm.run import Run


@pytest.fixture
def provider() -> YamlDirectoryProvider:
    return YamlDirectoryProvider()


def test_status_is_modelled():
    assert aviation.status == SegmentStatus.MODELLED


def test_compute_returns_long_format_zaf_jet_only(provider):
    run = Run(vintage="2026", scenario="high_demand")
    result = aviation.compute_demand(provider, run)
    assert {"country", "product", "period", "volume"}.issubset(result.frame.columns)
    # BLNS regression coefficients null in v1 -> only ZAF emits rows.
    assert set(result.frame["country"].unique()) == {"ZAF"}
    # Aviation produces only jet_a1 in v1.
    assert set(result.frame["product"].unique()) == {"jet_a1"}


def test_volumes_are_positive_and_finite(provider):
    run = Run(vintage="2026", scenario="high_demand")
    df = aviation.compute_demand(provider, run).frame
    assert (df["volume"] >= 0).all()
    assert df["volume"].notna().all()


def test_horizon_starts_at_or_after_start_year_ends_at_end_year(provider):
    run = Run(vintage="2026", scenario="high_demand")
    df = aviation.compute_demand(provider, run).frame
    years = sorted({p.year for p in df["period"]})
    # Aviation needs both GDP/capita and pax to be present; start_year may be
    # later than START_YEAR if pax history is short, but never earlier.
    assert years[0] >= START_YEAR
    assert years[-1] == END_YEAR


def test_high_vs_low_demand_diverge_through_gdp(provider):
    """The pax driver is shared; the GDP/capita driver is scenario-keyed.
    So the two scenarios should produce slightly different jet volumes."""
    high = aviation.compute_demand(
        provider, Run(vintage="2026", scenario="high_demand")
    ).frame
    low = aviation.compute_demand(
        provider, Run(vintage="2026", scenario="low_demand")
    ).frame

    def total_2050(df: pd.DataFrame) -> float:
        return df[df["period"].apply(lambda p: p.year) == 2050]["volume"].sum()

    # Direction depends on which scenario has the higher GDP path; just
    # require they're not identical.
    assert total_2050(high) != pytest.approx(total_2050(low))
