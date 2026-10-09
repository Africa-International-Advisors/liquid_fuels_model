"""Size the market each Vopak site can reach, from public data only.

Writes one row per site, product and measure:

    workstreams/WS2_model_development/market_sizing_durban_lesedi_2026-10-09.csv

Method (billion litres a year, petrol and diesel):

    Durban
      landed at Durban            imports cleared at the Durban customs office (observed)
      coastal catchment           KwaZulu-Natal sales (observed)
      inland-bound                landed at Durban less the coastal catchment (estimated)
    Lesedi
      near catchment              Gauteng sales (observed)
      inland catchment            sales in the six inland provinces (observed)
      inland-bound through Durban the same flow as Durban's inland-bound line (estimated)
    Combined
      both sites, counted once    landed at Durban: every litre Lesedi receives by pipeline landed there first

Capacity lines turn each site's tanks into a yearly throughput at the turns
registered in ``infrastructure/terminal_site_assumptions.csv``. Those turns
are analyst estimates, not client data, so the lines are ceilings on share,
not shares. No client throughput is assumed anywhere.

Every row is labelled observed, estimated or assumed and names its inputs.

Run:
    python -m lfm.scripts.build_market_sizing --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from lfm.config import Paths

OUT = Path("workstreams/WS2_model_development/market_sizing_durban_lesedi_2026-10-09.csv")
FIELDS = ["site", "product", "measure", "value", "unit", "period", "status", "inputs", "source", "note"]
PRODUCTS = ("petrol", "diesel")
COASTAL_CATCHMENT = ("KZN",)                                     # Durban's own province
INLAND = ("GP", "MP", "FS", "NW", "LP", "NC")
TRADE_YEAR, SALES_YEAR = 2025, 2022                              # latest full customs year; last year of provincial sales as published
TRUNK_LINE_M3_PER_WEEK = 148_000                                 # Transnet Pipelines: capacity, unchanged from 2020 to the year to March 2024
TRUNK_LINE_USED_M3_PER_WEEK = 97_000                             # Transnet Pipelines Report 2024: use in the year to March 2024
CUSTOMS = "SARS customs, imports by office of clearance (fuel_trade_sars_by_office.csv)"
PROVINCES = "Department of Mineral and Petroleum Resources, sales by magisterial district added up by province"
SITES = "infrastructure/terminal_site_assumptions.csv (NERSA licence, Vopak statements and analyst estimates, each marked)"


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load(vintage: Path) -> dict:
    ts = vintage / "timeseries"
    d: dict = {"landed": {}, "sales": {}, "site": {}}
    for r in _read(ts / "fuel_trade_sars_by_office.csv"):
        if r["flow"] == "import" and r["unit"] == "litres" and int(r["period"]) == TRADE_YEAR and r["product"] in PRODUCTS:
            key = (r["district_office"], r["product"])
            d["landed"][key] = d["landed"].get(key, 0.0) + float(r["value"]) / 1e9
    for r in _read(ts / "fuel_sales_department_by_province.csv"):
        if int(r["period"]) == SALES_YEAR and r["product"] in PRODUCTS:
            d["sales"][(r["province"], r["product"])] = float(r["value"]) / 1e9
    for r in _read(vintage / "infrastructure" / "terminal_site_assumptions.csv"):
        d["site"].setdefault((r["site"], r["parameter"]), []).append(r)
    return d


def operational_m3(d: dict, site: str) -> float:
    return sum(float(r["value"]) for r in d["site"][(site, "operational_capacity")])


def turns(d: dict, site: str, case: str) -> float:
    rows = d["site"].get((site, f"monthly_turns_{case}"))
    return float(rows[0]["value"]) if rows else float("nan")


def build(d: dict) -> list[dict]:
    rows: list[dict] = []

    def add(site, product, measure, value, period, status, inputs, source, note="", unit="billion litres a year"):
        rows.append(dict(site=site, product=product, measure=measure, value=f"{value:.3f}", unit=unit, period=period, status=status, inputs=inputs,
                         source=source, note=note))

    def by_product(function):
        values = {p: function(p) for p in PRODUCTS}
        return {**values, "petrol and diesel": sum(values.values())}

    landed = by_product(lambda p: d["landed"].get(("Durban", p), 0.0))
    national = by_product(lambda p: sum(v for (_, pr), v in d["landed"].items() if pr == p))
    coastal = by_product(lambda p: sum(d["sales"][(c, p)] for c in COASTAL_CATCHMENT))
    gauteng = by_product(lambda p: d["sales"][("GP", p)])
    inland = by_product(lambda p: sum(d["sales"][(c, p)] for c in INLAND))
    trunk = TRUNK_LINE_M3_PER_WEEK * 52 * 1000 / 1e9
    mixed = f"{TRADE_YEAR} imports, {SALES_YEAR} sales"
    for product in (*PRODUCTS, "petrol and diesel"):
        onward = landed[product] - coastal[product]
        add("Durban", product, "Landed at Durban", landed[product], str(TRADE_YEAR), "observed", "imports cleared at the Durban customs office", CUSTOMS,
            f"{landed[product] / national[product] * 100:.0f}% of the {national[product]:.2f} imported through every office. The most any Durban terminal can handle.")
        add("Durban", product, "Coastal catchment: KwaZulu-Natal sales", coastal[product], str(SALES_YEAR), "observed", "KwaZulu-Natal sales", PROVINCES,
            "Assumes KwaZulu-Natal is supplied from Durban, as both Durban refineries have stopped refining (DR08). The lower end of the Durban market.")
        add("Durban", product, "Inland-bound through Durban", onward, mixed, "estimated", "landed at Durban less KwaZulu-Natal sales", f"{CUSTOMS}; {PROVINCES}",
            "Mixes two years, and ignores coastwise shipments and exports by road from KwaZulu-Natal.")
        add("Lesedi", product, "Near catchment: Gauteng sales", gauteng[product], str(SALES_YEAR), "observed", "Gauteng sales", PROVINCES,
            "The market on Lesedi's doorstep. Part of it is supplied by Natref and Secunda, whose output by product is not published after 2021.")
        add("Lesedi", product, "Inland catchment: six inland provinces", inland[product], str(SALES_YEAR), "observed",
            "sales in Gauteng, Mpumalanga, Free State, North West, Limpopo and Northern Cape", PROVINCES, "The upper end: everything sold inland, whoever supplies it.")
        add("Lesedi", product, "Inland-bound through Durban", onward, mixed, "estimated", "the Durban line of the same name", f"{CUSTOMS}; {PROVINCES}",
            "The imported fuel that moves inland, by pipeline, road or rail. Lesedi receives by pipeline only.")
        add("Durban and Lesedi", product, "Both sites, counted once", landed[product], str(TRADE_YEAR), "observed", "landed at Durban", CUSTOMS,
            "Every litre Lesedi receives by pipeline landed at Durban first, so the two site markets are not added together.")
    both = "petrol and diesel"
    used = TRUNK_LINE_USED_M3_PER_WEEK * 52 * 1000 / 1e9
    add("Durban and Lesedi", "all products", "Trunk line capacity, Durban to Jameson Park", trunk, "years to March 2021 to 2024", "observed", "148,000 m3 a week x 52",
        "Transnet Pipelines Report 2024, key performance indicators", "Every shipper and refined product. Unchanged from the 2020 figure.")
    add("Durban and Lesedi", "all products", "Trunk line use, Durban to Jameson Park", used, "year to March 2024", "observed", "97,000 m3 a week x 52",
        "Transnet Pipelines Report 2024, key performance indicators", "About two thirds of capacity. Not split by product.")
    add("Durban and Lesedi", both, "Inland-bound fuel beyond the trunk line's capacity", landed[both] - coastal[both] - trunk, mixed, "estimated",
        "inland-bound through Durban less trunk line capacity", "Calculated from the rows above",
        "At least this much must leave Durban by road or rail even with the line full.")
    add("Durban and Lesedi", both, "Inland-bound fuel beyond what the trunk line carried", landed[both] - coastal[both] - used, f"{mixed}, pipeline year to March 2024",
        "estimated", "inland-bound through Durban less trunk line use", "Calculated from the rows above",
        "The fuel that left Durban for the interior by road or rail, on these figures. Mixes three periods, so read as an order of size.")
    for site in ("Vopak Durban", "Vopak Lesedi"):
        short = site.replace("Vopak ", "")
        tanks = operational_m3(d, site)
        add(short, both, "Operational tank capacity", tanks / 1e6, "2026", "estimated" if short == "Durban" else "observed", "sum of the site's operational capacity rows",
            SITES, "Durban is 90% of the design capacity Vopak announced; Lesedi is from the licence, with two new tanks estimated.", unit="million m3")
        market = landed[both] if short == "Durban" else landed[both] - coastal[both]
        for case in ("low", "base", "high"):
            t = turns(d, site, case)
            if t != t:                                               # no such case registered for this site
                continue
            volume = tanks * t * 12 * 1000 / 1e9
            add(short, both, f"Throughput the tanks allow at {t:g} turns a month", volume, "assumed turns", "assumed", "operational tank capacity x turns x 12", SITES,
                f"A ceiling, not a share: {volume / market * 100:.0f}% of the site's market of {market:.1f}. The turns are analyst estimates; actual throughput needs "
                "the client (DR02/05).")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    args = parser.parse_args()
    rows = build(load(Paths.default().vintage_dir(args.vintage)))
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows -> {OUT}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
