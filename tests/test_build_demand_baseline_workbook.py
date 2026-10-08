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
        "History", "Sector history", "Diesel by use", "Vehicle history", "HML response", "Gap status", "Checks",
        "History sources"]
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
    brought_in = history["Gauteng petrol"][at[2023]]                         # estimate, linked from section 6
    assert str(brought_in.value).startswith("=IF(ISNUMBER(") and brought_in.font.italic
    assert brought_in.fill.fgColor.rgb == build.FILL["estimate"]
    assert history["Gauteng petrol"][at[2022]].fill.fgColor.rgb == build.FILL["observation"]
    assert "ESTIMATES" in history["Gauteng petrol"][4].value
    assert history["Gauteng petrol"][at[2025]].value.startswith("=")          # blank until a national figure exists
    for product in ("petrol", "diesel"):
        assert "No national" in history[f"Why 2025 is blank, {product}"][4].value
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


def test_vehicle_sheet_carries_observed_stock_and_the_models_settings():
    d = build.load(VINTAGE / "timeseries", VINTAGE / "reference")
    vehicles = _rows(load_workbook(ROOT / build.OUT)["Vehicle history"])
    at = {year: build.FIRST - 1 + build.YEARS.index(year) for year in build.YEARS}
    assert vehicles["Cars"][at[2025]].value == d["stock"][("cars", 2025)]
    assert vehicles["Cars, new sales"][at[2024]].value == d["new_sales"][("cars", 2024)]
    assert vehicles["Diesel vehicles registered"][at[2023]].value == d["by_fuel_2023"]["diesel"]
    assert vehicles["Cars retirement rate"][3].value == pytest.approx(d["model_vehicles"]["scrappage_rate"]["passenger"] * 100)
    assert vehicles["Cars share of new sales"][3].value == pytest.approx(78)
    for label in ("Cars retired", "Cars retirement rate", "Implied less registered diesel vehicles",
                  "Distance implied by petrol sales"):
        assert str(vehicles[label][at[2023]].value).startswith("="), label


def test_diesel_by_use_splits_road_diesel_with_the_studys_shares():
    d = build.load(VINTAGE / "timeseries", VINTAGE / "reference")
    sheet = _rows(load_workbook(ROOT / build.OUT)["Diesel by use"])
    at = {year: build.FIRST - 1 + build.YEARS.index(year) for year in build.YEARS}
    shares = [sheet[group][3].value for group in build.VEHICLE_GROUPS]
    assert sum(shares) == pytest.approx(100)
    assert sheet["Heavy vehicles"][3].value == pytest.approx(60.5, abs=0.1)
    assert set(d["study_classes"]["Heavy vehicles"]) == {f"HCV{n}Diesel" for n in range(1, 10)}
    assert d["study_classes"]["Light vehicles"] == ["LCVDiesel"]
    assert "MBTDiesel" in d["study_classes"]["Passenger vehicles"] and "BusDiesel" in d["study_classes"]["Passenger vehicles"]
    assert "HCV1Diesel" in sheet["Heavy vehicles: classes"][4].value
    assert sheet["Fuel bought by road freight businesses"][at[2023]].value == pytest.approx(d["freight_floor"][2023][0])
    for label in ("Road vehicles and uses not listed above", "Heavy vehicles", "Sum of the six branches"):
        assert str(sheet[label][at[2023]].value).startswith("="), label


def test_lever_response_gap_status_jet_and_sources_are_in_the_workbook():
    wb = load_workbook(ROOT / build.OUT)
    levers = [row for row in wb["HML response"].iter_rows(min_row=5, values_only=True) if row[0]]
    assert len(levers) == 29                                                 # 20 proposed levers and 9 added
    results = [row[9] for row in levers]
    assert results.count("added lever") == 9 and "replacement proposed" in results and "no change" in results
    gaps = [row[0] for row in wb["Gap status"].iter_rows(min_row=5, values_only=True) if row[0]]
    assert gaps == [f"G{n:02d}" for n in range(1, 14)]
    history = _rows(wb["History"])
    at = {year: build.FIRST - 1 + build.YEARS.index(year) for year in build.YEARS}
    assert history["Department national file, jet"][at[2023]].value == pytest.approx(1843.97, abs=0.01)
    assert str(history["Jet sold per aircraft movement"][at[2024]].value).startswith("=")
    used_for = " ".join(str(row[0]) for row in wb["History sources"].iter_rows(min_row=5, values_only=True))
    for sheet in ("History section 7", "Diesel by use", "Vehicle history", "HML response"):
        assert sheet in used_for, sheet
