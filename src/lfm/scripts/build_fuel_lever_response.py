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
# Published tonne-kilometres, billions. Road, 2013: Havenga et al. (2016), "A Logistics Barometer for South
# Africa", J. Transport and Supply Chain Management. Rail-friendly general freight and what rail carried of
# it, 2019: Department of Transport, Roadmap for the Freight Logistics System (draft 7, 2023), p.38.
ROAD_TKM_2013 = 221.0
# Electric share of new sales in 2025, per cent. Trucks and light commercial vehicles: International Energy
# Agency, Global EV Outlook 2026, "Trends in other EV modes". Brazil trucks: ICCT, as reported by REGlobal.
ELECTRIC_TRUCK_SHARE_2025 = {"Brazil": 0.4, "Europe": 3.0, "World": 9.0, "China": 25.0}
ELECTRIC_LCV_SHARE_2025 = {"India": 1.0, "Europe": 10.0, "China": 14.0}
TRUCK_TURNOVER = 0.06          # share of the truck fleet replaced each year; observed 6.2-8.5% for 2022-2025
NEIGHBOURS = ("Botswana", "Lesotho", "Eswatini", "Namibia", "Zimbabwe", "Mozambique", "Zambia", "Malawi",
              "Democratic Republic Of Congo")
RAIL_FRIENDLY_GENERAL_TKM, RAIL_GENERAL_TKM = 47.0, 18.0
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

    jodi = defaultdict(lambda: defaultdict(float))
    with (ts.parents[2] / "external/data/raw/jodi/jodi-secondary-zaf-2023-2025.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["FLOW_BREAKDOWN"] == "REFGROUT" and r["UNIT_MEASURE"] == "KL" and r["OBS_VALUE"] not in ("x", "-"):
                jodi[int(r["TIME_PERIOD"][:4])][r["ENERGY_PRODUCT"]] += float(r["OBS_VALUE"])
    b["jodi"] = {y: {"petrol": v["GASOLINE"] / v["TOTPRODS"] * 100, "diesel": v["GASDIES"] / v["TOTPRODS"] * 100}
                 for y, v in jodi.items() if v.get("TOTPRODS")}

    stone = {r["vehicle_type"]: r for r in _read(ref / "vehicle_parameters_stone2018.csv")}
    b["stone_km"] = float(stone["CarGasoline"]["km_per_year_fleet_average"])
    b["stone_l100"] = float(stone["CarGasoline"]["l_per_100km_fleet_average"])
    b["petrol_vehicles"] = next(float(r["vehicles"]) for r in _read(ref / "vehicle_population_by_fuel_dot2023.csv")
                                if r["fuel_type"] == "petrol")
    b["petrol_sales_2023"] = next(float(r["value"]) for r in _read(ts / "fuel_sales_department.csv")
                                  if r["period"] == "2023" and r["product"] == "petrol")

    # Inputs for the levers added by the analyst.
    cpi, journeys = {}, defaultdict(list)
    for r in _read(ts / "activity_statssa_monthly.csv"):
        if r["series"] == "consumer_price_index_headline":
            cpi[r["period"]] = float(r["value"])
        elif r["series"] == "passenger_journeys_rail":
            journeys[int(r["period"][:4])].append(float(r["value"]) / 1000)
    b["rail_journeys"] = {y: sum(v) for y, v in journeys.items() if len(v) == 12}      # millions a year
    latest_cpi = cpi[max(cpi)]
    real = {"petrol_95_inland_retail": defaultdict(list), "diesel_005_inland_wholesale": defaultdict(list)}
    for r in _read(ts / "fuel_prices_department.csv"):
        if r["series"] in real and r["value"]:
            deflated = float(r["value"]) / cpi.get(r["period"], latest_cpi)
            real[r["series"]][r["period"][:4]].append(deflated)
            real[r["series"]][r["period"]] = [deflated]
    b["real_price"] = {}
    for key, series in (("petrol", "petrol_95_inland_retail"), ("diesel", "diesel_005_inland_wholesale")):
        base = sum(real[series]["2024"]) / len(real[series]["2024"])
        annual = {int(k): sum(v) / len(v) / base * 100 for k, v in real[series].items() if len(k) == 4 and int(k) <= 2025}
        b["real_price"][key] = {"annual": annual, "oct_2026": real[series]["2026-10"][0] / base * 100}
    exports = defaultdict(float)
    for r in _read(ts / "fuel_trade_sars_by_partner.csv"):
        if (r["flow"] == "export" and r["product"] in ("petrol", "diesel") and r["unit"] == "litres"
                and int(r["months_reported"]) and r["partner"] in NEIGHBOURS and int(r["period"]) <= 2025):
            exports[(int(r["period"]), "all")] += float(r["value"]) / 1e9
            if r["partner"] == "Botswana":
                exports[(int(r["period"]), "Botswana")] += float(r["value"]) / 1e9
    b["neighbours"] = dict(exports)
    market = {int(r["period"]): float(r["value"]) for r in _read(ts / "new_vehicle_market_naamsa.csv")
              if r["segment"] == "total" and r["basis"] != "projection"}
    b["hybrid_share"] = {kind: {y: nev[(y, kind)] / market[y] * 100 for y in range(2022, 2026)}
                         for kind in ("traditional_hybrid", "plug_in_hybrid")}

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
    plant = {
        "baseline": f"{util['all']:.0f}", "basis": "reported 2024 output over reported capacity, three plants; indicative",
        "evidence": (f"Secunda {util['Secunda']:.0f}%, Natref {util['Natref']:.0f}%, Astron {util['Astron']:.0f}%. "
                     "Output is all refined products against crude-equivalent capacity; Sasol's year ends June; "
                     "Astron converted at an assumed 36 MJ a litre. The model's Secunda capacity was 75 thousand "
                     "barrels a day and is now FIASA's 150, with utilisation re-based so output is unchanged; "
                     "the model then gives 62 thousand barrels a day for 2024 against 80 reported."), "changes": {}}
    none = {"baseline": "0", "basis": "no committed addition", "changes": {},
            "evidence": "Existing conditional illustration; no investment decision, timing or product slate is sourced."}
    return {
        ("diesel", "road_activity"): {
            "baseline": "100", "basis": f"road freight payload {road[2024]:.0f} Mt in 2024 (Stats SA P7162)",
            "evidence": (f"2014-2024 growth {_growth(road[2014], road[2024], 10):.1f}% a year; fastest eleven years "
                         f"(2012-2023) {_growth(road[2012], road[2023], 11):.1f}%; 2025 is "
                         f"{road[2025] / road[2024] * 100:.1f}. The 2035 high of 175 needs 5.2% a year for eleven years, "
                         "without precedent; 150 matches the fastest observed. In tonne-kilometres the only "
                         f"published road figure found is {ROAD_TKM_2013:.0f} bn for 2013 (Havenga et al. 2016, Logistics "
                         f"Barometer), an average haul of about {ROAD_TKM_2013 * 1000 / road[2013]:.0f} km against Stats SA's "
                         "tonnes. No annual tonne-kilometre series exists, so the index stays on tonnes. Part of "
                         "past growth was freight leaving rail, so this overlaps the rail lever."),
            "changes": {("2035", "high"): 150}},
        ("diesel", "rail_diversion"): {
            "baseline": "0", "basis": f"rail {rail[2024]:.0f} Mt and road {road[2024]:.0f} Mt in 2024 (Stats SA P7162)",
            "evidence": (f"In tonnes, as a share of 2024 road tonnes: rail back to its 2020 level ({rail[2020]:.0f} Mt) is "
                         f"{share(rail[2020]):.0f}%; back to its 2017 peak ({rail[2017]:.0f} Mt) is {share(rail[2017]):.0f}%; "
                         f"the 250 Mt target for 2029/30 (Draft National Rail Master Plan, April 2026) is {share(250):.0f}%; "
                         f"the market appetite of about 280 Mt reported with that plan is {share(280):.0f}%. In "
                         f"tonne-kilometres: rail-friendly general freight was {RAIL_FRIENDLY_GENERAL_TKM:.0f} bn in 2019 and "
                         f"rail carried {RAIL_GENERAL_TKM:.0f} bn (Freight Logistics Roadmap, 2023, p.38); the "
                         f"{RAIL_FRIENDLY_GENERAL_TKM - RAIL_GENERAL_TKM:.0f} bn left on road is "
                         f"{(RAIL_FRIENDLY_GENERAL_TKM - RAIL_GENERAL_TKM) / ROAD_TKM_2013 * 100:.0f}% of road tonne-kilometres "
                         "(2013 base). Both routes put the ceiling at 12-13%, so the 2035 high is 13 and the "
                         "proposed 20 and 35 exceed all rail-friendly freight. The 2030 medium of 10 is the full "
                         "official target, not a middle case."),
            "changes": {("2030", "medium"): 3, ("2030", "high"): 9, ("2035", "medium"): 7, ("2035", "high"): 13}},
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
            "baseline": f"{b['jodi'][2024]['diesel']:.0f}", "basis": "diesel share of refinery output in 2024 (JODI; lowest reliability)",
            "evidence": (f"Share of all refinery output: {b['jodi'][2023]['diesel']:.0f}% in 2023 and "
                         f"{b['jodi'][2024]['diesel']:.0f}% in 2024 (JODI). Before the Durban refineries closed, diesel was "
                         f"{min(slate[y]['diesel'] for y in slate):.0f} to {max(slate[y]['diesel'] for y in slate):.0f}% of the "
                         "five fuels in the 2017-2021 energy balances, which overstates its share of all output. "
                         "The registered legacy yield is 25%. Replacement: legacy as the low, the recent observed "
                         "share as the medium, the pre-closure share as the high. No plant-level slate is published."),
            "changes": {(y, c): v for y in YEARS for c, v in (("low", 25), ("medium", 30), ("high", 40))}},
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
                         "No South African forecast was found; each case is tied to a market's observed 2025 share "
                         "of new car sales (IEA, Global EV Outlook 2026). Low: South Africa stays under 1%, as in "
                         "2022-2025. Medium: India's share (nearly 4%) by 2030 and Indonesia's (15%) by 2035. High: "
                         "Turkiye's path, from just over 1% in 2022 to over 20% in 2025, by 2030, and Vietnam's "
                         "share (nearly 40%) by 2035. The IEA shares include plug-in hybrids, so they overstate "
                         "battery electric alone. The proposed 2035 high of 60 is above every market cited."),
            "changes": {("2030", "low"): 0.5, ("2030", "medium"): 4, ("2030", "high"): 20,
                        ("2035", "low"): 2, ("2035", "medium"): 15, ("2035", "high"): 40}},
        ("petrol", "new_cohort_efficiency"): {
            "baseline": "1.0 to 1.5", "basis": "registered petrol efficiency paths (low and high demand cases)",
            "evidence": "Low and high equal the registered endpoints. Neither has a source. No change proposed.",
            "changes": {}},
        ("petrol", "plant_utilisation"): plant,
        ("petrol", "product_yield"): {
            "baseline": f"{b['jodi'][2024]['petrol']:.0f}", "basis": "petrol share of refinery output in 2024 (JODI; lowest reliability)",
            "evidence": (f"Share of all refinery output: {b['jodi'][2023]['petrol']:.0f}% in 2023 and "
                         f"{b['jodi'][2024]['petrol']:.0f}% in 2024 (JODI). Petrol was "
                         f"{min(slate[y]['petrol'] for y in slate):.0f} to {max(slate[y]['petrol'] for y in slate):.0f}% of the five "
                         "fuels in the 2017-2021 energy balances. The registered legacy yield is 45%. Replacement: "
                         "legacy as the low, 50 as the medium, the recent observed share as the high. Petrol and "
                         "diesel yields must be chosen together; their highs cannot both hold."),
            "changes": {(y, c): v for y in YEARS for c, v in (("low", 45), ("medium", 50), ("high", 55))}},
        ("petrol", "restart_capacity"): none,
    }


def _fleet_share(start: float, at_2030: float, at_2035: float) -> float:
    """Rough share of the truck fleet that is electric in 2035 if the sales share rises in straight lines."""
    yearly = [start + (at_2030 - start) * n / 5 for n in range(1, 6)] + [at_2030 + (at_2035 - at_2030) * n / 5 for n in range(1, 6)]
    return sum(share * TRUCK_TURNOVER for share in yearly)


def additional(b: dict) -> list[dict]:
    """Levers the analyst adds to the tables; not in Nigel's proposed file. Values are ``{case: (2030, 2035)}``."""
    price, journeys, exports = b["real_price"], b["rail_journeys"], b["neighbours"]
    hybrid = b["hybrid_share"]["traditional_hybrid"]
    plug_in = b["hybrid_share"]["plug_in_hybrid"]
    hybrid_step = (hybrid[2025] - hybrid[2022]) / 3
    plug_in_step, plug_in_last = (plug_in[2025] - plug_in[2022]) / 3, plug_in[2025] - plug_in[2024]

    def price_lever(fuel, elasticity):
        annual, october = price[fuel]["annual"], price[fuel]["oct_2026"]
        low, high = round(min(annual.values()), -1), round(october, -1)
        return {"fuel": fuel, "lever": "real_fuel_price", "unit": "index_2024_100", "baseline": "100",
                "basis": "regulated inland price deflated by headline CPI, 2024 average",
                "evidence": (f"Annual range 2011-2025 is {min(annual.values()):.0f} to {max(annual.values()):.0f}; October "
                             f"2026 is {october:.0f}. Low is the bottom of that range, medium a return to 2024, high "
                             f"October 2026 held. Boshoff (2012) puts the long-run response at {elasticity}, so the "
                             f"high case lowers demand by about {abs(elasticity) * (high - 100):.0f}%. One study; the "
                             "model has no price response today."),
                "values": {"low": (low, low), "medium": (100, 100), "high": (high, high)}}

    return [
        price_lever("diesel", -0.13),
        {"fuel": "diesel", "lever": "private_backup_generation", "unit": "bn_litres_per_year", "baseline": "not measured",
         "basis": "no measured volume exists",
         "evidence": ("Recorded diesel sales fell by 1.2 bn litres between 2023 and 2024 as load-shedding ended; grid "
                      "turbines account for about 0.7 of that at 0.31 litres per kWh, leaving about 0.5 that may be "
                      "private generators. Indicative only: other causes are not excluded. High is load-shedding "
                      "returning at 2023 intensity. Move together with diesel power generation."),
         "values": {"low": (0, 0), "medium": (0, 0), "high": (0.5, 0.5)}},
        {"fuel": "diesel", "lever": "electric_share_of_new_truck_sales", "unit": "percent", "baseline": "not reported",
         "basis": "naamsa reports electrified sales for the whole market only; assumed close to zero",
         "evidence": ("No South African figure exists for electric trucks sold or on the road. Benchmarks, share of "
                      f"new truck sales in 2025: Brazil {ELECTRIC_TRUCK_SHARE_2025['Brazil']}% (ICCT); India about 800 trucks, "
                      f"well under 1%; Europe {ELECTRIC_TRUCK_SHARE_2025['Europe']:g}%; world {ELECTRIC_TRUCK_SHARE_2025['World']:g}%; "
                      f"China {ELECTRIC_TRUCK_SHARE_2025['China']:g}%, which is over 90% of all electric trucks sold (IEA, "
                      "Global EV Outlook 2026). Brazil and India are the closest comparators: long hauls, little "
                      "purchase support. Low stays at zero; medium reaches Brazil's 2025 share by 2030 and "
                      "Europe's by 2035; high reaches Europe's by 2030 and the world average by 2035. China is "
                      "not used. The effect on diesel is small within the horizon: about 6% of trucks are "
                      f"replaced a year, so the high case puts roughly {_fleet_share(0, 3, 9):.1f}% of the fleet on "
                      "electricity by 2035."),
         "values": {"low": (0, 0), "medium": (ELECTRIC_TRUCK_SHARE_2025["Brazil"], ELECTRIC_TRUCK_SHARE_2025["Europe"]),
                    "high": (ELECTRIC_TRUCK_SHARE_2025["Europe"], ELECTRIC_TRUCK_SHARE_2025["World"])}},
        {"fuel": "diesel", "lever": "electric_share_of_new_light_commercial_sales", "unit": "percent",
         "baseline": "not reported", "basis": "naamsa reports electrified sales for the whole market only; assumed close to zero",
         "evidence": ("No South African figure by segment. Benchmarks, share of new light commercial sales in 2025: "
                      f"India {ELECTRIC_LCV_SHARE_2025['India']:g}%, Europe {ELECTRIC_LCV_SHARE_2025['Europe']:g}%, China "
                      f"{ELECTRIC_LCV_SHARE_2025['China']:g}% (IEA, Global EV Outlook 2026). Low stays at zero; medium reaches "
                      "India's 2025 share by 2030 and half of Europe's by 2035; high reaches half of Europe's by "
                      "2030 and Europe's by 2035. Light commercial vehicles are mostly bakkies here, which differ "
                      "from the vans that dominate electric sales elsewhere, so these are loose comparators."),
         "values": {"low": (0, 0), "medium": (ELECTRIC_LCV_SHARE_2025["India"], ELECTRIC_LCV_SHARE_2025["Europe"] / 2),
                    "high": (ELECTRIC_LCV_SHARE_2025["Europe"] / 2, ELECTRIC_LCV_SHARE_2025["Europe"])}},
        price_lever("petrol", -0.5),
        {"fuel": "petrol", "lever": "plug_in_hybrid_new_sales_share", "unit": "percent", "baseline": f"{plug_in[2025]:.1f}",
         "basis": "share of all new vehicles in 2025 (naamsa)",
         "evidence": (f"Share rose from {plug_in[2022]:.2f}% in 2022 to {plug_in[2025]:.2f}% in 2025. Low holds 2025; "
                      f"medium adds the 2022-2025 average of {plug_in_step:.2f} points a year; high adds the 2025 "
                      f"increase of {plug_in_last:.2f} points a year. An extrapolation of South Africa's own sales, "
                      "not a forecast. Enters through fuel use per kilometre; the share of distance on the "
                      "battery is unsourced."),
         "values": {c: tuple(round(plug_in[2025] + step * n, 1) for n in (5, 10))
                    for c, step in (("low", 0), ("medium", plug_in_step), ("high", plug_in_last))}},
        {"fuel": "petrol", "lever": "conventional_hybrid_new_sales_share", "unit": "percent",
         "baseline": f"{hybrid[2025]:.1f}", "basis": "share of all new vehicles in 2025 (naamsa)",
         "evidence": (f"Share rose from {hybrid[2022]:.2f}% in 2022 to {hybrid[2024]:.2f}% in 2024 and was "
                      f"{hybrid[2025]:.2f}% in 2025. Low holds 2025; medium adds the 2022-2025 average of "
                      f"{hybrid_step:.2f} points a year; high adds twice that. An extrapolation of South Africa's "
                      "own sales, not a forecast. Enters through fuel use per kilometre; the saving per vehicle "
                      "is unsourced."),
         "values": {c: tuple(round(hybrid[2025] + step * n, 1) for n in (5, 10))
                    for c, step in (("low", 0), ("medium", hybrid_step), ("high", 2 * hybrid_step))}},
        {"fuel": "petrol", "lever": "rail_passenger_journeys", "unit": "million_per_year",
         "baseline": f"{journeys[2024]:.0f}", "basis": "rail passenger journeys in 2024 (Stats SA P7162)",
         "evidence": (f"Journeys were {journeys[2017]:.0f} million in 2017 and {journeys[2019]:.0f} in 2019, fell to "
                      f"{journeys[2022]:.0f} in 2022 and recovered to {journeys[2025]:.0f} in 2025. Low holds 2025; "
                      "medium returns to 2019 by 2030 and to 2018 by 2035; high returns to 2017 by 2030 and "
                      "holds. More rail journeys lower petrol use, but no survey covers the minibus taxi and "
                      "car trips displaced, so the effect in litres cannot yet be stated."),
         "values": {"low": (round(journeys[2025], -1),) * 2,
                    "medium": (round(journeys[2019], -1), round(journeys[2018], -1)),
                    "high": (round(journeys[2017], -1),) * 2}},
        {"fuel": "throughput", "lever": "exports_to_neighbours", "unit": "bn_litres_per_year",
         "baseline": f"{exports[(2024, 'all')]:.2f}",
         "basis": "petrol and diesel exported to nine neighbouring countries in 2024 (SARS customs)",
         "evidence": (f"{exports[(2019, 'all')]:.2f} bn litres in 2019, {exports[(2023, 'all')]:.2f} in 2023 and "
                      f"{exports[(2025, 'all')]:.2f} in 2025. Botswana took {exports[(2023, 'Botswana')]:.2f} in 2023 and "
                      f"{exports[(2025, 'Botswana')]:.2f} in 2025 and has said it is moving to Walvis Bay and Maputo. Low "
                      "is 2025 with Botswana gone; medium holds 2025; high returns to 2023. This is throughput for "
                      "South African terminals, not South African demand, and must not be added to it."),
         "values": {"low": (round(exports[(2025, "all")] - exports[(2025, "Botswana")], 1),) * 2,
                    "medium": (round(exports[(2025, "all")], 1),) * 2,
                    "high": (round(exports[(2023, "all")], 1),) * 2}},
    ]


def build(proposed: list[dict], notes: dict, extra: list[dict] | None = None) -> list[dict]:
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
    for lever in extra or []:
        for index, year in enumerate(YEARS):
            for case in CASES:
                rows.append({
                    "fuel": lever["fuel"], "lever": lever["lever"], "unit": lever["unit"], "baseline": lever["baseline"],
                    "baseline_basis": lever["basis"], "period": year, "case": case, "proposed_by_nigel": "",
                    "analyst_value": f"{lever['values'][case][index]:g}", "changed": "added",
                    "evidence": lever["evidence"]})
    return rows


def markdown(rows: list[dict]) -> str:
    def cell(lever_rows, year):
        parts = []
        for case in CASES:
            r = next(x for x in lever_rows if x["period"] == year and x["case"] == case)
            parts.append(f'{r["proposed_by_nigel"]} → **{r["analyst_value"]}**' if r["changed"] == "yes"
                         else f'**{r["analyst_value"]}**' if r["changed"] == "added" else r["proposed_by_nigel"])
        return " / ".join(parts)

    changed = sum(r["changed"] == "yes" for r in rows)
    added = len({(r["fuel"], r["lever"]) for r in rows if r["changed"] == "added"})
    out = ["# Diesel, jet and petrol input tables: analyst response, 7 October 2026", "",
           "Priority 2 on Manish's focus page (Convergence pack p24). Built by",
           "`python -m lfm.scripts.build_fuel_lever_response --vintage 2026`; the same content, one row per",
           f"value, is in `{STEM}.csv`. Nigel's proposed inputs",
           "(`assumptions/2026/timeseries/fuel_lever_design_2026_10_07.csv`) are not edited.", "",
           f"Of 120 proposed values, {changed} have a replacement proposed here and {120 - changed} are left as they",
           "are. Replacements are shown as proposed → **replacement**. Each baseline is computed from a",
           "registered input and is an observation unless its basis says otherwise. Cases order the input",
           "(low / medium / high), not the resulting demand. Nothing here is an accepted input.", "",
           f"{added} levers are added by the analyst and are not in Nigel's file: real fuel price (diesel and",
           "petrol), private backup generation, electric share of new truck and light commercial sales, plug-in",
           "and conventional hybrids, rail passengers, and exports to neighbours. Their values are shown in bold",
           "with no earlier value.", ""]
    for fuel in ("diesel", "jet", "petrol", "throughput"):
        heading = "Throughput for terminals (not South African demand)" if fuel == "throughput" else fuel.capitalize()
        out += [f"## {heading}", "",
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
    observed = baselines(vintage / "timeseries", vintage / "reference")
    rows = build(proposed, review(observed), additional(observed))
    with (OUT_DIR / f"{STEM}.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (OUT_DIR / f"{STEM}.md").write_text(markdown(rows), encoding="utf-8", newline="\n")
    print(f"wrote {len(rows)} values; {sum(r['changed'] == 'yes' for r in rows)} with a replacement; "
          f"{sum(r['changed'] == 'added' for r in rows)} added", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
