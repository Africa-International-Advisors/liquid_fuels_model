"""Diesel by model segment beside the energy balance sectors, for the agriculture and industry baselines.

Runs the six demand segments on the vintage as it stands and on a copy with the
agriculture and industry base-year volumes set to their earlier placeholders, so
the effect of the sourced values is measured with the unchanged engine. Writes:

    workstreams/WS1_data_validation/sector_baselines_2026-10-07.csv

Columns: scenario, period, segment, product, with_sourced_baselines,
with_placeholders, difference (litres).

Run:
    python -m lfm.scripts.build_sector_baseline_review --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import os
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

OUT = Path("workstreams/WS1_data_validation/sector_baselines_2026-10-07.csv")
YEARS = (2024, 2030, 2035)
SCENARIOS = ("high_demand", "low_demand")
# The unsourced values the two files carried before 6 October 2026.
PLACEHOLDERS = {"industrial.yaml": {"value": 2.5e9, "year": 2024}, "agriculture.yaml": {"value": 0.7e9, "year": 2024}}
FIELDS = ["scenario", "period", "segment", "product", "with_sourced_baselines", "with_placeholders", "difference"]


def segment_volumes(vintage: str, scenario: str) -> dict[tuple[int, str, str], float]:
    """Annual litres by ``(year, segment, product)`` from the engine's own segment modules."""
    from lfm.assumptions import YamlDirectoryProvider
    from lfm.assumptions.snapshot import SnapshotProvider
    from lfm.config import Paths
    from lfm.model.demand import agriculture, aviation, generation, industrial, marine, vehicles
    from lfm.run import Run

    run = Run(vintage=vintage, scenario=scenario)
    provider = SnapshotProvider(YamlDirectoryProvider(Paths.default()), run)
    out: dict[tuple[int, str, str], float] = {}
    for module in (vehicles, aviation, generation, industrial, marine, agriculture):
        frame = module.compute_demand(provider, run).frame
        if frame.empty:
            continue
        frame = frame.assign(year=frame["period"].astype(str).str[:4].astype(int))
        frame = frame[frame["year"].isin(YEARS) & (frame["country"] == "ZAF")]
        for (year, product), volume in frame.groupby(["year", "product"])["volume"].sum().items():
            out[(int(year), module.name, product)] = float(volume)
    return out


def with_placeholders(vintage: str, scenario: str) -> dict[tuple[int, str, str], float]:
    from lfm.config import Paths

    source = Paths.default().vintage_dir(vintage)
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "assumptions" / vintage
        shutil.copytree(source, copy)
        for name, old in PLACEHOLDERS.items():
            data = yaml.safe_load((copy / name).read_text(encoding="utf-8"))
            data["base_year_volume"]["by_country"]["ZAF"] = dict(old)
            (copy / name).write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        previous = os.environ.get("LFM_ASSUMPTIONS_DIR")
        os.environ["LFM_ASSUMPTIONS_DIR"] = str(copy.parent)
        try:
            return segment_volumes(vintage, scenario)
        finally:
            if previous is None:
                del os.environ["LFM_ASSUMPTIONS_DIR"]
            else:
                os.environ["LFM_ASSUMPTIONS_DIR"] = previous


def build_rows(vintage: str, scenarios: tuple[str, ...]) -> list[dict]:
    rows = []
    for scenario in scenarios:
        new, old = segment_volumes(vintage, scenario), with_placeholders(vintage, scenario)
        for key in sorted(new):
            rows.append({"scenario": scenario, "period": key[0], "segment": key[1], "product": key[2],
                         "with_sourced_baselines": round(new[key]), "with_placeholders": round(old[key]),
                         "difference": round(new[key] - old[key])})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    args = parser.parse_args()
    rows = build_rows(args.vintage, SCENARIOS)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows -> {OUT}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
