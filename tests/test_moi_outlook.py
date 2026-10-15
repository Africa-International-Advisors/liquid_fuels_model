import pytest

from lfm.assumptions import YamlDirectoryProvider
from lfm.model import moi_outlook as mo
from lfm.run import Run


def test_oil_linked_price_has_no_freight():
    # ($70 + $7.5 x 60%) x R16.50 / 158.987 L
    assert mo.oil_linked_price(70, 7.5, 0.6, 16.5) == pytest.approx(74.5 * 16.5 / 158.987)


def test_petrol_price_build_keeps_2025_and_orders_cases():
    oil = {"Low": dict(brent=80, margin=10, petrol_share=.5, fx=18), "Base": dict(brent=70, margin=7.5, petrol_share=.6, fx=16.5),
           "High": dict(brent=60, margin=5, petrol_share=.7, fx=15)}
    build = mo.petrol_price_build(oil, dict(brent=69.14, fx=17.88, cpi_2026=.034), pump_2025=21.66, pump_2026=25.71)
    assert build["oil_linked_2025"] + build["other_2025"] == pytest.approx(21.66)
    idx = {c: v["index"] for c, v in build["cases"].items()}
    assert idx["Low"] > 1 > idx["Base"] > idx["High"]                # low demand has the high price
    path = build["cases"]["Base"]["path"]
    assert path[0] == 1 and path[1] == pytest.approx(25.71 / 21.66 / 1.034)
    assert path[2] == pytest.approx((path[1] + path[3]) / 2) and path[3] == path[5]


def test_market_2025_scales_2022_shares_and_cuts_southern_free_state():
    prov = {"GP": dict(petrol=4, diesel=4), "FS": dict(petrol=1, diesel=1), "WC": dict(petrol=5, diesel=5)}
    dist = {("FS", "Bloemfontein"): dict(petrol=.8, diesel=.8), ("FS", "Zastron"): dict(petrol=.2, diesel=.2),
            ("GP", "Johannesburg"): dict(petrol=4, diesel=4), ("WC", "Cape Town"): dict(petrol=5, diesel=5)}
    m = mo.market_2025(dict(petrol=20, diesel=10), dict(petrol=1, diesel=1), prov, dist,
                       dict(provinces=["GP", "FS"], excluded_districts_fs=["Zastron"]))
    assert m["moi"]["petrol"] == pytest.approx((4 + .8) * 2) and m["moi"]["diesel"] == pytest.approx(4 + .8)
    assert [d["district"] for d in m["districts"]] == ["Johannesburg", "Bloemfontein"]
    with pytest.raises(ValueError, match="excluded"):
        mo.market_2025(dict(petrol=20, diesel=10), dict(petrol=1, diesel=1), prov, dist,
                       dict(provinces=["GP", "FS"], excluded_districts_fs=["Nowhere"]))


def test_road_freight_diesel_scales_truck_fleet_and_efficiency():
    trucks = [dict(vehicles=100, km=50000, l_per_100km=30), dict(vehicles=100, km=70000, l_per_100km=40)]
    a = dict(base_year=2010, efficiency_gain=.004)
    per_truck = (50000 * .30 + 70000 * .40) / 2                      # 21 500 L
    assert mo.road_freight_diesel(trucks, 400000, 2025, a) == pytest.approx(per_truck * 400000 * .996 ** 15 / 1e9)


def test_ipp_peakers_run_below_eskom_owned_by_reported_ratio():
    pk = dict(eskom_units_mw=dict(ankerlig=1338, gourikwa=746, acacia=171, port_rex=171), ipp_units_mw=dict(dedisa=335, avon=670),
              eskom_load_factor=dict(Base=.05, High=.10), eskom_gwh_2026=152, eskom_days_2026=191, litres_per_kwh=.31)
    load = mo.peaker_load_factors(pk, eskom_gwh=2176, ipp_gwh=662)    # FY2025, Eskom Integrated Report 2026
    assert load["ratio"] == pytest.approx((662 / 1005) / (2176 / 2426))
    assert round(load["ratio"], 3) == .734
    assert load["ipp"]["Base"] == pytest.approx(.05 * load["ratio"])
    avon = mo.peaker_diesel(pk, load, "Base", ["avon"])
    national = mo.peaker_diesel(pk, load, "Base", [*pk["eskom_units_mw"], *pk["ipp_units_mw"]])
    assert avon == pytest.approx(670 * .05 * load["ratio"] * 8.76 * .31 / 1000)
    assert national / (2426 + 1005) > avon / 670                      # national load factor above the market of interest


def test_ev_curves_pass_through_the_anchor_year_actual():
    ev = dict(anchor_year=2025, Low=dict(ceiling=.9, slope=2), High=dict(ceiling=.3, slope=3))
    curves = mo.anchor_ev_curves(ev, .0068)
    for c in ("Low", "High"):
        assert mo.ev_share(curves[c], 2025) == pytest.approx(.0068)
    assert mo.ev_share(curves["Low"], 2030) > mo.ev_share(curves["High"], 2030)


def test_ev_benchmark_check_flags_cases_outside_their_bands():
    ev = dict(anchor_year=2025, check_year=2030, Low=dict(ceiling=.9, slope=2), High=dict(ceiling=.3, slope=3),
              benchmarks=dict(world=.044, china=.057, brazil=.09, germany=.14),
              bands=dict(High=[None, "china"], Base=["china", "brazil"], Low=["brazil", "germany"]))
    curves = mo.anchor_ev_curves(ev, .0088 * .769)
    chk = mo.ev_benchmark_check(ev, curves, .769)
    assert all(v["ok"] for v in chk.values()) and chk["Low"]["car_share"] > chk["Base"]["car_share"] > chk["High"]["car_share"]
    with pytest.raises(ValueError, match="outside"):
        mo.ev_benchmark_check({**ev, "bands": {**ev["bands"], "High": ["china", None]}}, curves, .769)


def test_generator_diesel_is_the_diesel_drop_less_the_peaker_drop():
    a = dict(years=[2023, 2024], level=dict(Low=0.0, Base=0.0, High=1.0))
    g = mo.generator_diesel({2023: 14.0, 2024: 12.4}, {2023: 1.6, 2024: .9}, a)
    assert g["drop"] == pytest.approx(1.6 - .7)
    assert g["cases"] == {"Low": 0.0, "Base": 0.0, "High": pytest.approx(.9)}


def test_lever_contributions_add_up_to_the_yearly_change():
    def run(off):
        # demand = 10 x (1 + 2% GDP)^i x (1 - 1% efficiency)^i, the two levers interacting
        g, e = (0 if "gdp" in off else .02), (0 if "efficiency" in off else .01)
        return {"cases": {c: {y: {"total": 10 * (1 + g) ** i * (1 - e) ** i} for i, y in enumerate(mo.YEARS)} for c in mo.CASES}}
    lv = mo.lever_contributions(run)["Base"]
    for y, r in lv.items():
        assert sum(r[k] for k in (*mo.LEVERS, "interaction")) == pytest.approx(r["change"])
    assert lv[2026]["gdp"] == pytest.approx(10 * 1.02 * .99 - 10 * .99)
    assert lv[2026]["efficiency"] == pytest.approx(10 * 1.02 * .99 - 10 * 1.02)
    assert lv[2026]["rail"] == 0


def test_assumptions_load_through_provider():
    a = YamlDirectoryProvider().get("moi_outlook", "oil_price", Run(vintage="2026")).value
    assert a["Base"] == dict(brent=70, margin=7.5, petrol_share=.6, fx=16.5)
