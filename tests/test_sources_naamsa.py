"""naamsa reader — text copied from the published PDFs; no network or files."""
from __future__ import annotations

from lfm.sources import naamsa

NEV_2026 = """The following table reveals the diversity
 of drivetrain sales in the South African NEV landscape from
2020 through to 2026 Q2

 Year
2020
Year
2021
Year
2022
Year
2023
Year
2024
Year
2025
Q2:2025 Q2:2026
Tr a d i t i o n a l  h y b r i d 155 627 4,070 6,485 13,616 12,818 2,834 3,912
Plug-in hybrid 77 51 122 368 738 2,810 547 3,346
Electric  92 218 502 929 1,257 1,088 294 1,353
To t a l  N E Vs 324 896 4,694 7,782 15,611 16,716 3,675 8,611

The accelerating adoption of electrified vehicles
"""

NEV_2025 = """diversity of drivetrain sales in the South African NEV landscape from
2020 through to Q1:2025.
 FY2020 FY2021 FY2022 FY2023 FY2024 Q1:2024 Q1:2025
Plug-in hybrid 77 51 122 368 738 141 241
Traditional hybrid 155 627 4,070 6,485 13,616 2,587 2,970
Electric 92 218 502 929 1,257 330 276
Total NEVs 324 896 4,694 7,782 15,611 3,058 3,487
"""

MARKET = """
2023 2024 2025 2026 2027
CARS
Local Sales 79 110 77 573 72 541 75 000 80 000
TOTAL LOCAL CAR  MARKET 347 377 351 553 422 463 465 000 490 000
LIGHT COMMERCIALS
TOTAL LOCAL LCV MARKET 151 490 133 375 143 964 160 000 180 000
MEDIUM & HEAVY COMMERCIALS
TOTAL LOCAL MCV/HCV MARKET 32690 31 175 30 911 31 000 32 000
TOTAL AGGREGATE MARKET 531 557 516 103 597 338 656 000 702 000
TOTAL AGGREGATE EXPORTS 399 809 391 128 414 271 431 500 462 000
"""


def test_nev_table_with_spaced_out_labels_and_stacked_year_headings() -> None:
    table, warnings = naamsa.parse_nev(NEV_2026)
    assert warnings == []
    assert sorted(table) == [2020, 2021, 2022, 2023, 2024, 2025]   # quarters ignored
    assert table[2025] == {"traditional_hybrid": 12818, "plug_in_hybrid": 2810,
                           "battery_electric": 1088, "total": 16716}


def test_nev_table_older_one_line_heading() -> None:
    table, warnings = naamsa.parse_nev(NEV_2025)
    assert warnings == []
    assert table[2024]["total"] == 15611
    assert 2025 not in table


def test_nev_year_is_left_out_when_drivetrains_do_not_add_up() -> None:
    table, warnings = naamsa.parse_nev(NEV_2025.replace("Total NEVs 324", "Total NEVs 999"))
    assert 2020 not in table and 2021 in table
    assert warnings == ["new energy vehicles 2020: drivetrains do not add up to the total"]


def test_nev_table_missing() -> None:
    assert naamsa.parse_nev("no table here") == ({}, ["new energy vehicle table not found"])


def test_market_table_mixed_number_spacing() -> None:
    table, warnings = naamsa.parse_market(MARKET)
    assert warnings == []
    assert table[2023] == {"cars": 347377, "light_commercial": 151490,
                           "medium_heavy_commercial": 32690, "total": 531557}
    assert table[2027]["total"] == 702000


def test_market_year_is_left_out_when_segments_are_far_from_the_aggregate() -> None:
    table, warnings = naamsa.parse_market(MARKET.replace("531 557", "631 557"))
    assert 2023 not in table and 2024 in table
    assert warnings == ["market 2023: segments do not add up to the aggregate"]


def test_discover_sorts_reviews_and_projection_files_by_upload_month() -> None:
    html = (
        '<a href="https://naamsa.net/wp-content/uploads/2026/08/'
        '20260820-naamsa-2nd-Quarter-2026-Review-of-Business-Conditions.pdf">'
        '<a href="https://naamsa.net/wp-content/uploads/2026/08/'
        '20260817-Industry-Vehicle-Sales-2017-2027-Actual-and-Projections-updated.pdf">'
        '<a href="https://naamsa.net/wp-content/uploads/2025/05/'
        '20250526-naamsa-Q1-Review-of-Business-Conditions-2025.pdf">'
        '<a href="https://naamsa.net/wp-content/uploads/2026/10/20261001-Flash-Report.pdf">'
    )
    files = naamsa.discover(html)
    assert [(f.kind, f.uploaded) for f in files] == [
        ("review", "2025-05"), ("projections", "2026-08"), ("review", "2026-08")]
