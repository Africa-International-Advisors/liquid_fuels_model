"""Build the DR08 refinery supply evidence table from the registered inputs.

DR08 asks for each refinery, PetroSA included: capacity, output, yields,
utilisation, feedstock and closure or restart dates. This writes one row per
fact, each with its value, period, status, source and open gap:

    workstreams/WS1_data_validation/dr08_refinery_evidence_2026-10-08.csv

Values are read from ``reference/refinery_evidence_points.csv`` (figures typed
from the department, the operators and the Central Energy Fund), the
department's energy balances and ``reference/refinery_output_operators.csv``.
Status is ``observed``, ``inferred`` (calculated here) or ``not available``.
FIASA and JODI are not used.

Run:
    python -m lfm.scripts.build_dr08_refinery_evidence --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from lfm.config import Paths

OUT = Path("workstreams/WS1_data_validation/dr08_refinery_evidence_2026-10-08.csv")
FIELDS = ["request", "part", "item", "asset_or_route", "value", "unit", "period", "status", "source", "original_file", "page",
          "unresolved_gap", "scope"]
PARTS = ["Capacity", "Status and dates", "Output by plant", "National output by product", "Yields", "Utilisation", "Outlook"]
PLANTS = ["Secunda", "Natref", "Astron Energy", "Sapref", "Enref", "PetroSA"]
NATREF_SASOL_SHARE = 0.6364
BALANCE_YEARS = range(2014, 2022)


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load(vintage: Path) -> dict:
    ts, ref = vintage / "timeseries", vintage / "reference"
    d: dict = {"points": _read(ref / "refinery_evidence_points.csv")}
    d["production"] = {(r["product"], int(r["period"])): float(r["value"]) / 1e9
                       for r in _read(ts / "energy_balance_department.csv") if r["flow_key"] == "production"}
    d["operators"] = {(r["plant"], int(r["period"])): r for r in _read(ref / "refinery_output_operators.csv")}
    return d


def capacity(d: dict) -> dict[str, float]:
    """Published capacity by plant, barrels a day, latest department table."""
    return {p["subject"]: float(p["value"]) for p in d["points"] if p["series"] == "capacity_department_2023"}


def utilisation(d: dict) -> dict[tuple[str, int], float]:
    """Reported output over published capacity, for the plants whose output is reported in barrels.

    Natref's reported figure is Sasol's 63.64% share, scaled to the whole refinery. The year to June 2026 is left
    out for Natref because Sasol's figure that year includes output above its share.
    """
    cap = capacity(d)
    out: dict[tuple[str, int], float] = {}
    for (plant, year), row in d["operators"].items():
        if row["unit"] != "million barrels":
            continue
        days = 366 if year % 4 == 0 else 365
        if plant == "Secunda":
            out[(plant, year)] = float(row["value"]) * 1e6 / (cap["Secunda"] * days)
        elif plant == "Natref" and year != 2026:
            out[(plant, year)] = float(row["value"]) * 1e6 / NATREF_SASOL_SHARE / (cap["Natref"] * days)
    return out


def build(d: dict) -> list[dict]:
    rows: list[dict] = []
    points: dict[str, list[dict]] = {}
    for point in d["points"]:
        points.setdefault(point["series"], []).append(point)

    def add(part, item, subject, value, unit, period, status, source, original="", page="", gap=""):
        rows.append(dict(request="DR08", part=part, item=item, asset_or_route=subject, value=value, unit=unit, period=period, status=status,
                         source=source, original_file=original, page=page, unresolved_gap=gap, scope="petrol and diesel"))

    def from_point(part, item, p, status="observed"):
        add(part, item, p["subject"], p["value"], p["unit"], p["period"], status, p["source"], p["original_file"], p["page"], p["note"])

    # --- capacity -----------------------------------------------------------
    for p in points["capacity_department_2023"]:
        from_point("Capacity", "Published capacity", p)
    for p in points["capacity_department_2021"]:
        from_point("Capacity", "Published capacity before the closures", p)
    for p in points["capacity_operator"]:
        from_point("Capacity", "Capacity stated by the operator", p)
    cap = capacity(d)
    add("Capacity", "Capacity in operation", "Secunda, Natref and Astron Energy",
        f"{cap['Secunda'] + cap['Natref'] + cap['Astron Energy']:,.0f}", "barrels a day, crude equivalent", "2023 onward", "inferred",
        "Sum of the three plants operating", "", "", "Half of the 718,000 published in 2021. Sapref is still listed at 180,000 by the department although it is not refining.")

    # --- status and dates -----------------------------------------------------
    for p in points["status"]:
        from_point("Status and dates", "Status", p)

    # --- output by plant ------------------------------------------------------
    for plant, label in (("Secunda", "Secunda, all refined products"), ("Natref", "Natref, Sasol's share"),
                         ("Astron Energy (Cape Town)", "Astron Energy, all refined products")):
        series = sorted(((y, r) for (pl, y), r in d["operators"].items() if pl == plant), key=lambda x: x[0])
        unit = series[0][1]["unit"]
        add("Output by plant", "Output reported by the operator", label, "; ".join(f"{float(r['value']):,.1f}" if unit == "million barrels" else f"{float(r['value']):,.0f}"
                                                                                  for _, r in series), unit,
            ("years to June " if "June" in series[0][1]["period_basis"] else "") + "; ".join(str(y) for y, _ in series), "observed",
            "Sasol production and sales metrics" if plant != "Astron Energy (Cape Town)" else "Glencore annual reports",
            "assumptions/2026/reference/refinery_output_operators.csv", "",
            "All products together. No operator reports petrol and diesel separately."
            + (" Sasol's 63.64% share only; the year to June 2026 includes output above that share." if plant == "Natref" else "")
            + (" Reported as energy content, not volume." if plant.startswith("Astron") else ""))
    for p in points["secunda_fuels"]:
        from_point("Output by plant", "Secunda fuels output", p)
    add("Output by plant", "Petrol and diesel output by plant", "Every plant", "", "litres", "", "not available", "None published", "", "",
        "No operator publishes petrol and diesel volumes by plant. Needs the operators, through Nigel.")
    add("Output by plant", "Output of Sapref, Enref and PetroSA", "Plants not operating", "0", "", "while not operating", "inferred",
        "From the status rows", "", "", "PetroSA since December 2020; the stop dates for Sapref and Enref are not in a source held.")

    # --- national output by product -------------------------------------------
    years = [y for y in BALANCE_YEARS if ("petrol", y) in d["production"]]
    for product in ("petrol", "diesel"):
        add("National output by product", f"{product.capitalize()} produced, all plants", "South Africa",
            "; ".join(f"{d['production'][(product, y)]:.2f}" for y in years), "billion litres", "; ".join(str(y) for y in years), "observed",
            "Department of Mineral and Petroleum Resources, energy balances", "assumptions/2026/timeseries/energy_balance_department.csv", "",
            "The only output by product. Ends at 2021, the last balance published.")
    add("National output by product", "Petrol and diesel produced after 2021", "South Africa", "", "billion litres", "2022 onward", "not available",
        "None published", "", "", "The department has published no balance after 2021.")

    # --- yields -----------------------------------------------------------------
    def share(product, year):
        total = sum(d["production"].get((p, year), 0.0) for p in ("petrol", "diesel", "jet", "paraffin"))
        return d["production"][(product, year)] / total * 100

    for product in ("petrol", "diesel"):
        add("Yields", f"{product.capitalize()} share of the four main fuels produced", "South Africa, all plants",
            "; ".join(f"{share(product, y):.1f}" for y in years), "% of petrol, diesel, jet and paraffin", "; ".join(str(y) for y in years), "inferred",
            "Calculated from the energy balances", "assumptions/2026/timeseries/energy_balance_department.csv", "",
            "A national mix, not a plant yield. It will have shifted since the Durban refineries closed.")
    for p in points.get("natref_yield", []):
        from_point("Yields", "Natref white product yield", p)
    add("Yields", "Yield by plant after 2021", "Secunda, Natref, Astron Energy", "", "%", "", "not available", "None published", "", "",
        "Needed to turn plant output into petrol and diesel. Needs the operators.")

    # --- utilisation --------------------------------------------------------------
    use = utilisation(d)
    for plant in ("Secunda", "Natref"):
        ys = sorted(y for (pl, y) in use if pl == plant)
        add("Utilisation", "Output as a share of published capacity", plant, "; ".join(f"{use[(plant, y)] * 100:.0f}" for y in ys), "%",
            "years to June " + "; ".join(str(y) for y in ys), "inferred",
            "Reported output over published capacity" + (", Sasol's share scaled to the whole refinery" if plant == "Natref" else ""),
            "assumptions/2026/reference/refinery_output_operators.csv", "",
            "Capacity is crude equivalent and output is refined product, so this understates how hard the plant runs."
            + (" The year to June 2026 is left out because Sasol's figure includes output above its share." if plant == "Natref" else ""))
    add("Utilisation", "Output as a share of capacity", "Astron Energy", "", "%", "", "not available", "Not calculable",
        "", "", "Glencore reports energy content, not barrels. Converting it needs an assumed energy content per barrel.")

    # --- outlook --------------------------------------------------------------------
    for p in points["outlook"]:
        from_point("Outlook", "Outlook", p)
    order = {part: i for i, part in enumerate(PARTS)}
    assert {r["part"] for r in rows} <= set(PARTS)
    return sorted(rows, key=lambda r: order[r["part"]])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    args = parser.parse_args()
    rows = build(load(Paths.default().vintage_dir(args.vintage)))
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(f"wrote {len(rows)} rows -> {OUT}; {counts}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
