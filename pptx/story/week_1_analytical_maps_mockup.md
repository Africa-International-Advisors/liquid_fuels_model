# Week 1 analytical maps: revised three-page mockup

Supersedes the 12-page delivery-review outline. Status: approved in chat on 6 October 2026;
implemented in scripts/build_week1_maps.py with cartographic rendering refinements.
Deliverables: editable PPTX and matching PDF. Following Nigel's subsequent correction,
retain the kickoff cover and closing page and its four section chevrons.
The final pack has five slides: cover, three analytical pages, closing.
Use the kickoff deck's Vopak master, named layouts, map extent, Lato, logo and footer.

## 1. South African fuel demand and the infrastructure serving it

Layout: large consolidated editable evidence map; concise right-side text.
Bring together the appendix's seven infrastructure layers: production, pipelines,
ports, roads, rail, storage and corridors. Mute secondary infrastructure so demand
and Durban/Lesedi are legible. Gas/crude routes do not establish petrol/diesel access.

Add labelled regional demand markers; do not invent provincial boundaries or
allocate grouped demand to individual provinces. Illustrative annual petrol/diesel
demand, billion litres: eastern/coastal 4.5; inland 10.0; Western 4.0; other 2.5.
Markers indicate regional geography, not measured demand density or catchment extent.

Right-side editable text:

Where demand meets supply

- Match regional demand to domestic production and imported supply.
- Connect Durban receipts with coastal customers and inland transfers to Lesedi.
- Retain competing ports, supply points and operators as context.

Closing text: Geography establishes candidate connections. Capacity, product
compatibility and customer access determine whether those connections serve demand.

Visible disclosure: Illustrative demand; infrastructure schematic. Asset inclusion
does not establish current operation or usable capacity.
Sources: kickoff infrastructure appendix; existing network/map assets; Natural Earth;
story/illustrative_market_catchments.csv.

## 2. Conditional market access from Durban and Lesedi

Layout: two maps at identical extent, Durban left and Lesedi right. Editable
route overlays and terminal/destination markers; native PowerPoint table below.
Map labels: Durban — coastal customers and inland transfers;
Lesedi — inland customers supplied through connected routes.

Highlight illustrative candidate paths and destinations, not circular catchments.
Overlapping destinations are shared opportunity, not two independent demand pools.
Observed customer destinations are unknown until actual flow evidence is supplied.
Geographical access boundaries require route-level evidence.

| Condition | Accessibility shown | Evidence required |
|---|---|---|
| Observed service | Actual destinations and terminal flows | Customer records, receipts, transfers and deliveries; not supplied |
| Existing-route candidate | Illustrative pipeline/road connections to demand | Product compatibility, available capacity, access rights, dispatch and delivered cost |
| Expanded-route candidate | Additional destinations under an explicit intervention | Specific road/rail/pipeline change, timing, feasibility and cost |

Closing text: Physical reach and commercial access are separate. Contracts,
competitors and delivered cost determine the accessible share of reachable demand.

Visible disclosure: Candidate access is illustrative and conditional. No verified
Vopak catchment or rail fuel-service claim. Client volumes exclude jet.
Source: existing appendix geography; actual flow/access evidence outstanding.

## 3. Demand, accessible volume and Vopak's current share

Layout: native PowerPoint table, national balance line above and editable flow
reconciliation below. All volumes illustrative, billion litres/year, petrol/diesel.

National balance: demand 21.0 − domestic production 7.0 = required imports 14.0.
Exports and stock movements are zero in this illustration only.

| Catchment | Demand | Feasible flows | Commercial envelope | Current unique demand served | Additional candidate |
|---|---:|---:|---:|---:|---:|
| Eastern/coastal | 4.5 | 3.8 | 2.5 | 1.0 | 1.5 |
| Inland | 10.0 | 8.2 | 6.0 | 2.0 | 4.0 |
| Combined | 14.5 | 12.0 | 8.5 | 3.0 | 5.5 |

Reconciliation: Durban receipts 2.8 + Lesedi receipts 2.0 − shared
Durban→Lesedi transfer 1.8 = unique customer demand served 3.0.

Closing text: Additional candidate volume is conditional, not forecast capture.
The envelope includes domestic and imported supply. Western/other access remains
unassessed. Storage capacity is a stock, not annual throughput.

Speaker notes: request reviewed regional demand, route constraints/access,
terminal flows, customer contracts and competitor evidence. Each future row
needs product, period, source, refresh method and actual/modelled/illustrative/unknown
status. Diagnostics support this evidence work; omit the detailed governance inventory.

Visible disclosure: Illustrative volumes only; actual Vopak throughput not supplied.
Sources: the three existing illustrative story CSVs.

## Production checks

Preserve the kickoff deck and source template. Inspect all three rendered pages;
deliver matching PPTX/PDF. Do not infer operational capacity from map connections.
Keep illustration labels visible on every page. Detailed storage sizing is optional.
The three analytical pages retain the existing chevrons, with Analytical
specifications active. Cover and closing reuse the delivered kickoff's compositions,
photographs and original image credits, with Week 1/date labels updated.

## Subsequent layout and metric correction

Nigel supplied a preferred exhibit-left/key-takeaways-right slide structure.
All three analytical slides now use that structure and numbered interpretation.
The former volumes table is replaced by a geographical accessibility exhibit
with illustrative market-volume annotations. The cover/closing/chevrons remain.

Nigel selected delivered transport cost (R/litre) as the accessibility measure.
The first surface is explicitly illustrative: shortest schematic-road distance,
straight-line terminal/grid connections, an authored R0.15/L dispatch allowance
and R0.002/L/km rate, on 25 km cells. Darker means lower illustrative cost;
grey means unassessed. Settings and evidence limitations are declared in
illustrative_accessibility_settings.json. This is not carrier-quoted cost,
validated routing, a time isochrone or a verified customer catchment.

## Competitive-market and storage revision

User requested the missing contestability/share page and a richer storage layer
on 6 October. Preserve cover, closing, chevrons and the approved exhibit/takeaway
composition. Final sequence: cover; infrastructure + demand + operator storage;
cost accessibility; conditional market volumes; competitive footprint and share;
closing. The competition exhibit lists public operator sources and site-level
evidence gaps, followed by clearly illustrative catchment-share calculations.
Actual share is unknown until matched customer-throughput evidence is received.
Storage roles include independent terminal services, marketer depots, and pipeline
accumulation; mixed-product capacities and inactive depots cannot be counted as
usable petrol/diesel capacity. Source inventory and full limitations are retained
in CSVs and slide notes, with clickable operator references on the new page.

The subsequent demand-map correction replaces illustrative circles with real
province boundaries and a 2022 reported-sales choropleth. Region unions are
explicitly declared; colours show provincial volumes, not local hotspots.
The share table becomes stacked regional bars with three segments: current
Vopak, additional candidate, outside envelope. Western/other show unassessed.
Historical observed demand is kept separate from authored share illustrations.
