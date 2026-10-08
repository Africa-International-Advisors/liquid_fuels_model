import math

import pytest
import pandas as pd

from lfm.model.scenario_levers import (
    ev_energy_economics, liquid_output_after_diversion, rail_shift_diesel,
    throughput_market_share,
)
from lfm.sources.sa_review import parse_eskom_history, parse_worldbank
from lfm.reporting.sa_review import complete_period_totals, annual_series


def test_rail_recovery_can_increase_diesel_when_route_and_drayage_are_longer():
    result = rail_shift_diesel(transferred_tonnes=1000, available_rail_tonnes=1000,
                              displaced_road_km=100, added_rail_km=500, drayage_road_km=80,
                              road_litres_per_tonne_km=.03, rail_litres_per_tonne_km=.01)
    assert result['net_diesel_reduction_litres'] == -4400
    with pytest.raises(ValueError, match='capacity'):
        rail_shift_diesel(transferred_tonnes=1001, available_rail_tonnes=1000,
                          displaced_road_km=100, added_rail_km=500, drayage_road_km=80,
                          road_litres_per_tonne_km=.03, rail_litres_per_tonne_km=.01)


def test_ev_charging_losses_and_no_payback_when_energy_costs_are_higher():
    values = dict(ice_litres_per_100km=5, fuel_zar_per_litre=20,
                  ev_kwh_per_100km=20, electricity_zar_per_kwh=5,
                  charging_efficiency=.8, annual_km=10000, purchase_premium_zar=10000)
    result = ev_energy_economics(**values)
    assert result['annual_energy_saving_zar'] == -2500
    assert result['positive_premium_payback_years'] is None
    result = ev_energy_economics(**dict(values, electricity_zar_per_kwh=2))
    assert result['positive_premium_payback_years'] == 2
    with pytest.raises(ValueError):
        ev_energy_economics(**dict(values, charging_efficiency=0))


def test_diversion_does_not_create_negative_supply_or_double_as_demand_loss():
    result = liquid_output_after_diversion(recovered_output_litres=1000,
                                          diverted_feedstock_pj=2, displaced_liquids_litres_per_pj=200)
    assert result == {'diversion_loss_litres': 400, 'remaining_output_litres': 600}
    with pytest.raises(ValueError):
        liquid_output_after_diversion(recovered_output_litres=100, diverted_feedstock_pj=2,
                                      displaced_liquids_litres_per_pj=200)


@pytest.mark.parametrize('deliveries,market', [(1, 0), (2, 1), (math.nan, 2), (-1, 2)])
def test_share_rejects_unmatched_or_invalid_boundaries(deliveries, market):
    with pytest.raises(ValueError):
        throughput_market_share(unique_customer_deliveries_litres=deliveries, matched_market_litres=market)


def test_worldbank_missing_is_not_zero_and_response_country_must_match():
    record = dict(countryiso3code='ZAF', indicator={'id': 'FDI'}, date='2024', value=None)
    assert parse_worldbank([{'pages': 1}, [record]], 'FDI') == []
    with pytest.raises(ValueError):
        parse_worldbank([{'pages': 1}, [dict(record, countryiso3code='NAM')]], 'FDI')


def test_eskom_history_rejects_missing_or_unexpected_table():
    with pytest.raises(ValueError):
        parse_eskom_history(['Diesel and kerosene usage for OCGTs, M litres 679.1 1129.5'])


def test_eskom_history_drops_targets_and_retains_fuel_boundary_and_financial_year():
    header = '2025 2024 2023 2022 2021 2020 2019 2018 2017 2016'
    pages = [header + '\nDiesel and kerosene usage for OCGTs, M litres 679.1 1 129.5 937.5 580.4 458.7 426.2 385.0 37.8 10.0 1 247.8\n'
             'Energy availability factor (EAF), % 1 60.60 RA 54.56RA 56.03RA 62.02RA 64.19RA 66.64 RA 69.95RA 78.00 RA 77.30RA 71.07RA',
             'OCGT diesel usage, R million 2 19 033 9 028 15 551 13 316 23 873 21 355']
    rows = parse_eskom_history(pages)
    assert len(rows) == 23
    by_key = {(r['series'], r['period']): r for r in rows}
    fuel = by_key['eskom_ocgt_diesel_and_kerosene', 2024]
    assert fuel['value'] == 1129.5
    assert fuel['period_basis'] == 'financial year ending 31 March'
    assert by_key['eskom_ocgt_cost_including_storage_demurrage', 2025]['value'] == 13316
    assert 19033 not in [r['value'] for r in rows]


def test_provincial_partial_year_is_not_annualised_and_duplicates_fail():
    data = pd.DataFrame({'period': ['2022-Q1','2022-Q2','2022-Q3','2022-Q4','2023-Q1'],
                         'value': [1,2,3,4,5]})
    assert complete_period_totals(data, periods_per_year=4) == {2022: 10}
    with pytest.raises(ValueError, match='Competing'):
        complete_period_totals(pd.concat([data,data.iloc[[0]]]), periods_per_year=4)
    with pytest.raises(ValueError, match='Competing'):
        annual_series(pd.DataFrame({'period': [2024,2024], 'value': [10,20]}))
