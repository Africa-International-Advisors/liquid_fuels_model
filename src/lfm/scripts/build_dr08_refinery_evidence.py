"""Build the DR08 refinery supply evidence table from the registered inputs.

DR08 asks for each refinery, PetroSA included: capacity, output, yields,
utilisation, feedstock and closure or restart dates. This writes one row per
fact, each with its value, period, status, source and open gap:

    workstreams/WS1_data_validation/dr08_refinery_evidence_2026-10-08.csv

Values are read from ``reference/refinery_evidence_points.csv`` (figures typed
from the department, the operators, the Central Energy Fund and others named row by row), the
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
REFINING_NOW = [
    # plant, refining in 2026, period, source
    ("Secunda", "Yes", "2026", "Sasol business performance metrics, June 2026"),
    ("Natref", "Yes", "2026; planned shutdown and a unit outage, August to September", "Sasol business performance metrics, June 2026; Natref update, 1 September 2026"),
    ("Astron Energy", "Yes", "since the restart in early 2023", "Glencore annual reports 2023 to 2025"),
    ("Sapref", "No", "since the pause at the end of March 2022", "Shell South Africa release, 10 February 2022; Central Energy Fund, September 2026"),
    ("Enref", "No", "since the fire of 4 December 2020", "Engen's account to Parliament, 8 December 2020; department's 2023 report"),
    ("PetroSA", "No", "since December 2020", "PetroSA tender scope of work; department's 2023 report"),
]
PLANTS = ["Secunda", "Natref", "Astron Energy", "Sapref", "Enref", "PetroSA"]
NATREF_SASOL_SHARE = 0.6364
LITRES_PER_BARREL = 158.987
BTU_PER_BARREL_OF_OIL_EQUIVALENT = 5.8e6          # the standard definition of a barrel of oil equivalent
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


def astron_utilisation(d: dict) -> dict[int, float]:
    """Astron's output over capacity by calendar year, with Glencore's energy content turned into barrels of oil equivalent."""
    cap = capacity(d)["Astron Energy"]
    return {year: float(row["value"]) * 1e9 / BTU_PER_BARREL_OF_OIL_EQUIVALENT / (cap * (366 if year % 4 == 0 else 365))
            for (plant, year), row in d["operators"].items() if plant.startswith("Astron") and row["unit"] == "billion Btu"}


def natref_by_product(d: dict) -> dict[tuple[str, int], tuple[float, float]]:
    """Natref's petrol and diesel, billion litres, as a low and high figure for each year to June.

    Sasol's reported share is scaled to the whole refinery and multiplied by the range Sasol states for each
    product's share of production. The year to June 2026 is left out, as in ``utilisation``.
    """
    split = {p["subject"]: tuple(float(x) / 100 for x in p["value"].split("-")) for p in d["points"] if p["series"] == "split_natref"}
    out = {}
    for (plant, year), row in d["operators"].items():
        if plant == "Natref" and year != 2026:
            whole = float(row["value"]) / NATREF_SASOL_SHARE * LITRES_PER_BARREL / 1e3
            for product, (low, high) in split.items():
                out[(product, year)] = (whole * low, whole * high)
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
    for plant, refining, since, source in REFINING_NOW:
        add("Status and dates", "Refining in 2026", plant, refining, "", since, "inferred", source, "", "",
            "Read from the status rows below." + (" Natref is its own crude refinery at Sasolburg, part-owned by Sasol; its output is not part of Secunda's."
                                                    if plant == "Natref" else ""))
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
    by_product = natref_by_product(d)
    natref_years = sorted({y for _, y in by_product})
    for product in ("petrol", "diesel"):
        add("Output by plant", f"{product.capitalize()} output, estimated", "Natref, whole refinery",
            "; ".join("{:.2f} to {:.2f}".format(*by_product[(product, y)]) for y in natref_years), "billion litres",
            "years to June " + "; ".join(str(y) for y in natref_years), "inferred",
            "Sasol's reported Natref production, scaled to the whole refinery, times Sasol's stated product split",
            "assumptions/2026/reference/refinery_output_operators.csv; assumptions/2026/reference/refinery_evidence_points.csv", "",
            "An estimate: the split is a range Sasol stated in April 2021, applied to every year. The year to June 2026 is left out.")
    add("Output by plant", "Petrol and diesel output by plant", "Secunda and Astron Energy", "", "litres", "", "not available", "None published", "", "",
        "Sasol states Secunda's split (65% petrol, 35% diesel) but not the total it applies to. Glencore publishes no split for Astron. "
        "Sasol's annual filing and both companies' sites were checked on 9 October. Needs the operators.")
    for plant, since in (("Sapref", "since the pause at the end of March 2022"), ("Enref", "since the fire of 4 December 2020"),
                         ("PetroSA", "since December 2020")):
        add("Output by plant", "Output while not operating", plant, "0", "barrels a day", since, "inferred", "From the status rows", "", "", "")

    # --- national output by product -------------------------------------------
    years = [y for y in BALANCE_YEARS if ("petrol", y) in d["production"]]
    for product in ("petrol", "diesel"):
        add("National output by product", f"{product.capitalize()} produced, all plants", "South Africa",
            "; ".join(f"{d['production'][(product, y)]:.2f}" for y in years), "billion litres", "; ".join(str(y) for y in years), "observed",
            "Department of Mineral and Petroleum Resources, energy balances", "assumptions/2026/timeseries/energy_balance_department.csv", "",
            "The only output by product. Ends at 2021, the last balance published.")
    for p in points.get("national_output_un", []):
        add("National output by product", f"{p['subject'].capitalize()} produced, United Nations series (not used)", "South Africa", p["value"], p["unit"],
            p["period"], "observed", p["source"], p["original_file"], p["page"], p["note"])
    add("National output by product", "Petrol and diesel produced after 2021, on the department's basis", "South Africa", "", "billion litres",
        "2022 onward", "not available", "None published", "", "",
        "The department has published no balance after 2021. The United Nations series runs to 2023 but does not match the department in the years they share.")

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
    for series, plant in (("split_natref", "Natref"), ("split_secunda", "Secunda")):
        for p in points.get(series, []):
            add("Yields", f"{p['subject'].capitalize()} share of output", plant, p["value"].replace("-", " to "), p["unit"], p["period"], "observed",
                p["source"], p["original_file"], p["page"], p["note"])
    for product in ("petrol", "diesel"):
        add("Yields", f"{product.capitalize()} share of output, assumed", "Astron Energy", "50", "% of petrol and diesel", "assumption", "inferred",
            "Assumption agreed with Nigel on the call of 9 October 2026", "", "",
            "Nothing is published for Astron. An even split, so the model responds sensibly when the plant is switched on or off; not a measured figure.")

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
    astron = astron_utilisation(d)
    add("Utilisation", "Output as a share of published capacity, estimated", "Astron Energy", "; ".join(f"{astron[y] * 100:.0f}" for y in sorted(astron)), "%",
        "; ".join(str(y) for y in sorted(astron)), "inferred", "Glencore's energy content at 5.8 million Btu a barrel of oil equivalent, over published capacity",
        "assumptions/2026/reference/refinery_output_operators.csv", "",
        "An estimate: no throughput in barrels is published. Refined products hold a little less energy per barrel than the standard, so true utilisation is "
        "somewhat higher. 2023 is the restart year.")
    for p in points.get("astron_statement", []):
        from_point("Utilisation", "Utilisation as stated by the operator", p)

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
