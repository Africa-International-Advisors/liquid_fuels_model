"""Check the figures on the market sizing pack against the registered inputs.

The pack takes its numbers from ``pptx/story/issue_tree_volumes_2026_10_08.json``,
written by ``pptx/scripts/issue_tree_volumes.py``. This recomputes each headline
figure from the inputs with its own code, compares it with the file, and looks
for it in the text of the latest pack. One row per figure:

    workstreams/WS3_reporting_delivery/issue_tree_figure_check_2026-10-09.csv

Columns: item, pack_value, recomputed, result, shown_in_pack, input_file. A
figure "matches" when it agrees to the one decimal the pack shows. The command
exits with an error if any figure differs.

Run:
    python -m lfm.scripts.check_issue_tree_figures --vintage 2026
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from lfm.config import Paths
from lfm.scripts import build_market_sizing as sizing

VOLUMES = Path("pptx/story/issue_tree_volumes_2026_10_08.json")
PACKS = Path("pptx/output/delivered/supporting")
BALANCE = Path("workstreams/WS1_data_validation/fuel_balance_petrol_diesel_2009_2025_2026-10-06.csv")
OUT = Path("workstreams/WS3_reporting_delivery/issue_tree_figure_check_2026-10-09.csv")
FIELDS = ["item", "pack_value", "recomputed", "result", "shown_in_pack", "input_file"]
COASTAL = ("KZN", "WC", "EC")
PRODUCTS = ("petrol", "diesel")


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def recompute(vintage: Path) -> list[tuple[str, tuple, float, str]]:
    """``(item, path into the volumes file, value in billion litres, input file)`` for each headline figure."""
    ts = vintage / "timeseries"
    balance = {(r["product"], r["period"]): r for r in _read(BALANCE)}

    def line(year, column):
        return sum(float(balance[(p, year)][column] or 0) for p in PRODUCTS) / 1e9

    province = {(r["province"], r["product"]): float(r["value"]) / 1e9 for r in _read(ts / "fuel_sales_department_by_province.csv")
                if r["period"] == "2022" and r["product"] in PRODUCTS}
    office: dict[str, float] = {}
    for r in _read(ts / "fuel_trade_sars_by_office.csv"):
        if r["flow"] == "import" and r["period"] == "2025" and r["product"] in PRODUCTS and r["unit"] == "litres":
            office[r["district_office"]] = office.get(r["district_office"], 0.0) + float(r["value"]) / 1e9
    use = {}
    for r in _read(ts / "energy_balance_department.csv"):
        if r["period"] == "2021" and r["product"] in PRODUCTS:
            use[r["flow_key"]] = use.get(r["flow_key"], 0.0) + float(r["value"]) / 1e9
    sized = {(r["site"], r["measure"]): float(r["value"]) for r in sizing.build(sizing.load(vintage)) if r["product"] in ("petrol and diesel", "all products")}
    b, o, e, s = str(BALANCE), "fuel_trade_sars_by_office.csv", "energy_balance_department.csv", "fuel_sales_department_by_province.csv"
    m = str(sizing.OUT)
    return [
        ("National consumption, 2023", ("consumption", "billion_litres"), line("2023", "sales_used"), b),
        ("Petrol sales, 2023", ("petrol", "billion_litres"), float(balance[("petrol", "2023")]["sales_used"]) / 1e9, b),
        ("Diesel sales, 2023", ("diesel", "billion_litres"), float(balance[("diesel", "2023")]["sales_used"]) / 1e9, b),
        ("Gross imports, 2023", ("imports", "billion_litres"), line("2023", "imports_used"), b),
        ("Petrol imports, 2023", ("imports", "petrol"), float(balance[("petrol", "2023")]["imports_used"]) / 1e9, b),
        ("Diesel imports, 2023", ("imports", "diesel"), float(balance[("diesel", "2023")]["imports_used"]) / 1e9, b),
        ("Exports, 2023", ("exports", "billion_litres"), line("2023", "exports_used"), b),
        ("Production, 2021", ("production", "billion_litres"), line("2021", "production_used"), b),
        ("Imports through every office, 2025", ("entry_points", "billion_litres"), sum(office.values()), o),
        ("Imports through Durban, 2025", ("entry_points", "durban"), office["Durban"], o),
        ("Durban share of imports, 2025 (%)", ("entry_points", "durban_share_pct"), office["Durban"] / sum(office.values()) * 100, o),
        ("Demand by use: road, 2021", ("demand_by_use", "road"), use["road"], e),
        ("Demand by use: agriculture, 2021", ("demand_by_use", "agriculture"), use["agriculture"], e),
        ("Demand by use: all uses, 2021", ("demand_by_use", "billion_litres"), use["final_consumption"], e),
        ("Coastal demand, 2022", ("coastal_demand", "billion_litres"), sum(v for (code, _), v in province.items() if code in COASTAL), s),
        ("Inland demand, 2022", ("inland_demand", "billion_litres"), sum(v for (code, _), v in province.items() if code not in COASTAL), s),
        ("Both Vopak sites, counted once", ("site_markets", "combined"), sized[("Durban and Lesedi", "Both sites, counted once")], m),
        ("Durban market, low", ("site_markets", "durban_coastal"), sized[("Durban", "Coastal catchment: KwaZulu-Natal sales")], m),
        ("Durban market, high", ("site_markets", "durban_landed"), sized[("Durban", "Landed at Durban")], m),
        ("Inland-bound through Durban", ("site_markets", "inland_bound"), sized[("Durban", "Inland-bound through Durban")], m),
        ("Lesedi market, low", ("site_markets", "lesedi_gauteng"), sized[("Lesedi", "Near catchment: Gauteng sales")], m),
        ("Lesedi market, high", ("site_markets", "lesedi_inland"), sized[("Lesedi", "Inland catchment: six inland provinces")], m),
        ("Durban tanks at two turns a month", ("site_markets", "durban_tanks_allow"), sized[("Durban", "Throughput the tanks allow at 2 turns a month")], m),
        ("Lesedi tanks at two turns a month", ("site_markets", "lesedi_tanks_allow"), sized[("Lesedi", "Throughput the tanks allow at 2 turns a month")], m),
    ]


def pack_text() -> tuple[str, str]:
    """Name and text of the most recently built pack; empty if none is found or it cannot be read."""
    packs = sorted(PACKS.glob("*Vopak_Market_Sizing_v*.pptx"), key=lambda p: p.stat().st_mtime)
    if not packs:
        return "", ""
    from pptx import Presentation

    text = []
    for slide in Presentation(str(packs[-1])).slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                text.append(shape.text_frame.text)
    return packs[-1].name, "\n".join(text)


def check(vintage: Path) -> list[dict]:
    volumes = json.loads(VOLUMES.read_text(encoding="utf-8"))
    pack, text = pack_text()
    rows = []
    for item, (block, key), value, source in recompute(vintage):
        shown = volumes[block][key]
        percent = item.endswith("(%)")
        same = round(value) == round(float(shown)) if percent else abs(value - float(shown)) < 0.051
        label = f"{round(value)}%" if percent else f"{value:.1f}B"
        rows.append({"item": item, "pack_value": shown, "recomputed": f"{value:.3f}", "result": "matches" if same else "DIFFERS",
                     "shown_in_pack": "no pack found" if not pack else ("yes" if label in text else "not shown as " + label), "input_file": source})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--vintage", required=True)
    args = parser.parse_args()
    rows = check(Paths.default().vintage_dir(args.vintage))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    wrong = [r["item"] for r in rows if r["result"] != "matches"]
    print(f"wrote {len(rows)} figures -> {OUT}; {len(rows) - len(wrong)} match" + (f"; DIFFER: {wrong}" if wrong else ""), file=sys.stderr)
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
