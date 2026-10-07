"""The extended demand baseline workbook: sheets present, inputs carried faithfully, Nigel's cells untouched."""
from pathlib import Path

import pytest
from openpyxl import load_workbook

from lfm.scripts import build_demand_baseline_workbook as build

ROOT = Path(__file__).resolve().parents[1]
VINTAGE = ROOT / "assumptions" / "2026"
pytestmark = pytest.mark.skipif(not (ROOT / build.OUT).exists(), reason="workbook not built")


def _rows(ws):
    return {row[0].value: row for row in ws.iter_rows(min_row=5) if isinstance(row[0].value, str)}


def test_history_carries_the_registered_inputs_and_uses_formulas_for_the_balance():
    d = build.load(VINTAGE / "timeseries", VINTAGE / "reference")
    history = _rows(load_workbook(ROOT / build.OUT)["History"])
    at = {year: build.FIRST - 1 + build.YEARS.index(year) for year in build.YEARS}

    assert history["Imports, diesel"][at[2024]].value == pytest.approx(d["sars"][("import", "diesel", 2024)])
    assert history["Imports, diesel"][at[2013]].value is None          # customs is not in litres before 2014
    assert history["Department national file, petrol"][at[2023]].value == pytest.approx(d["dept"][("petrol", 2023)])
    assert history["Department national file, petrol"][at[2024]].value is None
    assert history["Gauteng diesel"][at[2022]].value == pytest.approx(d["province"][("diesel", "GP", 2022)])
    assert history["Production reported, diesel"][at[2022]].value is None    # no energy balance after 2021
    for label in ("Sum of nine provinces, diesel", "Net imports, diesel", "Sales used, diesel",
                  "Sales less net imports, diesel", "Litres levied less recorded sales"):
        assert str(history[label][at[2024]].value).startswith("="), label


def test_only_the_source_selection_changes_in_nigels_sheets():
    before, after = load_workbook(ROOT / build.SOURCE), load_workbook(ROOT / build.OUT)
    assert [ws.title for ws in after.worksheets] == [ws.title for ws in before.worksheets] + [
        "History", "Sector history", "Checks", "History sources"]
    changed = []
    for ws in before.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                new = after[ws.title][cell.coordinate].value
                # Saving rewrites floats to fifteen significant digits; that is not a change.
                same_number = (isinstance(new, (int, float)) and isinstance(cell.value, (int, float))
                               and new == pytest.approx(cell.value, rel=1e-12))
                if new != cell.value and not same_number:
                    changed.append((ws.title, cell.coordinate, cell.value, new))
    assert changed and all(sheet == "Source selection" and (old, new) == ("FIASA", "Department")
                           for sheet, _, old, new in changed)


def test_every_checked_evidence_value_matches_the_inputs():
    results = [row[5].value for row in load_workbook(ROOT / build.OUT)["Checks"].iter_rows(min_row=5)]
    assert results.count("matches") > 50 and "differs" not in results


def test_provincial_estimates_are_marked_and_kept_apart_from_observations():
    from lfm.scripts import backtest_provincial_shares as shares

    history = _rows(load_workbook(ROOT / build.OUT)["History"])
    at = {year: build.FIRST - 1 + build.YEARS.index(year) for year in build.YEARS}
    assert history["Gauteng petrol"][at[2023]].value is None                 # observed rows stay empty after 2022
    estimated = [history[f"{name} share of petrol"][at[2023]].value for name in build.PROVINCE_NAMES.values()]
    assert sum(estimated) == pytest.approx(100)
    quarter1 = shares.share(shares.load(VINTAGE / "timeseries")["quarter1"][("petrol", 2023)])
    assert history["Gauteng share of petrol"][at[2023]].value == pytest.approx(quarter1["GP"] * 100)
    assert history["Gauteng share of petrol"][2].value == "Proposed estimate"
    assert str(history["Gauteng petrol, estimated"][at[2024]].value).startswith("=")
    assert history["Gauteng petrol, estimated"][at[2022]].value is None


def test_quarter_one_shares_beat_holding_last_year_in_the_back_test():
    from lfm.scripts import backtest_provincial_shares as shares

    scores = {(r["product"], r["method"], r["years_ahead"]): r["mean_share_points_misallocated"]
              for r in shares.backtest(shares.load(VINTAGE / "timeseries"))}
    for product in ("petrol", "diesel"):
        assert scores[(product, "quarter1", 0)] < scores[(product, "hold", 1)] < scores[(product, "trend3", 3)]
