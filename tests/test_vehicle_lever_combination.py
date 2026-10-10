"""The vehicle engine multiplies the electric share and the efficiency gain; it does not add them (DR07 double-count check)."""
import pytest

from lfm.assumptions import YamlDirectoryProvider
from lfm.model.demand import vehicles
from lfm.run import Run

SHARE, GAIN = 0.10, 0.02          # electric share of new sales; efficiency gain a year


def _fuel(monkeypatch, share: float, gain: float):
    """Road fuel by year with a constant electric share and a constant yearly efficiency gain."""
    monkeypatch.setattr(vehicles, "_ev_penetration", lambda scurve, year: share)
    monkeypatch.setattr(vehicles, "_eff_series", lambda provider, run, fuel: {year: gain for year in range(1900, 2100)})
    provider = YamlDirectoryProvider()
    frame = vehicles.compute_country_annual(provider, Run(vintage="2026", scenario="high_demand"), "ZAF")
    return frame["petrol_95"] + frame["diesel_50ppm"]


def test_electric_share_and_efficiency_multiply(monkeypatch):
    neither = _fuel(monkeypatch, 0.0, 0.0)
    electric = _fuel(monkeypatch, SHARE, 0.0)
    efficient = _fuel(monkeypatch, 0.0, GAIN)
    both = _fuel(monkeypatch, SHARE, GAIN)
    # The electric share removes vehicles; efficiency lowers what the rest burn. Every cohort is built inside the walk,
    # so a constant share scales the whole fleet.
    assert (electric / neither).round(9).eq(1 - SHARE).all()
    assert (both / efficient).round(9).eq(1 - SHARE).all()
    year = both.index[-1]
    saved_both = neither[year] - both[year]
    saved_apart = (neither[year] - electric[year]) + (neither[year] - efficient[year])
    assert saved_both < saved_apart                                   # adding the two savings would overstate the total
    assert saved_apart - saved_both == pytest.approx(SHARE * (neither[year] - efficient[year]))
