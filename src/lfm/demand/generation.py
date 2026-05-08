"""Power-generation backup diesel (Eskom OCGT, IPPs). v1 status: HELD (ZAF only).

The xlsx already models OCGT diesel demand explicitly; this segment ports
that compute. Approach (to be implemented):

    diesel_litres = sum_over_stations(capacity_MW)
                  * 24 * operational_days
                  * load_factor(year, scenario)
                  / efficiency
                  * (1000 / mj_per_litre)        # GWh -> MJ -> litres

Plus the load-shedding-driven OCGT term where applicable. All inputs come
from `generation.yaml`.

For BLNS this is small or zero — leave null in the YAML until a use case
comes up.
"""
from __future__ import annotations

import pandas as pd

from ..assumptions import AssumptionProvider
from ..run import Run
from .base import DemandResult, SegmentStatus

name = "generation"
status = SegmentStatus.HELD


def compute_demand(provider: AssumptionProvider, run: Run) -> DemandResult:
    frame = pd.DataFrame(columns=["country", "product", "period", "volume"])
    return DemandResult(segment=name, status=status, frame=frame)
