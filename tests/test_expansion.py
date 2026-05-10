"""Annual->monthly expansion rules."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from lfm.core.time import ExpansionRule, expand_annual_to_monthly


def annual(values: list[float], start: int = 2024) -> pd.Series:
    idx = pd.period_range(start=str(start), periods=len(values), freq="Y")
    return pd.Series(values, index=idx, name="x")


def test_flat_repeats_annual_value_twelve_times():
    a = annual([100.0, 200.0])
    out = expand_annual_to_monthly(a, ExpansionRule(kind="flat"))
    assert len(out) == 24
    # The first 12 months are 100, the next 12 are 200.
    assert (out.iloc[:12] == 100.0).all()
    assert (out.iloc[12:] == 200.0).all()


def test_linear_interpolates_between_annual_anchors():
    a = annual([100.0, 200.0])
    out = expand_annual_to_monthly(a, ExpansionRule(kind="linear"))
    assert len(out) == 24
    # Anchors at June: index 5 == 100, index 17 == 200.
    assert out.iloc[5] == pytest.approx(100.0)
    assert out.iloc[17] == pytest.approx(200.0)
    # Midpoint between June year 1 and June year 2 (index 11 = December year 1)
    # should be 150.
    assert out.iloc[11] == pytest.approx(150.0, abs=1e-6)


def test_seasonal_applies_index_multiplicatively():
    a = annual([120.0])
    seasonal = pd.Series(
        # Jan high, July low, etc. — average to 1.0.
        [1.5, 1.5, 1.0, 1.0, 1.0, 0.5, 0.5, 1.0, 1.0, 1.0, 1.5, 0.5],
        index=range(1, 13),
    )
    out = expand_annual_to_monthly(
        a,
        ExpansionRule(kind="seasonal", seasonal_index="test"),
        seasonal_indices={"test": seasonal},
    )
    assert len(out) == 12
    assert out.iloc[0] == pytest.approx(120.0 * 1.5)
    assert out.iloc[5] == pytest.approx(120.0 * 0.5)


def test_unknown_rule_raises():
    with pytest.raises(ValueError):
        expand_annual_to_monthly(annual([1.0]), ExpansionRule(kind="bogus"))
