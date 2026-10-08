# Hand-back to Nigel, 7 October 2026

Answers the five priorities on page 24 of the Convergence pack (Manish's focus,
7 October) and the 7 October check-in. All work is on `manish-branch`; nothing
has gone to `main`. `main` was merged in five times, last at `37ffa0b`.

Read first:

- Deck: `pptx/output/delivered/supporting/Vopak_Manish_Handback_2026_10_07.pptx`
  (PDF alongside), one section per priority.
- Decision log: `manish_decision_log_2026-10-07.csv`, 21 decisions with the
  evidence, my proposal, the owner and a status.
- Workbook: `output/delivered/Demand_baseline_workshop_2026_10_08_history.xlsx`,
  your workshop workbook with the sourced history added.

## Status against the five priorities

| # | Priority | Output asked for | Status | What is ready | What is not |
|---|---|---|---|---|---|
| 1 | National balance | Corrected balance, source differences, missing production and stocks | Ready, with stated gaps | Balance rebuilt on customs trade by one command, with tests; three deck pages; 2018-2019 difference traced as far as the data allows | Production by product after 2021 and stocks do not exist in any source found; 2024 sales source is your decision |
| 2 | Forecast levers | Three fuel tables with baseline and low / medium / high for 2030 and 2035 | Proposed | All 20 levers have a baseline, rationale and source; 39 of 120 values have a proposed replacement; nine levers added | Several baselines are placeholders; freight is in tonnes; replacements await your challenge |
| 3 | Sector baselines | Agriculture and industry starting values; overlaps | Proposed | 1.06 and 1.50 bn litres with the forecast effect; overlap table by model segment | On-road overlap not sized; power generation is 2 bn litres above reported burn |
| 4 | Tank handling | Site assumptions, evidence and estimates labelled | Proposed | Lesedi and Durban, every value marked; eight marked to confirm with the client | No Vopak operating data; other operators' sites not done |
| 5 | Reviewable hand-back | Figures checked, hand-back refreshed, ready / proposed / unresolved listed | Ready | This note, the decision log, the deck, and 288 figures in the current 30-page pack checked with none differing | Vehicle block: observed against the model, see below |

## Three review corrections from 6 October

All three are done: the balance selects customs for every product and year
from 2014; "implied production" is "sales less net imports" and the diesel gap
is a hypothesis; battery electric, plug-in hybrid and conventional hybrid are
defined separately. The 6 October deck was corrected to match and moved to
`supporting/`.

## From the check-in

| Asked for | Status |
|---|---|
| Historical baseline: department by province, customs trade, refinery output, balance | Done from 2012 on the History sheet; customs is in litres only from 2014 and provinces start in 2013 |
| Every historical row sourced, with links | Done on the History sources sheet |
| Litres per unit of activity for mining, manufacturing, agriculture | Done on the Sector history sheet; mining swings 11-17 million litres per index point, so treat with care |
| FIASA as a data point only | Done: department selected for 2022-2023; FIASA shown as comparison rows |
| Python builds it, Excel shows it with formulas | Done: one command; your sheets are unchanged apart from eight source-selection cells |
| Vehicle block with sources | Done on the Vehicle history sheet; stock by age and by fuel within class is not available |
| Jet | Sales, trade, production and aircraft movements lined up on the History sheet (section 7); not a jet model |

## Added on 8 October, before the review

- Diesel by use sheet: the six branches of the check-in diagram, summing to sales; road diesel split into
  heavy, light and passenger vehicles with the 2018 study's shares (60.5 / 27.0 / 12.5%).
- Stats SA's transport industry survey gives a measured floor for truck diesel: about 2.9 bn litres (2019)
  and 3.2 bn (2023) bought by hire-and-reward road freight firms.
- Provincial estimates for 2023 and 2024 shown in the province rows, marked as estimates; 2025 explained.
- Jet section, HML response sheet, Gap status sheet and a 25-row sources sheet.

## New evidence found today

- **Road Accident Fund levy.** Audited accounts give 24.25 and 24.42 bn litres
  of petrol and diesel levied in the years to March 2024 and 2025, against
  recorded sales of 21.94 and 20.76. Volumes rose 0.7% where FIASA shows a
  fall of 5.4%. Independent of the department's sales returns; fiscal years,
  both fuels together.
- **Lesedi.** The 40,000 m3 expansion was commissioned in October 2025.
- **Rail.** Rail-friendly general freight left on road is about 13% of road
  tonne-kilometres, which caps road-to-rail diversion.
- **Power.** The model's 2024 diesel for generation is 3.58 bn litres against
  about 1.6 at the peak of load-shedding.

## Vehicle block: where the model's settings differ from what is observed

| Item | Observed | Model |
|---|---|---|
| Cars' share of new sales | 65-71% | 78% |
| Light commercial share of new sales | 24-29% | 18% |
| Cars retired each year, % of stock | 4.3 falling to 2.4 (2022-2025) | 4.0% |
| Diesel vehicles registered, December 2023 | 3.34 million | 3.66 million implied by the split |
| Petrol per registered petrol vehicle, 2023 | 1,056 litres | 1,615 litres |

## Input changes on the branch that need your decision

| Change | Effect on results | Marked |
|---|---|---|
| Agriculture and industry starting values (6 October) | -0.63 bn litres of diesel in 2024 | needs verification |
| Secunda capacity 75 to 150 with utilisation halved (7 October) | None | unreviewed in the register |

Nothing else on the branch changes model results.

## Checks

- `python -m pytest -q`: 177 passed, 1 skipped.
- `python -m lfm check --vintage 2026`: coverage passed, 54 open exceptions,
  so output remains draft.
- Both decks exported through PowerPoint and inspected; the workbook was
  recalculated in Excel with no formula errors.

## Not done

- Pack pages without charts of observations are not checked. The rest are: 288 figures, all match
  (`workstreams/WS3_reporting_delivery/pack_figure_check_2026-10-08.md`, with seven points on labels).
- Vehicle block: stock by age and by fuel within each class is not in any source held, so the
  cohort starting point cannot be checked. The rest is on the Vehicle history sheet.
- The Reatile workbook's own demand history is about 1 bn litres above the
  department's for diesel in 2022 and 2023, and for petrol in 2023. Not traced.
- The model run inside the workshop workbook is from `main`.

## Commands added today

| Command | Writes |
|---|---|
| `python -m lfm.scripts.build_fuel_balance --vintage 2026` | The petrol and diesel balance file |
| `python -m lfm.scripts.build_fuel_lever_response --vintage 2026` | The lever response tables |
| `python -m lfm.scripts.build_sector_baseline_review --vintage 2026` | Diesel by model segment, with and without the sourced baselines |
| `python -m lfm.scripts.backtest_provincial_shares --vintage 2026` | Scores for six ways of estimating provincial shares |
| `python -m lfm.scripts.build_demand_baseline_workbook --vintage 2026` | The extended workbook |
| `python -m lfm.scripts.check_pack_figures --vintage 2026` | The pack figure check |
