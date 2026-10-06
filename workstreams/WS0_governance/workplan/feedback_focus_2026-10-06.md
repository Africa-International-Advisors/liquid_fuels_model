# 6 October: feedback checklist and Manish discussion

Purpose: turn the current diagnostics and partner story into a reproducible,
traceable fuel baseline and one defensible integration candidate. South Africa
petrol and diesel are the client focus; jet remains tracked separately.
Nigel reviews proposed changes; Manish investigates and implements explained
replacements. Henry reviews the technical mechanisms. Assignments and dates
below are proposed discussion targets, not recorded meeting commitments.

## What is ready to use

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
