"""Petrol and diesel outlook to 2030, national and for the market of interest, Low / Base / High demand cases.

Pure calculations; ``lfm.scripts.build_moi_outlook`` reads the data and the ``moi_outlook`` assumptions and writes the results.

Market of interest (2025E): 2022 Department district sales give each district's share of national sales by product; the shares are
applied to 2025 national demand (production + imports - exports). Six provinces, less the southern Free State districts.

Drivers, by year from 2025:
  Petrol: income (GDP x 0.36) and price. The real petrol price comes from an oil price build (Henry Gilfillan, 14 October 2026):
    oil-linked price (R/L) = (Brent + refining margin x petrol share) x rand per US$ / 158.987 L per barrel; all other items held at
    their 2025 real level (2025 pump price less the 2025 oil-linked price, base-case margin and share). No freight. 2026 is the actual
    real price; 2027 halfway to the case level; case level 2028-2030. The long-run elasticity is phased in at the short-run/long-run
    ratio each year. Road petrol also falls with fleet efficiency and EVs.
  Diesel: non-power uses grow with GDP (no price response); road freight loses the tonnes moved to rail; road diesel falls with
    efficiency; light-vehicle diesel with EVs. Diesel peakers move from their 2025 use to the case load factor by 2030 (Henry
    Gilfillan, 13-14 October 2026): Eskom-owned units run first, at this year's rate / 5% / 10%; IPP units (Dedisa, Avon) at the
    Eskom-owned rate x the FY2025 IPP/Eskom load-factor ratio. National: all peakers. Market of interest: Avon only, so its load
    factor is below the national one. Private generators (Henry Gilfillan, 14 October 2026): the 2023-2024 fall in diesel, less
    the fall in peaker diesel, is generator diesel under stage 6 load shedding; none in 2025; by 2030 the case share of it returns.
"""
from __future__ import annotations

import math

YEARS = list(range(2025, 2031))
CASES = ("Low", "Base", "High")
LITRES_PER_BARREL = 158.987


# ---------------------------------------------------------------- market of interest, 2025E

def market_2025(national: dict, inside: dict, provinces_2022: dict, districts_2022: dict, market: dict) -> dict:
    """Market-of-interest demand in 2025E by product (bn L).

    national: 2025 demand by product; inside: Secunda + Natref output by product; provinces_2022 / districts_2022: 2022 sales by
    province code / (province code, district) -> {"petrol", "diesel"}; market: the ``moi_outlook.market`` assumption.
    """
    products = ("petrol", "diesel")
    n22 = {p: sum(v[p] for v in provinces_2022.values()) for p in products}
    grow = {p: national[p] / n22[p] for p in products}                 # 2022 sales -> 2025 demand, by product
    excluded = set(market["excluded_districts_fs"])
    missing = excluded - {d for (q, d) in districts_2022 if q == "FS"}
    if missing:
        raise ValueError(f"excluded Free State districts not in the district sales: {sorted(missing)}")
    prov = {c: {p: provinces_2022[c][p] * grow[p] for p in products} for c in market["provinces"]}
    cut = {p: sum(districts_2022["FS", d][p] for d in excluded) * grow[p] for p in products}
    if "FS" in prov:
        prov["FS"] = {p: prov["FS"][p] - cut[p] for p in products}
    districts = sorted(({"province": q, "district": d, **{p: v[p] * grow[p] for p in products}}
                        for (q, d), v in districts_2022.items() if q in prov and not (q == "FS" and d in excluded)),
                       key=lambda r: -(r["petrol"] + r["diesel"]))
    moi = {p: sum(v[p] for v in prov.values()) for p in products}
    return {"national": national, "moi": moi, "inside": inside, "need": {p: moi[p] - inside[p] for p in products},
            "provinces": prov, "southern_fs_cut": cut, "districts": districts}


# ---------------------------------------------------------------- oil price build (petrol)

def oil_linked_price(brent: float, margin: float, petrol_share: float, fx: float) -> float:
    """Oil-linked part of the petrol price, rand per litre (no freight)."""
    return (brent + margin * petrol_share) * fx / LITRES_PER_BARREL


def petrol_price_build(oil: dict, oil25: dict, pump_2025: float, pump_2026: float) -> dict:
    """Real petrol pump price index vs 2025 for each case, 2025-2030.

    oil: ``moi_outlook.oil_price`` (per case brent, margin, petrol_share, fx); oil25: ``moi_outlook.oil_price_2025``;
    pump_2025 / pump_2026: average nominal pump price (R/L) in each year.
    """
    base = oil["Base"]
    oil_2025 = oil_linked_price(oil25["brent"], base["margin"], base["petrol_share"], oil25["fx"])
    other = pump_2025 - oil_2025                                         # levies, transport, margins: held real
    real_2026 = pump_2026 / pump_2025 / (1 + oil25["cpi_2026"])
    cases = {}
    for case in CASES:
        a = oil[case]
        linked = oil_linked_price(a["brent"], a["margin"], a["petrol_share"], a["fx"])
        level = (linked + other) / pump_2025
        cases[case] = {"oil_linked": linked, "pump": level * pump_2025, "index": level,
                       "path": [1.0, real_2026, (real_2026 + level) / 2, level, level, level]}
    return {"pump_2025": pump_2025, "oil_linked_2025": oil_2025, "other_2025": other, "real_2026": real_2026, "cases": cases}


# ---------------------------------------------------------------- forecast

def road_freight_diesel(trucks: list[dict], fleet: float, year: int, a: dict) -> float:
    """National road freight diesel (bn L), bottom-up from the truck fleet.

    trucks: base-year diesel heavy truck classes, each {"vehicles", "km", "l_per_100km"}; fleet: eNaTIS trucks in ``year``;
    a: ``moi_outlook.road_freight_diesel``. Km per truck held at the base year; fuel use per km falls by the efficiency gain.
    """
    n0 = sum(t["vehicles"] for t in trucks)
    litres = sum(t["vehicles"] * t["km"] * t["l_per_100km"] / 100 for t in trucks)
    return litres / n0 * fleet * (1 - a["efficiency_gain"]) ** (year - a["base_year"]) / 1e9


def uses_2025(start: dict, segments: dict, power_2025: float) -> dict:
    """Split 2025 demand (``start["moi"]``: market of interest, or national) into uses with the national segments (bn L).

    Segments are the workbook's, with road freight diesel replaced by the bottom-up estimate; unallocated diesel takes the difference.
    power_2025: peaker diesel in the area in 2025; the rest of diesel is split across the non-power uses.
    """
    nat, moi = start["national"], start["moi"]
    sh_p = moi["petrol"] / nat["petrol"]
    pet_road, pet_other = segments["Petrol road use"], segments["Other petrol"]
    diesel = {"freight": segments["Road freight diesel"], "light": segments["Other road diesel"], "mining": segments["Mining"],
              "agri": segments["Agriculture"], "manuf": segments["Manufacturing"], "other": segments["Other diesel / unallocated"]}
    diesel["unal"] = nat["diesel"] - sum(diesel.values()) - segments["Utility and private power"]
    nonpower_moi = moi["diesel"] - power_2025
    out = {"petrol_road": pet_road * sh_p, "petrol_other": pet_other * sh_p,
           "petrol_unal": (nat["petrol"] - pet_road - pet_other) * sh_p}
    out.update({f"diesel_{k}": v / sum(diesel.values()) * nonpower_moi for k, v in diesel.items()})
    out["diesel_power"], out["diesel_private"] = power_2025, 0.0
    return out


def generator_diesel(diesel: dict, power: dict, a: dict) -> dict:
    """Private generator diesel (national bn L) in 2030 by case (Henry Gilfillan, 14 October 2026).

    The fall in diesel from the load-shedding year to the year without load shedding, less the fall in peaker diesel, is taken as
    generator diesel at that level of load shedding. diesel / power: national diesel and peaker diesel by calendar year;
    a: ``moi_outlook.backup_generators`` (years, and the share of that level back in 2030 in each case).
    """
    y0, y1 = a["years"]
    drop = (diesel[y0] - diesel[y1]) - (power[y0] - power[y1])
    return {"drop": drop, "diesel_drop": diesel[y0] - diesel[y1], "power_drop": power[y0] - power[y1],
            "cases": {c: drop * a["level"][c] for c in CASES}}


def peaker_load_factors(pk: dict, eskom_gwh: float, ipp_gwh: float) -> dict:
    """Load factor in 2030 by owner and case. eskom_gwh / ipp_gwh: OCGT output in the ratio year (FY ending March)."""
    eskom_mw, ipp_mw = sum(pk["eskom_units_mw"].values()), sum(pk["ipp_units_mw"].values())
    ratio = (ipp_gwh / (ipp_mw * 8.76)) / (eskom_gwh / (eskom_mw * 8.76))
    eskom = {"Low": pk["eskom_gwh_2026"] / (pk["eskom_days_2026"] / 365) / (eskom_mw * 8.76), **pk["eskom_load_factor"]}
    return {"ratio": ratio, "eskom": eskom, "ipp": {c: v * ratio for c, v in eskom.items()}}


def peaker_diesel(pk: dict, load: dict, case: str, units: list[str]) -> float:
    """Diesel (bn L) used by the named peakers at the case load factors."""
    mw = {**{k: ("eskom", v) for k, v in pk["eskom_units_mw"].items()}, **{k: ("ipp", v) for k, v in pk["ipp_units_mw"].items()}}
    return sum(mw[u][1] * load[mw[u][0]][case] for u in units) * 8.76 * pk["litres_per_kwh"] / 1000


def ev_share(curve: dict, year: int) -> float:
    return curve["ceiling"] / (1 + math.exp((curve["midpoint"] - year) / curve["slope"]))


def anchor_ev_curves(ev: dict, share: float) -> dict:
    """Low and High curves with the midpoint set so each passes through ``share`` (of new light vehicles) in the anchor year."""
    return {c: {**ev[c], "midpoint": ev["anchor_year"] + ev[c]["slope"] * math.log(ev[c]["ceiling"] / share - 1)}
            for c in ("Low", "High")}


def ev_benchmark_check(ev: dict, curves: dict, car_share: float) -> dict:
    """Each case's electric share of new cars in the check year against its benchmark band; raises if any case is outside it."""
    y, b = ev["check_year"], ev["benchmarks"]
    share = {"Low": ev_share(curves["Low"], y), "High": ev_share(curves["High"], y)}
    share["Base"] = (share["Low"] + share["High"]) / 2
    out = {}
    for case in CASES:
        lo, hi = (b[k] if k else None for k in ev["bands"][case])
        cars = share[case] / car_share
        ok = (lo is None or cars >= lo) and (hi is None or cars <= hi)
        out[case] = {"car_share": cars, "band": [lo, hi], "ok": ok}
    bad = {c: v for c, v in out.items() if not v["ok"]}
    if bad:
        raise ValueError(f"EV cases outside their benchmark bands in {y}: {bad}")
    return out


def rail_shift(a: dict, road_2025: float, rail_2025: float) -> dict:
    """Share of 2030 road freight tonnes moved to rail in each case, against 2025 mode shares."""
    total_2030 = (road_2025 + rail_2025) * math.prod(1 + g for g in a["gdp_path_rail_total"])
    rail_const = total_2030 * rail_2025 / (road_2025 + rail_2025)
    road_const = total_2030 - rail_const
    r = a["rail"]
    rail_2030 = {"Low": r["Low"], "Base": r["Base"], "High": rail_2025 * (1 + r["high_growth"]) ** 5}
    return {"rail_2030": rail_2030, "shift": {c: (v - rail_const) / road_const for c, v in rail_2030.items()},
            "rail_const_2030": rail_const, "road_const_2030": road_const}


LEVERS = ("gdp", "price", "efficiency", "ev", "rail", "peakers", "generators")


def forecast(base: dict, a: dict, price_path: dict, rail: dict, fleet: dict, start: dict, load: dict, units: list[str],
             generators: dict, off: frozenset = frozenset()) -> dict:
    """Demand by case and year (bn L), with the parts by use, for the area in ``start["moi"]`` (market of interest or national).

    base: ``uses_2025``; a: the ``moi_outlook`` assumptions; price_path: case -> real petrol price index 2025-2030; rail:
    ``rail_shift``; fleet: {"parc": cars + LCVs Dec 2025, "new": new cars + LCVs 2025, "km_factor": new vs fleet-average km,
    "ev_share_2025": electric share of new cars + LCVs in the EV anchor year};
    load: ``peaker_load_factors``; units: the peakers in the area; generators: ``generator_diesel`` (national, scaled to the area by
    its diesel share); off: levers (``LEVERS``) held at their 2025 level, for ``lever_contributions``.
    """
    el = a["petrol_elasticities"]
    adj = el["phasing_short_run"] / el["phasing_long_run"]            # share of the long-run price effect felt within a year
    pk = a["peakers"]
    curves = anchor_ev_curves(a["ev_scurves"], fleet["ev_share_2025"])
    sh_d = start["moi"]["diesel"] / start["national"]["diesel"]
    out = {}
    for case in CASES:
        gdp = [0.0 if "gdp" in off else a["gdp_growth"][case]] * 5
        ep, ed = (0.0, 0.0) if "efficiency" in off else (a["efficiency"][case]["petrol"], a["efficiency"][case]["diesel"])
        shift, rebound = 0.0 if "rail" in off else rail["shift"][case], a["rail"]["rebound"]
        pe = [0.0]                                                      # log price effect, moving towards its long-run level
        for i in range(1, len(YEARS)):
            target = 0.0 if "price" in off else el["price_long_run"] * math.log(price_path[case][i])
            pe.append(pe[-1] + adj * (target - pe[-1]))
        cum_ev, parc, years = 0.0, fleet["parc"], {}
        for i, y in enumerate(YEARS):
            if y > 2025:
                sales = fleet["new"] * math.prod(1 + g for g in gdp[:i])
                share = (0.0 if "ev" in off else (ev_share(curves["Low"], y) + ev_share(curves["High"], y)) / 2 if case == "Base"
                         else ev_share(curves[case], y))
                cum_ev += sales * share
                parc *= 1 + a["light_fleet"]["growth"]
            evd = cum_ev / parc * fleet["km_factor"]                    # share of light-vehicle fuel displaced
            act_d = math.prod(1 + a["diesel_gdp_elasticity"] * g for g in gdp[:i])
            act_p = math.prod(1 + el["income"] * g for g in gdp[:i]) * math.exp(pe[i])
            f = i / 5                                                   # rail shift and peaker use move evenly to 2030
            v = {"petrol_road": base["petrol_road"] * act_p * (1 - ep) ** i * (1 - evd),
                 "petrol_other": base["petrol_other"] * act_p, "petrol_unal": base["petrol_unal"] * act_p,
                 "diesel_freight": base["diesel_freight"] * act_d * (1 - ed) ** i * (1 - shift * f * (1 - rebound)),
                 "diesel_light": base["diesel_light"] * act_d * (1 - ed) ** i * (1 - evd)}
            for k in ("mining", "agri", "manuf", "other", "unal"):
                v[f"diesel_{k}"] = base[f"diesel_{k}"] * act_d
            power_2030 = base["diesel_power"] if "peakers" in off else peaker_diesel(pk, load, case, units)
            v["diesel_power"] = base["diesel_power"] + (power_2030 - base["diesel_power"]) * f
            gen_2030 = base["diesel_private"] if "generators" in off else generators["cases"][case] * sh_d
            v["diesel_private"] = base["diesel_private"] + (gen_2030 - base["diesel_private"]) * f
            petrol = sum(x for k, x in v.items() if k.startswith("petrol"))
            diesel = sum(x for k, x in v.items() if k.startswith("diesel"))
            inside = start["inside"]["petrol"] + start["inside"]["diesel"]
            years[y] = {"petrol": petrol, "diesel": diesel, "total": petrol + diesel, "brought_in": petrol + diesel - inside,
                        "ev_fleet_share": cum_ev / parc, "parts": v}
        out[case] = years
    return {"cases": out}


def lever_contributions(run, product: str = "total") -> dict:
    """Year-on-year change in demand split by lever, by case (bn L).

    run: a function ``off -> forecast(...)`` with every other input fixed. A lever's effect in a year is demand with all levers
    less demand with that lever held at 2025; its yearly contribution is the change in that effect. The remainder (levers acting
    together) is shown as "interaction", so each year's contributions add to the change in demand.
    """
    full = run(frozenset())["cases"]
    without = {lv: run(frozenset({lv}))["cases"] for lv in LEVERS}
    out = {}
    for case in CASES:
        rows = {}
        for i, y in enumerate(YEARS[1:], 1):
            prev = YEARS[i - 1]
            change = full[case][y][product] - full[case][prev][product]
            contrib = {lv: (full[case][y][product] - without[lv][case][y][product])
                       - (full[case][prev][product] - without[lv][case][prev][product]) for lv in LEVERS}
            contrib["interaction"] = change - sum(contrib.values())
            rows[y] = {"change": change, "level": full[case][y][product], **contrib}
        out[case] = rows
    return out
