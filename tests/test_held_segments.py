"""Tests for the three HELD segments — industrial, marine, agriculture.

Each follows the same pattern:
  - status flag is HELD
  - long-format frame with the right columns
  - volumes positive and finite
  - horizon covers START_YEAR..END_YEAR
"""
from __future__ import annotations

import pandas as pd
import pytest

from lfm.assumptions import YamlDirectoryProvider
from lfm.core.time import END_YEAR, START_YEAR
from lfm.demand import agriculture, industrial, marine
from lfm.demand.base import SegmentStatus
from lfm.run import Run


@pytest.fixture
def provider() -> YamlDirectoryProvider:
    return YamlDirectoryProvider()


@pytest.fixture
def run() -> Run:
    return Run(vintage="2026", scenario="high_demand")


# --------------------------------------------------------------------------- #
# Industrial

def test_industrial_status_held():
    assert industrial.status == SegmentStatus.HELD


def test_industrial_emits_zaf_diesel_only(provider, run):
    df = industrial.compute_demand(provider, run).frame
    assert {"country", "product", "period", "volume"}.issubset(df.columns)
    assert set(df["country"].unique()) == {"ZAF"}
    assert set(df["product"].unique()) == {"diesel_50ppm"}
    assert (df["volume"] >= 0).all()
    years = sorted({p.year for p in df["period"]})
    assert years[0] >= START_YEAR
    assert years[-1] == END_YEAR


# --------------------------------------------------------------------------- #
# Marine

def test_marine_status_held():
    assert marine.status == SegmentStatus.HELD


def test_marine_emits_zaf_with_two_products(provider, run):
    df = marine.compute_demand(provider, run).frame
    assert {"country", "product", "period", "volume"}.issubset(df.columns)
    # ZAF emits for v1. NAM ports (Walvis Bay, Lüderitz) are scaffolded in
    # marine.yaml but their compute drops because we haven't sourced NAM
    # GDP/capita yet — only ZAF is in macro.yaml's timeseries CSV. When NAM
    # macro data lands, this test should switch to expect {"ZAF", "NAM"}.
    countries = set(df["country"].unique())
    assert countries == {"ZAF"}
    # Two products from the bunkering split.
    assert {"fuel_oil", "diesel_500ppm"}.issubset(set(df["product"].unique()))
    assert (df["volume"] >= 0).all()


# --------------------------------------------------------------------------- #
# Agriculture

def test_agriculture_status_held():
    assert agriculture.status == SegmentStatus.HELD


def test_agriculture_emits_zaf_diesel_only(provider, run):
    df = agriculture.compute_demand(provider, run).frame
    assert {"country", "product", "period", "volume"}.issubset(df.columns)
    assert set(df["country"].unique()) == {"ZAF"}
    assert set(df["product"].unique()) == {"diesel_50ppm"}
    assert (df["volume"] >= 0).all()


def test_agriculture_low_elasticity_means_small_2050_change(provider, run):
    """Elasticity 0.2 on GDP ratio -> 2050 volume should be relatively close
    to base-year volume even after 26 years of GDP growth."""
    df = agriculture.compute_country_annual(provider, run, "ZAF")
    base = df.loc[2024, "diesel_50ppm"]
    far = df.loc[2050, "diesel_50ppm"]
    # 2050 should be within +/- 50% of 2024 given the low elasticity.
    assert 0.5 * base < far < 1.5 * base
