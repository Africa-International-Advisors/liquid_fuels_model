"""NaTIS reader — text copied from the published PDFs; no network or files."""
from __future__ import annotations

from lfm.sources import natis

POPULATION = """31 May 2026  -  Live vehicle population as per the National Traffic Information System - NaTIS
GP KZN WC EC FS MP NW L NC
Motor cars and station wagons                                                      3 473 498 1 167 884 1 445 241  505 260  327 501  476 412  364 663  417 521  138 268 8 316 248 66.10%
Trucks (Heavy load vehicles GVM > 3500kg)  150 813  59 132  50 836  23 090  26 068  41 124  18 890  28 207  9 820  407 980 3.24%
Total self-propelled vehicles 4 904 403 1 778 163 2 055 189  812 341  560 172  829 778  612 806  769 014  259 441 12 581 307
30 June 2026  -  Live vehicle population as per the National Traffic Information System - NaTIS
GP KZN WC EC FS MP NW L NC
Motor cars and station wagons                                                      3 485 272 1 171 505 1 448 715  506 193  328 418  477 358  365 628  419 050  138 453 8 340 592 66.12%
Increase / Decrease in Live Vehicle Population from 31 May 2026 to 30 June 2026
Motor cars and station wagons                                                       11 774  3 621  3 474   933   917   946   965  1 529   185  24 344 0.29%
"""


def _national(rows: list[dict]) -> dict[tuple[str, str], int]:
    return {(r["period"], r["vehicle_class"]): r["value"] for r in rows if r["province"] == "ZAF"}


def test_population_rows_are_placed_by_the_provincial_sum() -> None:
    rows, warnings = natis.parse(POPULATION)
    assert warnings == []
    national = _national(rows)
    assert national[("2026-05", "cars")] == 8_316_248
    assert national[("2026-05", "trucks")] == 407_980
    assert national[("2026-05", "total_self_propelled")] == 12_581_307
    gauteng = next(r for r in rows if r["period"] == "2026-05"
                   and r["vehicle_class"] == "cars" and r["province"] == "GP")
    assert gauteng["value"] == 3_473_498


def test_the_month_on_month_change_table_is_not_read_as_population() -> None:
    rows, _ = natis.parse(POPULATION)
    assert _national(rows)[("2026-06", "cars")] == 8_340_592


def test_older_files_decimal_comma_double_space_date_and_misspelt_month() -> None:
    text = (
        "30  Nonember 2018 -  New vehicle registrations as per the National Traffic "
        "Information System - eNaTIS\nGP KZ WC EC FS MP NW L NC\n"
        "Minibuses   771   295   228   197   51   151   76   170   21  1 960 4,52%\n"
    )
    rows, warnings = natis.parse(text)
    assert warnings == []
    assert _national(rows) == {("2018-11", "minibuses"): 1960}


def test_row_with_a_blank_province_gives_the_national_total_only() -> None:
    text = (
        "31 December 2025  -  New vehicle registrations as per the National Traffic "
        "Information System - NaTIS\n"
        "Buses, bus trains, midibuses   77   9   26   18   6   18   2   13   169 0.59%\n"
    )
    rows, warnings = natis.parse(text)
    assert warnings == []
    assert rows == [{"period": "2025-12", "vehicle_class": "buses",
                     "province": "ZAF", "value": 169}]


def test_row_whose_figures_do_not_add_up_is_left_out() -> None:
    text = (
        "31 December 2025  -  Live vehicle population as per NaTIS\n"
        "Minibuses  127 615  61 522  41 471  27 483  12 631  28 375  22 240  28 633  6 825  999 999 2.84%\n"
    )
    rows, warnings = natis.parse(text)
    assert rows == []
    assert warnings == ["2025-12 minibuses: columns could not be placed"]


def test_same_date_on_two_tables_is_left_out_not_guessed() -> None:
    table = ("28 February 2019 -  New vehicle registrations as per NaTIS\n"
             "Minibuses   771   295   228   197   51   151   76   170   21  1 960 4,52%\n")
    rows, warnings = natis.parse(table + table)
    assert rows == []
    assert warnings == ["2019-02: date printed on two tables, both left out"]


def test_discover_files_ignores_the_broken_localhost_host() -> None:
    listing = (
        '<a href="http://localhost/nat/media/com_natisdownloads/files/'
        'LiveVehPopPerClassProv20240531-20260715-142714.pdf">Download</a>'
        '<a href="https://www.natis.gov.za/media/com_natisdownloads/files/'
        'NewVehicleRegistration20251231-20260713-183033.pdf">Download</a>'
    )
    files = natis.discover_files(listing, "population")
    assert [(f.period, f.url) for f in files] == [(
        "2024-05",
        "https://www.natis.gov.za/media/com_natisdownloads/files/"
        "LiveVehPopPerClassProv20240531-20260715-142714.pdf",
    )]


def test_category_pages_come_from_the_site_menu() -> None:
    home = ('<a href="/index.php/statistics/live-vehicle-population/'
            'live-vehicle-population-2026?view=category&amp;amp;id=5">2026</a>'
            '<a href="/index.php/statistics/new-vehicle-registrations/'
            'new-vehicle-registrations-2026?view=category&amp;id=6">2026</a>')
    assert natis.category_pages(home, "population") == [
        "https://www.natis.gov.za/index.php/statistics/live-vehicle-population/"
        "live-vehicle-population-2026?view=category&id=5"
    ]
