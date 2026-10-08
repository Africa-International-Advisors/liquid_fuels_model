import pytest
from lfm.model.supply.capacity_sensitivity import capacity_case

def test_exclusion_and_proposal_are_independent_and_do_not_mutate_base():
    base={'Natref':108,'Sasol':150,'Astron':100,'Sapref':0}
    assert sum(capacity_case(base,['Natref'],400,False).values())==250
    assert sum(capacity_case(base,[],400,False).values())==358
    assert sum(capacity_case(base,[],400,True).values())==758
    assert base['Natref']==108

def test_reject_double_counted_sapref():
    with pytest.raises(ValueError):
        capacity_case({'Sapref':180},[],400,True)

def test_reject_unknown_exclusion():
    with pytest.raises(ValueError):
        capacity_case({'Natref':108},['Other'],400,False)
