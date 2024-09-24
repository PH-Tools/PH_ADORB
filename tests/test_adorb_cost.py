from pytest import approx

from ph_adorb.adorb_cost import (
    pv_direct_energy_cost,
    pv_install_cost,
    pv_embodied_CO2_cost,
    pv_grid_transition_cost,
    pv_operation_carbon_cost,
)
from ph_adorb.variant import YearlyCost


def test_pv_direct_energy_cost():
    assert pv_direct_energy_cost(0, 0, 0) == 0
    assert pv_direct_energy_cost(1, 1, 1) == approx(1.9607843)
    assert pv_direct_energy_cost(-1, 1, 1) == approx(2.04)
    assert pv_direct_energy_cost(1, 0, 0, _discount_rate=-1) == 0


def test_pv_operation_carbon_cost():
    assert pv_operation_carbon_cost(0, [0, 1, 2, 3], 0, 0.25) == 0
    assert pv_operation_carbon_cost(1, [0, 1, 2, 3], 1, 0.25) == approx(0.46511627906976744)
    assert pv_operation_carbon_cost(-1, [0, 1, 2, 3], 1, 0.25) == approx(1.075)
    assert pv_operation_carbon_cost(1, [0, 1, 2, 3], 0, 0.25, _discount_rate=-1) == 0


def test_pv_direct_maintenance_cost():
    costs = [YearlyCost(0, 0), YearlyCost(1, 1), YearlyCost(2, 2), YearlyCost(3, 3)]
    assert pv_install_cost(0, costs) == 0
    assert pv_install_cost(1, costs) == approx(0.9803921568627451)
    assert pv_install_cost(-1, costs) == approx(0.0)
    assert pv_install_cost(1, costs, _discount_rate=-1) == 0


def test_pv_embodied_CO2_cost():
    costs = [YearlyCost(0, 0), YearlyCost(1, 1), YearlyCost(2, 2), YearlyCost(3, 3)]
    assert pv_embodied_CO2_cost(0, costs) == 0
    assert pv_embodied_CO2_cost(1, costs) == approx(0.75)
    assert pv_embodied_CO2_cost(-1, costs) == approx(0.0)
    assert pv_embodied_CO2_cost(1, costs, _discount_rate=-1) == 0


def test_pv_grid_transition_cost():
    assert pv_grid_transition_cost(0, 0) == 0
    assert pv_grid_transition_cost(100, 0) == 0
    assert pv_grid_transition_cost(1, 1) == approx(0.09191176470588235)
    assert pv_grid_transition_cost(-1, 1) == approx(0.095625)
    assert pv_grid_transition_cost(1, 0, _discount_rate=-1) == 0
