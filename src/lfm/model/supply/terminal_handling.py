"""Screen annual terminal handling at an assumed gross-equivalent turn rate.

This is a sensitivity, not available capacity, production or customer share.
Resolve compatible working capacity and receipt/dispatch constraints before
using this screen for an operating decision. Inputs are resolved by the caller.
"""
from math import isfinite


def annual_handling_m3(capacity_m3: float, monthly_turns: float) -> float:
    """Count each volume once on dispatch; do not sum receipts and dispatches."""
    if not all(isfinite(v) and v >= 0 for v in (capacity_m3, monthly_turns)):
        raise ValueError("Capacity and monthly turns must be finite and non-negative")
    return capacity_m3 * monthly_turns * 12
