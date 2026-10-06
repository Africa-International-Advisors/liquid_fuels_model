"""Energy department and Eskom readers — parsing only, no network or files."""
from __future__ import annotations

from lfm.sources import energy_dept as dept
from lfm.sources import eskom

# --------------------------------------------------------------------------- #
# Energy department: fuel sales

def test_discover_sales_files_skips_district_level_workbooks() -> None:
    html = (
        '<a href="SA FUEL SALES VOLUME/2023-Quarter1-Magisterial-Districts-data.xlsx">'
        '<a href="SA FUEL SALES VOLUME/2023-National-Aggregated-FSV-data-Quarter4.xls">'
        '<a href="SA FUEL SALES VOLUME/2011 Annual dissagregated FSV data (T2).xlsx">'
        '<a href="SA FUEL SALES VOLUME/2011-National-Aggregated-FSV.xls">'
    )
    files = dept.discover_sales_files(html)
    assert [f.year for f in files] == [2011, 2023]
    assert files[1].url.endswith("SA%20FUEL%20SALES%20VOLUME/2023-National-Aggregated-FSV-data-Quarter4.xls")


def test_parse_sales_reads_quarters_and_ignores_the_total_column() -> None:
    sheets = {"Annual": [
        [None, 2023.0, "JANUARY TO DECEMBER"],
        [None, "Product name", "Q1", "Q2", "Q3", "Q4", "Grand Total"],
        [None, "Diesel (All grades)", 10.0, 20.0, 30.0, 40.0, 100.0],
        [None, "Petrol (All grades)", 1.0, 2.0, 3.0, 4.0, 10.0],
        [None, "Jet Fuel", 5.0, 5.0, 5.0, 5.0, 20.0],
        [None, "Grand Total", 16.0, 27.0, 38.0, 49.0, 130.0],
    ]}
    products = dept.parse_sales(sheets)
    assert products["diesel"] == [10.0, 20.0, 30.0, 40.0]
    assert products["jet"] == [5.0, 5.0, 5.0, 5.0]
    assert "grand_total" not in products


def test_parse_sales_marks_a_missing_quarter() -> None:
    sheets = {"2025": [
        ["Petrol (All grades)", 1.0, 2.0, 3.0],
        ["Diesel (All grades)", 1.0, 2.0, 3.0],
        ["Jet fuel", 1.0, 2.0, 3.0],
    ]}
    assert dept.parse_sales(sheets)["petrol"] == [1.0, 2.0, 3.0, None]


# --------------------------------------------------------------------------- #
# Energy department: energy balance

def test_parse_balance_older_layout() -> None:
    sheets = {"Commodity flow native units": [
        ["RSA 2019 ver 1"],
        ["BASIC FILE", "kl", "kl", "kl"],
        ["        ", "MOTORGAS", " JETKERO", " GASDIES"],
        [" Import (1)", 100.0, 10.0, 600.0],
        [" Final Consumption", 900.0, 0, 1300.0],
        [" Mining and Quarrying (9)", None, None, 160.0],
        [" Agriculture(4)", None, None, 90.0],
        [" Commerce and Public Services(4)", None, None, 380.0],
    ]}
    rows, warnings = dept.parse_balance(sheets)
    assert warnings == []
    diesel = {r["flow_key"]: r["value"] for r in rows if r["product"] == "diesel"}
    assert diesel == {
        "imports": 600.0, "final_consumption": 1300.0, "mining": 160.0,
        "agriculture": 90.0, "commercial_public": 380.0,
    }
    mining = next(r for r in rows if r["flow_key"] == "mining")
    assert mining["flow"] == "Mining and Quarrying"   # footnote marker removed


def test_parse_balance_newer_layout_and_unit_heading() -> None:
    sheets = {
        "Cover": [["nothing here"]],
        "Data in physical units": [
            ["Data in physical units"],
            [None, "Oil Products (Kl)", None, None, "Oil Products (kt)"],
            [None, "Motor gasoline", "Kerosene type jet fuel", "Gas/diesel oil", "Bitumen"],
            [None, "NONBIOGASO", "NONBIOJETK", "NONBIODIES", "BITUMEN"],
            ["Imports", 5.0, 1.0, 11.0, 0],
            ["Road", 8.0, 0, 6.0, 0],
            ["Commercial and public services", 0.9, 0, 4.3, 0],
        ],
    }
    rows, warnings = dept.parse_balance(sheets)
    assert warnings == []
    assert {(r["flow_key"], r["product"]): r["value"] for r in rows}[("road", "diesel")] == 6.0
    assert not any(r["product"] == "jet" and r["flow_key"] == "road" for r in rows)


def test_parse_balance_warns_when_the_unit_cannot_be_confirmed() -> None:
    sheets = {"x": [
        [None, "GASDIES"],
        ["Imports", 600.0],
    ]}
    rows, warnings = dept.parse_balance(sheets)
    assert rows and warnings == ["unit not confirmed as kilolitres"]


def test_parse_balance_reports_a_workbook_with_no_product_codes() -> None:
    assert dept.parse_balance({"x": [["a", 1.0]]}) == ([], ["no sheet with product codes found"])


# --------------------------------------------------------------------------- #
# Eskom

def test_discover_eskom_reports() -> None:
    html = (
        '<a href="https://www.eskom.co.za/wp-content/uploads/2025/10/Eskom-integrated-report-2025.pdf">'
        '<a href="https://www.eskom.co.za/wp-content/uploads/2026/09/Eskom-integrated-report-August-2026.pdf">'
    )
    assert [r.year for r in eskom.discover_reports(html)] == [2025, 2026]


def test_parse_eskom_report_own_and_combined_output() -> None:
    pages = [
        "Generation, GWh 2026 2025 2024 Coal-fired stations 1 2 3 "
        "Open-cycle gas turbines (OCGTs) 811 2 176 3 634 Hydro stations 4 5 6",
        "Non-renewable 1 079GWh Eskom and IPP OCGTs (2025: 2 838GWh) 425GWh Other",
    ]
    rows, warnings = eskom.parse_report(pages)
    assert warnings == []
    assert rows == {
        2026: [811.0, 1079.0],
        2025: [2176.0, 2838.0],
        2024: [3634.0, None],
    }


def test_parse_eskom_report_says_what_it_could_not_find() -> None:
    rows, warnings = eskom.parse_report(["no tables on this page"])
    assert rows == {}
    assert len(warnings) == 2


# --------------------------------------------------------------------------- #
# Energy department: sales by province

def _quarter_sheet() -> list[list]:
    provinces = ["Eastern Cape", "Freestate", "Gauteng", "KwaZulu Natal", "Limpopo Province",
                 "Mpumalanga", "Northern Cape", "NorthWest", "Western Cape"]
    rows = [["Region Type", "(Multiple Items)"], [],
            ["Row Labels", "Jet Fuel", "Aviation Gasoline", "Diesel", "Furnace Oil", "LPG",
             "Paraffin", "Petrol"]]
    for i, name in enumerate(provinces, start=1):
        rows.append([name, None if i > 3 else 5.0 * i, 0.1, 100.0 * i, 1.0, 1.0, 2.0, 50.0 * i])
        rows.append([f"District of {name}", 1.0, 0.0, 10.0, 0.0, 0.0, 0.0, 5.0])
    rows.append(["Grand Total", 30.0, 0.9, 4500.0, 9.0, 9.0, 18.0, 2250.0])
    return rows


def test_provincial_sales_reads_province_rows_only() -> None:
    rows, warnings = dept.parse_provincial_sales({"2022 Q4": _quarter_sheet(), "Sheet3": []})
    assert warnings == []
    pick = {(r["province"], r["product"]): r["value"] for r in rows}
    assert pick[("GP", "diesel")] == 300.0
    assert pick[("LP", "petrol")] == 250.0                # "Limpopo Province"
    assert pick[("NW", "diesel")] == 800.0                # "NorthWest"
    assert ("LP", "jet") not in pick                      # blank cell, not zero
    assert {(r["year"], r["quarter"]) for r in rows} == {(2022, 4)}
    assert sum(r["value"] for r in rows if r["product"] == "diesel") == 4500.0


def test_provincial_sheet_missing_a_province_is_left_out() -> None:
    sheet = [r for r in _quarter_sheet() if r and r[0] != "Gauteng"]
    rows, warnings = dept.parse_provincial_sales({"2022 Q4": sheet})
    assert rows == []
    assert warnings == ["sheet '2022 Q4': provinces not found (GP)"]


def test_discover_district_files_prefers_the_quarterly_workbook_from_2013() -> None:
    html = (
        '<a href="SA FUEL SALES VOLUME/2013-Magisterial-Districts-data.xlsx">'
        '<a href="SA FUEL SALES VOLUME/2013-FSV-Disaggregated-FSV-at-Magisterial-District-Quarter4.xlsx">'
        '<a href="SA FUEL SALES VOLUME/2012-Quaterly-Disaggregated-Data.xlsx">'
        '<a href="SA FUEL SALES VOLUME/2022-National-Aggregated-FSV-data-Quarter4.xls">'
    )
    files = dept.discover_district_files(html)
    assert [f.year for f in files] == [2013]
    assert "Quarter4" in files[0].url


# --------------------------------------------------------------------------- #
# Energy department: fuel price history

PRICE_TEXT = """Fuel Price History: 2022.
(RSA c/litre) Petrol Diesel Illuminating Paraffin Unleaded 0.05% sulphur
Inland 93 Coast 95 Inland 95 Inland Coast Coast Inland
Jan   1936.00 1889.00 1961.00 1724.68 1663.18 1014.788 1096.688
Mar   1460.00 1423.00 1482 1405.420 1356.620 839.178 899.678
Sep    2295,00 2273.00 2338.00 2396.10
2330.90
1681,088

1760,288
Oct   2206.00 2171.00 2236.00 2406.00 2340.90 1620.088
Nov
 Ytd Avg 2000.00 2000.00 2000.00 2000.00 2000.00 2000.00 2000.00
"""


def test_price_history_rows_across_line_breaks_and_decimal_commas() -> None:
    months, warnings = dept.parse_price_history(PRICE_TEXT)
    assert months[1] == [1936.0, 1889.0, 1961.0, 1724.68, 1663.18, 1014.788, 1096.688]
    assert months[3][2] == 1482.0                      # printed without decimals
    assert months[9] == [2295.0, 2273.0, 2338.0, 2396.1, 2330.9, 1681.088, 1760.288]
    assert 11 not in months                            # not yet filled in; average row ignored
    assert warnings == ["month 10: 6 prices found, expected 7"]


def test_discover_price_files_rewrites_old_addresses() -> None:
    html = ('<a href="December2022/Fuel-Price-History.pdf">2022</a>'
            '<a href="http://www.energy.gov.za/files/esources/petroleum/Dec2011/FuelPriceHistory.pdf">')
    files = dept.discover_price_files(html)
    assert [f.year for f in files] == [2011, 2022]
    assert files[0].url.endswith("/esources/petroleum/Dec2011/FuelPriceHistory.pdf")
    assert files[0].url.startswith("https://www.dmpr.gov.za/")


def test_parse_sales_prefers_the_published_table_over_a_working_pivot() -> None:
    # The 2013 workbook keeps a pivot with a superseded fourth quarter ahead of
    # the published table.
    sheets = {
        "Sheet4": [
            ["Diesel", 1.0, 2.0, 3.0, 4.0, 10.0],
            ["Jet Fuel", 1.0, 1.0, 1.0, 1.0, 4.0],
            ["Petrol", 1.0, 2.0, 3.0, 4.0, 10.0],
        ],
        "2013 Annual Aggregated FSV data": [
            [None, "2013 JANUARY TO DECEMBER SA FUEL SALES VOLUME / CONSUMPTION"],
            [None, "Diesel (All grades)", 1.0, 2.0, 3.0, 9.0, 15.0],
            [None, "Petrol (All grades)", 1.0, 2.0, 3.0, 8.0, 14.0],
            [None, "Jet Fuel", 1.0, 1.0, 1.0, 2.0, 5.0],
        ],
    }
    assert dept.parse_sales(sheets)["diesel"] == [1.0, 2.0, 3.0, 9.0]
    readings = dept.sales_readings(sheets)
    assert list(readings) == ["2013 Annual Aggregated FSV data", "Sheet4"]
    assert readings["Sheet4"]["petrol"] != readings["2013 Annual Aggregated FSV data"]["petrol"]
