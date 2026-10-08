"""Conditional capacity footprints, kept separate from fuel-output forecasts."""
import math

def capacity_case(base, excluded_assets, proposal_bpd, include_proposal):
    if set(excluded_assets)-set(base):
        raise ValueError('Unknown excluded plant')
    if any(not math.isfinite(v) or v < 0 for v in [*base.values(), proposal_bpd]):
        raise ValueError('Capacity must be finite and nonnegative')
    result={name:0.0 if name in excluded_assets else value for name,value in base.items()}
    if include_proposal:
        if base.get('Sapref',0) != 0:
            raise ValueError('Reconcile existing SAPREF capacity before adding the proposal')
        result['SAPREF proposal']=proposal_bpd
    return result
