"""Common contract every demand segment honors.

A segment is a callable that takes ``(provider, run)`` and returns a
long-format DataFrame keyed on ``[country, product, period]`` with a
``volume`` column (in litres unless declared otherwise). The engine
concatenates segment outputs into the model-wide demand table.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

import pandas as pd

from ..assumptions import AssumptionProvider
from ..run import Run


class SegmentStatus(str, Enum):
    """How completely the segment is implemented in the active model version."""
    MODELLED = "modelled"      # full bottom-up logic
    HELD = "held"              # driver-tied growth from history
    DEFERRED = "deferred"      # stub returning empty/zero — explicit non-coverage


@dataclass(frozen=True)
class DemandResult:
    """Output of one segment for one run."""
    segment: str
    status: SegmentStatus
    frame: pd.DataFrame  # columns: country, product, period, volume[, units]


class DemandSegment(Protocol):
    name: str
    status: SegmentStatus

    def compute_demand(
        self, provider: AssumptionProvider, run: Run
    ) -> DemandResult: ...
