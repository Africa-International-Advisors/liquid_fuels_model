# South Africa and regional geospatial library

[Layer catalogue](catalog.json) | [Corrected corridor map](corridor_map.png) | [Shared mapping contract](../../../../pptx/assets/maps/GEOSPATIAL_REFERENCE.md)

Downloaded 7 October 2026; source bytes preserved in `external/sources/geospatial/2026_10_07`.
GeoJSON coordinates are longitude/latitude, WGS84. Open individual layers directly in GIS software.

| Layer | Features | Source |
|---|---:|---|
| [Countries](ne_50m_admin_0_countries_southern_africa.geojson) | 10 | Natural Earth, 1:50m |
| [Roads](ne_10m_roads_southern_africa.geojson) | 1,300 | Natural Earth, 1:10m |
| [Railways](ne_10m_railroads_southern_africa.geojson) | 324 | Natural Earth, 1:10m |
| [Ports](ne_10m_ports_southern_africa.geojson) | 11 | Natural Earth, 1:10m |
| [Populated places](ne_10m_populated_places_southern_africa.geojson) | 185 | Natural Earth, 1:10m |
| [South African provinces](geoboundaries_zaf_adm1.geojson) | 9 | geoBoundaries; see catalogue for licence and boundary vintage |
| [Authored places](authored_places.geojson) | 10 | Existing project coordinates; approximate |
| [Authored corridors](authored_corridors.geojson) | 4 | Existing schematic waypoints; not source route alignments |

The region selects features intersecting 10–36°E, 36–16°S; country outlines may extend
beyond it. Counts refer to geometric features, not distinct operating routes or facilities.
Natural Earth is public domain. Provider metadata and hashes are in the catalogue.
Province attribution: OCHA ROSEA / South African Municipal Demarcation Board,
via geoBoundaries; boundaries represent 2020, CC BY 3.0 IGO.
Road and rail layers are cartographic context; they do not establish service availability,
liquid-fuel capability or network connectivity. Pipeline and terminal geometry remain
an evidence gap, owned by the analyst team before operational routing is adopted.

New maps use the shared LAEA projection and equal horizontal/vertical scale. Historical
deliverables remain preserved; other legacy builders migrate when their slides are revised.
