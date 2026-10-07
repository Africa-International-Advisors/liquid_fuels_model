# Agriculture and industry starting values: proposal for Nigel, 7 October 2026

Priority 3 on Manish's focus page (Convergence pack p24). A proposal for
decision; nothing here is accepted. Model figures come from
`python -m lfm.scripts.build_sector_baseline_review --vintage 2026`, which runs
the engine's own segment modules with and without the sourced values and
writes `sector_baselines_2026-10-07.csv`. Evidence figures are from
`assumptions/2026/timeseries/energy_balance_department.csv`.

## Proposal

Diesel, billion litres a year:

| Sector | Earlier placeholder | On the branch now | Range in the evidence | Proposed starting value |
|---|---|---|---|---|
| Agriculture | 0.70 for 2024, no source | 1.06 for 2021 (energy balance, agriculture/forestry) | 0.90–1.09 in eight of ten years 2012–2021; 1.89 and 1.88 in 2016 and 2017 | **1.06**, provisional |
| Industry | 2.50 for 2024, no source | 1.50 for 2021 (energy balance, industry; mining is 1.29 of it) | 1.32–1.93 over 2012–2021 | **1.50**, provisional |

Reasons for keeping the 2021 values and not an average:

- 2021 is the latest balance and one consistent year for both sectors.
- A 2018–2021 average gives 0.98 for agriculture and 1.68 for industry. The
  industry average is pulled up by 2018 and 2019 (1.88, 1.90), before mining
  output fell.
- Activity has moved since 2021. Stats SA's mining volume index is 93.5 in
  2024 against 100.9 in 2021. Scaling the mining part by that gives industry
  about 1.40 for 2024. Agriculture's real value added was 89 in 2024 and 104.5
  in 2025 on a 2021 base of 100.

Both values keep `needs_verification: true`. The uncertainty to carry is about
±0.1 for agriculture and ±0.3 for industry.

## Effect on the forecast

Change from the placeholders, same engine, billion litres of diesel:

| | 2024 | 2030 | 2035 |
|---|---|---|---|
| Agriculture | +0.36 | +0.36 | +0.36 |
| Industry | −0.99 | −1.02 (high), −0.99 (low) | −1.06 (high), −1.00 (low) |
| **Both** | **−0.63** | −0.66 (high), −0.63 (low) | −0.69 (high), −0.64 (low) |

These match the figures in Nigel's branch review (−0.634 in 2024; −0.692 and
−0.636 in 2035). No other segment changes.

## Overlaps and double counting

Model diesel for 2024 by segment, against the evidence, billion litres:

| Model segment | Model, 2024 | Evidence | Overlap or gap |
|---|---|---|---|
| Road vehicles | 8.50 | Balance 2021: road 6.33; commercial and public services 4.30; the two together 10.63 | See "the commercial line" below. The model sits between the two readings |
| Agriculture | 1.06 | Balance 2021: 1.06 | The balance counts diesel sold to farming, which includes farm bakkies and trucks on public roads. Those are also in the model's registered fleet. Size unknown |
| Industry | 1.51 | Balance 2021: 1.50, of which mining 1.29, construction 0.05 | Mine haul trucks are not registered, so no overlap; mines' and contractors' road vehicles do overlap. Construction at 0.05 is too small to be all construction plant, so part sits in another line |
| Power generation | 3.58 | Eskom reported 0.94 (year to March 2023) and 0.68 (year to March 2025). Eskom and independent output of 5,143 GWh in the year to March 2024 is about 1.6 at 0.31 litres per kWh | Not an overlap: the model is at least 2 bn litres above reported burn, even against the peak year |
| Marine (gas oil) | 0.77 | No observed figure | Whether ships' diesel is inside recorded inland sales is not established |
| **Total** | **15.42** | Recorded sales: 12.91 (2023, department); 11.73 (2024, FIASA, unverified) | Model is 2.5–3.7 above recorded sales |

**The commercial line.** In the balances, "road" and "commercial and public
services" swap volume between years while their sum stays steady: 9.44, 9.37
and 9.36 in 2015–2017, then 10.22, 10.55, 9.49 and 10.63 in 2018–2021. In
2015 and 2017 commercial is near zero; in 2016 and 2018–2021 it is 3.6–5.0.
The split therefore reflects who bought the fuel, not where it was burned.
The same is likely true of the agriculture and mining lines.

**What this means for double counting.**

- The two sectors together are 2.56 bn litres, so that is the most that could
  be double counted against road vehicles.
- The totals do not show double counting. Road vehicles, agriculture and
  industry together are 11.07 in the model against 13.41 of final consumption
  in the 2021 balance. On that comparison the model is short by about 2.3,
  which is roughly the part of the commercial line not covered by road
  vehicles (private generators, construction plant, depots).
- The excess over recorded sales comes from power generation, not from these
  two sectors. With generation at about 1.6, the model total would be 13.4.

## Decisions for Nigel

1. Accept 1.06 (agriculture) and 1.50 (industry) as provisional starting
   values, or choose the activity-adjusted 1.40 for industry.
2. Whether to deduct an allowance for on-road use from the two sectors. No
   source sizes it; SARS diesel refund statistics would, and have not been
   obtained.
3. The power generation starting value, which is outside this priority but is
   the largest difference from the evidence.
4. Whether marine gas oil belongs inside the inland diesel total.

## Not done

- No allowance for on-road overlap is applied.
- The balances stop at 2021; no later sector split exists.
- The growth driver is still GDP per person for both sectors. Mining volume
  and agricultural output would fit better and are now in the inputs; that is
  a lever question, not a starting-value one.
