# Week 1 analytical map review — 6 October 2026

Nigel requested geographic demand regions, a demand heatmap, richer operator
storage context and regional stacked share bars. The current ten-page Vopak pack keeps
the supplied master, cover, closing, chevrons and exhibit/key-takeaway structure.

## Evidence and presentation status

- Slide 2: reported 2022 provincial petrol/diesel sales, not 2026 demand. All four
  quarters are present for every province/product, and the provincial sum
  reconciles to the national source within one litre. This mechanical check is
  not independent validation of the original extraction.
- Working regions: eastern coastal = EC/KZN; inland = GP/FS/LP/MP/NW;
  western coastal = WC; other = NC. Province union outlines are geographic
  groupings, not operational catchments. Colour encodes provincial volume,
  not local density or within-province hotspots.
- Storage: 12 site/group records across Vopak, Bidvest, Sasol, Transnet and
  Burgan Cape; five Transnet lease-offer sites now mapped separately with numbered triangles.
  These are context only and are excluded from available operating capacity. Site existence does not establish present
  usable capacity, current operation or third-party access.
- Slides 3–4: illustrative road-cost surface and market opportunity volumes.
  Transport rates and schematic routes are not calibrated carrier/route evidence.
- Slide 7: all four working regions use reported 2022 demand, with public storage
  operators listed by region. Vopak deliveries, share and additional contestable
  volume are not established for any region. Earlier illustrative share bars have
  been removed from this page. Capacity is not a delivery or share denominator.

## Direction for Manish

1. Pull `origin/main` each morning and before pushing; both analysts work on
   `main`. Read the shared branch workflow. Run governance and relevant checks.
2. For Week 1, prioritise integrated petrol/diesel demand/supply reconciliation
   and explicit lever definitions. Track jet separately from the client scope.
3. Review the 2022 source workbook/extraction against the nine provincial totals,
   then seek a later complete provincial year. Do not annualise 2023 Q1 or
   silently label 2022 as current. Confirm the working region membership with Nigel.
4. Obtain actual unique petrol/diesel customer deliveries by product, destination,
   period and terminal; reconcile Durban receipts, Lesedi receipts and their shared
   transfers. Count the customer demand once. Keep actual share unknown until
   numerator and denominator are matched.
5. Use the dated storage/source CSVs under `pptx/story/` to resolve: Bidvest's
   discrepant mixed-product totals; Sasol's availability notice ending March 2026;
   current Transnet operation/access; and Burgan's current notice/market overlap.
   Record product eligibility, usable versus gross capacity, exact site geometry,
   vintage, download/API/manual refresh path, current contracts and evidence owner.
6. Test delivered transport cost and commercial switching/access before treating
   an operator footprint as contestable volume. Broad asset inventory and detailed
   storage sizing support integration; they do not replace it.

No model assumptions were changed by this reporting revision. Governance coverage
passes with 50 open exceptions; the model and opportunity illustration remain draft.

## Storage-location page added

Nigel requested a bar chart locating the largest published storage stocks.
Page 8 ranks five gross-capacity locations with operator segments and separately
shows quantified Transnet lease sites; closing is page 9. The chart uses published gross capacity, not annual throughput or usable
petrol/diesel-only capacity. It is a partial inventory and leaves missing
Sasol/Transnet values unknown. Vopak's HTML cbm capacity attributes confirm
360,246 m³ at Durban and 140,000 m³ at Lesedi; the alternate rendered numbers
are barrels and must not be ingested as m³. Terminal-page publication dates are
unstated; originals are preserved under `external/data/raw/vopak_storage_20261006/`.

## Provincial history, origin illustration and delivery cleanup

The current named nine-page pack includes annual provincial trends (page 3) and
the provincial domestic/finished-import stack (page 4). The stacks combine sourced
2022 demand with explicitly illustrative product-specific source shares; no actual
provincial source mix is asserted. National balance data in the current extract
ends in 2021, and sales by province do not contain origin. Obtain matched-year
evidence before replacing this illustration.

The trend page uses the quarterly source rather than potentially incomplete annual
totals. 2023 Q1 is excluded. Provincial sums versus the national sales source differ
in 2013, 2014, 2015, 2017, 2018 and 2021; the largest combined gaps are approximately
+0.54 bn L in 2013 and -0.43 bn L in 2018. Review the raw workbooks and product-level
differences without silently changing received data.

Use `Vopak_Week1_Analytical_Pack_2026_10_06.pptx` / `.pdf` as the current delivery.
Earlier shipped packs remain in `pptx/output/delivered/archive/2026-10-06/`;
unshipped drafts are kept in ignored QA. Preserve that history and avoid creating
further numbered variants in the delivery folder.

## Transnet lease evidence refresh ? 6 October 2026

Nigel supplied the official TPL Leasing Opportunities page. All five linked RFPs,
issued 5 October 2026 and closing 4 December 2026, are preserved with source URLs,
page references and SHA256 hashes in `external/data/raw/transnet_leasing_20261006/`.
The reporting inventory replaces the old local-CSV-only reference for these sites.

- Ladysmith: 8,540 m? petrol/diesel working capacity; 474 m? intermixture excluded
  from the chart. Total RFP working tankage is 9,014 m?. Tanks have been out of
  service since March 2018; there is no NMPP connection or road/rail decanting system.
- Standerton: 2,353 m? from three stated tank capacities; basis not labelled gross/working.
- Kroonstad: approximately 3,300 m?, with the same capacity-basis limitation.
- Bethlehem and Magdala: no petroleum tank capacity quantified. Unknown is not zero.
- Exact briefing coordinates are mapped on pages 2, 5 and 6. Magdala's RFP has
  conflicting location descriptions; its briefing coordinate is used pending verification.
- Page 8 separates the 0?850 thousand m? gross-storage panel from an enlarged
  0?10 thousand m? lease-capacity panel. The panels must not be summed as a
  like-for-like usable fuel inventory.

Manish: verify location, condition, eligible products, refurbishment cost,
receipt/dispatch connections, storage licence and lease award before activating
any of these assets in a route or market-access scenario. Refresh the index and
PDFs at an amendment, the 4 December closing date, award or reactivation. Keep
this manual-download path distinct from an API. No engine assumptions changed.

## Regional competition page clarified

Nigel requested all four regions while retaining competitor detail. Page 7 now
shows sourced 2022 petrol/diesel sales by working region: eastern coast 6.02,
inland 11.50, western coast 3.93 and Northern Cape 0.45 bn litres/year (rounded).
The national sum is 21.90 bn litres; aggregation uses unrounded provincial data.
The two adjacent fields, Vopak served and additional contestable, remain explicitly
not established for every region. No authored share percentages appear on this page.

Competitor details remain alongside the chart: Bidvest Durban/Richards Bay/Isando;
Sasol Alrode/Pretoria West/Waltloo/Sasolburg; Transnet Tarlton/Jameson Park and
lease opportunities; Burgan Cape at Cape Town. Mixed-product scope and lease
status remain explicit. Northern Cape operator coverage is incomplete; Shell
site notices and NERSA records are public inventory leads, not verified local sites.
The public links and detailed evidence limitations remain in the page notes.

Manish: fill unique matched-year Vopak customer deliveries and accessible candidate
volumes after checking destinations, double-counted transfers, costs, product
compatibility and contracts. Do not equate provincial geography with a terminal
catchment. Obtain later complete demand observations before reporting a current share.

## Storage chart readability correction

Nigel found the enlarged lease inset and smaller lower-panel fonts confusing.
Page 8 now shows all eight quantified locations on one 0-850 thousand m3 linear
scale. All location and value labels use 12pt; ticks and legend use 11pt. Every
operator segment retains its true proportional width, including the small lease
tanks. No scale break or minimum artificial bar width is used. Transnet lease
segments have an outline and a separate legend category. Values use consistent
two-decimal formatting; Kroonstad remains approximate in the source inventory.

The prior two-panel display is superseded. The mixed capacity bases, unquantified
sites and conditions for reactivation remain explicit. No source numbers or
engine assumptions changed. The current nine-page PPT/PDF filenames are retained.

## Partner story consolidated

The current pack adds page 9 linking Situation, Complication and Resolution to existing evidence and closure actions; closing is page 10. See [the detailed partner alignment review](partner_story_alignment_2026-10-06.md) and `pptx/story/partner_story_gap_register_2026_10_06.json` for 14 open gaps with owners, planning windows, source/refresh routes, model connections and evidence required for closure. Earlier nine-page references above describe prior shipped revisions. No model inputs or calculation logic changed.

## Shared exhibit typography

Nigel identified inconsistent map callout and chart font sizes. The builders now
use `pptx/scripts/exhibit_typography.py`: primary chart labels/values 12pt;
secondary chart labels, axes and legends 11pt; map callout text 11pt. These apply
to the provincial history/supply, regional-demand and storage charts and the
storage/market callouts on the maps. Regional competitor headings/body match
the other takeaway panels at 14pt/12.5pt. Smaller source notes and cartographic
point identifiers retain a separate supporting hierarchy.

Text boxes and legends were resized/repositioned to fit. Cost units remain explicit
in the exhibit heading. Data, quantitative axes, illustrative disclosures and the
ten-page structure are unchanged. Rendered pages 2-8, shared font assertions and
package checks passed. The same current PPT/PDF filenames are used.


## SCR-led delivery order

The former page 9 now leads immediately after the cover. Evidence/implications are separated from a ruled Next steps block with proposed owners. Regional competitor detail remains on its own inventory panel. Placeholder pages explicitly specify gaps and closure outputs, with complete source/refresh/model-connection records in notes; they do not imply actual results or forecast capture.

| Page | Content | Status |
|---|---|---|
| 1 | Cover | Retained |
| 2 | Situation?Complication?Resolution overview | Moved and reframed |
| 3 | Provincial demand and infrastructure map | Sourced historical evidence |
| 4 | Provincial sales time series | Sourced; six years flagged |
| 5 | National balance and import entry ports | New gap specification SA03/04 |
| 6 | Provincial domestic/import split | Explicit illustration |
| 7 | Power, rail, fleet and economic drivers | New gap specification SA05?08 |
| 8 | Refinery scenarios and Sasol/Natref | New gap specification SA09/10 |
| 9 | Delivered-cost accessibility map | Explicit illustration |
| 10 | Competing route cost comparison | New gap specification SA11 |
| 11 | Unique flows and conditional market envelope | Explicit illustration |
| 12 | Four regional markets and competitors | Demand sourced; share unknown |
| 13 | Actual share and contestable demand | New gap specification SA12/13 |
| 14 | Storage by location | Partial published inventory |
| 15 | Optional investment/service assessment | New deferred gap specification SA14 |
| 16 | Closing | Retained |

SA01 is covered by pages 3?4; SA02 by page 9 and the access specifications. All fourteen partner questions have an evidence page or explicit placeholder. Rendered in PowerPoint, exported to a matching 16-page PDF and checked for package integrity and slide-edge bounds. Governance coverage passes with the existing 50 open exceptions; this remains a review draft.


### SCR master table and page traceability

Page 2 is now a full-width native PowerPoint table matching the supplied roadmap structure: SCR reference, evidence/required next step, proposed lead, timing/output, and linked deep-dive page numbers. Seven rows (S1/S2/C1/C2/C3/R1/R2) cover pages 3?15. Each analytical page carries its row reference above the title and an internal link back to page 2. Table page links and backlinks were checked against slide relationships; the 16-page PowerPoint/PDF pair was rendered and visually reviewed. No extra pages or changed data were introduced. Owners and week windows remain proposed, and investment remains optional after the flow case.


### Clickable story navigation and matched panel headings

Analytical pages 2?15 now use SCR overview / Situation / Complication / Resolution chevrons, linked to pages 2 / 3 / 7 / 11. Section highlighting follows the ordered story. All 56 chevron links and active states were verified, with clickable annotations preserved in the matching PDF. The original photographic cover and closing remain intact. Both left/right panel headings on analytical pages 3?15 use 15-point Lato bold. Rendered section states and page 11 were reviewed. Reuse strips obsolete internal slide relationships before rebuilding links, preventing removed pages from surviving as orphan package parts; breadcrumbs are replaced without duplication.
# Public supply collection and accessibility conditions — 6 October update

The stable 16-page pack now replaces four specifications with review exhibits:

| Page / SCR | Exhibit added | What remains open |
| --- | --- | --- |
| 5 / S2 | 2024 sales, government imports/exports and net imports; explicit old-versus-new source flag | Matched production/stocks and product-specific port allocation; provincial origin cannot be inferred |
| 8 / C2 | Published 2016–2025 capacity footprint; side-by-side held-flat and conditional CEF redevelopment areas | Not output; source utilisation/yields and agree timing. Authored 2029 FID is not sanctioned |
| 10 / C3 | Southern Africa map linking Durban, Matola/Maputo and Walvis Bay to a common Gauteng comparison market | Schematic routes, not fuel service or commercial access. Compare same destination and full R/litre components |
| 13 / R1 | Illustrative unique served-volume milestones 3.0 → 4.5 → 8.5 bn L/year, with conditions for coastal +1.5 and inland +4.0 | Cost threshold, physical capacity, customer rights and unique-volume reconciliation remain unassessed |

The 2024 diesel-import source flag compares FIASA's staged 14.793 bn litres with
the government report's rounded 10.8 bn litres: difference -3.993 bn litres.
This is a source disagreement, not an approved correction. Existing FIASA inputs
are preserved; neither series has been adopted into the engine automatically.
The flag table is `output/delivered/supply_review_2026_10_06/trade_source_flags.csv`.

Preserved reports and download attempts live in
`external/data/raw/fuel_supply_review_20261006/manifest.json`. Latest report
requests and the TNPA PDF include failed fetches; those are not claimed as
collected. TNPA liquid bulk also has broader product scope than petrol/diesel.
Refresh by downloading new reports into a new dated raw folder, checking the
source sentences/table, rerunning `python -m lfm.scripts.collect_supply_review`,
and updating the input register deliberately. The current extractor targets
this preserved vintage and fails if its source table/sentences differ.

Inputs: `fuel_trade_department_review.csv`, `refinery_capacity_reported.csv`,
and `review_capacity_scenarios.yaml`, declared and registered under
EXC-SUPPLY-REVIEW-2026-10-06 (Manish; expires 12 November or before adoption).
The CEF case adds proposed 400 thousand bbl/day after an illustrative FID plus
48 months. The capacity history includes synthetic crude-equivalent capacity
and idle nameplate: it is not available petrol/diesel output.

Page 8's illustrative display horizon is now 2036, rather than stopping at the
2033 completion point. Both cases keep the same observed history and 0–800
thousand bbl/day axis. The baseline holds 358; the conditional case adds 400
from 2033 and holds 758 through 2036. The addition uses a contrasting blue
area and an explicit legend. This is a registered reporting assumption change,
not a revised capacity observation, sanctioned FID or fuel-output forecast.

For R1, Manish should assemble customer × product × destination × period × route
records with delivered R/litre, customer threshold, compatible capacity,
contract/switching evidence and final delivered litres. Mark each condition
passed, failed or unassessed, identify the binding constraint, and count shared
Durban–Lesedi transfers once. Nigel supplies client flows and agrees destinations
and thresholds. No volume milestone is a forecast until these conditions close.
# Demand-driver page 7 — indexed evidence

Display update: analytical subtitles on both sides are retained at 14 pt,
including "Evidence and implications" and "Regional competitor evidence".
The visible "SCR S1 | Situation | Return to overview: page 2" breadcrumb and
its equivalents are removed from every page. SCR references remain in notes;
the clickable overview chevron provides the return link. Main titles, chart
titles, units and findings/actions remain. The named breadcrumb is no longer
created by `scr_summary_table.py`; subtitle size is applied centrally in
`scr_navigation.py`, including the two retained map pages.

The expanded page 7 contains six native line charts, all normalised as
`100 × observed value / that series' 2024 value`, with the same 0–120 vertical
scale: passenger cars/minibuses, trucks/light-commercial vehicle stock,
agriculture/forestry/fishing real value added, manufacturing/mining real value
added, Eskom + IPP OCGT generation, and road/rail freight payload. NaTIS stocks
use national December snapshots for 2021–2025; OCGT is financial year ending
March; value added and payload are calendar years. BEV/conventional-hybrid new
sales remain visible in the findings and notes, separate from vehicle stock.
Indices compare relative movement, not equal fuel weights or causal contributions.

The NaTIS extract does not identify petrol/diesel/electric fleets, so the ICE
passenger and freight split remains explicitly unresolved. Cars/minibuses do
not cover buses/motorcycles; light commercial includes non-freight use. These
are identified classes, not complete fuel-consuming segments. Agriculture and
industrial value added are activity proxies, not observed sector fuel litres.

| Sector | Current evidence | Required fuel bridge / consuming module |
| --- | --- | --- |
| ICE passenger | All-fuel cars/minibuses stock | Fuel/drivetrain split × vehicle-km × cohort L/100km; `demand/vehicles.py` |
| ICE freight | All-fuel trucks/LCV stock; road/rail payload | Fuel split, tonne-km/loads, route shift, mileage and efficiency; `demand/vehicles.py`; rail lever remains open |
| Agriculture | Real agriculture/forestry/fishing value added | Sourced diesel baseline and activity/intensity relation; `demand/agriculture.py` still has a provisional baseline |
| Industry | Real manufacturing and mining value added, separately | Subsector fuel baseline, direct use versus generation and intensities; `demand/industrial.py` |
| Power | Eskom + IPP OCGT GWh | Sourced generation-to-diesel conversion and scope; `demand/generation.py` |

These charts do not automatically replace or calibrate engine inputs. Manish
must record the evidence, units and consuming equation for each bridge before
closing the demand-driver gaps. Nigel agrees intervention alternatives.

New Stats SA P7162 freight data use the December 2025 report consistently for
both 2024 and 2025. The prior December 2024 report had 2024 road payload of
790.611 million tonnes; the later report has 979.798 million tonnes. The
189.187 million-tonne difference is an explicit source revision flag, not an
inferred modal shift. No 2023 old-vintage values are spliced into this chart.
The two original PDFs are preserved in `external/data/raw/demand_drivers_20261006/`.
Refresh with the next December report and rerun
`python -m lfm.scripts.collect_freight_review`, comparing overlapping years
before updating any declared input. Four observations are registered, owned
by Manish, and remain unreviewed under EXC-FREIGHT-REVIEW-2026-10-06.

Fuel-price annual history ends in 2023. Inland petrol-95 is R23.14/litre nominal
in 2023; no 2024 price base or extrapolation is invented. Manish should refresh
prices, source freight tonne-km/diesel intensity, generation-to-fuel conversion,
fleet survival/mileage/efficiency and real-price activity response before
converting these observed drivers into fuel-demand scenarios.

EV visual restored on page 7: native line chart of BEV, plug-in hybrid and conventional hybrid new sales, 2019-2025, each indexed to 2024 = 100. All six activity charts retained. EV chart has an explicit 0-400 axis to include PHEV growth without clipping; activity charts remain 0-120. NaTIS fleet fuel mix remains a data gap. Sales do not establish fleet penetration or fuel displacement. Existing declared naamsa observations consumed; no engine or assumption changes.
