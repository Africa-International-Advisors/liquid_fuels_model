"""Economy sources — parsing only; no network or files."""
from __future__ import annotations

import json

from lfm.sources import economy

TREASURY_TABLE = """Table 2.2
Macroeconomic performance and projections
2024 2025 2026 2027 2028
Actual Estimate
Final household consumption 1.0       3.1     1.8    2.0        2.2
Exports  -2.8 -2.0 1.6   2.4        2.9
Real GDP growth 0.5      1.4    1.6   1.8        2.0
GDP inflation 3.9   2.5        4.1       3.4      3.3
Sources: National Treasury, Reserve Bank and Statistics South Africa
Percentage change Forecast
"""


def test_world_bank_response_keeps_only_years_with_a_figure() -> None:
    payload = json.dumps([
        {"page": 1, "lastupdated": "2026-07-13"},
        [{"date": "2026", "value": None},
         {"date": "2025", "value": 72846.27},
         {"date": "2024", "value": 72876.0}],
    ])
    values, updated = economy.parse_world_bank(payload)
    assert values == {2025: 72846.27, 2024: 72876.0}
    assert updated == "2026-07-13"


def test_world_bank_error_response_gives_nothing() -> None:
    payload = json.dumps([{"message": [{"id": "120", "value": "Invalid value"}]}])
    assert economy.parse_world_bank(payload) == ({}, None)


def test_base_year_is_where_constant_and_current_gdp_coincide() -> None:
    constant = {2014: 4363.0, 2015: 4420.8, 2016: 4450.2}
    current = {2014: 4133.9, 2015: 4420.8, 2016: 4759.6}
    assert economy.base_year(constant, current) == 2015


def test_base_year_is_not_guessed_when_no_year_matches() -> None:
    assert economy.base_year({2015: 100.0}, {2015: 120.0}) is None


def test_treasury_growth_row_and_labels() -> None:
    rows, warnings = economy.parse_treasury_growth(TREASURY_TABLE, publication_year=2026)
    assert warnings == []
    assert rows == [
        {"period": 2024, "value": 0.5, "basis": "actual"},
        {"period": 2025, "value": 1.4, "basis": "estimate"},
        {"period": 2026, "value": 1.6, "basis": "forecast"},
        {"period": 2027, "value": 1.8, "basis": "forecast"},
        {"period": 2028, "value": 2.0, "basis": "forecast"},
    ]


def test_treasury_table_missing_or_misaligned_is_reported() -> None:
    assert economy.parse_treasury_growth("nothing", 2026) == (
        [], ["macroeconomic projections table not found"])
    short = TREASURY_TABLE.replace("0.5      1.4    1.6   1.8        2.0", "0.5 1.4 1.6")
    rows, warnings = economy.parse_treasury_growth(short, 2026)
    assert rows == [] and "5 years but 3 growth figures" in warnings[0]


def test_treasury_candidates_try_the_later_document_first() -> None:
    labels = [(d.label, d.year) for d in economy.treasury_candidates(2026)]
    assert labels == [("mtbps", 2026), ("budget-review", 2026),
                      ("mtbps", 2025), ("budget-review", 2025)]
