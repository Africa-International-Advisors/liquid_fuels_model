# Shared geospatial reference

The 8 October road/rail/pipeline source-network layer supersedes authored corridor
lines for the market-story map. See [routing reference](ROUTING_REFERENCE.md) for
the SQLite topology database, GeoJSON layers, source PBFs and routing limitations.
The original boundary catalogue below remains the geographic context layer.

Use [reference.json](reference.json) for all newly revised South African presentation maps.
The earlier projected map layer was retained; a later ad-hoc longitude/latitude renderer
introduced unequal horizontal and vertical scales. The corridor renderer now uses the
shared projection and a single scale factor, leaving whitespace rather than stretching.

## Library

The dated GeoJSON library is `output/delivered/geospatial/2026_10_07/`.
Its `catalog.json` records source URLs, pinned Natural Earth commit, licences, hashes,
feature counts and storage paths. Received files and provider metadata are preserved
unchanged under `external/sources/geospatial/2026_10_07/`.

- Natural Earth: countries, roads, railroads, ports and populated places.
- geoBoundaries: South Africa's nine provinces, with provider licence and vintage.
- Storage: longitude, latitude in WGS84; display: Lambert azimuthal equal-area,
  centred on 25 degrees east, 29 degrees south, matching the earlier map.
- Regional extracts select whole features intersecting the stated Southern Africa extent.
  They are not clipped, routable networks or evidence of current operating service.

## Rendering contract

Load geometry through `pptx/scripts/geo_reference.py`; use `map_transform` for every
layer, marker and line. Never scale longitude and latitude independently. Preserve SVG
and PNG aspect ratios when embedding. Keep a consistent extent for compared maps.
Use a north indicator and nominal scale; no inferred driving distances from map lines.

Keep source geography separate from authored overlays. Existing corridor waypoints and
facility coordinates remain approximate in `corridor_comparison_2026_10_06.json`.
Do not relabel these as downloaded or validated alignments. Pipeline and terminal access,
fuel compatibility, service status and commercial rights require their own evidence.

Historical deck vintages are preserved. Other legacy map builders migrate to this
reference when their slides are revised; they have not all been retrofitted.

Owner: Nigel / analyst team. Refresh on a new mapping vintage or material geographic
correction. Verify operating routes and facility positions before quantitative routing.

Rebuild: `.venv/Scripts/python.exe pptx/scripts/collect_geo_reference.py`.
Check: `.venv/Scripts/python.exe pptx/scripts/check_geo_reference.py`.
Natural Earth terms: https://www.naturalearthdata.com/about/terms-of-use/
geoBoundaries API: https://www.geoboundaries.org/api.html
