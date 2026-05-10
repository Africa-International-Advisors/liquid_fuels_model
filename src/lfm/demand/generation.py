"""Power-generation backup diesel (Eskom OCGT, IPPs). v1 status: HELD (ZAF only).

Sectoral compute:
    elec_MWh   = sum(capacity_MW) * 24 * operational_days * load_factor(year, scenario)
    fuel_MWh   = elec_MWh / efficiency
    fuel_MJ    = fuel_MWh * 3600                       # 1 MWh = 3600 MJ
    diesel_L   = fuel_MJ / mj_per_litre

v1 SIMPLIFICATIONS (worth flagging):

  - Operational fleet is hard-coded to the four existing SA OCGT stations
    (Ankerlig, Gourikwa, Avon, Dedisa = 3072 MW total). "New 1" (1000 MW)
    and "New 2" (2000 MW) are listed in the YAML as notional future capacity
    but excluded here — they have no commissioning year and treating them as
    operational from day one would substantially overstate diesel demand.
    A future enhancement is to add `commissioning_year` per station and
    include capacity in the year it comes online.

  - The xlsx's `LoadShedding_*` named ranges (loaded into
    `generation.yaml::load_shedding`) are NOT used in v1. Their units in
    the xlsx are unclear (column header says "EAF" but values diverge
    sharply between scenarios), and the `load_factor` series already
    captures dispatched OCGT generation. Investigation queued.

  - Scenario→named-range mapping is taken from `_meta.yaml::xlsx_scenario_mapping`.
    Whether `high_demand` should be paired with `PowerGenLoadFactor_High`
    (high EAF / less load shedding / less OCGT use) or `PowerGenLoadFactor_Low`
    (low EAF / more load shedding / more OCGT use) is a real judgment call
    about what the high_demand worldview means for grid availability.
    Current mapping: `high_demand → PowerGenLoadFactor_High`. Worth checking
    once a complete scenario narrative is locked.
"""
from __future__ import annotations

import pandas as pd

from ..assumptions import AssumptionProvider
from ..core.geography import ISO3_LIST
from ..core.time import END_YEAR, START_YEAR, ExpansionRule, expand_annual_to_monthly
from ..run import Run
from .base import DemandResult, SegmentStatus

name = "generation"
status = SegmentStatus.HELD

# v1 fleet definition: existing SA OCGT stations only.
OPERATIONAL_STATIONS_ZAF = ("ankerlig", "gourikwa", "avon", "dedisa")

HOURS_PER_DAY = 24
MWH_TO_MJ = 3600  # 1 MWh = 3600 MJ


def compute_demand(provider: AssumptionProvider, run: Run) -> DemandResult:
    monthly_frames: list[pd.DataFrame] = []

    for iso3 in ISO3_LIST:
        annual = compute_country_annual(provider, run, iso3)
        if annual is None or annual.empty:
            continue
        monthly_frames.append(_to_monthly_long(annual, iso3))

    if not monthly_frames:
        frame = pd.DataFrame(columns=["country", "product", "period", "volume"])
    else:
        frame = pd.concat(monthly_frames, ignore_index=True)

    return DemandResult(segment=name, status=status, frame=frame)


def compute_country_annual(
    provider: AssumptionProvider, run: Run, iso3: str, *,
    start_year: int = START_YEAR,
) -> pd.DataFrame | None:
    """Annual diesel volume for ``iso3`` from ``start_year`` to END_YEAR.

    Returns None when the country has no OCGT capacity or efficiency set
    (BLNS in v1).
    """
    cap_block = provider.get("generation", "ocgt_capacity", run).value.get(iso3)
    if not cap_block or not cap_block.get("stations"):
        return None
    stations: dict = cap_block["stations"]

    if iso3 == "ZAF":
        operational_names = OPERATIONAL_STATIONS_ZAF
    else:
        # BLNS not supported in v1; if ever wired, every named station counts.
        operational_names = tuple(stations.keys())
    total_mw = sum(
        v for k, v in stations.items()
        if k in operational_names and isinstance(v, (int, float))
    )
    if total_mw <= 0:
        return None

    efficiency = provider.get("generation", "efficiency", run).value.get(iso3)
    mj_per_litre = provider.get("generation", "mj_per_litre", run).value
    operational_days = provider.get("generation", "operational_days", run).value

    if efficiency is None or mj_per_litre is None or operational_days is None:
        return None

    lf_df = provider.get("generation", "load_factor", run).value
    lf = _series_by_year(lf_df, iso3)
    if lf.empty:
        return None

    records: list[dict] = []
    for year in range(start_year, END_YEAR + 1):
        load_factor = lf.get(year)
        if load_factor is None or pd.isna(load_factor):
            continue
        elec_mwh = total_mw * HOURS_PER_DAY * operational_days * float(load_factor)
        fuel_mwh = elec_mwh / float(efficiency)
        fuel_mj = fuel_mwh * MWH_TO_MJ
        diesel_litres = fuel_mj / float(mj_per_litre)
        records.append({"year": year, "diesel_50ppm": diesel_litres})

    if not records:
        return None
    return pd.DataFrame(records).set_index("year")


# --------------------------------------------------------------------------- #

def _series_by_year(df: pd.DataFrame, iso3: str) -> pd.Series:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.Series(dtype=float)
    sub = df[df["country"] == iso3].copy()
    if sub.empty:
        return pd.Series(dtype=float)
    sub["period"] = sub["period"].astype(int)
    return sub.set_index("period")["value"].astype(float).sort_index()


def _to_monthly_long(annual: pd.DataFrame, iso3: str) -> pd.DataFrame:
    rule = ExpansionRule(kind="flat")
    annual_series = pd.Series(
        annual["diesel_50ppm"].values,
        index=pd.PeriodIndex([str(y) for y in annual.index], freq="Y"),
        name="volume",
    )
    monthly = expand_annual_to_monthly(annual_series, rule) / 12.0
    return pd.DataFrame({
        "country": iso3,
        "product": "diesel_50ppm",
        "period": monthly.index,
        "volume": monthly.values,
    })
