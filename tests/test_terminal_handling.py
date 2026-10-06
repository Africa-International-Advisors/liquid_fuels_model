import pytest

from lfm.model.supply.terminal_handling import annual_handling_m3


def test_monthly_turns_convert_stock_to_annual_dispatch():
    assert annual_handling_m3(140_000, 2) == 3_360_000
    assert annual_handling_m3(0, 2) == 0


@pytest.mark.parametrize("capacity,turns", [(-1, 2), (1, -2), (float('nan'), 2), (1, float('inf'))])
def test_invalid_screen_inputs_rejected(capacity, turns):
    with pytest.raises(ValueError):
        annual_handling_m3(capacity, turns)
