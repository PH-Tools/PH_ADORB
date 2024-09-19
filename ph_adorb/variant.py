# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A Building Variant with all of its relevant data, and related functions."""

from collections import namedtuple

import pandas as pd
from pydantic import BaseModel, Field

from ph_adorb.constructions import PhAdorbConstructionCollection
from ph_adorb.equipment import PhAdorbEquipmentCollection
from ph_adorb.fuel import PhAdorbFuel
from ph_adorb.grid_region import PhAdorbGridRegion
from ph_adorb.measures import PhAdorbCO2MeasureCollection
from ph_adorb.national_emissions import PhAdorbNationalEmissions

YearlyCost = namedtuple("YearlyCost", ["cost", "year"])


class PhAdorbVariant(BaseModel):
    """A single Variant of a building design."""

    name: str
    ep_hourly_results_df: pd.DataFrame
    ep_meter_results_df: pd.DataFrame
    construction_cost_estimate: list
    peak_electric_usage_W: float
    electricity: PhAdorbFuel
    gas: PhAdorbFuel
    grid_region: PhAdorbGridRegion
    national_emissions: PhAdorbNationalEmissions
    analysis_duration: int
    envelope_labor_cost_fraction: float

    measure_collection: PhAdorbCO2MeasureCollection = Field(default_factory=PhAdorbCO2MeasureCollection)
    construction_collection: PhAdorbConstructionCollection = Field(default_factory=PhAdorbConstructionCollection)
    equipment_collection: PhAdorbEquipmentCollection = Field(default_factory=PhAdorbEquipmentCollection)

    class Config:
        arbitrary_types_allowed = True

    @property
    def all_carbon_measures(self) -> PhAdorbCO2MeasureCollection:
        """Return a collection of all the Carbon Measures."""
        return self.measure_collection

    @property
    def performance_measure_collection(self) -> PhAdorbCO2MeasureCollection:
        """Return a collection of only the Performance Carbon Measures."""
        return self.measure_collection.performance_measures

    @property
    def nonperformance_carbon_measures(self) -> PhAdorbCO2MeasureCollection:
        """Return a collection of only the Non-Performance Carbon Measures."""
        return self.measure_collection.nonperformance_measures


# ---------------------------------------------------------------------------------------


def get_annual_electric_cost(
    _ep_hourly_results_df: pd.DataFrame,
    _electric_purchase_price: float,
    _electric_sell_price: float,
    _electric_annual_base_price: float,
) -> float:
    """Return the total annual electricity cost for the building."""

    KWH_PER_JOULE = 0.0000002778
    PURCHASED_ELEC_FIELD_NAME = "Whole Building:Facility Total Purchased Electricity Energy [J](Hourly)"
    SOLD_ELEC_FIELD_NAME = "Whole Building:Facility Total Surplus Electricity Energy [J](Hourly)"

    total_purchased_electric_J: float = _ep_hourly_results_df[PURCHASED_ELEC_FIELD_NAME].sum()
    total_purchased_electric_KWH = total_purchased_electric_J * KWH_PER_JOULE
    total_purchased_electric_cost = total_purchased_electric_KWH * _electric_purchase_price

    total_sold_electric_J: float = _ep_hourly_results_df[SOLD_ELEC_FIELD_NAME].sum()
    total_sold_electric_KWH = total_sold_electric_J * KWH_PER_JOULE
    total_sold_electric_cost = total_sold_electric_KWH * _electric_sell_price

    total_annual_electric_cost = total_purchased_electric_cost - total_sold_electric_cost + _electric_annual_base_price
    return total_annual_electric_cost


def get_hourly_electric_CO2(_hourly: pd.DataFrame, _grid_region_factors: PhAdorbGridRegion) -> list[float]:
    """Return a list of total annual CO2 emissions for each year from 2023 - 2011 (89 years)."""

    PURCHASED_ELEC_FIELD_NAME = "Whole Building:Facility Total Purchased Electricity Energy [J](Hourly)"
    MWH_PER_JOULE = 0.0000000002778

    # 8760 values (from the hourly simulation)....
    hourly_electric_MWH: pd.Series[float] = _hourly[PURCHASED_ELEC_FIELD_NAME] * MWH_PER_JOULE

    # Multiply each year's factors by the hourly electric MWH list, and sum the results for each year.
    total_annual_CO2: list[float] = (
        (_grid_region_factors.get_CO2_factors_as_df().multiply(hourly_electric_MWH, axis=0)).sum().tolist()
    )
    return total_annual_CO2


def get_annual_gas_cost(
    _gas_used: bool,
    _ep_meter_data: pd.DataFrame,
    _gas_purchase_price: float,
    _gas_annual_base_price: float,
) -> float:
    """Return the total annual gas cost for the building."""

    TONS_CO2_PER_JOULE = 0.000000009478169879
    FIELD_NAME = "NaturalGas:Facility [J](Monthly) "

    if not _gas_used:
        return 0.0

    t = sum(_ep_meter_data[FIELD_NAME] * TONS_CO2_PER_JOULE)
    return (t * _gas_purchase_price) + _gas_annual_base_price


def get_annual_gas_CO2(
    _gas_used: bool,
    _ep_meter_data: pd.DataFrame,
) -> float:
    NAT_GAS_FIELD_NAME = "NaturalGas:Facility [J](Monthly) "
    TONS_CO2_PER_JOULE = 0.000000009478169879
    # TODO: What is is constant?
    SOME_CONSTANT = 12.7

    if not _gas_used:
        return 0.0

    return sum(_ep_meter_data[NAT_GAS_FIELD_NAME] * TONS_CO2_PER_JOULE) * SOME_CONSTANT


def get_carbon_measures_cost(
    _construction_cost_est_table: list[list[list[str | float]]],
    _variant_CO2_measures: PhAdorbCO2MeasureCollection,
) -> tuple[list[YearlyCost], YearlyCost]:
    """Return the total annual cost of all the Carbon Measures, and the first cost."""

    CO2_measure_costs = [YearlyCost(measure.cost, measure.year) for measure in _variant_CO2_measures]

    # -- Find the first cost of the Carbon Measures
    ROW_SEARCH_NAME = "Cost Estimate Total ($)"
    table_data = _construction_cost_est_table[1]  # ['Construction Cost Estimate Summary', [...]]
    for row in table_data:
        if ROW_SEARCH_NAME in row:
            first_costs = YearlyCost(float(row[2]), 0)
            break
    else:
        raise ValueError(f"Could not find '{ROW_SEARCH_NAME}' in the construction cost estimate table?")

    CO2_measure_costs.append(first_costs)
    return CO2_measure_costs, first_costs


def get_carbon_measures_embodied_CO2(
    _variant_CO2_measures: PhAdorbCO2MeasureCollection,
    _kg_CO2_per_USD: float,
) -> list[YearlyCost]:
    """Return the total annual embodied CO2 cost of all the Carbon Measures."""

    # -------------------------------------------------------------------------------
    # TODO: CHANGE TO USE COUNTRY INDEX, 0 for US,
    embodied_CO2_cost: list[YearlyCost] = []

    for measure in _variant_CO2_measures:
        material_cost = measure.cost * _kg_CO2_per_USD * measure.material_fraction
        labor_cost = measure.cost * _kg_CO2_per_USD * measure.labor_fraction
        total_cost = material_cost + labor_cost
        embodied_CO2_cost.append(YearlyCost(total_cost, measure.year))

    # TODO: Labor fraction should be subtracted out and have USA EF applied

    return embodied_CO2_cost


def get_carbon_measures_embodied_CO2_first_cost(
    _envelope_labor_cost_fraction: float,
    _first_costs: YearlyCost,
    _kg_CO2_per_USD: float,
) -> YearlyCost:
    """Return the first cost of the embodied CO2 for the Carbon Measures."""

    material_fraction: float = 1.0 - _envelope_labor_cost_fraction
    material_first_cost = _first_costs.cost * material_fraction * _kg_CO2_per_USD
    labor_first_cost = _first_costs.cost * _envelope_labor_cost_fraction * _kg_CO2_per_USD
    total_first_cost = material_first_cost + labor_first_cost

    return YearlyCost(total_first_cost, 0)
