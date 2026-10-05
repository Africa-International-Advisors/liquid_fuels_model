"""Derive the petrol / diesel split of the vehicle fleet by segment, December 2023.

No recent split of the fleet by vehicle class AND fuel is published. Three
things are:

  1. vehicles by class, December 2023            (NaTIS, official)
  2. vehicles by fuel, December 2023             (Transport Statistics Bulletin, official)
  3. vehicles by class and fuel, 2010            (Stone et al. 2018, published)

This script scales the 2010 pattern (3) until it matches the 2023 totals (1)
and (2), by proportional fitting. The pattern says how petrol and diesel
divide between passenger and light commercial vehicles; the totals say how
many of each there are now. Nothing is tuned to fuel sales or model output.

Fixed before fitting (not taken from the pattern):
    trucks and buses         all diesel
    motorcycles              all petrol
    other self-propelled     all diesel      <- an assumption (tractors, plant)

Reads:
    assumptions/<vintage>/timeseries/vehicle_population_natis.csv
    assumptions/<vintage>/reference/vehicle_population_by_fuel_dot2023.csv
    assumptions/<vintage>/reference/vehicle_parameters_stone2018.csv
Writes:
    assumptions/<vintage>/reference/fleet_fuel_split_2023.csv
    assumptions/<vintage>/reference/fleet_fuel_split_2023.sources.yaml

Run:
    python -m lfm.scripts.derive_fleet_fuel_split --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import yaml

from lfm.config import Paths
from lfm.model.core.fitting import proportional_fit

PERIOD = "2023-12"

# NaTIS classes -> model segments (agreed 5 October 2026).
SEGMENT_OF_CLASS = {
    "cars": "passenger", "minibuses": "passenger",
    "light_commercial": "light_commercial",
    "trucks": "heavy", "buses": "heavy",
    "motorcycles": "motorcycles",
    "other_self_propelled": "other_self_propelled",
}
# Segments whose fuel is fixed rather than fitted.
FIXED_FUEL = {"heavy": "diesel", "motorcycles": "petrol", "other_self_propelled": "diesel"}
FITTED = ("passenger", "light_commercial")
FUELS = ("petrol", "diesel")

# Vehicle types in the 2018 paper -> fitted segments. Cars, SUVs and minibus
# taxis are passenger; hybrids count under the fuel they burn.
PAPER_PREFIX = {"Car": "passenger", "SUV": "passenger", "MBT": "passenger",
                "LCV": "light_commercial"}
PAPER_FUEL = {"petrol": "petrol", "petrol_hybrid": "petrol",
              "diesel": "diesel", "diesel_hybrid": "diesel"}

# Unsourced shares in the model as inherited, kept only for comparison.
PYTHON_PETROL_SHARE = {"passenger": 0.83, "light_commercial": 0.30}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    args = parser.parse_args()

    vintage = Paths.default().vintage_dir(args.vintage)
    reference = vintage / "reference"

    by_segment = _fleet_by_segment(vintage / "timeseries" / "vehicle_population_natis.csv")
    by_fuel = _fleet_by_fuel(reference / "vehicle_population_by_fuel_dot2023.csv")
    pattern = _pattern_2010(reference / "vehicle_parameters_stone2018.csv")

    # What is left for passenger and light commercial once the fixed segments are taken out.
    remaining = dict(by_fuel)
    for segment, fuel in FIXED_FUEL.items():
        remaining[fuel] -= by_segment[segment]
    row_totals = [by_segment[s] for s in FITTED]
    # The two official counts come from different publications and differ slightly
    # in total. The class counts are kept; the fuel totals are scaled to meet them.
    adjustment = sum(row_totals) / sum(remaining.values())
    column_totals = [remaining[f] * adjustment for f in FUELS]

    fitted = proportional_fit(
        [[pattern[s][f] for f in FUELS] for s in FITTED], row_totals, column_totals)

    rows: list[dict] = []
    for i, segment in enumerate(FITTED):
        for j, fuel in enumerate(FUELS):
            rows.append(_row(segment, fuel, fitted[i][j], row_totals[i], "fitted"))
    for segment, fuel in FIXED_FUEL.items():
        rows.append(_row(segment, fuel, by_segment[segment], by_segment[segment], "fixed"))

    out = reference / "fleet_fuel_split_2023.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    shares = {s: fitted[i][0] / row_totals[i] for i, s in enumerate(FITTED)}
    doc = {
        "what": "Petrol / diesel split of the registered fleet by model segment, December 2023",
        "status": "derived estimate; totals official, pattern published, split calculated",
        "method": "iterative proportional fitting of the 2010 pattern to 2023 totals",
        "inputs": {
            "vehicles_by_class": "timeseries/vehicle_population_natis.csv (NaTIS, 2023-12)",
            "vehicles_by_fuel": "reference/vehicle_population_by_fuel_dot2023.csv",
            "pattern_2010": "reference/vehicle_parameters_stone2018.csv (vehicles_2010)",
        },
        "segments": {
            "passenger": "cars + minibuses",
            "light_commercial": "LDVs, panel vans, light load vehicles up to 3500 kg",
            "heavy": "trucks + buses",
        },
        "fixed_before_fitting": {
            "heavy": "all diesel",
            "motorcycles": "all petrol",
            "other_self_propelled": "all diesel (assumption: tractors and plant)",
        },
        "fuel_totals_scaled_by": round(adjustment, 6),
        "petrol_share": {
            "pattern_2010": {s: round(pattern[s]["petrol"] / sum(pattern[s].values()), 4)
                             for s in FITTED},
            "fitted_2023": {s: round(shares[s], 4) for s in FITTED},
            "python_model_as_inherited": PYTHON_PETROL_SHARE,
        },
        "limits": [
            "The division between passenger and light commercial is not observed; "
            "it follows the 2010 pattern as far as the 2023 totals allow.",
            "This is the fleet on the road, not new sales. Recent sales will be "
            "more diesel than the fleet as a whole.",
            "Replace with the traffic authority's own class-by-fuel count if obtained.",
        ],
    }
    (reference / "fleet_fuel_split_2023.sources.yaml").write_text(
        yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")

    for segment in FITTED:
        print(f"[split] {segment:<17} petrol {shares[segment]:.1%}  "
              f"(2010 pattern {doc['petrol_share']['pattern_2010'][segment]:.1%}, "
              f"Python {PYTHON_PETROL_SHARE[segment]:.0%})", file=sys.stderr)
    print(f"[split] wrote {out.name}; fuel totals scaled by {adjustment:.4f} "
          "to agree with the class counts", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------- #

def _fleet_by_segment(path: Path) -> dict[str, float]:
    totals: dict[str, float] = {}
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["period"] == PERIOD and row["province"] == "ZAF":
                segment = SEGMENT_OF_CLASS.get(row["vehicle_class"])
                if segment:
                    totals[segment] = totals.get(segment, 0.0) + float(row["value"])
    missing = set(SEGMENT_OF_CLASS.values()) - set(totals)
    if missing:
        sys.exit(f"{path.name}: no {PERIOD} figure for {', '.join(sorted(missing))} — "
                 "run python -m lfm.scripts.fetch_natis first")
    return totals


def _fleet_by_fuel(path: Path) -> dict[str, float]:
    with path.open(encoding="utf-8") as fh:
        found = {row["fuel_type"]: float(row["vehicles"]) for row in csv.DictReader(fh)
                 if row["period"] == PERIOD}
    return {fuel: found[fuel] for fuel in FUELS}


def _pattern_2010(path: Path) -> dict[str, dict[str, float]]:
    pattern = {segment: dict.fromkeys(FUELS, 0.0) for segment in FITTED}
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            segment = next((s for prefix, s in PAPER_PREFIX.items()
                            if row["vehicle_type"].startswith(prefix)), None)
            fuel = PAPER_FUEL.get(row["fuel"])
            if segment and fuel:
                pattern[segment][fuel] += float(row["vehicles_2010"])
    return pattern


def _row(segment: str, fuel: str, vehicles: float, segment_total: float, basis: str) -> dict:
    return {"country": "ZAF", "period": PERIOD, "segment": segment, "fuel": fuel,
            "vehicles": round(vehicles), "share_of_segment": round(vehicles / segment_total, 4),
            "basis": basis}


if __name__ == "__main__":
    sys.exit(main())
