"""Jet A1 demand for SACU airports. v1 status: MODELLED (ZAF only).

Approach (to be implemented):
  - For ZAF: apply the xlsx's two-variable regression
        JetFuel = b_intercept + b_gdp_pc * GDP_per_capita + b_pax * PassengerDepartures
    Coefficients live in `aviation.yaml::regression`; drivers come from
    `macro.yaml::gdp_per_capita` (scenario-keyed) and
    `aviation.yaml::passenger_departures`.
  - For BLNS: regression coefficients are unset; segment falls back to
    HELD-style driver-tied growth from base-year volumes once those
    are sourced (TBD).

Marine bunkering at coastal airports is handled in ``marine``, not here.
"""
from __future__ import annotations

import pandas as pd

from ..assumptions import AssumptionProvider
from ..run import Run
from .base import DemandResult, SegmentStatus

name = "aviation"
status = SegmentStatus.MODELLED


def compute_demand(provider: AssumptionProvider, run: Run) -> DemandResult:
    frame = pd.DataFrame(columns=["country", "product", "period", "volume"])
    return DemandResult(segment=name, status=status, frame=frame)
