# Road-network reference — 8 October 2026

The map and routing reference now have separate layers for geography, network
topology and presentation. Use the same projected map transform in
`pptx/scripts/geo_reference.py`; never stretch either axis independently.

## Source and database

- Raw OpenStreetMap country extracts: South Africa, Namibia, Botswana and
  Mozambique, distributed by [Geofabrik](https://download.geofabrik.de/africa.html).
  Original PBFs and SHA-256 metadata live in
  `external/sources/geospatial/2026_10_08/osm/`.
- Delivered library: `output/delivered/geospatial/2026_10_08/`.
  `catalog.json` records the exact extract URLs, retrieval times and hashes.
- `roads.geojson`, `rails.geojson`, `pipelines.geojson` and `places.geojson`
  preserve OSM IDs and source tags in EPSG:4326. Geometry does not establish
  operating service, product compatibility or contractual access.
- `transport.sqlite` stores source ways, node IDs, directed road edges,
  restriction relations and named locations. Roads connect through shared
  OSM node IDs; line crossings alone do not create junctions. Edge lengths
  are WGS84 geodesic metres. Railway and pipeline geometries are not connected
  to the road graph.
- Boundary context continues to use the separately catalogued Natural Earth
  and geoBoundaries layers. OSM and boundary sources retain their own licences.

## Routing scope

The current graph includes motorway, trunk, primary and secondary roads and
their links. The diagnostic respects basic one-way and motor-vehicle access
tags. Port/city reference points are snapped to the graph; snap offsets are
reported in `route_checks.json`. These are approximate regional endpoints,
not verified terminal gates or customer delivery points.

`connectivity_routes.geojson` contains distance-minimising graph paths where
connected. These support the map's route discussion only. They are not tanker
instructions, selected commercial corridors, travel-time forecasts or cost
estimates. A disconnected major-road graph is not proof that no road route exists.

For a future routing engine, ingest the retained full PBF extracts, including
local streets. Merge overlapping extracts consistently and use a pinned engine
version and vehicle profile. Before freight costing:

1. Verify terminal entrances and customer receiving points; review snap offsets.
2. Apply turn restrictions, conditional access, HGV, hazardous-goods, axle,
   weight and height restrictions; validate against operator knowledge.
3. Add border eligibility, border delays, tolls and product-specific access.
4. Calibrate travel times and delivered costs separately from graph distance.
5. Treat pipeline allocations and rail services as separately evidenced networks.

Owner: Manish; Nigel reviews the commercial use. These limitations expire at
the first use for freight costs, customer capture or an investment recommendation;
they must be resolved before that use. No independent operational review is recorded.

## Rebuild and checks

Use the shared `.venv` with root and presentation requirements. The reader uses
the published OSM PBF schema and the existing `protobuf==7.34.1` runtime, now
pinned in root requirements; `pyproj` and `shapely` are in the established
presentation toolchain. The attempted osmium reader was blocked by Windows
application control and is not used. No editable development dependency was added.

Run the modules `lfm.scripts.collect_osm_ranges`, `lfm.scripts.build_osm_network`
and `lfm.scripts.check_osm_network`, then `pptx/scripts/render_sa_network_map.py`.
The builder refuses to overwrite a delivered database. Use a new vintage for
refreshes. `tests/test_routing.py` checks direction/access, shortest paths and
crossings without shared nodes. `qa.json` records source hashes, node alignment,
edge endpoints and SQLite integrity. Automated checks are not operational approval.

Attribution: © OpenStreetMap contributors; data under
[ODbL 1.0](https://www.openstreetmap.org/copyright), distributed by Geofabrik.
Retain attribution and licence obligations when sharing the database or derived maps.
