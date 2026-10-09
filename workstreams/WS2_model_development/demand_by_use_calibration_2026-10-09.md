# Demand by use: one baseline, proposed. 9 October 2026

For Nigel. Task 2 of `manish_next_steps_2026-10-09.md`. Nothing in the model is changed;
this is a proposal to agree before any input moves.

## The two questions

**1. Why does the model show 3.6 billion litres of diesel for power when 0.9 to 1.6 is
reported?**

The model's station list is twice the real fleet. `generation.yaml` holds Ankerlig,
Gourikwa, Avon and Dedisa (3,072 MW) plus two stations called "new_1" and "new_2"
(3,000 MW), carried over from the Reatile workbook as planned capacity. The model's
3.58 billion litres is what 6,072 MW burns at a load factor of about 22%, which is close
to how hard the four real stations ran in the heaviest year (17 to 20%). So the rate is
plausible and the capacity is doubled. That is my reading of the inputs; the placeholder
stations are Nigel's to confirm.

| Billion litres | Year to March 2023 | 2024 | 2025 |
|---|---|---|---|
| Eskom's turbines, reported | 0.94 | 1.13 | 0.68 |
| Avon and Dedisa, estimated from generation | 0.34 | 0.47 | 0.21 |
| Reported and estimated together | 1.28 | 1.60 | 0.89 |
| Model, calendar 2024 | | 3.58 | |

So the gap is about 2 billion litres in the heaviest year and 2.7 in the latest. The
power fleet work of 7 October (decision D22) already proposes replacing the two
placeholder stations.

**2. What sits in the energy balance's 5.3 billion litres of "other"?**

It is road fuel that the department moved to another line. From 2016 the balance
books a large volume to "commercial and public services" that it had booked to road
transport before. The two lines together barely move:

| Diesel, billion litres | 2014 | 2015 | 2016 | 2019 | 2021 |
|---|---|---|---|---|---|
| Road transport | 8.90 | 9.43 | 4.40 | 6.73 | 6.33 |
| Commercial and public services | 0.02 | 0.01 | 4.97 | 3.82 | 4.30 |
| The two together | 8.93 | 9.44 | 9.37 | 10.55 | 10.63 |

Petrol shows the same break in 2016 (2.24 moved; 0.91 in 2021). The likely reason is
sales through resellers and depots being classed by the seller, not the end user. The
department gives no explanation, so this is my reading of the figures.

## Proposed baseline

Use department sales as the total, take the sourced uses from the best source for
each, and treat road as what remains. For 2021, the last year every line is published:

| Billion litres, 2021 | Diesel | Petrol | Source |
|---|---|---|---|
| Sales (the total) | 12.95 | 9.30 | Department, provinces added up |
| Power generation | 0.58 | | Eskom, year to March 2022, reported |
| Mining | 1.29 | 0.05 | Energy balance |
| Manufacturing, other industry, construction | 0.21 | 0.02 | Energy balance |
| Agriculture | 1.06 | 0.12 | Energy balance |
| Rail | 0.14 | | Transnet, estimated (DR07) |
| Road, as the remainder | 9.67 | 9.11 | Sales less the lines above |

Road diesel at 9.7 sits close to the balance's road plus commercial lines (10.6), which
supports reading "other" as road fuel.

## What would change in the model

| Billion litres | Model, 2024 | Proposed basis | Change |
|---|---|---|---|
| Power generation | 3.58 | 0.9 to 1.6 | Down about 2 to 2.7 |
| Vehicles, petrol and diesel | 16.43 | about 18.8 (road as the remainder) | Up about 2.4 |
| Mining, manufacturing, agriculture | 2.57 | 2.7 | Little change |
| Total | 23.4 | sales were 21.9 in 2023 | |

The model's total is near sales, but for the wrong reasons: too much diesel for power
and too little for road, roughly cancelling. Fixing power alone would leave the model
about 2 billion litres short of sales.

## To agree with Nigel

1. Total: department sales.
2. Power: reported litres, with the fleet and cases of decision D22.
3. Road: the remainder, with "commercial and public services" treated as road fuel.
4. Which year the issue tree shows: 2021 (all lines published) or 2023 (latest sales,
   with the sector lines estimated).

## Limits

- The reclassification in the balance is inferred from the series, not documented.
- Eskom reports years to March; sales are calendar years.
- The vehicle figure is not re-estimated here. It needs the vehicle block to be
  recalibrated to road fuel, which is the larger piece of work.

Sources: `energy_balance_department.csv`, `fuel_balance_petrol_diesel_2009_2025_2026-10-06.csv`,
`sector_baselines_2026-10-07.csv`, `dr07_demand_evidence_2026-10-08.csv`, `generation.yaml`.
