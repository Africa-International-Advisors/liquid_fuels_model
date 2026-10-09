# Hand-back to Nigel, 7 October 2026

Answers the five priorities on page 24 of the Convergence pack (Manish's focus,
7 October) and the 7 October check-in. All work is on `manish-branch`; nothing
has gone to `main`. `main` was merged in five times, last at `37ffa0b`.

Read first:

- Deck: `pptx/output/delivered/supporting/Vopak_Manish_Handback_2026_10_07.pptx`
  (PDF alongside), one section per priority.
- Decision log: `manish_decision_log_2026-10-07.csv`, 23 decisions with the
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

## DR01 national balance and FIASA (8 October, afternoon)

- FIASA and JODI are not selected for any figure; they stay as comparison rows only.
- Sales are the department's provincial data added up for 2013-2022, as published, and kept by province.
  2023 is the national total split by first-quarter shares (an estimate). 2024 and 2025 are blank: FIASA and
  JODI have 2024 figures, but neither is reliable; the reasons are on the History sheet and in the DR01 note.
- Trade is customs from 2014.
- Production is the department's energy balance only, which ends at 2021. JODI is not used; it is a comparison
  row only. All fifteen energy balance files were downloaded again and match the copies held. Decision D23.
- The matched years are 2014 to 2021. Supply and recorded sales agree within 0.9 bn litres except diesel in
  2021 (supply 1.2 bn litres higher). Stock change is not available.
- Every selected figure in the balance file, and every row on the added workbook sheets, names its source.
- Detail: `workstreams/WS1_data_validation/dr01_national_balance_2026-10-08.md` and its evidence table.

## DR01 and DR04: what is missing (8 October, evening)

Workbook sheets: DR01 balance, Demand by use, DR04 routes, DR04 entry points, DR04 transport cost. Notes:
`workstreams/WS1_data_validation/dr01_national_balance_2026-10-08.md` and `dr04_routes_access_2026-10-08.md`.

**DR01 National balance: data not available.** The work is done as far as the sources go. Three things are
not published by anyone, so they cannot be filled in:

- Production after 2021 (the department's last energy balance is 2021)
- Sales for 2024 and 2025 (the department's sales data stops at 2023)
- Stocks, for any year

**DR04 Routes and access: not done.**

- Fuel tanker road and rail rates: not published; needs Vopak, a haulier or Transnet. Found on 9 October: Transnet's
  container comparison (road 1.23, rail 0.43 rand per net tonne-kilometre) and Stats SA's all-goods income per tonne
- Island View capacity for petrol and diesel: needs the port authority or Vopak. Found: 10 berths, 10 operators
- How Vopak Durban connects to the pipeline: needs Vopak. Found: the former Sapref site and Sasol inject directly
- Pipeline tariffs on routes other than Durban to Johannesburg: not found online
- Petrol and diesel storage at Matola: one terminal found (Galp, 40,000 m3 diesel and 20,000 m3 petrol)
- The delivered-cost comparison itself, which depends on the rates above

Pipeline capacity uses Transnet's 2020 figure: 148 million litres a week on the Durban to Jameson Park trunk
line, about 7.7 bn litres a year.

**DR07 Demand evidence.** Workbook sheets DR07 evidence, DR07 power diesel, DR07 fleet by province and DR07
efficiency and rail; note `dr07_demand_evidence_2026-10-08.md`.

- Eskom's reported turbine fuel is in: 0.94, 1.13 and 0.68 bn litres in the years to March 2023 to 2025. It
  confirms 0.31 litres per kWh. Eskom reports one total, not by station.
- New-vehicle fuel use fell 1.3% a year from 2005 to 2019 (IEA), inside the model's 0.5 to 1.5%.
- The system operator gives Avon's and Dedisa's contracts ending in 2030, Acacia and Port Rex shutting in
  2030, and 6 GW of gas plant assumed for 2030. Avon's end date in `power_fleet_diesel.csv` is changed to
  match: the low power case for 2030 falls from 86 to 20 million litres.
- Transnet carried 160 million tonnes in the year to March 2025 and aims for 250.

- Found on a second search: diesel used by rail locomotives (about 138 million litres a year), petrol and diesel
  vehicles by province, freight tonne-kilometres for 2019, truck fuel use, and the average age of vehicles.

Not available from any source:

- Diesel burned in private backup generators
- New gas plant: firm commissioning date for any project. Found on 9 October: Eskom plans to produce at Richards Bay
  from 2031; four bids of 29 May 2026 (Khanyazwe Flexpower 440 MW, Pictor 990 MW, Kelvin 600 MW, Komatipoort
  Power/Vutomi 800 MW) with no preferred bidder yet; a new 5,000 MW determination on 7 October 2026. The system
  operator's 2030 for 6 GW is not supported by any of these
- Vehicles by fuel within each class
- Vehicles by year of age
- Electric trucks and electric light commercial vehicles sold
- Fuel use of trucks, by year
- Road freight in tonne-kilometres, by year

**DR08 Refinery supply.** Workbook sheets DR08 evidence and DR08 refinery output; note
`dr08_refinery_evidence_2026-10-08.md`.

- Three plants operate (Secunda, Natref, Astron): 358,000 barrels a day, half of the 718,000 published in 2021.
  Sapref, Enref and PetroSA are not refining.
- Output by plant is all products together (Sasol, Glencore). Petrol and diesel are estimated for Natref only
  (Sasol's stated split: about 1.3 billion litres of petrol and 1.4 to 1.7 of diesel in the year to June 2024).
- Nationally, petrol and diesel by product are reported only to 2021. The United Nations series runs to 2023 but
  does not match the department, so it is shown and not used.
- Dates: Enref shut after the fire of 4 December 2020 (closure announced 23 April 2021); Sapref paused at the end
  of March 2022 (announced 10 February 2022).
- The capacity figures are from the department's Energy Sector Reports, whose table cites the industry
  association (SAPIA, now FIASA). Flagged.

Not available:

- Petrol and diesel output for Secunda and Astron Energy
- Petrol and diesel produced after 2021 on the department's basis
- Yield for Astron Energy
- Output as a share of capacity (Astron Energy)

## Power generation fleet (your message of 7 October)

Deck pages 11 and 12; workbook sheet Power fleet; input `assumptions/2026/infrastructure/power_fleet_diesel.csv`.

- Four stations burn diesel: Ankerlig 1,338 MW and Gourikwa 746 MW (Eskom), Avon 670 MW and Dedisa 335 MW
  (independent), 3,089 MW in all. Acacia and Port Rex burn kerosene and are not counted.
- Coal: Komati shut in 2022; Camden, Grootvlei, Hendrina, Arnot and Kriel may run to 31 March 2030; Duvha and
  Matla to 2034. Eskom's decision on the five, due end September 2026, had not been announced by 8 October.
- Diesel for power, million litres a year, low / medium / high: 301 / 792 / 1,435 to 2027, 20 / 637 / 4,224 in
  2030, 20 / 637 / 4,224 from 2031. The model has 3,581 for 2024.
- Every case setting is yours and Henry's to confirm (decision D22). Not sourced: 10% of output on diesel when
  gas is available, 40% load factor on gas, the gas turbines being sited at the five coal stations, and no gas
  reaching them in the high case.

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

## GDP: proposed for you, not changed (9 October)

The model still reads GDP from the Vopak/Reatile workbook (`timeseries/gdp.csv`, `gdp_per_capita.csv`,
`gdp_growth.csv`). The Stats SA series is staged beside it (`timeseries/macro_statssa.csv`, P0441, 1993-2025) and
is not read by the model. Proposal: point the model's GDP history at Stats SA. I have not made the change.

- The two agree for 2005-2017 except 2007, where the model's figure is 5.1% below Stats SA: it repeats the 2006
  value, which looks like a copy error.
- 2018-2024 differ by up to 0.5% (Stats SA revisions since); 2025 is 0.8% below Stats SA.
- Growth after 2025 (1.6% high, 1.0% low) is a separate assumption. Treasury forecasts 1.6%, 1.8% and 2.0% for
  2026-2028 (`timeseries/gdp_growth_treasury.csv`); nothing official exists after 2028.
- Yearly refresh: `python -m lfm.scripts.fetch_economy --vintage <year>`. Stats SA's site blocks scripted
  downloads, so the P0441, P0441.2 and P0302 files are first saved by hand into `external/data/raw/statssa/`.
  The World Bank and Treasury figures are fetched automatically.

## Checks

- `python -m pytest -q`: 179 passed, 1 skipped.
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
