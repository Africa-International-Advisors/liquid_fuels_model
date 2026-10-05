"""Proportional fitting — rows and columns must both hit their totals."""
from __future__ import annotations

import pytest

from lfm.core.fitting import proportional_fit


def test_fitted_table_matches_row_and_column_totals() -> None:
    pattern = [[5.36, 0.42], [1.39, 0.85]]          # 2010: passenger, light commercial
    rows, columns = [8.15, 2.69], [8.20, 2.64]      # 2023 totals
    table = proportional_fit(pattern, rows, columns)
    for i, total in enumerate(rows):
        assert sum(table[i]) == pytest.approx(total, rel=1e-8)
    for j, total in enumerate(columns):
        assert sum(row[j] for row in table) == pytest.approx(total, rel=1e-8)


def test_pattern_already_at_the_totals_is_returned_unchanged() -> None:
    pattern = [[3.0, 1.0], [2.0, 4.0]]
    table = proportional_fit(pattern, [4.0, 6.0], [5.0, 5.0])
    assert table == [[pytest.approx(3.0), pytest.approx(1.0)],
                     [pytest.approx(2.0), pytest.approx(4.0)]]


def test_a_zero_cell_stays_zero() -> None:
    table = proportional_fit([[1.0, 0.0], [1.0, 1.0]], [2.0, 4.0], [3.0, 3.0])
    assert table[0][1] == 0.0


def test_fitting_keeps_the_order_of_the_pattern() -> None:
    # Passenger is more petrol than light commercial in the pattern, and stays so.
    table = proportional_fit([[5.36, 0.42], [1.39, 0.85]], [8.15, 2.69], [8.20, 2.64])
    assert table[0][0] / sum(table[0]) > table[1][0] / sum(table[1])


def test_totals_that_disagree_are_refused() -> None:
    with pytest.raises(ValueError, match="differ"):
        proportional_fit([[1.0, 1.0], [1.0, 1.0]], [5.0, 5.0], [4.0, 4.0])


def test_all_zero_row_with_a_positive_total_is_refused() -> None:
    with pytest.raises(ValueError, match="all zero"):
        proportional_fit([[0.0, 0.0], [1.0, 1.0]], [2.0, 2.0], [2.0, 2.0])
