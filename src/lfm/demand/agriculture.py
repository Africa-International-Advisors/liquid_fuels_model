"""Agricultural diesel demand. v1 status: DEFERRED.

Returns an empty frame. Smaller absolute volumes than industrial, but
distinct seasonality (planting/harvest) and policy treatment (rebates).
Worth its own segment when the team is ready to model it.
"""
from __future__ import annotations

import pandas as pd

from ..assumptions import AssumptionProvider
from ..run import Run
from .base import DemandResult, SegmentStatus

name = "agriculture"
status = SegmentStatus.DEFERRED


def compute_demand(provider: AssumptionProvider, run: Run) -> DemandResult:
    frame = pd.DataFrame(columns=["country", "product", "period", "volume"])
    return DemandResult(segment=name, status=status, frame=frame)
