# Integrity flag log — 6 October 2026 (work package 1)

Investigated by Manish on `manish-branch`; for Nigel's review. Covers the eight
P1 rows of `output/delivered/Liquid_fuels_source_audit_2026_10_05.xlsx`
(Direction tab). No file under `assumptions/2026/` holding values has been
changed. Edits made: a repaired source record (flag 7), originals copied into
`external/` (flag 6), and three extraction fixes in code with tests (flags 2, 3
and 4). The corrected extracts are candidates under
`runs/manish_candidate_20261006/` (not tracked by Git); promoting them into the
vintage and the register awaits review.

Status: **resolved** = cause established and nothing further needed;
**ready for review** = cause established, proposed change awaits approval;
**partial** / **open** = evidence still missing, next action named.

## Summary

| # | P1 flag | Finding | Status | Owner / next action |
|---|---|---|---|---|
| 1 | Provincial annual coverage (26 rows) | None of the 26 rows is petrol or diesel. Every missing quarter is a blank cell in the department's own workbook, so the extract is faithful. | Resolved | — |
| 2 | Province vs national ties (6 rows) | Three single-quarter causes, each traced to the original cells: a wrong sheet read by our parser (2013), two department files that differ (2014; the energy balance supports the national one), an incomplete district sheet (2018). | Ready for review | Nigel: approve the 2013 correction; accept national for 2014 and 2018 |
| 3 | Refinery repeated keys (558 rows) | The workbook's `Production_High` named range is `Assumptions!L102:R13102`; it should stop at row 131. Extractor fixed; candidate has no repeats and the same values the engine reads today. | Ready for review | Nigel: approve promotion of the candidate CSV and register update |
| 4 | Historical demand repeated keys (15 rows) | The extractor walked past the jet table into three regional tables. Extractor fixed; candidate drops the 15 rows and nothing else. | Ready for review | Nigel: as above |
| 5 | Provisional sector baselines and elasticities | No source was ever recorded for the seven blocks. Evidence now located for industry, agriculture and marine volumes and for the diesel income elasticity; none matches the placeholders. | Partial | Section 5 |
| 6 | Missing originals (5 records) | All five are held locally with matching hashes; copied to `external/data/raw/`. | Ready for review | Nigel: confirm these may be committed |
| 7 | Unreadable DoT source metadata | YAML repaired. The 573 difference is in the published table, not the transcription. | Resolved | — |
| 8 | Provisional road parameters | Sourced alternatives exist for four of five blocks; none is adopted. | Ready for review | Nigel: review bridge from 24 vehicle types to 3 segments |
| 9 | Wide reference-table register coverage | Register holds one row per CSV row with all fields in the identity. A register-format question, not a data error. | Open | Nigel: decide whether to register field by field |

## 1. Provincial annual coverage

File: `assumptions/2026/timeseries/fuel_sales_department_by_province_quarterly.csv`.

Quarters present per province, petrol and diesel: 4 in every year 2013–2022 for
all nine provinces; 1 (Q1) in 2023. The 26 flagged rows by product: LPG 13,
jet 11, fuel oil 1, aviation gasoline 1. Provinces: EC, LP, NW, MP, NC, WC, KZN.

Original cells: for all 26 rows, every quarter absent from the extract is a
blank cell in the province row of that quarter's sheet in the district workbook
(for example 2014 EC LPG: `F5` blank on the Q2, Q3 and Q4 sheets; 2021 MP jet:
`B198`, `B198`, `B196`). None is a zero and none was dropped by the extraction.
The department's pivot tables leave a cell blank where no sales were reported;
whether that means nil sales or a non-reporting supplier is not stated. The
annual value for these rows is therefore the sum of the reported quarters, and
should stay flagged as fewer than four quarters.

## 2. Province versus national

Sum of nine provinces minus the national file, same quarter:

| Quarter | Petrol | Diesel | National file | District file |
|---|---|---|---|---|
| 2013-Q4 | +10.77% (+287 ML) | +8.25% (+251 ML) | `2013-Annual-FSV-at-National-Level-07-February-…` | `2013-FSV-Disaggregated-FSV-at-Magisterial-District-Quarter4-16Jan2015.xlsx` |
| 2014-Q3 | +5.38% (+140 ML) | +4.30% (+128 ML) | `2014-Annual-FSV-at-National-Level-Quarter-3-16…` | `2014-Quarterly-Disaggregated-FSV-Data-Magisterial-District-Level-01Dec2015.xlsx` |
| 2018-Q1 | −7.66% (−213 ML) | −7.24% (−220 ML) | `2018-National-Aggregated-FSV.xls` | `2018-Quarter4-Magisterial-Districts-data.xlsx` |

The Week 1 pack (page 4) lists six flagged years. Three are the material ones
above. The other three are small and not yet traced to cells: 2015 differs in
all four quarters (year: diesel −28 ML, −0.21%; petrol −6 ML, −0.05%; largest
quarter Q4 diesel −28 ML), 2017 in Q4 only (diesel −2.1 ML, petrol −0.3 ML)
and 2021 in Q1 diesel only (−0.8 ML). All other quarters 2013–2023-Q1 tie to
the litre. Next action (Manish): compare cells for 2015; the 2017 and 2021
differences are below 0.02% of the year. What the original cells show for the
three material ones:

**2013-Q4: our extraction read the wrong sheet.** The national workbook has
three sheets. `Sheet4` and `Sheet1` are a working pivot and its data, with
Q4 diesel 3,039,253,633 and petrol 2,666,145,468. The published table, sheet
"2013 Annual Aggregated FSV data" (headed "2013 JANUARY TO DECEMBER SA FUEL
SALES VOLUME / CONSUMPTION"), has Q4 diesel 3,289,996,382 (`F5`) and petrol
2,953,393,316 (`F6`). The parser took the first sheet. Three independent
records agree with the published table: the district quarterly workbook, the
separate 2013 annual district workbook (grand total row 378) and the Reatile
workbook's history.

| 2013, litres | Current CSV | Proposed (published sheet) | Change |
|---|---|---|---|
| Diesel | 11,890,350,007 | 12,141,281,548 | +250,931,541 |
| Petrol | 11,152,866,181 | 11,439,925,235 | +287,059,054 |
| Jet | 2,223,444,585 | 2,305,651,372 | +82,206,787 |
| Paraffin | 529,971,037 | 538,617,919 | +8,646,882 |
| Fuel oil | 523,171,500 | 560,574,922 | +37,403,422 |
| LPG | 484,932,089 | 499,517,824 | +14,585,735 |

Fix: `energy_dept.parse_sales` now prefers the sheet carrying the published
title, and `fetch_energy_dept` warns when a workbook's sheets disagree. Run over
all national workbooks 2005–2023, 2013 is the only file whose values change.
Note that FIASA's 2013 figures (11,890 and 11,153 ML) equal the superseded
pivot, so this correction also removes the apparent agreement with FIASA.

**2014-Q3: two department files differ; open.** National file dated 16 January
2015: diesel 2,982,077,297, petrol 2,610,535,183. District file dated
1 December 2015, sheet "2014 Q3", grand total row 351: diesel 3,110,443,824,
petrol 2,750,992,369. The district file is ten months later, which suggests a
revision, but no third record settles it: the Reatile workbook follows the
national file (12,615 and 10,890 ML for the year) and FIASA prints a third
pair (13,169 and 11,344 ML). The department's own 2014 energy balance gives
final consumption of 12.60 bn litres of diesel and 10.86 bn of petrol, which
sits with the national file (12.615 and 10.890) and not with the district
sum (12.743 and 11.031). On that evidence the national figure stands and the
district 2014-Q3 sheet is the outlier; both records are preserved.

**2018-Q1: the district sheet is incomplete.** National file: diesel
3,039,026,286, petrol 2,775,178,163. District workbook sheet "2018 Q1", grand
total row 334: diesel 2,818,960,276, petrol 2,562,546,859. The national figure
is supported by the Reatile workbook and FIASA (12,539 and 11,142 ML for the
year). The district Q1 sheet lists six fewer districts than Q2 and carries a
"Region Type: (Multiple Items)" filter. So provincial sums for 2018 understate
petrol by 1.9% and diesel by 1.8%; the national series is right. Proposed:
keep the provincial 2018 figures as published and flag the year as not tying.

## 3. Refinery repeated keys

File: `assumptions/2026/timeseries/refinery_production.csv` (948 rows; 774
`high_demand`, 174 `low_demand`). Extractor:
`src/lfm/scripts/extract_xlsx_to_assumptions.py::extract_refinery_production`.

Cause: in the Reatile workbook, `Production_Low` is `Assumptions!L135:R164`
(correct), but `Production_High` is `Assumptions!L102:R13102`. The extractor
keeps every row in the range whose first cell is a year. Tables inside the
range (column L to R):

| Rows | Years | What it is |
|---|---|---|
| 103–131 | 2022–2050 | High production utilisation — the intended table |
| 136–164 | 2022–2050 | Low production utilisation |
| 172–200 | 2022–2050 | High EAF load factor; high demand diesel % |
| 204–232 | 2022–2050 | Low EAF load factor; low demand diesel % |
| 237–263 | 2024–2050 | High EAF |
| 267–293 | 2024–2050 | Low EAF |
| 300–342 | 2008–2050 | Freight payload, tonnes |
| 350–392 | 2008–2050 | Fuel price, CPI index, real price |

Effect on the model: `flows.py::_utilisation_series` takes the first value per
year. For 2022–2050 the first value is the intended table in all 174 cases
(checked cell by cell, no mismatch), so current outputs use the right numbers.
For 2008–2021 the 70 rows are freight tonnes and price figures labelled as
utilisation (for example Enref 2008 = 8.89 and 725,799,000); the forecast
horizon starts in 2024, so they are not read.

Fix made: `leading_year_rows` stops the read at the first row that does not
start with a year. Candidate `runs/manish_candidate_20261006/timeseries/refinery_production.csv`
has 348 rows (6 refineries × 29 years × 2 scenarios), no repeated key, and the
same value as the engine reads today for all 348 keys. The only keys that
disappear are the 42 mislabelled 2008–2021 ones (Enref, Sapref, Natref).
Test: `tests/test_extract_xlsx_boundaries.py`.

## 4. Historical demand repeated keys

File: `assumptions/2026/timeseries/historical_demand.csv`. Extractor:
`extract_historical_demand`, sheet `Jet - DemandSupply`, year column E, value
column J.

Cause: the RSA Demand table is rows 9–23 (2010–2024). The extractor continues
down column E and picks up three more tables that also have years 2019–2023:

| Rows | Table | What column J holds |
|---|---|---|
| 27–31 | Jet fuel by region | "NC, WC" regional volume |
| 35–39 | Aviation gasoline by region | "NC, WC" regional volume |
| 45–49 | Regional shares | "NC, WC" share (0.11–0.22) |

So each of 2019–2023 has four `jet_a1` values; only the first is national
demand. Petrol and diesel sheets have no repeats.

Fix made: the walk now stops at the first non-year row once the table has
started (row 24 is blank). Candidate `historical_demand.csv` has 57 rows, no
repeated key, and all 57 values equal the first value in the current file.
Test: `tests/test_extract_xlsx_boundaries.py`.

## 5. Sector baselines and elasticities

Current parameter, its claimed source, and the evidence located. Energy balance
figures are from `energy_balance_department.csv` (department commodity flow and
energy balance workbooks, diesel, converted to litres).

| Block | Current value | Claimed source in YAML | Evidence located | Unresolved |
|---|---|---|---|---|
| `industrial.base_year_volume` | 2.5 bn L (2024) | Residual of workbook diesel; "mid-range guess" | Energy balance, industry sector: 1.50 bn L in 2021 (of which mining 1.29); range 1.00–1.93 over 2007–2021 | Balance ends 2021. Category boundaries, below |
| `industrial.elasticity` | 1.0 | "Literature mid-range", no citation | None located | No source |
| `agriculture.base_year_volume` | 0.7 bn L (2024) | Placeholder | Energy balance, agriculture/forestry: 1.06 bn L in 2021; 0.88–1.09 in 13 of 15 years; 1.89 and 1.88 in 2016–2017 | 2016–2017 look like a classification change |
| `agriculture.elasticity` | 0.2 | Placeholder | None located | No source |
| `marine.base_year_volume` | Durban 1.5, Cape Town 0.5, Saldanha 0.2 bn L (2024) | Placeholder | Energy balance reports diesel marine bunkers only for 2007 and 2010–2012 (0.26, 1.60, 1.65, 2.02 bn L); nothing after | No port-level or recent national figure |
| `marine.product_split` | 65% fuel oil, 35% diesel | "Literature mid-range" | Implies 1.43 bn L of fuel oil bunkers; total recorded national fuel oil sales are 0.41–0.66 bn L a year (2014–2023) | Whether bunkers sit outside the sales record |
| `marine.elasticity` | 0.4 | Placeholder | None located | No source |

New flag from this work: the energy balance sector boundaries are not stable.
"Commerce and public services" diesel is 0.01–0.08 bn L up to 2015 and 3.6–5.0
bn L from 2016, while road falls from 9.4 to 4.4–6.7 bn L. Any sector baseline
taken from the balance must state which year's definitions it uses.

Further evidence located on 6 October:

- **Diesel income elasticity.** Boshoff, W.H., "Petrol, diesel fuel and jet fuel
  demand in South Africa: 1998–2009" (Econex research article 13; published as
  Boshoff 2012, *Studies in Economics and Econometrics* 36(1)). Table 11,
  page 15: long-run income elasticity of total diesel demand with respect to
  real GDP is 1.01 (1982Q1–2009Q3) and 1.51 (1998Q1–2009Q3); long-run price
  elasticity −0.13. Kept at
  `external/data/raw/literature/boshoff-econex-research-article-13-fuel-demand-1998-2009.pdf`.
  Limits: it is for all diesel, not industry, agriculture or marine separately;
  it uses GDP, not GDP per capita as the model does; the sample ends in 2009.
  It gives no support for 0.2 (agriculture) or 0.4 (marine).
- **Marine bunker volumes.** Trade press only, no official series found.
  Freight News, 3 June 2026, quoting FFS Refiners: about 840,000 tonnes a year
  across Cape Town, Durban and Richards Bay, against a past peak above 3.5
  million tonnes. Other trade reports: about 130,000 tonnes a month through
  2023, about 80,000 a month in early 2024 after offshore bunkering at Algoa
  Bay stopped. At roughly 1,000 litres a tonne these are about 1.6, 1.0 and
  0.85 bn litres a year, against the model's 2.2 bn litres for 2024. Not
  verified against a primary source; articles not archived.

Marine lines in the original balance workbooks (read 6 October, all fifteen
years): international marine bunkers are reported for fuel oil in 2007 only
(2.42 bn litres, plus 0.26 bn of diesel) and for diesel in 2010–2012; the row
is empty from 2013 and zero in 2021. The 2.2 bn litre placeholder is therefore
close to the 2007 level, the last time the department measured it, and about
twice what the trade press reports for 2024–2026.

Next actions (Manish): (a) done, above; (b) Transnet National Ports
Authority and SARS ship-stores data for an official bunker series; (c) a
sector-level source for agriculture and marine response to activity, or a
decision to drive them with something other than GDP per capita. None replaces
a parameter until reviewed.

## 6. Missing originals

Audit tab "Source evidence" lists five records with no local original. All are
on Manish's machine. Hashes match the three that have recorded hashes.

| Record | Copied to | Hash check |
|---|---|---|
| Stone et al. 2018, main paper | `external/data/raw/literature/stone-2018-vehicle-parc-model-jesa-29-2.pdf` | No hash recorded; sha256 `2ee456a9…4bc5e8` |
| Stone et al. 2018, supplementary | `external/data/raw/literature/stone-2018-supplementary.pdf` | No hash recorded; sha256 `b8730af0…25d3bd` |
| Stats SA GDP P0441 time series, Q2 2026 | `external/data/raw/statssa/` | Matches |
| Stats SA country projection 2002–2026 | `external/data/raw/statssa/` | Matches |
| Department 2013 magisterial districts workbook | `external/data/raw/energy_dept/fsv_district/` | Matches |

Also copied: the Department of Transport bulletin (flag 7) and the Stats SA
mid-year estimates report table. Not yet committed; these are public documents
but the repository rule asks for a decision before adding received material.

## 7. Department of Transport source record

File: `assumptions/2026/reference/vehicle_population_by_fuel_dot2023.sources.yaml`.
A list item began with a quoted word, which YAML rejects; rewritten as folded
text. All source records in `assumptions/2026/` now parse.

The 573: Table 2.8 (page 40) prints a total of 13,188,374; its fourteen fuel
rows add to 13,187,801. The nine provincial totals add to the printed
13,188,374, and each provincial total exceeds the fuel rows above it, so the
gap is in the publisher's table. Petrol (8,555,772) and diesel (3,335,546) each
equal the sum of their nine provincial cells.

## 8. Road parameters

| Block | Model value | Sourced alternative in the repo | Gap |
|---|---|---|---|
| `annual_km_per_vehicle` | 17,000 / 28,000 / 70,000 km | Stone et al. 2018 (2014 values), 24 vehicle types: petrol car 14,457; diesel LCV 20,397 | Values are for 2014; weighting to three segments not reviewed |
| `fuel_consumption` | 9.5 / 7.5 / 35 L per 100 km | Same paper: petrol car 8.2, diesel car 8.1 (fleet average) | As above |
| `petrol_diesel_split` | Passenger 83/17; LCV 30/70 | `fleet_fuel_split_2023.csv`: passenger 86.1/13.9; LCV 44.1/55.9 | Derived: 2010 pattern fitted to official December 2023 totals; class-level split is not published |
| `scrappage_rate` | 4% / 5% / 6% a year | Same paper: Weibull survival curves by type | Different functional form from the model |
| `new_vehicle_segment_split` | 78 / 18 / 4% | NaTIS new registrations by class; naamsa market by segment | Not yet computed as shares |

Original paper and supplement are now in `external/data/raw/literature/`
(flag 6). The tables were typed by hand; an independent re-check against the
PDF has not been done.

## Checks run

- `python -m lfm check --vintage 2026`: governance coverage passed; 52 open exceptions.
- `python -m pytest -q`: 136 passed, 1 skipped (133 before; three tests added).
- `ruff check` on the five touched files: clean.

## Audit re-run, 6 October

`python -m lfm.scripts.audit_source_inputs --vintage 2026` on `manish-branch`
(output in `runs/source_audit_20261006T115205706711Z/`, untracked): both
scenarios run; metadata parse errors 0 (1 on 5 October); the engine requests
the same six CSVs as in the 5 October profile; provincial gaps 26 and repeated
keys unchanged, as expected, because no vintage value has been changed.

## Changes applied on 6 October after Manish's review

Manish approved five of the items above; they are now applied on
`manish-branch` for Nigel to confirm. The register was reconciled with
`python -m lfm.scripts.sync_register` for the five blocks touched (804 rows
kept, 20 updated, 209 added, 809 removed); every changed row is `unreviewed`.

| Item | Applied | Effect |
|---|---|---|
| 2013 national sales | `fuel_sales_department.csv` and its quarterly file now read the published sheet: diesel 12,141,281,548; petrol 11,439,925,235 litres (all six products change) | Reference data only; not read by the engine |
| Refinery repeated keys | `refinery_production.csv` is 348 rows, no repeated key | Supply unchanged in every year, both scenarios |
| Jet history repeated keys | `historical_demand.csv` is 57 rows | Comparison data only |
| Industry and agriculture baselines | Industry 2.5e9 (2024) → 1,499,139,260 litres (2021); agriculture 0.7e9 (2024) → 1,058,398,950 litres (2021); source: 2021 energy balance; marked `needs_verification` | Diesel demand falls 0.63 bn litres in 2024 (15.29 → 14.65 in the high scenario, 15.24 → 14.61 in the low) and by 0.63–0.69 bn in 2030 and 2035 |
| Original documents | Committed under `external/data/raw/` (not the three Glencore annual reports) | Closes the missing-originals flag for the five records |

Left for Nigel, unchanged: the 2014 and 2018 provincial treatment, the
elasticities, the road parameters and the register layout. The marine baseline
stays at its placeholder on hold.

Checks after the changes: `python -m lfm check --vintage 2026` passes with 52
open exceptions; `python -m pytest -q` 150 passed, 1 skipped; both scenarios
run.
