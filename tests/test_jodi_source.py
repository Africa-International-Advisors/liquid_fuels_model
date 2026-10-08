"""JODI annual totals: units, partial years and the December stock level."""
from lfm.sources import jodi


def _row(period, flow, value, unit="KL", product="GASDIES", area="ZA", code="3"):
    return {"REF_AREA": area, "TIME_PERIOD": period, "ENERGY_PRODUCT": product, "FLOW_BREAKDOWN": flow,
            "UNIT_MEASURE": unit, "OBS_VALUE": value, "ASSESSMENT_CODE": code}


def test_months_are_added_in_litres_and_only_kilolitre_rows_are_used():
    rows = [_row(f"2023-{m:02d}", "REFGROUT", "100") for m in range(1, 13)]
    rows += [_row("2023-01", "REFGROUT", "629", unit="KBBL"), _row("2023-01", "REFGROUT", "5", area="AE")]
    (out,) = jodi.annual(rows)
    assert (out["product"], out["flow"], out["value"], out["unit"]) == ("diesel", "refinery_output", 1_200_000_000, "litres")
    assert out["months_reported"] == 12


def test_blank_months_are_not_filled_and_closing_stock_is_december():
    rows = [_row("2024-01", "TOTIMPSB", "10"), _row("2024-02", "TOTIMPSB", "x"),
            _row("2024-11", "CLOSTLV", "400"), _row("2024-12", "CLOSTLV", "350"), _row("2025-06", "CLOSTLV", "9")]
    out = {(r["period"], r["flow"]): r for r in jodi.annual(rows)}
    assert out[(2024, "imports")]["months_reported"] == 1
    assert out[(2024, "closing_stock")]["value"] == 350_000_000
    assert (2025, "closing_stock") not in out
