"""Fuel product taxonomy.

Splitting a product retroactively forces re-allocating history, so the
dimension is declared up front even if v1 collapses some categories.
Codes are short, lowercase, snake_case and used as keys in dataframes.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    code: str
    name: str
    family: str  # broad category for stakeholder roll-ups


PRODUCTS: tuple[Product, ...] = (
    Product("petrol_95",   "Petrol 95",            family="petrol"),
    Product("petrol_93",   "Petrol 93",            family="petrol"),
    Product("diesel_50ppm","Diesel 50ppm",         family="diesel"),
    Product("diesel_500ppm","Diesel 500ppm",       family="diesel"),
    Product("jet_a1",      "Jet A1",               family="jet"),
    Product("ip",          "Illuminating paraffin",family="paraffin"),
    Product("lpg",         "LPG",                  family="lpg"),
    Product("fuel_oil",    "Fuel oil",             family="heavy"),
)

CODES: tuple[str, ...] = tuple(p.code for p in PRODUCTS)


def product(code: str) -> Product:
    for p in PRODUCTS:
        if p.code == code:
            return p
    raise KeyError(f"unknown product code {code!r}; known: {CODES}")
