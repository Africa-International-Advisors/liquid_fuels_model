"""Road-transport liquid fuel demand. v1 status: MODELLED.

Bottom-up structure (to be implemented):
  1. New-vehicle demand per country, driven by GDP/capita (and population).
     The xlsx fits a single SA regression; SACU likely needs per-country
     coefficients pooled where data is thin.
  2. EV penetration share via a logistic (Boltzmann) S-curve per country.
     Parameters (max penetration, midpoint, slope) are scenario-tagged
     assumptions.
  3. Cumulative ICE vs EV stock, with scrappage applied (the xlsx omits
     scrappage; the rebuild adds it explicitly).
  4. Liquid-fuel demand = ICE stock × annual km × consumption, split by
     petrol/diesel mix per country.

Inputs come exclusively via the ``AssumptionProvider``. No numbers are
embedded in this module.
"""
from __future__ import annotations

import pandas as pd

from ..assumptions import AssumptionProvider
from ..run import Run
from .base import DemandResult, SegmentStatus

name = "vehicles"
status = SegmentStatus.MODELLED


def compute_demand(provider: AssumptionProvider, run: Run) -> DemandResult:
    frame = pd.DataFrame(columns=["country", "product", "period", "volume"])
    return DemandResult(segment=name, status=status, frame=frame)
