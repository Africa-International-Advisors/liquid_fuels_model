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

## Provincial sales for 2023-2025: estimated, with a tested method

The department's district data stops at quarter 1 of 2023. Six ways of
estimating provincial shares were tested against 2013-2022
(`python -m lfm.scripts.backtest_provincial_shares --vintage 2026`; results in
`workstreams/WS1_data_validation/provincial_share_backtest_2026-10-08.csv`).
The score is the share points placed in the wrong province.

| Method | Petrol, 1 / 2 / 3 years ahead | Diesel, 1 / 2 / 3 years ahead |
|---|---|---|
| Same year's quarter 1 shares | 2.5 (same year) | 5.3 (same year) |
| Hold the last year's shares | 3.4 / 4.4 / 4.9 | 7.5 / 10.9 / 12.6 |
| Move shares with provincial GDP | 3.2 / 4.1 / 4.7 | 7.4 / 10.6 / 12.3 |
| Average of the last three years | 3.7 / 4.4 / 4.9 | 9.2 / 11.7 / 13.6 |
| Extend the three-year trend | 4.4 / 6.8 / 8.4 | 7.7 / 12.0 / 16.7 |
| Move shares with registered cars | 3.8 (one test only) | 6.1 (one test only) |

Method used on the History sheet (section 6), marked as estimates:

- **2023:** the quarter 1 2023 shares, which are observed, times the
  department's national total for 2023. This is the best method tested.
- **2024:** the 2023 shares moved with each province's share of real GDP,
  times the 2024 national total, which is FIASA's and unverified.
- **2025:** 2024 shares held. No national sales figure exists for 2025 from
  any source, so the shares are shown and the volumes are blank.

What the scores mean: 2.5 share points for petrol is about 1.2% of national
volume in the wrong province. A single province can still be far out; the
worst case in the tests was 15-18% for one province using quarter 1 shares,
and 40% for diesel when holding shares. Diesel is roughly twice as uncertain
as petrol by every method, because its provincial figures follow where bulk
sales are booked. Trend extension is the worst method and should not be used.

## Vehicle block: observed beside the model's settings

The Vehicle history sheet lines up registered vehicles (NaTIS, December
2021-2025), new sales (naamsa, 2017-2025), electrified sales, the fuel split
of the fleet and the model's settings. Retirements, shares and cross-checks
are formulas.

| Item | Observed | Model setting | Reading |
|---|---|---|---|
| Cars' share of new sales | 65-71% (2019-2025) | 78% | Model puts too many new vehicles in the passenger class |
| Light commercial share | 24-29% | 18% | Too few |
| Medium and heavy share | 5-6% | 4% | Slightly low |
| Cars retired, % of stock a year | 4.3, 3.1, 2.5, 2.4 (2022-2025) | 4.0% | Model is at the top of the observed range, which is falling |
| Light commercial retired | 5.6, 4.5, 3.6, 3.4 | 5.0% | Same pattern |
| Trucks retired | 8.5, 6.8, 6.4, 6.2 | 6.0% | Close |
| Diesel vehicles on the road, December 2023 | 3.34 million registered | 3.66 million implied by the model's split | Model's split gives about 0.33 million too many |
| Petrol per registered petrol vehicle, 2023 | 1,056 litres | 1,615 litres (17,000 km at 9.5 L/100 km) | Model's distance and fuel use together are about 50% above what sales support |
| Distance implied by petrol sales | about 12,900 km | 17,000 km | Published study gives 14,457 km |
| Battery electric share of new sales | 0.03% (2019) to 0.24% (2024), 0.18% (2025) | S-curve to 30% | See the lever response |

Retirements are apparent: last December's stock plus the year's sales less
this December's stock. Used imports and re-registrations would lower the true
figure, and naamsa's segments do not map exactly onto NaTIS classes.

Not available from any source held: stock by age, stock by fuel within each
class, electric and hybrid vehicles in the fleet by year, distance driven
after 2014, and the petrol and diesel split of new sales by segment.

## Not done

- History starts where each source does: customs in litres from 2014,
  provinces from 2013. FIASA trade is shown for 2012-2013 as a comparison.
- Stock change is not in the balance; no usable series exists.
- Opening stock by age and by fuel within class is not available from any
  source held, so the cohort start cannot yet be checked.
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

## Diesel used by trucks: what the sources say, checked 8 October

No source measures diesel used by trucks. Three were checked for the nearest
thing; the documents are kept in `external/data/raw/literature/` and
`external/data/raw/statssa/`.

| Source | What it gives | Figure |
|---|---|---|
| Stats SA, Transport and storage industry 2023 (Report 71-02-01), Table 20 | Fuel bought by road freight transport enterprises | R41,640 million (2019) and R71,468 million (2023, preliminary) |
| Merven, Hartley and Ahjum (2019), Road freight and energy in South Africa, SA-TIED WP60, p.10 | Land freight's share of domestic diesel demand, 2012 | 60.5% (and 33% of petrol) |
| Stone et al. (2018), vehicle parameters already held | Vehicles x distance x fuel use by class, 2010 fleet | Trucks 4.84, light commercial 2.16, cars 0.70, buses and taxis 0.29 bn litres; road diesel 7.99 |
| National GHG inventory 2000-2022 (DFFE, 2024), p.578 | Road transport as one total | Split by cars, light-duty trucks and heavy-duty trucks is marked "NE" (not estimated) |

Stats SA's rand figures divided by the average inland wholesale diesel price
over each survey's reference year (R14.58 and R22.66 a litre) give about
**2.9 bn litres in 2019 and 3.2 bn litres in 2023**. This is the only figure
based on what operators report. It covers enterprises whose business is road
freight, so it leaves out trucks run by retailers, mines, farms and
manufacturers for their own goods; it may include some petrol and lubricants;
and operators buying in bulk pay less than the list price, which would raise
the litres. It is a floor for truck diesel, not the total.

The two modelled figures agree with each other (they come from the same
research group) and sit above the Stats SA floor, as they should: about 4.8 bn
litres for all trucks in 2010 against about 2.9 bn for hire-and-reward
operators in 2019.

## Diesel by use: the six branches, approach A

The Diesel by use sheet lays out the diagram from the check-in. Mining,
manufacturing, agriculture and power come from sources (observed to 2021,
estimated after). Road diesel is what remains of recorded sales, and is split
into three vehicle groups with the shares of the 2018 vehicle study, held at
their 2010 values. Every figure below the source rows is a formula.

| Branch, million litres | 2019 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| Diesel sales used | 12,909 | 12,946 | 12,717 | 12,908 | 11,734 |
| Mining | 1,667 | 1,294 | 1,396 | 1,396 | 1,404 |
| Manufacturing and other industry | 231 | 157 | 167 | 168 | 167 |
| Agriculture | 922 | 1,058 | 1,106 | 1,055 | 963 |
| Power | 29 | 0 | 1,276 | 1,594 | 880 |
| Road vehicles and uses not listed | 10,060 | 10,437 | 8,773 | 8,694 | 8,320 |
| of which heavy vehicles (60.5%) | 6,089 | 6,317 | 5,310 | 5,263 | 5,036 |
| of which light vehicles (27.0%) | 2,715 | 2,817 | 2,368 | 2,347 | 2,246 |
| of which passenger vehicles (12.5%) | 1,255 | 1,302 | 1,095 | 1,085 | 1,038 |

Which classes of the study fall in each group (also on the sheet):

| Group | Diesel classes counted | Diesel in the study, 2010 fleet |
|---|---|---|
| Heavy vehicles | HCV1Diesel to HCV9Diesel: trucks in nine weight classes | 4,836 million litres |
| Light vehicles | LCVDiesel: light commercial vehicles (bakkies and vans) | 2,157 |
| Passenger vehicles | CarDiesel, CarHybridDiesel, SUVDiesel, BusDiesel, MBTDiesel: cars, SUVs, buses and minibus taxis | 997 |

Points to carry with it:

- The road figure is a remainder. It includes rail, construction plant,
  private generators and ships' diesel, which no source separates, and it
  moves with every error in the rows above it.
- Power is the energy balance to 2021 and generation times 0.31 litres per
  kWh from 2022, shown under the calendar year the financial year mostly
  covers. The balance shows almost nothing for power in 2017-2021.
- The shares are for the 2010 fleet. Diesel vehicles have doubled since and
  trucks grew by about a quarter, so today's heavy share is probably lower.
- Heavy vehicles sit above Stats SA's figure for hire-and-reward road freight
  (2,855 in 2019 and 3,154 in 2023) by 3,234 and 2,108, as they should.
- 2024 uses FIASA's unverified sales; 2025 has no sales figure.

## Added on 8 October: jet, lever response, gap status and full sources

**Jet (History, section 7).** Low effort, so brought in. Million litres:

| | 2014 | 2019 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| Sales used | 2,293 | 2,439 | 1,048 | 1,478 | 1,844 | 1,955 (FIASA) |
| Net imports | — | — | 348 | 426 | 222 | 240 |
| Production reported | 1,715 | 1,090 | 861 | — | — | — |
| Sales less net imports | — | — | 700 | 1,053 | 1,622 | 1,715 |
| Aircraft movements, thousand | 541 | 512 | 316 | 416 | 451 | 456 |
| Jet sold per movement, litres | 4,238 | 4,759 | 3,312 | 3,553 | 4,086 | 4,285 |

Jet sales in 2023 were 76% of their 2019 level while movements were 88%, so
jet sold per movement is 14% below 2019. Customs has a month missing for jet
imports in 2019, so net imports start in 2020. Whether fuel loaded onto
international flights is recorded as an export is not established. Cargo,
aircraft mix, route length and airports outside ACSA are not separated; this
is a starting point, not a jet model.

**HML response sheet.** The 29 levers (Nigel's 20 and nine added) with
baseline, his low / medium / high values and the analyst's, for 2030 and 2035,
and the evidence. The HML sheet itself is unchanged.

**Gap status sheet.** A status against each of the 13 gaps on the Data gaps
sheet: ten narrowed, one open (marine), two proposed (freight
electrification and ranges). None is marked closed; that
is for the owner.

**History sources sheet.** Now 25 rows, covering every added sheet, including
the two documents that are not registered datasets (the Stats SA transport
survey and the freight energy study).

## Power fleet: station by station, in answer to Nigel's message of 7 October

Nigel asked for the power generation fleet to be defined, the coal
decommissioning timeline set beside it, and a block by year showing how much
diesel the fleet could consume, with repowered coal sites able to use diesel
as backup. The Power fleet sheet does this for 2022-2035. Stations and dates
are in `assumptions/2026/infrastructure/power_fleet_diesel.csv`.

**The diesel fleet today is four stations, 3,089 MW.**

| Station | Owner | MW | Note |
|---|---|---|---|
| Ankerlig | Eskom | 1,338 | Eskom sought a gas supply in 2023, aiming to switch by December 2027 with diesel as a supplement |
| Gourikwa | Eskom | 746 | Same tender |
| Avon | Independent producer | 670 | |
| Dedisa | Independent producer | 335 | |

Acacia and Port Rex (171 MW each) burn kerosene, not diesel, and are left out.
The model carries the same four stations plus two placeholders, "New 1" and
"New 2", of 1,000 and 2,000 MW with no source.

**What the fleet has done.** Load factor was 13.7%, 17.1%, 9.4% and 3.6% in
the years to March 2023-2026, which is about 1.28, 1.59, 0.88 and 0.33 bn
litres at 0.31 litres per kWh. The model has 3.58 bn litres for 2024 and 4.59
(high) or 1.05 (low) for 2030 and 2035.

**What it could burn.** Million litres a year:

| | 2022-2027 | 2028-2029 | 2030-2035 |
|---|---|---|---|
| Low (3.6% load factor) | 301 | 118 | 118 |
| Medium (9.4%) | 792 | 311 | 637 |
| High (17.1%) | 1,435 | 564 | 1,216 |
| Ceiling: everything on diesel all year | 8,389 | 8,389 | 14,906 |

The drop in 2028 is Ankerlig and Gourikwa moving to gas with 10% of output
still on diesel. The rise in 2030 in the medium and high cases is gas plants
at retired coal sites using diesel as backup.

**Coal retirements.** Komati (990 MW) is shown as shut from 2023. Camden,
Grootvlei, Hendrina, Arnot and Kriel (9,474 MW together) hold exemptions to 31
March 2030. Duvha and Matla (6,600 MW) are shown to 2033. Eskom was to decide
by end September 2026 whether the five shut, are repowered or run on; I could
not find the outcome.

**Repowering is a scenario, not a plan.** No source says which sites get gas
plants. The sheet uses the national gas requirement in IRP 2025 (about 6 GW by
2030) as a stand-in: none, half or all of it at these sites.

Three assumptions drive the result and have no source; each is a single cell
on the sheet: 10% of output on diesel once gas is the main fuel; a 40% load
factor for gas plants at repowered sites; and 0.31 litres per kWh.

Not included: private generators at firms and homes. To confirm: Komati's
shutdown date (from memory) and the 2034 date for Duvha and Matla (from a
press summary).
