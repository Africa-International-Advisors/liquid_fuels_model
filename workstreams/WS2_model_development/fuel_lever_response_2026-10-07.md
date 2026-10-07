# Diesel, jet and petrol input tables: analyst response, 7 October 2026

Priority 2 on Manish's focus page (Convergence pack p24). Built by
`python -m lfm.scripts.build_fuel_lever_response --vintage 2026`; the same content, one row per
value, is in `fuel_lever_response_2026-10-07.csv`. Nigel's proposed inputs
(`assumptions/2026/timeseries/fuel_lever_design_2026_10_07.csv`) are not edited.

Of 120 proposed values, 29 have a replacement proposed here and 91 are left as they
are. Replacements are shown as proposed → **replacement**. Each baseline is computed from a
registered input and is an observation unless its basis says otherwise. Cases order the input
(low / medium / high), not the resulting demand. Nothing here is an accepted input.

## Diesel

| Lever | Unit | Baseline | Baseline basis | 2030 low / medium / high | 2035 low / medium / high |
|---|---|---|---|---|---|
| road_activity | index_2024_100 | 100 | road freight payload 980 Mt in 2024 (Stats SA P7162) | 95 / 115 / 135 | 95 / 135 / 175 → **150** |
| rail_diversion | percent | 0 | rail 161 Mt and road 980 Mt in 2024 (Stats SA P7162) | 0 / 10 → **3** / 20 → **9** | 0 / 20 → **7** / 35 → **15** |
| ocgt_generation | index_FY2024_100 | 100 | Eskom and independent OCGT output 5,143 GWh, year to March 2024 | 10 / 25 / 60 | 5 / 15 / 50 |
| new_cohort_efficiency | percent_per_year | 0.5 to 1.0 | registered diesel efficiency paths (low and high demand cases) | 0.5 / 0.75 / 1 | 0.5 / 0.75 / 1 |
| plant_utilisation | percent | 67 | reported 2024 output over reported capacity, three plants; indicative | 60 / 75 / 90 | 60 / 75 / 90 |
| product_yield | percent | 25 | registered legacy yield; share of throughput, not observed | 20 / 25 / 30 | 20 / 25 / 30 |
| restart_capacity | thousand_bbl_per_day | 0 | no committed addition | 0 / 0 / 0 | 0 / 0 / 400 |

Evidence and rationale:

- **road_activity.** Tonnes, not tonne-kilometres. 2014-2024 growth 2.4% a year; fastest eleven years (2012-2023) 3.7%; 2025 is 99.5. The 2035 high of 175 needs 5.2% a year for eleven years, without precedent; 150 matches the fastest observed. Part of past growth was freight leaving rail, so this overlaps the rail lever.
- **rail_diversion.** As a share of 2024 road tonnes: rail back to its 2020 level (190 Mt) is 3%; back to its 2017 peak (225 Mt) is 7%; Transnet's 250 Mt target for 2029/30 met in full is 9%. The proposed 2030 medium of 10% is therefore the full target, and 20% would put rail far above its peak. The 2035 high of 15% has no source. Tonnes understate rail's share of tonne-kilometres.
- **ocgt_generation.** Year to March 2025 is 55 and year to March 2026 is 21 on this index, so the medium of 25 in 2030 holds today's level. Reported burn is 0.31 litres per kWh in three years. No change proposed.
- **new_cohort_efficiency.** Low and high equal the registered endpoints. Neither has a source. No change proposed.
- **plant_utilisation.** Secunda 53%, Natref 71%, Astron 84%. Output is all refined products against crude-equivalent capacity; Sasol's year ends June; Astron converted at an assumed 36 MJ a litre. The model's registered Secunda nameplate is 75 thousand barrels a day; FIASA reports 150.
- **product_yield.** Energy balances report 0.84 to 0.87 litres of diesel per litre of petrol (2017-2021); the legacy yields imply 0.56. JODI gives 0.61 and 0.53 for 2023 and 2024 at its lowest reliability. The evidence does not settle a value; set diesel and petrol yields together, by plant. No change proposed.
- **restart_capacity.** Existing conditional illustration; no investment decision, timing or product slate is sourced.

## Jet

| Lever | Unit | Baseline | Baseline basis | 2030 low / medium / high | 2035 low / medium / high |
|---|---|---|---|---|---|
| aircraft_movements | index_2024_100 | 100 | 456,214 movements at ACSA airports in 2024 | 100 / 120 → **110** / 140 → **125** | 100 / 145 → **120** / 190 → **140** |
| fuel_burn_per_movement | index_2024_100 | 100 | 4,090 litres of jet sold per movement in 2024 | 80 / 90 / 100 → **113** | 65 / 80 / 100 → **113** |
| saf_volume_share | percent | 0 | no sustainable aviation fuel supply recorded in the sources held; unsourced | 0 / 2 / 5 | 0 / 5 / 10 |
| plant_utilisation | percent | 67 | reported 2024 output over reported capacity, three plants; indicative | 60 / 75 / 90 | 60 / 75 / 90 |
| product_yield | percent | 10 | registered legacy yield for capable plants | 5 / 10 / 15 | 5 / 10 / 15 |
| restart_capacity | thousand_bbl_per_day | 0 | no committed addition | 0 / 0 / 0 | 0 / 0 / 400 |

Evidence and rationale:

- **aircraft_movements.** 2019 was 112 and the peak, 2016, was 125 on this index; 2025 is 101.3. Movements fell 0.1% a year over 2013-2019. The proposed highs (140 and 190) are above every year on record. Replacement: medium returns to the 2019 level by 2030, high to the 2016 peak; 2035 extends each.
- **fuel_burn_per_movement.** The 2013-2019 average was 4,608 litres, 113 on this index. Jet sales have recovered less than movements since 2020, for reasons not yet established (aircraft mix, fuel loaded abroad, or sales coverage). The proposed range only falls; the high case should allow a return to the earlier intensity.
- **saf_volume_share.** No South African blend requirement is sourced. No change proposed.
- **plant_utilisation.** Secunda 53%, Natref 71%, Astron 84%. Output is all refined products against crude-equivalent capacity; Sasol's year ends June; Astron converted at an assumed 36 MJ a litre. The model's registered Secunda nameplate is 75 thousand barrels a day; FIASA reports 150.
- **product_yield.** Jet was 5 to 8% of the five fuels produced in the 2017-2021 energy balances, consistent with the range. No change proposed.
- **restart_capacity.** Existing conditional illustration; no investment decision, timing or product slate is sourced.

## Petrol

| Lever | Unit | Baseline | Baseline basis | 2030 low / medium / high | 2035 low / medium / high |
|---|---|---|---|---|---|
| passenger_mileage | km_per_vehicle_year | 17000 | registered placeholder; not an observation | 13600 → **12900** / 17000 → **14500** / 20400 → **17000** | 13600 → **12900** / 17000 → **14500** / 20400 → **17000** |
| gdp_growth | percent_per_year | 0.5 | real GDP growth in 2024 (Stats SA P0441) | 1 → **0.7** / 2 → **1.6** / 3 → **2** | 1 → **0.7** / 2 → **1.6** / 3 → **2** |
| bev_new_sales_share | percent | 0.2 | 1,088 battery electric vehicles sold in 2025, share of all new vehicles (naamsa) | 5 → **0.5** / 15 → **3** / 30 → **10** | 15 → **2** / 35 → **10** / 60 → **30** |
| new_cohort_efficiency | percent_per_year | 1.0 to 1.5 | registered petrol efficiency paths (low and high demand cases) | 1 / 1.25 / 1.5 | 1 / 1.25 / 1.5 |
| plant_utilisation | percent | 67 | reported 2024 output over reported capacity, three plants; indicative | 60 / 75 / 90 | 60 / 75 / 90 |
| product_yield | percent | 45 | registered legacy yield; share of throughput, not observed | 35 / 45 / 55 | 35 / 45 / 55 |
| restart_capacity | thousand_bbl_per_day | 0 | no committed addition | 0 / 0 / 0 | 0 / 0 / 400 |

Evidence and rationale:

- **passenger_mileage.** Stone et al. (2018) give 14,457 km a year for the petrol car fleet. 2023 petrol sales over 8.56 million registered petrol vehicles is 1,056 litres each, about 12,881 km at 8.2 litres per 100 km. The placeholder sits above both, so it is better treated as the high case.
- **gdp_growth.** Average growth was 0.7% a year over 2014-2024 and 1.6% over 2010-2019. National Treasury forecasts 1.6% for 2026 rising to 2.0% in 2028. The model's registered cases are 1.0% and 1.6%. A medium of 2% equals the top of the official forecast; 3% has no recent precedent.
- **bev_new_sales_share.** Battery electric sales fell from 1,257 in 2024 to 1,088 in 2025. The policy target of 20% of sales by 2025 was missed by a wide margin. Electric cars were over 6% of sales in Brazil and 9% across Southeast Asia in 2024 (International Energy Agency). The proposed low of 5% by 2030 is a 27-fold rise in five years. Replacement: low continues near today, medium reaches Brazil's 2024 level by about 2032, high follows Southeast Asia. Hybrids are excluded here and enter through fuel use per kilometre.
- **new_cohort_efficiency.** Low and high equal the registered endpoints. Neither has a source. No change proposed.
- **plant_utilisation.** Secunda 53%, Natref 71%, Astron 84%. Output is all refined products against crude-equivalent capacity; Sasol's year ends June; Astron converted at an assumed 36 MJ a litre. The model's registered Secunda nameplate is 75 thousand barrels a day; FIASA reports 150.
- **product_yield.** Petrol was 47 to 50% of the five fuels produced in the 2017-2021 energy balances; as a share of all throughput it would be lower. Set together with the diesel yield, by plant. No change proposed.
- **restart_capacity.** Existing conditional illustration; no investment decision, timing or product slate is sourced.
