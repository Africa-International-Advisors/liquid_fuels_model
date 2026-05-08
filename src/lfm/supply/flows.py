"""Cross-border and refining-import flows.

BLNS demand is materially shaped by what crosses the SA border, not by
independent supply decisions. v1 holds this as a thin balancing layer:
country demand minus domestic refining (SA only) implies imports/exports.
Pipeline, road, and rail mode splits come later.
"""
from __future__ import annotations

import pandas as pd

from ..assumptions import AssumptionProvider
from ..run import Run


def compute_flows(demand: pd.DataFrame, provider: AssumptionProvider, run: Run) -> pd.DataFrame:
    """Balance demand against refining and imports. To be implemented."""
    return pd.DataFrame(
        columns=["origin", "destination", "product", "period", "volume", "mode"]
    )
