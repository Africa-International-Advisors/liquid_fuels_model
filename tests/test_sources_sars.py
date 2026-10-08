"""SARS trade portal: reading the form and a downloaded report."""

from pathlib import Path

import openpyxl

from lfm.sources import sars

FORM = """
<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="abc123" />
<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="xyz" />
<input id="ctl00_ContentPlaceHolder1_ddlTariffs_0" type="checkbox" name="t$0" />
<label for="ctl00_ContentPlaceHolder1_ddlTariffs_0">27101202 - Petrol, as defined</label>
<input id="ctl00_ContentPlaceHolder1_ddlTariffs_1" type="checkbox" name="t$1" />
<label for="ctl00_ContentPlaceHolder1_ddlTariffs_1">27101247 - Lubricating grease</label>
<input id="ctl00_ContentPlaceHolder1_ddlYears_14" type="checkbox" name="y$14" />
<label for="ctl00_ContentPlaceHolder1_ddlYears_14">2024</label>
"""


def test_form_fields_and_tick_lists_are_read() -> None:
    assert sars.hidden_fields(FORM) == {"__VIEWSTATE": "abc123", "__EVENTVALIDATION": "xyz"}
    assert sars.checkbox_labels(FORM, "ddlYears") == [(14, "2024")]
    tariffs = sars.checkbox_labels(FORM, "ddlTariffs")
    assert [i for i, label in tariffs if label[:8] in sars.TARIFF_PRODUCT] == [0]


def test_download_link_and_refusal_message() -> None:
    accepted = "<script>window.open('Download.aspx?&c=1', '_blank', 'status=no');</script>"
    assert sars.download_link(accepted).endswith("/tradestatsportal/Download.aspx?&c=1")
    refused = "<script>alert('Please select Country!');</script>"
    assert sars.download_link(refused) is None
    assert sars.refusal(refused) == "Please select Country!"


def _report(path: Path, rows: list[tuple]) -> Path:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["TradeType", "DistrictOfficeCode", "DistrictOfficeName", "CountryOfOrigin",
               "CountryOfOriginName", "CountryOfDestination", "CountryOfDestinationName", "Tariff",
               "StatisticalUnit", "TransportCode", "TransportCodeDescription", "YearMonth",
               "CalendarYear", "StatisticalQuantity", "CustomsValue"])
    for row in rows:
        ws.append(row)
    wb.save(path)
    return path


def test_report_rows_and_annual_totals_keep_units_apart(tmp_path) -> None:
    path = _report(tmp_path / "r.xlsx", [
        ("Imports", "DBN", "Durban", "OM", "Oman", "ZA", "South Africa", 27101230, "LI", 1,
         "Maritime", 202401, 2024, 600.0, 10),
        ("Imports", "DBN", "Durban", "IN", "India", "ZA", "South Africa", 27101230, "LI", 1,
         "Maritime", 202402, 2024, 400.0, 10),
        ("Imports", "CTN", "Cape Town", "IN", "India", "ZA", "South Africa", 27101930, "KG", 1,
         "Maritime", 202402, 2024, 50.0, 10),
        ("Exports", "KFN", "Kopfontein", "ZA", "South Africa", "BW", "Botswana", 27101202, "LI",
         3, "Road", 202401, 2024, 70.0, 10),
    ])
    rows = sars.read_report(path)
    assert rows[0]["product"] == "diesel" and rows[0]["partner"] == "Oman"
    assert rows[3]["flow"] == "export" and rows[3]["partner"] == "Botswana"

    totals = {(r["flow"], r["product"], r["unit"]): r for r in sars.annual(rows)}
    assert totals[("import", "diesel", "litres")]["value"] == 1000.0
    assert totals[("import", "diesel", "litres")]["months_reported"] == 2
    assert totals[("import", "diesel", "kilograms")]["value"] == 50.0
    assert totals[("export", "petrol", "litres")]["value"] == 70.0

    by_office = sars.annual(rows, ("district_office", "transport_mode"))
    durban = [r for r in by_office if r["district_office"] == "Durban"]
    assert len(durban) == 1 and durban[0]["value"] == 1000.0


def test_every_tariff_line_maps_to_one_product() -> None:
    codes = [code for codes in sars.PRODUCT_TARIFFS.values() for code in codes]
    assert len(codes) == len(set(codes)) == len(sars.TARIFF_PRODUCT)
