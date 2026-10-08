"""Explicit-input investment screens; no file I/O or implied calibration.

These functions do not allocate flows automatically or replace the forecast engine.
All volumes are annual m3; all costs are ZAR unless a suffix specifies otherwise.
"""
from math import isfinite


def _positive(**values):
    if any(not isfinite(v) or v <= 0 for v in values.values()):
        raise ValueError('Expected finite positive inputs')


def _nonnegative(**values):
    if any(not isfinite(v) or v < 0 for v in values.values()):
        raise ValueError('Expected finite nonnegative inputs')


def balance_residual(*, production, imports, exports, consumption, stock_build=None):
    """Exports positive; stock build positive. Unknown stock stays unresolved."""
    _nonnegative(production=production, imports=imports, exports=exports, consumption=consumption)
    residual = production + imports - exports - consumption
    if stock_build is not None and not isfinite(stock_build):
        raise ValueError('Stock change must be finite')
    return {'before_stock': residual,
            'after_stock': None if stock_build is None else residual-stock_build}


def delivered_economics(*, product, handling, transport, border, losses,
                        inventory_finance, destination_price, required_margin):
    """All inputs on the same delivered ZAR/m3, product, date and tax basis."""
    _nonnegative(**locals())
    logistics = handling + transport + border + losses + inventory_finance
    bearable = destination_price - product - required_margin
    return {'logistics_zar_m3': logistics, 'delivered_zar_m3': product+logistics,
            'bearable_logistics_zar_m3': bearable, 'headroom_zar_m3': bearable-logistics}


def capture_screen(*, market_m3, accessible_fraction, capture_fraction, route_limit_m3):
    """Fractions must be calibrated; use once per mutually exclusive customer pool."""
    _nonnegative(**locals())
    if max(accessible_fraction, capture_fraction) > 1:
        raise ValueError('Fractions cannot exceed one')
    accessible = market_m3 * accessible_fraction
    requested = accessible * capture_fraction
    return {'accessible_m3': accessible, 'requested_capture_m3': requested,
            'captured_m3': min(requested, route_limit_m3),
            'route_constrained_m3': max(0, requested-route_limit_m3)}


def required_monthly_turns(*, annual_m3, capacity_m3):
    _nonnegative(annual_m3=annual_m3)
    _positive(capacity_m3=capacity_m3)
    return annual_m3 / capacity_m3 / 12


def terminal_screen(*, annual_m3, working_m3, achievable_monthly_turns,
                    receipt_limit_m3, dispatch_limit_m3):
    _nonnegative(annual_m3=annual_m3, achievable_monthly_turns=achievable_monthly_turns,
                 receipt_limit_m3=receipt_limit_m3, dispatch_limit_m3=dispatch_limit_m3)
    _positive(working_m3=working_m3)
    constraints = {'tank_turns': working_m3*achievable_monthly_turns*12,
                   'receipts': receipt_limit_m3, 'dispatch': dispatch_limit_m3}
    limit = min(constraints.values())
    return {'required_monthly_turns': required_monthly_turns(annual_m3=annual_m3, capacity_m3=working_m3),
            'achievable_annual_m3': limit, 'headroom_m3': limit-annual_m3,
            'unserved_m3': max(0, annual_m3-limit),
            'binding_constraints': [k for k,v in constraints.items() if v == limit]}


def break_even_screen(*, capex, annual_fixed_cost, contribution_zar_m3,
                      discount_rate, life_years):
    """Level pre-tax annual screen. Not NPV/IRR or a full investment appraisal.

Contribution must be incremental revenue less incremental variable cost, including
lost contribution elsewhere. No tax, working capital, ramp-up or residual value.
"""
    _nonnegative(capex=capex, annual_fixed_cost=annual_fixed_cost, discount_rate=discount_rate)
    _positive(life_years=life_years)
    if int(life_years) != life_years or not isfinite(contribution_zar_m3):
        raise ValueError('Integer life and finite contribution required')
    factor = (1/life_years if discount_rate == 0 else
              discount_rate/(1-(1+discount_rate)**(-life_years)))
    annual_cost = capex*factor + annual_fixed_cost
    return {'annual_cost_to_cover': annual_cost,
            'break_even_m3': None if contribution_zar_m3 <= 0 else annual_cost/contribution_zar_m3,
            'status': 'no positive contribution' if contribution_zar_m3 <= 0 else 'pre-tax level screen'}


def nine_world_balances(*, demand_paths, supply_paths, exports_m3, stock_build_m3):
    """A single matched year/product; imports and surplus remain distinct.

Routing/capture/operations must be recalculated for each row by the caller.
No probabilities are assigned; these are stress tests, not equiprobable forecasts.
"""
    labels = {'Low', 'Medium', 'High'}
    if set(demand_paths) != labels or set(supply_paths) != labels:
        raise ValueError('Three explicit paths required for both axes')
    _nonnegative(**demand_paths)
    _nonnegative(**supply_paths)
    _nonnegative(exports_m3=exports_m3)
    if not isfinite(stock_build_m3):
        raise ValueError('Finite stock change required')
    if not (demand_paths['Low'] <= demand_paths['Medium'] <= demand_paths['High'] and
            supply_paths['Low'] <= supply_paths['Medium'] <= supply_paths['High']):
        raise ValueError('Low/Medium/High paths must be ordered')
    result=[]
    for demand in ('Low','Medium','High'):
        for supply in ('High','Medium','Low'):
            gap=demand_paths[demand]+exports_m3+stock_build_m3-supply_paths[supply]
            result.append({'demand':demand,'supply':supply,'imports_m3':max(0,gap),
                           'unallocated_surplus_m3':max(0,-gap)})
    return result
