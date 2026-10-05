from pathlib import Path

import pandas as pd
import pytest

from lfm.assumptions import YamlDirectoryProvider
from lfm.model.demand import vehicles
from lfm.reporting.reconciliation import build_reconciliation, midpoint_bridge
from lfm.run import Run


def test_vehicle_diagnostics_preserve_results_and_sum_to_output():
    provider = YamlDirectoryProvider()
    run = Run(vintage='2026', scenario='high_demand')
    expected = vehicles.compute_country_annual(provider, run, 'ZAF')
    rows = []
    actual = vehicles.compute_country_annual(provider, run, 'ZAF', diagnostics=rows)
    pd.testing.assert_frame_equal(actual, expected)
    totals = pd.DataFrame(rows).pivot_table(index='year', columns='product', values='litres', aggfunc='sum')
    for product in actual:
        assert totals[product].to_numpy() == pytest.approx(actual[product].to_numpy())


def test_midpoint_bridge_splits_interaction_equally_and_reverses():
    effects = midpoint_bridge(2, 3, 4, 5)
    assert list(effects.values()) == [8, 6]
    assert list(midpoint_bridge(4, 5, 2, 3).values()) == [-8, -6]


def test_workbook_reconciliation_ties_and_jet_is_calculation_parity(tmp_path):
    workbook = Path(__file__).resolve().parents[1] / 'external/sources/Liquid Fuels Model - Supply Demand, 2025 - Reatile Copy.xlsx'
    result = build_reconciliation(workbook, tmp_path)
    for fuel in ['petrol', 'diesel', 'jet']:
        r = result[fuel]
        assert sum(r['effects'].values()) == pytest.approx(r['python']-r['observed'], abs=.01)
    assert result['jet']['python'] == pytest.approx(result['jet']['excel_calculated'], abs=.01)
    assert result['jet']['observed'] != pytest.approx(result['jet']['excel_calculated'])
