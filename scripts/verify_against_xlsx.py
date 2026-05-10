"""Verify that ZAF scalar/table values in the assumption YAMLs match the
original xlsx's named-range / sheet-cell values.

What this DOES NOT check:
  - Time-series CSVs under assumptions/<vintage>/timeseries/. Those are
    extracted mechanically by `extract_xlsx_to_assumptions.py` and re-running
    that script is the way to refresh them; this verifier wouldn't add
    information.
  - BLNS values (they are intentionally null in v1).
  - Output behaviour (no engine yet).

Exit code:
  0   all checks pass
  1   at least one drift exceeds tolerance — prints a diff per failing key

Run:
  python scripts/verify_against_xlsx.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

import openpyxl
import yaml

REPO = Path(__file__).resolve().parent.parent
XLSX = REPO / "docs" / "Liquid Fuels Model - Supply Demand, 2025 - Reatile Copy.xlsx"
VINTAGE = REPO / "assumptions" / "2026"

# Floating-point tolerance for comparing numbers. The xlsx cached values are
# IEEE-754 doubles; YAML round-trips through string. 1e-6 relative is plenty.
RTOL = 1e-6
ATOL = 1e-9


# --------------------------------------------------------------------------- #
# Helpers

def yaml_load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def named_range_rows(wb, name: str) -> list[list]:
    dn = wb.defined_names[name]
    rows: list[list] = []
    for sheet_title, coord in dn.destinations:
        ws = wb[sheet_title]
        cells = ws[coord]
        if hasattr(cells, "value"):
            rows.append([cells.value])
        else:
            for row in cells:
                if hasattr(row, "value"):
                    rows.append([row.value])
                else:
                    rows.append([c.value for c in row])
    return rows


def named_range_scalar(wb, name: str) -> Any:
    rows = named_range_rows(wb, name)
    return rows[0][0]


def cell(wb, sheet: str, coord: str) -> Any:
    return wb[sheet][coord].value


def numbers_match(a: Any, b: Any) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    try:
        return math.isclose(float(a), float(b), rel_tol=RTOL, abs_tol=ATOL)
    except (TypeError, ValueError):
        return a == b


# --------------------------------------------------------------------------- #
# Check registry

class Verifier:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.checks_run = 0

    def check(self, label: str, yaml_value: Any, xlsx_value: Any) -> None:
        self.checks_run += 1
        if not numbers_match(yaml_value, xlsx_value):
            self.failures.append(
                f"  [DRIFT] {label}\n"
                f"          YAML: {yaml_value!r}\n"
                f"          xlsx: {xlsx_value!r}"
            )

    def report(self) -> int:
        print(f"\nRan {self.checks_run} checks.")
        if not self.failures:
            print("All checks passed.")
            return 0
        print(f"{len(self.failures)} drift(s) detected:")
        for f in self.failures:
            print(f)
        return 1


# --------------------------------------------------------------------------- #
# Per-domain checks

def check_vehicles(wb, v: Verifier) -> None:
    y = yaml_load(VINTAGE / "vehicles.yaml")

    # EV S-curve — xlsx has scenario tables with three rows (penetration, midpoint, slope).
    # Our high_demand scenario maps to xlsx EV_Low_Penetration.
    low_pen = [r[0] for r in named_range_rows(wb, "EV_Low_Penetration")[1:]]
    high_pen = [r[0] for r in named_range_rows(wb, "EV_High_Penetration")[1:]]
    yaml_high = y["ev_scurve"]["by_country"]["ZAF"]["by_scenario"]["high_demand"]
    yaml_low = y["ev_scurve"]["by_country"]["ZAF"]["by_scenario"]["low_demand"]

    v.check("vehicles.ev_scurve.ZAF.high_demand.max_penetration", yaml_high["max_penetration"], low_pen[0])
    v.check("vehicles.ev_scurve.ZAF.high_demand.midpoint",        yaml_high["midpoint"],        low_pen[1])
    v.check("vehicles.ev_scurve.ZAF.high_demand.slope",           yaml_high["slope"],           low_pen[2])
    v.check("vehicles.ev_scurve.ZAF.low_demand.max_penetration",  yaml_low["max_penetration"],  high_pen[0])
    v.check("vehicles.ev_scurve.ZAF.low_demand.midpoint",         yaml_low["midpoint"],         high_pen[1])
    v.check("vehicles.ev_scurve.ZAF.low_demand.slope",            yaml_low["slope"],            high_pen[2])

    # New-vehicle regression coefficients live as raw cells in `fEV Penetration`.
    yaml_reg = y["new_vehicle_regression"]["by_country"]["ZAF"]
    v.check("vehicles.new_vehicle_regression.ZAF.slope",
            yaml_reg["slope"],     cell(wb, "fEV Penetration", "E2"))
    v.check("vehicles.new_vehicle_regression.ZAF.intercept",
            yaml_reg["intercept"], cell(wb, "fEV Penetration", "E3"))
    # R^2 is in RegEV row 5 col 2.
    v.check("vehicles.new_vehicle_regression.ZAF.r_squared",
            yaml_reg["r_squared"], cell(wb, "RegEV", "B5"))


def check_aviation(wb, v: Verifier) -> None:
    y = yaml_load(VINTAGE / "aviation.yaml")
    yaml_reg = y["regression"]["by_country"]["ZAF"]

    v.check("aviation.regression.ZAF.coefficients.gdp_per_capita",
            yaml_reg["coefficients"]["gdp_per_capita"], cell(wb, "fJetFuel", "E2"))
    v.check("aviation.regression.ZAF.coefficients.passenger_departures",
            yaml_reg["coefficients"]["passenger_departures"], cell(wb, "fJetFuel", "E3"))
    v.check("aviation.regression.ZAF.intercept",
            yaml_reg["intercept"], cell(wb, "fJetFuel", "E4"))
    v.check("aviation.regression.ZAF.r_squared",
            yaml_reg["r_squared"], cell(wb, "RegJetFuel", "B5"))


def check_generation(wb, v: Verifier) -> None:
    y = yaml_load(VINTAGE / "generation.yaml")

    # PowerGen_Capacity has rows: ['Power Station', 'MW'] then per-station rows.
    cap_rows = named_range_rows(wb, "PowerGen_Capacity")[1:]
    xlsx_caps = {str(r[0]).strip().lower().replace(" ", "_"): r[1] for r in cap_rows}
    # First row is "Total " — skip; verify per station.
    yaml_stations = y["ocgt_capacity"]["by_country"]["ZAF"]["stations"]
    for station_name, mw in yaml_stations.items():
        xlsx_mw = xlsx_caps.get(station_name)
        v.check(f"generation.ocgt_capacity.ZAF.{station_name}", mw, xlsx_mw)

    v.check("generation.efficiency.ZAF",
            y["efficiency"]["by_country"]["ZAF"], named_range_scalar(wb, "PowerGen_Efficiency"))
    v.check("generation.mj_per_litre.value",
            y["mj_per_litre"]["value"], named_range_scalar(wb, "MJ_Litres_Conversion"))
    v.check("generation.operational_days.value",
            y["operational_days"]["value"], named_range_scalar(wb, "Operational_days"))


def check_supply(wb, v: Verifier) -> None:
    y = yaml_load(VINTAGE / "supply.yaml")

    # Refinery_capacity: 2 rows x 7 cols. r1 header (refinery names), r2 capacities.
    cap_rows = named_range_rows(wb, "Refinery_capacity")
    refineries = [str(c).strip().lower() for c in cap_rows[0][1:]]
    capacities = cap_rows[1][1:]
    xlsx_caps = dict(zip(refineries, capacities))
    yaml_caps = y["refinery_capacity"]["by_country"]["ZAF"]
    for refinery, cap in yaml_caps.items():
        v.check(f"supply.refinery_capacity.ZAF.{refinery}", cap, xlsx_caps.get(refinery))

    # SupplyFuelMix: 3 rows (gasoline, diesel, jet) x 7 cols (label + 6 refineries).
    mix_rows = named_range_rows(wb, "SupplyFuelMix")
    products = ["gasoline", "diesel", "jet_a1"]
    xlsx_mix: dict[str, dict[str, Any]] = {r: {} for r in refineries}
    for product, row in zip(products, mix_rows):
        # Row format: [product_label, e_value, sa_value, n_value, sasol_value, ast_value, pet_value]
        for refinery, val in zip(refineries, row[1:]):
            xlsx_mix[refinery][product] = val
    yaml_mix = y["refinery_product_mix"]["by_country"]["ZAF"]
    for refinery, splits in yaml_mix.items():
        for product, frac in splits.items():
            v.check(f"supply.refinery_product_mix.ZAF.{refinery}.{product}",
                    frac, xlsx_mix.get(refinery, {}).get(product))

    v.check("supply.refinery_availability.value",
            y["refinery_availability"]["value"], named_range_scalar(wb, "Refinery_availability"))


def check_macro(wb, v: Verifier) -> None:
    y = yaml_load(VINTAGE / "macro.yaml")
    v.check("macro.crude_oil_litres_per_barrel.value",
            y["crude_oil_litres_per_barrel"]["value"],
            named_range_scalar(wb, "Crude_oil_litresPerBarrel"))


# --------------------------------------------------------------------------- #
# Entrypoint

def main() -> int:
    print(f"Verifying {VINTAGE.relative_to(REPO).as_posix()} against {XLSX.name}")
    wb = openpyxl.load_workbook(XLSX, data_only=True)

    v = Verifier()
    check_vehicles(wb, v)
    check_aviation(wb, v)
    check_generation(wb, v)
    check_supply(wb, v)
    check_macro(wb, v)
    return v.report()


if __name__ == "__main__":
    sys.exit(main())
