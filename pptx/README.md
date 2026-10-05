# Liquid fuels analyst briefing

Presentation project for the analyst walkthrough and six-week model development plan.
Status: 12-slide editable Vopak kickoff deck built and rendered through PowerPoint.
Current files: [PowerPoint](output/delivered/Vopak_Analyst_Kickoff.pptx) and
[PDF](output/delivered/Vopak_Analyst_Kickoff.pdf). Both contain 12 pages.
User-requested styling: primary blue sampled from the Vopak logo (#0A2373),
Vopak-only visible logos, and native Marvin-style tables with white backgrounds,
bold headers and horizontal rules. The original supplied template remains unchanged.
Titles and body text, including table headers, subsection labels and footer notes,
must be black unless the user explicitly requests another colour. Vopak blue remains
in branding and navigation chevrons. Red title accents are removed. Dividers use
neutral greys: #B8B8B8 body, #B0B0B0 frame, #A0A0A0 header. Rules remain
0.25 pt for body and frame, 0.35 pt for table headers; contrast increased after review.
Content slides include four editable section chevrons at the very top, above the title,
with the current section highlighted.
The active reusable template is `templates/Vopak_Template_v2.pptx`, with a matching
`.potx` for starting new presentations. Rebuild it with `scripts/build_template.py`.
The original `AIA_Vopak_Template.pptx` is preserved. Template v2 uses a thin title/body
separator and compact footer with source text on the left, a small Vopak logo on the
right and a page number at the far right. The user's reference images informed the
layout proportions; their blue annotation boxes are not presentation elements.
Package checks passed and rendered pages were visually reviewed.
The revised source copy and speaker notes are in [the four-part story](story/analyst-kickoff-scr.md).
The deck separates project SCR, analytical requirements, model-build SCR and delivery approach.
Applied page-by-page feedback is recorded in `story/feedback.csv`. Slides 2 and 6
use matching native SCR tables with editable icons; slide 3 uses a smaller question,
numbered sections and editable icons. The current content revision removes the
training page: team ownership is now slide 10, the week-1 baseline gate slide 11,
and a cover-style closing page slide 12. Slide 4 includes the required nine-scenario
matrix with M/M baseline. Slide 9 integrates model/data, client analysis and storyboarding.
Regional requirements cover SACU and screening in East/West/North Africa and SADC
excluding SACU, with a Namibia/Walvis Bay focus. These are deck requirements;
this revision does not implement new model geographies or scenarios.
Rebuild with `brand-pptx build`, which calls `scripts/build_kickoff.py` and
replaces the current output, as requested by the user. The supplied master and named layouts
are retained. Original model code and project canon are unchanged.

## Environment

PDF review delivery is split into the 44-page `Vopak_Analyst_Kickoff.pdf` and
the 56-page `Vopak_Assumption_Inventory.pdf`. The main deck retains the demand
module overview and refers to the companion for every registered value.
Build with `LFM_PDF_ONLY=1`; set `LFM_INVENTORY_ONLY=1` for the companion and
unset it (or set it to `0`) for the main deck. Review PPTX intermediates go to
`qa/pdf-review/`; delivered PPTX files remain unchanged in this workflow.

Use the model repository's `.venv`. The installed toolkit is the local
`brand-pptx` 2.4.0 feature release, built from
`C:/Users/ITafr/.codex/skills/brand-pptx` with `smartart`, `data` and `xlsx` extras.
It replaces the former editable 2.3.0 installation from the neighbouring checkout.
The installation is a built wheel, so subsequent source edits require reinstalling.
Python imports, CLI startup and `pip check` passed.

To reproduce the local installation, run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r pptx/requirements.txt
.\.venv\Scripts\python.exe -m pip install 'C:/Users/ITafr/.codex/skills/brand-pptx[smartart,data,xlsx]'
.\.venv\Scripts\brand-pptx.exe --version
.\.venv\Scripts\python.exe -m pip check
```

Version 2.4.0 is currently a local feature release; the neighbouring GitHub
checkout remains at 2.3.0. Use an approved published tag for a portable release
environment when available. Windows SmartArt support uses `pywin32==312`,
pinned in `pptx/requirements.txt`, and desktop PowerPoint.

The new `add_smartart_navigation` and `restyle_smartart_navigation` helpers
create and style native editable chevron SmartArt after a deck has been saved.
See the package's `docs/SMARTART_NAVIGATION.md`. Avoid python-pptx round trips
after adding SmartArt. The current builder continues to use its established
native shape navigation until a deck migration is requested.

Update checks (2 October 2026): dependency check passed; 8 navigation validation
and flat-styling tests passed; the 100-slide review deck rebuilt and passed
package QA. The live native-SmartArt test failed because desktop PowerPoint
returned `Application.SmartArtLayouts: Object does not exist`. Native creation
is therefore not verified on this machine; this update does not migrate the
deck's existing navigation.

## Project files

- `deck.yaml`: workflow, output paths and template policy; discovered from the repository root.
- `templates/`: place the user-supplied original template here without modifying it.
- `brand_configs/`: project-specific brand configuration, to be completed from that template.
- `story/analyst-kickoff-mockup.md`: full slide copy, object types and speaker/source notes for review.
- `story/deck.html`: prototype entry point, still a setup-status page until mockup approval.
- `scripts/`: presentation builders; consumes model results rather than duplicating model calculations.
- `output/`: generated presentations, PDFs and reusable templates; ignored except tracked `delivered/` copies.
- `qa/`: generated QA reports; created when checks run and ignored by Git.

## Finish setup when the template arrives

1. Inspect its slide dimensions, theme, layouts, placeholders and logos.
2. Create the project brand config from the toolkit example, using the supplied template's
   approved settings. Template paths are relative to this `pptx/` folder.
   Configure generated template paths under `output/templates/`; preserve the original in `templates/`.
3. From `pptx/`, run `..\.venv\Scripts\brand-pptx-validate.exe --config brand_configs/<brand>.py`.
4. Inspect and generate the clean reusable templates with `brand-pptx-inspect` and
   `brand-pptx-build-template`, using the same config and working directory.
5. Update `deck.yaml` with the brand config, source template and its SHA-256 fingerprint.
   Keep template policy enabled. Do not declare `template_aware: true` until the builder
   actually consumes that template and its named layouts.
6. Prepare and review the slide mockup before implementing the deck builder, following
   the brand-pptx skill's mockup-first workflow. Keep the builder in `scripts/` and register it using an `@python`
   command and repository-relative paths. Use versioned output filenames.
7. Run the diagnostics, build, package checks and visual review, then export through
   PowerPoint and verify the PDF page count.

Commands from the repository root:

```powershell
.\.venv\Scripts\brand-pptx.exe doctor --strict
.\.venv\Scripts\brand-pptx.exe prototype --no-open
.\.venv\Scripts\brand-pptx.exe build
.\.venv\Scripts\brand-pptx.exe check --report qa/report.json
.\.venv\Scripts\brand-pptx.exe export-pdf
```

Strict diagnostics are expected to report missing brand config, template and builder
until the remaining setup is complete. Do not weaken the policy to hide these messages.

This namespaced workspace is an explicit project-canon exception. Model calculations stay
in `src/lfm/model/`; presentation scripts consume stamped outputs from `runs/`.

The kickoff deck now has 23 pages, including nine appendix pages after the closing:
the 2024 South African historical demand comparison, the macro/sector input inventory,
and the port/logistics evidence inventory. `scripts/appendix_data.py` calls the existing
`lfm.scripts.compare_history` functions, with vintage 2026 and `high_demand`, and saves
the full comparison to `output/data/historical_comparison.csv`. No model calculation
is duplicated in the presentation builder. The Excel comparator is recorded historical
RSA demand, not an Excel forecast. Document evidence is distinguished from structured
model inputs; neither is presented as independently validated.

The three fuel-specific driver pages use `lfm.reporting.reconciliation` and native
PowerPoint contribution charts. The petrol stock/intensity bridge uses a midpoint
decomposition; the diesel bridge explicitly discloses non-power coverage overlap.
The jet page demonstrates Python/Excel calculation parity for 2024 and separates
the regression-to-recorded-demand gap. Results and cohort diagnostic rows are saved
in `output/data/driver_reconciliation.json` and `output/data/vehicle_diagnostics.csv`.

Appendix page 15 maps national South African model coverage and four port references
from the prior report: Walvis Bay, Durban, Cape Town and Saldanha Bay. The full Africa
overview links to an enlarged South African/coastal callout; no model volumes have been allocated to ports. The map uses editable
PowerPoint shapes generated by `scripts/coverage_map.py` from public-domain Natural
Earth outlines in `assets/maps/`. Port and corridor evidence is distinct from a
validated asset or routing dataset.

Pages 5-6 show resolved demand and domestic-production assumptions and outputs for
South Africa in 2030. The medium scenario and available imports are explicitly unset.
`scripts/scenario_pages.py` reads existing provider and engine functions. The supply
page discloses duplicate/invalid source rows and uses the engine's existing first-row
selection; it does not repair or silently replace model inputs. Full paths and
asset-specific yields are described in speaker notes.

Pages 15-17 show the regional scope in Vopak blue shades, the six South African
production assets with selected pipeline connections, and Excel's terminal/provincial
fuel-storage entries. SACU and SADC excluding SACU are distinct; East Africa excludes
SADC members to avoid overlapping colour categories. Region membership sources and
pipeline source links are in speaker notes. `scripts/asset_maps.py` reads the original
workbook capacities directly, preserving Durban 2024 and Lesedi 2026 labels. Pipelines
are schematic external context, not newly implemented model constraints. Pipeline
throughput, storage stocks and refinery nameplate capacity use distinct units.

## Week 1 analytical map pack

The approved three-page outline is `story/week_1_analytical_maps_mockup.md`.
It supersedes the longer delivery-review outline. Nigel approved the three-page
scope and GIS-style cartographic treatment in chat on 6 October 2026.

Run `.venv/Scripts/python.exe pptx/scripts/build_week1_maps.py` from the repo root.
Install the additional projection dependency from `pptx/requirements.txt` in the
shared environment. The builder uses the supplied Vopak master and named
`Header only` layout, editable map geometry/text/tables, the three existing
illustrative CSVs and the Natural Earth 1:50m boundary layer.

Deliveries are versioned under `output/delivered/Vopak_Week1_Analytical_Maps_*`:
consolidated infrastructure/demand, Durban/Lesedi conditional candidate access,
and market volumes with shared-transfer reconciliation. Export the matching PDF
through PowerPoint and inspect every slide. `qa/week1_maps/build_manifest.json`
records the template/boundary hashes and projection; rendered QA stays untracked.

The revised five-slide delivery restores the existing kickoff cover and closing
page around the three analytical pages and retains the original section chevrons.
All figures and candidate access are illustrative. Accurate projection and
cartographic styling do not make the inherited schematic routes an operational
GIS network or verified service area. See `assets/maps/README.md` for evidence
limitations, owner and replacement trigger. No model assumptions were changed.

The subsequent revision follows Nigel's supplied exhibit-left/key-takeaways-right
reference. All analytical pages retain numbered interpretation; the former
volume table is now a geographic accessibility exhibit with market annotations.
Nigel selected delivered transport cost (R/litre): maps use a graduated,
explicitly illustrative road-cost surface with 25 km cells. Story settings
declare dispatch and per-km rates, classification and connection limits.
`scripts/accessibility_cartography.py` generates this example from schematic
geometry; tests check route detours, unassessed areas and terminal selection.
Operational routing, carrier rates, pipeline tariffs and customer access remain
outstanding evidence before any real reach or capture conclusion.

The six-slide revision adds a competitive-market page before closing and expands
the consolidated map's storage layer. Dated presentation evidence lives in
`story/storage_operator_inventory_2026_10_06.csv` (12 mapped site/group records,
five excluded historical/lease records) and
`story/competitive_market_evidence_2026_10_06.csv`. These are public-evidence
reporting inventories, not engine inputs or verified operating-capacity assumptions.
Vopak, Bidvest, Sasol, Transnet and Burgan Cape have separate asset roles and
product/access flags. National-map callouts group clustered inland sites;
speaker notes retain the named sites and source URLs. Coordinates are approximate
except the Tarlton point published in Transnet's tender. Transnet Jameson Park
and Vopak Lesedi remain distinct assets despite sharing an approximate map point.
Actual Vopak share is unknown; the share table is explicitly an illustration
from authored catchment volumes. Do not infer throughput from tank capacity.
Manish owns refresh/reconciliation with Nigel review: confirm Bidvest's discrepant
mixed-product totals, refresh Sasol's notice ending March 2026, check current
usable tanks/access, and obtain matched unique petrol/diesel customer deliveries.

Slide 2 now separates the working regions geographically and shades the nine
provinces by observed 2022 petrol/diesel sales volume. `provincial_demand_map.py`
requires four quarters for each of 18 province/product series and reconciles
their total against the national CSV. It reads registered assumptions without
altering them. 2022 is the latest complete year in the current provincial extract;
2023 has Q1 only. This is total volume by province, not density or a smoothed
district hotspot surface. The later opportunity figures remain illustrative,
with different denominators. `story/demand_map_regions_2026_10_06.csv` declares
working province membership; these outlines are not commercial catchments.
The competition page uses editable 100% stacked bars for current/candidate/outside
envelope shares; western/other remain visibly unassessed, not zero.

For a reporting-only revision, the builder supports
`--reuse-deck pptx/output/delivered/<previous-pack>.pptx`, preserving the validated
cost-map pages while rebuilding the demand and competition pages. A full build
without that argument computes all maps from source. Always run package checks
and inspect matching PowerPoint-rendered pages before delivering.

The seven-page revision adds a storage-by-location bar chart before closing.
It aggregates only six quantified gross-capacity records across five locations,
with operator segments; missing Sasol/Transnet capacities remain explicitly unknown.
Vopak Durban (360,246 m³) and Lesedi (140,000 m³) are taken from the cbm
`data-end-number` attributes on the current terminal pages, not their alternate
barrel values. Original HTML is retained under
`external/data/raw/vopak_storage_20261006/`. The figures are published gross
stocks, with product eligibility, usable capacity and access still outstanding.
The chart is a partial inventory, not a national fuel-storage census or market share.
