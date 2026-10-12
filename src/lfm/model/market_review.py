"""Public market context and explicitly conditional terminal capture screens.

Inputs are resolved by the caller. No inference of inland flows from mismatched
years, and no inference of customer capture from gross tankage.
"""
from __future__ import annotations


def handling_bn_l(working_m3: float, monthly_turns: float) -> float:
    if working_m3 < 0 or monthly_turns < 0:
        raise ValueError("Working capacity and turns must be non-negative")
    return working_m3 * monthly_turns * 12 * 1000 / 1e9


def capture_screen(gateway_bn_l: float, capture_fraction: float,
                   lesedi_routing_fraction: float, durban_handling_bn_l: float,
                   lesedi_handling_bn_l: float) -> dict:
    """A conditional imported chain, with Lesedi as a subset of Durban flow.

Tank arithmetic is a screening constraint only. Physical access, product
allocation, peaks and customer contestability remain unverified. Site volumes
are gross physical volumes, not ownership-proportional or incremental volumes.
"""
    if not 0 <= capture_fraction <= 1 or not 0 <= lesedi_routing_fraction <= 1:
        raise ValueError("Fractions must lie between zero and one")
    if min(gateway_bn_l, durban_handling_bn_l, lesedi_handling_bn_l) < 0:
        raise ValueError("Volumes must be non-negative")
    requested = gateway_bn_l * capture_fraction
    durban = min(requested, durban_handling_bn_l)
    lesedi = min(durban * lesedi_routing_fraction, lesedi_handling_bn_l)
    return dict(requested_durban_bn_l=requested, durban_bn_l=durban,
                lesedi_bn_l=lesedi, unique_bn_l=durban,
                gross_site_movements_bn_l=durban + lesedi,
                tank_screen_reduction_bn_l=requested - durban)


def pipeline_context(usage_ml_week: float, capacity_ml_week: float, weeks: float) -> dict:
    if capacity_ml_week <= 0 or not 0 <= usage_ml_week <= capacity_ml_week:
        raise ValueError("Pipeline usage/capacity inputs are inconsistent")
    return dict(usage_annualised_bn_l=usage_ml_week * weeks / 1000,
                capacity_annualised_bn_l=capacity_ml_week * weeks / 1000,
                utilisation_pct=usage_ml_week / capacity_ml_week * 100,
                arithmetic_unused_bn_l=(capacity_ml_week - usage_ml_week) * weeks / 1000)
