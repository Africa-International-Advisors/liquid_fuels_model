"""Jet A1 demand for SACU airports. v1 status: MODELLED (ZAF only).

Compute is the xlsx's two-variable regression:
    JetFuel(t) = intercept + b_gdp_pc * GDP_per_capita(t) + b_pax * PassengerDepartures(t)

Coefficients live in ``aviation.yaml::regression``; drivers come from
``macro.yaml::gdp_per_capita`` (scenario-keyed) and
``aviation.yaml::passenger_departures`` (shared — observed history stitched
with PaxBaseScenario forecast in the extraction step).

For ZAF the regression has R^2 = 0.946 on the xlsx fit, so historical
reproduction should be tight. For BLNS the regression has no coefficients
yet and the segment yields nothing for those countries.

Marine bunkering at coastal airports is handled in ``marine``, not here.
"""
from __future__ import annotations

import pandas as pd

from ..assumptions import AssumptionProvider
from ..core.geography import ISO3_LIST
from ..core.time import END_YEAR, START_YEAR, ExpansionRule, expand_annual_to_monthly
from ..run import Run
from .base import DemandResult, SegmentStatus

name = "aviation"
status = SegmentStatus.MODELLED


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
    """Annual jet_a1 volume for ``iso3`` from ``start_year`` to END_YEAR.

    Returns None for countries whose regression coefficients are unset
    (BLNS in v1).
    """
    reg_dict = provider.get("aviation", "regression", run).value
    reg = reg_dict.get(iso3)
    if reg is None or reg.get("intercept") is None:
        return None
    intercept = float(reg["intercept"])
    b_gdp = float(reg["coefficients"]["gdp_per_capita"])
    b_pax = float(reg["coefficients"]["passenger_departures"])

    gdp_pc = _series_by_year(provider.get("macro", "gdp_per_capita", run).value, iso3)
    pax = _series_by_year(provider.get("aviation", "passenger_departures", run).value, iso3)
    if gdp_pc.empty or pax.empty:
        return None

    records: list[dict] = []
    for year in range(start_year, END_YEAR + 1):
        g = gdp_pc.get(year)
        p = pax.get(year)
        if g is None or p is None or pd.isna(g) or pd.isna(p):
            continue
        jet = intercept + b_gdp * g + b_pax * p
        # Negative regression output is non-physical — clamp to zero.
        records.append({"year": year, "jet_a1": max(0.0, jet)})

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
        annual["jet_a1"].values,
        index=pd.PeriodIndex([str(y) for y in annual.index], freq="Y"),
        name="volume",
    )
    monthly = expand_annual_to_monthly(annual_series, rule) / 12.0
    return pd.DataFrame({
        "country": iso3,
        "product": "jet_a1",
        "period": monthly.index,
        "volume": monthly.values,
    })
