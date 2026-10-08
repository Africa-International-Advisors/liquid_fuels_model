# DR08 Refinery supply: evidence, 8 October 2026

For Nigel's review. Answers request DR08: for each refinery, PetroSA included,
its capacity, output, yields, utilisation, feedstock and closure or restart
dates. Petrol and diesel only.

Status: **40 facts read from sources, 8 calculated, 4 not available.**

**Where to look:** the workbook `output/delivered/Demand_baseline_workshop_2026_10_08_history.xlsx`.

- Sheet **DR08 evidence**: every fact with its source and open gap.
- Sheet **DR08 refinery output**: the six refineries with capacity, status and
  reported output, then national petrol and diesel production.

Table behind the first sheet: `dr08_refinery_evidence_2026-10-08.csv`, rebuilt by
`python -m lfm.scripts.build_dr08_refinery_evidence --vintage 2026`.

## The six refineries

| Plant | Type | Published capacity, barrels a day | Status | Source for status |
|---|---|---|---|---|
| Secunda (Sasol) | Coal to liquids | 150,000 | Operating | Sasol metrics, June 2026 |
| Natref (Sasol and TotalEnergies) | Crude oil | 108,000 | Operating; unit outage August to September 2026 | Sasol update, 1 September 2026 |
| Astron Energy, Cape Town | Crude oil | 100,000 | Operating; restarted early 2023 after a multi-year rebuild | Glencore Annual Report 2023 |
| Sapref, Durban | Crude oil | 180,000 | Not refining since the pause at the end of March 2022; acquired by the Central Energy Fund | Shell, 10 February 2022; Central Energy Fund, September 2026 |
| Enref (Engen), Durban | Crude oil | 0 (135,000 in 2021) | Shut since the fire of 4 December 2020; closure announced 23 April 2021 | Engen to Parliament, 8 December 2020; Engineering News, 23 April 2021 |
| PetroSA, Mossel Bay | Gas to liquids | 0 (45,000 in 2021) | Not operating since December 2020: no feedstock | PetroSA tender; department's 2023 report |

Capacity in operation is 358,000 barrels a day, half of the 718,000 published
for all six plants in 2021.

**A caution on the capacity figures.** They come from the department's
Energy Sector Reports, but the department's table names the industry
association's annual report (SAPIA, now FIASA) as its own source. So the only
official capacity table rests on FIASA. The operators confirm three of them: Glencore gives Astron 100,000, and Sasol's
Business Overview (April 2021) gives Secunda 150,000 and Natref 108,500.

## Output

Reported by the operators, all refined products, million barrels, years to June:

| | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| Secunda | 31.2 | 32.1 | 29.2 | 29.9 | 29.1 | 27.6 | 30.6 |
| Natref, Sasol's 63.64% share | 16.8 | 17.7 | 18.9 | 17.2 | 17.8 | 14.7 | 25.8 |

Source: Sasol production and sales metrics. Natref's 2026 figure includes
output above Sasol's share, because Sasol used a co-owner's capacity. Astron
reports energy content, not barrels (164,365 billion Btu in 2025).

Secunda's fuels were 3,472, 3,293 and 3,634 thousand tonnes in the years to
June 2024 to 2026, about half of its total production; the rest is chemicals.

**Petrol and diesel by plant: an estimate for Natref only.** Sasol states
Natref's split as 29 to 32% petrol and 31 to 37% diesel (Business Overview,
April 2021). Applied to Natref's reported production, scaled to the whole
refinery, billion litres, years to June:

| | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| Petrol | 1.22 to 1.34 | 1.28 to 1.41 | 1.37 to 1.51 | 1.25 to 1.38 | 1.29 to 1.42 | 1.06 to 1.18 |
| Diesel | 1.30 to 1.55 | 1.37 to 1.64 | 1.46 to 1.75 | 1.33 to 1.59 | 1.38 to 1.65 | 1.14 to 1.36 |

This is calculated, not reported: one stated range is applied to every year.
Sasol gives Secunda's split as 65% petrol, 35% diesel but not the total it
applies to, so no volume is calculated. Nothing is published for Astron.

The only reported output by product is national, from the department's
energy balances, and it ends at 2021:

| Billion litres | 2017 | 2018 | 2019 | 2020 | 2021 |
|---|---|---|---|---|---|
| Petrol | 9.43 | 9.97 | 10.42 | 7.89 | 6.35 |
| Diesel | 7.92 | 8.43 | 9.08 | 6.45 | 5.31 |

**After 2021.** The United Nations energy statistics run to 2023, in thousand
tonnes:

| Thousand tonnes | 2019 | 2020 | 2021 | 2022 | 2023 |
|---|---|---|---|---|---|
| Petrol | 5,030 | 3,491 | 2,488 | 1,323 | 1,827 |
| Diesel | 7,535 | 4,676 | 4,282 | 2,383 | 2,222 |

**Shown for comparison, not used.** In the years both exist, the petrol series
is about half the department's (it implies 0.39 to 0.48 kg a litre; petrol
weighs about 0.75). Diesel is close in 2019 and 2021 and low in 2020. For
Nigel: whether to use it at all.

## Yields and utilisation

- **Natref white product yield** (petrol, diesel, jet and other light
  products, % of crude processed): 89.4, 88.5, 87.3, 88.1, 87.5 for the years
  to June 2020 to 2024. Source: Sasol metrics. Not reported for 2025 and 2026.
- **Stated product split:** Natref 29 to 32% petrol, 31 to 37% diesel; Secunda
  65% petrol, 35% diesel. Source: Sasol Business Overview, April 2021.

- **National mix, 2017 to 2021:** petrol was 48 to 51% and diesel 40 to 43% of
  the four main fuels produced (petrol, diesel, jet, paraffin). This is a mix
  across all plants, not a plant yield, and it will have shifted since the
  Durban refineries stopped.
- **Utilisation, output over published capacity:** Secunda 57, 59, 53, 55, 53, 50, 56% for the
  years to June 2020 to 2026; Natref 67, 71, 75, 69, 71, 59% for 2020 to 2025. Capacity is
  crude equivalent and output is refined product, so these understate how hard
  the plants run.

## Outlook

| Plant | What is stated | Source |
|---|---|---|
| Sapref site | Three phases: imports through existing tanks; a refinery of about 400,000 barrels a day; then 400,000 to 650,000. No dates or investment decision | Central Energy Fund, 10 September 2026 |
| Secunda | Sasol finds it feasible to supply Secunda's methane-rich gas to outside customers from July 2028 to June 2030 as Mozambican gas declines. No fuel penalty quantified | Sasol, 6 November 2025 |
| PetroSA | Tender to recommission the liquids refinery and adapt the terminal to import finished products. No date | PetroSA tender |

The first phase at Sapref is an import terminal in Durban, which would compete
with existing terminals there. That bears directly on Vopak.

## Not available

| What | Why |
|---|---|
| Petrol and diesel output, Secunda and Astron Energy | Sasol states Secunda's split but not the total it applies to. Glencore publishes no split. Needs the operators, through Nigel. |
| Petrol and diesel produced after 2021, on the department's basis | The department has published no balance after 2021. The United Nations series does not match it. |
| Yield, Astron Energy | Nothing found. No plant publishes a split by year. |
| Output as a share of capacity, Astron Energy | Glencore reports energy content, not barrels, and no throughput in barrels was found. |

## Checks

- The evidence table is rebuilt from registered inputs; a test checks the
  committed file equals a fresh build and that every fact has a source.
- Every figure typed from a document was read against the page named.
- FIASA and JODI are not selected. The department's capacity table, which
  cites the industry association, is used and flagged.
- No model input read by the engine changed; model results are unchanged.
