"""The department's zone differentials: the 2024 price list, the 2014 workbook and the staged files."""
import csv
from pathlib import Path

import pytest

from lfm.scripts import stage_zone_differentials as stage

REFERENCE = Path(__file__).resolve().parents[1] / "assumptions" / "2026" / "reference"
LIST = """  Diesel 0.05% sulfur
ZONES Basic Zone RTL
1A 2,162.3 3.8 2166.09
2A  10.1  2172.39
9C GAUTENG 82.80  2245.09
35J  Port Nolloth 138.8  2301.09
  Diesel 0.005% sulfur
1A 2176.690  3.8 2180.49
"""


def test_2024_list_reads_the_first_block_and_checks_each_zone_against_its_price():
    rows = stage.parse_diesel_2024(LIST)
    assert [(r["zone"], r["value"]) for r in rows] == [("01A", 3.8), ("02A", 10.1), ("09C", 82.8), ("35J", 138.8)]
    assert {r["effective"] for r in rows} == {"2024-04-03"}
    with pytest.raises(ValueError, match="is not"):
        stage.parse_diesel_2024(LIST.replace("2172.39", "2199.99"))


def test_2014_workbook_rows_skip_blank_columns_and_headings():
    rates, places = stage.parse_zones_2014(
        [["Zones", "Differential (c/l)"], ["01A", 2.5, "", "01A", 2.5, "", "01A", 2.5], ["09C", 33.1, "", "09C", 33.1]],
        [["Current Zone", "Magisterial district", "Province"], ["01A", "Cape Town   ", "Western Cape"], ["09C", "Alberton", "Gauteng"]])
    assert [(r["zone"], r["product"], r["value"]) for r in rates] == [("01A", "petrol", 2.5), ("01A", "diesel", 2.5),
                                                                      ("09C", "petrol", 33.1), ("09C", "diesel", 33.1)]
    assert places == [{"zone": "01A", "magisterial_district": "Cape Town", "province": "Western Cape"},
                      {"zone": "09C", "magisterial_district": "Alberton", "province": "Gauteng"}]


def test_staged_files_hold_54_zones_and_gauteng_as_published():
    with (REFERENCE / "zone_differentials_department.csv").open(encoding="utf-8", newline="") as fh:
        rates = {(r["zone"], r["product"], r["effective"]): float(r["value"]) for r in csv.DictReader(fh)}
    for product, effective in (("diesel", "2024-04-03"), ("diesel", "2014-04-02"), ("petrol", "2014-04-02")):
        assert sum(1 for key in rates if key[1:] == (product, effective)) == 54
    assert rates[("09C", "diesel", "2024-04-03")] == 82.8 and rates[("09C", "diesel", "2014-04-02")] == 33.1
    assert rates[("01A", "diesel", "2024-04-03")] == min(v for k, v in rates.items() if k[2] == "2024-04-03")
    with (REFERENCE / "zone_districts_department.csv").open(encoding="utf-8", newline="") as fh:
        places = list(csv.DictReader(fh))
    assert len(places) == 385 and {p["province"] for p in places if p["zone"] == "09C"} >= {"Gauteng"}
