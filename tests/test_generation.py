"""Generation compute — exercise the OCGT calculation against the real 2026 vintage."""
from __future__ import annotations

import pandas as pd
import pytest

from lfm.assumptions import YamlDirectoryProvider
from lfm.core.time import END_YEAR, START_YEAR
from lfm.demand import generation
from lfm.demand.base import SegmentStatus
from lfm.run import Run


@pytest.fixture
def provider() -> YamlDirectoryProvider:
    return YamlDirectoryProvider()


def test_status_is_modelled():
    assert generation.status == SegmentStatus.MODELLED


def test_compute_returns_long_format_zaf_diesel_only(provider):
    run = Run(vintage="2026", scenario="high_demand")
    result = generation.compute_demand(provider, run)
    assert {"country", "product", "period", "volume"}.issubset(result.frame.columns)
    # BLNS has no OCGT data in v1.
    assert set(result.frame["country"].unique()) == {"ZAF"}
    # Generation produces only diesel.
    assert set(result.frame["product"].unique()) == {"diesel_50ppm"}


def test_volumes_are_positive_and_finite(provider):
    run = Run(vintage="2026", scenario="high_demand")
    df = generation.compute_demand(provider, run).frame
    assert (df["volume"] >= 0).all()
    assert df["volume"].notna().all()


def test_horizon_starts_at_or_after_start_year_ends_at_end_year(provider):
    run = Run(vintage="2026", scenario="high_demand")
    df = generation.compute_demand(provider, run).frame
    years = sorted({p.year for p in df["period"]})
    assert years[0] >= START_YEAR
    assert years[-1] == END_YEAR


def test_2024_volume_in_plausible_range(provider):
    """For ZAF 2024 with 3072 MW operational fleet at the xlsx-given load
    factor (~0.55), the OCGT diesel volume should be on the order of
    a few billion litres — sanity check, not a calibration assertion."""
    run = Run(vintage="2026", scenario="high_demand")
    df = generation.compute_demand(provider, run).frame
    df = df[(df["product"] == "diesel_50ppm") & (df["country"] == "ZAF")]
    df = df.assign(year=lambda x: x["period"].apply(lambda p: p.year))
    annual_2024_BL = df[df["year"] == 2024]["volume"].sum() / 1e9
    # Wide window: a few hundred million litres up to ~10 BL is the plausible
    # band for OCGT in a heavy load-shedding year.
    assert 0.1 < annual_2024_BL < 10.0
