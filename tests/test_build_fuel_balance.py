"""The petrol and diesel balance: source selection and agreement with the customs extract."""
import csv
from pathlib import Path

import pytest

from lfm.scripts import build_fuel_balance as bfb

ROOT = Path(__file__).resolve().parents[1]
TIMESERIES = ROOT / "assumptions" / "2026" / "timeseries"
BALANCE = ROOT / bfb.DEFAULT_OUT


def _inputs(sars_rows):
    def trade(period, flow, value, report="2024"):
        return {"period": period, "flow": flow, "product": "diesel", "value": value, "source_report": report}
    return {
        "fuel_sales_department": [
            {"period": "2013", "product": "diesel", "value": "100", "quarters_reported": "4"},
            {"period": "2014", "product": "diesel", "value": "110", "quarters_reported": "4"},
            {"period": "2015", "product": "diesel", "value": "999", "quarters_reported": "3"},
        ],
        "fuel_sales_fiasa": [
            {"period": "2015", "product": "diesel", "value": "118", "source_report": "2024"},
            {"period": "2015", "product": "diesel", "value": "120", "source_report": "2025"},
        ],
        "fuel_trade_fiasa": [trade("2013", "import", "40"), trade("2013", "export", "10"),
                             trade("2014", "import", "55"), trade("2014", "export", "12"),
                             trade("2015", "import", "60"), trade("2015", "export", "15")],
        "fuel_trade_sars": sars_rows,
        "fuel_trade_department_review": [],
        "energy_balance_department": [
            {"period": "2013", "flow_key": "production", "product": "diesel", "value": "65"},
            {"period": "2013", "flow_key": "exports", "product": "diesel", "value": "-9"},
        ],
    }


def _sars(period, flow, value, unit="litres", months="12"):
    return {"period": period, "flow": flow, "product": "diesel", "value": value, "unit": unit,
            "months_reported": months}


def _row(rows, year):
    return next(r for r in rows if r["product"] == "diesel" and r["period"] == year)


def test_customs_is_selected_from_2014_and_fiasa_is_never_selected():
    rows = bfb.build(_inputs([_sars("2013", "import", "41"), _sars("2013", "export", "11"),
                              _sars("2014", "import", "50"), _sars("2014", "export", "13")]))
    before, after = _row(rows, 2013), _row(rows, 2014)
    assert (before["trade_used_source"], before["imports_used"], before["exports_used"]) == ("", "", "")
    assert (before["imports_fiasa"], before["sales_less_net_imports"]) == (40, "")   # shown, not used
    assert (after["trade_used_source"], after["imports_used"], after["exports_used"]) == ("SARS customs", 50, 13)
    assert (after["imports_fiasa"], after["exports_fiasa"]) == (55, 12)
    assert after["sales_less_net_imports"] == 110 - (50 - 13)
    assert before["exports_energy_balance"] == 9


def test_part_years_and_kilogram_records_are_not_selected():
    rows = bfb.build(_inputs([_sars("2014", "import", "50", unit="kilograms"), _sars("2014", "export", "13"),
                              _sars("2015", "import", "30", months="8"), _sars("2015", "export", "7", months="8")]))
    assert _row(rows, 2014)["trade_used_source"] == ""
    assert _row(rows, 2014)["imports_sars"] == ""
    assert _row(rows, 2015)["trade_used_source"] == ""


def test_incomplete_department_year_is_left_blank_and_fiasa_stays_a_comparison():
    row = _row(bfb.build(_inputs([])), 2015)
    assert (row["sales_used"], row["sales_used_source"]) == ("", "")
    assert (row["sales_fiasa"], row["sales_fiasa_edition"]) == (120, "2025")


@pytest.mark.skipif(not BALANCE.exists(), reason="balance file not built")
def test_committed_balance_matches_the_registered_inputs_and_the_customs_extract():
    def read(path):
        with path.open(encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))

    stems = ["fuel_sales_department_by_province", "fuel_sales_department", "fuel_sales_fiasa", "fuel_trade_sars",
             "fuel_trade_fiasa", "fuel_trade_department_review", "energy_balance_department", "oil_balance_jodi"]
    inputs = {stem: read(TIMESERIES / f"{stem}.csv") for stem in stems}
    expected = [{k: str(round(v)) if isinstance(v, float) else str(v) for k, v in row.items()}
                for row in bfb.build(inputs)]
    committed = read(BALANCE)
    assert committed == expected, "rebuild with: python -m lfm.scripts.build_fuel_balance --vintage 2026"

    customs = bfb.sars_annual(inputs["fuel_trade_sars"])
    for row in committed:
        year = int(row["period"])
        if year < bfb.SARS_PRIMARY_FROM:
            assert row["trade_used_source"] == "" and row["imports_used"] == ""
            continue
        assert row["trade_used_source"] == "SARS customs", (year, row["product"])
        for flow, name in (("import", "imports"), ("export", "exports")):
            assert float(row[f"{name}_used"]) == round(customs[(row["period"], flow, row["product"])][0])
        if row["sales_used"]:
            residual = float(row["sales_used"]) - float(row["imports_used"]) + float(row["exports_used"])
            assert abs(float(row["sales_less_net_imports"]) - residual) <= 2


def test_production_is_the_energy_balance_only_and_jodi_is_never_selected():
    inputs = _inputs([_sars("2013", "import", "41"), _sars("2013", "export", "11"),
                      _sars("2014", "import", "50"), _sars("2014", "export", "13")])
    inputs["energy_balance_department"].append(
        {"period": "2014", "flow_key": "production", "product": "diesel", "value": "75", "source_file": "2014-balance.xlsx"})

    def jodi(period, flow, value, months="12"):
        return {"period": period, "flow": flow, "product": "diesel", "value": value, "months_reported": months}
    inputs["oil_balance_jodi"] = [jodi("2014", "refinery_output", "80"), jodi("2015", "refinery_output", "90")]
    rows = bfb.build(inputs)
    with_balance, without = _row(rows, 2014), _row(rows, 2015)
    assert (with_balance["production_used"], with_balance["production_used_source"]) == (75, "energy balance")
    assert "2014-balance.xlsx" in with_balance["production_used_source_ref"]
    assert with_balance["production_jodi"] == 80                 # shown alongside, not selected
    assert with_balance["supply_less_sales"] == 75 + (50 - 13) - 110
    assert (without["production_jodi"], without["production_used"], without["supply_less_sales"]) == (90, "", "")


def test_every_selected_figure_in_the_committed_balance_names_its_source():
    with BALANCE.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        for value, source in (("sales_used", "sales_used"), ("imports_used", "trade_used"), ("production_used", "production_used")):
            named = row[f"{source}_source"] != "" and row[f"{source}_source_ref"] != ""
            assert named == (row[value] != ""), (row["period"], row["product"], value)
        year = int(row["period"])
        expected = "department, by province" if 2013 <= year <= 2022 else "department, national" if year <= 2023 else ""
        assert row["sales_used_source"] == expected, (year, row["product"])
        if expected == "department, by province":
            assert row["sales_used"] == row["sales_provinces"]
        assert row["trade_used_source"] in ("", "SARS customs")
        assert row["production_used_source"] in ("", "energy balance")
        if int(row["period"]) > 2021:
            assert row["production_used"] == "" and row["supply_less_sales"] == ""
        if row["production_used"]:
            assert f"{row['period']}-Commodity-Flow-and-Energy-Balance" in row["production_used_source_ref"]


def test_provincial_sales_are_used_where_all_nine_provinces_are_published():
    inputs = _inputs([_sars("2014", "import", "50"), _sars("2014", "export", "13")])
    inputs["fuel_sales_department_by_province"] = (
        [{"period": "2014", "product": "diesel", "province": f"P{i}", "value": "13"} for i in range(9)]
        + [{"period": "2013", "product": "diesel", "province": f"P{i}", "value": "13"} for i in range(8)])
    rows = bfb.build(inputs)
    full, short = _row(rows, 2014), _row(rows, 2013)
    assert (full["sales_used"], full["sales_used_source"]) == (117, "department, by province")   # not the national 110
    assert full["sales_department"] == 110                                                       # kept alongside
    assert (short["sales_used"], short["sales_used_source"]) == (100, "department, national")     # eight provinces only
