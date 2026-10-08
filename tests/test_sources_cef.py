"""CEF daily basic fuel price sheets: finding them and reading the regulated prices."""

from datetime import date

from lfm.sources import cef

SHEET = """South African Cents per Litre (SA c/l) PETROL 95 ULP PETROL 93 ULP & LRP DIESEL 0.05% DIESEL 0.005% ILL. PAR.
GAUTENG PUMP PRICE AS FROM 04/02/2026 2,010.000 1,999.000 - - -
WHOLESALE PRICE AS FROM 04/02/2026 - - 1,791.830 1,795.230 1,210.098
SINGLE NATIONAL MAXIMUM RETAIL PRICE AS FROM 04/02/2026 - - - - 1,529.000
BASIC FUEL PRICE - 13/02/2026 840.322 825.017 955.743 961.674 955.030
"""


def test_daily_sheet_gives_the_four_inland_prices_and_their_effective_date() -> None:
    effective, prices, warnings = cef.parse_daily_sheet(SHEET)
    assert effective == date(2026, 2, 4)
    assert warnings == []
    assert prices == {
        "petrol_95_inland_retail": 2010.0, "petrol_93_inland_retail": 1999.0,
        "diesel_005_inland_wholesale": 1791.83, "paraffin_inland": 1210.098,
    }


def test_daily_sheet_without_price_lines_is_reported() -> None:
    assert cef.parse_daily_sheet("BASIC FUEL PRICE - 13/02/2026 840.322") == (
        None, {}, ["price lines not found"])


def test_year_pages_and_sheets_are_found_and_one_sheet_a_month_is_picked() -> None:
    index = '<a href="https://cefgroup.co.za/2025-4/">2025</a><a href="https://cefgroup.co.za/2026-4/">2026</a>'
    assert cef.discover_year_pages(index) == {
        2025: "https://cefgroup.co.za/2025-4/", 2026: "https://cefgroup.co.za/2026-4/"}
    page = "".join(
        f'<a href="https://cefgroup.co.za/wp-content/uploads/2026/{m}/Daily-{d}-{m}-2026{s}.pdf">Download</a>'
        for d, m, s in (("02", "09", ""), ("15", "09", "-1"), ("30", "09", ""), ("05", "10", "")))
    sheets = cef.discover_daily_sheets(page)
    assert [when for when, _ in sheets] == [
        date(2026, 9, 2), date(2026, 9, 15), date(2026, 9, 30), date(2026, 10, 5)]
    chosen = cef.pick_monthly(sheets)
    assert chosen[(2026, 9)][0] == date(2026, 9, 15)
    assert chosen[(2026, 10)][0] == date(2026, 10, 5)
