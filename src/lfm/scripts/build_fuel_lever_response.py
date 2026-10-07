"""Analyst response to the proposed diesel, jet and petrol lever inputs for 2030 and 2035.

Reads the proposed low / medium / high values (owned by Nigel) and sets beside
each lever an observed starting value computed from the registered inputs, the
evidence, and a replacement value where the evidence points to one. Writes:

    workstreams/WS2_model_development/fuel_lever_response_2026-10-07.csv
    workstreams/WS2_model_development/fuel_lever_response_2026-10-07.md

The proposed-inputs file is not edited. Replacement values are the analyst's
proposals for review; nothing here is an accepted input.

Run:
    python -m lfm.scripts.build_fuel_lever_response --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

from lfm.config import Paths

OUT_DIR = Path("workstreams/WS2_model_development")
STEM = "fuel_lever_response_2026-10-07"
PROPOSED = "fuel_lever_design_2026_10_07.csv"
CASES = ("low", "medium", "high")
YEARS = ("2030", "2035")
LITRES_PER_BARREL = 158.987
MJ_PER_BTU, MJ_PER_LITRE_ASSUMED = 0.00105506, 36.0
FIELDS = ["fuel", "lever", "unit", "baseline", "baseline_basis", "period", "case", "proposed_by_nigel",
          "analyst_value", "changed", "evidence"]


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _growth(first: float, last: float, years: int) -> float:
    return ((last / first) ** (1 / years) - 1) * 100


def baselines(ts: Path, ref: Path) -> dict:
    """Observed starting values, each computed from a registered input."""
    b: dict = {}

    payload = defaultdict(lambda: [0.0, 0])
    for r in _read(ts / "activity_statssa_monthly.csv"):
        if r["series"] in ("freight_payload_road", "freight_payload_rail"):
            cell = payload[(r["series"][16:], int(r["period"][:4]))]
            cell[0] += float(r["value"]) / 1000
            cell[1] += 1
    tonnes = {k: v[0] for k, v in payload.items() if v[1] == 12}        # million tonnes, complete years
    b["road"], b["rail"] = ({y: t for (mode, y), t in tonnes.items() if mode == m} for m in ("road", "rail"))

    b["ocgt"] = {int(r["period"]): float(r["value"]) for r in _read(ts / "ocgt_generation_eskom.csv")
                 if r["series"] == "eskom_and_ipp_ocgt"}

    b["movements"] = {int(r["period"]): float(r["value"]) for r in _read(ts / "air_traffic_acsa_annual.csv")
                      if (r["measure"], r["flight_type"], r["direction"]) == ("aircraft_movements", "total", "total")}
    jet = {int(r["period"]): float(r["value"]) for r in _read(ts / "historical_demand.csv") if r["product"] == "jet_a1"}
    b["burn"] = {y: jet[y] / b["movements"][y] for y in jet if y in b["movements"]}

    b["gdp"] = {int(r["period"]): float(r["value"]) for r in _read(ts / "macro_statssa.csv")
                if r["code"] == "AR1000" and r["basis"] == "actual"}
    b["treasury"] = {int(r["period"]): float(r["value"]) for r in _read(ts / "gdp_growth_treasury.csv")}

    nev = {(int(r["period"]), r["drivetrain"]): float(r["value"]) for r in _read(ts / "nev_sales_naamsa.csv")}
    b["bev"] = {y: nev[(y, "battery_electric")] for (y, kind) in nev if kind == "battery_electric"}
    b["nev_total_2025"] = nev[(2025, "total")]

    production = defaultdict(dict)
    for r in _read(ts / "energy_balance_department.csv"):
        if r["flow_key"] == "production":
            production[int(r["period"])][r["product"]] = float(r["value"])
    b["slate"] = {y: {p: v / sum(production[y].values()) * 100 for p, v in production[y].items()}
                  for y in (2017, 2018, 2019, 2021)}

    stone = {r["vehicle_type"]: r for r in _read(ref / "vehicle_parameters_stone2018.csv")}
    b["stone_km"] = float(stone["CarGasoline"]["km_per_year_fleet_average"])
    b["stone_l100"] = float(stone["CarGasoline"]["l_per_100km_fleet_average"])
    b["petrol_vehicles"] = next(float(r["vehicles"]) for r in _read(ref / "vehicle_population_by_fuel_dot2023.csv")
                                if r["fuel_type"] == "petrol")
    b["petrol_sales_2023"] = next(float(r["value"]) for r in _read(ts / "fuel_sales_department.csv")
                                  if r["period"] == "2023" and r["product"] == "petrol")

    capacity = {r["asset"]: float(r["value"]) / 1000 for r in _read(ts / "refinery_capacity_reported.csv")
                if r["period"] == "2024"}
    out = {(r["plant"], r["period"]): r for r in _read(ref / "refinery_output_operators.csv")}
    kbpd = {
        "Secunda": float(out[("Secunda", "2024")]["value"]) * 1000 / 365,
        "Natref": float(out[("Natref", "2024")]["value"]) / 0.6364 * 1000 / 365,
        "Astron": float(out[("Astron Energy (Cape Town)", "2024")]["value"]) * 1e9 * MJ_PER_BTU
                  / MJ_PER_LITRE_ASSUMED / LITRES_PER_BARREL / 365 / 1000,
    }
    cap = {"Secunda": capacity["Sasol"], "Natref": capacity["Natref"], "Astron": capacity["Astron Energy"]}
    b["utilisation"] = {plant: kbpd[plant] / cap[plant] * 100 for plant in kbpd}
    b["utilisation"]["all"] = sum(kbpd.values()) / sum(cap.values()) * 100
    return b


def review(b: dict) -> dict[tuple[str, str], dict]:
    """Per lever: baseline, basis, evidence and any replacement values ``{(year, case): value}``."""
    road, rail, mov, burn, gdp = b["road"], b["rail"], b["movements"], b["burn"], b["gdp"]

    def share(million_tonnes: float) -> float:
        """Rail tonnes gained, as a percentage of 2024 road tonnes."""
        return (million_tonnes - rail[2024]) / road[2024] * 100

    pre = [burn[y] for y in range(2013, 2020)]
    pre_index = sum(pre) / len(pre) / burn[2024] * 100
    implied_km = b["petrol_sales_2023"] / b["petrol_vehicles"] / b["stone_l100"] * 100
    bev_share = b["bev"][2025] / (b["nev_total_2025"] / 0.028) * 100
    util = b["utilisation"]
    slate = b["slate"]
    ratio = [slate[y]["diesel"] / slate[y]["petrol"] for y in (2017, 2018, 2019, 2021)]
    plant = {
        "baseline": f"{util['all']:.0f}", "basis": "reported 2024 output over reported capacity, three plants; indicative",
        "evidence": (f"Secunda {util['Secunda']:.0f}%, Natref {util['Natref']:.0f}%, Astron {util['Astron']:.0f}%. "
                     "Output is all refined products against crude-equivalent capacity; Sasol's year ends June; "
                     "Astron converted at an assumed 36 MJ a litre. The model's registered Secunda nameplate is "
                     "75 thousand barrels a day; FIASA reports 150."), "changes": {}}
    none = {"baseline": "0", "basis": "no committed addition", "changes": {},
            "evidence": "Existing conditional illustration; no investment decision, timing or product slate is sourced."}
    return {
        ("diesel", "road_activity"): {
            "baseline": "100", "basis": f"road freight payload {road[2024]:.0f} Mt in 2024 (Stats SA P7162)",
            "evidence": (f"Tonnes, not tonne-kilometres. 2014-2024 growth {_growth(road[2014], road[2024], 10):.1f}% a year; "
                         f"fastest eleven years (2012-2023) {_growth(road[2012], road[2023], 11):.1f}%; 2025 is "
                         f"{road[2025] / road[2024] * 100:.1f}. The 2035 high of 175 needs 5.2% a year for eleven years, "
                         "without precedent; 150 matches the fastest observed. Part of past growth was freight leaving "
                         "rail, so this overlaps the rail lever."),
            "changes": {("2035", "high"): 150}},
        ("diesel", "rail_diversion"): {
            "baseline": "0", "basis": f"rail {rail[2024]:.0f} Mt and road {road[2024]:.0f} Mt in 2024 (Stats SA P7162)",
            "evidence": (f"As a share of 2024 road tonnes: rail back to its 2020 level ({rail[2020]:.0f} Mt) is "
                         f"{share(rail[2020]):.0f}%; back to its 2017 peak ({rail[2017]:.0f} Mt) is {share(rail[2017]):.0f}%; "
                         f"Transnet's 250 Mt target for 2029/30 met in full is {share(250):.0f}%. The proposed 2030 medium "
                         "of 10% is therefore the full target, and 20% would put rail far above its peak. The 2035 "
                         "high of 15% has no source. Tonnes understate rail's share of tonne-kilometres."),
            "changes": {("2030", "medium"): 3, ("2030", "high"): 9, ("2035", "medium"): 7, ("2035", "high"): 15}},
        ("diesel", "ocgt_generation"): {
            "baseline": "100", "basis": f"Eskom and independent OCGT output {b['ocgt'][2024]:,.0f} GWh, year to March 2024",
            "evidence": (f"Year to March 2025 is {b['ocgt'][2025] / b['ocgt'][2024] * 100:.0f} and year to March 2026 is "
                         f"{b['ocgt'][2026] / b['ocgt'][2024] * 100:.0f} on this index, so the medium of 25 in 2030 holds "
                         "today's level. Reported burn is 0.31 litres per kWh in three years. No change proposed."),
            "changes": {}},
        ("diesel", "new_cohort_efficiency"): {
            "baseline": "0.5 to 1.0", "basis": "registered diesel efficiency paths (low and high demand cases)",
            "evidence": "Low and high equal the registered endpoints. Neither has a source. No change proposed.",
            "changes": {}},
        ("diesel", "plant_utilisation"): plant,
        ("diesel", "product_yield"): {
            "baseline": "25", "basis": "registered legacy yield; share of throughput, not observed",
            "evidence": (f"Energy balances report {min(ratio):.2f} to {max(ratio):.2f} litres of diesel per litre of petrol "
                         "(2017-2021); the legacy yields imply 0.56. JODI gives 0.61 and 0.53 for 2023 and 2024 at its "
                         "lowest reliability. The evidence does not settle a value; set diesel and petrol yields "
                         "together, by plant. No change proposed."),
            "changes": {}},
        ("diesel", "restart_capacity"): none,
        ("jet", "aircraft_movements"): {
            "baseline": "100", "basis": f"{mov[2024]:,.0f} movements at ACSA airports in 2024",
            "evidence": (f"2019 was {mov[2019] / mov[2024] * 100:.0f} and the peak, 2016, was {mov[2016] / mov[2024] * 100:.0f} "
                         f"on this index; 2025 is {mov[2025] / mov[2024] * 100:.1f}. Movements fell "
                         f"{-_growth(mov[2013], mov[2019], 6):.1f}% a year over 2013-2019. The proposed highs (140 and 190) "
                         "are above every year on record. Replacement: medium returns to the 2019 level by 2030, "
                         "high to the 2016 peak; 2035 extends each."),
            "changes": {("2030", "medium"): 110, ("2030", "high"): 125, ("2035", "medium"): 120, ("2035", "high"): 140}},
        ("jet", "fuel_burn_per_movement"): {
            "baseline": "100", "basis": f"{burn[2024]:,.0f} litres of jet sold per movement in 2024",
            "evidence": (f"The 2013-2019 average was {sum(pre) / len(pre):,.0f} litres, {pre_index:.0f} on this index. "
                         "Jet sales have recovered less than movements since 2020, for reasons not yet established "
                         "(aircraft mix, fuel loaded abroad, or sales coverage). The proposed range only falls; the "
                         "high case should allow a return to the earlier intensity."),
            "changes": {("2030", "high"): round(pre_index), ("2035", "high"): round(pre_index)}},
        ("jet", "saf_volume_share"): {
            "baseline": "0", "basis": "no sustainable aviation fuel supply recorded in the sources held; unsourced",
            "evidence": "No South African blend requirement is sourced. No change proposed.", "changes": {}},
        ("jet", "plant_utilisation"): plant,
        ("jet", "product_yield"): {
            "baseline": "10", "basis": "registered legacy yield for capable plants",
            "evidence": (f"Jet was {min(slate[y]['jet'] for y in slate):.0f} to {max(slate[y]['jet'] for y in slate):.0f}% of "
                         "the five fuels produced in the 2017-2021 energy balances, consistent with the range. "
                         "No change proposed."), "changes": {}},
        ("jet", "restart_capacity"): none,
        ("petrol", "passenger_mileage"): {
            "baseline": "17000", "basis": "registered placeholder; not an observation",
            "evidence": (f"Stone et al. (2018) give {b['stone_km']:,.0f} km a year for the petrol car fleet. 2023 petrol "
                         f"sales over {b['petrol_vehicles'] / 1e6:.2f} million registered petrol vehicles is "
                         f"{b['petrol_sales_2023'] / b['petrol_vehicles']:,.0f} litres each, about {implied_km:,.0f} km at "
                         f"{b['stone_l100']} litres per 100 km. The placeholder sits above both, so it is better "
                         "treated as the high case."),
            "changes": {(y, c): v for y in YEARS for c, v in
                        (("low", round(implied_km, -2)), ("medium", round(b["stone_km"], -2)), ("high", 17000))}},
        ("petrol", "gdp_growth"): {
            "baseline": f"{_growth(gdp[2023], gdp[2024], 1):.1f}", "basis": "real GDP growth in 2024 (Stats SA P0441)",
            "evidence": (f"Average growth was {_growth(gdp[2014], gdp[2024], 10):.1f}% a year over 2014-2024 and "
                         f"{_growth(gdp[2010], gdp[2019], 9):.1f}% over 2010-2019. National Treasury forecasts "
                         f"{b['treasury'][2026]}% for 2026 rising to {b['treasury'][2028]}% in 2028. The model's registered "
                         "cases are 1.0% and 1.6%. A medium of 2% equals the top of the official forecast; 3% has "
                         "no recent precedent."),
            "changes": {(y, c): v for y in YEARS for c, v in
                        (("low", round(_growth(gdp[2014], gdp[2024], 10), 1)),
                         ("medium", round(_growth(gdp[2010], gdp[2019], 9), 1)), ("high", b["treasury"][2028]))}},
        ("petrol", "bev_new_sales_share"): {
            "baseline": f"{bev_share:.1f}",
            "basis": f"{b['bev'][2025]:,.0f} battery electric vehicles sold in 2025, share of all new vehicles (naamsa)",
            "evidence": (f"Battery electric sales fell from {b['bev'][2024]:,.0f} in 2024 to {b['bev'][2025]:,.0f} in 2025. "
                         "The policy target of 20% of sales by 2025 was missed by a wide margin. Electric cars were "
                         "over 6% of sales in Brazil and 9% across Southeast Asia in 2024 (International Energy "
                         "Agency). The proposed low of 5% by 2030 is a 27-fold rise in five years. Replacement: low "
                         "continues near today, medium reaches Brazil's 2024 level by about 2032, high follows "
                         "Southeast Asia. Hybrids are excluded here and enter through fuel use per kilometre."),
            "changes": {("2030", "low"): 0.5, ("2030", "medium"): 3, ("2030", "high"): 10,
                        ("2035", "low"): 2, ("2035", "medium"): 10, ("2035", "high"): 30}},
        ("petrol", "new_cohort_efficiency"): {
            "baseline": "1.0 to 1.5", "basis": "registered petrol efficiency paths (low and high demand cases)",
            "evidence": "Low and high equal the registered endpoints. Neither has a source. No change proposed.",
            "changes": {}},
        ("petrol", "plant_utilisation"): plant,
        ("petrol", "product_yield"): {
            "baseline": "45", "basis": "registered legacy yield; share of throughput, not observed",
            "evidence": (f"Petrol was {min(slate[y]['petrol'] for y in slate):.0f} to "
                         f"{max(slate[y]['petrol'] for y in slate):.0f}% of the five fuels produced in the 2017-2021 "
                         "energy balances; as a share of all throughput it would be lower. Set together with the "
                         "diesel yield, by plant. No change proposed."), "changes": {}},
        ("petrol", "restart_capacity"): none,
    }


def build(proposed: list[dict], notes: dict) -> list[dict]:
    rows = []
    for r in proposed:
        note = notes[(r["fuel"], r["lever"])]
        value = note["changes"].get((r["period"], r["case"]))
        given = float(r["value"])
        rows.append({
            "fuel": r["fuel"], "lever": r["lever"], "unit": r["unit"], "baseline": note["baseline"],
            "baseline_basis": note["basis"], "period": r["period"], "case": r["case"],
            "proposed_by_nigel": r["value"], "analyst_value": r["value"] if value is None else f"{value:g}",
            "changed": "yes" if value is not None and float(value) != given else "no", "evidence": note["evidence"]})
    return rows


def markdown(rows: list[dict]) -> str:
    def cell(lever_rows, year):
        parts = []
        for case in CASES:
            r = next(x for x in lever_rows if x["period"] == year and x["case"] == case)
            parts.append(f'{r["proposed_by_nigel"]} → **{r["analyst_value"]}**' if r["changed"] == "yes"
                         else r["proposed_by_nigel"])
        return " / ".join(parts)

    changed = sum(r["changed"] == "yes" for r in rows)
    out = ["# Diesel, jet and petrol input tables: analyst response, 7 October 2026", "",
           "Priority 2 on Manish's focus page (Convergence pack p24). Built by",
           "`python -m lfm.scripts.build_fuel_lever_response --vintage 2026`; the same content, one row per",
           f"value, is in `{STEM}.csv`. Nigel's proposed inputs",
           "(`assumptions/2026/timeseries/fuel_lever_design_2026_10_07.csv`) are not edited.", "",
           f"Of 120 proposed values, {changed} have a replacement proposed here and {120 - changed} are left as they",
           "are. Replacements are shown as proposed → **replacement**. Each baseline is computed from a",
           "registered input and is an observation unless its basis says otherwise. Cases order the input",
           "(low / medium / high), not the resulting demand. Nothing here is an accepted input.", ""]
    for fuel in ("diesel", "jet", "petrol"):
        out += [f"## {fuel.capitalize()}", "",
                "| Lever | Unit | Baseline | Baseline basis | 2030 low / medium / high | 2035 low / medium / high |",
                "|---|---|---|---|---|---|"]
        levers = list(dict.fromkeys(r["lever"] for r in rows if r["fuel"] == fuel))
        for lever in levers:
            mine = [r for r in rows if (r["fuel"], r["lever"]) == (fuel, lever)]
            out.append(f'| {lever} | {mine[0]["unit"]} | {mine[0]["baseline"]} | {mine[0]["baseline_basis"]} | '
                       f'{cell(mine, "2030")} | {cell(mine, "2035")} |')
        out += ["", "Evidence and rationale:", ""]
        for lever in levers:
            mine = next(r for r in rows if (r["fuel"], r["lever"]) == (fuel, lever))
            out.append(f'- **{lever}.** {mine["evidence"]}')
        out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    args = parser.parse_args()
    vintage = Paths.default().vintage_dir(args.vintage)
    proposed = _read(vintage / "timeseries" / PROPOSED)
    rows = build(proposed, review(baselines(vintage / "timeseries", vintage / "reference")))
    with (OUT_DIR / f"{STEM}.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (OUT_DIR / f"{STEM}.md").write_text(markdown(rows), encoding="utf-8", newline="\n")
    print(f"wrote {len(rows)} values; {sum(r['changed'] == 'yes' for r in rows)} with a replacement", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
