"""Market sizing for Durban and Lesedi: built from registered inputs, shared flows counted once, nothing from the client."""
import csv
from pathlib import Path

import pytest

from lfm.scripts import build_market_sizing as sizing

ROOT = Path(__file__).resolve().parents[1]
VINTAGE = ROOT / "assumptions" / "2026"


def _rows():
    return {(r["site"], r["product"], r["measure"]): r for r in sizing.build(sizing.load(VINTAGE))}


def test_committed_file_equals_a_fresh_build_and_every_row_is_labelled_and_sourced():
    rows = sizing.build(sizing.load(VINTAGE))
    with (ROOT / sizing.OUT).open(encoding="utf-8", newline="") as fh:
        assert list(csv.DictReader(fh)) == rows, "rebuild with: python -m lfm.scripts.build_market_sizing --vintage 2026"
    assert {r["status"] for r in rows} == {"observed", "estimated", "assumed"}
    assert all(r["source"] and r["inputs"] for r in rows)
    assert not any("FIASA" in r["source"] or "JODI" in r["source"] for r in rows)


def test_products_add_up_and_the_two_sites_are_counted_once():
    rows = _rows()
    value = lambda site, product, measure: float(rows[(site, product, measure)]["value"])  # noqa: E731
    for site, measure in (("Durban", "Landed at Durban"), ("Lesedi", "Near catchment: Gauteng sales"), ("Durban", "Inland-bound through Durban")):
        assert value(site, "petrol", measure) + value(site, "diesel", measure) == pytest.approx(value(site, "petrol and diesel", measure), abs=0.002)
    both = "petrol and diesel"
    landed = value("Durban", both, "Landed at Durban")
    assert landed == pytest.approx(13.16, abs=0.01)                                  # Durban customs office, 2025
    assert value("Durban and Lesedi", both, "Both sites, counted once") == landed    # not Durban plus Lesedi
    assert value("Durban", both, "Inland-bound through Durban") == pytest.approx(landed - value("Durban", both, "Coastal catchment: KwaZulu-Natal sales"), abs=0.002)
    assert value("Lesedi", both, "Inland-bound through Durban") == value("Durban", both, "Inland-bound through Durban")


def test_capacity_lines_are_marked_assumed_and_never_called_a_share():
    rows = _rows()
    tanks = [r for (_, _, measure), r in rows.items() if measure.startswith("Throughput the tanks allow")]
    assert len(tanks) >= 5 and {r["status"] for r in tanks} == {"assumed"}
    assert all("ceiling, not a share" in r["note"].lower() for r in tanks)
    lesedi = float(rows[("Lesedi", "petrol and diesel", "Throughput the tanks allow at 2 turns a month")]["value"])
    assert lesedi == pytest.approx(124000 * 2 * 12 * 1000 / 1e9, abs=0.001)            # 124,000 m3 operational, two turns a month


def test_trunk_line_use_is_below_capacity_and_the_road_and_rail_remainder_follows():
    rows = _rows()
    value = lambda site, product, measure: float(rows[(site, product, measure)]["value"])  # noqa: E731
    capacity = value("Durban and Lesedi", "all products", "Trunk line capacity, Durban to Jameson Park")
    used = value("Durban and Lesedi", "all products", "Trunk line use, Durban to Jameson Park")
    assert (capacity, used) == (pytest.approx(7.696), pytest.approx(5.044))          # 148 and 97 million litres a week
    inland = value("Durban", "petrol and diesel", "Inland-bound through Durban")
    assert value("Durban and Lesedi", "petrol and diesel", "Inland-bound fuel beyond what the trunk line carried") == pytest.approx(inland - used, abs=0.002)
