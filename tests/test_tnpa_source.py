"""Port authority cargo summaries: the liquid bulk block, negative corrections and the publisher's odd files."""
import pytest

from lfm.scripts import stage_tnpa
from lfm.sources import tnpa

HEADER = "   RICHARDS BAY      DURBAN   EAST LONDON   NGQURA   PORT ELIZABETH   MOSSEL BAY   CAPE TOWN   SALDANHA   TOTAL"


def summary(title="AUG 2026", heading="SUMMARY OF CARGO HANDLED AT PORTS OF SOUTH AFRICA", transhipment="5-      -      -      -      -      -      -      -      5-"):
    return "\n".join([
        heading, title, "EXPRESSED IN METRIC TONS", "DRY BULK CARGO HANDLED", "IMPORTS 9      9      -      -      -      -      -      -      18",
        "LIQUID BULK CARGO HANDLED -", "LANDED -",
        "IMPORTS 100      1 200 300      -      -      -      -      50      -      1 200 450",
        "TOTAL LIQUIDBULK LANDED 100      1 200 300      -      -      -      -      50      -      1 200 450",
        "EXPORTS 10      20      -      -      -      -      -      -      30",
        "COASTWISE LIQUID BULK CARGO -      40      -      -      -      -      -      -      40",
        f"TRANSHIPMENT LIQUID BULK CARGO {transhipment}",
        "TOTAL LIQUIDBULK HANDLED 105      1 200 360      -      -      -      -      50      -      1 200 515",
        "BREAKBULK CARGO HANDLED", "IMPORTS 1      1      -      -      -      -      -      -      2"])


def cell(rows, port, movement):
    return next(r["value"] for r in rows if (r["port"], r["movement"]) == (port, movement))


def test_liquid_bulk_block_is_read_by_port_with_negative_corrections():
    rows = tnpa.parse_liquid_bulk(summary(), HEADER)
    assert {r["period"] for r in rows} == {"2026-08"} and rows[0]["period_basis"] == "month"
    assert cell(rows, "Durban", "landed") == 1_200_300 and cell(rows, "All ports", "handled") == 1_200_515
    assert cell(rows, "Richards Bay", "transhipment") == -5          # "5-" in the source
    assert cell(rows, "Ngqura", "landed") == 0                        # "-" is nil
    assert len(rows) == 5 * 9 and {r["unit"] for r in rows} == {"tonnes"}


def test_calendar_year_and_invoiced_headings_are_recognised():
    year = tnpa.parse_liquid_bulk(summary("JAN - DEC 2025 (CALENDAR YEAR)"), HEADER)
    assert (year[0]["period"], year[0]["period_basis"]) == ("2025", "calendar year")
    invoiced = tnpa.parse_liquid_bulk(summary("APR 2026 0", "SUMMARY OF CARGO INVOICED AT PORTS OF SOUTH AFRICA"), HEADER)
    assert (invoiced[0]["period"], invoiced[0]["measure"]) == ("2026-04", "invoiced")


def test_wrong_columns_rows_that_do_not_add_and_other_reports_are_refused():
    with pytest.raises(ValueError, match="unexpected port columns"):
        tnpa.parse_liquid_bulk(summary(), HEADER.replace("DURBAN", "DURBAN  SALDANHA"))
    with pytest.raises(ValueError, match="do not add"):
        tnpa.parse_liquid_bulk(summary(transhipment="900      -      -      -      -      -      -      -      900"), HEADER)
    with pytest.raises(tnpa.NotACargoSummary):
        tnpa.period_of("NATIONAL PORT AUTHORITY OF SOUTH AFRICA\nEXPRESSED IN 6M UNITS (TEU'S)\nJAN 2025")


def test_staging_skips_copies_keeps_mislabelled_months_with_a_note_and_never_fills_a_month():
    may_2025 = tnpa.parse_liquid_bulk(summary("MAY 2025"), HEADER)
    different = tnpa.parse_liquid_bulk(summary("MAY 2025").replace("1 200 300", "1 200 301").replace("1 200 450", "1 200 451")
                                       .replace("1 200 360", "1 200 361").replace("1 200 515", "1 200 516"), HEADER)
    rows, problems = stage_tnpa.assemble([
        ("a.pdf", "2025-01", "container report"),
        ("b.pdf", "2025-05", may_2025),
        ("c.pdf", "2025-06", tnpa.parse_liquid_bulk(summary("MAY 2025"), HEADER)),      # an exact copy of May
        ("d.pdf", "2026-05", different),                                                 # May 2025 heading, other figures
    ])
    assert sorted({r["period"] for r in rows}) == ["2025-05", "2026-05"]
    assert {r["note"] for r in rows if r["period"] == "2026-05"} == {
        "heading says 2025-05; the page lists it as 2026-05 and the figures differ from 2025-05"}
    assert len(problems) == 3 and "2025-01 has no figures" in problems[0] and "2025-06 has no figures" in problems[1]


def test_statistics_page_records_are_discovered():
    html = '''<div class="cargoRecord" style="display: none;"><span class="cargo-doc1">getFile.ashx?id=7</span>
      <span class="cargo-date">2026-08</span><span class="cargo-type">Monthly</span></div>
      <div class="cargoRecord"><span class="cargo-doc1">getFile.ashx?id=9</span><span class="cargo-date">2025-12</span>
      <span class="cargo-type">Annual</span></div>'''
    assert tnpa.discover(html) == [
        {"period": "2025-12", "kind": "annual", "url": "https://www.transnet.net/getFile.ashx?id=9"},
        {"period": "2026-08", "kind": "monthly", "url": "https://www.transnet.net/getFile.ashx?id=7"}]
