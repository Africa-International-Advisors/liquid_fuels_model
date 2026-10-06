# Week 1 analytical map review — 6 October 2026

Nigel requested geographic demand regions, a demand heatmap, richer operator
storage context and regional stacked share bars. The six-page Vopak pack keeps
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
  Burgan Cape; five historical/lease-status Transnet records excluded from
  the mapped available footprint. Site existence does not establish present
  usable capacity, current operation or third-party access.
- Slides 3–4: illustrative road-cost surface and market opportunity volumes.
  Transport rates and schematic routes are not calibrated carrier/route evidence.
- Slide 5: public operator sources plus illustrative 100% stacked share bars.
  Current Vopak share, additional candidate and outside-envelope segments use
  authored 4.5/10.0 bn L examples, not slide 2's historical sales denominators.
  Western/other are unassessed. Actual Vopak share remains unknown.

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
Page 6 ranks five quantified locations with operator segments; closing moves to
page 7. The chart uses published gross capacity, not annual throughput or usable
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
