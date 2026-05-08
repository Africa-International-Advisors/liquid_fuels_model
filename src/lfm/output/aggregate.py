"""Monthly→annual roll-up.

Default rule for v1:
  - volumes  : sum across the 12 months in the year
  - stocks   : end-of-period (December observation)
  - prices   : volume-weighted mean across the 12 months

Most demand series are flow-volumes, so ``aggregate_volumes`` is the hot path.
"""
from __future__ import annotations

import pandas as pd


def aggregate_volumes(monthly: pd.DataFrame, value_col: str = "volume") -> pd.DataFrame:
    """Sum a monthly long-format frame to annual. To be implemented.

    Expects columns ``[country, product, period, <value_col>]`` with ``period``
    a monthly ``Period``. Returns the same shape with ``period`` annual.
    """
    raise NotImplementedError("annual roll-up to be implemented in v1 build-out")
