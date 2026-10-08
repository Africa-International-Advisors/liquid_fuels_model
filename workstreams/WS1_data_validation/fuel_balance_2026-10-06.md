# Petrol and diesel balance — 6 October 2026 (work package 4)

Investigated by Manish on `manish-branch`; for Nigel's review. Supports the
national accounting page of the Week 1 Convergence pack. Revised 7 October
after Nigel's branch review (`manish_branch_review_2026-10-06.md`, findings 1
and 2): the table is rebuilt on customs trade, and the residual is described
as a balancing requirement, not as production.

**Updated 8 October:** reported production now runs to 2024 from JODI refinery
output, and the statement below that JODI is not usable is corrected for that
one line. See `dr01_national_balance_2026-10-08.md`. The tables in this note
are unchanged.

Status: **partial.** Sales, imports and exports are matched by product and
calendar year. Production after 2021, stock changes and what the sales series
covers are **unresolved**, so the balance is not closed.

Table: `fuel_balance_petrol_diesel_2009_2025_2026-10-06.csv`, one row per
product and year, one column per source, litres. It is built from the
registered inputs only:

    python -m lfm.scripts.build_fuel_balance --vintage 2026

`tests/test_build_fuel_balance.py` checks that the committed file equals a
fresh build and that selected imports and exports equal the customs extract
for every product and year from 2014.

## Sources lined up

| Flow | Selected source | Years | Kept for comparison (own columns) |
|---|---|---|---|
| Sales | Department national sales (`fuel_sales_department.csv`), complete years | 2009–2023 | FIASA annual reports |
| Sales | FIASA annual report, 2025 edition, p.47 | 2024 | Unverified; see flag B |
| Imports, exports | FIASA annual reports | 2009–2013 | Energy balances |
| Imports, exports | SARS customs (`fuel_trade_sars.csv`), complete years in litres | 2014–2025 | FIASA; department trade report (2023–2024, rounded); energy balances |
| Production, final consumption | Department energy balances | 2009–2021 | None published after 2021 |
| Stock change | — | — | Not available |

Customs records before 2014 are in kilograms or mixed units and are not used.
All periods are calendar years. The columns `sales_used_source`,
`trade_used_source`, `sars_months_reported` and the two FIASA edition columns
record what was selected for each row.

## Result, billion litres

**Sales less net imports** is sales minus imports plus exports. It is the
volume that domestic production, stock changes and differences in what
"sales" covers would together have to supply. It is a balancing requirement,
not a measurement of production.

| Year | Petrol sales | Imports | Exports | Sales less net imports | Balance-reported production | Diesel sales | Imports | Exports | Sales less net imports | Balance-reported production |
|---|---|---|---|---|---|---|---|---|---|---|
| 2014 | 10.89 | 1.15 | 0.99 | 10.73 | 10.83 | 12.62 | 4.99 | 1.49 | 9.12 | 9.59 |
| 2015 | 11.48 | 1.87 | 1.09 | 10.69 | 10.46 | 13.52 | 6.45 | 1.61 | 8.68 | 9.37 |
| 2016 | 11.46 | 1.40 | 1.16 | 11.22 | 10.39 | 12.08 | 4.42 | 1.89 | 9.54 | 9.01 |
| 2017 | 11.17 | 2.11 | 1.08 | 10.14 | 9.43 | 12.15 | 6.04 | 1.78 | 7.89 | 7.92 |
| 2018 | 11.14 | 1.83 | 1.14 | 10.45 | 9.97 | 12.54 | 5.12 | 1.58 | 9.00 | 8.43 |
| 2019 | 10.77 | 1.48 | 1.17 | 10.47 | 10.42 | 12.91 | 5.59 | 1.74 | 9.06 | 9.08 |
| 2020 | 8.76 | 1.72 | 1.15 | 8.20 | 7.89 | 11.69 | 6.81 | 0.91 | 5.79 | 6.45 |
| 2021 | 9.30 | 4.01 | 1.05 | 6.35 | 6.35 | 12.95 | 9.76 | 0.89 | 4.08 | 5.31 |
| 2022 | 9.18 | 5.46 | 0.85 | 4.58 | — | 12.72 | 11.95 | 0.89 | 1.65 | — |
| 2023 | 9.04 | 4.48 | 0.99 | 5.55 | — | 12.91 | 12.87 | 0.89 | 0.93 | — |
| 2024 | 9.03 | 4.00 | 0.92 | 5.95 | — | 11.73 | 10.79 | 0.80 | 1.74 | — |
| 2025 | — | 4.45 | 0.80 | — | — | — | 12.25 | 0.75 | — | — |

Earlier years are in the CSV. For 2024, both products together: sales 20.76,
net imports 13.08, sales less net imports 7.69 bn litres.

What changed from the 6 October table: imports and exports from 2014 are now
customs figures throughout, where the earlier table used FIASA and, for 2024
diesel imports, the department's rounded 10.8. Apart from FIASA's 2024 diesel
import misprint (flag A), customs and FIASA differ by 0.05 bn litres or more in
these cases; every other figure from 2014 is closer than that. The causes are
not known.

| Year | Flow | Customs | FIASA | Difference |
|---|---|---|---|---|
| 2018 | petrol imports | 1.83 | 2.19 | -0.37 |
| 2018 | petrol exports | 1.14 | 1.32 | -0.19 |
| 2022 | petrol exports | 0.85 | 0.79 | +0.06 |
| 2018 | diesel imports | 5.12 | 6.11 | -0.98 |
| 2018 | diesel exports | 1.58 | 1.84 | -0.26 |
| 2019 | diesel imports | 5.59 | 5.86 | -0.27 |
| 2021 | diesel imports | 9.76 | 9.57 | +0.19 |
| 2022 | diesel exports | 0.89 | 0.70 | +0.19 |
| 2023 | diesel imports | 12.87 | 12.79 | +0.08 |

**Against balance-reported production, 2014–2021.** The largest difference is
+0.83 bn litres for petrol (2016) and -1.24 for diesel (2021). Flag C
applies: the 2019 and 2020 energy balances repeat the previous year's trade.

**2022–2024.** No production is reported. Sales less net imports is
4.58, 5.55 and 5.95 bn litres for petrol and 1.65, 0.93 and 1.74 for diesel. These
are not estimates of output and are not used as such.

**Hypothesis to test, not a finding.** The diesel figure is low next to
petrol, and comparisons in the sensitivity section point to 3 to 4 bn litres
a year of diesel supply above recorded sales. That is one reading. It is not
added to demand anywhere. Explanations to test, none yet evidenced:

- stock changes (no usable stock series);
- product scope: the surviving plants' petrol-to-diesel mix is not published;
- coverage of the sales series (importers and wholesalers not reporting);
- product moving to neighbouring countries without an export record;
- diesel supplied directly to power generation or ships;
- period mismatch between sources.

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

Since 7 October the balance uses the customs figure, 10.793 bn litres; FIASA's
figure stays recorded as a suspected misprint. FIASA's 2025 figure
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
| Customs data by tariff line (petrol, diesel; volume and partner country) | Nigel | Obtained and registered on manish-branch (see review outcomes); confirm |
| Actual production 2022 onward | Manish | Sasol, Natref and Astron totals obtained (see follow-up and the all-product check); product split still missing; ask the department whether a 2022 or 2023 balance exists |
| Stock movements | Manish / Nigel | JODI carries a stock series of low reliability (see the fuel levy section); ask the department or FIASA |
| Diesel residual from 2022 | Manish, Henry review | Test each candidate explanation; exports to neighbouring countries by partner from SARS is the first check |
| Imports by entry port | Nigel | Customs office now gives a public proxy (see the SARS section); terminal-level data still needs client or port access |

## SARS customs data, obtained 6 October

The portal download now works by script (`python -m lfm.scripts.fetch_sars`).
The step that had been missing: the form refuses a download unless every
country is ticked, even when the selection is by tariff line; it also allows at
most two years at a time. The page then serves the workbook from a second
address in the same session. 34 workbooks (imports and exports, each year 2010
to August 2026; 31,982 lines) are in `external/data/raw/sars/`, uncommitted.

Extracts, now in the vintage under `assumptions/2026/timeseries/`:
`fuel_trade_sars.csv` (by product and year), `fuel_trade_sars_by_office.csv`
(by customs office and transport mode) and `fuel_trade_sars_by_partner.csv`
(by country of origin or destination).

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
shipping, or stocks, or reflects plant product mix. This is a hypothesis until
production and stocks are matched.

## The 2018 and 2019 differences between customs and FIASA, traced 7 October

Status: **partly traced.** The customs download is complete and internally
consistent; the higher FIASA figure is an older reading that two publications
share. Which entries changed cannot be shown without a customs extract from
that time.

What was checked in the customs downloads kept on this branch
(`external/data/raw/sars/`, 2017–2020):

- **No missing month.** All twelve months of 2018 and 2019 are present for
  both products and both flows, and no month is near zero.
- **No fuel under another tariff line.** The 2018 files contain only the lines
  already counted; nothing of the missing size sits under an unmapped code.
- **No unit problem.** Every 2018 and 2019 petrol and diesel line is in litres.
- **No window that reproduces FIASA.** Adding neighbouring months (a 13- or
  14-month year) does not give FIASA's 2018 figures for all four flows.

Where each 2018 figure appears, million litres:

| Source | Diesel imports | Petrol imports | Diesel exports | Petrol exports |
|---|---|---|---|---|
| SARS customs, downloaded October 2026 | 5,123 | 1,830 | 1,582 | 1,135 |
| FIASA annual report (2025 edition) | 6,105 | 2,195 | 1,838 | 1,321 |
| Department energy balance, 2018 | 6,105 | 2,195 | 1,838 | 1,321 |

FIASA and the department's balance carry the same four figures to the million
litres, so they are one reading, not two confirmations. South Africa's own
submission to UN Comtrade agrees with today's customs data, not with that
reading: for all lines under heading 2710.12 it reports 2018 imports of 8,020
million litres and exports of 5,295, against 7,371 and 5,133 for the six fuel
lines in the SARS download. The differences (649 and 162) are in line with
2017 (681 and 230) and 2019 (785 and 172), which are the other products under
that heading. On FIASA's figures the 2018 differences would be negative.
Comtrade files: `external/data/raw/comtrade/`.

For 2019 only diesel imports differ materially (customs 5,590, FIASA 5,858).
December 2019 is the lowest month in the customs series (295 against a monthly
average of 481 for January to November), which would fit a later correction to
that month, but this is not shown.

Reading: today's customs record and Comtrade agree, and the higher 2018
figure is an earlier reading repeated in two publications. The likeliest cause
is a later revision of customs entries, but no dated extract is held to prove
it. Customs stays the selected source. The effect on 2018 is that sales less
net imports is 9.00 bn litres for diesel and 10.45 for petrol, against 8.27
and 10.27 on FIASA's figures.

To settle it: a customs extract for 2018 as published in 2019, or SARS's own
statement of revisions. Neither has been requested.

## Neighbours' own customs records, 6 October

A test of whether the diesel residual leaves by land without being recorded as
an export: what neighbouring countries report importing from South Africa,
against what SARS records as exported to them. Source: UN Comtrade public
API, headings 2710.12 and 2710.19, litres; responses kept in
`runs/manish_candidate_20261006/raw/comtrade/` (untracked). All fuel lines,
billion litres:

| | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|
| Botswana: its imports / SARS exports | 1.13 / 1.12 | 1.06 / 1.07 | 1.02 / 1.07 | 0.63 / 0.82 |
| Lesotho | 0.23 / 0.30 | 0.21 / 0.26 | 0.29 / 0.27 | 0.25 / 0.28 |
| Eswatini | 0.18 / 0.23 | 0.15 / 0.19 | 0.22 / 0.29 | not reported / 0.31 |
| Zimbabwe | 0.10 / 0.07 | 0.06 / 0.03 | 0.10 / 0.09 | 0.09 / 0.06 |
| Zambia | 0.05 / 0.00 | 0.05 / 0.01 | 0.10 / 0.02 | 0.08 / 0.01 |
| DR Congo | 0.03 / 0.07 | 0.20 / 0.06 | 0.21 / 0.05 | 0.07 / 0.05 |
| Namibia | 0.08 / 0.10 | 0.02 / 0.02 | 0.02 / 0.00 | 0.02 / 0.01 |
| Nine countries together | 1.80 / 1.87 | 1.75 / 1.64 | 2.02 / 1.79 | 1.17 / 1.60 |

The two sides agree to within about 0.2 bn litres a year in total (2024 lacks
Eswatini). The neighbours do not report receiving more South African fuel than
SARS records sending, so recorded trade on either side of the border does not
account for a residual of 3 to 4 bn litres. What remains is sales not reported
to the department, movement that neither side records, direct supply to power
or ships, or stocks.

A second reading: Botswana's recorded imports from South Africa fell from
1.02 bn litres in 2023 to 0.63 bn in 2024, and SARS shows the same direction.
Botswana is sourcing less of its fuel through South Africa.

Limits: Mozambique's 2021 quantity in Comtrade is implausible against its
value and was left out; Malawi has no matching SARS rows; the comparison is
for all fuel lines together because neighbours' data is at six-digit level.

## Sensitivities: indicative comparisons, not matched accounting

Nothing in this section is part of the balance. Each comparison mixes periods,
product scope or units, as stated, and is kept as a lead to test. Reported
figures are given in their original units; conversions are assumptions.

### Diesel-to-petrol ratio

Over 2017–2019 the energy balances report 0.84 to 0.87 litres of diesel
produced per litre of petrol. Applying that to petrol's sales less net imports
would put diesel at 3.8, 4.7 and 5.0 bn litres for 2022–2024, which is 2.2, 3.7 and
3.3 bn above diesel's own figure. The ratio is an assumption: Natref, Secunda
and Astron need not have the old fleet's product mix, and petrol's figure is
itself a balancing requirement.

### Operator output for petrol and diesel

Sasol reports Secunda and
Natref refined output of about 9.0 bn litres in each of the years to June 2023
and 2024 (all products; table in `driver_evidence_2026-10-06.md`). Sales
less net imports for petrol plus diesel in calendar 2023 and 2024 is 6.5 and 7.7 bn
litres. Natref's white product yield was 87–89% in the last years it was
reported (FY2020–FY2022), so petrol, diesel and jet make up most of that
9.0 bn, and Astron's output comes on top from 2023. Domestic petrol and diesel
output may therefore be higher than sales less net imports. The periods (years
to June against calendar years) and the products (all refined products against
two fuels) do not match, so this is an indication only. The size cannot be fixed without a product split and
Astron's output.

### All refined products, 2023 and 2024, with Astron included

Astron's output is reported by Glencore (Annual Reports 2023–2025; detail in
`driver_evidence_2026-10-06.md`): about 4.0 bn litres in 2023 and 4.9 bn in
2024 after converting energy content at an assumed 36 MJ a litre. With Sasol's figures this gives a
supply check that does not depend on a product split. Petrol, diesel, jet,
paraffin and fuel oil together, billion litres:

| | 2023 | 2024 | Source |
|---|---|---|---|
| Recorded sales | 25.7 | 24.2 | Department (2023); FIASA 2025 edition (2024) |
| Imports | 20.2 | 17.2 | SARS |
| Exports | 3.1 | 3.6 | SARS |
| Production needed to balance | 8.7 | 10.6 | sales − imports + exports |
| Secunda | 4.75 | 4.6 | Sasol, years to June 2023 and 2024 |
| Natref, whole refinery | 4.3 | 4.5 | Sasol, scaled from its 63.64% share |
| Astron | about 4.0 | about 4.9 | Glencore, calendar years, converted from energy content |
| Reported output, three plants | about 13.1 | about 14.0 | |
| **Output above what the balance needs** | **about 4.4** | **about 3.3** | |

The three operators report roughly 4.4 bn litres (2023) and 3.3 bn litres
(2024) more refined product than recorded sales, imports and exports can
absorb. That is the same order as the diesel residual found product by
product, reached by a separate route, and it holds in both years.

Limits: the operator figures are all refined products, so they include
liquefied gas, bitumen and other products that are not in the five fuels
counted on the sales side (liquefied gas sales were 0.3 bn litres); Sasol's
year runs July to June; Astron's litres depend on the assumed energy content
(the gap is 4.2 to 4.6 bn for 2023 and 3.1 to 3.6 bn for 2024 across the plausible range); and ships' bunkers may
be supplied from this output without appearing in sales. Together these could
account for part or all of the gap; it has not been reconciled.

As reported by the operators, before any conversion
(`assumptions/2026/reference/refinery_output_operators.csv`):

| Plant | Period | Reported | Basis |
|---|---|---|---|
| Secunda | Year to 30 June 2023; 2024 | 29.9; 29.1 million barrels | Sasol; all refined products |
| Natref | Year to 30 June 2023; 2024 | 17.2; 17.8 million barrels | Sasol's 63.64% share only |
| Astron (Cape Town) | Calendar 2023; 2024 | 136,665; 166,204 billion Btu | Glencore; energy content of all refined products |

The litres in the table above come from these through three assumptions: 159
litres a barrel, scaling Natref from Sasol's share to the whole refinery, and
36 MJ a litre for Astron.

### Road Accident Fund levy: an independent count of litres, found 7 October

The Road Accident Fund levy is a fixed 218 cents on every litre of petrol and
diesel sold. The Fund's audited statements give gross levies before diesel
rebates (Annual Report 2024/25, note 16, p.183; reported figures in
`assumptions/2026/reference/fuel_levy_revenue_raf.csv`). Dividing by the rate:

| Year to 31 March | Gross levies, R million | Litres levied, bn | Recorded petrol and diesel sales, bn | Difference, bn |
|---|---|---|---|---|
| 2024 | 52,857 | 24.25 | 21.94 (calendar 2023, department) | 2.3 |
| 2025 | 53,245 | 24.42 | 20.76 (calendar 2024, FIASA 2025 edition) | 3.7 |

Two things follow, both as indications:

- **Level.** Litres levied are 2.3 to 3.7 bn above recorded sales, which is
  the same order as the other comparisons in this section.
- **Direction.** Litres levied rose 0.7% between the two years. The Fund says
  the volume of petrol and diesel consumed "saw a year-on-year increase"
  (p.64). FIASA's 2024 figures show a fall of 5.4% from 2023 (6.3% on its
  earlier edition). The two do not agree on whether 2024 fell.

Limits: fiscal years against calendar years; both fuels together; accrual
basis, while cash received fell from R48.6 bn to R47.4 bn and SARS withheld
R995 million in a dispute over Eskom's claims; and the report does not say
whether fuel later exported to neighbours (about 1.5 bn litres) is in the
base. It also conflicts with SARS's own statement of 21 bn litres against 24
bn (next section), which has not been reconciled.

Diesel rebates on the same levy were R4,246 million and R3,174 million, which
is 1.95 and 1.46 bn litres rebated across farming, forestry, mining,
electricity generation, rail, harbour and offshore use. The fall of
0.49 bn litres is in line with lower diesel burn for power.

### Fuel levy volumes

SARS collects the fuel levy on petrol and diesel as they leave refineries and
import terminals, so the volume declared for levy is a measure of fuel entering
the domestic market that does not depend on the department's sales returns.
SARS media release, 12 March 2025: "Fuel consumption as at February 2025 was
21 billion litres compared to 24 billion in the prior year".

Read as the eleven months April to February of each fiscal year, and set
against recorded petrol plus diesel sales for roughly the same months:

| Eleven months to February | Levy-declared volume | Recorded sales (11/12 of the calendar year) | Difference |
|---|---|---|---|
| 2024 | 24 bn litres | about 20.1 (2023: 21.94) | about 3.9 |
| 2025 | 21 bn litres | about 19.0 (2024: 20.76, FIASA) | about 2.0 |

In the first period the levy was declared on about 3.9 bn litres more than the
department recorded as sold, which is of the same order as the all-product comparison above (4.4 bn in 2023).
One reading is that the fuel is taxed and consumed and that the department's
sales series undercounts. The comparison rests on an assumed April-to-February
period set against eleven-twelfths of calendar-year sales, so a period mismatch
or stock movement could produce the same difference. A second SARS release (12 November
2025) points the same way: declarations by importers rose 133% (3.6 bn litres)
in April to September 2025 while those by local manufacturers fell 39% (3.4 bn).

This is an inference, not a finding. The release gives round figures for both
fuels together, "as at February" is read here as fiscal year to date, and the
comparison months do not line up exactly. The tables in SARS's Tax Statistics
2025 that would give the levy by fiscal year (Table A1.7.2) could not be read
from the PDF. If the reading is right, recorded "demand" in the model's history
understates diesel consumption by a fifth or more in 2023, which matters for
any estimate of Vopak's addressable market.

**JODI.** South Africa's submissions to the JODI oil database carry refinery
output, imports, exports, stocks and demand by product and month for 2023 and
2024 (kept at `external/data/raw/jodi/`; 2025 is blank). They are the only
source found with a product split of refinery output (2023: petrol 8.52,
diesel 5.19 bn litres; 2024: 7.34 and 3.89) and a stock series (closing diesel
stock 0.65 bn litres at December 2023, 0.55 at December 2024). They are not
usable as they stand: reported diesel imports are 6.8 bn litres for 2023
against 12.9 in customs, the statistical differences are 1 to 3.5 bn litres,
and every entry has JODI's lowest reliability code.

## Review outcomes, 6 October

Manish reviewed this package. Applied on `manish-branch` for Nigel to confirm:

- **SARS is the primary record of imports and exports from 2014.** FIASA's
  trade table is kept as a cross-check and for years before 2014. The three
  SARS extracts are declared in `sources.yaml`, registered (7,509 rows) and
  `fetch_sars` is part of `refresh_sources`. The engine does not read them, so
  no output changes.
- **Operator output is recorded** in
  `assumptions/2026/reference/refinery_output_operators.csv` (17 rows: Secunda
  and Natref for the years to June 2020-2026, Astron for 2023-2025) with its
  evidence record, in reported units only.

Left for Nigel:

- Which 2024 diesel import figure to use, together with how to report the
  diesel residual. Customs gives 10.793 bn litres; the residual is a
  hypothesis (see the sensitivities section).
- Whether implied production may stand in for petrol output after 2021.
- Whether to stop using the 2019 and 2020 energy balances for trade.

Dropped: querying FIASA about its 2024 misprint, duplicated 2025 row and the
2018 difference.

## Nigel's review and changes made, 7 October

Nigel reviewed this package at commit `4e64c8c`
(`manish_branch_review_2026-10-06.md`). His answers to the items above:

- 2024 diesel imports: the customs figure, 10.793 bn litres, in line with
  customs as the primary source. Done: the balance now selects customs for
  every product and year from 2014.
- The residual is a balancing requirement and the 3 to 4 bn litre diesel gap
  is a hypothesis. It does not stand in for petrol output and is not added to
  demand. Done: wording and column names changed
  (`sales_less_net_imports`, with its basis stated in the file).
- Operator and fuel levy comparisons moved to the sensitivities section, in
  reported units, with fiscal and calendar years marked.

Still open: production by product after 2021, stock changes, coverage of the
sales series, and which 2024 national sales figure to use (Nigel).

## Other sources checked for 2024 national sales, 7 October

| Source | Result |
|---|---|
| Department's sales volumes page, re-read | Latest national file is still 2023 quarter 4, posted 8 April 2024 |
| Road Accident Fund Annual Report 2024/25 | Litres levied for both fuels together; see the sensitivities section |
| FIASA quarterly industry review (FTI Consulting, 2024 Q1) | Charts only, sourced to the department; no 2024 volumes |
| SARS media releases on the fuel levy | Round figures, already recorded |
| Not checked | South African Reserve Bank series, the International Energy Agency's paid data, and operators' sales disclosures |

None gives 2024 petrol and diesel separately. The Road Accident Fund figure is
the only independent count found, and it does not show the fall in 2024 that
FIASA's figures show.
