"""SACU geography — the v1 country list.

Wider SADC (Mozambique, Zambia, Zimbabwe, Angola, etc.) is a planned
extension; do not add countries here without an explicit scope change.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Country:
    iso3: str        # ISO 3166-1 alpha-3, used as the key in dataframes
    name: str
    is_refining: bool  # has domestic refining capacity (matters for supply layer)


SACU: tuple[Country, ...] = (
    Country("ZAF", "South Africa", is_refining=True),
    Country("BWA", "Botswana", is_refining=False),
    Country("LSO", "Lesotho", is_refining=False),
    Country("NAM", "Namibia", is_refining=False),
    Country("SWZ", "Eswatini", is_refining=False),
)

ISO3_LIST: tuple[str, ...] = tuple(c.iso3 for c in SACU)


def country(iso3: str) -> Country:
    for c in SACU:
        if c.iso3 == iso3:
            return c
    raise KeyError(f"{iso3} is not in the SACU v1 scope: {ISO3_LIST}")
