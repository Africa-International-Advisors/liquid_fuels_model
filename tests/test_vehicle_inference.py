"""Vehicles by fuel within each class, the light commercial electric forecast and the pipeline map's measures."""
from pathlib import Path

import pytest

from lfm.scripts import build_dr07_demand_evidence as dr07
from lfm.scripts import build_pipeline_map as pipeline_map
from lfm.scripts import vehicle_inference as infer

ROOT = Path(__file__).resolve().parents[1]
VINTAGE = ROOT / "assumptions" / "2026"


def test_fuel_by_class_keeps_each_class_total_and_adds_to_the_bulletins_diesel_total():
    d = dr07.load(VINTAGE)
    by_class, factor = dr07.fuel_by_class(d)
    for name, (petrol, diesel) in by_class.items():
        assert petrol + diesel == pytest.approx(d["natis_2023"][name])              # the register's class totals are untouched
    share = d["by_fuel"]["diesel"] / (d["by_fuel"]["diesel"] + d["by_fuel"]["petrol"])
    assert sum(v[1] for v in by_class.values()) / sum(sum(v) for v in by_class.values()) == pytest.approx(share, abs=1e-6)
    assert factor > 1                                                               # diesel has gained share since the 2010 fleet
    assert by_class["buses"][0] == 0 and by_class["motorcycles"][1] == 0            # all diesel and all petrol stay so
    seed = infer.seed_shares(d["stone"])
    assert by_class["light_commercial"][1] / sum(by_class["light_commercial"]) > seed["light_commercial"] == pytest.approx(0.3795, abs=0.001)


def test_fuel_by_class_returns_the_seed_when_the_totals_already_agree():
    classes, seed = {"cars": 1000.0, "trucks": 100.0}, {"cars": 0.1, "trucks": 0.9}
    result, factor = infer.fuel_by_class(classes, 190.0, seed)                       # 100 + 90: nothing to move
    assert factor == pytest.approx(1.0, abs=1e-6) and result["cars"][1] == pytest.approx(100.0, abs=1e-3)


def test_light_commercial_forecast_follows_the_lever_cases_and_adds_up_sales():
    forecast = infer.light_commercial_electric_forecast({"medium": {2030: 1.0, 2035: 5.0}}, {2026: 160000.0, 2027: 180000.0}, 2_800_000.0, 2600.0)["medium"]
    assert (forecast["share"][2030], forecast["share"][2035]) == (1.0, 5.0)
    assert forecast["share"][2026] == pytest.approx(0.2) and forecast["share"][2032] == pytest.approx(2.6)
    assert forecast["on_road"][2027] == pytest.approx(160000 * 0.002 + 180000 * 0.004)   # sales x share, added up
    assert forecast["displaced_million_litres"][2027] == pytest.approx(forecast["on_road"][2027] * 2600 / 1e6)
    d = dr07.load(VINTAGE)
    cases = dr07.lcv_forecast(d)
    assert set(cases) == {"low", "medium", "high"} and cases["low"]["on_road"][2035] == 0
    assert cases["high"]["on_road"][2035] > cases["medium"]["on_road"][2035] > 0


def test_pipeline_runs_from_durban_to_jameson_park_and_island_view_is_beside_it():
    m = pipeline_map.measures(pipeline_map.pipeline_ways())
    assert m["ways"] == 10 and 500 < m["pipeline_length_km"] < 620                   # Transnet describes a trunk line of about 555 km
    assert m["coastal_end"][0] > 30.9 and m["inland_end"][0] < 28.4                  # near Durban; near Jameson Park
    assert m["island_view_to_pipeline_km"] < 10
    assert pipeline_map.distance_km((0, 0), (1, 0)) == pytest.approx(111.19, abs=0.05)
