# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Calculate the annual costs for the ADORB analysis.

A.D.O.R.B. cost: Annualized De-carbonization Of Retrofitted Buildings cost - a “full-cost-accounted” 
annualized life-cycle cost metric for building projects. It includes the (annualized) direct costs of 
retrofit and maintenance, direct energy costs, a carbon cost for both operating and embodied/upfront 
greenhouse gas emissions, and a renewable-energy system-transition cost based on the required 
electrical service capacity.
"""


import pandas as pd

from ph_adorb.yearly_values import YearlyCost

# -- Constants
# TODO: Support non-USA countries.
# TODO: Move these to be variables someplace...
USA_NUM_YEARS_TO_TRANSITION = 30
USA_NATIONAL_TRANSITION_COST = 4_500_000_000_000.00
NAMEPLATE_CAPACITY_INCREASE_GW = 1_600.00
USA_TRANSITION_COST_FACTOR = USA_NATIONAL_TRANSITION_COST / (NAMEPLATE_CAPACITY_INCREASE_GW * 1_000_000_000.00)


# ---------------------------------------------------------------------------------------


def pv_direct_energy_cost(
    _year: int, _annual_cost_electric: float, _annual_cost_gas: float, _discount_rate: float = 0.02
) -> float:
    """Calculate the total direct energy cost for a given year."""
    try:
        return (_annual_cost_electric + _annual_cost_gas) / ((1 + _discount_rate) ** _year)
    except ZeroDivisionError:
        return 0.0


def pv_operation_carbon_cost(
    _year: int,
    _future_annual_CO2_electric: list[float],
    _annual_CO2_gas: float,
    _price_of_carbon: float,
    _discount_rate: float = 0.075,
) -> float:
    """Calculate the total operational carbon cost for a given year."""
    try:
        return ((_future_annual_CO2_electric[_year] + _annual_CO2_gas) * _price_of_carbon) / (
            (1 + _discount_rate) ** _year
        )
    except ZeroDivisionError:
        return 0.0


def pv_install_cost(_year: int, _carbon_measure_yearly_costs: list[YearlyCost], _discount_rate: float = 0.02) -> float:
    """Calculate the total direct maintenance cost for a given year."""
    try:
        return sum(
            row.cost / ((1 + _discount_rate) ** _year) for row in _carbon_measure_yearly_costs if row.year == _year
        )
    except ZeroDivisionError:
        return 0.0


def pv_embodied_CO2_cost(
    _year: int, _carbon_measure_embodied_CO2_yearly_costs: list[YearlyCost], _discount_rate: float = 0.00
) -> float:
    """Calculate the total embodied CO2 cost for a given year."""
    # TODO: What is this factor for? Why do we multiply by it?
    FACTOR = 0.75
    try:
        return sum(
            FACTOR * (yearly_cost.cost / ((1 + _discount_rate) ** _year))
            for yearly_cost in _carbon_measure_embodied_CO2_yearly_costs
            if yearly_cost.year == _year
        )
    except ZeroDivisionError:
        return 0.0


def pv_grid_transition_cost(_year: int, _grid_transition_cost: float, _discount_rate: float = 0.02) -> float:
    """Calculate the total grid transition cost for a given year."""
    if _year > USA_NUM_YEARS_TO_TRANSITION:
        year_transition_cost_factor = 0  # $/Watt-yr
    else:
        # TODO: Support non-USA countries.
        year_transition_cost_factor = USA_TRANSITION_COST_FACTOR / USA_NUM_YEARS_TO_TRANSITION  # linear transition <- ?

    try:
        return (year_transition_cost_factor * _grid_transition_cost) / ((1 + _discount_rate) ** _year)
    except ZeroDivisionError:
        return 0.0


def calculate_annual_ADORB_costs(
    _analysis_duration_years: int,
    _annual_total_cost_electric: float,
    _annual_total_cost_gas: float,
    _annual_hourly_CO2_electric: list[float],
    _annual_total_CO2_gas: float,
    _all_yearly_install_costs: list[YearlyCost],
    _all_yearly_embodied_kgCO2: list[YearlyCost],
    _grid_transition_cost: float,
    _price_of_carbon: float,
) -> pd.DataFrame:
    """Returns a DataFrame with the yearly costs from the ADORB analysis."""

    # --  Define the column names
    columns = [
        "pv_direct_energy",
        "pv_operational_CO2",
        "pv_direct_MR",
        "pv_embodied_CO2",
        "pv_e_trans",
    ]

    # -- Create the row data
    rows: list[pd.Series] = []
    for n in range(1, _analysis_duration_years + 1):
        new_row: pd.Series[float] = pd.Series(
            {
                columns[0]: pv_direct_energy_cost(n, _annual_total_cost_electric, _annual_total_cost_gas),
                columns[1]: pv_operation_carbon_cost(
                    n, _annual_hourly_CO2_electric, _annual_total_CO2_gas, _price_of_carbon
                ),
                columns[2]: pv_install_cost(n, _all_yearly_install_costs),
                columns[3]: pv_embodied_CO2_cost(n, _all_yearly_embodied_kgCO2),
                columns[4]: pv_grid_transition_cost(n, _grid_transition_cost),
            }
        )
        rows.append(new_row)

    return pd.DataFrame(rows, columns=columns)
