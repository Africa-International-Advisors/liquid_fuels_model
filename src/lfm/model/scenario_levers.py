"""Explicit-input review calculations; not automatically applied to forecasts.

No defaults calibrate an adoption response, rail transfer or product diversion.
Callers must resolve registered inputs before entering this module.
"""
from math import isfinite


def _nonnegative(**values):
    if any(not isfinite(v) or v < 0 for v in values.values()):
        raise ValueError('Inputs must be finite and non-negative')


def ev_energy_economics(*, ice_litres_per_100km, fuel_zar_per_litre,
                        ev_kwh_per_100km, electricity_zar_per_kwh,
                        charging_efficiency, annual_km, purchase_premium_zar):
    """Energy-only economics, not TCO or an inferred adoption rate.

    EV consumption is battery-side; efficiency converts to billed energy.
    Purchase premium is EV minus ICE; negative values are allowed.
    No maintenance, financing, tax, resale or insurance assumptions are implied.
    """
    _nonnegative(ice=ice_litres_per_100km, fuel=fuel_zar_per_litre,
                 ev=ev_kwh_per_100km, electricity=electricity_zar_per_kwh, km=annual_km)
    if not isfinite(charging_efficiency) or not 0 < charging_efficiency <= 1:
        raise ValueError('Charging efficiency must be in (0, 1]')
    if not isfinite(purchase_premium_zar):
        raise ValueError('Purchase premium must be finite')
    ice_cost = ice_litres_per_100km * fuel_zar_per_litre / 100
    ev_cost = ev_kwh_per_100km * electricity_zar_per_kwh / charging_efficiency / 100
    saving = (ice_cost - ev_cost) * annual_km
    payback = purchase_premium_zar / saving if purchase_premium_zar > 0 and saving > 0 else None
    return dict(ice_energy_zar_per_km=ice_cost, ev_energy_zar_per_km=ev_cost,
                annual_energy_saving_zar=saving, positive_premium_payback_years=payback,
                purchase_premium_zar=purchase_premium_zar)


def rail_shift_diesel(*, transferred_tonnes, available_rail_tonnes,
                     displaced_road_km, added_rail_km, drayage_road_km,
                     road_litres_per_tonne_km, rail_litres_per_tonne_km):
    """Net diesel reduction, including road drayage and diesel rail traction.

    Tonnes must be freight actually transferred from road, not all new rail
    tonnage. Rail intensity is diesel-only; electric traction may be zero here.
    A negative reduction is allowed when the alternative route uses more diesel.
    """
    _nonnegative(**locals())
    if transferred_tonnes > available_rail_tonnes:
        raise ValueError('Transferred freight exceeds available rail capacity')
    displaced = transferred_tonnes * displaced_road_km * road_litres_per_tonne_km
    drayage = transferred_tonnes * drayage_road_km * road_litres_per_tonne_km
    rail = transferred_tonnes * added_rail_km * rail_litres_per_tonne_km
    return dict(displaced_road_diesel_litres=displaced, added_drayage_diesel_litres=drayage,
                added_rail_diesel_litres=rail, net_diesel_reduction_litres=displaced - drayage - rail)


def liquid_output_after_diversion(*, recovered_output_litres, diverted_feedstock_pj,
                                 displaced_liquids_litres_per_pj):
    """A calibrated marginal bridge, not a generic gas-to-liquids conversion.

    Product-specific coefficients must come from the operator/process evidence.
    recovered_output already includes availability/feedstock recovery: do not
    deduct the same gas loss again in the diversion coefficient.
    """
    _nonnegative(**locals())
    loss = diverted_feedstock_pj * displaced_liquids_litres_per_pj
    if loss > recovered_output_litres:
        raise ValueError('Diversion loss exceeds available liquid output')
    return dict(diversion_loss_litres=loss, remaining_output_litres=recovered_output_litres - loss)


def throughput_market_share(*, unique_customer_deliveries_litres, matched_market_litres):
    """Matched product, geography and period; transfers must already be removed."""
    _nonnegative(**locals())
    if matched_market_litres == 0:
        raise ValueError('Market denominator must be positive')
    if unique_customer_deliveries_litres > matched_market_litres:
        raise ValueError('Deliveries exceed market: reconcile boundary or duplicate flows')
    return unique_customer_deliveries_litres / matched_market_litres
