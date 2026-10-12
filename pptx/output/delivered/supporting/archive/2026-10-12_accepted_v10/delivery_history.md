# Current supporting deliverables

Updated 12 October 2026. Previous versions are archived; no deliverables were deleted.

| Deliverable | PowerPoint | PDF |
|---|---|---|
| SCR evidence v10 (16 pages, current; stacked demand chart) | [Open](../../SA_SCR_Evidence_2026-10-12_v10.pptx) | [Open](../../SA_SCR_Evidence_2026-10-12_v10.pdf) |
| SCR evidence v09 (16 pages; graphical balance) | [Open](SA_SCR_Evidence_2026-10-12_v09.pptx) | [Open](SA_SCR_Evidence_2026-10-12_v09.pdf) |
| SCR evidence v08 (16 pages; balance, efficiency and refinery outlook) | [Open](SA_SCR_Evidence_2026-10-12_v08.pptx) | [Open](SA_SCR_Evidence_2026-10-12_v08.pdf) |
| SCR evidence v07 (14 pages; approved layout) | [Open](SA_SCR_Evidence_2026-10-12_v07.pptx) | [Open](SA_SCR_Evidence_2026-10-12_v07.pdf) |
| SCR evidence v06 (14 pages) | [Open](SA_SCR_Evidence_2026-10-12_v06.pptx) | [Open](SA_SCR_Evidence_2026-10-12_v06.pdf) |
| SCR with evidence and sizing flowchart v05 (14 pages) | [Open](SA_SCR_Evidence_2026-10-12_v05.pptx) | [Open](SA_SCR_Evidence_2026-10-12_v05.pdf) |
| SCR with seven evidence pages v04 (13 pages) | [Open](SA_SCR_Evidence_2026-10-11_v04.pptx) | [Open](SA_SCR_Evidence_2026-10-11_v04.pdf) |
| Six-page SCR and sizing framework v03 (current short story) | [Open](SA_SCR_Six_Page_2026-10-11_v03.pptx) | [Open](SA_SCR_Six_Page_2026-10-11_v03.pdf) |
| Four-page SCR and sizing framework v02 | [Open](SA_SCR_Four_Page_2026-10-11_v02.pptx) | [Open](SA_SCR_Four_Page_2026-10-11_v02.pdf) |
| Three-page SCR story v01 | [Open](SA_SCR_Three_Page_2026-10-11_v01.pptx) | [Open](SA_SCR_Three_Page_2026-10-11_v01.pdf) |
| South Africa market story v37 | [Open](../../SA_Market_Story_2026-10-11_v37.pptx) | [Open](../../SA_Market_Story_2026-10-11_v37.pdf) |
| Durban and Lesedi market sizing v2000 | [Open](../../10102026_Vopak_Market_Sizing_v2000.pptx) | [Open](../../10102026_Vopak_Market_Sizing_v2000.pdf) |

The current short story has six pages: cover, situation, complication, market-sizing framework, resolution and closing. Complications are grouped into demand, domestic supply and import routes; road-to-rail and vehicle efficiency remain separate demand drivers. The framework makes addressable market and achievable capture the core Vopak sizing steps, with sectors, ports and inland connections explicit. Walvis Bay diversion is unquantified; the 2.63bn-litre illustration does not explicitly deduct diversion via Matola or Walvis Bay. Prior short versions are retained above.

The full story has 15 core pages, an appendix divider on page 16 and eight supporting pages. The 5.8bn-litre domestic production assumption remains explicit. Commercial capture and product reconciliation remain subject to review.

## Supporting workbooks

The v06 pack makes baseline demand the first clickable evidence-index row on p3, restores reported 2014–2021 production history on p9, restores the corridor map beside all five route-evidence items on p10, and removes cross-reference badges from the p11 flowchart. The 2025 production assumption remains separate from observations. Rebuild via build_production_chart_v06, revise_feedback_v06, refresh_feedback_chart_caches_v06, package_feedback_charts_v06, polish_feedback_v06 and finalize_sa_evidence_polished_v06.

The v05 pack adds the existing native sizing issue tree at p11, before the retained framework table at p12. Page 3 has clickable references to all evidence pages (pp4–10), including the demand baseline. Rebuild from v04 using insert_sizing_flow_v05.py, refresh_flow_chart_caches_v05.py and finalize_sa_evidence_v05.mjs; original chart workbooks are preserved.

The v04 evidence pack retains the cover, situation, complication, sizing framework, resolution and closing, adding seven evidence pages at pp4–10: national demand, sectors, Eskom, freight, vehicle technology, domestic production and routes. The complication summary refers to these deep dives. Charts contain editable data snapshots; model assumptions remain in the analytical workbook. Build with setup/build, trim, style, navigation, chart packaging, polish and reviewed finalizer scripts for evidence_v04.

- [South Africa analytical workbook v02](../../../../../../output/delivered/sa_analytics_2026_10_11_v02/SA_Fuel_Analytics_2025_Baseline_2026-10-11_v02.xlsx)
- [Market-sizing workbook](../../../../../../output/delivered/Vopak_Market_Sizing_2026-10-10_v01.xlsx)
- [Master-data review and gaps](../../../../../../output/delivered/Master_data_book_review_2026-10-10_v01.xlsx)

## Reference material

- [Review scope](../../Review_scope)
- [Archived revisions and delivery history](../2026-10-11_cleanup/README.md)
- [Earlier archive](../README.md)

Rebuild the current story with the v37 preparation, builder, trim, style, navigation, chart-workbook, cover-note cleanup and finalizer scripts in `pptx/scripts/`. Archived v30/v31 template references remain available to those builders.

## Approved layout — v07

The current pack applies the saved Vopak Exhibit + Commentary v1 standard to pp4–10 and numbered navigation to pp2–13. Story, six native charts, embedded chart data, and p3 links to pp4–10 are preserved. Reference, layout contract, build extension and release instructions are saved under pptx/templates, pptx/brand_configs and pptx/scripts; see [layout instructions](../../../../../brand_configs/VOPAK_LAYOUT.md). All previous deliverables remain available.

## v08 additions

Page 2 now shows all four 2025 balance measures with reported/estimated/assumed status, the 0.034bn-litre aggregate gap and offsetting product differences. Page 9 adds the base-case fuel-efficiency effect; vehicle sales remain on p8. Historical production remains on p10. The restored 2030 combined import scenarios are on p14, in the outlook section, with refinery and demand assumptions explicit. The map moves to p11, framework flowchart/table to pp12–13, and resolution/closing to pp15–16. All nine evidence/outlook references on p3 were checked in the exported PDF. Eight native charts carry embedded workbooks. Existing analytical outputs reused; no new model assumptions.

V09 replaces page 2 with an editable stacked supply/use balance chart in the locked exhibit layout. It retains the recorded/estimated/assumed distinction, unresolved stock change and product-level differences. All other slide content is retained. Nine native charts; package and layout checks passed; page 2 visually reviewed.

V10 changes only p4’s chart to stacked area, showing total demand and the petrol/diesel composition. Source series and embedded workbook are unchanged; 2024E–2025E remain labelled. Native PowerPoint render reviewed.
