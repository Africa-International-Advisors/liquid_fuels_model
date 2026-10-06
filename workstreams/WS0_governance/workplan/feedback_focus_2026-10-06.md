# 6 October: feedback checklist and Manish discussion

Start with the [standalone Manish handover instructions](manish_handover_2026-10-06.md),
including files to open and the stand-up meeting-record reference.

Purpose: source and reconcile the evidence behind the current diagnostics and
partner story before quantifying levers or adopting replacements. South Africa
petrol and diesel are the client focus; jet remains tracked separately.
Nigel reviews proposed changes; Manish investigates and implements explained
replacements. Henry reviews the technical mechanisms. Assignments and dates
below are proposed discussion targets, not recorded meeting commitments.

## Today's direction confirmed by Nigel

### Start instruction for Manish and his LLM

Preserve any local work, then start from the latest shared main:

```powershell
git fetch origin
git switch -c manish-branch origin/main
```

If that branch already exists, switch to it and merge `origin/main` using the
[branch workflow](branch_workflow.md). Do not recreate it or discard local changes.
Open [the PDF handover](../../../pptx/output/delivered/Vopak_Manish_Handover_2026_10_06.pdf):
page 6 is the five-package handback checklist; page 7 is the driver evidence checklist.

Copy this instruction into the LLM working on Manish's branch:

> Read AGENTS.md, CLAUDE.md, GATE_CHECKLIST.md and this dated runbook. Work through
> five packages: integrity, traceability, provincial demand after 2022, matched
> production/import/export/stock balance, and driver evidence. Use the exact
> source paths and staged fetch commands below. For drivers, collect passenger
> vehicles, freight, agriculture, industry (manufacturing and mining separately),
> power, electrification and GDP/price context. Also resolve refinery source/key
> flags under integrity and fuel-balance work. Preserve originals and existing
> observations; implement and test missing downloads/parsers. Return extracted
> data, a source-to-file-to-function map, old/new flags and sourced/partial/open
> status for every checklist item. Every open item needs an owner and next action.
> Do not silently replace assumptions or quantify lever scenarios today. Restore
> staging environment variables, run governance and relevant tests, then commit
> intended code, registered inputs and review evidence to Manish's branch. Publish
> that branch for Nigel's review; do not push analyst changes directly to main.

**Acceptance:** the five packages and seven driver categories each have reviewable
evidence or an explicit gap. A passing fetch command alone does not close a row.
Nigel reviews source fidelity and accepted input changes before model integration.

Nigel works on main. Manish creates his own branch from current origin/main and
returns his changes for review. See [branch commands](branch_workflow.md).
Today's objective is **data first**, not quantified lever scenarios or a GDP
integration candidate. Source the evidence needed to update the client pages,
resolve integrity flags, and expose missing observations. Integration follows
reviewed evidence; broader infrastructure and investment work remain secondary.

| Priority | Exact files to start with | Work today | Handback |
|---|---|---|---|
| 1 Data integrity | [Audit workbook](../../../output/delivered/Liquid_fuels_source_audit_2026_10_05.xlsx): Direction, Provincial gaps, Repeated keys; [source profile](../../../output/delivered/source_profile_2026_10_05.html) | Check incomplete quarters, province/national differences, repeated refinery/history keys, unsupported baselines/elasticities and missing originals. Use the source-file table below. | Flag -> old value -> source cell/page -> competing/proposed value -> reason -> resolved/open. Preserve originals; no silent deduplication. |
| 2 Source traceability | [Source profile CSV](../../../output/delivered/source_profile_2026_10_05.csv), [sources.yaml](../../../assumptions/2026/sources.yaml), fetchers under `src/lfm/scripts/` | Trace each priority dataset from publisher/API/download to original file, extracted CSV and consuming function. Distinguish engine-used, staged unused and reporting-only. | Source URL, exact file path, period/units/geography, extraction function, consuming calculation, refresh method and any failure. |
| 3 Provincial demand from 2022 to date | [Annual provincial CSV](../../../assumptions/2026/timeseries/fuel_sales_department_by_province.csv), [quarterly provincial CSV](../../../assumptions/2026/timeseries/fuel_sales_department_by_province_quarterly.csv), [national sales](../../../assumptions/2026/timeseries/fuel_sales_department.csv), [FIASA sales](../../../assumptions/2026/timeseries/fuel_sales_fiasa.csv) | First verify the department report's provincial petrol/diesel charts through 2024. Look for underlying tables. Then seek 2025 and latest 2026 YTD evidence; source provincial drivers for any period without observed fuel sales. | Province by petrol/diesel by period table; observed/reconstructed/estimated status, source page and national tie. Do not present a chart-read estimate as an exact published table value or annualise incomplete YTD silently. |
| 4 Reconcile domestic production and trade | [Energy balance](../../../assumptions/2026/timeseries/energy_balance_department.csv), [FIASA trade](../../../assumptions/2026/timeseries/fuel_trade_fiasa.csv), [government trade](../../../assumptions/2026/timeseries/fuel_trade_department_review.csv), [flags](../../../output/delivered/supply_review_2026_10_06/trade_source_flags.csv) | Assemble actual production, imports, exports and stock movements for the same petrol/diesel periods. Use SARS product-specific trade data and energy/operator production evidence. Resolve the competing 2024 diesel-import values. | Product by period balance with units, definitions, source, stock treatment and unexplained residual. Separate finished fuel from crude and other petroleum products. |
| 5 Source all driver/lever pages | Existing CSVs and official source links below; pack p7 demand drivers and p8 refining history | Collect and reconcile observed series first: passenger/freight, agriculture, manufacturing, mining, power, EVs and refinery output/status. | One source-and-coverage row per chart series; original download, extract, dates, geography, units, revisions and open gaps. No high/medium/low lever calibration required today. |

## Commands for Manish's LLM

Run from the repository root on Manish's branch. These fetchers write CSVs,
so use a separate candidate folder first. This setup preserves the existing
assumptions and available raw cache; new downloads and extracts remain under runs.

```powershell
$fetchRoot = Join-Path (Get-Location) ("runs/manish_fetch_" + (Get-Date -Format yyyyMMdd_HHmmss))
New-Item -ItemType Directory -Path "$fetchRoot/assumptions", "$fetchRoot/data/raw" -Force | Out-Null
Copy-Item -LiteralPath 'assumptions/2026' -Destination "$fetchRoot/assumptions/2026" -Recurse
if (Test-Path -LiteralPath 'external/data/raw') {
    Get-ChildItem -LiteralPath 'external/data/raw' | Copy-Item -Destination "$fetchRoot/data/raw" -Recurse
}
$priorAssumptionsDir = $env:LFM_ASSUMPTIONS_DIR
$priorDataDir = $env:LFM_DATA_DIR
$env:LFM_ASSUMPTIONS_DIR = "$fetchRoot/assumptions"
$env:LFM_DATA_DIR = "$fetchRoot/data"
```

In this same PowerShell session, execute the fetchers in order. Capture each
command's stdout/stderr, exit code, source warnings and resulting coverage.
When running commands separately, a failure in one must not be hidden by the
exit code of a later successful command.

| Order | Dataset | Command | Main candidate extracts under `$fetchRoot/assumptions/2026/timeseries/` |
|---|---|---|---|
| 1 | Department sales, provincial history, balances and prices | `.\.venv\Scripts\python.exe -m lfm.scripts.fetch_energy_dept --vintage 2026` | `fuel_sales_department.csv`, `fuel_sales_department_by_province.csv`, quarterly companions, `energy_balance_department.csv`, price CSVs |
| 2 | FIASA sales and imports/exports | `.\.venv\Scripts\python.exe -m lfm.scripts.fetch_fuel_sales --vintage 2026` | `fuel_sales_fiasa.csv`, `fuel_trade_fiasa.csv` |
| 3 | GDP/population, Treasury and locally downloaded Stats SA GDP | `.\.venv\Scripts\python.exe -m lfm.scripts.fetch_economy --vintage 2026` | `macro_worldbank.csv`, `macro_statssa.csv` if the required workbook is present, `gdp_growth_treasury.csv` |
| 4 | Vehicle stock and registrations | `.\.venv\Scripts\python.exe -m lfm.scripts.fetch_natis --vintage 2026` | `vehicle_population_natis.csv`, `new_vehicle_registrations_natis.csv`, annual companion |
| 5 | BEV/PHEV/hybrid sales and vehicle market | `.\.venv\Scripts\python.exe -m lfm.scripts.fetch_naamsa --vintage 2026` | `nev_sales_naamsa.csv`, `new_vehicle_market_naamsa.csv` |
| 6 | Eskom/IPP OCGT generation | `.\.venv\Scripts\python.exe -m lfm.scripts.fetch_eskom --vintage 2026` | `ocgt_generation_eskom.csv` |

For an individual parser rerun without downloading, append `--offline`. It only
works if the original files are already in the candidate raw folders. An offline
rerun is not a test of current publisher connectivity or freshness.

The existing single-command orchestrator is
`.\.venv\Scripts\python.exe -m lfm.scripts.refresh_sources --vintage 2026`.
It runs the above fetchers plus ACSA, lists failed commands, returns nonzero on
failure and compares department/FIASA sales. Use it instead of rerunning all six
individually once source-specific problems are understood. It does not fetch all
the new source leads below or perform a complete production/trade reconciliation.

**Required work not covered by those six commands:**

- Download the latest Stats SA **GDP Time series** workbook from P0441 into
  `$fetchRoot/data/raw/statssa/` before the economy fetch. The existing reader
  expects `GDP P0441*Time series*.xlsx` and reads the **Annual** sheet. Quarterly
  2026 observations need parser support; presence of the Q2 workbook alone does
  not establish a quarterly extract.
- Add and test extraction for the newer provincial market report; the department
  workbook fetcher does not automatically extract its provincial PDF charts.
- Add and test current Stats SA mining P2041, manufacturing P3041.2 and land
  transport P7162 downloads/parsers. The existing freight-review extractor only
  rereads two fixed December PDFs; it is not a current monthly downloader.
- Add and test product-specific SARS trade collection or ingest a documented
  manual export. The FIASA command does not download SARS records.

The LLM should first inspect existing modules under `src/lfm/sources/` and
`src/lfm/scripts/`, then implement missing retrieval/parsing there. Preserve
originals, compare overlapping old/new values and test source values, units,
duplicates, coverage, revisions and failed-fetch preservation. Do not adopt
candidate CSVs just because a command exits zero.

Restore the original environment settings before running the normal repository
governance check. If the LLM wraps the commands in a script, put restoration in
`finally` so failures cannot leave candidate inputs selected:

```powershell
$env:LFM_ASSUMPTIONS_DIR = $priorAssumptionsDir
$env:LFM_DATA_DIR = $priorDataDir
.\.venv\Scripts\python.exe -m lfm check --vintage 2026
.\.venv\Scripts\python.exe -m pytest -q tests/test_sources_energy_dept_eskom.py tests/test_sources_economy.py tests/test_sources_statssa.py tests/test_sources_natis.py tests/test_sources_naamsa.py tests/test_sources_fiasa.py tests/test_supply_review.py tests/test_freight_review.py
```

Also run new tests for any retrieval/parser changes. Return per-source outcomes,
original and candidate paths, old/new flags and unresolved gaps. Reviewed data
promotion must deliberately update the vintage declarations/register; today's
candidate downloads do not alter the existing fuel baseline.

## Official source leads

Checked on 6 October. A publisher listing is evidence of availability, not a
completed extraction. Keep last complete year and latest YTD separate.

| Page / data need | Official source to open | What it gives / remaining limit |
|---|---|---|
| pp3-4 Provincial petrol/diesel | [Department petrol and diesel market overview 2015-2024](https://www.dmre.gov.za/LinkClick.aspx?fileticket=ExxZyYuQywM%3D&portalid=0) | Search-indexed report includes provincial sales charts through 2024, including petrol Figure 8. Verify original PDF and underlying numbers before adoption; web PDF fetch timed out during this review. Existing CSV remains through 2022. |
| Provincial update proxies | [Stats SA provincial GDP P0441.2 for 2024](https://www.statssa.gov.za/?PPN=P0441.2&SCH=74226&page_id=1854) | Provincial economic activity, not fuel litres. Collect price basis/sector detail and release vintage; do not apply national sector indices as observed provincial fuel sales. |
| p7 Agriculture and macro/sector activity | [Stats SA GDP P0441](https://www.statssa.gov.za/?page_id=1854&PPN=P0441) | Q2 2026 listing has the GDP time-series workbook. Current macro_statssa.csv holds annual series; inspect/download quarterly observations for the 2026 update. Agriculture includes forestry/fishing; GVA is not diesel consumption. |
| p7 Manufacturing | [Stats SA manufacturing P3041.2](https://www.statssa.gov.za/?page_id=1854&PPN=P3041.2) | July 2026 release and Excel/ASCII time series listed. Collect production-volume index and distinguish it from nominal sales. |
| p7 Mining | [Stats SA mining P2041 archive](https://www.statssa.gov.za/?PPN=P2041&SCH=1039&page_id=1866&page_no=1) | July 2026 listed as latest at review. Collect production indices by relevant mineral group; preserve revisions and index base. |
| p7 Freight and passenger activity | [Stats SA land transport P7162](https://www.statssa.gov.za/?page_id=1854&PPN=P7162) | Inspect freight/passenger tables and scope. Payload is not tonne-km; public passenger transport is not the complete private-car market. Keep one revision vintage. |
| p7 Passenger/freight fleet and EVs | NaTIS/naamsa existing extract links in the file table; their fetchers contain publisher URLs | Vehicle classes/fleet counts and BEV/PHEV/hybrid sales need their own sources. Stats SA activity series do not establish fleet fuel mix or EV penetration. |
| p7 Diesel for power | Eskom generation extract/source metadata in the file table | Source OCGT generation and actual diesel use where reported. General electricity output is not OCGT diesel consumption. |
| p7 Prices | [Existing annual prices](../../../assumptions/2026/timeseries/fuel_prices_department_annual.csv), [monthly prices](../../../assumptions/2026/timeseries/fuel_prices_department.csv), department price publications; Stats SA CPI for deflation | Collect later monthly petrol/diesel prices; identify inland/coastal and retail/wholesale scope. Current annual extract ends 2023. CPI is a deflator, not petrol/diesel sales volume. |
| pp9-10 Competing routes | Transnet/NERSA tariffs, operator quotations, route access and border evidence; existing route exhibits | Stats SA activity data does not provide a full delivered R/litre route cost. Obtain dated comparable components for the same destination; keep unsupported costs illustrative. |
| p5 Domestic production/imports/exports; p8 refinery status | [SARS detailed trade downloads](https://tools.sars.gov.za/tradestatsportal/data_download.aspx), [SARS trade statistics](https://www.sars.gov.za/customs-and-excise/trade-statistics/), energy balance, FIASA and plant/operator reports | Filter petrol/diesel tariff lines and verify quantities/units, not only rand values. SARS trade is not domestic production. Production requires matched energy/operator records; nameplate capacity is not actual output. |

Use the existing extracted inputs and fetchers first. Preserve any new downloads
under a dated `external/data/raw/` folder, then extract and register reviewed
observations deliberately. No new series is adopted into the engine by this brief.

For priority 1, inspect these baseline settings:
[vehicles.yaml](../../../assumptions/2026/vehicles.yaml),
[agriculture.yaml](../../../assumptions/2026/agriculture.yaml),
[industrial.yaml](../../../assumptions/2026/industrial.yaml) and
[marine.yaml](../../../assumptions/2026/marine.yaml), alongside the
[refinery CSV](../../../assumptions/2026/timeseries/refinery_production.csv) and
[historical demand CSV](../../../assumptions/2026/timeseries/historical_demand.csv).
For an unsupported baseline/elasticity, return the current parameter, its claimed
source, the exact evidence located and any unresolved definition; do not replace
it with an activity index or a borrowed parameter just to remove the flag.

For priority 2, use these columns in the handback: dataset; source URL; original
file path and page/sheet/cell; extracted CSV/YAML path; API/download/manual;
fetcher and parser function; engine/reporting consumer; used/staged/reporting;
latest complete year and latest partial period; units; geography; old/new value
and vintage; refresh outcome; unresolved issue and owner. Publisher availability,
download success, parse success and numerical verification are separate checks.

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

- [Current PowerPoint](../../../pptx/output/delivered/Vopak_Week1_Convergence_2026_10_06.pptx) and [PDF](../../../pptx/output/delivered/Vopak_Week1_Convergence_2026_10_06.pdf): current Convergence storyline, 22 pages; supersedes the earlier Analytical Pack reviewed below.
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

## Exact new source flags to discuss

| Flag | Existing / earlier record | New / competing record | Required disposition |
|---|---|---|---|
| 2024 diesel imports | FIASA staged 14.793 bn litres | Government report 10.8 bn litres; difference −3.993 bn litres | Source/scope disagreement, not approved correction. Reconcile definitions, units and period; preserve both records. [Flag CSV](../../../output/delivered/supply_review_2026_10_06/trade_source_flags.csv). |
| 2024 road payload | December 2024 report: 790.611 million tonnes | December 2025 report: 979.798 million tonnes; +189.187 million tonnes | Revision flag; use one report vintage for overlapping years. Do not claim modal shift from the revision; payload is not tonne-km. |
| Fleet fuel mix | NaTIS total vehicle classes | No verified petrol/diesel/EV stock split supplied by this extract | Mark unknown; BEV/hybrid annual new sales do not resolve fleet stock, survival or mileage. |
| Price freshness | Annual price extract ends 2023 | No complete annual 2024 replacement established here | Refresh before real-price response calibration; no extrapolated index base. |

## End-of-day and Week 1 review

### Handback checklist: five distinct work packages

Unchecked items below are requirements, not an assertion that no evidence exists.
Manish returns each as ready for review, partial or open, with an owner and next
retrieval action for missing evidence. Nigel reviews adoption and integration.

- [ ] **Integrity:** resolve the provincial completeness/tie flags and repeated
  refinery/history keys; log old value, source cell, proposed value and reason.
- [ ] **Traceability:** map publisher -> original -> extract -> consuming function;
  include exact paths and identify originals absent from the shared repository.
- [ ] **Provincial demand:** collect observed petrol/diesel sales after 2022;
  verify newer chart/table evidence, seek 2025/2026 and reconcile national totals.
- [ ] **Fuel balance:** match production, imports, exports and stock movements by
  product/period/units; explain the residual or leave it explicitly open.
- [ ] **Driver evidence:** return the seven categories below with originals and
  extracts; implement and test missing retrieval/parsers on Manish's branch.

Driver collection checklist (annual new sales and fleet stock remain separate):

- [ ] **Passenger vehicles:** NaTIS passenger stock/registrations; separately
  source petrol/diesel stock split, mileage and efficiency or mark them open.
- [ ] **Freight:** NaTIS goods-vehicle stock and Stats SA P7162 road/rail payload;
  tonne-km where available. Use one revision vintage; tonnes are not tonne-km.
- [ ] **Agriculture:** Stats SA P0441 activity plus separate evidence of diesel
  consumption/intensity; national activity does not establish provincial litres.
- [ ] **Industry:** separate manufacturing P3041.2 and mining P2041 output series;
  keep activity indices distinct from fuel consumption.
- [ ] **Power:** Eskom and IPP OCGT generation plus reported diesel burn where
  available; distinguish financial/calendar years and GWh/litres.
- [ ] **Electrification:** naamsa BEV, PHEV and conventional hybrid new sales;
  fleet stock/survival where available. Sales are not penetration; hybrids use fuel.
- [ ] **Economic context:** Stats SA real GDP and department petrol/diesel prices;
  identify nominal/real treatment and refresh periods. No elasticity calibration today.

Every series needs source URL/table, original path, extracted CSV, coverage,
units and revision check. Source collection, checking and reviewed integration
are distinct stages; collecting an activity series does not quantify a fuel lever.

[PDF handover checklist](../../../pptx/output/delivered/Vopak_Manish_Handover_2026_10_06.pdf)
uses the same five work packages and seven driver categories.

Today's handback is a resolved/open flag table, source-to-file-to-function map,
new provincial demand evidence or an explicit evidence gap, a matched national
production/import/export reconciliation, and sourced driver series with coverage
and revisions. It is not a quantified lever matrix or an approved integration.
Nigel tightens the SCR pack; the afternoon review links Manish's evidence to the
exhibits and identifies remaining gaps. The proposed 9 October Week 1 gate remains
a reproducible baseline, reviewed mapping and defined integration gaps. Lever
quantification follows sourcing; infrastructure is not a Week 1 gate.

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


## Pending visual feedback - canonical Convergence pack, 6 October 2026

Status: logged only. Nigel requested feedback collection before implementation.
Reference: current 22-page [Convergence PDF](../../../pptx/output/delivered/Vopak_Week1_Convergence_2026_10_06.pdf), page 8 (C4 refinery capacity).

| Item | Feedback / finding | Proposed action | Status |
|---|---|---|---|
| VIS-01: blue explanatory text | Scenario headings, history disclaimer, 2036 volume labels and reported-output note feel too prominent; they compete with the title and charts. | Review dark grey for these text elements; retain navy for charts, navigation and the divider. Nigel to review the treatment before applying it across the pack. | Pending; no slide changes |
| VIS-02: divider brand colour | Nigel asked whether the filled circle uses the Vopak logo blue. Page 8 PPTX shape XML confirms circle fill and outline are both `#0A2373`. `pptx/brand_configs/vopak.py` records the same value as the dominant opaque pixel sampled from the supplied logo; `footer_layout.py` uses the brand primary accent and a white arrow. | Keep the existing colour pending further feedback. The current divider matches the recorded logo-derived primary blue. | Checked; no slide changes |

Owner: Nigel (visual direction); presentation builder implements after instruction.
Revisit when Nigel finishes the feedback round and requests action. This entry
changes no deck, model input or analytical conclusion.
