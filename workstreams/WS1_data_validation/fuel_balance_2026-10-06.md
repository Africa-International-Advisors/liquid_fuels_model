# Petrol and diesel balance — 6 October 2026 (work package 4)

Investigated by Manish on `manish-branch`; for Nigel's review. Supports pack
pages 5, 6 and 8. Nothing under `assumptions/2026/` was changed.

Status: **partial.** Sales, imports and exports are matched by product and
year for 2009–2024. Actual production stops at 2021 and stock movements are
not available, so the balance is not closed after 2021. The 2024 diesel import
disagreement is explained. A diesel residual of roughly 3 bn litres a year
from 2022 is left explicitly open.

Table: `fuel_balance_petrol_diesel_2009_2025_2026-10-06.csv`, one row per
product and year, one column per source, litres.

## Sources lined up

| Flow | Source | Years | Note |
|---|---|---|---|
| Sales | Department national sales (`fuel_sales_department.csv`) | 2009–2023 | 2013 uses the corrected figure (flag log, section 2) |
| Sales | FIASA annual report 2025, p.47 | 2024 | See flag B |
| Imports, exports | FIASA annual reports (customs data), p.48 of the 2025 edition | 2009–2025 | Finished product; "kerosene" not used here |
| Imports, exports | Department Energy Trade Report 2024, printed pp.12–15 (customs data) | 2023–2024 | Rounded narrative figures |
| Production, final consumption | Department energy balances | 2009–2021 | No balance published after 2021 |
| Stock change | — | — | Not in the extract; not found elsewhere |

Implied production is sales minus imports plus exports. Where the energy
balance reports production, the two can be compared.

## Result, billion litres

| Year | Petrol sales | Imports | Exports | Implied production | Reported production | Diesel sales | Imports | Exports | Implied production | Reported production |
|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | 11.17 | 2.11 | 1.08 | 10.14 | 9.43 | 12.15 | 6.04 | 1.78 | 7.90 | 7.92 |
| 2018 | 11.14 | 2.19 | 1.32 | 10.27 | 9.97 | 12.54 | 6.10 | 1.84 | 8.27 | 8.43 |
| 2019 | 10.77 | 1.48 | 1.18 | 10.48 | 10.42 | 12.91 | 5.86 | 1.79 | 8.84 | 9.08 |
| 2020 | 8.76 | 1.72 | 1.16 | 8.20 | 7.90 | 11.69 | 6.82 | 0.91 | 5.79 | 6.45 |
| 2021 | 9.30 | 4.01 | 1.05 | 6.35 | 6.35 | 12.95 | 9.57 | 0.90 | 4.27 | 5.31 |
| 2022 | 9.18 | 5.46 | 0.79 | 4.52 | — | 12.72 | 11.91 | 0.70 | 1.50 | — |
| 2023 | 9.04 | 4.48 | 1.02 | 5.57 | — | 12.91 | 12.79 | 0.94 | 1.05 | — |
| 2024 | 9.03 | 4.00 | 0.94 | 5.97 | — | 11.73 | 10.80 | 0.82 | 1.76 | — |

2024 diesel imports use the trade report figure (flag A). Earlier years are in
the CSV.

**Petrol balances.** For 2013–2021 implied production is within 0.8 bn litres
of reported production every year and within 0.3 bn in five of the last six.
The implied 2022–2024 figures (4.5, 5.6, 6.0 bn litres) are a usable indication
of domestic petrol output, pending actual production data.

**Diesel balances to 2019, then stops balancing.** Implied and reported
production agree within 0.25 bn litres for 2017–2019. The gap is 0.7 in 2020
and 1.0 in 2021. For 2022–2024 implied diesel production is only 1.1–1.8 bn
litres while implied petrol production is 4.5–6.0. Over 2017–2019 the plants
made 0.84–0.87 litres of diesel per litre of petrol. If anything like that
ratio still held, diesel output would be about 3.8, 4.7 and 5.1 bn litres,
leaving roughly 2.3, 3.6 and 3.3 bn litres of diesel supply a year that is
imported but appears in neither recorded sales nor recorded exports. That ratio
is an assumption: the surviving plants (Natref, Secunda, Astron) need not have
the old fleet's product mix.

Candidate explanations for the diesel residual, none yet evidenced:

- sales by importers and wholesalers who do not report to the department
  (recorded 2024 diesel sales fell 9% while imports stayed high);
- product moving to neighbouring countries without appearing as exports;
- diesel supplied directly to power generation or to ships;
- stock build;
- a real change in plant product mix.

## Flags

**A. 2024 diesel imports: 10.8 bn litres is the supported figure.** FIASA
prints 14 793 ML; the department's trade report says 10.8 bn litres. Evidence:

- The trade report's own shares only work with 10.8: diesel 10.8 of a 16.33
  total (petrol 4.0, jet 0.718, LPG 0.589, paraffin 0.219) is 66%, as printed.
  With 14.8 the share would be 73%.
- The same check works for 2023 (12.8 of 19.13 = 67%), and for 2023 FIASA
  agrees with the trade report (12 794 against 12.8).
- With 14.8, implied diesel production in 2024 is negative (−2.2 bn litres).
- FIASA's 2024 row is also out for LPG (2 771 against 589 in the trade report).
- The last three digits match: 10 793 would round to the report's 10.8. A
  one-digit misprint (14 793 for 10 793) is the simplest reading. This is an
  inference; FIASA has not confirmed it.

Proposed: use 10.8 bn litres for 2024 diesel imports, keep FIASA's figure
recorded as a suspected misprint, and ask FIASA. FIASA's 2025 figure
(12 249 ML) has no second source yet.

**B. FIASA's 2024 sales appear in two versions.** The 2024 edition (p.32) gives
2024 petrol 8 763 and diesel 11 807 ML. The 2025 edition (p.47) gives 9 029 and
11 734 for 2024, and prints the identical row again for 2025 (all six
products). One of the two rows in the 2025 edition is a copy. The repo holds
9 029 and 11 734 as 2024. Until the department publishes 2024, national 2024
sales are uncertain by about 0.27 bn litres for petrol and 0.07 for diesel.
This carries into the 2024 provincial estimate in package 3.

**C. The 2019 and 2020 energy balances repeat the previous year's trade.**
Balance imports for 2019 (petrol 2.20, diesel 6.11) equal customs imports for
2018; for 2020 (1.48, 5.86) they equal 2019. Exports show the same pattern.
The 2019 and 2020 balances should not be used for trade.

**D. Production evidence ends in 2021.** The department's balance page lists
no balance after 2021. Refinery capacity (pack p8) is nameplate, not output.

## Not done

| Item | Owner | Next action |
|---|---|---|
| Customs data by tariff line (petrol, diesel; volume and partner country) | Nigel | Obtained (see the SARS section); review and decide on registering the three extracts in the vintage |
| Actual production 2022 onward | Manish | Sasol and Natref totals obtained (see follow-up); product split and Astron still missing; ask the department whether a 2022 or 2023 balance exists |
| Stock movements | Manish / Nigel | None published found; ask the department or FIASA |
| Diesel residual from 2022 | Manish, Henry review | Test each candidate explanation; exports to neighbouring countries by partner from SARS is the first check |
| FIASA: 2024 diesel misprint (confirmed by customs), duplicated 2025 sales row, and the 2018 difference | Nigel | Query FIASA |
| Imports by entry port | Nigel | Customs office now gives a public proxy (see the SARS section); terminal-level data still needs client or port access |

## Follow-up, later on 6 October

**Operator output supports the diesel residual.** Sasol reports Secunda and
Natref refined output of about 9.0 bn litres in each of the years to June 2023
and 2024 (all products; table in `driver_evidence_2026-10-06.md`). Implied
petrol plus diesel production for calendar 2023 and 2024 is 6.6 and 7.7 bn
litres. Natref's white product yield was 87–89% in the last years it was
reported (FY2020–FY2022), so petrol, diesel and jet make up most of that
9.0 bn, and Astron's output comes on top from 2023. Domestic petrol and diesel
output is therefore likely to be higher than the implied figure, which is the
same direction as the residual: more product is supplied than recorded sales
and exports account for. The size cannot be fixed without a product split and
Astron's output.

## SARS customs data, obtained 6 October

The portal download now works by script (`python -m lfm.scripts.fetch_sars`).
The step that had been missing: the form refuses a download unless every
country is ticked, even when the selection is by tariff line; it also allows at
most two years at a time. The page then serves the workbook from a second
address in the same session. 34 workbooks (imports and exports, each year 2010
to August 2026; 31,982 lines) are in `external/data/raw/sars/`, uncommitted.

Candidate extracts, kept beside this note and not in the vintage:
`fuel_trade_sars_candidate_2026-10-06.csv` (by product and year),
`fuel_trade_sars_by_office_candidate_2026-10-06.csv` (by customs office and
transport mode) and `fuel_trade_sars_by_partner_candidate_2026-10-06.csv` (by
country of origin or destination).

Tariff lines used: petrol 27101102, 27101202; diesel 27101130, 27101230,
27101930; biodiesel blends 27102000; jet 27101107, 27101207, 27101907;
paraffin 27101115, 27101126, 27101215, 27101226, 27101915, 27101926; fuel oil
27101135, 27101235, 27101935.

**Flag A is settled: 2024 diesel imports were 10.793 bn litres.** SARS minus
FIASA, billion litres:

| Year | Diesel imports | Petrol imports | Diesel exports | Petrol exports |
|---|---|---|---|---|
| 2014–2017 | within 0.005 | within 0.001 | within 0.012 | within 0.006 |
| 2018 | −0.982 | −0.365 | −0.256 | −0.186 |
| 2019 | −0.268 | 0.000 | −0.045 | −0.004 |
| 2020 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2021 | +0.194 | 0.000 | −0.002 | −0.002 |
| 2022 | +0.040 | 0.000 | +0.191 | +0.062 |
| 2023 | +0.076 | 0.000 | −0.046 | −0.024 |
| 2024 | **−4.000** | +0.001 | −0.025 | −0.019 |
| 2025 | 0.000 | 0.000 | −0.001 | 0.000 |

FIASA's table is the customs data, to the million litres in most years. Its
2024 diesel figure is exactly 4,000 million litres too high: 14 793 printed
for 10 793. The trade report's 10.8 bn is right. New flag: for 2018 SARS now
shows about 1.0 bn litres less diesel and 0.4 bn less petrol imported than
FIASA printed, and smaller differences in 2019 and 2021–2023; these look like
later customs revisions but have not been explained.

**Units.** SARS records these lines in kilograms to 2012 and litres from 2014;
2013 has both (litres in two months only). The litre series is therefore
usable from 2014. Nothing has been converted.

**Where imports enter**, petrol plus diesel, billion litres, by customs office:

| Office | 2024 | Share | 2025 | Share |
|---|---|---|---|---|
| Durban | 11.84 | 80.0% | 13.16 | 78.8% |
| Cape Town | 1.09 | 7.4% | 1.52 | 9.1% |
| Mossel Bay | 0.62 | 4.2% | 0.52 | 3.1% |
| East London | 0.53 | 3.6% | 0.43 | 2.6% |
| Richards Bay | 0.39 | 2.6% | 0.66 | 3.9% |
| Komatipoort (road, from Mozambique) | 0.19 | 1.3% | 0.09 | 0.5% |
| Port Elizabeth | 0.14 | 1.0% | 0.32 | 1.9% |

In 2024 Durban cleared 8.03 bn litres of diesel and 3.80 bn of petrol; 98% of
diesel imports arrived by sea. The customs office is where goods were cleared,
which is the nearest public indication of entry port but is not a terminal or
berth record.

**Where exports go**, billion litres:

| | Botswana | Eswatini | Lesotho | Namibia | Other |
|---|---|---|---|---|---|
| Diesel 2023 | 0.448 | 0.138 | 0.127 | 0.000 | 0.177 |
| Diesel 2024 | 0.281 | 0.151 | 0.131 | 0.004 | 0.229 |
| Petrol 2023 | 0.598 | 0.151 | 0.122 | 0.000 | 0.123 |
| Petrol 2024 | 0.509 | 0.152 | 0.127 | 0.000 | 0.132 |

**The diesel residual is not explained by recorded exports.** Customs confirms
both the import figure and the export figure used in the balance. Recorded
diesel exports to all destinations are 0.8–0.9 bn litres a year, and Botswana's
recorded purchases fell from 0.45 to 0.28 bn litres between 2023 and 2024. The
roughly 3 bn litres a year therefore sits in sales not reported to the
department, unrecorded cross-border movement, direct supply to power or
shipping, or stocks.
