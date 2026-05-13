"""Supply-side compute: refineries → product output, plus demand-supply balance.

v1 scope: VOLUMES ONLY. Pricing (crude cost, refined wholesale, import parity,
retail BFP) is explicitly deferred — see docs/demand_hypothesis_tree.md
Section 8.

Supply compute path, per (refinery, year, scenario):
    effective_kbpd = nameplate_kbpd × utilisation(refinery, year, scenario) × availability
    annual_barrels = effective_kbpd × 365 × 1000
    annual_litres  = annual_barrels × crude_oil_litres_per_barrel
    per_product    = annual_litres × product_mix[refinery][product]

Then sum across refineries → country supply per product per year.

Balance: demand-products are aggregated to refinery-products before
differencing (petrol_95 + petrol_93 → gasoline; diesel_50ppm + diesel_500ppm
→ diesel; jet_a1 → jet_a1). Products with no refinery yield (fuel_oil, LPG,
paraffin) appear in the balance with supply=0 (i.e., fully imported).
"""
from __future__ import annotations

import pandas as pd

from ..assumptions import AssumptionProvider
from ..core.time import END_YEAR, START_YEAR
from ..run import Run


# How demand-side product codes roll up to refinery-side product yields.
DEMAND_TO_REFINERY_PRODUCT = {
    "petrol_95":     "gasoline",
    "petrol_93":     "gasoline",
    "diesel_50ppm":  "diesel",
    "diesel_500ppm": "diesel",
    "jet_a1":        "jet_a1",
    # Products with no domestic refinery yield in v1: fuel_oil, lpg, ip.
}

REFINERY_PRODUCTS = ("gasoline", "diesel", "jet_a1")

DAYS_PER_YEAR = 365
KBPD_TO_BPD = 1000


def compute_supply(provider: AssumptionProvider, run: Run) -> pd.DataFrame:
    """Return long-format country × refinery_product × year supply (litres).

    For BLNS (no refineries in v1), this contributes nothing — supply is
    ZAF-only until refining outside SA is added.
    """
    cap_block = provider.get("supply", "refinery_capacity", run).value or {}
    mix_block = provider.get("supply", "refinery_product_mix", run).value or {}
    util_df = provider.get("supply", "refinery_utilisation", run).value
    availability = provider.get("supply", "refinery_availability", run).value
    litres_per_barrel = provider.get("macro", "crude_oil_litres_per_barrel", run).value

    if (
        not isinstance(util_df, pd.DataFrame) or util_df.empty
        or availability is None or litres_per_barrel is None
    ):
        return _empty_supply_frame()

    records: list[dict] = []
    for iso3, refineries in cap_block.items():
        if not isinstance(refineries, dict):
            continue
        mixes = mix_block.get(iso3) or {}
        for refinery_name, kbpd in refineries.items():
            if kbpd is None:
                continue
            mix = mixes.get(refinery_name) or {}
            utilisation = _utilisation_series(util_df, iso3, refinery_name)
            if utilisation.empty:
                continue
            for year in range(START_YEAR, END_YEAR + 1):
                u = utilisation.get(year)
                if u is None or pd.isna(u):
                    continue
                effective_kbpd = float(kbpd) * float(u) * float(availability)
                if effective_kbpd <= 0:
                    continue
                annual_litres = (
                    effective_kbpd * KBPD_TO_BPD * DAYS_PER_YEAR
                    * float(litres_per_barrel)
                )
                for product in REFINERY_PRODUCTS:
                    share = mix.get(product)
                    if share is None or share == 0:
                        continue
                    records.append({
                        "country": iso3,
                        "refinery_product": product,
                        "period": year,
                        "supply_litres": annual_litres * float(share),
                    })

    if not records:
        return _empty_supply_frame()

    df = pd.DataFrame(records)
    # Sum across refineries to get country totals per product per year.
    return df.groupby(
        ["country", "refinery_product", "period"], as_index=False,
    )["supply_litres"].sum()


def compute_balance(
    demand_long: pd.DataFrame, supply_annual: pd.DataFrame,
) -> pd.DataFrame:
    """Demand-supply balance per (country × refinery_product × year).

    Inputs:
      - demand_long: monthly long-format frame with columns
                     [country, product, period, volume]
      - supply_annual: output of compute_supply (litres, annual)

    Output columns:
      country, refinery_product, period (year), demand_litres,
      supply_litres, deficit_litres.

    Conventions:
      - deficit > 0  →  imports needed
      - deficit < 0  →  surplus (exports / inventory build)
      - Demand products with no refinery yield (fuel_oil, LPG, paraffin)
        show up with supply_litres = 0 — i.e., 100% imported.
    """
    # Roll up demand: monthly → annual, demand-product → refinery-product.
    if demand_long.empty:
        return pd.DataFrame(columns=[
            "country", "refinery_product", "period",
            "demand_litres", "supply_litres", "deficit_litres",
        ])

    d = demand_long.copy()
    d["year"] = d["period"].apply(lambda p: p.year if hasattr(p, "year") else int(p))
    d["refinery_product"] = d["product"].map(
        lambda p: DEMAND_TO_REFINERY_PRODUCT.get(p, p),
    )
    annual_demand = (
        d.groupby(["country", "refinery_product", "year"], as_index=False)["volume"]
         .sum()
         .rename(columns={"year": "period", "volume": "demand_litres"})
    )

    # Outer-join with supply: keep every demand-product line, fill missing
    # supply with zero (so e.g. fuel_oil shows up as 100% imports).
    s = (supply_annual.rename(columns={})
         if not supply_annual.empty
         else _empty_supply_frame())

    merged = annual_demand.merge(
        s, on=["country", "refinery_product", "period"], how="outer",
    )
    merged["demand_litres"] = merged["demand_litres"].fillna(0.0)
    merged["supply_litres"] = merged["supply_litres"].fillna(0.0)
    merged["deficit_litres"] = merged["demand_litres"] - merged["supply_litres"]

    return merged[[
        "country", "refinery_product", "period",
        "demand_litres", "supply_litres", "deficit_litres",
    ]].sort_values(["country", "refinery_product", "period"]).reset_index(drop=True)


# --------------------------------------------------------------------------- #

def _utilisation_series(df: pd.DataFrame, iso3: str, refinery_name: str) -> pd.Series:
    """Refinery utilisation indexed by year, for a specific country×refinery×scenario.

    The utilisation CSV encodes refinery in the `country` column as
    ``"<ISO3>:<refinery_name>"``.
    """
    key = f"{iso3}:{refinery_name}"
    sub = df[df["country"] == key].copy()
    if sub.empty:
        return pd.Series(dtype=float)
    sub["period"] = sub["period"].astype(int)
    # The provider has already filtered by run.scenario; deduplicate just in case.
    return sub.groupby("period")["value"].first().astype(float).sort_index()


def _empty_supply_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=["country", "refinery_product", "period", "supply_litres"])
