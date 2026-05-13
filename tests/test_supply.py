"""Supply + balance compute — exercise refinery output and demand-supply balance."""
from __future__ import annotations

import pandas as pd
import pytest

from lfm.assumptions import YamlDirectoryProvider
from lfm.demand import vehicles
from lfm.run import Run
from lfm.supply.flows import (
    DEMAND_TO_REFINERY_PRODUCT,
    REFINERY_PRODUCTS,
    compute_balance,
    compute_supply,
)


@pytest.fixture
def provider() -> YamlDirectoryProvider:
    return YamlDirectoryProvider()


@pytest.fixture
def run() -> Run:
    return Run(vintage="2026", scenario="high_demand")


# --------------------------------------------------------------------------- #
# Supply

def test_supply_returns_long_format_with_expected_columns(provider, run):
    df = compute_supply(provider, run)
    assert not df.empty
    assert {"country", "refinery_product", "period", "supply_litres"}.issubset(df.columns)


def test_supply_only_zaf_in_v1(provider, run):
    """v1: only ZAF has refineries declared in supply.yaml."""
    df = compute_supply(provider, run)
    assert set(df["country"].unique()) == {"ZAF"}


def test_supply_covers_three_refinery_products(provider, run):
    df = compute_supply(provider, run)
    assert set(df["refinery_product"].unique()).issubset(set(REFINERY_PRODUCTS))
    # All three should appear at least once.
    assert {"gasoline", "diesel", "jet_a1"}.issubset(set(df["refinery_product"].unique()))


def test_supply_volumes_are_positive_and_finite(provider, run):
    df = compute_supply(provider, run)
    assert (df["supply_litres"] >= 0).all()
    assert df["supply_litres"].notna().all()


def test_supply_diverges_between_scenarios_in_forecast(provider):
    """The xlsx Production_High vs Production_Low diverge from ~2026; supply totals should follow."""
    hi = compute_supply(provider, Run(vintage="2026", scenario="high_demand"))
    lo = compute_supply(provider, Run(vintage="2026", scenario="low_demand"))

    def total_2030(df: pd.DataFrame) -> float:
        return df[df["period"] == 2030]["supply_litres"].sum()

    assert total_2030(hi) != pytest.approx(total_2030(lo))


# --------------------------------------------------------------------------- #
# Balance

def test_balance_columns_and_invariant(provider, run):
    """deficit_litres MUST equal demand_litres - supply_litres exactly."""
    veh = vehicles.compute_demand(provider, run).frame
    supply = compute_supply(provider, run)
    bal = compute_balance(veh, supply)

    assert {
        "country", "refinery_product", "period",
        "demand_litres", "supply_litres", "deficit_litres",
    } == set(bal.columns)
    assert ((bal["demand_litres"] - bal["supply_litres"]) == bal["deficit_litres"]).all()


def test_balance_no_domestic_supply_for_marine_products():
    """fuel_oil and diesel_500ppm (marine) have no refinery yield in v1 —
    they should appear with supply_litres == 0."""
    fake_demand = pd.DataFrame({
        "country": ["ZAF", "ZAF"],
        "product": ["fuel_oil", "diesel_500ppm"],
        "period": [pd.Period("2030-06", freq="M"), pd.Period("2030-06", freq="M")],
        "volume": [1_000_000.0, 2_000_000.0],
    })
    # diesel_500ppm rolls up to "diesel"; fuel_oil stays as itself (no mapping).
    bal = compute_balance(fake_demand, pd.DataFrame(
        columns=["country", "refinery_product", "period", "supply_litres"],
    ))
    fuel_oil_rows = bal[bal["refinery_product"] == "fuel_oil"]
    assert not fuel_oil_rows.empty
    assert (fuel_oil_rows["supply_litres"] == 0).all()
    # 100% of fuel_oil demand becomes deficit.
    assert (fuel_oil_rows["deficit_litres"] == fuel_oil_rows["demand_litres"]).all()


def test_demand_to_refinery_product_mapping():
    """Sanity check the documented rollup contract."""
    assert DEMAND_TO_REFINERY_PRODUCT["petrol_95"] == "gasoline"
    assert DEMAND_TO_REFINERY_PRODUCT["diesel_50ppm"] == "diesel"
    assert DEMAND_TO_REFINERY_PRODUCT["diesel_500ppm"] == "diesel"
    assert DEMAND_TO_REFINERY_PRODUCT["jet_a1"] == "jet_a1"
    assert "fuel_oil" not in DEMAND_TO_REFINERY_PRODUCT  # no domestic yield mapping
