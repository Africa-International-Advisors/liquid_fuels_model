from copy import deepcopy
from pathlib import Path
import pytest,yaml
from lfm.model.illustrative_investment import evaluate_case,npv

@pytest.fixture
def inputs():
    p=Path(__file__).resolve().parents[1]/'assumptions/2026/vopak_investment_illustration.yaml'
    c=yaml.safe_load(p.read_text());return c['reported']['value'],c['illustrative']['value']

def test_npv_hand_calculation():
    assert npv(.1,[-100,55,60.5])==pytest.approx(0)

def test_no_volume_does_not_create_rent(inputs):
    r,a=inputs;x=evaluate_case(r,a,demand_bn_l=0,domestic_bn_l=0)
    assert x['preferred_option']=='Existing'
    assert all(o['incremental_rent_zar_year']==0 for o in x['options'])
    assert x['options'][2]['npv_zar']<0

def test_existing_tanks_filled_before_extra_rent(inputs):
    r,a=inputs;x=evaluate_case(r,a,demand_bn_l=6.8,domestic_bn_l=3.6)
    assert x['captured_lesedi_m3']<x['improved_limit_m3']
    assert x['options'][2]['contracted_added_gross_m3']==0

def test_ownership_changes_only_financial_interest(inputs):
    r,a=inputs;x=evaluate_case(r,a,demand_bn_l=7.6,domestic_bn_l=2.4)
    rr={**r,'ownership_fraction':.5};y=evaluate_case(rr,a,demand_bn_l=7.6,domestic_bn_l=2.4)
    assert x['captured_lesedi_m3']==y['captured_lesedi_m3']
    assert x['options'][2]['npv_zar']==y['options'][2]['npv_zar']
    assert y['options'][2]['ownership_share_npv_zar']==pytest.approx(y['options'][2]['npv_zar']*.5)

def test_loss_of_chargeable_services_can_reverse_investment(inputs):
    r,a=inputs;x=evaluate_case(r,{**a,'excess_service_contribution_zar_m3':0},demand_bn_l=7.6,domestic_bn_l=2.4)
    assert x['preferred_option']=='Existing'
    assert x['options'][1]['npv_zar']<0

def test_higher_capex_cannot_improve_npv(inputs):
    r,a=inputs;x=evaluate_case(r,a,demand_bn_l=7.6,domestic_bn_l=2.4)
    y=evaluate_case(r,{**a,'tank_addition_capex_zar':a['tank_addition_capex_zar']*1.25},demand_bn_l=7.6,domestic_bn_l=2.4)
    assert y['options'][2]['npv_zar']<x['options'][2]['npv_zar']
