# DR01 National product balance: evidence and reconciliation, 8 October 2026

For Nigel's review. Answers request DR01 in
`output/delivered/investment_bridge_2026_10_08/data_request.csv` and milestone
M1 in `sa_review_milestone_2026_10_08.md`: petrol and diesel production,
imports, exports, stock changes and statistical differences, with definitions
reconciled and no residual labelled as production.

Status: **reported production now runs to 2024; stock change is still not
available.** The balance is therefore complete on four of five lines, and the
fifth (stock change) sits inside an explicit "supply less sales" line.

Files:

- Balance: `fuel_balance_petrol_diesel_2009_2025_2026-10-06.csv`, one row per
  product and year, one column per source, litres. Rebuilt by
  `python -m lfm.scripts.build_fuel_balance --vintage 2026`.
- Evidence table: `dr01_national_balance_evidence_2026-10-08.csv`, one row per
  line of the balance: source, period, unit, status, owner, unresolved gap.
- New input: `assumptions/2026/timeseries/oil_balance_jodi.csv`, built by
  `python -m lfm.scripts.stage_jodi --vintage 2026`; originals in
  `external/data/raw/jodi/`.
- Workbook: History sheet, sections 3 and 4, carry the same rows.

Earlier work this builds on: `fuel_balance_2026-10-06.md` (trade source,
FIASA differences, the diesel hypothesis and its sensitivities).

## What is new

South Africa reports refinery output by product and month to the JODI oil
database. On 6 October I set JODI aside because its imports and demand are far
from customs and recorded sales. That was too broad. Tested line by line
against the department's own energy balances for 2017 to 2021, its diesel
refinery output agrees within 4% in every year. JODI therefore gives a reported
production figure by product for 2022, 2023 and 2024, the years after the
department stopped publishing balances.

Diesel production, billion litres:

| Year | Energy balance | JODI | JODI / balance |
|---|---|---|---|
| 2017 | 7.92 | 8.06 | 1.02 |
| 2018 | 8.43 | 8.14 | 0.97 |
| 2019 | 9.08 | 8.89 | 0.98 |
| 2020 | 6.45 | 6.36 | 0.99 |
| 2021 | 5.31 | 5.30 | 1.00 |

Petrol production, billion litres:

| Year | Energy balance | JODI | JODI / balance |
|---|---|---|---|
| 2017 | 9.43 | 11.73 | 1.24 |
| 2018 | 9.97 | 11.31 | 1.13 |
| 2019 | 10.42 | 12.11 | 1.16 |
| 2020 | 7.89 | 8.93 | 1.13 |
| 2021 | 6.35 | 7.12 | 1.12 |

Petrol does not agree: JODI is 12% to 24% above the energy balance. The cause
is not established. Using JODI for petrol from 2022 therefore introduces a
break in level at 2022.

## The balance, billion litres

Supply is production plus imports less exports. **Supply less sales** is what
is left: the stock change and the statistical difference together. It is not
production, and nothing is adjusted with it.

Diesel:

| Year | Production | Source | Imports | Exports | Supply | Sales | Supply less sales |
|---|---|---|---|---|---|---|---|
| 2017 | 7.92 | energy balance | 6.04 | 1.78 | 12.18 | 12.15 | +0.03 |
| 2018 | 8.43 | energy balance | 5.12 | 1.58 | 11.97 | 12.54 | -0.57 |
| 2019 | 9.08 | energy balance | 5.59 | 1.74 | 12.93 | 12.91 | +0.02 |
| 2020 | 6.45 | energy balance | 6.81 | 0.91 | 12.35 | 11.69 | +0.66 |
| 2021 | 5.31 | energy balance | 9.76 | 0.89 | 14.18 | 12.95 | +1.24 |
| 2022 | 4.11 | JODI | 11.95 | 0.89 | 15.18 | 12.72 | +2.46 |
| 2023 | 5.19 | JODI | 12.87 | 0.89 | 17.17 | 12.91 | +4.26 |
| 2024 | 3.89 | JODI | 10.79 | 0.80 | 13.89 | 11.73 (FIASA) | +2.16 |
| 2025 | — | — | 12.25 | 0.75 | — | — | — |

Petrol:

| Year | Production | Source | Imports | Exports | Supply | Sales | Supply less sales |
|---|---|---|---|---|---|---|---|
| 2017 | 9.43 | energy balance | 2.11 | 1.08 | 10.47 | 11.17 | -0.70 |
| 2018 | 9.97 | energy balance | 1.83 | 1.14 | 10.67 | 11.14 | -0.47 |
| 2019 | 10.42 | energy balance | 1.48 | 1.17 | 10.73 | 10.77 | -0.05 |
| 2020 | 7.89 | energy balance | 1.72 | 1.15 | 8.46 | 8.76 | -0.30 |
| 2021 | 6.35 | energy balance | 4.01 | 1.05 | 9.31 | 9.30 | +0.01 |
| 2022 | 6.64 | JODI | 5.46 | 0.85 | 11.24 | 9.18 | +2.05 |
| 2023 | 8.52 | JODI | 4.48 | 0.99 | 12.01 | 9.04 | +2.97 |
| 2024 | 7.34 | JODI | 4.00 | 0.92 | 10.42 | 9.03 (FIASA) | +1.39 |
| 2025 | — | — | 4.45 | 0.80 | — | — | — |

Reading, diesel: reported supply and recorded sales agree within 0.7 bn litres
in every year from 2017 to 2020. From 2021 reported supply is above recorded
sales, by 1.2, 2.5, 4.3 and 2.2 bn litres. This is the first evidence on a
matched basis (calendar years, one product, production reported) for the
hypothesis that recorded diesel sales fall short of supply. It remains a
hypothesis: the stock change is not known, and the production figures for
2022 to 2024 carry JODI's lowest assessment code.

Reading, petrol: the balance closes within 0.7 bn litres to 2021. The 2022 to
2024 differences (2.1, 3.0 and 1.4 bn litres) are partly the break in level
between the two production sources, which accounts for 0.8 to 1.0 bn litres a year. If JODI petrol is scaled by its average
ratio to the energy balance in 2018 to 2021 (0.880), production is
5.84, 7.50 and 6.46 bn litres and supply less sales is
+1.25, +1.95 and +0.51. That scaling is an inference, shown here only;
it is not in the balance file.

## The 2021 to 2022 bridge

2021 is the last year with a published energy balance; 2022 is the first that
rests on JODI for production.

Diesel, billion litres:

| Line | 2021 | 2022 | Change | 2021 source | 2022 source |
|---|---|---|---|---|---|
| Production | 5.31 | 4.11 | -1.20 | Energy balance | JODI |
| Imports | 9.76 | 11.95 | +2.19 | SARS customs | SARS customs |
| Exports | 0.89 | 0.89 | -0.00 | SARS customs | SARS customs |
| Sales | 12.95 | 12.72 | -0.23 | Department | Department |
| Supply less sales | 1.24 | 2.46 | +1.22 | Computed | Computed |

Petrol, billion litres:

| Line | 2021 | 2022 | Change | 2021 source | 2022 source |
|---|---|---|---|---|---|
| Production | 6.35 | 6.64 | +0.29 | Energy balance | JODI |
| Imports | 4.01 | 5.46 | +1.45 | SARS customs | SARS customs |
| Exports | 1.05 | 0.85 | -0.20 | SARS customs | SARS customs |
| Sales | 9.30 | 9.18 | -0.12 | Department | Department |
| Supply less sales | 0.01 | 2.05 | +2.05 | Computed | Computed |

Diesel: production fell 1.2 bn litres (SAPREF stopped refining in 2022),
imports rose 2.2, and recorded sales fell 0.2. Supply rose by 1.0 bn litres
while recorded sales did not, so the difference doubled.

Petrol: the production change is not a like-for-like figure because the source
changes. On JODI's own basis petrol output fell from 7.12 to 6.64 bn litres
(-0.48).

## Definitions and where the sources differ

| Line | Selected | Definition | Differs from |
|---|---|---|---|
| Production | Energy balance to 2021; JODI 2022-2024 | Refinery and synthetic fuel plant output of the product, calendar year | Operators' reports (all products, Sasol's year to June) |
| Imports, exports | SARS customs from 2014 | Goods cleared under the petrol and diesel tariff lines, litres | FIASA (2018, 2019); the 2021 energy balance; JODI |
| Sales | Department national file to 2023 | Volumes returned by licensed wholesalers | FIASA 2024 (two editions); Road Accident Fund levy; energy balance final consumption |
| Stock change | None | — | JODI reports one but it is not usable |
| Supply less sales | Computed | Production + imports - exports - sales | Energy balance statistical difference |

Three differences in definition or revision that are not reconciled:

1. **The 2021 energy balance uses higher imports than customs.** It shows
   petrol imports of 5.42 bn litres against 4.01 in customs, and diesel 11.22
   against 9.76. Its exports are also higher (1.42 and 1.03 against 1.05 and
   0.89). Its own diesel statistical difference is 2.10 bn litres of supply
   above consumption. The department's balance and customs therefore both show
   diesel supply above use in 2021, by different amounts.
2. **Energy balance final consumption is above recorded sales** in 2021:
   petrol 9.84 against 9.30, diesel 13.41 against 12.95.
3. **JODI's total refinery output against operators' reports.** For 2024 JODI
   gives 13.6 bn litres for all products, against about 14.0 for Secunda,
   Natref and Astron together (after the conversions set out in
   `fuel_balance_2026-10-06.md`). For 2023 JODI gives 16.6 against about 13.1.
   The 2023 JODI figure is therefore about 3.5 bn litres above what the three
   operating plants report, and should be treated with more caution than 2022
   or 2024.

## Why JODI's other lines are not used

| JODI line | 2023 diesel, bn litres | Comparison | Decision |
|---|---|---|---|
| Imports | 6.80 | Customs 12.87 | Not used |
| Exports | 0.46 | Customs 0.89 | Not used |
| Demand | 13.85 | Department sales 12.91 | Not used; noted as a second figure above recorded sales |
| Stock change | +0.01 | Closing stock fell 0.08 | Not used |
| Statistical difference | -2.34 | — | Not used |

Stock change and closing stock do not agree with each other in any year
checked (2021 diesel: stock change +0.59 bn litres; closing stock rose 0.38).

## Unresolved, by owner

| Gap | Owner | What would close it |
|---|---|---|
| Stock change by product | Nigel to coordinate; Manish to reconcile | Industry stock returns from the department or FIASA; none is published |
| Whether to accept JODI refinery output as the production record for 2022-2024 | Nigel | Decision; a 2022 or later energy balance from the department would replace it |
| Petrol: why JODI is 12-24% above the energy balance | Manish | The department's JODI questionnaire definition; not found in public metadata |
| JODI total output for 2023 against operators | Manish | Product split from Sasol or Astron; part of DR08 |
| 2021 energy balance imports above customs | Manish | The department's working for the 2021 balance |
| 2024 sales source; no 2025 sales | Nigel | Department publication; decision D01 |

## Checks

- `tests/test_jodi_source.py`: units, partial years, December stock.
- `tests/test_build_fuel_balance.py`: production is the energy balance while
  published and JODI after; a part-year is never selected; the committed file
  equals a fresh build; JODI diesel is within 4% of the energy balance for
  2017-2021.
- No model input read by the engine changed; model results are unchanged.
- `python -m pytest -q`: 212 passed, 1 skipped (four tests added). The message on commit `b25661d`
  says 215 and five; that is wrong.
- Workbook History rows for 2017-2025 read back after recalculation in Excel: production used and the
  unexplained line equal the balance file in every year (the workbook shows the opposite sign, as labelled).
