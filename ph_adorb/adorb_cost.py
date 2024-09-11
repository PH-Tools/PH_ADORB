"""Calculate the annual costs for the ADORB analysis.

A.D.O.R.B. cost: Annualized De-carbonization Of Retrofitted Buildings cost - a “full-cost-accounted” 
annualized life-cycle cost metric for building projects. It includes the (annualized) direct costs of 
retrofit and maintenance, direct energy costs, a carbon cost for both operating and embodied/upfront 
greenhouse gas emissions, and a renewable-energy system-transition cost based on the required 
electrical service capacity.
"""

import eppy as eppy
import pandas as pd

import ph_adorb.variant as variant
from ph_adorb.variant import Variant, YearlyCost

# -- Constants
# -- TODO: Move these to the Variant? Or to an outside Config file?
PC = 0.25

# TODO: Support non-USA countries.
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
    _year: int, _future_annual_CO2_electric: list[float], _annual_CO2_gas: float, _discount_rate: float = 0.075
) -> float:
    """Calculate the total operational carbon cost for a given year."""
    try:
        return ((_future_annual_CO2_electric[_year] + _annual_CO2_gas) * PC) / ((1 + _discount_rate) ** _year)
    except ZeroDivisionError:
        return 0.0


def pv_direct_maintenance_cost(
    _year: int, _carbon_measure_yearly_costs: list[YearlyCost], _discount_rate: float = 0.02
) -> float:
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
            FACTOR * (row.cost / ((1 + _discount_rate) ** _year))
            for row in _carbon_measure_embodied_CO2_yearly_costs
            if row.year == _year
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
    _annual_cost_electric: float,
    _annual_cost_gas: float,
    _future_annual_CO2_electric: list[float],
    _annual_CO2_gas: float,
    _carbon_measure_yearly_costs: list[YearlyCost],
    _carbon_measure_embodied_CO2_yearly_costs: list[YearlyCost],
    _grid_transition_cost: float,
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
                columns[0]: pv_direct_energy_cost(n, _annual_cost_electric, _annual_cost_gas),
                columns[1]: pv_operation_carbon_cost(n, _future_annual_CO2_electric, _annual_CO2_gas),
                columns[2]: pv_direct_maintenance_cost(n, _carbon_measure_yearly_costs),
                columns[3]: pv_embodied_CO2_cost(n, _carbon_measure_embodied_CO2_yearly_costs),
                columns[4]: pv_grid_transition_cost(n, _grid_transition_cost),
            }
        )
        rows.append(new_row)

    return pd.DataFrame(rows, columns=columns)


# ---------------------------------------------------------------------------------------


def calculate_variant_ADORB_costs(_variant: Variant) -> pd.DataFrame:
    """Return a DataFrame with the Variant's ADORB costs for each year of the analysis duration."""

    # -----------------------------------------------------------------------------------
    # -- Electric: Annual Costs, Annual CO2
    annual_cost_electric = variant.get_annual_electric_cost(
        _variant.ep_hourly_results_df,
        _variant.electricity.purchase_price,
        _variant.electricity.sale_price,
        _variant.gas.annual_base_price,
    )
    future_annual_CO2_electric = variant.get_hourly_electric_CO2(
        _variant.ep_hourly_results_df,
        _variant.grid_region,
    )

    # -----------------------------------------------------------------------------------
    # -- Gas: Annual Costs, Annual CO2
    annual_cost_gas = variant.get_annual_gas_cost(
        _variant.gas.used,
        _variant.ep_meter_results_df,
        _variant.gas.purchase_price,
        _variant.gas.annual_base_price,
    )
    annual_CO2_gas = variant.get_annual_gas_CO2(
        _variant.gas.used,
        _variant.ep_meter_results_df,
    )

    # -----------------------------------------------------------------------------------
    # -- Add Embodied Carbon Costs for all the Measures
    carbon_measure_yearly_costs, first_costs = variant.get_carbon_measures_cost(
        _variant.construction_cost_estimate,
        _variant.all_carbon_measures,
    )
    carbon_measure_embodied_CO2_yearly_costs = variant.get_carbon_measures_embodied_CO2(
        _variant.all_carbon_measures,
        _variant.national_emissions.kg_CO2_per_USD,
    )
    carbon_measure_embodied_CO2_first_cost = variant.get_carbon_measures_embodied_CO2_first_cost(
        _variant.envelope_labor_cost_fraction,
        first_costs,
        _variant.national_emissions.kg_CO2_per_USD,
    )
    carbon_measure_embodied_CO2_yearly_costs.append(carbon_measure_embodied_CO2_first_cost)

    # -----------------------------------------------------------------------------------
    # -- Add Embodied Carbon Costs for all the Variant's Construction Materials
    for construction in _variant.construction_collection:
        material_cost: float = construction.cost * construction.material_fraction
        material_carbon_cost: float = material_cost * (_variant.national_emissions.kg_CO2_per_USD * PC)

        if construction.lifetime_years != 0:
            for year in range(0, _variant.analysis_duration, construction.lifetime_years):
                carbon_measure_yearly_costs.append(YearlyCost(construction.cost, year))
                carbon_measure_embodied_CO2_yearly_costs.append(YearlyCost(material_carbon_cost, year))
        else:
            carbon_measure_yearly_costs.append(YearlyCost(construction.cost, 0))
            carbon_measure_embodied_CO2_yearly_costs.append(YearlyCost(material_carbon_cost, 0))

    # -----------------------------------------------------------------------------------
    # -- Add Embodied Carbon Cost for all the Variant's Equipment
    for equip in _variant.equipment_collection:
        material_cost: float = equip.cost * equip.material_fraction
        material_carbon_cost: float = material_cost * (_variant.national_emissions.kg_CO2_per_USD * PC)

        if equip.lifetime_years != 0:
            for year in range(0, _variant.analysis_duration, equip.lifetime_years):
                carbon_measure_yearly_costs.append(YearlyCost(equip.cost, year))
                carbon_measure_embodied_CO2_yearly_costs.append(YearlyCost(material_carbon_cost, year))
        else:
            carbon_measure_yearly_costs.append(YearlyCost(equip.cost, 0))
            carbon_measure_embodied_CO2_yearly_costs.append(YearlyCost(material_carbon_cost, 0))

    # -----------------------------------------------------------------------------------
    # -- Compute and return the ADORB costs DataFrame
    return calculate_annual_ADORB_costs(
        _variant.analysis_duration,
        annual_cost_electric,
        annual_cost_gas,
        future_annual_CO2_electric,
        annual_CO2_gas,
        carbon_measure_yearly_costs,
        carbon_measure_embodied_CO2_yearly_costs,
        _variant.peak_electric_usage_W,
    )
