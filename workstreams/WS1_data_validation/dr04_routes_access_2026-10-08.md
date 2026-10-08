# DR04 Routes and access: evidence so far, 8 October 2026

For Nigel's review. Answers request DR04 in
`output/delivered/investment_bridge_2026_10_08/data_request.csv` and milestone
M3: port and pipeline limits, route access, and matched delivered costs to the
same destinations.

Status: **started; the Durban to Gauteng pipeline route is documented, the
rest is not.** 45 facts are taken from original documents, 2 are calculated,
and 8 lines are open. No matched delivered-cost comparison is possible yet.

**Where to look:** the workbook `output/delivered/Demand_baseline_workshop_2026_10_08_history.xlsx`,
sheet **DR04 routes** (every fact, grouped, with source, page and open gap; open
lines in yellow) and sheet **DR04 ports** (liquid bulk landed at each port by
calendar year and by month).

Evidence table: `dr04_routes_access_evidence_2026-10-08.csv`, one row per
fact, with its source, the original file, the page and the open gap.
Originals: `external/data/raw/routes_access_20261008/` (with a manifest of
addresses and checksums) and `external/data/raw/vopak_storage_20261006/`.

## What the documents establish

**The pipeline from Durban to Gauteng**

| Fact | Value | Source |
|---|---|---|
| Trunk line capacity | 148 million litres a week, as stated in 2020 | Transnet Pipelines 2020 report, PDF p.3 |
| The same, over a year | 7.7 bn litres (calculated; every week at full rate) | — |
| Inland accumulation at Jameson Park | 180 million litres, since December 2017 | Same |
| Products | Two diesel grades, two petrol grades, jet fuel | Same |
| Old Durban to Johannesburg line | Being decommissioned in 2020 | Same |
| Volumes on all Transnet petroleum lines | 17.8 bn litres (year to March 2020); 15.2 (2024); 13.4 (2025) | 2020 report; Transnet Integrated Report 2025, PDF p.26 |
| Share of inland refined product by pipeline | More than 70%, as stated in 2020 | 2020 report |

**What the pipeline costs**

| Fact | Value | Source |
|---|---|---|
| Revenue the regulator allows | R7.2 bn (2024/25), R7.8 bn (2025/26), R8.3 bn (2026/27) | NERSA media statement, 15 April 2025 |
| Effect on the fuel price | +5.23 cents a litre in 2025/26, +3.80 in 2026/27 | Same |
| Regulated price difference, Gauteng less coast, diesel | 79.0 cents a litre (July 2024), 83.3 (July 2025) | Department's regulated prices, already held |

The regulator says it uses the pipeline tariff "as a proxy for the cost of
transporting fuel from Durban to Johannesburg". The price difference between
the coast and Gauteng is therefore the nearest public figure for the regulated
cost of the route, about 83 cents a litre for diesel. It is an allowance in
the price, not what a shipper pays a haulier or Transnet.

**Where imports enter**

| Customs office | 2024, bn litres | 2025 | Share in 2025 |
|---|---|---|---|
| Durban | 11.84 | 13.16 | 78.8% |
| Cape Town | 1.09 | 1.52 | 9.1% |
| Richards Bay | 0.39 | 0.66 | 3.9% |
| Komatipoort (road, from Mozambique) | 0.19 | 0.09 | 0.5% |
| All offices | 14.79 | 16.70 | 100% |

Petrol and diesel together, SARS customs. The office is where goods were
cleared, not a berth or terminal record.

**Liquid bulk through the ports**

| Fact | Value | Source |
|---|---|---|
| Liquid bulk handled, all ports, years to March | 41.9 (2020), 41.8 (2021), 38.1 (2022), 35.5 (2023), 38.9 (2024) million kilolitres | Port authority reports 2023 and 2024, PDF p.9 |
| Target for the year to March 2025 | 34.6 million kilolitres | 2024 report |
| Planned at Island View, Durban | Berth 1 rebuilt and Berth 3 converted from dry bulk to liquid bulk, both dated 2026 | Port authority tariff application slides, September 2025, PDF p.14 |
| Planned at Richards Bay | New liquid bulk berth 210 and the South Dunes liquid bulk development | Same, PDF pp.11-12 |

Those volumes are all eight ports and all liquids together.

**Liquid bulk by port (port statistics, calendar years, million tons)**

| Port | Landed 2024 | Landed 2025 | All movements 2025 |
|---|---|---|---|
| Durban | 19.88 | 20.70 | 22.42 |
| Saldanha | 5.31 | 5.12 | 5.12 |
| Richards Bay | 1.76 | 2.16 | 3.51 |
| Cape Town | 1.43 | 1.90 | 3.49 |
| East London | 0.57 | 0.52 | 1.23 |
| Mossel Bay | 0.69 | 0.49 | 0.51 |
| Port Elizabeth | 0.16 | 0.32 | 0.85 |
| Ngqura | 0.04 | 0.06 | 0.06 |
| All eight ports | 29.84 | 31.27 | 37.19 |

Durban landed 66% of all liquid bulk by weight in 2025 and has 8 liquid bulk berths; Richards Bay
has 2. The statistics are in tons and cover every liquid (crude oil, fuels, gas
and chemicals), so they do not give fuel litres. Source: the port authority's
port statistics and Our Ports page at https://www.transnet.net/TNPA.

**Monthly series.** The port authority publishes a summary for each month from
July 2024. All 26 months to August 2026 were downloaded; 25 are usable.
Durban landed between 1.23 and 2.46 million tons a month, 1.69 on average.
Three of the publisher's files are wrong or odd, and none is filled in:

| Month | Problem | Treatment |
|---|---|---|
| January 2025 | The link leads to a container report | No figures; shown as not published |
| April 2026 | The heading says cargo invoiced, not handled | Kept, with a note |
| May 2026 | The heading says May 2025, but the figures differ from May 2025 | Kept as May 2026, with a note |

Staged as `assumptions/2026/timeseries/port_liquid_bulk_tnpa.csv` by
`python -m lfm.scripts.stage_tnpa --vintage 2026 --fetch`; originals in
`external/data/raw/tnpa/`.

**Access at the two Vopak sites**

| Site | Receives by | Dispatches by | Source |
|---|---|---|---|
| Lesedi, Jameson Park | Four pipelines from the Transnet system; intake is from the Transnet pipeline | Eight road loading bays | NERSA reasons for decision, February 2026, PDF pp.6-7 |
| Durban, Island View | Ship (own lines at jetties 1, 2 and 4; industry lines at berths 6, 7 and 8) and pipeline transfer from neighbours | Mainly road; also ship, barge and pipeline transfer | Vopak's allocation mechanism filed with NERSA, pp.4-6 (an old, undated document) |

The regulator records that Lesedi's contracted customers, with one exception,
are shippers on the Transnet pipeline from Durban (2024/25).

## One comparison worth Nigel's attention, not a finding

Durban cleared 13.2 bn litres of petrol and diesel imports in 2025. The
trunk line's stated capacity works out at about 7.7 bn litres a year, and
all Transnet petroleum lines together moved 13.4 bn litres in the year to
March 2025, crude included. If those figures are right and current, a large
part of what lands at Durban cannot go inland by pipeline and must be used on
the coast or move by road or rail. The capacity figure is from 2020 and the
volumes include crude, so this is a lead to check, not a conclusion.

## Open, by owner

| Gap | Owner | What would close it |
|---|---|---|
| Pipeline tariff by route (Durban to Alrode and others), cents a litre | Manish | NERSA's reasons for decision on the 2025-27 tariffs |
| Today's trunk line capacity, and refined product volumes on it | Manish | A later Transnet or NERSA document; the 2020 figure is the latest found |
| Liquid-bulk capacity in kilolitres and tankage at Island View and Richards Bay | Manish | The port authority's Durban brochure and framework plan; not on its pages at transnet.net/TNPA. Ask the authority or Vopak |
| Fuel by product through each port | Nigel to coordinate | The port statistics are tons of all liquids; a product split needs the port authority or terminal operators |
| Road and rail rates, Durban to Gauteng | Nigel to coordinate | Vopak, a haulier or Transnet Freight Rail; none is public |
| Whether Vopak Durban can inject into the trunk line directly | Nigel to coordinate | Vopak operations |
| Maputo and Matola, Walvis Bay, and inland supply from Natref and Secunda | Manish | Not started |
| Matched delivered cost to the same destination | Manish, once the above are in | Same product, date, destination and tax basis for each route |

## Not used

Figures seen only in search summaries are recorded in the evidence table as
"not verified" and are not used: Durban's liquid-bulk capacity of 19.5 million
kilolitres a year with 10 berths and 962 tanks, and Richards Bay's two berths
and 3 million kilolitres a year. The port authority's site did not respond, so
the original documents could not be opened.

## Checks

- Every "observed" row was read from the original document named, at the page
  given.
- Import and price figures are computed from registered inputs already held.
- No model input changed; model results are unchanged.
