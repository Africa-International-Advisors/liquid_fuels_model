"""YAML provider — exercises each shape of resolution against the real 2026 vintage."""
from __future__ import annotations

import pandas as pd
import pytest

from lfm.assumptions import YamlDirectoryProvider
from lfm.run import Run


@pytest.fixture
def provider() -> YamlDirectoryProvider:
    return YamlDirectoryProvider()


@pytest.fixture
def high() -> Run:
    return Run(vintage="2026", scenario="high_demand")


@pytest.fixture
def low() -> Run:
    return Run(vintage="2026", scenario="low_demand")


def test_scalar_value(provider, high):
    a = provider.get("macro", "crude_oil_litres_per_barrel", high)
    assert a.value == pytest.approx(158.987)
    assert a.scenario is None  # shared


def test_by_country_returns_per_country_dict(provider, high):
    a = provider.get("vehicles", "annual_km_per_vehicle", high)
    assert isinstance(a.value, dict)
    assert a.value["ZAF"] == {"passenger": 17000, "lcv": 28000, "hcv": 70000}
    assert a.value["BWA"] is None or all(v is None for v in a.value["BWA"].values())


def test_by_scenario_resolves_to_active_scenario(provider, high, low):
    a_high = provider.get("vehicles", "ev_scurve", high).value["ZAF"]
    a_low = provider.get("vehicles", "ev_scurve", low).value["ZAF"]
    # high_demand maps to xlsx EV_Low_Penetration
    assert a_high["max_penetration"] == pytest.approx(0.30)
    assert a_high["midpoint"] == 2040
    # low_demand maps to xlsx EV_High_Penetration
    assert a_low["max_penetration"] == pytest.approx(0.90)
    assert a_low["midpoint"] == 2036


def test_csv_returns_dataframe_filtered_by_scenario(provider, high):
    a = provider.get("macro", "gdp_per_capita", high)
    df = a.value
    assert isinstance(df, pd.DataFrame)
    assert {"country", "period", "scenario", "value"}.issubset(df.columns)
    # Filter sanity: only "shared" rows or the active scenario.
    assert set(df["scenario"].unique()).issubset({"high_demand", "shared"})


def test_dotted_key_descends_nested_block(provider, high):
    a = provider.get("vehicles", "efficiency_improvement.diesel", high)
    df = a.value
    assert isinstance(df, pd.DataFrame)
    assert (df["scenario"] == "high_demand").all()


def test_missing_key_raises(provider, high):
    with pytest.raises(KeyError):
        provider.get("vehicles", "no_such_key", high)
