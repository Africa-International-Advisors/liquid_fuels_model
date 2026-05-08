"""Industrial / mining diesel demand. v1 status: HELD.

Approach (to be implemented):
  - Anchor on most recent observed industrial diesel consumption per country.
  - Apply a driver-tied growth path (e.g. industrial GDP, mining GVA) drawn
    from assumptions.
  - Apply a per-country×month seasonal index (mining maintenance, agri spillover).

When this segment graduates to MODELLED, replace this module with bottom-up
mining-fleet and industrial-process detail.
"""
from __future__ import annotations

import pandas as pd

from ..assumptions import AssumptionProvider
from ..run import Run
from .base import DemandResult, SegmentStatus

name = "industrial"
status = SegmentStatus.HELD


def compute_demand(provider: AssumptionProvider, run: Run) -> DemandResult:
    frame = pd.DataFrame(columns=["country", "product", "period", "volume"])
    return DemandResult(segment=name, status=status, frame=frame)
