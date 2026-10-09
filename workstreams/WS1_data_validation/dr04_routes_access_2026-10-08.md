# DR04 Routes and access: evidence, 8 October 2026

For Nigel's review. Answers request DR04 in
`output/delivered/investment_bridge_2026_10_08/data_request.csv` and milestone
M3: port and pipeline limits, route access, and matched delivered costs to the
same destinations. **Petrol and diesel only.**

Status: **the Durban to Gauteng pipeline route and the entry points are
documented, and the regulated cost of transport is known for every pricing
zone. Fuel tanker road and rail rates are not published.** 64 facts are read
from original documents or registered inputs, 6 are calculated, and 7 lines
are open. Each row holds one data point.

**Where to look:** the data requests workbook `output/delivered/Data_requests_DR01_DR04_DR07_DR08_2026_10_09.xlsx`.

- Sheet **DR04 routes and access**: every fact, grouped, with status, source, page and
  open gap. Open lines are yellow.
- Sheet **DR04 entry points**: petrol and diesel imports by customs office,
  2014 to 2025, in billion litres.
- Sheet **DR04 transport cost**: the Durban to Gauteng route element by
  element, then the regulated transport differential for all 54 pricing zones.

Evidence table behind the first sheet: `dr04_routes_access_evidence_2026-10-08.csv`.
Originals: `external/data/raw/routes_access_20261008/` (with a manifest of
addresses and checksums) and `external/data/raw/vopak_storage_20261006/`.

## Petrol and diesel only

The tables show only facts about petrol and diesel, or about the route itself
(a pipeline's capacity, a tariff, a site's connections). 27 facts that mix
in other products are kept in the evidence file, marked "other products
included", and are not shown: the port authority's liquid bulk tonnage (all
liquids, crude and chemicals included), Transnet's pipeline volumes (crude and
jet included) and its regulated revenue for the whole system.

## The pipeline from Durban to Gauteng

| Fact | Value | Source |
|---|---|---|
| Trunk line capacity | 148 million litres a week, as stated in 2020. This is the figure used | Transnet Pipelines 2020 report, PDF p.3 |
| The same, over a year | 7.7 bn litres (calculated; every week at full rate) | — |
| Inland accumulation at Jameson Park | 180 million litres, since December 2017 | Same |
| Products on the trunk line | Two diesel grades, two petrol grades, jet fuel | Same |
| Old Durban to Johannesburg line | Being decommissioned in 2020 | Same |

## What the pipeline costs

| Year | Tariff, Durban to Alrode, cents a litre | Basis |
|---|---|---|
| 2023/24 | 61.74 | NERSA statement of 15 March 2024, as quoted by Engineering News |
| 2024/25 | 67.99 | Same; a 10.13% increase |
| 2025/26 | 73.22 | Calculated: 67.99 plus the 5.23 increase in NERSA's statement of 15 April 2025 |
| 2026/27 | 77.02 | Calculated: plus a further 3.80 |

The two calculated years assume the increase NERSA states for the fuel price
is the change in this tariff, as it was in 2024/25. NERSA's own March 2024
statement and its reasons for decision were not located, so the first two
figures rest on a news report quoting the regulator word for word, and tariffs
on other routes are not available.

For comparison, the regulated diesel price is 79.0 cents a litre higher in
Gauteng than at the coast in July 2024 and 83.3 in July 2025 (department
prices). That is about 10 to 11 cents above the pipeline tariff in each year;
what the rest covers has not been established.

## Road and rail: what is and is not public

**Not public.** No haulier publishes a tanker rate, and Transnet Freight Rail
does not publish rates by commodity. No commercial road or rail rate for
petrol or diesel was found.

**Public: the regulated allowance for transport to every destination.** The
regulated price in each of the 54 pricing zones is the coastal price plus a
zone differential, which the department describes as the transport tariffs
for moving petrol and diesel "by means of the pipeline network and road
network". It is the nearest public figure to a delivered cost by destination.

| Regulated element, cents a litre | April 2014 | April 2024 | April 2026 | Source |
|---|---|---|---|---|
| Transport differential, Gauteng (zone 9C) | 33.1 | 82.8 | 91.1 | Department zone lists; Central Energy Fund price composition |
| Transport differential, coast (zone 1A) | 2.5 | 3.8 | — | Department zone lists |
| Transport differential, highest zone | 106.6 | 179.6 | — | Department zone lists |
| Secondary distribution (depot to service station by road) | — | 17.2 | 19.1 | Department diesel margins; Central Energy Fund |
| Secondary storage (depot) | — | 36.6 | 39.0 | Same |

The sheet lists all 54 zones with the districts in each. Three points:

- The Gauteng differential (82.8 in April 2024) is 14.8 cents above the pipeline
  tariff for the same year (67.99). What the rest covers is not established.
- Secondary storage, 39 cents a litre, is the regulated allowance for depot
  storage, which is the service an inland terminal sells.
- These are allowances in the price. They are not what a shipper pays, and
  the files do not say which mode serves each zone.

**One industry statement.** The managing director of a fuel haulier told
Bloomberg in May 2025 that fuel sent by pipeline and then trucked the last
stretch costs "about a third higher than transporting it exclusively by road".
No rate was given. It suggests road competes with the pipeline; it is not a
measurement.

Staged as `assumptions/2026/reference/zone_differentials_department.csv` and
`zone_districts_department.csv` by `python -m lfm.scripts.stage_zone_differentials --vintage 2026`.

## Where petrol and diesel imports enter

Billion litres, petrol and diesel together, SARS customs by office of clearance:

| Entry point | 2023 | 2024 | 2025 | Share in 2025 |
|---|---|---|---|---|
| Durban | 13.29 | 11.84 | 13.16 | 78.8% |
| Cape Town | 1.62 | 1.09 | 1.52 | 9.1% |
| Richards Bay | 0.32 | 0.39 | 0.66 | 3.9% |
| Mossel Bay | 1.16 | 0.62 | 0.52 | 3.1% |
| East London | 0.36 | 0.53 | 0.43 | 2.6% |
| Port Elizabeth | 0.34 | 0.14 | 0.32 | 1.9% |
| Komatipoort (road, from Mozambique) | 0.25 | 0.19 | 0.09 | 0.5% |
| All offices | 17.35 | 14.79 | 16.70 | 100% |

The sheet gives diesel and petrol separately from 2014. In 2025 Durban cleared
73% of diesel imports and 95% of petrol imports.

## Competing routes

| Route | What the record shows | Source |
|---|---|---|
| Maputo and Matola, by road through Komatipoort | Diesel: 0.27 bn litres in 2022, 0.19 in 2024, 0.08 in 2025. Petrol: 0.029 in 2022, almost nil since 2023. Together 0.5% of imports in 2025 | SARS customs |
| Walvis Bay, by the Trans-Kalahari road | No petrol or diesel is recorded entering through the Namibian or Botswanan border posts in any year from 2019 to 2025 | SARS customs |
| Walvis Bay storage | 45 million litres of diesel and 20 of petrol planned, built for Namibia's own supply | Namibian Ports Authority news item, undated |
| Other South African ports | Cape Town 1.52, Richards Bay 0.66, Mossel Bay 0.52, East London 0.43, Port Elizabeth 0.32 bn litres in 2025 | SARS customs |
| Inland supply from Natref and Secunda | Not started; no production by product after 2021 | DR08 |

Reading: on the customs record, Durban is by far the largest entry point, and
the two routes that bypass South African ports barely feature. The Mozambique
road route is small and has shrunk by two thirds since 2022, and the Namibian
route is not used at all. Richards Bay is
the one entry point that is growing, from 0.32 to 0.66 bn litres between 2023
and 2025. This says where fuel entered, not what each route would cost, and
it does not cover fuel that Maputo or Walvis Bay supply to neighbouring
countries which South African terminals might otherwise serve.

## Access at the two Vopak sites

| Site | Receives by | Dispatches by | Source |
|---|---|---|---|
| Lesedi, Jameson Park | Four pipelines from the Transnet system; intake is from the Transnet pipeline | Eight road loading bays | NERSA reasons for decision, February 2026, PDF pp.6-7 |
| Durban, Island View | Ship (own lines at jetties 1, 2 and 4; industry lines at berths 6, 7 and 8) and pipeline transfer from neighbours | Mainly road; also ship, barge and pipeline transfer | Vopak's allocation mechanism filed with NERSA, pp.4-6 (an old, undated document) |

The regulator records that Lesedi's contracted customers, with one exception,
are shippers on the Transnet pipeline from Durban (2024/25). Durban has 8
liquid bulk berths and Richards Bay 2 (port authority's Our Ports page).

## One comparison worth Nigel's attention, not a finding

Durban cleared 13.2 bn litres of petrol and diesel imports in 2025. The trunk
line's stated capacity works out at about 7.7 bn litres a year, and it also
carries jet fuel. If the capacity figure is still right, close to half of the
petrol and diesel landed at Durban cannot go inland by pipeline and must be
used on the coast or move by road or rail. The capacity figure is from 2020,
so this is a lead to check, not a conclusion.

## Added on 9 October: the regulated transport cost to Gauteng by year

The department's yearly price tables give the transport cost in the Gauteng price month by month from January
2012 to April 2024. Cents a litre, as it stood at the end of each year (it is reset each April):

| 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | April 2024 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 26.8 | 28.9 | 33.1 | 35.3 | 41.0 | 41.5 | 51.7 | 57.4 | 63.7 | 64.9 | 64.9 | 75.7 | 75.7 |

Diesel table shown; the petrol table is the same except 2014 (28.9 all year) and December 2022 (67.9). It almost
trebled in eleven years. Staged as `reference/transport_cost_gauteng_department.csv` by
`python -m lfm.scripts.stage_fuel_price_margins --vintage 2026 --fetch`.

Two cautions. The April 2024 table shows 75.7 while the zone list of the same month shows 82.8; both are kept and
the difference is not explained. Eight months are unreadable in the department's tables and are left out.

## Added on 9 October: a second search of official sources

Sources: Parliament's committee report on Island View (11 March 2026), NERSA's licence decisions, Transnet's rail
tariff proposal, Stats SA's land transport survey and Galp.

| Gap | What was found | Source |
|---|---|---|
| Road and rail rates | No fuel rate. Transnet's own comparison for containers: road 1.23 and rail 0.43 rand per net tonne-kilometre (2025). Track access for tankers: 30 rand per train-kilometre plus 6.96 cents per gross tonne-kilometre | Transnet Rail Infrastructure Manager, Tariff Proposal 2025/26 |
| Road and rail rates | Average income per tonne carried, all goods: road 205 and rail 272 rand in 2025 | Stats SA, Land transport survey |
| Island View | 10 berths, 10 operators (Vopak included). No capacity figure for petrol and diesel | Parliament |
| Pipeline use | About 70% of capacity, all products | Minister of Transport to Parliament |
| Direct injection | The former Sapref site and Sasol both inject straight into the pipeline. Vopak says it works with Transnet on pipeline evacuation but does not say how it connects | NERSA; Parliament |
| Island View leases | All ten leases to be renewed for 25 years, with third-party access and more pipeline use required | Parliament |
| Matola storage | One terminal: 40,000 m3 diesel and 20,000 m3 petrol | Galp |

None of these is a fuel tanker rate, so the delivered-cost comparison is still not built.

## Added on 9 October: the trunk line today, and the open lines of Nigel's task 5

**Trunk line capacity and use (task 6).** Transnet's Pipelines Report 2024 (KPI table, PDF p.5) still gives the
multi-product pipeline a capacity of 148 million litres a week, the 2020 figure, and reports use against it:

| Year to March | 2021 | 2022 | 2023 | 2024 | 2025 target |
|---|---|---|---|---|---|
| Use, million litres a week | 81 | 91 | 87 | 97 | 104 |

So the line was about two thirds full in the year to March 2024: 5.0 billion litres a year against a capacity of 7.7.
No later report was found.

**Task 5, line by line.**

| Open line | Result | Source, or where I looked |
|---|---|---|
| Petrol and diesel on the trunk line | Not split by product. All refined products on the line: 5.0 billion litres (year to March 2024). Petrol and diesel on every Transnet line: 9.5 billion litres | Transnet Pipelines Report 2024, PDF p.5 |
| NERSA's reasons for decision; tariffs beyond Durban to Alrode | Not available | NERSA's decisions pages (petroleum pipelines, tariff decisions), its 2024/25 annual report and the 15 April 2025 statement. Only Durban to Alrode is quoted |
| Zone differentials after April 2024 | Gauteng only: 87.1 cents a litre from June 2025 and 91.1 from April 2026. The full zone list after April 2024 was not found | Central Energy Fund price releases, p.3 |
| The gap between tariff and regulated differential | About 14 cents a litre in each of 2024/25, 2025/26 and 2026/27 (82.8, 87.1, 91.1 against 67.99, 73.22, 77.02). What it pays for is not itemised anywhere found | Department price tables and the releases above. The 2025 release shows differentials are rebuilt from the pipeline tariff to each zone's supply point |
| Matched delivered cost to the same destination | Not available. Pipeline: 77.02 (tariff) or 91.1 (allowance). No fuel tanker or rail rate is published | Transnet's tariff proposal, Stats SA, NERSA, Parliament |

**What the pipeline tariff covers (call of 9 October).** NERSA sets one set of tariffs for Transnet's whole licensed
petroleum pipelines system. The department uses the Durban to Alrode tariff as its proxy for moving fuel from Durban to
Johannesburg. The statement does not say which products or line each route tariff applies to; that detail is in the
reasons for decision, which are not online. Nigel to validate next week, as agreed.

## Open, by owner

| Gap | Owner | What would close it |
|---|---|---|
| Petrol and diesel volumes on the trunk line | Manish | A Transnet or NERSA document that splits volumes by line and product |
| Pipeline tariff on routes other than Durban to Alrode; NERSA's own statements | Manish | NERSA's reasons for decision; not located |
| What makes up the 10 to 11 cents between the tariff and the regulated price difference | Manish | The department's price structure by zone |
| Petrol and diesel through each port, by terminal | Nigel to coordinate | The port authority's statistics are all liquids in tons; a product split needs the authority or terminal operators |
| Island View capacity and tankage for petrol and diesel | Nigel to coordinate | Port authority or Vopak; Parliament's report gives berths and operators only |
| Fuel tanker road and rail rates, Durban to Gauteng and Matola to Gauteng | Nigel to coordinate | Vopak, a haulier or Transnet Freight Rail; only container and all-goods figures are published |
| Zone differentials after April 2024, and which mode serves each zone | Manish | The department's current zone schedule; its site did not respond on 8 October |
| How Vopak Durban connects to the trunk line (own lines or through a neighbour) | Nigel to coordinate | Vopak operations; two neighbours inject directly |
| Fuel that Maputo and Walvis Bay supply to neighbours | Manish | Not found for petrol and diesel alone. Matola terminals other than Galp's are not pursued (Manish, 9 October) |
| Inland supply from Natref and Secunda | Manish | DR08 |
| Matched delivered cost to the same destination | Manish, once the above are in | Same product, date, destination and tax basis for each route |

## Checks

- Every "observed" row was read from the original document named, at the page
  given, or computed from a registered input.
- The entry points sheet adds to national customs imports for each fuel in
  every year (tested).
- A first version of the two Mozambique road rows dropped years in which the
  Komatipoort office cleared fuel in fewer than twelve months; corrected
  before commit.
- No model input read by the engine changed; model results are unchanged.
