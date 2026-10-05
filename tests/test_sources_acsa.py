"""ACSA group statistics reader — small tables in the published layout."""
from __future__ import annotations

from lfm.sources import acsa

HEADING = ("Flight Type   Month   FY   FY24/25   FY25/26   FY24/25   FY25/26   "
           "FY24/25   FY25/26")


def _table(sections: int = 5, *, april: str = "   100   110   90   95   190   205") -> str:
    lines = ["   arr/dep   Arrival   Departure   Total", HEADING]
    for _ in range(sections):
        lines.append("01-Apr" + april)
        lines.append("10-Jan   1 000   0   2 000   0   3 000   0")
        lines.append("   Total   1 100   110   2 090   95   3 190   205")
    return "\n".join(lines)


def test_rows_become_monthly_figures_in_the_right_calendar_year() -> None:
    rows, warnings = acsa.parse(_table())
    assert warnings == []
    pick = {(r["flight_type"], r["period"], r["direction"]): r["value"] for r in rows}
    assert pick[("international", "2024-04", "arrival")] == 100
    assert pick[("international", "2025-04", "departure")] == 95
    assert pick[("regional", "2025-01", "total")] == 3000      # January of FY24/25 is 2025
    assert pick[("total", "2026-01", "total")] == 0
    assert {r["financial_year"] for r in rows} == {"FY24/25", "FY25/26"}


def test_figures_that_have_run_together_are_separated() -> None:
    assert acsa._figures("11 935 88611 666 804   4 013 579") == [11935886, 11666804, 4013579]
    assert acsa._figures("490   74   440 293") == [490, 74, 440293]


def test_row_that_fails_arrivals_plus_departures_is_left_out() -> None:
    rows, warnings = acsa.parse(_table(april="   100   110   90   95   999   205"))
    assert not any(r["period"].endswith("-04") for r in rows)
    assert warnings.count("international row 01: arrivals and departures do not add up "
                          "to the total") == 1
    assert len(warnings) == 5


def test_missing_sections_are_reported() -> None:
    _, warnings = acsa.parse(_table(sections=3))
    assert warnings == ["only 3 of 5 sections found"]


def test_months_not_yet_reported_are_dropped() -> None:
    rows, _ = acsa.parse(_table())
    kept, last = acsa.drop_unreported_months(rows)
    assert last == "2025-04"                      # 2026-01 is still zero
    assert max(r["period"] for r in kept) == "2025-04"


def test_calendar_years_need_all_twelve_months() -> None:
    rows = [{"period": f"2025-{m:02d}", "flight_type": "total", "direction": "departure",
             "value": 10} for m in range(1, 13)]
    rows += [{"period": "2026-01", "flight_type": "total", "direction": "departure",
              "value": 10}]
    assert acsa.calendar_years(rows) == [
        {"period": 2025, "flight_type": "total", "direction": "departure", "value": 120}]
