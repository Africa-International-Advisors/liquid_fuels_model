# Current South Africa review

## Current issue: 11 October 2026 — v37

[PowerPoint](SA_Market_Story_2026-10-11_v37.pptx) and [PDF](SA_Market_Story_2026-10-11_v37.pdf). The 24-page pack has 15 core pages, an Appendix divider on page 16, and eight supporting pages. Complication pages 7–11 present sector, Eskom, freight, refinery-output and Matola evidence. The import-outlook chart opens Resolution on page 12. Power, rail, refinery and route-cost scenarios are in the appendix, pages 17–20. The SCR references match the revised page order. Internal HG framing and unsupported Walvis Bay evidence were removed from the client-facing deck; assumption provenance remains in the working files. Workbook v02 and model cases are unchanged.

Build with the v37 preparation, builder, trim, style, native-navigation, chart-workbook and finalizer scripts in `pptx/scripts/`. Use UTF-8 when reading builder source. The source captions distinguish reported observations, estimates and assumptions without internal workflow language.

## Previous issue: 11 October 2026 — v36

[PowerPoint](SA_Market_Story_2026-10-11_v36.pptx) and [PDF](SA_Market_Story_2026-10-11_v36.pdf). The 23-page pack contains an 18-page core and five appendix pages. Page 2 has SCR row dividers and final deep-dive references. Page 3 merges the former baseline and driver overview into a demand time series with outlook commentary. All eight chart pages use aligned headings, horizontal rules and a vertical divider. Page 5 ranks demand segments in descending order. Page 8 charts the 2025 power baseline and 2030 scenario endpoints. Tables use white Marvin styling, horizontal rules and right-aligned numbers. Petrol assumptions are on page 21 and the detailed segment table on page 22. Workbook v02 and the 5.8bn-litre production assumption are retained; Walvis Bay remains unquantified.

Rebuild: `prepare_sa_story_v36.py`, `build_sa_story_v36.mjs`, `trim_sa_story_v36.py`, `style_sa_story_v36.py`, `apply_sa_story_navigation_v36.py`, `package_sa_chart_workbooks_v36.py`, and `finalize_sa_story_v36.mjs` in `pptx/scripts/`. The power chart consumes the model's existing scenario bridge through `src/lfm/model/sa_story_views.py`.

## Previous issue: 11 October 2026 — v35

[PowerPoint](SA_Market_Story_2026-10-11_v35.pptx) and [PDF](SA_Market_Story_2026-10-11_v35.pdf). Page 2 uses horizontal Situation, Complication and Resolution rows. The five agreed complication drivers are explicit: mining/manufacturing/agriculture; Eskom/power; road-to-rail/vehicle efficiency; refineries/domestic production; Matola/Walvis Bay. Walvis Bay remains an unquantified route sensitivity. The 23-page deck, model assumptions and workbook v02 are otherwise retained. Builders: `build_sa_scr_v35.mjs`, `assemble_sa_scr_v35.py`, `normalize_sa_charts_v35.py`, `finalize_sa_story_v35.mjs`.

## Previous issue: 11 October 2026 — v34

[PowerPoint](SA_Market_Story_2026-10-11_v34.pptx) and [PDF](SA_Market_Story_2026-10-11_v34.pdf). Page 2 now gives the answer in one Situation–Complication–Resolution page, immediately after the cover. The analytical baseline follows on page 3, driver overview on page 4, and deep dives on pages 5–20. Appendix starts on page 21. Page references are updated; model assumptions and workbook v02 are unchanged. The new page retains native SmartArt and editable text. Build with `build_sa_scr_v34.mjs`, assemble with `assemble_sa_scr_v34.py`, normalize Office chart cache precision with `normalize_sa_charts_v34.py`, and finalize with `finalize_sa_story_v34.mjs`.

## Previous issue: 11 October 2026 — v33

- [South Africa story PowerPoint](SA_Market_Story_2026-10-11_v33.pptx) and [PDF](SA_Market_Story_2026-10-11_v33.pdf): 19 core pages plus three appendix pages. Pages 2–3 give the baseline answer and driver overview; 4–7 establish demand; 8–11 quantify power and freight; 12–14 assess production and imports; 15–16 assess Mozambique routes; 17–19 connect the market to Vopak capture and investment. HG's original framing is retained on page 20.
- [Analytical workbook v02](../../../../output/delivered/sa_analytics_2026_10_11_v02/SA_Fuel_Analytics_2025_Baseline_2026-10-11_v02.xlsx): 11 editable sheets. National production is a user-directed 5.8bn-litre planning assumption, not reported output. The original 10.23bn plant estimate remains visible. Provisional petrol/diesel allocation leaves offsetting product gaps, shown on page 21 and in the Balance sheet.
- The resulting 2025 demand estimate is 20.99bn litres; demand-implied gross imports are 16.74bn, and base-case 2030 imports are 16.61bn. Vopak's illustrative capture remains 2.63bn unique litres, including 1.32bn routed onward through Lesedi.
- All 22 pages rendered in PowerPoint and reviewed; 21 native SmartArt navigation bars retained. Workbook formula results agree with the model. Governance coverage passed with 58 open exceptions; these checks do not constitute business approval. Previous versions remain preserved.
- Rebuild using `prepare_sa_story_v33.py`, `build_sa_story_v33.mjs`, `trim_sa_story_v33.py`, `apply_sa_story_navigation_v33.py`, `package_sa_chart_workbooks_v33.py`, and `finalize_sa_story_v33.mjs` in `pptx/scripts/`. Analytical inputs include `assumptions/2026/sa_story_case_2025.yaml`.

## Previous issue: 11 October 2026 — v32

- South Africa story v32: [PowerPoint](SA_Market_Story_2026-10-11_v32.pptx) and [PDF](SA_Market_Story_2026-10-11_v32.pdf). Core story ends at page 19; appendix starts at page 20 (49 slides total). HG's framing and the current answer remain on pp2–3. Baseline pp4–9; transport and sector demand pp10–11; power p12; refinery developments and import implications pp13–14; competing routes p15; Vopak capture p16; operating capacity p17; investment tests p18; conclusions and next decisions p19. Detailed valuation changes and the nine-world matrix are in the appendix, rather than the opening. Reported observations, sector estimates and conditional cases remain distinct.
- Native SmartArt chevrons retained: 47 four-section bars, with new section highlights. Prior versions are preserved. Build body with `pptx/scripts/build_sa_core_v32.mjs`, attach preserved package components and export PDF with `pptx/scripts/apply_sa_core_navigation_v32.py`, then finalize with `pptx/scripts/finalize_sa_core_v32.mjs`. Approved structure and new copy: `pptx/story/sa_core_v32_2026_10_11.json`. The native components were generated and preserved by the v31 package workflow; no live SmartArt gallery call is needed for this rebuild.
- Market sizing v2000: [PowerPoint](10102026_Vopak_Market_Sizing_v2000.pptx) and [PDF](10102026_Vopak_Market_Sizing_v2000.pdf), cover plus eight numbered pages.
- [Editable sizing workbook](../../../../output/delivered/Vopak_Market_Sizing_2026-10-10_v01.xlsx): Capture cases, Market context, Operations, Sources and gaps.
- [Master workbook with review and gaps](../../../../output/delivered/Master_data_book_review_2026-10-10_v01.xlsx). Manish's received master is preserved.

Start at story page 16 or sizing printed page 8 for the capture calculation; story page 17 shows working-tank turnover. The 2025 Durban customs import pool is 13.16bn litres. Authored 10%/20%/30% capture cases and 50% onward routing to Lesedi are editable sensitivities, not measured shares or probability bounds. The base gives Durban 2.632bn litres and Lesedi 1.316bn litres within that same flow. Do not add these to estimate unique market volume. Domestic and other-terminal receipts at Lesedi are outside this single-chain screen.

The revision separates observed national and provincial demand, imports, terminal handling capacity and commercially captured volumes. It withdraws the mixed-year 8.88bn-litre inland residual and unsupported road/rail residuals; adopts FY2025 MPP 105/148 ML per week as shared pipeline context; updates sector estimates and evidence status; and retains explicit power/road, hybrid/rail and commercial calibration gaps.

Story pages 46–49 recalculate the separate investment illustration using 124,000 m³ Lesedi working capacity (88,000 documented plus 36,000 estimated). The combined-option advantage over operational improvement becomes approximately R58m NPV, previously R8m. This is a model consequence of the capacity/rental assumptions, not new commercial evidence. Its 1.25/1.50 monthly turns differ from the capture screen's two turns. Tested downside cases still reverse the expansion preference.

Rebuild review calculations with `python -m lfm.scripts.build_market_review --output output/delivered/market_review_2026_10_10` and the investment illustration with `python -m lfm.scripts.build_vopak_illustration --output output/delivered/vopak_illustration_2026_10_10`. Presentation edits are prepared by `pptx/scripts/prepare_sa_review_v28.py` and applied by `pptx/scripts/build_sa_review_v28.mjs`; PDF export uses `pptx/scripts/export_sa_review_v28.ps1`. The immutable finalizer requires a fresh private release directory and receipt on subsequent builds. The Excel builder is `src/lfm/scripts/build_market_review_workbook.mjs`.

Checks: the 11 October governance check passed with 57 open exceptions; 10 relevant model tests passed during the 10 October model update (not rerun for this narrative-only revision); Excel cached results match the model. These checks do not constitute commercial validation or business approval. Capture, routing and eligible working capacity require Vopak confirmation before an investment decision; owners and expiry triggers remain in the register and workbook gap review.

## Previous issue: 8–9 October 2026

The notes and rebuild commands below describe the previous issue and are retained for history. They do not rebuild v28.

**Current: 8 October 2026 — v27:** [PDF](SA_Market_Story_2026-10-08_v27.pdf) · [PowerPoint](SA_Market_Story_2026-10-08_v27.pptx)

**Durban and Lesedi market sizing pack (current, built 9 October 2026 11:00):** [PDF](09102026_Vopak_Market_Sizing_v1100.pdf) · [editable PowerPoint](09102026_Vopak_Market_Sizing_v1100.pptx). Cover, then eight pages: 1 national balance; 2 issue tree; 3 demand by product and province; 4 demand by use (three sources to calibrate); 5 demand parameters (2035 lever cases, not accepted); 6 port and logistics; 7 outstanding data; 8 decisions and next steps. Built on Manish's DR01, DR04, DR07 and DR08 hand-back; where our work overlapped, his evidence is primary — see the [overlap log](../../../../workstreams/WS0_governance/workplan/overlap_log_2026_10_08.md). Rebuild with `pptx/scripts/build_market_sizing_issue_tree.ps1 -IncludeRequests -Layout flow`. Files are named ddmmyyyy_filename_vHHMM, with the build time rounded to the nearest half hour. The current file was built as v14; earlier versions v1-v13 are in [archive](archive/README.md) (record: `archive/records/cleanup_2026-10-09_issue_tree_v14.json`).

- **[Review scope](Review_scope/)** — agreed scope and comments applied.
- **[Archive](archive/)** — older story versions, background and illustrations.

43 pages. Appendix starts at page 19. Nigel’s existing taglines are preserved. Manish's workbook history, estimates and proposed scenarios are integrated where relevant; scenario and commercial calibration remain open.

Page 8 now uses three stacked sector chart rows with a common scale; 2024 estimates are outlined. Figures and other pages are preserved from v26.

New exhibits: industry demand (mining, manufacturing and agriculture), page 8; Durban–Lesedi market-sizing issue tree, page 16; vehicle stock and calibration, page 26; power fleet and proposed cases, page 33.

Data request: page 18. Baseline reconciliation and implementation status: pages 36–37. [Page-by-page workbook audit](../../../../workstreams/WS3_reporting_delivery/sa_pack_workbook_audit_2026_10_08.csv) and [cell evidence](../../../story/sa_workbook_evidence_v26_2026_10_08.json).

Investment conditions: p4; nine-world investment priorities: p5; options: p17; original SCR synthesis: p38.

Illustrative investment case, annual-report context, assumptions and downside tests: pages 39–42. Reported, inferred and illustrative inputs are distinguished; actual commercial calibration remains open.

Previous story versions, including v25, v26 and Nigel's edited v18, are preserved in `archive/story_versions/`. The first one-page issue-tree handback is in `archive/background/`. Builders use the archived sources; the active folder contains v27 and the current two-page handback.


Page 11: current asset position and operating data gaps. Page 43: illustrative turnover sensitivity. Actual site share and investment capacity remain dependent on the client inputs listed on page 18.

Previous workbook revision: [v26 PDF](archive/story_versions/SA_Market_Story_2026-10-08_v26.pdf) · [PowerPoint](archive/story_versions/SA_Market_Story_2026-10-08_v26.pptx). [Cleanup record](archive/records/cleanup_2026-10-08_v27.json) maps former paths and verified duplicate removals.
