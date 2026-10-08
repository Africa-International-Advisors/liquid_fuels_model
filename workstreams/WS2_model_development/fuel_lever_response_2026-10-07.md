# Diesel, jet and petrol input tables: analyst response, 7 October 2026

Priority 2 on Manish's focus page (Convergence pack p24). Built by
`python -m lfm.scripts.build_fuel_lever_response --vintage 2026`; the same content, one row per
value, is in `fuel_lever_response_2026-10-07.csv`. Nigel's proposed inputs
(`assumptions/2026/timeseries/fuel_lever_design_2026_10_07.csv`) are not edited.

Of 120 proposed values, 39 have a replacement proposed here and 81 are left as they
are. Replacements are shown as proposed → **replacement**. Each baseline is computed from a
registered input and is an observation unless its basis says otherwise. Cases order the input
(low / medium / high), not the resulting demand. Nothing here is an accepted input.

9 levers are added by the analyst and are not in Nigel's file: real fuel price (diesel and
petrol), private backup generation, electric share of new truck and light commercial sales, plug-in
and conventional hybrids, rail passengers, and exports to neighbours. Their values are shown in bold
with no earlier value.

## Diesel

| Lever | Unit | Baseline | Baseline basis | 2030 low / medium / high | 2035 low / medium / high |
|---|---|---|---|---|---|
| road_activity | index_2024_100 | 100 | road freight payload 980 Mt in 2024 (Stats SA P7162) | 95 / 115 / 135 | 95 / 135 / 175 → **150** |
| rail_diversion | percent | 0 | rail 161 Mt and road 980 Mt in 2024 (Stats SA P7162) | 0 / 10 → **3** / 20 → **9** | 0 / 20 → **7** / 35 → **13** |
| ocgt_generation | index_FY2024_100 | 100 | Eskom and independent OCGT output 5,143 GWh, year to March 2024 | 10 / 25 / 60 | 5 / 15 / 50 |
| new_cohort_efficiency | percent_per_year | 0.5 to 1.0 | registered diesel efficiency paths (low and high demand cases) | 0.5 / 0.75 / 1 | 0.5 / 0.75 / 1 |
| plant_utilisation | percent | 67 | reported 2024 output over reported capacity, three plants; indicative | 60 / 75 / 90 | 60 / 75 / 90 |
| product_yield | percent | 29 | diesel share of refinery output in 2024 (JODI; lowest reliability) | 20 → **25** / 25 → **30** / 30 → **40** | 20 → **25** / 25 → **30** / 30 → **40** |
| restart_capacity | thousand_bbl_per_day | 0 | no committed addition | 0 / 0 / 0 | 0 / 0 / 400 |
| real_fuel_price | index_2024_100 | 100 | regulated inland price deflated by headline CPI, 2024 average | **80** / **100** / **140** | **80** / **100** / **140** |
| private_backup_generation | bn_litres_per_year | not measured | no measured volume exists | **0** / **0** / **0.5** | **0** / **0** / **0.5** |
| electric_share_of_new_truck_sales | percent | not reported | naamsa reports electrified sales for the whole market only; assumed close to zero | **0** / **0.4** / **3** | **0** / **3** / **9** |
| electric_share_of_new_light_commercial_sales | percent | not reported | naamsa reports electrified sales for the whole market only; assumed close to zero | **0** / **1** / **5** | **0** / **5** / **10** |

Evidence and rationale:

- **road_activity.** 2014-2024 growth 2.4% a year; fastest eleven years (2012-2023) 3.7%; 2025 is 99.5. The 2035 high of 175 needs 5.2% a year for eleven years, without precedent; 150 matches the fastest observed. In tonne-kilometres the only published road figure found is 221 bn for 2013 (Havenga et al. 2016, Logistics Barometer), an average haul of about 307 km against Stats SA's tonnes. No annual tonne-kilometre series exists, so the index stays on tonnes. Part of past growth was freight leaving rail, so this overlaps the rail lever.
- **rail_diversion.** In tonnes, as a share of 2024 road tonnes: rail back to its 2020 level (190 Mt) is 3%; back to its 2017 peak (225 Mt) is 7%; the 250 Mt target for 2029/30 (Draft National Rail Master Plan, April 2026) is 9%; the market appetite of about 280 Mt reported with that plan is 12%. In tonne-kilometres: rail-friendly general freight was 47 bn in 2019 and rail carried 18 bn (Freight Logistics Roadmap, 2023, p.38); the 29 bn left on road is 13% of road tonne-kilometres (2013 base). Both routes put the ceiling at 12-13%, so the 2035 high is 13 and the proposed 20 and 35 exceed all rail-friendly freight. The 2030 medium of 10 is the full official target, not a middle case.
- **ocgt_generation.** Year to March 2025 is 55 and year to March 2026 is 21 on this index, so the medium of 25 in 2030 holds today's level. Reported burn is 0.31 litres per kWh in three years. No change proposed.
- **new_cohort_efficiency.** Low and high equal the registered endpoints. Neither has a source. No change proposed.
- **plant_utilisation.** Secunda 53%, Natref 71%, Astron 84%. Output is all refined products against crude-equivalent capacity; Sasol's year ends June; Astron converted at an assumed 36 MJ a litre. The model's Secunda capacity was 75 thousand barrels a day and is now FIASA's 150, with utilisation re-based so output is unchanged; the model then gives 62 thousand barrels a day for 2024 against 80 reported.
- **product_yield.** Share of all refinery output: 31% in 2023 and 29% in 2024 (JODI). Before the Durban refineries closed, diesel was 40 to 42% of the five fuels in the 2017-2021 energy balances, which overstates its share of all output. The registered legacy yield is 25%. Replacement: legacy as the low, the recent observed share as the medium, the pre-closure share as the high. No plant-level slate is published.
- **restart_capacity.** Existing conditional illustration; no investment decision, timing or product slate is sourced.
- **real_fuel_price.** Annual range 2011-2025 is 76 to 120; October 2026 is 143. Low is the bottom of that range, medium a return to 2024, high October 2026 held. Boshoff (2012) puts the long-run response at -0.13, so the high case lowers demand by about 5%. One study; the model has no price response today.
- **private_backup_generation.** Recorded diesel sales fell by 1.2 bn litres between 2023 and 2024 as load-shedding ended; grid turbines account for about 0.7 of that at 0.31 litres per kWh, leaving about 0.5 that may be private generators. Indicative only: other causes are not excluded. High is load-shedding returning at 2023 intensity. Move together with diesel power generation.
- **electric_share_of_new_truck_sales.** No South African figure exists for electric trucks sold or on the road. Benchmarks, share of new truck sales in 2025: Brazil 0.4% (ICCT); India about 800 trucks, well under 1%; Europe 3%; world 9%; China 25%, which is over 90% of all electric trucks sold (IEA, Global EV Outlook 2026). Brazil and India are the closest comparators: long hauls, little purchase support. Low stays at zero; medium reaches Brazil's 2025 share by 2030 and Europe's by 2035; high reaches Europe's by 2030 and the world average by 2035. China is not used. The effect on diesel is small within the horizon: about 6% of trucks are replaced a year, so the high case puts roughly 2.5% of the fleet on electricity by 2035.
- **electric_share_of_new_light_commercial_sales.** No South African figure by segment. Benchmarks, share of new light commercial sales in 2025: India 1%, Europe 10%, China 14% (IEA, Global EV Outlook 2026). Low stays at zero; medium reaches India's 2025 share by 2030 and half of Europe's by 2035; high reaches half of Europe's by 2030 and Europe's by 2035. Light commercial vehicles are mostly bakkies here, which differ from the vans that dominate electric sales elsewhere, so these are loose comparators.

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
- **plant_utilisation.** Secunda 53%, Natref 71%, Astron 84%. Output is all refined products against crude-equivalent capacity; Sasol's year ends June; Astron converted at an assumed 36 MJ a litre. The model's Secunda capacity was 75 thousand barrels a day and is now FIASA's 150, with utilisation re-based so output is unchanged; the model then gives 62 thousand barrels a day for 2024 against 80 reported.
- **product_yield.** Jet was 5 to 8% of the five fuels produced in the 2017-2021 energy balances, consistent with the range. No change proposed.
- **restart_capacity.** Existing conditional illustration; no investment decision, timing or product slate is sourced.

## Petrol

| Lever | Unit | Baseline | Baseline basis | 2030 low / medium / high | 2035 low / medium / high |
|---|---|---|---|---|---|
| passenger_mileage | km_per_vehicle_year | 17000 | registered placeholder; not an observation | 13600 → **12900** / 17000 → **14500** / 20400 → **17000** | 13600 → **12900** / 17000 → **14500** / 20400 → **17000** |
| gdp_growth | percent_per_year | 0.5 | real GDP growth in 2024 (Stats SA P0441) | 1 → **0.7** / 2 → **1.6** / 3 → **2** | 1 → **0.7** / 2 → **1.6** / 3 → **2** |
| bev_new_sales_share | percent | 0.2 | 1,088 battery electric vehicles sold in 2025, share of all new vehicles (naamsa) | 5 → **0.5** / 15 → **4** / 30 → **20** | 15 → **2** / 35 → **15** / 60 → **40** |
| new_cohort_efficiency | percent_per_year | 1.0 to 1.5 | registered petrol efficiency paths (low and high demand cases) | 1 / 1.25 / 1.5 | 1 / 1.25 / 1.5 |
| plant_utilisation | percent | 67 | reported 2024 output over reported capacity, three plants; indicative | 60 / 75 / 90 | 60 / 75 / 90 |
| product_yield | percent | 54 | petrol share of refinery output in 2024 (JODI; lowest reliability) | 35 → **45** / 45 → **50** / 55 | 35 → **45** / 45 → **50** / 55 |
| restart_capacity | thousand_bbl_per_day | 0 | no committed addition | 0 / 0 / 0 | 0 / 0 / 400 |
| real_fuel_price | index_2024_100 | 100 | regulated inland price deflated by headline CPI, 2024 average | **80** / **100** / **120** | **80** / **100** / **120** |
| plug_in_hybrid_new_sales_share | percent | 0.5 | share of all new vehicles in 2025 (naamsa) | **0.5** / **1.2** / **2.1** | **0.5** / **2** / **3.7** |
| conventional_hybrid_new_sales_share | percent | 2.1 | share of all new vehicles in 2025 (naamsa) | **2.1** / **4.4** / **6.7** | **2.1** / **6.7** / **11.3** |
| rail_passenger_journeys | million_per_year | 74 | rail passenger journeys in 2024 (Stats SA P7162) | **100** / **180** / **320** | **100** / **250** / **320** |

Evidence and rationale:

- **passenger_mileage.** Stone et al. (2018) give 14,457 km a year for the petrol car fleet. 2023 petrol sales over 8.56 million registered petrol vehicles is 1,056 litres each, about 12,881 km at 8.2 litres per 100 km. The placeholder sits above both, so it is better treated as the high case.
- **gdp_growth.** Average growth was 0.7% a year over 2014-2024 and 1.6% over 2010-2019. National Treasury forecasts 1.6% for 2026 rising to 2.0% in 2028. The model's registered cases are 1.0% and 1.6%. A medium of 2% equals the top of the official forecast; 3% has no recent precedent.
- **bev_new_sales_share.** Battery electric sales fell from 1,257 in 2024 to 1,088 in 2025. No South African forecast was found; each case is tied to a market's observed 2025 share of new car sales (IEA, Global EV Outlook 2026). Low: South Africa stays under 1%, as in 2022-2025. Medium: India's share (nearly 4%) by 2030 and Indonesia's (15%) by 2035. High: Turkiye's path, from just over 1% in 2022 to over 20% in 2025, by 2030, and Vietnam's share (nearly 40%) by 2035. The IEA shares include plug-in hybrids, so they overstate battery electric alone. The proposed 2035 high of 60 is above every market cited.
- **new_cohort_efficiency.** Low and high equal the registered endpoints. Neither has a source. No change proposed.
- **plant_utilisation.** Secunda 53%, Natref 71%, Astron 84%. Output is all refined products against crude-equivalent capacity; Sasol's year ends June; Astron converted at an assumed 36 MJ a litre. The model's Secunda capacity was 75 thousand barrels a day and is now FIASA's 150, with utilisation re-based so output is unchanged; the model then gives 62 thousand barrels a day for 2024 against 80 reported.
- **product_yield.** Share of all refinery output: 51% in 2023 and 54% in 2024 (JODI). Petrol was 47 to 50% of the five fuels in the 2017-2021 energy balances. The registered legacy yield is 45%. Replacement: legacy as the low, 50 as the medium, the recent observed share as the high. Petrol and diesel yields must be chosen together; their highs cannot both hold.
- **restart_capacity.** Existing conditional illustration; no investment decision, timing or product slate is sourced.
- **real_fuel_price.** Annual range 2011-2025 is 79 to 109; October 2026 is 121. Low is the bottom of that range, medium a return to 2024, high October 2026 held. Boshoff (2012) puts the long-run response at -0.5, so the high case lowers demand by about 10%. One study; the model has no price response today.
- **plug_in_hybrid_new_sales_share.** Share rose from 0.02% in 2022 to 0.47% in 2025. Low holds 2025; medium adds the 2022-2025 average of 0.15 points a year; high adds the 2025 increase of 0.33 points a year. An extrapolation of South Africa's own sales, not a forecast. Enters through fuel use per kilometre; the share of distance on the battery is unsourced.
- **conventional_hybrid_new_sales_share.** Share rose from 0.77% in 2022 to 2.64% in 2024 and was 2.15% in 2025. Low holds 2025; medium adds the 2022-2025 average of 0.46 points a year; high adds twice that. An extrapolation of South Africa's own sales, not a forecast. Enters through fuel use per kilometre; the saving per vehicle is unsourced.
- **rail_passenger_journeys.** Journeys were 317 million in 2017 and 175 in 2019, fell to 19 in 2022 and recovered to 103 in 2025. Low holds 2025; medium returns to 2019 by 2030 and to 2018 by 2035; high returns to 2017 by 2030 and holds. More rail journeys lower petrol use, but no survey covers the minibus taxi and car trips displaced, so the effect in litres cannot yet be stated.

## Throughput for terminals (not South African demand)

| Lever | Unit | Baseline | Baseline basis | 2030 low / medium / high | 2035 low / medium / high |
|---|---|---|---|---|---|
| exports_to_neighbours | bn_litres_per_year | 1.48 | petrol and diesel exported to nine neighbouring countries in 2024 (SARS customs) | **0.7** / **1.4** / **1.7** | **0.7** / **1.4** / **1.7** |

Evidence and rationale:

- **exports_to_neighbours.** 2.66 bn litres in 2019, 1.73 in 2023 and 1.37 in 2025. Botswana took 1.05 in 2023 and 0.68 in 2025 and has said it is moving to Walvis Bay and Maputo. Low is 2025 with Botswana gone; medium holds 2025; high returns to 2023. This is throughput for South African terminals, not South African demand, and must not be added to it.
