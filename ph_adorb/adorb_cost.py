# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Calculate the annual costs for the ADORB analysis.

A.D.O.R.B. cost: Annualized De-carbonization Of Retrofitted Buildings cost - a “full-cost-accounted” 
annualized life-cycle cost metric for building projects. It includes the (annualized) direct costs of 
retrofit and maintenance, direct energy costs, a carbon cost for both operating and embodied/upfront 
greenhouse gas emissions, and a renewable-energy system-transition cost based on the required 
electrical service capacity.
"""

import logging
import pandas as pd

from ph_adorb.yearly_values import YearlyCost, YearlyPresentValueFactor

logger = logging.getLogger(__name__)

# -- Constants
# TODO: Support non-USA countries.
# TODO: Move these to be variables someplace...
USA_NUM_YEARS_TO_TRANSITION = 30
USA_NATIONAL_TRANSITION_COST = 4.5e12
NAMEPLATE_CAPACITY_INCREASE_GW = 1_600
USA_TRANSITION_COST_FACTOR = USA_NATIONAL_TRANSITION_COST / (NAMEPLATE_CAPACITY_INCREASE_GW * 1e9)


# ---------------------------------------------------------------------------------------


def present_value_factor(_year: int, _discount_rate: float) -> YearlyPresentValueFactor:
    """Calculate the present value factor for a given year."""
    rate = (1 + _discount_rate) ** (_year + 1)
    return YearlyPresentValueFactor(rate, _year + 1)


def energy_purchase_cost_PV(
    _pv_factor: YearlyPresentValueFactor, _annual_cost_electric: float, _annual_cost_gas: float
) -> float:
    """Calculate the total direct energy cost for a given year."""
    logger.info(f"energy_purchase_cost_PV(year={_pv_factor.year}, factor={_pv_factor.factor :.3f})")

    if _pv_factor.factor == 0:
        return 0.0

    annual_energy_cost = _annual_cost_electric + _annual_cost_gas
    annual_energy_cost_PV = annual_energy_cost / _pv_factor.factor

    logger.debug(
        f"Energy Actual Cost: ${_annual_cost_electric :,.0f}[Elec.] + ${_annual_cost_gas :,.0f}[Gas] = ${annual_energy_cost :,.0f}"
    )
    logger.debug(
        f"Energy PV Cost: ${annual_energy_cost :,.0f} / {_pv_factor.factor :.3f} = PV${annual_energy_cost_PV :,.0f}"
    )

    return annual_energy_cost_PV


def energy_CO2_cost_PV(
    _pv_factor: YearlyPresentValueFactor,
    _future_annual_CO2_electric: list[float],
    _annual_CO2_gas: float,
    _price_of_carbon: float,
) -> float:
    """Calculate the total operational carbon cost for a given year."""
    logger.info(f"energy_CO2_cost_PV(year={_pv_factor.year}, factor={_pv_factor.factor :.3f})")

    if _pv_factor.factor == 0:
        return 0.0

    annual_elec_CO2 = _future_annual_CO2_electric[_pv_factor.year - 1]
    annual_CO2 = annual_elec_CO2 + _annual_CO2_gas
    annual_CO2_cost = annual_CO2 * _price_of_carbon
    annual_CO2_cost_PV = annual_CO2_cost / _pv_factor.factor

    logger.debug(
        f"Energy CO2 Emissions: {annual_elec_CO2 :,.0f}[Elec.] + {_annual_CO2_gas :,.0f}[Gas] = {annual_CO2 :,.0f}"
    )
    logger.debug(
        f"Energy CO2 Actual Cost: {annual_CO2 :,.0f} * ${_price_of_carbon :,.2f}/unit = ${annual_CO2_cost :,.0f}"
    )
    logger.debug(
        f"Energy CO2 PV Cost [{_pv_factor.year}]: ${annual_CO2_cost :,.0f} / {_pv_factor.factor :.3f} = PV${annual_CO2_cost_PV :,.0f}"
    )

    return annual_CO2_cost_PV


def measure_purchase_cost_PV(
    _pv_factor: YearlyPresentValueFactor, _carbon_measure_yearly_purchase_costs: list[YearlyCost]
) -> float:
    """Calculate the total Measure purchase, install and maintenance cost for a single year."""
    logger.info(f"measure_purchase_cost_PV(year={_pv_factor.year}, factor={_pv_factor.factor :.3f})")

    if _pv_factor == 0:
        return 0.0

    measure_costs = [
        measure.cost for measure in _carbon_measure_yearly_purchase_costs if measure.year == _pv_factor.year - 1
    ]
    if not measure_costs:
        return 0.0

    total_measure_cost = sum(measure_costs)
    total_measure_PV_cost = total_measure_cost / _pv_factor.factor

    logging.debug(f"Measure Actual Costs: {[f'${_ :,.0f}' for _ in measure_costs]} = {total_measure_cost :,.0f}")
    logging.debug(
        f"Measure PV Cost: ${total_measure_cost :,.0f} / {_pv_factor.factor :.3f} = PV${total_measure_PV_cost :,.0f}"
    )

    return total_measure_PV_cost


def measure_CO2_cost_PV(
    _pv_factor: YearlyPresentValueFactor, _carbon_measure_embodied_CO2_yearly_costs: list[YearlyCost]
) -> float:
    """Calculate the total Measure embodied CO2 cost for a given year."""
    logger.info(f"measure_CO2_cost_PV(year={_pv_factor.year}, factor={_pv_factor.factor :.3f})")

    # TODO: What is this factor for? Why do we multiply by it?
    FACTOR = 0.75

    if _pv_factor.factor == 0:
        return 0.0

    measure_costs = [
        yearly_cost.cost
        for yearly_cost in _carbon_measure_embodied_CO2_yearly_costs
        if yearly_cost.year == _pv_factor.year
    ]
    if not measure_costs:
        return 0.0

    total_measure_cost = sum(measure_costs)
    total_measure_PV_cost = sum(FACTOR * (cost / _pv_factor.factor) for cost in measure_costs)

    logging.debug(f"Measure CO2 Actual Cost: {[f'${_ :,.0f}' for _ in measure_costs]} = {total_measure_cost :,.0f}")
    logging.debug(
        f"Measure CO2 PV Cost: ${total_measure_cost :,.0f} / {_pv_factor.factor :.3f} = PV${total_measure_PV_cost :,.0f}"
    )

    return total_measure_PV_cost


def grid_transition_cost_PV(_pv_factor: YearlyPresentValueFactor, _grid_transition_cost: float) -> float:
    """Calculate the total grid transition cost for a given year."""
    logger.info(f"grid_transition_PV_cost(year={_pv_factor.year}, factor={_pv_factor.factor :.3f})")

    if _pv_factor.year > USA_NUM_YEARS_TO_TRANSITION:
        year_transition_cost_factor = 0  # $/Watt-yr
    else:
        # TODO: Support non-USA countries.
        year_transition_cost_factor = USA_TRANSITION_COST_FACTOR / USA_NUM_YEARS_TO_TRANSITION  # linear transition <- ?

    if _pv_factor.factor == 0:
        return 0.0

    transition_cost = year_transition_cost_factor * _grid_transition_cost
    transition_PV_cost = transition_cost / _pv_factor.factor

    logger.debug(
        f"Transition Cost [{_pv_factor.year}]: {year_transition_cost_factor: .0f} * ${_grid_transition_cost :,.0f} = ${transition_cost :,.0f}"
    )
    logger.debug(
        f"Transition PV Cost [{_pv_factor.year}]: ${transition_cost :,.0f} / {_pv_factor.factor :.3f} = PV${transition_PV_cost :,.0f}"
    )

    return transition_PV_cost


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
    for n in range(0, _analysis_duration_years):
        logger.info(f"Calculating year {n} costs:")

        new_row: pd.Series[float] = pd.Series(
            {
                columns[0]: energy_purchase_cost_PV(
                    present_value_factor(n, 0.02), _annual_total_cost_electric, _annual_total_cost_gas
                ),
                columns[1]: energy_CO2_cost_PV(
                    present_value_factor(n, 0.075), _annual_hourly_CO2_electric, _annual_total_CO2_gas, _price_of_carbon
                ),
                columns[2]: measure_purchase_cost_PV(present_value_factor(n, 0.02), _all_yearly_install_costs),
                columns[3]: measure_CO2_cost_PV(present_value_factor(n, 0.0), _all_yearly_embodied_kgCO2),
                columns[4]: grid_transition_cost_PV(present_value_factor(n, 0.02), _grid_transition_cost),
            }
        )
        rows.append(new_row)

    return pd.DataFrame(rows, columns=columns)
