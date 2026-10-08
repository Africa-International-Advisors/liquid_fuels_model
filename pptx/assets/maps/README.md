# Map source

For newly revised maps, use the [shared geospatial reference](GEOSPATIAL_REFERENCE.md)
and its downloaded GeoJSON catalogue. This defines projection, aspect ratio and provenance.

`ne_110m_admin_0_countries.geojson` is Natural Earth public-domain country geometry,
retrieved 1 October 2026 from the Natural Earth vector repository:
https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson

Dataset: https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-0-countries/

The deck shows full Africa and enlarged Southern African views. Port markers use approximate
city/harbour locations, suitable for an evidence-coverage map, not navigation.
Port selection and corridor references come from the existing intermediary report,
PDF pages 37-38. Official context: https://www.namport.com.na/ and
https://www.transnetnationalportsauthority.net/ContactUs/Pages/Ports-Contact-Details.aspx

No terminal ownership, accessible capacity, routed fuel flow or current operating
status is inferred from the markers or lines.

Regional membership: https://sadc.int/member-states and https://www.sacu.int/about-sacu
North/West/East grouping follows the map subregion fields; SADC membership takes
precedence. Small absent islands are shown as schematic points.

Selected pipelines: Transnet Shippers Manual (September 2024), pp. 4, 19-20:
https://www.transnet.net/getFile.ashx?id=5330
NMPP capacity: https://www.transnet.net/SubsiteRender.aspx?id=6794475
Saldanha-Astron crude connection: https://www.astronenergy.co.za/about-us/refinery/
These lines are schematic endpoint connections, not surveyed alignments.

## Week 1 analytical maps, 6 October 2026

`ne_50m_admin_0_countries.geojson` was retrieved from the Natural Earth vector
repository on 6 October 2026 for the higher-resolution country boundary layer:
https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson

The presentation builder projects WGS84 coordinates into Lambert azimuthal
equal-area centred at 25 degrees east, 29 degrees south, with metric units.
Both accessibility maps use identical extent. Scale bars show a nominal 500 km
at the map centre; the north indicator follows the local projected meridian.
Transport waypoints and facility coordinates remain inherited, approximate
appendix evidence. Lesedi uses the Jameson Park-area reference point, not a
surveyed facility coordinate. Road/pipe/rail styles are matched to their legends.

Demand markers use the authored illustrative regional CSV; their area is
proportional to volume. Their position is an annotation, not measured demand
density or a provincial allocation. No validated travel-time or delivered-cost
surface, operational service area or verified customer catchment is calculated.
Candidate paths illustrate conditions to test. A future operational GIS accessibility result
requires an operational/routable network, confirmed sites, product/handling
capacity, access rights, costs and customer destinations.

Owner: Manish assembles route/customer evidence; Nigel reviews interpretation.
Replace these illustrative paths when those inputs are available, and before
claiming measured reach or investment-ready addressable volumes.

Nigel subsequently selected delivered transport cost (R/litre), with a graduated
surface like the supplied accessibility-map examples. The revised pack uses
25 km clipped cells and five sequential cost classes. For illustration only,
cost is R0.15/litre dispatch plus R0.002/litre/km on shortest paths through the
existing schematic road graph, including straight-line terminal/grid connections.
The lower example cost from Durban or Lesedi determines each cell's class.
Cells over 100 km from the sampled road geometry or without a connected path
remain unassessed. These settings are authored examples, not quotes or approvals;
see `story/illustrative_accessibility_settings.json` for the full declaration.
Fuel purchase price, taxes, storage and pipe/rail tariffs are excluded. No
cost-based regional capture is inferred: the volume annotations remain independent
illustrations. Replace rates with carrier evidence and schematic links with an
operational network before interpreting this as delivered-cost accessibility.
# Provincial demand layer

`geoboundaries_zaf_adm1_simplified.geojson` was downloaded on 6 October 2026
through https://www.geoboundaries.org/api/current/gbOpen/ZAF/ADM1/.
Metadata is preserved in `geoboundaries_zaf_adm1_metadata.json`, including the
pinned download URL, 2020 boundary year, OCHA ROSEA / South African Municipal
Demarcation Board source and CC BY 3.0 IGO licence. The provider spells Northern
Cape `Nothern Cape`; the reporting mapping explicitly normalises that name.
Projection: the existing WGS84 LAEA map; display simplification 1,500 m in projected
space. Lesotho remains outside the South African demand layer.

Colour represents 2022 annual petrol/diesel sales in billion litres per province,
from the declared quarterly departmental series; it does not imply within-province
uniformity or a district-level hotspot. Each product/province has all four quarters;
the sum reconciles to the national annual source within one litre. Raw received
workbooks remain in `external/`; extraction is provisional until analyst review.
Working regions are province unions from the dated story CSV and are not validated
terminal service areas. Owner: Manish, Nigel review. Refresh trigger: a later
complete provincial source year, improved boundaries, or agreed region definitions.
