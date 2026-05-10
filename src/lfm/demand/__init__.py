"""Demand segments.

v1 status by segment:
  - vehicles    : MODELLED (S-curve EV penetration + GDP-driven new-vehicle demand)
  - aviation    : MODELLED (xlsx 2-var jet regression on GDP/capita + pax)
  - generation  : MODELLED (OCGT capacity x load factor / efficiency -> diesel)
  - industrial  : HELD     (driver-tied growth from history)
  - marine      : HELD     (driver-tied growth from history)
  - agriculture : DEFERRED (stub only)

All segments expose the same ``compute_demand`` signature so the engine
can iterate them uniformly.
"""
from .base import DemandResult, DemandSegment, SegmentStatus
