"""Stats SA GDP workbook reader — rows as they appear in the "Annual" sheet."""
from __future__ import annotations

from pathlib import Path

from lfm.sources import statssa

HEADER = ["H01", "H02", "H03", "H04", "H05", "H06", "H15", "H17", "H25", "Y2023", "Y2024", "Y2025"]


def _row(code: str, group: str, name: str, basis: str, *values, unit: str = "R million") -> list:
    return ["P0441", "Gross domestic product", code, group, name, None, basis, unit,
            "Annual", *values]


def test_reads_constant_price_gdp_and_industries_in_rand() -> None:
    rows = [
        HEADER,
        _row("AN1000", "GDP at market prices", "GDP at market prices", "Current prices",
             7037674.0, 7352449.0, 7641793.0),
        _row("AR1002", "Value added at basic prices", "Mining and quarrying",
             "Constant 2015 prices", 200000.0, 203000.0, 205000.0),
        _row("AR1000", "GDP at market prices", "GDP at market prices",
             "Constant 2015 prices", 4639792.0, 4664608.0, 4716601.0),
    ]
    series, warnings = statssa.parse_constant_price_series(rows)
    assert warnings == []
    by_name = {s["name"]: s for s in series}
    assert set(by_name) == {"gdp", "Mining and quarrying"}       # current prices left out
    assert by_name["gdp"]["values"][2025] == 4716601.0 * 1_000_000
    assert by_name["gdp"]["price_basis"] == "Constant 2015 prices"


def test_blank_years_are_left_out() -> None:
    rows = [HEADER, _row("AR1000", "GDP at market prices", "GDP at market prices",
                         "Constant 2015 prices", 4639792.0, None, 4716601.0)]
    series, _ = statssa.parse_constant_price_series(rows)
    assert sorted(series[0]["values"]) == [2023, 2025]


def test_unexpected_unit_is_skipped_with_a_warning() -> None:
    rows = [HEADER, _row("AR1000", "GDP at market prices", "GDP at market prices",
                         "Constant 2015 prices", 4.6, 4.7, 4.7, unit="R billion")]
    series, warnings = statssa.parse_constant_price_series(rows)
    assert series == []
    assert "expected R million" in warnings[0] and "AR1000 not found" in warnings[1]


def test_changed_layout_is_reported() -> None:
    assert statssa.parse_constant_price_series([["A", "B"], [1, 2]]) == (
        [], ["annual sheet: expected column headings H03-H05, H15 and H17 not found"])


def test_latest_gdp_file_picks_the_most_recent_quarter(tmp_path: Path) -> None:
    for name in ("GDP P0441 - GDP Time series Q4 2025.xlsx",
                 "GDP P0441 - GDP Time series Q2 2026.xlsx",
                 "GDP P0441 - GDP Time series Q1 2026.xlsx",
                 "~$GDP P0441 - GDP Time series Q3 2026.xlsx"):
        (tmp_path / name).write_bytes(b"")
    assert statssa.latest_gdp_file(tmp_path).name == "GDP P0441 - GDP Time series Q2 2026.xlsx"
    assert statssa.latest_gdp_file(tmp_path / "missing") is None


# --------------------------------------------------------------------------- #
# Mid-year population estimates

POPULATION_ROWS = [
    ["Projection by population group, sex and age"],
    [],
    # Three tables side by side, each repeating the years, as in the workbook.
    ["Population Group", "Sex", "Age", 2025, 2026, None, "Sex", "Age", 2025, 2026, None, "Age", 2025, 2026],
    ["African", "Male", "0-4", 10.0, 11.0, None, "Male", "0-4", 30.0, 33.0, None, "0-4", 70.0, 77.0],
    ["African", "Female", "0-4", 20.0, 22.0, None, "Female", "0-4", 40.0, 44.0, None, None, 70.0, 77.0],
    ["White", "Male", "0-4", 20.0, 22.0],
    ["White", "Female", "0-4", 20.0, 22.0],
    [None, None, None, 70.0, 77.0],          # the sheet's own total row
]


def test_population_reads_only_the_first_table_and_skips_the_total_row() -> None:
    population, warnings = statssa.parse_population(POPULATION_ROWS)
    assert warnings == []
    assert population == {2025: 70.0, 2026: 77.0}     # not doubled or trebled


def test_population_heading_not_found_is_reported() -> None:
    assert statssa.parse_population([["nothing"], [1, 2]]) == (
        {}, ["population sheet: heading row with Sex and year columns not found"])


def test_summary_total_is_the_last_large_number_on_the_total_row() -> None:
    rows = [["Population group", "Male", None, "Female", None, "Total"],
            ["African", 25525335, 82, 26390832, 82, 51916167, 82],
            ["Total", 31211210, "100,0", 32311170, "100,0", 63522380, "100,0"]]
    assert statssa.parse_summary_total(rows) == 63522380.0


def test_average_growth_over_a_window() -> None:
    rate, first, last = statssa.average_growth({2021: 100.0, 2026: 110.0, 2025: 108.0}, 5)
    assert (first, last) == (2021, 2026)
    assert abs((1 + rate) ** 5 - 1.10) < 1e-12


def test_quarterly_series_take_unadjusted_constant_price_rows_only() -> None:
    header = ["H01", "H02", "H03", "H04", "H05", "H06", "H15", "H16", "H17", "H25",
              "202504", "202601", "202602"]
    rows = [
        header,
        ["P0441", "GDP", "QNU1002", "Value added at basic prices", "Mining and quarrying", None,
         "Current prices", "Actual values", "R million", "Quarterly", 9.0, 9.0, 9.0],
        ["P0441", "GDP", "QRU1002", "Value added at basic prices", "Mining and quarrying", None,
         "Constant 2015 prices", "Actual values", "R million", "Quarterly", 54.0, 47.0, 52.0],
        ["P0441", "GDP", "QRS1002", "Value added at basic prices", "Mining and quarrying", None,
         "Constant 2015 prices", "Seasonally adjusted and annualised values", "R million",
         "Quarterly", 200.0, 201.0, 202.0],
        ["P0441", "GDP", "QRU1000", "GDP at market prices", "GDP at market prices", None,
         "Constant 2015 prices", "Actual values", "R million", "Quarterly", 1195.0, 1168.0, None],
        ["P0441", "GDP", "QRU1099", "Value added at basic prices", "Mining and quarrying", None,
         "Constant 2015 prices", "Actual values", "% of GDP", "Quarterly", 4.5, 4.0, 4.4],
    ]
    series, warnings = statssa.parse_quarterly_constant_price_series(rows)
    assert warnings == []
    assert [s["code"] for s in series] == ["QRU1002", "QRU1000"]
    assert series[0]["values"] == {"2025-Q4": 54e6, "2026-Q1": 47e6, "2026-Q2": 52e6}
    assert series[1]["name"] == "gdp" and "2026-Q2" not in series[1]["values"]


def test_monthly_series_are_read_by_code_and_missing_codes_are_reported() -> None:
    rows = [
        ["H01", "H02", "H03", "H04", "H05", "H16", "H17", "H18", "H25", "MO062026", "MO072026"],
        ["P2041", "Mining", "FMP20000", "Physical volume", "Total, gold included",
         "Actual indices", "Index", "2019=100", "Monthly", 96, "91,4"],
        ["P2041", "Mining", "FMP20000S", "Physical volume", "Total, gold included",
         "Seasonally adjusted indices", "Index", "2019=100", "Monthly", 95.0, 94.0],
        ["P2041", "Mining", "FMP21000", "Physical volume", "Coal",
         "Actual indices", "Index", "2019=100", "Monthly", 93.0, ".."],
    ]
    wanted = {"FMP20000": ("mining_volume_total", "index, 2019=100"),
              "FMP21000": ("mining_volume_coal", "index, 2019=100"),
              "FMP99999": ("not_there", "index")}
    series, warnings = statssa.parse_monthly_series(rows, wanted)
    by = {s["name"]: s for s in series}
    assert by["mining_volume_total"]["values"] == {"2026-06": 96.0, "2026-07": 91.4}
    assert by["mining_volume_coal"]["values"] == {"2026-06": 93.0}
    assert warnings == ["series FMP99999 not found"]


def test_latest_release_file_picks_the_newest_stamp(tmp_path) -> None:
    for name in ("P7162 Land transport survey(202605).zip", "P7162 Land transport survey(202607).zip",
                 "P7162 Land transport survey.zip"):
        (tmp_path / name).write_bytes(b"")
    found = statssa.latest_release_file(tmp_path, "P7162 Land transport survey(*).zip")
    assert found.name == "P7162 Land transport survey(202607).zip"


def test_provincial_gdp_reads_the_constant_price_block_only() -> None:
    sheet = [
        ["Western Cape – GDPR by activity", None, None],
        ["a. Current prices - Rand million", None, None],
        ["Industry", "2023", "2024"],
        ["Mining and quarrying", 1921.9, 1863.5],
        ["GDPR at market prices", 900000.0, 950000.0],
        [None, None, None],
        ["c. Constant 2015 prices - Rand million", None, None],
        ["Industry", "2023", "2024"],
        ["Mining and quarrying", 1500.0, 1400.0],
        ["GDPR at market prices", 600000.0, 604000.0],
        [None, None, None],
        ["d. Constant 2015 prices - percentage changes", None, None],
        ["Industry", "2023", "2024"],
        ["Mining and quarrying", None, -6.7],
    ]
    rows, warnings = statssa.parse_provincial_gdp({
        "ReadMe": [["Description of tables"]],
        "Table 1": [["South Africa – GDP by activity"]],
        "Table 2": sheet,
    })
    assert {(r["province"], r["industry"], r["year"]): r["value"] for r in rows} == {
        ("WC", "Mining and quarrying", 2023): 1.5e9, ("WC", "Mining and quarrying", 2024): 1.4e9,
        ("WC", "GDPR at market prices", 2023): 6.0e11, ("WC", "GDPR at market prices", 2024): 6.04e11,
    }
    assert "no sheet read for province GP" in warnings and len(warnings) == 8
