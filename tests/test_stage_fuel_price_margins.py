"""The department's yearly price tables: the transport cost column is read by position and bad rows are left out."""
import csv
from pathlib import Path

import pytest

from lfm.scripts import stage_fuel_price_margins as stage

REFERENCE = Path(__file__).resolve().parents[1] / "assumptions" / "2026" / "reference"
DIESEL = """BFP Fuel tax Customs & excise IP Tracer Dye Levy Pipeline Levy Road accident fund Transport
cost Wholesale margin Secondary Storage Secondary Distribution Slate Levy
Jan 1 240.630 381.000 4.000 0.100 0.330 218.000 75.700 89.610 36.600 17.200 0.00
Feb 913.630 381.000 4.000 0.100 0.330 218.000 75.700 89.610 36.600 17.200 0.00
Mar 961.030 80.220 30.700 17.940 41.66
Apr
"""


def test_transport_cost_is_read_by_position_and_incomplete_months_are_left_out():
    values, problems = stage.parse_transport_cost(DIESEL, "diesel")
    assert values == {1: 75.7, 2: 75.7}                       # "1 240.630" is one number; April is not yet published
    assert problems == ["Mar"]                                # a row with columns missing is reported, not guessed
    with pytest.raises(ValueError, match="expected order"):
        stage.parse_transport_cost(DIESEL.replace("Road accident fund Transport", "Transport Road accident fund"), "diesel")


def test_staged_series_matches_the_zone_list_in_april_2014_and_runs_to_april_2024():
    with (REFERENCE / "transport_cost_gauteng_department.csv").open(encoding="utf-8", newline="") as fh:
        rows = {(r["product"], r["period"]): float(r["value"]) for r in csv.DictReader(fh)}
    assert rows[("diesel", "2014-04")] == 33.1                # the Gauteng zone differential of 2 April 2014
    assert rows[("diesel", "2012-01")] == 22.9 and rows[("diesel", "2024-04")] == 75.7
    assert max(period for _, period in rows) == "2024-04"
    assert ("diesel", "2016-12") not in rows                  # unreadable in the department's table
