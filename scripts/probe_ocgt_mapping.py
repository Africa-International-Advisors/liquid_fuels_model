"""Probe: which scenario should `PowerGenLoadFactor_High` map to?

Background
----------
The xlsx defines two OCGT load-factor paths: `_High` (drops to ~0.14 by 2026)
and `_Low` (sustains ~0.7). Their column headers say "High EAF" / "Low EAF",
which suggests they describe *grid availability*, not OCGT utilisation:

  - High EAF = healthy grid = less load shedding = LOW OCGT diesel demand
  - Low EAF  = stressed grid = more load shedding = HIGH OCGT diesel demand

For our two-scenario world the question is which load-factor series belongs
in each. There are two coherent narratives:

  Mapping A (current — `_meta.yaml`):
    high_demand -> PowerGenLoadFactor_High (low OCGT use)
    low_demand  -> PowerGenLoadFactor_Low  (high OCGT use)
    Reasoning: high GDP -> grid investment -> less load shedding.

  Mapping B (alternative):
    high_demand -> PowerGenLoadFactor_Low  (high OCGT use)
    low_demand  -> PowerGenLoadFactor_High (low OCGT use)
    Reasoning: high fuel demand worldview should consistently push
    OCGT diesel upward, alongside higher GDP and lower EV penetration.

This script computes annual OCGT diesel under each mapping × each scenario and
prints a side-by-side view. The xlsx Notes sheet is silent on this question
(it documents jet fuel methodology only), so the choice is a stakeholder
narrative call. This script is the input to that decision, not the answer.

Run:
    python scripts/probe_ocgt_mapping.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent

LOAD_FACTOR_CSV = REPO / "assumptions/2026/timeseries/ocgt_load_factor.csv"
OPERATIONAL_MW = 3072  # Ankerlig + Gourikwa + Avon + Dedisa
EFFICIENCY = 0.4
MJ_PER_LITRE = 36.9
OPERATIONAL_DAYS = 365
HOURS_PER_DAY = 24
MWH_TO_MJ = 3600


def diesel_litres(load_factor: float) -> float:
    elec_mwh = OPERATIONAL_MW * HOURS_PER_DAY * OPERATIONAL_DAYS * load_factor
    fuel_mwh = elec_mwh / EFFICIENCY
    fuel_mj = fuel_mwh * MWH_TO_MJ
    return fuel_mj / MJ_PER_LITRE


def main() -> int:
    df = pd.read_csv(LOAD_FACTOR_CSV)
    pivot = df.pivot_table(
        index="period", columns="scenario", values="value", aggfunc="first"
    ).rename(columns={"high_demand": "_High", "low_demand": "_Low"})
    pivot = pivot.sort_index()

    print("\n=== ZAF OCGT load factor (raw, from xlsx) ===\n")
    print(pivot.round(4).to_string())

    diesel = pd.DataFrame({
        "load_factor_High_BL": pivot["_High"].apply(diesel_litres) / 1e9,
        "load_factor_Low_BL":  pivot["_Low"].apply(diesel_litres) / 1e9,
    }).round(2)
    diesel.index.name = "year"

    print("\n=== Implied OCGT diesel under each load-factor series (BL/yr) ===\n")
    print(diesel.to_string())

    print("\n=== Side-by-side mapping comparison ===\n")
    out = pd.DataFrame({
        "high_demand_diesel_BL  (Mapping A)": diesel["load_factor_High_BL"],
        "low_demand_diesel_BL   (Mapping A)": diesel["load_factor_Low_BL"],
        "high_demand_diesel_BL  (Mapping B)": diesel["load_factor_Low_BL"],
        "low_demand_diesel_BL   (Mapping B)": diesel["load_factor_High_BL"],
    })
    print(out.round(2).to_string())

    print(
        "\nReading guide:\n"
        "  Under Mapping A (current), high_demand has LESS OCGT diesel than low_demand\n"
        "  (e.g. 2030: high=~0.27 BL vs low=~3.78 BL).\n"
        "  Under Mapping B (flipped), high_demand has MORE OCGT diesel than low_demand.\n"
        "\n"
        "  If the high_demand worldview is meant to be 'lots of liquid fuel needed'\n"
        "  internally consistent (high GDP + low EV pen + heavy load-shedding-driven\n"
        "  diesel), Mapping B is more coherent. If it's meant to be 'high economic\n"
        "  growth that fixes the grid as a side effect', Mapping A is more coherent.\n"
        "\n"
        "  Decide and update assumptions/2026/_meta.yaml::xlsx_scenario_mapping.\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
