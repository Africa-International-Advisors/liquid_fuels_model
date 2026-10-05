"""Monthly→annual roll-up.

Default rule for v1:
  - volumes  : sum across the 12 months in the year
  - stocks   : end-of-period (December observation)        [not used in v1]
  - prices   : volume-weighted mean across the 12 months   [not used in v1]

Most demand series are flow-volumes, so ``aggregate_volumes`` is the hot path.
"""
from __future__ import annotations

import pandas as pd


def aggregate_volumes(monthly: pd.DataFrame, value_col: str = "volume") -> pd.DataFrame:
    """Sum a monthly long-format frame to annual.

    Expects columns ``[country, product, period, <value_col>]`` with ``period``
    a monthly ``Period``. Returns the same shape with ``period`` annual.
    """
    if monthly.empty:
        return monthly.copy()

    df = monthly.copy()
    df["year"] = df["period"].apply(lambda p: p.year)
    grouped = (
        df.groupby(["country", "product", "year"], as_index=False)[value_col].sum()
    )
    grouped = grouped.rename(columns={"year": "period"})
    return grouped[["country", "product", "period", value_col]]
