# South Africa review milestone 8 October 2026

The milestone is the 39-page v25 South Africa review story, its evidence trail and a reproducible illustrative investment calculation. Use this as the baseline for the next analytical handback. Publishing it does not approve the forecast, investment assumptions or expenditure.

## Start here

- [Current PDF](../../../pptx/output/delivered/supporting/SA_Market_Story_2026-10-08_v25.pdf) and [editable PowerPoint](../../../pptx/output/delivered/supporting/SA_Market_Story_2026-10-08_v25.pptx).
- [Canonical story](../../../pptx/story/sa_market_story_v25_2026_10_08.json). Preserve Nigel's taglines unless a reviewed change is recorded.
- [Data request DR01–DR09](../../../output/delivered/investment_bridge_2026_10_08/data_request.csv). Prepared, not sent. Nigel coordinates commercial requests; do not represent a request as received evidence.
- [Worked case](../../../output/delivered/vopak_illustration_2026_10_08/index.html), [registered assumptions](../../../assumptions/2026/vopak_investment_illustration.yaml) and [implementation log](sa_illustrative_investment_2026_10_08.csv).

## Milestones and acceptance

Owners below follow existing workstream responsibilities; dates are not new commitments. Complete each evidence gate before relying on its conclusion.

| Milestone | Owner and review | Required handback | Acceptance condition |
|---|---|---|---|
| M0 Review baseline | Nigel | v25 and this handover | Story and illustrative calculations preserved; current links resolve. Completed for review, not business approval. |
| M1 Reconciled baseline | Manish; Nigel reviews | DR01, product/year balance CSV, source definitions and reconciliation note | Production, imports, exports and stock changes use compatible definitions; statistical differences remain explicit. Never infer production from an unexplained residual. |
| M2 Actual terminal position | Nigel coordinates Vopak; Manish reconciles | DR02/03/05: 36 months of movements, eligible working tanks, receipt/dispatch limits and customer commitments | Separate Durban and Lesedi; deduplicate inter-terminal deliveries; reconcile actual throughput, turns and stock occupancy. Replace page 10 evidence gaps only when supported. |
| M3 Accessible corridor volumes | Manish; Nigel reviews | DR04, matched cost and access table for Durban, Maputo/Matola, Walvis Bay and domestic origins | Same product, destination, date and tax basis; verified terminal gates, customer points, service rights, capacity and border constraints. A mapped route is not tanker access or commercial competitiveness. |
| M4 Calibrated nine worlds | Manish; Nigel reviews | DR07/08, annual L/M/H demand and plant-output inputs with lever register and dependency checks | Calibrate rail tonne-km, EV turnover, ICE efficiency, power dispatch and plant output. Include Secunda gas/MRG, SAPREF, Natref and PetroSA. No double counting; capacity is not production. Medium is an agreed baseline, not an arbitrary midpoint. |
| M5 Investment decision | Nigel coordinates finance/engineering; Manish models; Henry independent review proposed | DR06, incremental existing/improvement/expansion cash flows for all nine worlds, thresholds and downside tests | Validate rents and chargeable services, capex, schedule, tax, working capital and hurdle rate. Compare incremental alternatives. Rail/corridor and EV investments require their own evidence and economics; DR09 covers EV adjacency. |
| M6 Approval readiness | Nigel accountable; reviewer and approver to confirm | Signed assumption decisions, independent review, closed applicable exceptions and investment paper | Apply GATE_CHECKLIST.md; record actual approval separately. Passing tests or committing to Git is not investment approval. |

Immediate priority: Manish reconciles DR01 and assembles DR04/07/08 public evidence; Nigel coordinates DR02/03/05/06. Hand back an evidence table with source, period, unit, observed/inferred/illustrative status, owner and unresolved gap. Do not wait for commercial inputs to complete independent public-source work.

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

The delivered archive preserves story progression and Nigel's edited v18 source. Use only the dated v25 pair as the current review pack. Historic records can name former paths; `archive/story_versions/` holds those files now.

## Verification at this milestone

170 Python tests passed. Governance coverage passed with 57 open exceptions; formal readiness is still blocked by the recorded review and calibration gaps. v25 has 39 matching PPTX/PDF pages; bounds, titles and render count passed and changed pages 10 and 39 were visually reviewed. No independent model review or business approval is implied.
