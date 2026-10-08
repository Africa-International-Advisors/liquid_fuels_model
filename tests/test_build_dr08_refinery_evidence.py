"""The DR08 evidence table: built from the registered inputs, every fact sourced, FIASA and JODI not selected."""
import csv
from pathlib import Path

import pytest

from lfm.scripts import build_dr08_refinery_evidence as dr08

ROOT = Path(__file__).resolve().parents[1]
VINTAGE = ROOT / "assumptions" / "2026"


def test_committed_table_equals_a_fresh_build_and_every_fact_has_a_source():
    rows = dr08.build(dr08.load(VINTAGE))
    with (ROOT / dr08.OUT).open(encoding="utf-8", newline="") as fh:
        assert list(csv.DictReader(fh)) == rows, "rebuild with: python -m lfm.scripts.build_dr08_refinery_evidence --vintage 2026"
    assert all(r["source"] for r in rows)
    assert all(bool(r["value"]) != (r["status"] == "not available") for r in rows)
    assert not any("JODI" in r["source"] or r["source"].startswith("FIASA") for r in rows)


def test_capacity_output_and_utilisation_follow_the_sources():
    d = dr08.load(VINTAGE)
    cap = dr08.capacity(d)
    assert (cap["Secunda"], cap["Natref"], cap["Astron Energy"], cap["Enref"], cap["PetroSA"]) == (150000, 108000, 100000, 0, 0)
    use = dr08.utilisation(d)
    assert use[("Secunda", 2026)] == pytest.approx(30.6e6 / (150000 * 365))
    assert use[("Natref", 2024)] == pytest.approx(17.8e6 / 0.6364 / (108000 * 366))
    assert ("Natref", 2026) not in use                                    # that year's figure includes output above Sasol's share
    rows = {(r["item"], r["asset_or_route"]): r for r in dr08.build(d)}
    assert rows[("Diesel produced, all plants", "South Africa")]["value"].endswith("6.45; 5.31")
    assert rows[("Petrol and diesel output by plant", "Secunda and Astron Energy")]["status"] == "not available"
    low, high = dr08.natref_by_product(d)[("diesel", 2024)]               # Sasol's share scaled up, times its stated 31 to 37%
    assert (low, high) == pytest.approx((17.8 / 0.6364 * 158.987 / 1e3 * 0.31, 17.8 / 0.6364 * 158.987 / 1e3 * 0.37))
    assert rows[("Diesel output, estimated", "Natref, whole refinery")]["status"] == "inferred"
    assert "not used" in rows[("Petrol produced, United Nations series (not used)", "South Africa")]["item"]
    dated = {(r["asset_or_route"], r["period"]) for r in dr08.build(d) if r["part"] == "Status and dates"}
    assert {("Sapref", "10 February 2022"), ("Enref (Engen)", "4 December 2020"), ("Enref (Engen)", "23 April 2021")} <= dated
