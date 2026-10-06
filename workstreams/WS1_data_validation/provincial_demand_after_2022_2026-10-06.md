# Provincial petrol and diesel after 2022 — 6 October 2026 (work package 3)

Investigated by Manish on `manish-branch`; for Nigel's review. Supports pack
pages 3, 4, 6 and 12. Nothing under `assumptions/2026/` was changed.

Status: **partial.** Observed provincial sales stop at 2023-Q1 and no later
official figure could be obtained. National totals exist for 2023 and 2024. An
estimate for 2023 and 2024 is provided and labelled as such.

## What is observed

| Period | Geography | Source | Status |
|---|---|---|---|
| 2013–2022, annual | Nine provinces | Department district workbooks (four quarters each) | Observed. 2018 is about 1.8% low: the Q1 district sheet omits districts (flag log, section 2) |
| 2023-Q1 | Nine provinces | `2023-Quarter1-Magisterial-Districts-data.xlsx` | Observed; ties to the national quarter to the litre |
| 2023, annual | National | `2023-National-Aggregated-FSV-data-Quarter4.xls`: petrol 9,036,950,000; diesel 12,907,500,000 litres (rounded) | Observed |
| 2024, annual | National | FIASA annual report 2025: petrol 9,029 ML; diesel 11,734 ML | Observed, industry source |
| 2023-Q2 onward | Provinces | — | **Not published** |
| 2025, 2026 to date | National or provincial | — | **Not found** |

## Why later provincial data is missing

- The department's sales page (`media_SAVolumes.html`, fetched 6 October 2026)
  lists no district workbook after 2023-Q1 and no national workbook after 2023.
  Twelve likely file names for 2023-Q2 to 2025 all return 404.
- The department's own "Publishing Schedule for FSV Data 2024–2026" commits to
  district data with a 12-month lag (through October–December 2024) and
  national data with a one-quarter lag (through July–September 2025). Neither
  has been met. The schedule names the contact for queries: the Deputy
  Director, Energy Data Analysis and Dissemination. Copy kept at
  `external/data/raw/energy_dept/fsv-publishing-schedule-2024-2026.pdf`
  (sha256 `083fba94…338b8cb8`), uncommitted.
- The "petrol and diesel market overview 2015–2024" named in the handover could
  not be retrieved: the `dmre.gov.za` link refuses connections, the same link on
  `dmpr.gov.za` returns 404, and web search finds only the fourth edition,
  2013–2022 (published 2024). That edition is held locally. Its provincial
  content (Figures 9 and 10, pages 16–17) is charts with no tables, and it
  draws on the same district data already extracted.

## Estimate for 2023 and 2024

File: `provincial_petrol_diesel_2013_2024_2026-10-06.csv` (234 rows: 198
observed, 36 estimated; each row carries `status` and `basis`).

Method: each province's 2022 share of the provincial sum, multiplied by the
observed national total for the year. Billion litres:

| Province | Petrol 2023 | Petrol 2024 | Diesel 2023 | Diesel 2024 |
|---|---|---|---|---|
| Gauteng | 3.47 | 3.47 | 3.33 | 3.03 |
| KwaZulu-Natal | 1.47 | 1.47 | 2.83 | 2.57 |
| Western Cape | 1.41 | 1.41 | 2.54 | 2.31 |
| Eastern Cape | 0.69 | 0.69 | 1.05 | 0.95 |
| Mpumalanga | 0.60 | 0.60 | 1.16 | 1.06 |
| Free State | 0.58 | 0.58 | 0.79 | 0.72 |
| North West | 0.44 | 0.44 | 0.63 | 0.57 |
| Limpopo | 0.27 | 0.27 | 0.23 | 0.20 |
| Northern Cape | 0.10 | 0.10 | 0.36 | 0.32 |
| **National (observed)** | **9.04** | **9.03** | **12.91** | **11.73** |

How far to trust it. Back-test over 2014–2022: predict each year from the
previous year's shares and the actual national total.

| Mean absolute error | Petrol | Diesel |
|---|---|---|
| Gauteng | 2.2% | 4.7% |
| KwaZulu-Natal | 2.1% | 7.8% |
| Western Cape | 2.4% | 11.3% (worst year 39%) |
| Eastern Cape | 2.3% | 3.0% |
| Mpumalanga | 7.0% | 8.1% |
| Free State | 10.0% | 9.9% |
| North West | 3.9% | 9.3% |
| Limpopo | 4.4% | 11.2% |
| Northern Cape | 4.8% | 5.6% |

- **Petrol shares are stable** for the large provinces; the estimate is usable
  with a 2–3% caveat there, more for Free State and Mpumalanga.
- **Diesel shares are not stable.** The one later observation confirms it:
  between 2022-Q1 and 2023-Q1 KwaZulu-Natal's diesel share fell from 23.1% to
  19.0% and the Western Cape's rose from 17.7% to 23.5%. Recorded diesel sales
  appear to follow where wholesale volumes are booked, not only where fuel is
  used. A 2024 provincial diesel figure from held shares should not be shown
  as more than indicative.
- The estimate also assumes two years with no change in shares, which the
  one-year back-test does not cover.

## Provincial driver evidence for the unobserved period

NaTIS live vehicle population by province (already extracted, monthly to June
2026), December snapshots, December 2022 = 100:

| Province | Cars and minibuses, Dec 2024 | Dec 2025 | Light commercial, trucks and buses, Dec 2024 | Dec 2025 |
|---|---|---|---|---|
| Gauteng | 103.5 | 106.7 | 103.5 | 105.3 |
| KwaZulu-Natal | 103.9 | 108.0 | 103.6 | 107.1 |
| Western Cape | 104.4 | 107.2 | 103.6 | 106.0 |
| Limpopo | 105.3 | 109.1 | 102.2 | 104.0 |
| Eastern Cape | 101.7 | 103.4 | 100.3 | 101.1 |
| Mpumalanga | 102.4 | 104.2 | 100.3 | 100.6 |
| North West | 102.4 | 104.5 | 101.9 | 103.4 |
| Free State | 99.7 | 100.5 | 101.4 | 103.0 |
| Northern Cape | 100.3 | 101.6 | 101.8 | 102.6 |

Provincial shares of the vehicle stock moved by less than 0.3 percentage
points over the three years, which is consistent with holding petrol shares.
Vehicle stock is all fuels together and is not fuel sold; it has not been used
to adjust the estimate.

Not yet collected: Stats SA provincial GDP (P0441.2, 2024). The site blocks
scripted downloads; it needs a manual download like the other Stats SA files.

## Open items

| Item | Owner | Next action |
|---|---|---|
| "2015–2024" overview report | Nigel | Confirm where the link was seen; retry `dmre.gov.za` from another network |
| National sales 2025 and 2026 to date | Manish | FIASA annual report 2026 when published; department national workbook if released |
| Provincial GDP as a driver | Manish | Manual download of Stats SA P0441.2 |
| Whether the pack may show estimated 2023–2024 provincial bars | Nigel | Decision; recommended for petrol only, clearly labelled |

## Review outcomes and the 2024 national total, 6 October

Manish accepted the finding that no official provincial figure exists after
2023-Q1. The estimate method and what the pack may show are left for Nigel.

**Can the 2024 national total be verified? No.** Manish asked for other
sources. Four were checked; they do not agree with either FIASA version or
with each other. Billion litres, calendar 2024 unless stated:

| Source | Petrol | Diesel | Note |
|---|---|---|---|
| FIASA annual report 2025, p.47 | 9.03 | 11.73 | The same row is printed again for 2025 |
| FIASA annual report 2024, p.32 | 8.76 | 11.81 | Earlier edition; may be preliminary |
| JODI oil database, demand reported by South Africa | 10.14 | 10.04 | All twelve months; every South African entry carries JODI's lowest reliability code (3) |
| SARS, fuel on which levy was declared | 21 for both fuels together, April 2024 to February 2025 (24 the year before) | | Media release of 12 March 2025; eleven months of a fiscal year, both fuels together |
| Department national sales workbook | — | — | Not published for 2024 |

For 2023, where the department's own figure exists (petrol 9.04, diesel 12.91),
JODI gives 11.68 and 13.85, so JODI is not a reliable check on the level.

What can be said: 2024 petrol sales lie between 8.8 and 10.1 bn litres and
diesel between 10.0 and 11.8 bn across the sources; all sources show diesel
falling from 2023. The estimate in this note keeps FIASA's 2025 edition (9.03
and 11.73), flagged as unverified. Each provincial figure for 2024 carries that
uncertainty on top of the share error.

Dropped by Manish on 6 October: requesting the unpublished provincial data
from the department, and approaching a commercial data provider. Neither is an
open action.
