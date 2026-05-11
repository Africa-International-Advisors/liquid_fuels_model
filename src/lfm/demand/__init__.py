"""Demand segments.

v1 status by segment:
  - vehicles    : MODELLED (S-curve EV penetration + GDP-driven new-vehicle demand)
  - aviation    : MODELLED (xlsx 2-var jet regression on GDP/capita + pax)
  - generation  : MODELLED (OCGT capacity x load factor / efficiency -> diesel)
  - industrial  : HELD     (base-year x GDP-ratio^elasticity)
  - marine      : HELD     (per-port base x GDP-ratio^elasticity, summed by country)
  - agriculture : HELD     (base-year x GDP-ratio^elasticity, low elasticity)

All segments expose the same ``compute_demand`` signature so the engine
can iterate them uniformly.
"""
from .base import DemandResult, DemandSegment, SegmentStatus
