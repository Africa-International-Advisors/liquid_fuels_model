"""The DR07 evidence table: built from the registered inputs, every fact sourced, FIASA and JODI not used."""
import csv
from pathlib import Path

import pytest

from lfm.scripts import build_dr07_demand_evidence as dr07

ROOT = Path(__file__).resolve().parents[1]
VINTAGE = ROOT / "assumptions" / "2026"


def test_committed_table_equals_a_fresh_build_and_every_fact_has_a_source():
    rows = dr07.build(dr07.load(VINTAGE))
    with (ROOT / dr07.OUT).open(encoding="utf-8", newline="") as fh:
        assert list(csv.DictReader(fh)) == rows, "rebuild with: python -m lfm.scripts.build_dr07_demand_evidence --vintage 2026"
    assert all(r["source"] for r in rows)
    assert {r["status"] for r in rows} == {"observed", "inferred", "not available"}
    assert all(bool(r["value"]) != (r["status"] == "not available") for r in rows)          # a value, or marked not available
    assert not any("FIASA" in r["source"] or "JODI" in r["source"] for r in rows)


def test_efficiency_history_and_plant_dates_come_from_the_evidence_points():
    rows = {r["item"]: r for r in dr07.build(dr07.load(VINTAGE))}
    assert rows["Fuel use of new light vehicles, by year"]["value"] == "8.8; 8.6; 7.8; 7.4"
    assert rows["Fuel use of new light vehicles: average change"]["value"] == "-1.3"
    assert rows["Independent diesel plants: contract end"]["period"] == "August and September 2030"
    assert rows["Freight carried by Transnet Freight Rail"]["value"].endswith("151.7; 160.1")
    assert rows["Extra rail freight if the target is met"]["value"] == "90"


def test_the_eight_gaps_searched_on_8_october_are_filled_where_a_source_exists():
    rows = {r["item"]: r for r in dr07.build(dr07.load(VINTAGE))}
    assert rows["Diesel used by rail locomotives"]["value"] == "138"                       # 199 million litres x 69.2%
    assert rows["Freight in tonne-kilometres"]["value"] == "446; 181; 141"
    assert rows["Average age of vehicles"]["value"] == "10.5"
    assert rows["Diesel vehicles by province"]["value"].startswith("1,142,275")              # Gauteng
    assert rows["Fuel use of trucks, lightest to heaviest class"]["value"] == "17.3; 24.6; 44.9; 51.6"
    assert "Ceiling on backup generator diesel" not in rows                                  # the data is recorded as unavailable; no stand-in
    still_missing = {r["item"] for r in rows.values() if r["status"] == "not available"}
    assert still_missing == {
        "Diesel burned in private backup generators",
        "Vehicles by fuel within each class", "Vehicles by year of age", "Electric trucks and electric light commercial vehicles sold",
        "Fuel use of trucks, by year", "Road freight in tonne-kilometres, by year"}
    assert rows["Fuel use of new light vehicles: figure in use"]["value"] == "7.4"
    assert (rows["New gas plant: dates in use"]["value"], rows["New gas plant: dates in use"]["asset_or_route"]) == ("2029; 2030", "Eskom gas; independent producers' gas")
    shutdowns = [r for r in dr07.build(dr07.load(VINTAGE)) if r["item"] == "Coal station shutdown"]
    assert {r["asset_or_route"] for r in shutdowns} >= {"Komati", "Duvha", "Matla", "Camden, Hendrina, Grootvlei, Arnot and Kriel"}
    assert all("Eskom" in r["source"] or "System operator" in r["source"] for r in shutdowns)


def test_eskom_reported_fuel_gives_the_litres_per_kwh_used_on_the_power_fleet_sheet():
    implied = dr07.implied_litres_per_kwh(dr07.load(VINTAGE))
    assert set(implied) >= {2023, 2024, 2025}
    for year in (2023, 2024, 2025):
        assert implied[year] == pytest.approx(dr07.LITRES_PER_KWH, abs=0.003)
