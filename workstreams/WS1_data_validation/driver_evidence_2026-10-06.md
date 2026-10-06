# Driver evidence — 6 October 2026 (work package 5)

Investigated by Manish on `manish-branch`; for Nigel's review. Supports pack
pages 7 and 8. One row per series, following handover PDF page 7. Activity
series are not fuel litres and no lever has been quantified. Nothing under
`assumptions/2026/` was changed.

Status key: **sourced** = original, extract, coverage and units in hand;
**partial** = some of those missing or the series is short; **open** = not
obtained, with owner and next action.

Extract paths are under `assumptions/2026/`; where each original is held is in
`source_trace_2026-10-06.csv`.

## Checklist

| Driver | Series | Source and table | Extract | Coverage | Units | Revision check | Status |
|---|---|---|---|---|---|---|---|
| Passenger vehicles | Cars and minibuses on the road, by province | NaTIS live vehicle population, monthly | `timeseries/vehicle_population_natis.csv` | Feb 2021 – Jun 2026 | vehicles | Dates repeated within a file are dropped, not guessed | Sourced |
| | New registrations by class | NaTIS new registrations, monthly | `timeseries/new_vehicle_registrations_natis.csv` | May 2016 – Jun 2026 | vehicles | As above | Sourced |
| | Petrol/diesel split of the fleet | DoT Transport Statistics Bulletin 2023, Table 2.8 (totals only) | `reference/vehicle_population_by_fuel_dot2023.csv`; derived split in `reference/fleet_fuel_split_2023.csv` | December 2023 only | vehicles | Single edition | Partial: split by class is an estimate |
| | Distance and fuel use | Stone et al. 2018, JESA 29(2) | `reference/vehicle_parameters_stone2018.csv` | 2014 values | km/year; L/100 km | Typed by hand; not re-checked | Partial: nothing newer found |
| Freight | Light commercial vehicles, trucks, buses on the road | NaTIS, as above | `timeseries/vehicle_population_natis.csv` | Feb 2021 – Jun 2026 | vehicles | As above | Sourced |
| | Road and rail payload | Stats SA P7162 Land transport, December 2025 release, p.7 | `timeseries/freight_payload_statssa_review.csv` | 2024, 2025 | thousand tonnes | 2024 road revised 790.6 → 979.8 Mt between the December 2024 and 2025 releases; one release used | Partial: two years only |
| | Tonne-kilometres | — | — | — | — | — | Open: P7162 reports payload and income, not tonne-km |
| Agriculture | Agriculture, forestry and fishing, real value added | Stats SA P0441 GDP time series, Q2 2026, Annual sheet, code AR1001 | `timeseries/macro_statssa.csv` | 1993–2025 | rand, constant 2015 prices | One release vintage | Sourced |
| | Diesel used by agriculture | Department energy balances | `timeseries/energy_balance_department.csv` | 2007–2021 | litres | 2016–2017 are about double the other years | Partial: ends 2021; definition break |
| Industry | Manufacturing, real value added | P0441, code AR1003 | `timeseries/macro_statssa.csv` | 1993–2025 | rand, constant 2015 prices | One release vintage | Sourced |
| | Mining and quarrying, real value added | P0441, code AR1002 | `timeseries/macro_statssa.csv` | 1993–2025 | rand, constant 2015 prices | One release vintage | Sourced |
| | Manufacturing production volume index | Stats SA P3041.2 | — | — | — | — | Open: needs manual download |
| | Mining production volume index | Stats SA P2041 | — | — | — | — | Open: needs manual download |
| | Diesel used by industry and mining | Department energy balances | `timeseries/energy_balance_department.csv` | 2007–2021 | litres | Sector boundaries shift in 2016 | Partial: ends 2021 |
| Power | Gas turbine output, Eskom and independent producers | Eskom integrated reports, years to March | `timeseries/ocgt_generation_eskom.csv` | FY2022–FY2026 (Eskom); FY2023–FY2026 (combined) | GWh | Overlapping years agree across reports (none revised) | Sourced |
| | Diesel burned, litres | Minister of Public Enterprises, replies reported in the press (Eskom's own turbines) | Not extracted | FY2022: 571 ML; FY2023: 937.5 ML | litres | Press reports of parliamentary replies; primary replies not retrieved | Partial: two years; see follow-up |
| Electrification | Battery electric, plug-in hybrid and hybrid new sales | naamsa quarterly reviews | `timeseries/nev_sales_naamsa.csv` | 2019–2025 | vehicles | Warnings reviewed 6 October: all relate to superseded editions; final values match the latest year-end review exactly | Sourced |
| | Electric vehicles in the fleet | DoT bulletin Table 2.8: 4,090 electric at December 2023 | `reference/vehicle_population_by_fuel_dot2023.csv` | December 2023 only | vehicles | The same table shows 6 hybrids, which cannot be right | Partial |
| Economic context | Real GDP and GDP per person | P0441 (code AR1000) and P0302 population | `timeseries/macro_statssa.csv` | 1993–2025; population to 2026 | rand, constant 2015 prices; persons | One release vintage; years after 2026 are projections | Sourced |
| | Growth forecast | National Treasury Budget Review 2026, chapter 2 | `timeseries/gdp_growth_treasury.csv` | 2024–2028 | % a year, real | Single edition | Sourced |
| | Petrol and diesel prices, monthly | Department "Fuel Price History" | `timeseries/fuel_prices_department.csv`; **candidate to November 2025** in `runs/manish_candidate_20261006/timeseries/` | Vintage: Jan 2011 – Apr 2024. Candidate: Jan 2011 – Nov 2025 | cents per litre, nominal | All 1,113 overlapping values unchanged in the candidate | Sourced to Nov 2025 as a candidate; Dec 2025 – Feb 2026 in a different document, not extracted; later months not posted |
| | Consumer price index for real prices | Stats SA P0141 | — | — | — | — | Open: needs manual download |
| Plant | Refinery nameplate capacity | FIASA annual report 2025, p.49 | `timeseries/refinery_capacity_reported.csv` | 2016–2025 | barrels a day | Single edition | Sourced (capacity, not output) |
| | Refinery output by product | Department energy balances | `timeseries/energy_balance_department.csv` | 2007–2021 | litres | — | Partial: ends 2021; implied 2022–2024 output in the package 4 balance |
| | Secunda and Natref refined output, all products | Sasol production and sales metrics, years to June | Not extracted | FY2020–FY2026 | million barrels | Overlapping years agree across the three editions read | Partial: no product split; Astron not published |
| | Utilisation and yields by plant | Reatile workbook only | `timeseries/refinery_production.csv` | 2022–2050 | fraction | — | Open: no published source |

## What was added today

**Fuel prices, May 2024 to November 2025.** The department's old price archive
stops at April 2024. Later files sit under a new folder pattern,
`Fuel Prices Per Zone/<year>/<Month> <year>/Fuel-Price-History.pdf`, which the
archive page does not list. `fetch_energy_dept` now tries those folders, latest
month first, for 2024 onward. Result: 2024 is complete (December file) and 2025
runs to November. 133 new monthly values; no existing value changed. Annual
averages now exist for 2024 (petrol 95 inland 2,312 c/l; diesel inland
wholesale 2,058 c/l).

Two parser faults were found and fixed on the way: the November 2025 row prints
"2 112.00" and "1 298.618" with a gap, which was read as 112.00 and 298.618.
The parser now joins such figures and leaves out, with a warning, any month in
which a price moves more than 70% from the month before (the largest genuine
move on record is 52%). The candidate's June 2024 and June 2025 values match
the prices FIASA prints for those dates.

Files for 2026 exist on the department's site behind numbered download links
with no predictable name; the archive page itself only lists to February 2026.
Not collected.

## Open items

| Item | Owner | Next action |
|---|---|---|
| Stats SA P3041.2 manufacturing, P2041 mining, P7162 land transport (time-series workbooks), P0141 CPI | Manish | Manual download into `external/data/raw/statssa/`; the site returns a block page to scripts. Then add readers and tests, as for GDP |
| Stats SA quarterly GDP for 2026 | Manish | The workbook is on disk; the reader takes the Annual sheet only. Add quarterly support |
| Tonne-kilometres for road and rail | Manish | Transnet annual report for rail; no road tonne-km series identified |
| Diesel burned for power, litres | Manish | Retrieve the primary parliamentary replies; FY2024 onward not found |
| Fleet by fuel type after 2023; split by vehicle class | Nigel | Request from RTMC; not published |
| Distance driven newer than 2014 | Nigel | Decide whether to approach the paper's authors or a commercial source |
| Fuel prices from December 2025 | Manish | Add a reader for the monthly "Breakdown of Prices" document (see follow-up); the department has posted nothing after February 2026 |
| Refinery output and utilisation by plant | Manish, Henry review | Operator reports (Sasol, Natref, Astron) |

## Follow-up, later on 6 October

**naamsa warnings: cleared.** The offline re-read gives ten warnings. Two are
the year-end reviews of February 2024 and February 2025, whose electric and
hybrid table could not be read (the 2025 one has a broken header, "Q4:2024"
twice). Three are older market tables not read; five are editions whose own
segment figures do not add to their printed total. Every one is an edition
that a later file supersedes. The extracted 2019–2025 electric and hybrid
figures equal the table in the February 2026 year-end review, line by line
(2025: battery electric 1,088; plug-in hybrid 2,810; hybrid 12,818; total
16,716).

**Fuel prices, December 2025 to February 2026.** The "Fuel Price History" file
stops at November 2025. The department's archive page lists December 2025,
January 2026 and February 2026 only as "Breakdown of Prices" documents, a
different layout. They were downloaded and read by eye, not parsed:

| Effective | Petrol 93 inland | Petrol 95 inland | Petrol 95 coast | Diesel 0.05% inland wholesale | Paraffin inland | Paraffin coast |
|---|---|---|---|---|---|---|
| 3 December 2025 | 2126.00 | 2141.00 | 2058.00 | 1978.83 | 1373.098 | 1271.598 |
| 7 January 2026 | 2064.00 | 2075.00 | 1992.00 | 1841.83 | 1263.098 | 1161.598 |
| 4 February 2026 | 1999.00 | 2010.00 | 1927.00 | 1791.83 | 1210.098 | 1108.598 |

Cents per litre. Coastal diesel is not given in this document. Nothing is
posted for March 2026 onward (page read 6 October 2026). These are not in any
CSV yet.

**Diesel burned for power.** Two press reports of ministerial replies give
litres for Eskom's own turbines. Set against the GWh already extracted:

| Year to March | Eskom turbines, GWh | Diesel, million litres | Litres per kWh |
|---|---|---|---|
| 2022 | 1,826 | 571 | 0.313 |
| 2023 | 3,018 | 937.5 | 0.311 |

The two years agree on about 0.31 litres per kWh, an efficiency of roughly 31%
at 36.9 MJ a litre. The Reatile workbook's 40% gives 0.244 litres per kWh, so
it understates diesel per unit of output by about a fifth. Applying 0.31 to
later output would give about 1.13 bn litres (FY2024), 0.68 (FY2025) and 0.25
(FY2026) for Eskom's own turbines; these are estimates, not reported figures,
and exclude the independent producers. The litres come from news reports
(forgood.org.za, 2 July 2022; a second outlet for FY2023), not the replies
themselves.

**Refinery output from the operator.** Sasol's production and sales metrics
(editions for the years to June 2022, 2025 and 2026; copies in
`external/data/raw/sasol/`, uncommitted), million barrels of refined product:

| Year to June | Secunda, total refined | Natref, Sasol's 63.64% share | Natref, whole refinery (share ÷ 0.6364) |
|---|---|---|---|
| 2020 | 31.2 | 16.8 | 26.4 |
| 2021 | 32.1 | 17.7 | 27.8 |
| 2022 | 29.2 | 18.9 | 29.7 |
| 2023 | 29.9 | 17.2 | 27.0 |
| 2024 | 29.1 | 17.8 | 28.0 |
| 2025 | 27.6 | 14.7 | 23.1 |
| 2026 | 30.6 | 25.8, of which 6.9 above its share | not derivable |

At 159 litres a barrel, Secunda and Natref together made about 9.0 bn litres of
refined products in each of FY2023 and FY2024 and 8.1 bn in FY2025. That is all
products (petrol, diesel, jet, paraffin, fuel oil, gas), for July–June years,
with no split by product. Astron Energy (Cape Town, 100,000 barrels a day
nameplate, restarted 2023) publishes no output. What this means for the
balance is in `fuel_balance_2026-10-06.md`.
