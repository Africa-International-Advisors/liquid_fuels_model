import pytest
from lfm.model.investment_bridge import (balance_residual, delivered_economics,
    capture_screen, terminal_screen, break_even_screen, nine_world_balances)


def test_stock_unknown_does_not_close_balance():
    assert balance_residual(production=60,imports=50,exports=5,consumption=100)=={'before_stock':5,'after_stock':None}
    assert balance_residual(production=60,imports=50,exports=5,consumption=100,stock_build=5)['after_stock']==0


def test_cost_headroom_and_binding_capacity():
    e=delivered_economics(product=100,handling=2,transport=8,border=1,losses=1,inventory_finance=3,destination_price=120,required_margin=10)
    assert e['headroom_zar_m3']==-5
    t=terminal_screen(annual_m3=1500,working_m3=100,achievable_monthly_turns=2,receipt_limit_m3=1800,dispatch_limit_m3=1200)
    assert t['binding_constraints']==['dispatch']
    assert t['unserved_m3']==300
    assert t['required_monthly_turns']==1.25


def test_capture_cannot_exceed_route_or_market():
    assert capture_screen(market_m3=100,accessible_fraction=.5,capture_fraction=.8,route_limit_m3=30)['captured_m3']==30
    with pytest.raises(ValueError):
        capture_screen(market_m3=100,accessible_fraction=1.1,capture_fraction=.8,route_limit_m3=30)


def test_break_even_zero_rate_and_no_margin():
    assert break_even_screen(capex=1000,annual_fixed_cost=50,contribution_zar_m3=5,discount_rate=0,life_years=10)['break_even_m3']==30
    assert break_even_screen(capex=1000,annual_fixed_cost=50,contribution_zar_m3=0,discount_rate=.1,life_years=10)['break_even_m3'] is None


def test_nine_world_order_and_surplus():
    rows=nine_world_balances(demand_paths={'Low':50,'Medium':100,'High':150},supply_paths={'Low':20,'Medium':80,'High':110},exports_m3=0,stock_build_m3=0)
    assert len(rows)==9
    assert rows[0]['imports_m3']==0 and rows[0]['unallocated_surplus_m3']==60
    assert rows[4]['imports_m3']==20
    assert rows[-1]['imports_m3']==130
