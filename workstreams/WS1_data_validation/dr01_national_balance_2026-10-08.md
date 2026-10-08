# DR01 National product balance: evidence and reconciliation, 8 October 2026

For Nigel's review. Answers request DR01 in
`output/delivered/investment_bridge_2026_10_08/data_request.csv` and milestone
M1 in `sa_review_milestone_2026_10_08.md`: petrol and diesel sales, imports,
exports, production and stocks, with periods and definitions reconciled and no
residual labelled as production.

Status: **four of five lines are sourced; the matched years are 2014 to 2021.**
Stocks are not available from any source. Production stops at 2021 and sales
at 2023, where the department's publications stop.

## Sources used, and only these

| Line | Source | Years | Address |
|---|---|---|---|
| Sales | Department of Mineral and Petroleum Resources, national fuel sales volumes | 2009-2023 | https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/media_SAVolumes.html |
| Imports, exports | SARS customs, trade statistics portal | 2014-2025 | https://tools.sars.gov.za/tradestatsportal/data_download.aspx |
| Production | Department of Mineral and Petroleum Resources, energy balances | 2009-2021 | https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/Energy_Balances.html |
| Stocks | None | — | — |

FIASA and JODI are **not used** for any figure. Both are kept in their own
columns of the balance file and as rows marked "Not used" in the workbook, so
the comparison can be seen.

Every selected figure in the balance file names its source twice: the
publisher (`*_used_source`) and the file and address (`*_used_source_ref`). A
test fails if a selected figure has no source, or if FIASA or JODI is selected.

Files:

- Balance: `fuel_balance_petrol_diesel_2009_2025_2026-10-06.csv`, rebuilt by
  `python -m lfm.scripts.build_fuel_balance --vintage 2026`.
- Evidence table: `dr01_national_balance_evidence_2026-10-08.csv`.
- Energy balance references: `dr01_energy_balance_references_2026-10-08.csv`.
- Workbook: History sheet, sections 2 to 4.

## The energy balance files

The department publishes one workbook a year, 2007 to 2021. All fifteen are
held in `external/data/refresh_20261005/raw/energy_dept/energy_balance/`. On
8 October each was downloaded again from the department's site and compared
with the held copy; all fifteen are identical. The department's page lists no
balance after 2021. Production is the "Production" line of each file, in
kilolitres, shown here in billion litres:

| Year | File | Petrol | Diesel | Same as today's download |
|---|---|---|---|---|
| 2007 | [2007-Commodity-Flow-and-Energy-Balance.xlsx](https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/explained/2007-Commodity-Flow-and-Energy-Balance.xlsx) | 10.24 | 8.92 | yes |
| 2008 | [2008-Commodity-Flow-and-Energy-Balance.xlsx](https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/explained/2008-Commodity-Flow-and-Energy-Balance.xlsx) | 11.12 | 12.11 | yes |
| 2009 | [2009-Commodity-Flow-and-Energy-Balance.xlsx](https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/explained/2009-Commodity-Flow-and-Energy-Balance.xlsx) | 10.52 | 11.27 | yes |
| 2010 | [2010-Commodity-Flow-and-Energy-Balance.xlsx](https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/explained/2010-Commodity-Flow-and-Energy-Balance.xlsx) | 9.50 | 9.63 | yes |
| 2011 | [2011-Commodity-Flow-and-Energy-Balance.xlsx](https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/explained/2011-Commodity-Flow-and-Energy-Balance.xlsx) | 10.91 | 11.37 | yes |
| 2012 | [2012-Commodity-Flow-and-Energy-Balance.xlsx](https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/explained/2012-Commodity-Flow-and-Energy-Balance.xlsx) | 9.64 | 9.66 | yes |
| 2013 | [2013-Commodity-Flow-and-Energy-Balance.xlsx](https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/explained/2013-Commodity-Flow-and-Energy-Balance.xlsx) | 10.48 | 9.38 | yes |
| 2014 | [2014-Commodity-Flow-and-Energy-Balance.xlsx](https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/explained/2014-Commodity-Flow-and-Energy-Balance.xlsx) | 10.83 | 9.59 | yes |
| 2015 | [2015-Commodity-Flow-and-Energy-Balance.xlsx](https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/explained/2015-Commodity-Flow-and-Energy-Balance.xlsx) | 10.46 | 9.37 | yes |
| 2016 | [2016-Commodity-Flow-and-Energy-Balance.xlsx](https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/explained/2016-Commodity-Flow-and-Energy-Balance.xlsx) | 10.39 | 9.01 | yes |
| 2017 | [2017-Commodity-Flow-and-Energy-Balance.xlsx](https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/explained/2017-Commodity-Flow-and-Energy-Balance.xlsx) | 9.43 | 7.92 | yes |
| 2018 | [2018-Commodity-Flow-and-Energy-Balance.xlsx](https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/explained/2018-Commodity-Flow-and-Energy-Balance.xlsx) | 9.97 | 8.43 | yes |
| 2019 | [2019-Commodity-Flow-and-Energy-Balance.xlsx](https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/explained/2019-Commodity-Flow-and-Energy-Balance.xlsx) | 10.42 | 9.08 | yes |
| 2020 | [2020-Commodity-Flow-and-Energy-Balance.xlsx](https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/explained/2020-Commodity-Flow-and-Energy-Balance.xlsx) | 7.89 | 6.45 | yes |
| 2021 | [2021-Commodity-Flow-and-Energy-Balance.xlsm](https://www.dmpr.gov.za/Portals/0/Energy_Website/files/media/explained/2021-Commodity-Flow-and-Energy-Balance.xlsm) | 6.35 | 5.31 | yes |

The reference file adds the checksum of each workbook.

## The balance, billion litres

Supply is production plus imports less exports. **Supply less sales** is what
is left: the stock change and the statistical difference together. It is not
production, and nothing is adjusted with it.

Diesel:

| Year | Production | Imports | Exports | Supply | Sales | Supply less sales |
|---|---|---|---|---|---|---|
| 2014 | 9.59 | 4.99 | 1.49 | 13.09 | 12.62 | +0.47 |
| 2015 | 9.37 | 6.45 | 1.61 | 14.21 | 13.52 | +0.69 |
| 2016 | 9.01 | 4.42 | 1.89 | 11.55 | 12.08 | -0.53 |
| 2017 | 7.92 | 6.04 | 1.78 | 12.18 | 12.15 | +0.03 |
| 2018 | 8.43 | 5.12 | 1.58 | 11.97 | 12.54 | -0.57 |
| 2019 | 9.08 | 5.59 | 1.74 | 12.93 | 12.91 | +0.02 |
| 2020 | 6.45 | 6.81 | 0.91 | 12.35 | 11.69 | +0.66 |
| 2021 | 5.31 | 9.76 | 0.89 | 14.18 | 12.95 | +1.24 |
| 2022 | — | 11.95 | 0.89 | — | 12.72 | — |
| 2023 | — | 12.87 | 0.89 | — | 12.91 | — |
| 2024 | — | 10.79 | 0.80 | — | — | — |
| 2025 | — | 12.25 | 0.75 | — | — | — |

Petrol:

| Year | Production | Imports | Exports | Supply | Sales | Supply less sales |
|---|---|---|---|---|---|---|
| 2014 | 10.83 | 1.15 | 0.99 | 10.99 | 10.89 | +0.10 |
| 2015 | 10.46 | 1.87 | 1.09 | 11.24 | 11.48 | -0.23 |
| 2016 | 10.39 | 1.40 | 1.16 | 10.63 | 11.46 | -0.83 |
| 2017 | 9.43 | 2.11 | 1.08 | 10.47 | 11.17 | -0.70 |
| 2018 | 9.97 | 1.83 | 1.14 | 10.67 | 11.14 | -0.47 |
| 2019 | 10.42 | 1.48 | 1.17 | 10.73 | 10.77 | -0.05 |
| 2020 | 7.89 | 1.72 | 1.15 | 8.46 | 8.76 | -0.30 |
| 2021 | 6.35 | 4.01 | 1.05 | 9.31 | 9.30 | +0.01 |
| 2022 | — | 5.46 | 0.85 | — | 9.18 | — |
| 2023 | — | 4.48 | 0.99 | — | 9.04 | — |
| 2024 | — | 4.00 | 0.92 | — | — | — |
| 2025 | — | 4.45 | 0.80 | — | — | — |

Reading: for the eight matched years, 2014 to 2021, supply and recorded sales
agree within 0.9 bn litres in every year but one. The exception is diesel in
2021, where supply is 1.24 bn litres above recorded sales. One year is not
a trend, and the stock change is not known. It is consistent with, but does
not establish, the hypothesis that recorded diesel sales fall short of supply.

After 2021 the balance cannot be computed: there is no production figure for
2022 or 2023, and no sales figure for 2024 or 2025.

## The 2021 to 2022 bridge

2021 is the last year with a published energy balance.

Diesel, billion litres:

| Line | 2021 | 2022 | Change | Source |
|---|---|---|---|---|
| Production | 5.31 | — | — | Department energy balance; none for 2022 |
| Imports | 9.76 | 11.95 | +2.19 | SARS customs |
| Exports | 0.89 | 0.89 | -0.00 | SARS customs |
| Sales | 12.95 | 12.72 | -0.23 | Department national sales |
| Supply less sales | 1.24 | — | — | Calculated |

Petrol, billion litres:

| Line | 2021 | 2022 | Change | Source |
|---|---|---|---|---|
| Production | 6.35 | — | — | Department energy balance; none for 2022 |
| Imports | 4.01 | 5.46 | +1.45 | SARS customs |
| Exports | 1.05 | 0.85 | -0.20 | SARS customs |
| Sales | 9.30 | 9.18 | -0.12 | Department national sales |
| Supply less sales | 0.01 | — | — | Calculated |

Between 2021 and 2022 diesel imports rose 2.2 bn litres and petrol imports
1.4, while recorded sales fell slightly. Without a 2022 production figure the
bridge cannot be closed.

## Definitions and where the sources differ

| Line | Definition | Not reconciled with |
|---|---|---|
| Sales | Volumes returned by licensed wholesalers, calendar year, litres | Energy balance final consumption; Road Accident Fund levy |
| Imports, exports | Goods cleared under the petrol and diesel tariff lines, calendar year, litres | The 2021 energy balance's own trade lines |
| Production | Refinery and synthetic fuel output of the product, calendar year, kilolitres in the file | Operators' reports (all products, Sasol's year to June) |
| Supply less sales | Production + imports - exports - sales | Energy balance statistical difference |

Periods are reconciled: every line is a calendar year in litres. Two
differences in definition are identified and not explained:

1. **The 2021 energy balance uses higher imports than customs.** Petrol
   5.42 bn litres against 4.01; diesel 11.22 against 9.76. Its own
   diesel statistical difference is 2.10 bn litres of supply above
   consumption.
2. **Energy balance final consumption is above recorded sales** in 2021:
   petrol 9.84 against 9.30, diesel 13.41 against 12.95.

The 2019 and 2020 energy balances repeat the previous year's trade figures, so
their trade lines are not used; their production lines are.

## Unresolved, by owner

| Gap | Owner | What would close it |
|---|---|---|
| Production for 2022 onward | Nigel to coordinate | A 2022 or later energy balance from the department, or output by product from the refiners (DR08) |
| Sales for 2024 and 2025 | Nigel to coordinate | Department publication |
| Stock change by product | Nigel to coordinate | Industry stock returns from the department; none is published |
| 2021 energy balance imports above customs | Manish | The department's working for the 2021 balance |
| Trade before 2014 | Manish | Customs is in kilograms before 2014; a density by tariff line would convert it |

## Not used, and why

| Source | What it has | Why it is not used |
|---|---|---|
| FIASA annual reports | Sales and trade to 2025 | Not a neutral source; instruction of 7 and 8 October |
| JODI oil database | Refinery output, stocks, demand to 2024 | Instruction of 8 October. For the record: diesel output is within 4% of the energy balance in 2017-2021, petrol is 12-24% above it, its imports are half of customs, and every entry carries JODI's lowest assessment code |
| Operators' reports (Sasol, Glencore) | Output of all products together | No split by product; fiscal years |

## Checks

- `python -m pytest -q`: 213 passed, 1 skipped.
- `tests/test_build_fuel_balance.py`: only the department and customs are ever
  selected; every selected figure names its source and file; no production or
  supply-less-sales figure after 2021; the committed file equals a fresh build.
- `tests/test_build_demand_baseline_workbook.py`: every row on the added
  sheets has a source.
- The fifteen energy balance files re-downloaded and matched by checksum.
- No model input read by the engine changed; model results are unchanged.
