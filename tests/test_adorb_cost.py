from pytest import approx

from ph_adorb.adorb_cost import (
    present_value_factor,
    energy_purchase_cost_PV,
    measure_CO2_cost_PV,
    grid_transition_cost_PV,
    measure_purchase_cost_PV,
    energy_CO2_cost_PV,
    calculate_annual_ADORB_costs,
)
from ph_adorb.variant import YearlyCost

# -- Sample Data created from the Phius GUI Calculator to test against
phius_gui_annual_total_cost_electric = 1473.4188631811944
phius_gui_annual_total_cost_gas = 1414.5608710406113
phius_gui_annual_hourly_CO2_electric = [
    2978.655155240317,
    2978.655155240317,
    2625.0052682194573,
    2625.0052682194573,
    2170.890662041063,
    2170.890662041063,
    2239.323754255612,
    2239.323754255612,
    2408.991854512229,
    2408.991854512229,
    2408.991854512229,
    2408.991854512229,
    2408.991854512229,
    2602.3522388332867,
    2602.3522388332867,
    2602.3522388332867,
    2602.3522388332867,
    2602.3522388332867,
    2625.336537281845,
    2625.336537281845,
    2625.336537281845,
    2625.336537281845,
    2625.336537281845,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
    2593.221517493905,
]
phius_gui_annual_total_CO2_gas = 11177.480479866495
phius_gui_all_yearly_install_costs = [
    YearlyCost(23562.69, 0),
    YearlyCost(641.7, 0),
    YearlyCost(1717.96, 0),
    YearlyCost(820.55, 0),
    YearlyCost(861.21, 0),
    YearlyCost(861.21, 30),
    YearlyCost(795.83, 0),
    YearlyCost(1949.67, 0),
    YearlyCost(1949.67, 30),
    YearlyCost(5.0, 0),
    YearlyCost(5.0, 25),
    YearlyCost(3458.91, 0),
    YearlyCost(3458.91, 10),
    YearlyCost(3458.91, 20),
    YearlyCost(3458.91, 30),
    YearlyCost(3458.91, 40),
    YearlyCost(7500.0, 0),
    YearlyCost(7500.0, 20),
    YearlyCost(7500.0, 40),
    YearlyCost(1000.0, 0),
    YearlyCost(1000.0, 13),
    YearlyCost(1000.0, 26),
    YearlyCost(1000.0, 39),
    YearlyCost(87.87, 0),
    YearlyCost(611.0, 0),
    YearlyCost(611.0, 17),
    YearlyCost(611.0, 34),
    YearlyCost(662.0, 0),
    YearlyCost(662.0, 14),
    YearlyCost(662.0, 28),
    YearlyCost(662.0, 42),
    YearlyCost(1000.0, 0),
    YearlyCost(1000.0, 13),
    YearlyCost(1000.0, 26),
    YearlyCost(1000.0, 39),
    YearlyCost(992.0, 0),
    YearlyCost(992.0, 13),
    YearlyCost(992.0, 26),
    YearlyCost(992.0, 39),
    YearlyCost(959.0, 0),
    YearlyCost(959.0, 11),
    YearlyCost(959.0, 22),
    YearlyCost(959.0, 33),
    YearlyCost(959.0, 44),
    YearlyCost(250.0, 0),
]
phius_gui_all_yearly_embodied_kgCO2 = [
    YearlyCost(5513.66946, 0),
    YearlyCost(26.277615, 0),
    YearlyCost(70.350462, 0),
    YearlyCost(33.601522499999994, 0),
    YearlyCost(35.2665495, 0),
    YearlyCost(35.2665495, 30),
    YearlyCost(32.5892385, 0),
    YearlyCost(57.02784750000001, 0),
    YearlyCost(57.02784750000001, 30),
    YearlyCost(0.21937500000000001, 0),
    YearlyCost(0.21937500000000001, 25),
    YearlyCost(101.1731175, 0),
    YearlyCost(101.1731175, 10),
    YearlyCost(101.1731175, 20),
    YearlyCost(101.1731175, 30),
    YearlyCost(101.1731175, 40),
    YearlyCost(263.25, 0),
    YearlyCost(263.25, 20),
    YearlyCost(263.25, 40),
    YearlyCost(11.699999999999998, 0),
    YearlyCost(11.699999999999998, 13),
    YearlyCost(11.699999999999998, 26),
    YearlyCost(11.699999999999998, 39),
    YearlyCost(0, 0),
    YearlyCost(30.381975000000004, 0),
    YearlyCost(30.381975000000004, 17),
    YearlyCost(30.381975000000004, 34),
    YearlyCost(32.91795, 0),
    YearlyCost(32.91795, 14),
    YearlyCost(32.91795, 28),
    YearlyCost(32.91795, 42),
    YearlyCost(49.725, 0),
    YearlyCost(49.725, 13),
    YearlyCost(49.725, 26),
    YearlyCost(49.725, 39),
    YearlyCost(52.22880000000001, 0),
    YearlyCost(52.22880000000001, 13),
    YearlyCost(52.22880000000001, 26),
    YearlyCost(52.22880000000001, 39),
    YearlyCost(39.27105, 0),
    YearlyCost(39.27105, 11),
    YearlyCost(39.27105, 22),
    YearlyCost(39.27105, 33),
    YearlyCost(39.27105, 44),
    YearlyCost(10.2375, 0),
]
phius_gui_grid_transition_cost = 3009.76


def test_present_value_factor():
    assert present_value_factor(0, 0).factor == 1
    assert present_value_factor(1, 0).factor == 1
    assert present_value_factor(1, 0.02).factor == 1.0404
    assert present_value_factor(-1, 0.02).factor == 1.0
    assert present_value_factor(15, 0.02).factor == 1.3727857050906125


def test__adorb_cost_works_with_phius_gui_data():
    result = calculate_annual_ADORB_costs(
        50,
        phius_gui_annual_total_cost_electric,
        phius_gui_annual_total_cost_gas,
        phius_gui_annual_hourly_CO2_electric,
        phius_gui_annual_total_CO2_gas,
        phius_gui_all_yearly_install_costs,
        phius_gui_all_yearly_embodied_kgCO2,
        phius_gui_grid_transition_cost,
        0.25,
    )

    # Test against the known results from the PHIUS GUI tool
    assert result["pv_direct_energy"].sum() == approx(90_750.73699703957)
    assert result["pv_operational_CO2"].sum() == approx(44_516.49666105372)
    assert result["pv_direct_MR"].sum() == approx(73_733.73329487)
    assert result["pv_embodied_CO2"].sum() == approx(6_030.867828375)
    assert result["pv_e_trans"].sum() == approx(6_319.495880549157)


def test_pv_direct_energy_cost():
    assert energy_purchase_cost_PV(present_value_factor(0, 0), 0, 0) == 0
    assert energy_purchase_cost_PV(present_value_factor(1, 0.02), 1, 0) == approx(0.9611687812379854)
    assert energy_purchase_cost_PV(present_value_factor(-1, 0.02), 1, 0) == 1.0


def test_pv_operation_carbon_cost():
    assert energy_CO2_cost_PV(present_value_factor(0, 0.02), [0, 1, 2, 3], 0, 0.25) == 0
    assert energy_CO2_cost_PV(present_value_factor(1, 0.02), [0, 1, 2, 3], 0, 0.25) == approx(0.24029219530949636)
    assert energy_CO2_cost_PV(present_value_factor(-1, 0.02), [0, 1, 2, 3], 0, 0.25) == 0.75


def test_pv_direct_maintenance_cost():
    costs = [YearlyCost(0, 0), YearlyCost(1, 1), YearlyCost(2, 2), YearlyCost(3, 3)]
    assert measure_purchase_cost_PV(present_value_factor(0, 0.02), costs) == 0
    assert measure_purchase_cost_PV(present_value_factor(1, 0.02), costs) == approx(0.9611687812379854)
    assert measure_purchase_cost_PV(present_value_factor(-1, 0.02), costs) == 0


def test_pv_embodied_CO2_cost():
    costs = [YearlyCost(0, 0), YearlyCost(1, 1), YearlyCost(2, 2), YearlyCost(3, 3)]
    assert measure_CO2_cost_PV(present_value_factor(0, 0.02), costs) == approx(0)
    assert measure_CO2_cost_PV(present_value_factor(1, 0.02), costs) == approx(0.7208765859284891)
    assert measure_CO2_cost_PV(present_value_factor(-1, 0.02), costs) == 0


def test_pv_grid_transition_cost():
    assert grid_transition_cost_PV(present_value_factor(0, 0.02), 0) == 0
    assert grid_transition_cost_PV(present_value_factor(1, 0.02), 1) == approx(0.09010957324106113)
    assert grid_transition_cost_PV(present_value_factor(-1, 0.02), 1) == 0.09375
