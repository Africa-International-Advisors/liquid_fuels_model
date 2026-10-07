# Demand baseline workbook: history added, for review on 8 October

Follows the 7 October check-in. Nigel's workbook
(`output/delivered/Demand_baseline_workshop_2026_10_07_compact.xlsx`) is kept
unchanged. The extended copy is
`output/delivered/Demand_baseline_workshop_2026_10_08_history.xlsx`, built by

    python -m lfm.scripts.build_demand_baseline_workbook --vintage 2026

Observations are values read from the registered inputs; totals, balances and
intensities are Excel formulas. Opened in Excel and recalculated: no formula
errors. Nothing here is an accepted input.

## What was added

| Sheet | Contents |
|---|---|
| History | The whiteboard table, 2012-2025, million litres: department sales by province (petrol and diesel), customs imports, exports and net imports, refinery production, the balance, and the Road Accident Fund count |
| Sector history | Mining, manufacturing and agriculture diesel beside their activity measures, litres per unit of activity, and an indicative figure for 2022-2025 |
| Checks | Each Evidence value that traces to a registered input, recomputed; and the changes made in the copy |
| History sources | Publisher, link, original file, extract and refresh command for each dataset |

One change to an existing sheet: Source selection for 2022 and 2023 is set to
Department instead of FIASA (the two agree to within rounding in those years).
2024 stays on FIASA, unverified, because the department has published nothing.

## Checks on the existing workbook

- 66 Evidence values were recomputed from the registered inputs; all match.
- Not checked yet: vehicle sales and stock, electric vehicle sales, freight,
  power and airport rows (the vehicle block comes next), and the Model run
  sheet, which is a frozen engine run.
- The model run in the workbook was made on `main`, where industry starts at
  2.5 bn litres and agriculture at 0.7. `manish-branch` proposes 1.50 and 1.06.
- Baseline, 2024: the model gives 16,055 million litres of diesel against
  selected sales of 11,734, a difference of 4,321; petrol is 7,930 against
  9,029. Power generation is the largest part of the diesel difference
  (`sector_baselines_2026-10-07.md`).

## What the history shows

- **Department files.** Provincial sums equal the national file in most years.
  They differ in 2014 (petrol +140, diesel +128 million litres) and slightly
  in other years already traced. Provincial data covers 2013-2022; the
  national file runs 2012-2023.
- **Customs.** Net imports of petrol and diesel rose from 3.7 bn litres in
  2014 to 15.7 bn in 2022, and were 13.1 bn in 2024 and 15.2 bn in 2025.
- **Production.** Reported by product only to 2021 (petrol 6.35, diesel 5.32
  bn litres that year). Operators' figures after that are all products
  together, in barrels or energy units, and are shown unconverted.
- **Balance.** Sales less net imports for 2024 is 5.95 bn litres for petrol
  and 1.74 for diesel. Against reported production the unexplained part is
  within 0.1 bn litres for petrol in 2014, 2019 and 2021, and is -0.5, 0.0
  and -1.2 for diesel in the same years.
- **Road Accident Fund.** Litres levied exceed recorded sales by 2.3 bn (year
  to March 2024) and 3.7 bn (to March 2025). New evidence; a hypothesis.

## Sector history: what can and cannot be said

| Sector | Diesel in the balance, 2012-2021 | Per unit of activity | Indicative 2024 |
|---|---|---|---|
| Mining | 1.04-1.82 bn litres | 11-17 million litres per index point; unstable | 1.40 bn litres |
| Manufacturing and other industry | 0-0.23 bn litres, by difference | Not usable before 2016, when the balance had no manufacturing lines | 0.17 bn litres |
| Agriculture | 0.90-1.09 bn litres in most years | 8-11 million litres per bn rand of value added | 0.96 bn litres |

The indicative figures hold the 2018-2021 average intensity and apply the
2022-2025 activity. They are estimates for discussion. Mining's intensity
swings by 40% between years with little change in output, which says the
balance's sector lines are not steady enough to calibrate on without care.

## Not done

- History starts where each source does: customs in litres from 2014,
  provinces from 2013. FIASA trade is shown for 2012-2013 as a comparison.
- Stock change is not in the balance; no usable series exists.
- The vehicle block (opening stock, new sales, scrapping, electrification) is
  not yet sourced or checked.
- Jet, power, marine and the provincial forecast are not touched.
- The Mining, Manufacturing and Agriculture sheets' workshop inputs are left
  blank for Nigel to agree; the evidence for them is on Sector history.

## Decisions for the review

1. The 2024 sales source, or start from 2023.
2. Whether the sector split should rest on the energy balance at all, given
   its instability, and which base year to use.
3. Whether to hold intensity constant when growing mining, manufacturing and
   agriculture with their indices.
4. Whether History replaces the Source selection sheet as the place where the
   historical choice is made.
