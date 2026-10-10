"""Draw the Durban to Jameson Park fuel pipeline against the two Vopak terminals.

Reads the map layers already delivered with the road-network reference:

    output/delivered/geospatial/2026_10_08/pipelines.geojson     OpenStreetMap ways tagged as pipelines
    output/delivered/geospatial/2026_10_07/ne_10m_populated_places_southern_africa.geojson    Natural Earth towns
    output/delivered/geospatial/2026_10_07/ne_50m_admin_0_countries_southern_africa.geojson

and writes, under ``output/delivered/geospatial/2026_10_09/``:

    nmpp_vopak_terminals.png        the map
    nmpp_vopak_terminals.geojson    the pipeline and the marked sites
    nmpp_vopak_terminals.json       the pipeline's length and each site's distance from it

The pipeline is the set of ways OpenStreetMap names "New Multi-Product
Pipeline", operator Transnet Pipelines. A mapped line shows where the pipe
runs. It does not show who may use it or at what rate.

The two Vopak sites are not in OpenStreetMap by name. Durban is placed at the
Island View suburb node and Lesedi at the inland end of the mapped pipeline,
Transnet's Jameson Park terminal, to which its licence says it is connected.
Neither is a surveyed site position.

Run:
    python -m lfm.scripts.build_pipeline_map
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LAYERS = Path("output/delivered/geospatial")
OUT = LAYERS / "2026_10_09"
PIPELINE_NAME = "New Multi-Product Pipeline"
WEST, EAST, SOUTH, NORTH = 26.6, 32.9, -30.6, -25.4
ISLAND_VIEW = (31.0375, -29.8902778)                 # OpenStreetMap node 262707234, the Island View suburb
TOWNS = ["Johannesburg", "Pretoria", "Pietermaritzburg", "Ladysmith", "Bethlehem", "Kroonstad", "Standerton", "Vereeniging", "Matola", "Mbombela"]
LEASE_SITES = {"Kroonstad", "Standerton", "Ladysmith", "Bethlehem"}          # Transnet storage sites out for proposal that are towns on the map
INK, LINE, LAND, SEA, MUTED, ACCENT = (36, 59, 83), (200, 60, 40), (245, 246, 248), (226, 235, 244), (120, 130, 140), (10, 36, 114)


def distance_km(a, b) -> float:
    """Great-circle distance between two (longitude, latitude) points."""
    lon1, lat1, lon2, lat2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 6371.0088 * 2 * math.asin(math.sqrt(h))


def pipeline_ways() -> list[list[tuple[float, float]]]:
    data = json.loads((LAYERS / "2026_10_08" / "pipelines.geojson").read_text(encoding="utf-8"))
    return [[tuple(point) for point in f["geometry"]["coordinates"]] for f in data["features"]
            if f["properties"].get("name") == PIPELINE_NAME and f["geometry"]["type"] == "LineString"]


def measures(ways) -> dict:
    points = [p for way in ways for p in way]
    inland_end = min(points, key=lambda p: p[0])                 # the westernmost point is the Jameson Park end
    coastal_end = max(points, key=lambda p: p[0])
    return {
        "pipeline_length_km": round(sum(distance_km(a, b) for way in ways for a, b in zip(way, way[1:])), 1),
        "ways": len(ways),
        "coastal_end": [round(v, 4) for v in coastal_end],
        "inland_end": [round(v, 4) for v in inland_end],
        "straight_line_end_to_end_km": round(distance_km(coastal_end, inland_end), 1),
        "island_view_to_pipeline_km": round(min(distance_km(ISLAND_VIEW, p) for p in points), 1),
        "lesedi_position": "placed at the inland end of the mapped pipeline (Transnet's Jameson Park terminal); not a surveyed site position",
    }


def towns() -> dict[str, tuple[float, float]]:
    data = json.loads((LAYERS / "2026_10_07" / "ne_10m_populated_places_southern_africa.geojson").read_text(encoding="utf-8"))
    found = {}
    for f in data["features"]:
        name = f["properties"].get("NAME")
        if name in TOWNS:
            found.setdefault(name, tuple(f["geometry"]["coordinates"][:2]))
    return found


def draw(ways, places: dict, m: dict, path: Path) -> None:
    scale = 260                                                  # pixels a degree of latitude
    squeeze = math.cos(math.radians((SOUTH + NORTH) / 2))        # a degree of longitude is shorter this far south
    width, height = int((EAST - WEST) * scale * squeeze), int((NORTH - SOUTH) * scale)
    title_band = 120
    image = Image.new("RGB", (width, height + title_band), "white")
    pen = ImageDraw.Draw(image)

    def xy(lon, lat):
        return (lon - WEST) * scale * squeeze, title_band + (NORTH - lat) * scale

    def font(size, bold=False):
        try:
            return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
        except OSError:
            return ImageFont.load_default()

    pen.rectangle([0, title_band, width, height + title_band], fill=SEA)
    countries = json.loads((LAYERS / "2026_10_07" / "ne_50m_admin_0_countries_southern_africa.geojson").read_text(encoding="utf-8"))
    for f in countries["features"]:
        geometry = f["geometry"]
        polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
        for polygon in polygons:
            pen.polygon([xy(*p[:2]) for p in polygon[0]], fill=LAND, outline=(170, 178, 188))
    for way in ways:
        pen.line([xy(*p) for p in way], fill=LINE, width=6, joint="curve")
    for name, (lon, lat) in places.items():
        x, y = xy(lon, lat)
        lease = name in LEASE_SITES
        pen.ellipse([x - 6, y - 6, x + 6, y + 6], fill="white" if lease else MUTED, outline=INK, width=2)
        pen.text((x + 10, y - 11), name + (" (Transnet storage site out for proposal)" if lease else ""), fill=INK, font=font(19))
    for label, (lon, lat), dx, dy in (("Vopak Terminal Durban, Island View", ISLAND_VIEW, 18, -13),
                                      ("Vopak Lesedi, Jameson Park", tuple(m["inland_end"]), -290, 16)):
        x, y = xy(lon, lat)
        pen.rectangle([x - 11, y - 11, x + 11, y + 11], fill=ACCENT, outline="white", width=2)
        pen.text((x + dx, y + dy), label, fill=ACCENT, font=font(22, bold=True))
    pen.rectangle([0, 0, width, title_band], fill="white")
    pen.text((24, 16), "The Durban to Jameson Park fuel pipeline and the two Vopak terminals", fill=INK, font=font(30, bold=True))
    pen.text((24, 60), f"Red: Transnet's multi-product pipeline as mapped, {m['pipeline_length_km']:,.0f} km. Both terminals sit at its ends: Island View is "
                       f"{m['island_view_to_pipeline_km']:.0f} km from the coastal end; Lesedi connects at the inland end.", fill=INK, font=font(18))
    pen.text((24, 88), "Source: OpenStreetMap contributors (pipeline), Natural Earth (towns, borders). Site positions are approximate, not surveyed. "
                       "A mapped line does not show access or capacity.", fill=MUTED, font=font(16))
    image.save(path)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ways = pipeline_ways()
    if not ways:
        sys.exit("no way named 'New Multi-Product Pipeline' in the pipeline layer")
    m, places = measures(ways), towns()
    features = [{"type": "Feature", "properties": {"name": PIPELINE_NAME, "operator": "Transnet Pipelines", "source": "OpenStreetMap"},
                 "geometry": {"type": "MultiLineString", "coordinates": [[list(p) for p in way] for way in ways]}},
                {"type": "Feature", "properties": {"name": "Vopak Terminal Durban", "position_basis": "Island View suburb node, OpenStreetMap 262707234; not surveyed"},
                 "geometry": {"type": "Point", "coordinates": list(ISLAND_VIEW)}},
                {"type": "Feature", "properties": {"name": "Vopak Lesedi", "position_basis": m["lesedi_position"]},
                 "geometry": {"type": "Point", "coordinates": m["inland_end"]}}]
    (OUT / "nmpp_vopak_terminals.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": features}) + "\n", encoding="utf-8", newline="\n")
    (OUT / "nmpp_vopak_terminals.json").write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8", newline="\n")
    draw(ways, places, m, OUT / "nmpp_vopak_terminals.png")
    print(f"wrote {OUT / 'nmpp_vopak_terminals.png'}; {m}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
