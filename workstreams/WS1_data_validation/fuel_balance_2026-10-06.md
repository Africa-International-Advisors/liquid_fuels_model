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
| Actual production 2022 onward | Manish | Sasol, Natref and Astron totals obtained (see follow-up and the all-product check); product split still missing; ask the department whether a 2022 or 2023 balance exists |
| Stock movements | Manish / Nigel | JODI carries a stock series of low reliability (see the fuel levy section); ask the department or FIASA |
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

## All-product check for 2023 and 2024, with Astron included

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
be supplied from this output without appearing in sales. These reduce the gap
but are unlikely to remove it.

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

## Fuel levy volumes: the likeliest explanation of the residual, 6 October

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
department recorded as sold, which is the size of the residual found from the
balance (3 to 4 bn), from operators' output (4.4 bn in 2023) and now from tax.
The simplest reading is that the fuel is real, taxed and consumed, and that the
department's sales series undercounts, most plausibly sales by importers and
wholesalers who do not file returns with it. A second SARS release (12 November
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
