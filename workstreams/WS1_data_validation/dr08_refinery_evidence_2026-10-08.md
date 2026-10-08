# DR08 Refinery supply: evidence, 8 October 2026

For Nigel's review. Answers request DR08: for each refinery, PetroSA included,
its capacity, output, yields, utilisation, feedstock and closure or restart
dates. Petrol and diesel only.

Status: **28 facts read from sources, 6 calculated, 4 not available.**

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
| Sapref, Durban | Crude oil | 180,000 | Not refining; acquired by the Central Energy Fund | Central Energy Fund, September 2026 |
| Enref (Engen), Durban | Crude oil | 0 (135,000 in 2021) | Not operating after a major fire | Department, Energy Sector Report 2023 |
| PetroSA, Mossel Bay | Gas to liquids | 0 (45,000 in 2021) | Not operating since December 2020: no feedstock | PetroSA tender; department's 2023 report |

Capacity in operation is 358,000 barrels a day, half of the 718,000 published
for all six plants in 2021.

**A caution on the capacity figures.** They come from the department's
Energy Sector Reports, but the department's table names the industry
association's annual report (SAPIA, now FIASA) as its own source. So the only
official capacity table rests on FIASA. Astron's 100,000 is confirmed by
Glencore. I found no operator figure for Secunda or Natref in the documents
held.

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

**No operator publishes petrol and diesel by plant.** The only output by
product is national, from the department's energy balances, and it ends at
2021:

| Billion litres | 2017 | 2018 | 2019 | 2020 | 2021 |
|---|---|---|---|---|---|
| Petrol | 9.43 | 9.97 | 10.42 | 7.89 | 6.35 |
| Diesel | 7.92 | 8.43 | 9.08 | 6.45 | 5.31 |

## Yields and utilisation

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
| Petrol and diesel output by plant, Every plant | No operator publishes petrol and diesel volumes by plant. Needs the operators, through Nigel. |
| Petrol and diesel produced after 2021, South Africa | The department has published no balance after 2021. |
| Yield by plant after 2021, Secunda, Natref, Astron Energy | Needed to turn plant output into petrol and diesel. Needs the operators. |
| Output as a share of capacity, Astron Energy | Glencore reports energy content, not barrels. Converting it needs an assumed energy content per barrel. |

Also not in a source held: the dates Enref and Sapref stopped refining, and an
operator's own capacity figure for Secunda and Natref.

## Checks

- The evidence table is rebuilt from registered inputs; a test checks the
  committed file equals a fresh build and that every fact has a source.
- Every figure typed from a document was read against the page named.
- FIASA and JODI are not selected. The department's capacity table, which
  cites the industry association, is used and flagged.
- No model input read by the engine changed; model results are unchanged.
