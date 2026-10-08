"""South Africa's monthly submissions to the JODI oil database (secondary products), totalled by year.

JODI publishes one file a year covering every reporting country:

    jodidata.org > Oil > Database > Data downloads > annual CSV, secondary

Each row is one country, month, product, flow and unit, with an assessment
code. Code 1 is JODI's best (comparable with other sources), 2 is "consult
metadata", 3 is its lowest (not comparable, or not assessed). Every South
African entry carries code 3.

Only the kilolitre rows are used: the file's ``KL`` unit is thousand
kilolitres, so a value is in million litres. Flows are added over the months
reported; the closing stock is the December level. Nothing is converted from
barrels or tonnes and no missing month is filled.
"""
from __future__ import annotations

import urllib.request

URL = "https://www.jodidata.org/_resources/files/downloads/oil-data/annual-csv/secondary/{year}.csv"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
COUNTRY = "ZA"

PRODUCTS = {"GASOLINE": "petrol", "GASDIES": "diesel", "JETKERO": "jet", "KEROSENE": "paraffin", "LPG": "lpg",
            "NAPHTHA": "naphtha", "RESFUEL": "fuel_oil", "ONONSPEC": "other_products", "TOTPRODS": "total_products"}
FLOWS = {"REFGROUT": "refinery_output", "RECEIPTS": "receipts", "TOTIMPSB": "imports", "TOTEXPSB": "exports",
         "PTRANSF": "products_transferred", "IPTRANSF": "interproduct_transfers", "STOCKCH": "stock_change",
         "STATDIFF": "statistical_difference", "TOTDEMO": "demand", "CLOSTLV": "closing_stock"}
LITRES_PER_UNIT = 1_000_000  # the file's "KL" is thousand kilolitres


def fetch_country_rows(year: int) -> str:
    """The header and South Africa's rows of JODI's annual file, as CSV text."""
    request = urllib.request.Request(URL.format(year=year), headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=300) as response:
        lines = response.read().decode("utf-8-sig").splitlines()
    return "\n".join([lines[0]] + [line for line in lines[1:] if line.startswith(COUNTRY + ",")]) + "\n"


def annual(rows: list[dict]) -> list[dict]:
    """One row per year, product and flow, in litres, from JODI's monthly rows.

    ``months_reported`` counts the months with a number; a year with fewer than
    twelve is still written, so the reader can see it is partial.
    """
    total: dict[tuple, float] = {}
    months: dict[tuple, set] = {}
    code: dict[tuple, str] = {}
    december: dict[tuple, float] = {}
    for row in rows:
        if row["REF_AREA"] != COUNTRY or row["UNIT_MEASURE"] != "KL":
            continue
        if row["ENERGY_PRODUCT"] not in PRODUCTS or row["FLOW_BREAKDOWN"] not in FLOWS:
            continue
        try:
            value = float(row["OBS_VALUE"])
        except ValueError:
            continue
        year, month = row["TIME_PERIOD"].split("-")
        key = (int(year), PRODUCTS[row["ENERGY_PRODUCT"]], FLOWS[row["FLOW_BREAKDOWN"]])
        total[key] = total.get(key, 0.0) + value
        months.setdefault(key, set()).add(month)
        code[key] = max(code.get(key, ""), row["ASSESSMENT_CODE"])
        if month == "12":
            december[key] = value
    out = []
    for key in sorted(total):
        year, product, flow = key
        if flow == "closing_stock":
            if key not in december:
                continue
            value, basis = december[key], "level at end of December"
        else:
            value, basis = total[key], "sum of months reported"
        out.append({"country": "ZAF", "period": year, "scenario": "shared", "product": product, "flow": flow,
                    "value": round(value * LITRES_PER_UNIT), "unit": "litres", "basis": basis,
                    "months_reported": len(months[key]), "assessment_code": code[key]})
    return out
