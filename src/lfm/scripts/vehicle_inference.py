"""Two estimates built from the vehicle data held, for request DR07.

``fuel_by_class``
    No source crosses fuel with vehicle class. The register gives vehicles by
    class and the transport bulletin gives petrol and diesel vehicles in
    total. This fits the two together: it starts from each class's diesel
    share in the 2010 fleet (Stone et al. 2018) and moves every share by one
    common factor until the classes add up to the bulletin's diesel total.

``light_commercial_electric_forecast``
    naamsa does not report electric sales by segment, so there is no history
    to project. This turns the three cases already proposed for the electric
    share of new light commercial sales (2030 and 2035) into a year by year
    path, the electric vehicles that puts on the road and the fuel they
    displace.

Both are estimates and are labelled as such wherever they are shown.
"""
from __future__ import annotations

CLASSES = ["cars", "light_commercial", "trucks", "buses", "minibuses", "motorcycles", "other_self_propelled"]
# Stone et al. (2018) vehicle types that make up each register class: (diesel types, petrol types)
STONE_TYPES = {
    "cars": (("CarDiesel", "SUVDiesel", "CarHybridDiesel"), ("CarGasoline", "SUVGasoline", "CarHybridGasoline", "SUVHybridGasoline")),
    "light_commercial": (("LCVDiesel",), ("LCVGasoline",)),
    "trucks": (tuple(f"HCV{n}Diesel" for n in range(1, 10)), ("HCV1Gasoline",)),
    "buses": (("BusDiesel",), ()),
    "minibuses": (("MBTDiesel",), ("MBTGasoline",)),
    "motorcycles": ((), ("MotoGasoline",)),
}
OTHER_DIESEL_SHARE = 1.0        # tractors and plant: taken as diesel; an assumption, not in any source held
FORECAST_YEARS = list(range(2026, 2036))


def seed_shares(stone: dict) -> dict[str, float]:
    """Diesel share of each class in the 2010 fleet."""
    out = {"other_self_propelled": OTHER_DIESEL_SHARE}
    for name, (diesel, petrol) in STONE_TYPES.items():
        d = sum(float(stone[t]["vehicles_2010"]) for t in diesel)
        p = sum(float(stone[t]["vehicles_2010"]) for t in petrol)
        out[name] = d / (d + p)
    return out


def fuel_by_class(class_totals: dict[str, float], diesel_total: float, seed: dict[str, float]) -> tuple[dict[str, tuple[float, float]], float]:
    """``({class: (petrol, diesel)}, factor)`` with diesel adding to ``diesel_total``.

    Each class's odds of being diesel are its 2010 odds times one factor, the same for every class. A class that was all
    diesel or all petrol in 2010 stays so.
    """
    def diesel(name: str, factor: float) -> float:
        s = seed[name]
        return class_totals[name] * (s * factor / (s * factor + 1 - s) if 0 < s < 1 else s)

    low, high = 1e-6, 1e6
    for _ in range(200):                                             # bisection on the common factor
        factor = (low * high) ** 0.5
        if sum(diesel(name, factor) for name in class_totals) < diesel_total:
            low = factor
        else:
            high = factor
    return {name: (class_totals[name] - diesel(name, factor), diesel(name, factor)) for name in class_totals}, factor


def light_commercial_electric_forecast(cases: dict[str, dict[int, float]], sales: dict[int, float], fleet: float, litres_a_year: float) -> dict[str, dict]:
    """For each case: the share of new sales, the vehicles on the road and the fuel displaced, by year.

    ``cases`` is ``{case: {2030: %, 2035: %}}``. The share rises in a straight line from nil in 2025 to the 2030 value and
    on to the 2035 value. New sales after the last year in ``sales`` are held at that year's level. No electric vehicle is
    scrapped inside the ten years.
    """
    last = max(sales)
    out = {}
    for case, points in cases.items():
        share, on_road, displaced, total = {}, {}, {}, 0.0
        for year in FORECAST_YEARS:
            share[year] = points[2030] * (year - 2025) / 5 if year <= 2030 else points[2030] + (points[2035] - points[2030]) * (year - 2030) / 5
            total += sales.get(year, sales[last]) * share[year] / 100
            on_road[year] = total
            displaced[year] = total * litres_a_year / 1e6
        out[case] = {"share": share, "on_road": on_road, "fleet_share": {y: on_road[y] / fleet * 100 for y in FORECAST_YEARS}, "displaced_million_litres": displaced}
    return out
