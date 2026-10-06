# 6 October: feedback checklist and Manish discussion

Purpose: turn the current diagnostics and partner story into a reproducible,
traceable fuel baseline and one defensible integration candidate. South Africa
petrol and diesel are the client focus; jet remains tracked separately.
Nigel reviews proposed changes; Manish investigates and implements explained
replacements. Henry reviews the technical mechanisms. Assignments and dates
below are proposed discussion targets, not recorded meeting commitments.

## Start the conversation here

Ask Manish for three things today: **reproduce the baseline, explain the flagged
data, and propose one source-backed integration change**. Define the demand and
supply levers alongside that work. Do not ask him to rebuild all the maps first.

| Start with | Exact files to open | What Manish returns |
|---|---|---|
| 1. Find what the model actually uses | [Source audit workbook](../../../output/delivered/Liquid_fuels_source_audit_2026_10_05.xlsx), then [source profile](../../../output/delivered/source_profile_2026_10_05.html) | Input name → current file → consuming function → output; distinguish unused sources and presentation-only evidence. |
| 2. Investigate the flagged numbers | Workbook tabs **Direction**, **Provincial gaps**, **Repeated keys**; open the CSVs in the file table below | Old value → competing/proposed value → original source cell → explanation. Keep unresolved cases open. |
| 3. Propose the first integration | [Current GDP/capita input](../../../assumptions/2026/timeseries/gdp_per_capita.csv) versus [World Bank extract](../../../assumptions/2026/timeseries/macro_worldbank.csv) and [Stats SA extract](../../../assumptions/2026/timeseries/macro_statssa.csv) | Explain units, GDP/population consistency and forecast extension; one before/after petrol/diesel comparison. No automatic substitution. |

## Where the files are

Nigel's local project folder is
`C:\Users\ITafr\Desktop\Insights\liquid_fuels_model`.
All paths below are relative to that folder. Manish uses the same paths beneath
his own clone; he does not need Nigel's Windows username or Desktop path.
Every linked file below is on main. The separate local refresh folder is the
exception described after the table.

| Folder | What it contains | What this means |
|---|---|---|
| `external/` | Original workbooks, reports and captured source documents | Evidence to check against; not automatically a model input. |
| `assumptions/2026/` | Extracted CSV data and YAML settings | Some are consumed by the engine; others are staged or used only in the pack. Check the specific row below. |
| `src/lfm/model/` | Demand and supply calculations | This is where fuel quantities are calculated. Fetch/download functions live in `src/lfm/scripts/`. |
| `output/delivered/` and `pptx/output/delivered/` | Audit workbook, profiles, flags and delivered presentation | Review outputs; not the original source data. |

## Exact source files, use and investigation

| Question | Extracted data / settings: click to open | Original evidence / where to trace it | Where it is used and what to check |
|---|---|---|---|
| Current workbook baseline | [gdp_per_capita.csv](../../../assumptions/2026/timeseries/gdp_per_capita.csv), [macro.yaml](../../../assumptions/2026/macro.yaml) | [Original Reatile workbook](<../../../external/sources/Liquid Fuels Model - Supply Demand, 2025 - Reatile Copy.xlsx>) | Engine input. `macro.gdp_per_capita` feeds [vehicles.py](../../../src/lfm/model/demand/vehicles.py), [agriculture.py](../../../src/lfm/model/demand/agriculture.py), [industrial.py](../../../src/lfm/model/demand/industrial.py) and other demand modules; trace the profile for each block. |
| Proposed macro replacement | [macro_worldbank.csv](../../../assumptions/2026/timeseries/macro_worldbank.csv), [macro_statssa.csv](../../../assumptions/2026/timeseries/macro_statssa.csv), [gdp_growth_treasury.csv](../../../assumptions/2026/timeseries/gdp_growth_treasury.csv) | Fetcher [fetch_economy.py](../../../src/lfm/scripts/fetch_economy.py); source records in the companion metadata and source profile | Staged; sector activity also appears on pack p7. Not an automatic replacement of current GDP/capita or its forecast through 2050. |
| Provincial demand and completeness | [Annual provincial sales](../../../assumptions/2026/timeseries/fuel_sales_department_by_province.csv), [quarterly provincial sales](../../../assumptions/2026/timeseries/fuel_sales_department_by_province_quarterly.csv), [national annual sales](../../../assumptions/2026/timeseries/fuel_sales_department.csv) | The `source_file` column identifies each original department workbook. [fetch_energy_dept.py](../../../src/lfm/scripts/fetch_energy_dept.py), function `_provincial`, performs extraction; some original downloads are still local. | Reporting pp3–4, not a calibrated provincial engine. Use quarters and exact source cells to explain the 26 flagged totals and six national ties; 2023 is incomplete. |
| Repeated refinery records | [refinery_production.csv](../../../assumptions/2026/timeseries/refinery_production.csv), [supply.yaml](../../../assumptions/2026/supply.yaml) | Original Reatile workbook: `Production_High` / `Production_Low`; [scenario mapping](../../../assumptions/2026/_meta.yaml) | Despite its filename, this CSV is wired as **refinery utilisation** in [flows.py](../../../src/lfm/model/supply/flows.py), `compute_supply` / `_utilisation_series`. Resolve 558 extra rows before replacing values. |
| Repeated historical demand records | [historical_demand.csv](../../../assumptions/2026/timeseries/historical_demand.csv) | Original Reatile workbook: RSA Demand table; audit workbook **Repeated keys** tab | Historical comparison evidence; inspect all 15 extra rows, including jet keys. This is not a reason to sum repeated observations. |
| Sales, imports and exports | [fuel_sales_fiasa.csv](../../../assumptions/2026/timeseries/fuel_sales_fiasa.csv), [fuel_trade_fiasa.csv](../../../assumptions/2026/timeseries/fuel_trade_fiasa.csv), [fuel_trade_department_review.csv](../../../assumptions/2026/timeseries/fuel_trade_department_review.csv) | [FIASA report](../../../external/data/raw/fuel_supply_review_20261006/annual-report-2025.pdf), [government trade report](../../../external/data/raw/fuel_supply_review_20261006/trade2024.pdf), [source flag CSV](../../../output/delivered/supply_review_2026_10_06/trade_source_flags.csv) | Pack p5. These collected observations do not replace engine supply. Resolve 14.793 versus 10.8 bn litres of diesel imports; collect matched output/stocks before claiming a closed balance. |
| Vehicle stock and EV uptake | [vehicle_population_natis.csv](../../../assumptions/2026/timeseries/vehicle_population_natis.csv), [nev_sales_naamsa.csv](../../../assumptions/2026/timeseries/nev_sales_naamsa.csv), current [vehicles.yaml](../../../assumptions/2026/vehicles.yaml) | [fetch_natis.py](../../../src/lfm/scripts/fetch_natis.py), [fetch_naamsa.py](../../../src/lfm/scripts/fetch_naamsa.py); underlying prior PDFs are in the local refresh folder | Extracts appear on pack p7. Engine [vehicles.py](../../../src/lfm/model/demand/vehicles.py) uses current vehicle settings; observed new sales are not fleet penetration. Fuel split, retirement, mileage and intensity need a reviewed bridge. |
| Power, agriculture and industry | [ocgt_generation_eskom.csv](../../../assumptions/2026/timeseries/ocgt_generation_eskom.csv), [macro_statssa.csv](../../../assumptions/2026/timeseries/macro_statssa.csv), current [generation.yaml](../../../assumptions/2026/generation.yaml), [agriculture.yaml](../../../assumptions/2026/agriculture.yaml), [industrial.yaml](../../../assumptions/2026/industrial.yaml) | [fetch_eskom.py](../../../src/lfm/scripts/fetch_eskom.py), [fetch_economy.py](../../../src/lfm/scripts/fetch_economy.py); source profile for originals | Pack p7 observations. Proposed integration targets [generation.py](../../../src/lfm/model/demand/generation.py), [agriculture.py](../../../src/lfm/model/demand/agriculture.py), [industrial.py](../../../src/lfm/model/demand/industrial.py). GWh/value added must be translated to fuel litres with sourced parameters. |
| Road/rail source revision | [freight_payload_statssa_review.csv](../../../assumptions/2026/timeseries/freight_payload_statssa_review.csv), [revision metadata](../../../assumptions/2026/timeseries/freight_payload_statssa_review.sources.json) | [December 2024 PDF](../../../external/data/raw/demand_drivers_20261006/P7162December2024.pdf), [December 2025 PDF](../../../external/data/raw/demand_drivers_20261006/P7162December2025.pdf); [collect_freight_review.py](../../../src/lfm/scripts/collect_freight_review.py) | Pack p7 only; road-to-rail fuel lever not integrated. Use one report vintage, then source tonne-km/load and diesel intensity. |
| Refining capacity scenarios | [refinery_capacity_reported.csv](../../../assumptions/2026/timeseries/refinery_capacity_reported.csv), [review_capacity_scenarios.yaml](../../../assumptions/2026/review_capacity_scenarios.yaml) | FIASA report above and [CEF source capture](../../../external/data/raw/fuel_supply_review_20261006/cef_refinery_update.html); [collect_supply_review.py](../../../src/lfm/scripts/collect_supply_review.py) | Pack p8 only. Capacity is not output; authored future dates do not overwrite engine utilisation/yields. |
| Storage and Transnet lease sites | [storage_transnet_pipelines_depots.csv](../../../assumptions/2026/infrastructure/storage_transnet_pipelines_depots.csv), [source metadata](../../../assumptions/2026/infrastructure/storage_transnet_pipelines_depots.sources.yaml) | [Transnet page capture](../../../external/sources/transnet_tpl_leasing_2026/tpl-leasing-opportunities.html); original RFP PDFs in that same folder | Storage context in pack; no operational logistics engine or actual market share established. Lease opportunities are conditional, not operating supply. |

**Files not yet shared:** `external/data/refresh_20261005/raw/` contains prior
department, Stats SA, NaTIS, naamsa, Eskom and other downloads. Its 247 files
remain local after the bulk-upload rejection. The extracted CSVs linked above
are on main; availability of a CSV does not mean its underlying PDF/workbook is
also shared. Record missing originals explicitly when investigating a row.

**Where freshness and refresh are documented:** [source_profile_2026_10_05.csv](../../../output/delivered/source_profile_2026_10_05.csv)
lists refresh routes and input shapes; [source_connectivity_2026_10_05.csv](../../../output/delivered/source_connectivity_2026_10_05.csv)
records earlier URL probes. These are dated checks, not live connectivity today.
World Bank is API-based; many department/operator/Stats SA sources require
document downloads. A reachable page does not establish a complete refresh.
Use the individual fetcher linked above, preserve new raw files in a dated
folder, compare overlapping observations and review changes before adoption.

## Pack and diagnostic reference files

- [Current PowerPoint](../../../pptx/output/delivered/Vopak_Week1_Analytical_Pack_2026_10_06.pptx) and [PDF](../../../pptx/output/delivered/Vopak_Week1_Analytical_Pack_2026_10_06.pdf): stable filenames, 16 pages; original cover/closing retained.
- [Source audit workbook](../../../output/delivered/Liquid_fuels_source_audit_2026_10_05.xlsx): Direction, provincial gaps and repeated keys give row-level investigation leads.
- [Source profile](../../../output/delivered/source_profile_2026_10_05.html): input shapes, consuming functions and refresh routes. Its engine-use counts describe the 5 October diagnostic, not a new 6 October adoption audit.
- [Partner-story gap register](../../../pptx/story/partner_story_gap_register_2026_10_06.json): questions, closure evidence and owners. Use current pack page numbers below; older evidence strings retain earlier page references.
- Local prior refresh downloads: `external/data/refresh_20261005/manifest.json` inventories 247 raw files, 110,363,392 bytes. These files are preserved locally, not published on main. Automatic approval review rejected the bulk upload because contents/provenance are not fully verified; explicit approval is required to publish this payload. Hashes establish file identity only. Exact URL/download provenance and numerical accuracy still require source review.

## Feedback checklist: completed presentation changes versus open analysis

| SCR / pack pages | Feedback incorporated | Remaining gap / close-out evidence | Lead |
|---|---|---|---|
| Overview / 2 | SCR leads the analytical story; linked summary table and clickable section chevrons. Visible SCR breadcrumbs removed; analytical subtitles 14 pt. | Confirm today's priorities and acceptance tolerances; do not interpret a completed exhibit as a closed evidence gap. | Nigel / Manish |
| S1 / 3–4 | Provincial demand heatmap, explicit four-region grouping, storage context and provincial sales time series. | Latest complete extract is 2022; 2023 has Q1 only. Resolve six annual provincial/national differences and 26 exact province/product/year completeness flags against quarters and original workbook cells. | Manish |
| S2 / 5–6 | Collected 2024 national sales/trade; source-disagreement flag. Provincial origin illustration clearly labelled. | Matched domestic output, exports and stock movements; petrol/diesel imports by entry port. Provincial import/domestic allocation remains unsupported. | Manish; Nigel source access |
| C1 / 7 | Passenger/freight stock, agriculture, industry, power and road/rail payload; EV, plug-in hybrid and conventional hybrid sales restored. Every series indexed to 2024 = 100. | Fleet fuel mix, retirements, mileage, efficiency and sector fuel-intensity bridges. Sales are not fleet penetration; activity is not fuel litres. EV scale is explicitly 0–400; activity scales 0–120. | Manish; Nigel lever review |
| C2 / 8 | Capacity history and two conditional cases on the same 0–800 thousand bbl/day axis: 358 versus 758 after a 400 addition. | Capacity is not production. Resolve plant keys, operating status, utilisation, product yields and the gas/liquid mechanism. Illustrative FID 2029 is not sanctioned; future addition is conditional. | Manish; Henry technical review |
| C3 / 9–10 | Illustrative road-cost accessibility and competing Durban, Matola/Maputo and Walvis Bay gateway map to a common inland market. | Same product, destination, period and full delivered-cost components; actual tariffs, capacity and cross-border/customer access. These maps do not establish fuel service or an operational catchment. | Manish; Nigel selects comparison |
| R1 / 11–14 | Unique-flow arithmetic, all four regional demand totals, competitor detail, volume conditions and common-scale storage chart including Transnet lease sites. | Actual Vopak unique deliveries and share; compatible usable tanks, routes, contracts and switching rights. Gross capacity and conditional lease tanks are not throughput or available supply. Illustrative volumes are not forecast capture. | Nigel client records; Manish reconciliation |
| R2 / 15 | Investment/service assessment retained as optional after the flow case. | Do not prioritise storage sizing ahead of model integration and evidenced incremental customer demand. | Nigel |

## Today's focus: ordered work and specific handbacks

| Priority | Manish's work on 6 October | Concrete handback / acceptance evidence | Decision or support |
|---|---|---|---|
| 1 | Pull main, reproduce both existing scenarios without changing inputs, retain dated outputs. | Commands, commit, input hashes, run folders and key petrol/diesel totals. Explain any difference from the existing baseline. | Nigel agrees comparison outputs/tolerances. |
| 2 | Extend the existing source-to-model mapping. The 5 October diagnostic found 29 of 66 blocks requested by the engine; all 24 sources.* blocks were staged. | For every block: used, staged unused, reporting-only or unresolved; source file/cell, scalar/time-series/group/snapshot, units, transformation, consuming function and affected output. No claim of 100% source accuracy from coverage alone. | Nigel reviews the first integration choice. |
| 3 | Investigate exact flagged records before changing values: provincial completeness/ties; 558 extra refinery rows; 15 extra historical rows including repeated jet keys. | Old value and source vintage, competing/proposed value, original workbook cell, reason, proposed resolution, affected calculation/output, owner and review status. Missing quarters are not zero; do not sum/deduplicate repeated keys automatically. | Nigel reviews corrections separately from assumption changes. |
| 4 | Define demand and supply levers now, using the page 7 evidence as context. | Baseline and alternatives, units, start/ramp dates, evidence, equation/product, dependency and expected direction for each lever. Priorities: freight to rail; BEV/PHEV/hybrid uptake; mileage/efficiency; OCGT diesel; agriculture/industry intensity; plant availability/yields. | Nigel agrees alternatives; Henry reviews production mechanisms. |
| 5 | Prepare one integration candidate, starting with macro/GDP per capita if its basis and forecast boundary can be reconciled. | Current input → source-backed proposal → transformation → consuming function; explain GDP/population consistency, real-price basis, actual/forecast boundary and extension to 2050. Before/after petrol/diesel output comparison; registered inputs and targeted checks. If evidence is insufficient, return the exact blocker rather than invent an extension. | Nigel reviews the candidate before adoption. |
| 6 | Record refresh reliability for the candidate and its key URLs. | Separate URL response, successful full download, parser completeness and latest observation; retain original and retry failures, hashes, API/download/manual method and safe fallback. Partial failures must not erase prior data. | Manish verifies; Nigel resolves inaccessible evidence. |
| Supporting | Define the first customer/product/destination comparison and client data request. Use the existing storage/route inventory. | Client receipt/delivery/transfer/destination fields and matched period; delivered R/litre cost components, capacity and access gates. Do not turn Week 1 into a broad infrastructure rebuild. | Nigel obtains client data; route work follows integration capacity. |

## Exact new source flags to discuss

| Flag | Existing / earlier record | New / competing record | Required disposition |
|---|---|---|---|
| 2024 diesel imports | FIASA staged 14.793 bn litres | Government report 10.8 bn litres; difference −3.993 bn litres | Source/scope disagreement, not approved correction. Reconcile definitions, units and period; preserve both records. [Flag CSV](../../../output/delivered/supply_review_2026_10_06/trade_source_flags.csv). |
| 2024 road payload | December 2024 report: 790.611 million tonnes | December 2025 report: 979.798 million tonnes; +189.187 million tonnes | Revision flag; use one report vintage for overlapping years. Do not claim modal shift from the revision; payload is not tonne-km. |
| Fleet fuel mix | NaTIS total vehicle classes | No verified petrol/diesel/EV stock split supplied by this extract | Mark unknown; BEV/hybrid annual new sales do not resolve fleet stock, survival or mileage. |
| Price freshness | Annual price extract ends 2023 | No complete annual 2024 replacement established here | Refresh before real-price response calibration; no extrapolated index base. |

## End-of-day and Week 1 review

Today's proposed handback is a reproducible baseline, completed first-pass mapping,
row-level investigation results, lever definitions and one reviewed integration
candidate (or its precise evidence blocker). Full fleet/history reconciliation
continues into Week 2. The proposed 9 October Week 1 review tests those outputs;
infrastructure inventory and first-route construction are secondary, not Week 1 gates.

For current share, require unique final customer deliveries divided by matched
regional demand for the same product/period. Count shared Durban–Lesedi transfers
once. Additional contestable volumes require cost, physical capacity and customer
rights to pass separately; unknown access is not zero and competitors' volumes
are not automatically capturable.

Validation on 6 October: governance coverage passes with 52 open exceptions;
8 relevant source-profile, source-audit, supply-review and freight-review tests pass.
The 16-page updated deck has passed package/bounds checks and page 7 was rendered.
This does not establish independent model review, data accuracy or formal-use approval.

Publish this checklist to main; the current delivered pack is already there.
The local raw-download payload remains a sharing gap pending approval; do not
claim Manish can access it from main. Manish should pull main after publication.
Record actual meeting decisions separately; this document contains preparation
and proposed actions.
