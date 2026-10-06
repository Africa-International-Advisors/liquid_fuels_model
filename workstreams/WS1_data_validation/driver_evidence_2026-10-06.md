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
| | Manufacturing production volume index | Stats SA P3041.2, July 2026 | `timeseries/activity_statssa_monthly.csv` | Jan 1998 – Jul 2026 | index, 2019=100 | One release | Sourced |
| | Mining production volume index | Stats SA P2041, July 2026 | `timeseries/activity_statssa_monthly.csv` | Jan 2003 – Jul 2026 | index, 2019=100 | One release | Sourced |
| | Diesel used by industry and mining | Department energy balances | `timeseries/energy_balance_department.csv` | 2007–2021 | litres | Sector boundaries shift in 2016 | Partial: ends 2021 |
| Power | Gas turbine output, Eskom and independent producers | Eskom integrated reports, years to March | `timeseries/ocgt_generation_eskom.csv` | FY2022–FY2026 (Eskom); FY2023–FY2026 (combined) | GWh | Overlapping years agree across reports (none revised) | Sourced |
| | Diesel burned, litres | Minister of Public Enterprises, replies reported in the press (Eskom's own turbines) | Not extracted | FY2022: 571 ML; FY2023: 937.5 ML; FY2025: 679 ML | litres | FY2025 from the reply itself (NW1980); the other two from press reports | Partial: three years, FY2024 missing; see follow-up |
| Electrification | Battery electric, plug-in hybrid and hybrid new sales | naamsa quarterly reviews | `timeseries/nev_sales_naamsa.csv` | 2019–2025 | vehicles | Warnings reviewed 6 October: all relate to superseded editions; final values match the latest year-end review exactly | Sourced |
| | Electric vehicles in the fleet | DoT bulletin Table 2.8: 4,090 electric at December 2023 | `reference/vehicle_population_by_fuel_dot2023.csv` | December 2023 only | vehicles | The same table shows 6 hybrids, which cannot be right | Partial |
| Economic context | Real GDP and GDP per person | P0441 (code AR1000) and P0302 population | `timeseries/macro_statssa.csv` | 1993–2025; population to 2026 | rand, constant 2015 prices; persons | One release vintage; years after 2026 are projections | Sourced |
| | Growth forecast | National Treasury Budget Review 2026, chapter 2 | `timeseries/gdp_growth_treasury.csv` | 2024–2028 | % a year, real | Single edition | Sourced |
| | Petrol and diesel prices, monthly | Department "Fuel Price History" | `timeseries/fuel_prices_department.csv`; **candidate to November 2025** in `runs/manish_candidate_20261006/timeseries/` | Vintage: Jan 2011 – Apr 2024. Candidate: Jan 2011 – Nov 2025 | cents per litre, nominal | All 1,113 overlapping values unchanged in the candidate | Sourced to Feb 2026 as a candidate (six of seven series from Dec 2025); later months not posted |
| | Consumer price index for real prices | Stats SA P0141, August 2026 | `timeseries/activity_statssa_monthly.csv` | Jan 2008 – Aug 2026 | index, December 2024=100 | One release | Sourced |
| Plant | Refinery nameplate capacity | FIASA annual report 2025, p.49 | `timeseries/refinery_capacity_reported.csv` | 2016–2025 | barrels a day | Single edition | Sourced (capacity, not output) |
| | Refinery output by product | Department energy balances | `timeseries/energy_balance_department.csv` | 2007–2021 | litres | — | Partial: ends 2021; implied 2022–2024 output in the package 4 balance |
| | Secunda and Natref refined output, all products | Sasol production and sales metrics, years to June | Not extracted | FY2020–FY2026 | million barrels | Overlapping years agree across the three editions read | Partial: no product split |
| | Astron (Cape Town) refined output, all products | Glencore Annual Reports 2023 (p.104), 2024 (p.85), 2025 (p.69), "Astron Energy – energy content of refined products" | Not extracted | 2023–2025; nil in 2022 | billion Btu | 2023 and 2024 agree across editions | Partial: energy content, not litres; no product split |
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
| Stats SA provincial GDP (P0441.2) | Manish | Done 6 October: `timeseries/gdp_by_province_statssa.csv`, nine provinces, 2013–2024; see the provincial note |
| Tonne-kilometres for road and rail | Manish | Rail tonnes confirmed (see second follow-up); tonne-km is not in the results coverage read; no road series identified |
| Diesel burned for power, litres | Manish | FY2024 litres not found (only R23.4 bn of spend); primary replies for FY2022 and FY2023 not retrieved |
| Fuel prices after February 2026 | Manish | Nothing posted by the department yet; the fetcher will pick new months up when they appear |
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
with no split by product. What this means for the balance is in
`fuel_balance_2026-10-06.md`.

**Astron's output is published by its owner.** An earlier version of this note
said Astron publishes no output; that was wrong. Astron Energy (Pty) Ltd issues
no report of its own, but Glencore, which holds 68%, reports it in its Annual
Reports for 2023 (page 104), 2024 (page 85) and 2025 (page 69); copies are in
`external/data/raw/glencore/`, uncommitted:

| Calendar year | Energy content of refined products | In PJ | Litres at 36 MJ a litre |
|---|---|---|---|
| 2022 | nil (refinery not operating) | — | — |
| 2023 | 136,665 billion Btu | 144.2 | about 4.0 bn |
| 2024 | 166,204 billion Btu | 175.4 | about 4.9 bn |
| 2025 | 164,365 billion Btu | 173.4 | about 4.8 bn |

The litres are a conversion, not a reported figure: 36 MJ a litre is an assumed
average for a mixed slate (petrol is about 34, diesel about 38), which puts the
2024 figure between 4.6 and 5.1 bn litres, about 84% of the 100,000 barrels a
day nameplate, and the 2023 figure between 3.8 and 4.2 bn litres (the refinery
restarted in early 2023, so that is a part year). Two cautions: the same report says (p.30 of the TCFD section)
that "sold oil products processed by our Astron Energy Refinery" rose 28% in
2025, which does not sit with a 1% fall in energy content and has not been
reconciled. The 2023 and 2024 values are the same in each edition that prints
them.

## Second follow-up, 6 October

**Fuel prices now run to February 2026 by script.** `fetch_energy_dept` reads
the department's monthly "Breakdown of Prices" pages for months the yearly
history no longer covers (reader: `energy_dept.parse_price_breakdown`). Six of
the seven series continue; coastal diesel is not published on those pages. As a
check the November 2025 breakdown is read as well and equals the history for
all six series. Candidate file: 151 monthly values beyond the vintage, none of
the existing 1,113 changed.

**Power diesel: a third year, from the primary source.** Reply to
parliamentary question NW1980 (Minister of Electricity and Energy, 14 May
2025): "During FY2025, Eskom OCGTs burnt 679 million litres of diesel." Against
2,176 GWh that is 0.312 litres per kWh, the same as FY2022 (0.313) and FY2023
(0.311). The factor of about 0.31 now rests on three years. FY2024 litres were
not found; a reply of 25 April 2024 gives only the spend, R23.38 bn.

**Quarterly GDP and industry value added.** `statssa.parse_quarterly_constant_price_series`
reads the Quarterly sheet of the P0441 workbook already on disk (constant 2015
prices, not seasonally adjusted). Candidate `macro_statssa_quarterly.csv`:
15 series, 1993-Q1 to 2026-Q2. For every complete year the four quarters add
to the annual figure within 0.1%.

**Rail tonnes.** Transnet's results for the year to March 2026 as reported in
the press: rail volumes 167.9 million tonnes, up from 160.1 million; the
target is 250 million tonnes by 2029/30, of which Transnet Freight Rail about
185 and private train operators about 65, the first of them from April 2027.
These agree with the Stats SA rail payload already extracted (160.7 and 168.3
million tonnes for calendar 2024 and 2025). Transnet's own report was not
retrieved; figures are from Engineering News and other coverage.

**Not obtained.** The port authority's statistics site did not respond from
this network, so no official bunker series. Sasol and Glencore publish no
split of refinery output by product.

## Review outcomes, 6 October

Manish reviewed this package and accepted this checklist as the record. Applied
on `manish-branch` for Nigel to confirm:

- **Fuel prices to February 2026** are in the vintage
  (`fuel_prices_department.csv`, 1,264 monthly values; annual averages to
  2025). No earlier value changed. **Flag: coastal diesel
  (`diesel_005_coast_wholesale`) has no value from December 2025, because the
  department stopped publishing it** when it moved to monthly breakdown pages;
  the gap is recorded in `energy_department.sources.yaml`.
- **Quarterly GDP and industry value added** are in the vintage
  (`macro_statssa_quarterly.csv`, 1993-Q1 to 2026-Q2), declared and registered.
- **Reported power diesel litres** are recorded in
  `reference/ocgt_diesel_burn_reported.csv` (years to March 2022, 2023 and
  2025), declared and registered.

Left for Nigel: whether to adopt 0.31 litres per kWh for power diesel in place
of the workbook's implied 0.244. It changes model results.

Dropped by Manish: requests to RTMC for the fleet by fuel type and to the
paper's authors for newer distance figures. The fleet fuel split and the 2014
distance values therefore stay as they are, marked partial.

## Stats SA monthly releases obtained, 6 October

The four releases were downloaded through the browser (the site refuses
scripts but serves a signed-in browser session) and are kept as downloaded in
`external/data/raw/statssa/`, with the provincial GDP release (P0441.2, 2024),
which is read by `statssa.parse_provincial_gdp`. Reader: `statssa.parse_monthly_series`; command:
`python -m lfm.scripts.fetch_statssa_monthly --vintage 2026`. Output: `activity_statssa_monthly.csv` (2,753 monthly values), in the vintage
from 6 October (see below).

| Series | Release | Coverage | Unit |
|---|---|---|---|
| Mining production volume: total, excluding gold, coal | P2041, July 2026 | Jan 2003 – Jul 2026 | index, 2019=100 |
| Manufacturing production volume, total | P3041.2, July 2026 | Jan 1998 – Jul 2026 | index, 2019=100 |
| Freight payload: total, road, rail | P7162, July 2026 | Jan 2008 – Jul 2026 | thousand tonnes |
| Passenger journeys: total, road, rail | P7162, July 2026 | Jan 2008 – Jul 2026 | thousand journeys |
| Consumer price index, headline | P0141, August 2026 | Jan 2008 – Aug 2026 | index, December 2024=100 |

All are actual values, not seasonally adjusted. This closes the open rows for
the manufacturing and mining indices and the consumer price index, and turns
the two-year freight payload series into a full one.

Checks: annual rail payload is 160.7 million tonnes for 2024 and 168.3 for
2025, and road 979.8 for 2024, the same as the December 2025 release already
extracted; road for 2025 is 975.2 against 976.5 in that release, a revision of
1.3 million tonnes. The 2019 averages of both volume indices are 100.0.

What the freight series shows: rail carried 214 million tonnes in 2019, 156 in
2022 and 168 in 2025; road carried 896, 1,049 and 975. Tonnes are not
tonne-kilometres, which Stats SA does not publish.

## Prices to October 2026 from the Central Energy Fund, and Stats SA monthly series promoted

Manish pointed to the Central Energy Fund's daily basic fuel price sheets
(cefgroup.co.za > Petrol Price > Daily Basic Fuel Price), which run to
5 October 2026. Each sheet restates the regulated Gauteng pump price for petrol
and the wholesale price for diesel and paraffin, with the date they took
effect. Reader: `lfm.sources.cef`; `fetch_energy_dept` now takes one sheet a
month, the one nearest the 15th, for months after the department's latest.

- `fuel_prices_department.csv` now runs from January 2011 to October 2026
  (1,296 monthly values). No earlier value changed.
- Check: CEF's February 2026 sheet equals the department's February breakdown
  for all four series it carries.
- **Flags.** CEF prints inland prices only. Four series continue to October
  2026 (petrol 93 and 95 inland retail, diesel 0.05% inland wholesale, paraffin
  inland). Three stop: coastal diesel from December 2025, and coastal petrol 95
  and coastal paraffin from March 2026. The gaps are recorded in
  `energy_department.sources.yaml`.
- The file keeps its name, but from March 2026 its rows come from CEF; the
  `source_file` column shows which.

Regulated inland prices for 2026, rand per litre:

| Effective | Petrol 95 retail | Diesel 0.05% wholesale |
|---|---|---|
| 4 February | 20.10 | 17.92 |
| 4 March | 20.30 | 18.54 |
| 1 April | 23.36 | 25.91 |
| 6 May | 26.63 | 31.18 |
| 3 June | 28.06 | 27.93 |
| 1 July | 26.10 | 24.79 |
| 5 August | 25.58 | 26.17 |
| 2 September | 26.92 | 29.11 |
| 7 October | 30.25 | 31.95 |

Diesel has risen by 78% and petrol by 50% since February. Any work on demand
response to price has to use the series to October, not to February.

The Stats SA monthly series (previous section) are now in the vintage,
declared, registered (2,753 rows) and part of `refresh_sources`. That fetcher
never downloads; it reads whatever release zips are in
`external/data/raw/statssa/`.
