"""Lesedi investment illustration with explicit, resolved inputs and no I/O.

Demand/supply are catchment deliveries, not national production or calibrated
forecasts. Throughput stays at 100% site level; ownership is financial only.
All option cash flows are incremental against the existing-asset alternative.
"""
from math import isfinite
from .investment_bridge import terminal_screen, required_monthly_turns


def npv(rate, flows):
    if not isfinite(rate) or rate < 0 or not all(isfinite(v) for v in flows):
        raise ValueError('Finite cash flows and nonnegative discount rate required')
    return sum(v/(1+rate)**t for t,v in enumerate(flows))


def _ramp(ramps, year):
    return ramps[min(year-1,len(ramps)-1)]


def evaluate_case(reported, inputs, *, demand_bn_l, domestic_bn_l):
    """Evaluate existing, access/dispatch improvement, and improvement + tanks.

    Added storage is contracted in proportion to extra flow beyond the improved
    existing tanks. This is an explicit allocation assumption, not occupancy data.
    Service contribution is net of variable costs and EXCLUDES rental already billed.
    """
    a=inputs
    for x in [demand_bn_l,domestic_bn_l,*[v for v in a.values() if isinstance(v,(int,float))]]:
        if not isfinite(x) or x < 0:raise ValueError('Finite nonnegative inputs required')
    for key in ['durban_gateway_import_share','vopak_share_of_durban_imports',
                'lesedi_share_of_vopak_flow','lesedi_domestic_capture_share','working_fraction']:
        if not 0 <= a[key] <= 1:raise ValueError(f'{key} must be a fraction')
    if a['working_fraction']==0 or a['improved_monthly_turns']<=0:
        raise ValueError('Positive working fraction and improved turns required')
    if a['improved_monthly_turns']<a['existing_monthly_turns']:
        raise ValueError('Improvement cannot reduce achievable turns')
    if int(a['operating_years'])!=a['operating_years'] or a['operating_years']<1:
        raise ValueError('Positive integer operating years required')
    ramps=a['ramp_fractions']
    if not ramps or any(not isfinite(v) or not 0<=v<=1 for v in ramps) or ramps!=sorted(ramps):
        raise ValueError('Explicit nondecreasing ramp fractions required')
    imports=max(0,demand_bn_l-domestic_bn_l)*1e6
    domestic=min(domestic_bn_l,demand_bn_l)*1e6
    gateway=imports*a['durban_gateway_import_share']
    coastal=gateway*a['vopak_share_of_durban_imports']
    lesedi_import=coastal*a['lesedi_share_of_vopak_flow']
    lesedi_domestic=domestic*a['lesedi_domestic_capture_share']
    captured=lesedi_import+lesedi_domestic
    working=reported['lesedi_gross_m3']*a['working_fraction']
    def screen(capacity,turns):
        return terminal_screen(annual_m3=captured,working_m3=capacity,achievable_monthly_turns=turns,
             receipt_limit_m3=a['operating_receipt_limit_m3'],dispatch_limit_m3=a['operating_dispatch_limit_m3'])
    existing=screen(working,a['existing_monthly_turns'])
    improved=screen(working,a['improved_monthly_turns'])
    expanded=screen(working+a['added_gross_m3']*a['working_fraction'],a['improved_monthly_turns'])
    specs=[('Existing',existing,0,0,False),
           ('Improve access / dispatch',improved,a['access_package_capex_zar'],a['access_package_fixed_opex_zar'],False),
           ('Improve + add tanks',expanded,a['access_package_capex_zar']+a['tank_addition_capex_zar'],a['access_package_fixed_opex_zar']+a['tank_addition_fixed_opex_zar'],True)]
    options=[]
    for name,s,capex,fixed,add_tanks in specs:
        served=min(captured,s['achievable_annual_m3'])
        incremental=served-min(captured,existing['achievable_annual_m3'])
        extra_storage_flow=max(0,served-improved['achievable_annual_m3']) if add_tanks else 0
        contracted_gross=min(a['added_gross_m3'],extra_storage_flow/(a['working_fraction']*a['improved_monthly_turns']*12))
        rent=contracted_gross*a['storage_rent_zar_gross_m3_year']
        services=incremental*a['excess_service_contribution_zar_m3']
        maintenance=capex*a['maintenance_capex_fraction']
        cashflows=[-capex]+[(rent+services)*_ramp(ramps,y)-fixed-maintenance for y in range(1,a['operating_years']+1)]
        value=npv(a['discount_rate'],cashflows)
        options.append(dict(option=name,capex_zar=capex,served_m3=served,
            unserved_m3=captured-served,incremental_m3=incremental,contracted_added_gross_m3=contracted_gross,
            incremental_rent_zar_year=rent,incremental_service_contribution_zar_year=services,
            incremental_ebitda_zar_year=rent+services-fixed,maintenance_capex_zar_year=maintenance,
            steady_cashflow_zar_year=rent+services-fixed-maintenance,npv_zar=value,
            ownership_share_npv_zar=value*reported['ownership_fraction'],cashflows=cashflows,
            achievable_annual_m3=s['achievable_annual_m3']))
    best=max(options,key=lambda x:x['npv_zar'])
    return dict(demand_bn_l=demand_bn_l,domestic_bn_l=domestic_bn_l,import_requirement_m3=imports,
        durban_gateway_m3=gateway,vopak_durban_m3=coastal,lesedi_import_m3=lesedi_import,
        lesedi_domestic_m3=lesedi_domestic,captured_lesedi_m3=captured,
        capture_share_of_catchment=captured/(demand_bn_l*1e6) if demand_bn_l else 0,
        working_m3=working,required_monthly_turns=required_monthly_turns(annual_m3=captured,capacity_m3=working),
        existing_limit_m3=existing['achievable_annual_m3'],improved_limit_m3=improved['achievable_annual_m3'],
        logistics_headroom_zar_m3=a['allowable_logistics_zar_m3']-a['assumed_durban_logistics_zar_m3'],
        options=options,preferred_option=best['option'],preferred_npv_zar=best['npv_zar'])


def reversal_volume(reported,inputs,*,domestic_bn_l,lower_demand_bn_l,upper_demand_bn_l,
                    option_a,option_b):
    """Bisection of a caller-bracketed demand point where option NPVs cross."""
    def delta(d):
        opts={x['option']:x for x in evaluate_case(reported,inputs,demand_bn_l=d,domestic_bn_l=domestic_bn_l)['options']}
        return opts[option_b]['npv_zar']-opts[option_a]['npv_zar']
    lo,hi=lower_demand_bn_l,upper_demand_bn_l
    if lo>hi or delta(lo)>0 or delta(hi)<0:return None
    for _ in range(60):
        mid=(lo+hi)/2
        if delta(mid)>0:hi=mid
        else:lo=mid
    return evaluate_case(reported,inputs,demand_bn_l=(lo+hi)/2,domestic_bn_l=domestic_bn_l)['captured_lesedi_m3']
