"""Collect the volume tags shown on the market-sizing pack.

Reads registered results and writes a small JSON that the PowerPoint builder
consumes. The national balance is Manish's DR01 file, not recalculated here
(see workstreams/WS0_governance/workplan/overlap_log_2026_10_08.md, item 1):
production is the published energy balance and ends in 2021; trade is SARS
customs; sales are the department's. No residual is labelled as production.
The coastal/inland split is a presentation proxy (coastal provinces KZN, WC, EC),
not a registered modelling assumption.
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SERIES = REPO / "assumptions" / "2026" / "timeseries"
BALANCE_FILE = REPO / "workstreams" / "WS1_data_validation" / "fuel_balance_petrol_diesel_2009_2025_2026-10-06.csv"
OUTPUT = REPO / "pptx" / "story" / "issue_tree_volumes_2026_10_08.json"
PRODUCTS = ("petrol", "diesel")
COASTAL_PROVINCES = ("KZN", "WC", "EC")
BASE_YEAR = "2023"
PRODUCTION_YEAR = "2021"
PROVINCE_YEAR = "2022"
BALANCE_YEAR = "2021"
ENTRY_YEAR = "2025"
BALANCE_ROWS = ("2019", "2021", "2023")


def read(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def billions(value):
    # Adding 0.0 turns a rounded -0.0 into 0.0 so tags never print a negative zero.
    return None if value is None else round(value / 1e9, 1) + 0.0


def number(text):
    return float(text) if text not in ("", None) else None


def balance_by_year():
    rows = defaultdict(dict)
    for r in read(BALANCE_FILE):
        if r["product"] in PRODUCTS:
            rows[r["period"]][r["product"]] = r
    return rows


def line(year_rows, column):
    """Petrol plus diesel for one balance column, with the split; None when either is unpublished."""
    values = {p: number(year_rows[p][column]) for p in PRODUCTS}
    if any(v is None for v in values.values()):
        return {"value": None, "split": None}
    return {"value": billions(sum(values.values())), "split": {p: billions(v) for p, v in values.items()}}


def national_balance(balance):
    rows = []
    for year in BALANCE_ROWS:
        year_rows = balance[year]
        production = line(year_rows, "production_used")
        supply_less_sales = line(year_rows, "supply_less_sales")
        rows.append({
            "year": year,
            "basis": "Energy balance, customs, sales" if production["value"] is not None else "Customs and sales",
            "production": {**production, "status": "observed" if production["value"] is not None else "not published"},
            "imports": {**line(year_rows, "imports_used"), "status": "customs"},
            "exports": {**line(year_rows, "exports_used"), "status": "customs"},
            "sales": {**line(year_rows, "sales_used"), "status": "observed"},
            "supply_less_sales": {**supply_less_sales,
                                  "status": "calculated" if supply_less_sales["value"] is not None else "cannot close"},
        })
    return rows


def closure(balance):
    """How closely supply matched sales in the matched years, and the single largest gap."""
    gaps = [(year, p, number(rows[p]["supply_less_sales"]))
            for year, rows in balance.items() for p in PRODUCTS
            if p in rows and number(rows[p]["supply_less_sales"]) is not None]
    gaps.sort(key=lambda gap: -abs(gap[2]))
    exception, rest = gaps[0], gaps[1:]
    years = sorted({year for year, _, _ in gaps})
    return {"from": years[0], "to": years[-1], "within": billions(max(abs(v) for _, _, v in rest)),
            "exception": {"year": exception[0], "product": exception[1], "value": billions(exception[2])}}


PROVINCE_FILE = REPO / "workstreams" / "WS1_data_validation" / "provincial_petrol_diesel_2013_2024_2026-10-06.csv"
BACKTEST_FILE = REPO / "workstreams" / "WS1_data_validation" / "provincial_share_backtest_2026-10-08.csv"
SECTOR_FILE = REPO / "workstreams" / "WS1_data_validation" / "sector_baselines_2026-10-07.csv"
DR07_FILE = REPO / "workstreams" / "WS1_data_validation" / "dr07_demand_evidence_2026-10-08.csv"
LEVER_FILE = REPO / "workstreams" / "WS2_model_development" / "fuel_lever_response_2026-10-07.csv"
PROVINCE_NAMES = {"GP": "Gauteng", "KZN": "KwaZulu-Natal", "WC": "Western Cape", "EC": "Eastern Cape",
                  "MP": "Mpumalanga", "FS": "Free State", "NW": "North West", "LP": "Limpopo", "NC": "Northern Cape"}
# Demand levers shown on the parameters page, grouped as on the issue tree (fuels, lever, label).
# Levers the file holds for both fuels are shown with both.
LEVER_GROUPS = {
    "Economic activity": [(("petrol",), "gdp_growth", "GDP growth"), (("diesel",), "road_activity", "Road freight activity"),
                          (("petrol", "diesel"), "real_fuel_price", "Real fuel price")],
    "Vehicle fleet": [(("petrol",), "bev_new_sales_share", "Battery EV share of new sales"),
                      (("petrol", "diesel"), "new_cohort_efficiency", "New-vehicle efficiency"),
                      (("petrol",), "conventional_hybrid_new_sales_share", "Hybrid share of new sales")],
    "Freight and rail": [(("diesel",), "rail_diversion", "Road freight moved to rail"),
                         (("diesel",), "electric_share_of_new_truck_sales", "Electric share of new trucks"),
                         (("petrol",), "rail_passenger_journeys", "Rail passenger journeys")],
    "Power": [(("diesel",), "ocgt_generation", "Diesel turbine output"),
              (("diesel",), "private_backup_generation", "Private backup generation")],
}


def provinces_by_year():
    """Provincial petrol and diesel (DR01 file), first and last observed years and the 2023 estimate."""
    values = defaultdict(dict)
    status = {}
    for r in read(PROVINCE_FILE):
        values[(r["province"], r["period"])][r["product"]] = float(r["value"])
        status[r["period"]] = r["status"]
    error = {r["product"]: float(r["mean_share_points_misallocated"]) for r in read(BACKTEST_FILE) if r["method"] == "quarter1"}
    rows = []
    for code, name in PROVINCE_NAMES.items():
        first, last = values[(code, "2013")], values[(code, "2022")]
        rows.append({"code": code, "name": name, "coastal": code in COASTAL_PROVINCES,
                     "petrol": billions(last["petrol"]), "diesel": billions(last["diesel"]),
                     "total": billions(last["petrol"] + last["diesel"]),
                     "petrol_2013": billions(first["petrol"]), "diesel_2013": billions(first["diesel"]),
                     "change_pct": round(100 * (sum(last.values()) / sum(first.values()) - 1))})
    # Totals and comparisons use unrounded litres so they match the issue tree.
    litres = {code: sum(values[(code, "2022")].values()) for code in PROVINCE_NAMES}
    national = sum(litres.values())
    for row in rows:
        row["share_pct"] = round(100 * litres[row["code"]] / national)
    petrol_fell = [values[(c, "2022")]["petrol"] < values[(c, "2013")]["petrol"] for c in PROVINCE_NAMES]
    return {"year": "2022", "first_year": "2013", "status": status["2022"], "rows": rows,
            "coastal_total": billions(sum(v for c, v in litres.items() if c in COASTAL_PROVINCES)),
            "inland_total": billions(sum(v for c, v in litres.items() if c not in COASTAL_PROVINCES)),
            "petrol_fell_in": sum(petrol_fell), "province_count": len(petrol_fell),
            "estimate_year": "2023", "estimate_status": status["2023"],
            "estimate_error_points": {k: round(v, 1) for k, v in error.items()},
            "source": "provincial_petrol_diesel_2013_2024_2026-10-06.csv (DR01)"}


def dr07_series(item):
    row = next(r for r in read(DR07_FILE) if r["item"] == item)
    values = [float(v.replace(",", "")) for v in row["value"].split(";")]
    periods = [p.strip() for p in row["period"].replace("years to March ", "").split(";")]
    return dict(zip(periods, values))


def sector_use(flow_total):
    """Each demand-by-use source side by side; nothing is reconciled here (overlap log item 6)."""
    model = defaultdict(float)
    for r in read(SECTOR_FILE):
        if r["scenario"] == "high_demand" and r["period"] == "2024" and r["product"].split("_")[0] in ("petrol", "diesel"):
            model[r["segment"]] += float(r["with_sourced_baselines"])
    eskom = dr07_series("Fuel burned at Eskom's turbines, as reported")
    independent = dr07_series("Diesel burned at independent plants, estimated")
    reported = {year: billions((eskom.get(year, 0) + independent.get(year, 0)) * 1e6) for year in ("2023", "2024", "2025")}
    return {
        "balance_year": BALANCE_YEAR, "model_year": "2024",
        "sectors": [
            {"key": "road", "label": "Road transport", "balance": billions(flow_total("Road")), "model": billions(model["vehicles"]),
             "reported": None},
            {"key": "industry", "label": "Mining and industry", "balance": billions(flow_total("Industry")), "model": billions(model["industrial"]),
             "reported": None, "note": "mining {:.1f} of balance".format(billions(flow_total("Mining and quarrying")))},
            {"key": "agriculture", "label": "Agriculture", "balance": billions(flow_total("Agriculture/forestry")), "model": billions(model["agriculture"]),
             "reported": None},
            {"key": "power", "label": "Power generation", "balance": None, "model": billions(model["generation"]),
             "reported": reported},
            {"key": "other", "label": "Other and marine", "balance": billions(flow_total("Other") - flow_total("Agriculture/forestry")),
             "model": billions(model["marine"]), "reported": None},
        ],
        "balance_total": billions(flow_total("Final consumption")),
        "model_total": billions(sum(model[k] for k in ("vehicles", "industrial", "agriculture", "generation", "marine"))),
        "source": "energy balance 2021; sector_baselines_2026-10-07.csv (model, high demand, 2024); DR07 (Eskom reported, independent estimated)",
    }


def demand_levers():
    rows = read(LEVER_FILE)
    groups = []
    for group, levers in LEVER_GROUPS.items():
        items = []
        for fuels, lever, label in levers:
            by_fuel = []
            for fuel in fuels:
                cases = {r["case"]: r for r in rows if r["fuel"] == fuel and r["lever"] == lever and r["period"] == "2035"}
                low, medium, high = (cases[c] for c in ("low", "medium", "high"))
                by_fuel.append({"fuel": fuel, "unit": low["unit"], "baseline": low["baseline"],
                                "cases_2035": [low["analyst_value"], medium["analyst_value"], high["analyst_value"]],
                                "changed": sum(cases[c]["changed"] == "yes" for c in cases),
                                "proposed_2035": [low["proposed_by_nigel"], medium["proposed_by_nigel"], high["proposed_by_nigel"]]})
            items.append({"label": label, "fuels": by_fuel})
        groups.append({"group": group, "levers": items})
    return {"period": "2035", "groups": groups, "status": "analyst proposal, not accepted",
            "source": "fuel_lever_response_2026-10-07.csv (Manish)"}


def main():
    balance = balance_by_year()
    base, production_year = balance[BASE_YEAR], balance[PRODUCTION_YEAR]
    provinces = [r for r in read(SERIES / "fuel_sales_department_by_province.csv")
                 if r["period"] == PROVINCE_YEAR and r["product"] in PRODUCTS]

    # Sector split from the latest full department energy balance. Industry includes mining;
    # other is commercial/public, residential and non-specified. Not reconciled with the model's
    # sector baselines (overlap log item 6).
    energy = [r for r in read(SERIES / "energy_balance_department.csv")
              if r["period"] == BALANCE_YEAR and r["product"] in PRODUCTS]
    flow_total = lambda flow: sum(float(r["value"] or 0) for r in energy if r["flow"] == flow)
    uses = {"road": flow_total("Road"), "transport_other": flow_total("Transport") - flow_total("Road"),
            "industry_incl_mining": flow_total("Industry"), "agriculture": flow_total("Agriculture/forestry"),
            "other": flow_total("Other") - flow_total("Agriculture/forestry")}

    offices = defaultdict(float)
    for r in read(SERIES / "fuel_trade_sars_by_office.csv"):
        if r["period"] == ENTRY_YEAR and r["flow"] == "import" and r["product"] in PRODUCTS:
            assert r["unit"] == "litres", r
            offices[r["district_office"]] += float(r["value"])
    entry_total = sum(offices.values())

    # All-liquids port tonnage (crude, fuels, gas, chemicals), kept beside the fuel-only customs
    # figures as a trend and port-share indicator; never used to size the fuel market.
    landed = {r["port"]: float(r["value"]) for r in read(SERIES / "port_liquid_bulk_tnpa.csv")
              if r["period"] == ENTRY_YEAR and r["movement"] == "landed" and r["period_basis"] == "calendar year"}
    assert all(r["unit"] == "tonnes" for r in read(SERIES / "port_liquid_bulk_tnpa.csv") if r["period"] == ENTRY_YEAR)

    coastal = sum(float(r["value"]) for r in provinces if r["province"] in COASTAL_PROVINCES)
    inland = sum(float(r["value"]) for r in provinces if r["province"] not in COASTAL_PROVINCES)
    sales = line(base, "sales_used")
    imports = line(base, "imports_used")

    volumes = {
        "consumption": {"year": BASE_YEAR, "billion_litres": sales["value"], "status": "observed",
                        "source": "DR01 balance file, department sales"},
        "petrol": {"year": BASE_YEAR, "billion_litres": sales["split"]["petrol"], "status": "observed"},
        "diesel": {"year": BASE_YEAR, "billion_litres": sales["split"]["diesel"], "status": "observed"},
        "imports": {"year": BASE_YEAR, "billion_litres": imports["value"], "status": "customs",
                    **imports["split"], "source": "DR01 balance file, SARS customs"},
        "exports": {"year": BASE_YEAR, "billion_litres": line(base, "exports_used")["value"], "status": "customs"},
        "production": {"year": PRODUCTION_YEAR, "billion_litres": line(production_year, "production_used")["value"],
                       "status": "last published", "source": "DR01 balance file, department energy balance"},
        "entry_points": {"year": ENTRY_YEAR, "billion_litres": billions(entry_total), "status": "customs",
                         "durban": billions(offices["Durban"]),
                         "durban_share_pct": round(100 * offices["Durban"] / entry_total),
                         "by_office": {k: billions(v) for k, v in sorted(offices.items(), key=lambda x: -x[1]) if v >= 1e8},
                         "source": "fuel_trade_sars_by_office.csv (DR04)"},
        "port_liquid_bulk": {"year": ENTRY_YEAR, "status": "all products, tonnes",
                             "landed_all_ports_mt": round(landed["All ports"] / 1e6, 1),
                             "landed_durban_mt": round(landed["Durban"] / 1e6, 1),
                             "durban_share_pct": round(100 * landed["Durban"] / landed["All ports"]),
                             "source": "port_liquid_bulk_tnpa.csv (registered; DR04)"},
        "demand_by_use": {"year": BALANCE_YEAR, "billion_litres": billions(sum(uses.values())), "status": "balance",
                          **{key: billions(value) for key, value in uses.items()},
                          "source": "energy_balance_department.csv final consumption; industry includes mining"},
        "coastal_demand": {"year": PROVINCE_YEAR, "billion_litres": billions(coastal), "status": "proxy",
                           "provinces": list(COASTAL_PROVINCES), "source": "fuel_sales_department_by_province.csv"},
        "inland_demand": {"year": PROVINCE_YEAR, "billion_litres": billions(inland), "status": "proxy",
                          "provinces": sorted({r["province"] for r in provinces} - set(COASTAL_PROVINCES)),
                          "source": "fuel_sales_department_by_province.csv"},
        "balance": national_balance(balance),
        "closure": closure(balance),
        "provinces": provinces_by_year(),
        "sector_use": sector_use(flow_total),
        "levers": demand_levers(),
    }
    OUTPUT.write_text(json.dumps(volumes, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in volumes.items() if k != "balance"}, indent=2))
    for row in volumes["balance"]:
        print(row["year"], {k: v["value"] for k, v in row.items() if isinstance(v, dict)})


if __name__ == "__main__":
    main()
