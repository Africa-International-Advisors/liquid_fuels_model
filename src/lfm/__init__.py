"""SACU liquid fuels supply-demand model.

This is the v1 rebuild of the Vopak/Reatile Excel model. Scope:
SACU (ZA, BW, LS, NA, SZ), monthly granularity to 2050, single
scenario for v1, annual xlsx as the consumer artifact.

The model consumes assumptions from a vintaged config directory
(``assumptions/<vintage>/``); that boundary is intentionally narrow
so the provider can later be swapped for the central assumptions repo
without touching model code.
"""

__version__ = "0.1.0"
