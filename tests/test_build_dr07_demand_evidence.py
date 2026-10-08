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


def test_eskom_reported_fuel_gives_the_litres_per_kwh_used_on_the_power_fleet_sheet():
    implied = dr07.implied_litres_per_kwh(dr07.load(VINTAGE))
    assert set(implied) >= {2023, 2024, 2025}
    for year in (2023, 2024, 2025):
        assert implied[year] == pytest.approx(dr07.LITRES_PER_KWH, abs=0.003)
