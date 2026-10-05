"""FIASA annual-report reader — table parsing and report-to-report checks.

No network and no PDFs: the page text below is copied from the reports'
extracted text, including the broken digit spacing the 2025 report produces.
"""
from __future__ import annotations

from lfm.sources import fiasa

HEADING = fiasa.CONSUMPTION_HEADING
N = len(fiasa.CONSUMPTION_PRODUCTS)


def _page(plain_rows: list[str], layout_rows: list[str]) -> fiasa.PageText:
    head = f"{HEADING} in South Africa\nMillions of litres\n"
    return fiasa.PageText(
        plain=head + "\n".join(plain_rows),
        layout=head + "\n".join(layout_rows),
    )


def test_discover_reports_reads_year_from_any_link_shape() -> None:
    html = (
        '<a href="/wp-content/uploads/2026/07/Annual-Report-2025.pdf">2025</a>'
        '<a href="https://fuelsindustry.org.za/download/39/x/16248/annual-report-2021.pdf">'
    )
    reports = fiasa.discover_reports(html)
    assert [r.year for r in reports] == [2025, 2021]
    assert reports[0].url.startswith("https://fuelsindustry.org.za/wp-content")


def test_row_with_clean_column_gaps_is_read_directly() -> None:
    page = _page(
        ["2023 9 037 12 907 1 298 1 844 658 288"],
        ["  2023      9 037      12 907      1 298      1 844      658      288"],
    )
    rows, warnings = fiasa.read_table([page], HEADING, N)
    assert rows == {2023: [9037.0, 12907.0, 1298.0, 1844.0, 658.0, 288.0]}
    assert warnings == []


def test_broken_digit_spacing_is_resolved_from_another_report() -> None:
    # 2025 report: the layout reading splits "1 078" into "1  07 8".
    page = _page(
        ["2021 9 302 12 946 1 078 1 048 491 308"],
        ["  2021  9 302  12 946  1  07 8  1 048  491  308"],
    )
    reference = {2021: [9302.0, 12946.0, 1078.0, 1048.0, 491.0, 308.0]}
    rows, warnings = fiasa.read_table([page], HEADING, N, reference)
    assert rows[2021] == [9302.0, 12946.0, 1078.0, 1048.0, 491.0, 308.0]
    assert warnings == []


def test_new_year_without_clean_layout_uses_nearest_year_for_columns_only() -> None:
    page = _page(
        ["2023 9 037 12 907 1 298 1 844 658 288",
         "2024 9 029 11 734 1 045 1 955 441 315"],
        ["  2023  9 037  12 907  1 298  1 844  658  288"],   # 2024 line lost
    )
    rows, _ = fiasa.read_table([page], HEADING, N)
    assert rows[2024] == [9029.0, 11734.0, 1045.0, 1955.0, 441.0, 315.0]


def test_row_is_dropped_not_guessed_when_there_is_nothing_to_place_columns() -> None:
    page = _page(["2024 9 029 11 734 1 045 1 955 441 315"], [])
    rows, warnings = fiasa.read_table([page], HEADING, N)
    assert rows == {}
    assert "no reference row" in warnings[0]


def test_decimal_comma_and_dash_cells() -> None:
    page = fiasa.PageText(
        plain=fiasa.TRADE_HEADING + "\n2010 2 095 2 575 268 7,55 439 736 – 114",
        layout=fiasa.TRADE_HEADING + "\n 2010   2 095   2 575   268   7,55   439   736   –   114",
    )
    rows, _ = fiasa.read_table([page], fiasa.TRADE_HEADING, len(fiasa.TRADE_COLUMNS))
    assert rows[2010] == [2095.0, 2575.0, 268.0, 7.55, 439.0, 736.0, None, 114.0]


def test_contents_page_heading_without_rows_is_skipped() -> None:
    contents = fiasa.PageText(plain=HEADING + "\nPrices in Gauteng\n44", layout="")
    table = _page(
        ["2023 9 037 12 907 1 298 1 844 658 288"],
        ["  2023   9 037   12 907   1 298   1 844   658   288"],
    )
    rows, _ = fiasa.read_table([contents, table], HEADING, N)
    assert 2023 in rows


def test_combine_newest_report_wins_and_logs_the_revision() -> None:
    tables = {
        2024: {2023: [9037.0], 2024: [8763.0]},
        2025: {2023: [9037.0], 2024: [9029.0]},
    }
    out = fiasa.combine(tables, ("petrol",))
    values = {r["period"]: (r["value"], r["source_report"]) for r in out.rows}
    assert values[2024] == (9029.0, 2025)
    assert out.revisions == [{
        "period": 2024, "column": "petrol",
        "earlier_report": 2024, "earlier_value": 8763.0,
        "later_report": 2025, "later_value": 9029.0,
    }]


def test_combine_drops_a_final_year_that_repeats_the_year_before() -> None:
    tables = {2025: {2023: [9037.0, 12907.0], 2024: [9029.0, 11734.0],
                     2025: [9029.0, 11734.0]}}
    out = fiasa.combine(tables, ("petrol", "diesel"))
    assert out.latest_year == 2024
    assert out.carried_over == [{"report": 2025, "period": 2025}]


def test_combine_warns_about_a_missing_year() -> None:
    out = fiasa.combine({2021: {2009: [1.0], 2011: [3.0]}}, ("petrol",))
    assert out.warnings == ["petrol: no figure for 2010"]
