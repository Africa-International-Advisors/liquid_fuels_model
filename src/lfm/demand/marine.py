"""Marine bunkering. v1 status: HELD.

SACU coastal volumes (Durban, Cape Town, Saldanha, Walvis Bay) are
non-trivial. Lesotho/Eswatini/Botswana naturally absent.

Approach (to be implemented):
  - Anchor on observed bunkering volumes per port.
  - Driver tie: trade volumes through the port (TEUs / dwt-throughput).
  - Watch for IMO sulphur-cap composition shifts (fuel oil → marine gasoil)
    when this graduates to MODELLED.
"""
from __future__ import annotations

import pandas as pd

from ..assumptions import AssumptionProvider
from ..run import Run
from .base import DemandResult, SegmentStatus

name = "marine"
status = SegmentStatus.HELD


def compute_demand(provider: AssumptionProvider, run: Run) -> DemandResult:
    frame = pd.DataFrame(columns=["country", "product", "period", "volume"])
    return DemandResult(segment=name, status=status, frame=frame)
