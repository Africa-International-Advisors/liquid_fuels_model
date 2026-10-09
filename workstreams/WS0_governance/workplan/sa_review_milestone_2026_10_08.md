# South Africa review milestone 8 October 2026

The current review is the 43-page v27 South Africa story, refreshed from Manish's workbook. It preserves the v25 investment illustration and Nigel's existing taglines, adds four exhibits, and updates supporting evidence and outstanding requests. Publishing a review pack does not approve the forecast, investment assumptions or expenditure.

## Start here

- [Current PDF](../../../pptx/output/delivered/supporting/SA_Market_Story_2026-10-08_v27.pdf) and [editable PowerPoint](../../../pptx/output/delivered/supporting/SA_Market_Story_2026-10-08_v27.pptx).
- [Canonical story](../../../pptx/story/sa_market_story_v27_2026_10_08.json). Preserve Nigel's taglines unless a reviewed change is recorded.
- [Workbook page audit](../../WS3_reporting_delivery/sa_pack_workbook_audit_2026_10_08.csv) and [63-cell evidence trace](../../../pptx/story/sa_workbook_evidence_v26_2026_10_08.json); source branch commit `8a3c884`.
- [Data request DR01–DR09](../../../output/delivered/investment_bridge_2026_10_08/data_request.csv). Prepared, not sent. Nigel coordinates commercial requests; do not represent a request as received evidence.
- [Worked case](../../../output/delivered/vopak_illustration_2026_10_08/index.html), [registered assumptions](../../../assumptions/2026/vopak_investment_illustration.yaml) and [implementation log](sa_illustrative_investment_2026_10_08.csv).

## Milestones and acceptance

Owners below follow existing workstream responsibilities; dates are not new commitments. Complete each evidence gate before relying on its conclusion.

| Milestone | Owner and review | Required handback | Acceptance condition |
|---|---|---|---|
| M0 Review baseline | Nigel | v27 and this handover | Story and illustrative calculations preserved; current links resolve. Completed for review, not business approval. |
| M1 Reconciled baseline | Manish; Nigel reviews | DR01, product/year balance CSV, source definitions and reconciliation note | Production, imports, exports and stock changes use compatible definitions; statistical differences remain explicit. Never infer production from an unexplained residual. |
| M2 Actual terminal position | Nigel coordinates Vopak; Manish reconciles | DR02/03/05: 36 months of movements, eligible working tanks, receipt/dispatch limits and customer commitments | Separate Durban and Lesedi; deduplicate inter-terminal deliveries; reconcile actual throughput, turns and stock occupancy. Replace page 11 evidence gaps only when supported. |
| M3 Accessible corridor volumes | Manish; Nigel reviews | DR04, matched cost and access table for Durban, Maputo/Matola, Walvis Bay and domestic origins | Same product, destination, date and tax basis; verified terminal gates, customer points, service rights, capacity and border constraints. A mapped route is not tanker access or commercial competitiveness. |
| M4 Calibrated nine worlds | Manish; Nigel reviews | DR07/08, annual L/M/H demand and plant-output inputs with lever register and dependency checks | Calibrate rail tonne-km, EV turnover, ICE efficiency, power dispatch and plant output. Include Secunda gas/MRG, SAPREF, Natref and PetroSA. No double counting; capacity is not production. Medium is an agreed baseline, not an arbitrary midpoint. |
| M5 Investment decision | Nigel coordinates finance/engineering; Manish models; Henry independent review proposed | DR06, incremental existing/improvement/expansion cash flows for all nine worlds, thresholds and downside tests | Validate rents and chargeable services, capex, schedule, tax, working capital and hurdle rate. Compare incremental alternatives. Rail/corridor and EV investments require their own evidence and economics; DR09 covers EV adjacency. |
| M6 Approval readiness | Nigel accountable; reviewer and approver to confirm | Signed assumption decisions, independent review, closed applicable exceptions and investment paper | Apply GATE_CHECKLIST.md; record actual approval separately. Passing tests or committing to Git is not investment approval. |

Immediate priority: Manish reconciles DR01 and assembles DR04/07/08 public evidence; Nigel coordinates DR02/03/05/06. Hand back an evidence table with source, period, unit, observed/inferred/illustrative status, owner and unresolved gap. Do not wait for commercial inputs to complete independent public-source work.

## 8 October PS follow-up

The market sizing pack (built 9 October 2026 11:00: cover, national balance, issue tree, three demand deep dives, port and logistics, outstanding data, decisions and next steps) is the [PDF](../../../pptx/output/delivered/supporting/09102026_Vopak_Market_Sizing_v1100.pdf) and [editable PowerPoint](../../../pptx/output/delivered/supporting/09102026_Vopak_Market_Sizing_v1100.pptx). It supplements the v25 story. Nigel retains the original session transcript and marked storyboard locally; they are excluded from this public handback. Obtain the originals from Nigel before reviewing the session sources.

Manish's next handback has three parts: close the remaining evidence gaps, consolidate a reconciled current petrol/diesel baseline, and estimate the accessible annual market separately for Durban and Lesedi. Build the market-size calculation from destination demand, gross imports and exports, actual domestic production, feasible routes, competing supply and terminal access. Show ranges, assumptions and shared Durban-Lesedi flows explicitly. The approximately 20 billion litres discussed is a provisional consumption starting point, not imports or Vopak-accessible volume.

Prioritise reported historical Eskom diesel litres, provincial vehicle composition and efficiency evidence, the complete refinery picture including PetroSA/Mossgas, and port/pipeline capacity and access. Existing source collection does not establish that these gaps are closed. Retain originals and distinguish observations, estimates and proposed scenarios in the handback.

Nigel coordinates client movements/customer commitments (DR02/05), actual operating capacity (DR03), and commercial/project inputs (DR06). Manish can estimate accessible-market ranges while those inputs are pending; current capture and market share remain unverified until client evidence is reconciled. Compare achievable additional capture with existing assets and operational improvements before testing expansion economics. Nigel/Henry review scenario settings. The request register remains prepared, not sent, with no receipt recorded; this handback does not record approval or a new deadline.

Rebuild the pack with `python pptx/scripts/issue_tree_volumes.py` and then `pptx/scripts/build_market_sizing_issue_tree.ps1 -IncludeRequests -Layout flow` in PowerShell. It uses the preserved v25 Vopak master, its `1_Title` cover and named `Header only` layout, preserves previous deliveries, and exports the PPTX, PDF and PNGs. The builder checks bounds and text fit; visually inspect the exports before delivery.

## What the current numbers mean

The nine-world calculation is a steady-state illustration, not a calibrated annual forecast. Six cells retain existing assets, two prefer improvements and one prefers improvement plus tanks among the three authored packages. In the last case, tanks add only about R8m NPV over improvement alone. This is conditional on illustrative capture, tariffs, operating limits and capex, with pre-tax cash flows. It is not evidence that Vopak should invest.

Vopak annual reporting establishes asset and group context. Group occupancy is not terminal turns, group revenue intensity is not a Lesedi tariff, and rent may include guaranteed throughput. The further 40,000 m³ in the case is hypothetical, beyond reported Lesedi capacity; it is not the expansion already commissioned in 2025.

## Working instructions

Nigel works on `main`. Manish uses the agreed `manish-branch`, based on current `origin/main`; merge current main before each handback. Commit and push the analyst branch for Nigel's review. Do not force-push. See [branch workflow](branch_workflow.md).

Use the shared `.venv`, `requirements.txt` and existing presentation environment. Keep calculations in `src/lfm/model/`, registered inputs in YAML/CSV, and presentation-only code in `pptx/scripts/`. Preserve source originals, shipped assumptions and delivered versions. Use a new vintage/output path for new assumptions and results; some dated reporting scripts still target fixed paths and must be adapted before refresh.

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m lfm check --vintage 2026
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe pptx/scripts/check_sa_revision.py
```

The deck check needs locally rendered PNGs under the current QA path; they are generated, not committed. On a fresh clone, inspect the shipped PPTX/PDF and export renders with PowerPoint before running that check. The approved deck inherits the existing Vopak master and layout. The dated revision builders are historical edit steps, not an unattended build pipeline; v25's builder requires archived v24 and refuses to overwrite an existing delivery. Choose a new version before further edits. After export, visually inspect changed slides and refresh the current manifest, hashes and delivery index.

## Source recovery and repository size

Large downloaded map extracts, detailed map layers, the routing SQLite database and the 87 MB annual-report PDF remain preserved locally, excluded from Git. [Bulk inventory](sa_milestone_bulk_assets_2026_10_08.json) records their exact paths, sizes and SHA-256 hashes. A fresh clone does not contain these assets.

- Vopak annual report: https://www.vopak.com/system/files/Vopak_Annual_Report_2025.pdf . Restore to the path in the bulk inventory and verify the hash before claiming the same source vintage.
- Geospatial sources and recovery: [routing reference](../../../pptx/assets/maps/ROUTING_REFERENCE.md), [boundary reference](../../../pptx/assets/maps/GEOSPATIAL_REFERENCE.md), and `external/sources/geospatial/` metadata. OSM dated downloads use `python -m lfm.scripts.collect_osm_ranges`; a new network build uses `python -m lfm.scripts.build_osm_network` after resolving its output vintage. It refuses an existing delivered database.
- Metadata and compact map products are tracked. Retain OSM/Geofabrik attribution and licences. The graph is a connectivity diagnostic, not a validated truck-routing engine.
- If an original URL no longer returns the recorded hash, obtain the preserved original from Nigel or register the download as a new source vintage. Do not silently substitute it.

The delivered archive preserves story progression and Nigel's edited v18 source. Use the dated v27 pair as the current review pack. v25 and v26 are in `archive/story_versions/`; revision and standalone issue-tree builders use those archived sources. The active folder contains only v27 and the two-page issue-tree handback. The [cleanup record](../../../pptx/output/delivered/supporting/archive/records/cleanup_2026-10-08_v27.json) maps former paths; historical snapshots retain their original paths.

## Verification at this milestone

170 Python tests passed. Governance coverage passed with 57 open exceptions; formal readiness is still blocked by the recorded review and calibration gaps. v26 has 43 matching PPTX/PDF pages; bounds, titles, revised evidence content and render count passed. All pages were visually inspected, including the independent PDF renders. No independent model review or business approval is implied.

v26 adds industry demand on page 8, the issue tree on page 16, vehicle calibration on page 26 and the power fleet/cases on page 33. Outstanding requests are on page 18. Estimates retain their method and period labels; 2024 FIASA sales remain unverified. Sector and vehicle diagnostics do not adopt new model assumptions. Proposed power cases remain Nigel/Henry review items. Existing investment economics remain illustrative.

For a new build, obtain the exact workbook at `8a3c884:output/delivered/Demand_baseline_workshop_2026_10_08_history.xlsx`, retain its original hash, and recalculate a review copy in Excel under `runs/review/manish_workbook_2026_10_08_latest/`. The evidence JSON records both the source and cited cells. `pptx/scripts/prepare_sa_workbook_v26.py` reads that review copy; `pptx/scripts/build_sa_workbook_v26.ps1 -Attempt <new-name>` creates a private build using v25's master and named layouts. Preserve the delivered v26; use a new revision for later deliveries. `pptx/scripts/render_pdf_windows.ps1` renders the PDF independently under Windows PowerShell 5.1.

Latest visual revision, v27: page 8 replaces the sector table with three stacked horizontal-bar chart rows. All rows use a common zero-based 0-2bn litre scale; outlined bars distinguish 2024 estimates. Nine chart values were verified, the PowerPoint/PDF slide was visually inspected, and all other 42 pages retain their shape geometry and text. Rebuild with `pptx/scripts/build_sa_sector_charts_v27.ps1` from the preserved v26.
