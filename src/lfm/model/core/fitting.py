"""Proportional fitting: scale a table so its rows and columns match known totals.

Used where the totals are verified but the breakdown is not — for example,
the official count of petrol and diesel vehicles (column totals) and the
official count of vehicles by class (row totals), with only an older
published table saying how the two cross. The older table supplies the
pattern; the totals supply the level. Nothing else is assumed.
"""
from __future__ import annotations


def proportional_fit(
    pattern: list[list[float]],
    row_totals: list[float],
    column_totals: list[float],
    *,
    tolerance: float = 1e-9,
    max_rounds: int = 1000,
) -> list[list[float]]:
    """Scale ``pattern`` until row and column sums equal the given totals.

    Rows and columns are scaled in turn (iterative proportional fitting) until
    every sum is within ``tolerance`` of its target, as a fraction of the
    target. A cell that is zero in the pattern stays zero.

    Raises ``ValueError`` if the row totals and column totals do not add up to
    the same grand total, if the pattern cannot reach a target (an all-zero
    row or column with a positive total), or if it does not settle.
    """
    grand_rows, grand_columns = sum(row_totals), sum(column_totals)
    if abs(grand_rows - grand_columns) > 1e-6 * max(grand_rows, grand_columns, 1.0):
        raise ValueError(
            f"row totals ({grand_rows:,.0f}) and column totals ({grand_columns:,.0f}) differ"
        )
    table = [[float(cell) for cell in row] for row in pattern]
    n_rows, n_columns = len(table), len(table[0])

    for _ in range(max_rounds):
        for i in range(n_rows):
            _scale(table, [(i, j) for j in range(n_columns)], row_totals[i], f"row {i}")
        for j in range(n_columns):
            _scale(table, [(i, j) for i in range(n_rows)], column_totals[j], f"column {j}")
        worst = max(
            abs(sum(table[i]) - row_totals[i]) / max(row_totals[i], 1.0) for i in range(n_rows)
        )
        if worst < tolerance:
            return table
    raise ValueError("proportional fitting did not settle")


def _scale(table: list[list[float]], cells: list[tuple[int, int]], target: float, label: str) -> None:
    current = sum(table[i][j] for i, j in cells)
    if current == 0:
        if target > 0:
            raise ValueError(f"{label} is all zero in the pattern but its total is {target:,.0f}")
        return
    factor = target / current
    for i, j in cells:
        table[i][j] *= factor
