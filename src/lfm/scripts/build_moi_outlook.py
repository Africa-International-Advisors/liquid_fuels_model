"""Build the petrol and diesel outlook to 2030, market of interest and national (Low / Base / High demand cases).

    python -m lfm.scripts.build_moi_outlook [--vintage 2026]

Reads the ``moi_outlook`` assumptions through the provider and the data below, runs ``lfm.model.moi_outlook`` and writes
``runs/moi_outlook/<timestamp>/``: moi_2025.json (starting point), oil_price_build.json (petrol price by case),
moi_forecast.json (all results; ``cases`` = market of interest, ``national`` = South Africa) and moi_forecast_results.csv
(area x case x year).
Data: Sasol and Glencore refinery output; analytical workbook v02 plant yields, segments and evidence; SARS fuel trade; Department
district sales 2022; Department petrol 95 inland prices; Eskom OCGT and IPP OCGT output; eNaTIS fleet and new registrations; Stone et al. (2018) vehicle parameters.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
from datetime import datetime
from pathlib import Path

import openpyxl

from lfm.assumptions import YamlDirectoryProvider
from lfm.config import Paths
from lfm.model import moi_outlook as mo
from lfm.run import Run

T, A = "assumptions/2026/timeseries/", "output/delivered/sa_analytics_2026_10_11_v02/"
PRODUCTS = ("petrol", "diesel")
DISTRICT_FILE = "data/raw/energy_dept/fsv_district/2022-Quarter4-Magisterial-Districts-data.xlsx"
PROVINCES = {"Eastern Cape": "EC", "Free State": "FS", "Gauteng": "GP", "KwaZulu Natal": "KZN", "Limpopo": "LP", "Mpumalanga": "MP",
             "North West": "NW", "Northern Cape": "NC", "Western Cape": "WC"}
KEYS = ("market", "gdp_growth", "gdp_path_rail_total", "petrol_elasticities", "diesel_gdp_elasticity", "oil_price", "oil_price_2025",
        "efficiency", "ev_scurves", "light_fleet", "road_freight_diesel", "rail", "peakers", "backup_generators")


def rows(root: Path, rel: str) -> list[dict]:
    with open(root / rel, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def national_2025(root: Path, year: int = 2025) -> tuple[dict, dict, dict]:
    """Demand by product (production + imports - exports), Secunda + Natref output and all plant output, bn L (pack pp4, 11)."""
    y = str(year)
    ops = rows(root, "assumptions/2026/reference/refinery_output_operators.csv")
    sasol = {(r["plant"], r["period"]): float(r["value"]) for r in ops if r["operator"] == "Sasol"}
    astron = {r["period"]: float(r["value"]) for r in ops if r["operator"] == "Glencore"}
    plant = {r["Plant"]: r for r in rows(root, A + "plant_supply.csv")}
    bbl = 158.987294928 / 1000
    btu = float(plant["Astron"]["All products bn L"]) / astron["2025"]                 # 2025 product litres per reported unit
    output = {"Secunda": sasol["Secunda", y] * bbl, "Natref": sasol["Natref", y] / 0.6364 * bbl, "Astron": astron[y] * btu}
    by_plant = {k: {p: v * float(plant[k][f"{p.capitalize()} yield"]) for p in PRODUCTS} for k, v in output.items()}
    trade = rows(root, T + "fuel_trade_sars.csv")

    def flow(f, p):
        rr = [r for r in trade if r["period"] == y and r["flow"] == f and r["product"] == p]
        if not rr or any(r["unit"] != "litres" or r["months_reported"] != "12" for r in rr):
            raise ValueError(f"incomplete {y} SARS trade for {f} {p}")
        return sum(float(r["value"]) for r in rr) / 1e9

    national = {p: sum(v[p] for v in by_plant.values()) + flow("import", p) - flow("export", p) for p in PRODUCTS}
    inside = {p: by_plant["Secunda"][p] + by_plant["Natref"][p] for p in PRODUCTS}
    return national, inside, {p: sum(v[p] for v in by_plant.values()) for p in PRODUCTS}


def district_sales_2022(root: Path) -> tuple[dict, dict]:
    """2022 sales by province and district (bn L): four quarterly sheets; a province row is followed by its districts."""
    def province_of(name):
        n = name.replace("-", " ").replace(" Province", "").replace(" ", "").strip().lower()
        return next((c for k, c in PROVINCES.items() if n == k.replace(" ", "").lower()), None)

    wb = openpyxl.load_workbook(root / DISTRICT_FILE, read_only=True, data_only=True)
    prov = collections.defaultdict(lambda: {"petrol": 0.0, "diesel": 0.0})
    dist = collections.defaultdict(lambda: {"petrol": 0.0, "diesel": 0.0})
    def num(v):
        return float(v) if v not in (None, "") else 0.0

    for sheet in ("2022 Q1", "2022 Q2", "2022 Q3", "2022 Q4"):
        header, current = None, None
        for row in wb[sheet].iter_rows(values_only=True):
            if row[0] == "Row Labels":
                header = [str(c) if c else "" for c in row]
                col = {"petrol": header.index("Petrol"), "diesel": header.index("Diesel")}
                continue
            if header is None or row[0] is None or str(row[0]).strip().lower().startswith("grand total"):
                continue
            name = str(row[0]).strip()
            code = province_of(name)
            target = prov[code] if code else dist[current, name]
            if code:
                current = code
            elif current is None:
                raise ValueError(f"district before any province: {name}")
            for p in PRODUCTS:
                target[p] += num(row[col[p]]) / 1e9
    wb.close()
    if set(prov) != set(PROVINCES.values()):
        raise ValueError(f"provinces found: {sorted(prov)}")
    for c in prov:
        if abs(sum(v["petrol"] + v["diesel"] for (q, _), v in dist.items() if q == c) - prov[c]["petrol"] - prov[c]["diesel"]) > 1e-6:
            raise ValueError(f"districts do not add to province {c}")
    return dict(prov), dict(dist)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vintage", default="2026")
    args = parser.parse_args(argv)
    paths = Paths.default()
    root = paths.repo_root
    provider, run = YamlDirectoryProvider(paths), Run(vintage=args.vintage)
    a = {k: provider.get("moi_outlook", k, run).value for k in KEYS}

    national, inside, produced = national_2025(root)
    provinces, districts = district_sales_2022(root)
    start = mo.market_2025(national, inside, provinces, districts, a["market"])

    analytics = json.loads((root / A / "analytics.json").read_text(encoding="utf-8"))
    sheets = analytics["sheets"]
    segments = {r[0]: r[3]["value"] for r in sheets["Segments"]["rows"] if isinstance(r, list) and r and isinstance(r[3], dict)}
    evidence = {r[0]: r[1] for r in sheets["Evidence"]["rows"] if isinstance(r, list) and r}
    pk = a["peakers"]
    ocgt = {(r["series"], int(r["period"])): float(r["value"]) for r in rows(root, T + "ocgt_generation_eskom.csv")}
    load = mo.peaker_load_factors(pk, ocgt["eskom_ocgt", pk["ratio_year"]], ocgt["ipp_ocgt", pk["ratio_year"]])
    ipp_l = ocgt["ipp_ocgt", 2025] * pk["litres_per_kwh"] / 1000                     # IPP diesel, FY2025, bn L
    ipp_mw = sum(pk["ipp_units_mw"].values())
    power_moi = ipp_l * sum(pk["ipp_units_mw"][u] for u in pk["market_units"]) / ipp_mw
    power_nat = evidence["eskom_2025"] + ipp_l                                          # Eskom fuel (IR 2025 p141) + IPP
    gy = a["backup_generators"]["years"]
    gen_diesel = {y: national_2025(root, y)[0]["diesel"] for y in gy}
    gen_power = {y: evidence[f"eskom_{y + 1}"] + ocgt["ipp_ocgt", y + 1] * pk["litres_per_kwh"] / 1000 for y in gy}  # FY to next March
    generators = mo.generator_diesel(gen_diesel, gen_power, a["backup_generators"])
    generators.update(diesel=gen_diesel, power=gen_power)
    trucks = [{"vehicles": float(r["vehicles_2010"]), "km": float(r["km_per_year_fleet_average"]),
               "l_per_100km": float(r["l_per_100km_fleet_average"])}
              for r in rows(root, "assumptions/2026/reference/vehicle_parameters_stone2018.csv")
              if r["vehicle_type"].startswith("HCV") and r["fuel"] == "diesel"]
    truck_fleet = collections.defaultdict(float)
    for r in rows(root, T + "vehicle_population_natis.csv"):
        if r["province"] != "ZAF" and r["vehicle_class"] == "trucks" and r["period"].endswith("-12"):
            truck_fleet[int(r["period"][:4])] += float(r["value"])
    freight = {y: mo.road_freight_diesel(trucks, truck_fleet[y], y, a["road_freight_diesel"]) for y in (2023, 2024, 2025)}
    road_freight = {"bottom_up": freight, "workbook_2025": segments["Road freight diesel"], "trucks": dict(truck_fleet)}
    seg = {**segments, "Road freight diesel": freight[2025]}
    base = mo.uses_2025(start, seg, power_moi)
    start_nat = {**start, "moi": national, "inside": produced}                        # national: all demand, all local plants
    base_nat = mo.uses_2025(start_nat, seg, power_nat)

    prices = {r["period"]: float(r["value"]) / 100 for r in rows(root, T + "fuel_prices_department.csv")
              if r["series"] == "petrol_95_inland_retail"}
    pump_2025 = sum(prices[f"2025-{m:02d}"] for m in range(1, 13)) / 12
    last = max(p for p in prices if p.startswith("2026-"))
    months = int(last[-2:])
    pump_2026 = (sum(prices[f"2026-{m:02d}"] for m in range(1, months + 1)) + (12 - months) * prices[last]) / 12   # rest of 2026 held
    price = mo.petrol_price_build(a["oil_price"], a["oil_price_2025"], pump_2025, pump_2026)

    rail = mo.rail_shift(a, evidence["freight_road_2025"], evidence["freight_rail_2025"])
    parc = sum(float(r["value"]) for r in rows(root, T + "vehicle_population_natis.csv")
               if r["period"] == "2025-12" and r["province"] != "ZAF" and r["vehicle_class"] in ("cars", "light_commercial"))
    ev = a["ev_scurves"]
    new_by = {k: sum(float(r["value"]) for r in rows(root, T + "new_vehicle_registrations_natis_annual.csv")
                     if r["period"] == str(ev["anchor_year"]) and r["vehicle_class"] == k)
              for k in ("cars", "light_commercial")}
    new = new_by["cars"] + new_by["light_commercial"]
    car_share = new_by["cars"] / new
    stone = {r["vehicle_type"]: r for r in rows(root, "assumptions/2026/reference/vehicle_parameters_stone2018.csv")}
    km_factor = float(stone["CarGasoline"]["km_per_year_new"]) / float(stone["CarGasoline"]["km_per_year_fleet_average"])
    fleet = {"parc": parc, "new": new, "km_factor": km_factor, "car_share_of_new": car_share,
             "ev_share_2025": ev["anchor_car_share"] * car_share}                     # electric sales are almost all cars
    curves = mo.anchor_ev_curves(ev, fleet["ev_share_2025"])
    ev_check = mo.ev_benchmark_check(ev, curves, car_share)

    path = {c: v["path"] for c, v in price["cases"].items()}
    nat_units = [*pk["eskom_units_mw"], *pk["ipp_units_mw"]]
    res = mo.forecast(base, a, path, rail, fleet, start, load, pk["market_units"], generators)
    res_nat = mo.forecast(base_nat, a, path, rail, fleet, start_nat, load, nat_units, generators)

    def run_moi(off):
        return mo.forecast(base, a, path, rail, fleet, start, load, pk["market_units"], generators, off)

    def run_nat(off):
        return mo.forecast(base_nat, a, path, rail, fleet, start_nat, load, nat_units, generators, off)
    levers = {area: {p: mo.lever_contributions(fn, p) for p in ("petrol", "diesel", "total")}
              for area, fn in (("market_of_interest", run_moi), ("national", run_nat))}

    out = paths.runs_dir / "moi_outlook" / datetime.now().strftime("%Y%m%d_%H%M%S")
    out.mkdir(parents=True, exist_ok=False)

    def dump(name, obj):
        (out / name).write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")

    dump("moi_2025.json", {**start, "districts_count": len(start["districts"])})
    dump("oil_price_build.json", {"assumptions": {"oil_price": a["oil_price"], "oil_price_2025": a["oil_price_2025"]},
                                  "latest_price_month": last, **price})
    shares = {p: start["moi"][p] / start["national"][p] for p in PRODUCTS}
    dump("moi_forecast.json", {"vintage": run.vintage, "model_version": run.model_version, "years": mo.YEARS, "assumptions": a,
                               "shares": shares, "inside": sum(start["inside"].values()),
                               "base2025": base, "road_freight_diesel": road_freight, "fleet": fleet, "ev_curves": curves, "ev_benchmark_check": ev_check, "rail": rail, "peaker_load_factor": load, "generators": generators, "levers": levers,
                               "base2025_national": base_nat, "produced_national": produced,
                               "petrol_price_index": {c: v["path"] for c, v in price["cases"].items()},
                               "cases": {c: {str(y): d for y, d in ys.items()} for c, ys in res["cases"].items()},
                               "national": {c: {str(y): d for y, d in ys.items()} for c, ys in res_nat["cases"].items()}})
    with open(out / "moi_forecast_results.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["area", "case", "year", "petrol_bn_l", "diesel_bn_l", "total_bn_l", "brought_in_bn_l", "real_petrol_price_index"])
        for area, r in (("market_of_interest", res), ("national", res_nat)):
            for c, ys in r["cases"].items():
                for i, (y, d) in enumerate(ys.items()):
                    w.writerow([area, c, y, round(d["petrol"], 4), round(d["diesel"], 4), round(d["total"], 4),
                                round(d["brought_in"], 4), round(price["cases"][c]["path"][i], 4)])

    m = start["moi"]
    print(f"2025E market of interest: petrol {m['petrol']:.2f} diesel {m['diesel']:.2f} total {m['petrol'] + m['diesel']:.2f} bn L; "
          f"{len(start['districts'])} districts; inside {sum(start['inside'].values()):.2f}")
    print("road freight diesel, national bn L:", {y: round(v, 3) for y, v in freight.items()},
          f"(workbook 2025 {segments['Road freight diesel']:.3f}); market of interest 2025 {base['diesel_freight']:.3f}")
    print(f"petrol pump 2025 R{price['pump_2025']:.2f} = oil-linked R{price['oil_linked_2025']:.2f} + other R{price['other_2025']:.2f}; "
          f"2026 real {price['real_2026'] - 1:+.1%} (prices to {last})")
    print(f"peakers: IPP/Eskom load-factor ratio FY{pk['ratio_year']} {load['ratio']:.3f} | Eskom-owned " +
          " / ".join(f"{v:.2%}" for v in load["eskom"].values()) + " | IPP " + " / ".join(f"{v:.2%}" for v in load["ipp"].values()) +
          f" | 2025 power: market of interest {power_moi:.3f}, national {power_nat:.3f} bn L")
    print(f"EV curves anchored at {ev['anchor_car_share']:.2%} of new cars = {fleet['ev_share_2025']:.2%} of new light vehicles in "
          f"{ev['anchor_year']} (cars {car_share:.1%}): midpoints " + ", ".join(f"{c} {v['midpoint']:.1f}" for c, v in curves.items()) +
          "; 2030 share of new cars " + ", ".join(
              f"{c} {(mo.ev_share(curves['Low'], 2030) + mo.ev_share(curves['High'], 2030)) / 2 / car_share:.2%}" if c == "Base"
              else f"{c} {mo.ev_share(curves[c], 2030) / car_share:.2%}" for c in mo.CASES))
    print(f"generators: diesel {gy[0]}->{gy[1]} fell {generators['diesel_drop']:.3f}, peakers {generators['power_drop']:.3f}, "
          f"so generator diesel {generators['drop']:.3f} bn L; 2030 national " +
          " / ".join(f"{c} {v:.3f}" for c, v in generators["cases"].items()))

    def pct(x):
        return "-" if x is None else f"{x:.1%}"
    print(f"EV benchmark check {ev['check_year']}: " + ", ".join(
        f"{c} {v['car_share']:.1%} in [{pct(v['band'][0])}, {pct(v['band'][1])}]" for c, v in ev_check.items()))
    for area, r in (("market of interest", res), ("national", res_nat)):
        for c, ys in r["cases"].items():
            y = ys[2030]
            print(f"{area} {c}: price {price['cases'][c]['index'] - 1:+.1%} | 2030 petrol {y['petrol']:.2f} diesel {y['diesel']:.2f} "
                  f"(power {y['parts']['diesel_power']:.3f}, generators {y['parts']['diesel_private']:.3f}) total {y['total']:.2f} brought in {y['brought_in']:.2f}")
    for c in mo.CASES:
        lv = levers["market_of_interest"]["total"][c]
        tot = {k: sum(r[k] for r in lv.values()) for k in (*mo.LEVERS, "interaction", "change")}
        print(f"levers 2025-2030, market of interest {c}: " + ", ".join(f"{k} {v:+.2f}" for k, v in tot.items()))
    print("saved", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
