"""Smoke tests — package imports cleanly and primitives are wired correctly."""
from __future__ import annotations

from lfm import __version__
from lfm.core.geography import ISO3_LIST, SACU, country
from lfm.core.products import CODES, product
from lfm.run import Run


def test_version_present():
    assert __version__


def test_sacu_is_five_countries():
    assert len(SACU) == 5
    assert ISO3_LIST == ("ZAF", "BWA", "LSO", "NAM", "SWZ")


def test_only_zaf_refines():
    refining = [c.iso3 for c in SACU if c.is_refining]
    assert refining == ["ZAF"]


def test_country_lookup_rejects_outside_sacu():
    import pytest
    with pytest.raises(KeyError):
        country("MOZ")


def test_products_include_petrol_diesel_jet():
    assert {"petrol_95", "diesel_50ppm", "jet_a1"}.issubset(set(CODES))
    assert product("jet_a1").family == "jet"


def test_run_tag_is_stable():
    r = Run(vintage="2026", scenario="reference", model_version="0.1.0")
    assert r.tag() == "2026-reference-v0.1.0"
