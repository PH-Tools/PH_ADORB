# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A Building Variant with all of its relevant data, and related functions."""

import pandas as pd
from pydantic import BaseModel, Field
from pathlib import Path

from ph_adorb.constructions import PhAdorbConstructionCollection
from ph_adorb.equipment import PhAdorbEquipmentCollection
from ph_adorb.fuel import PhAdorbFuel
from ph_adorb.grid_region import PhAdorbGridRegion
from ph_adorb.measures import PhAdorbCO2MeasureCollection
from ph_adorb.national_emissions import PhAdorbNationalEmissions
from ph_adorb.yearly_values import YearlyCost, YearlyKgCO2
from ph_adorb import adorb_cost

from ph_adorb.tables.variant_costs import (
    preview_yearly_install_costs,
    preview_yearly_embodied_CO2_costs,
    preview_yearly_embodied_kgCO2,
    preview_variant_constructions,
    preview_variant_equipment,
)


# ---------------------------------------------------------------------------------------


class PhAdorbVariant(BaseModel):
    """A single Variant of a building design."""

    name: str
    ep_meter_results_df: pd.DataFrame
    hourly_purchased_electricity_kwh: list[float]
    total_purchased_electricity_kwh: float
    total_sold_electricity_kwh: float
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

    price_of_carbon: float = 0.25

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


def calc_annual_total_electric_cost(
    _purchased_electricity_kwh: float,
    _sold_electricity_kwh: float,
    _electric_purchase_price: float,
    _electric_sell_price: float,
    _electric_annual_base_price: float,
) -> float:
    """Return the total annual electricity cost for the building."""

    total_purchased_electric_cost = _purchased_electricity_kwh * _electric_purchase_price
    total_sold_electric_cost = _sold_electricity_kwh * _electric_sell_price
    total_annual_electric_cost = total_purchased_electric_cost - total_sold_electric_cost + _electric_annual_base_price
    return total_annual_electric_cost


def calc_annuals_hourly_electric_CO2(
    _hourly_purchased_electricity_kwh: list[float], _grid_region_factors: PhAdorbGridRegion
) -> list[float]:
    """Return a list of total annual CO2 emissions for each year from 2023 - 2011 (89 years)."""
    MWH_PER_KWH = 0.001

    # -- Convert the hourly purchased electricity from KWH to a pd.Series as MWH
    hourly_electric_MWH = pd.Series(_hourly_purchased_electricity_kwh) * MWH_PER_KWH

    # Multiply each year's factors by the hourly electric MWH list, and sum the results for each year.
    total_annual_CO2: list[float] = (
        (_grid_region_factors.get_CO2_factors_as_df().multiply(hourly_electric_MWH, axis=0)).sum().tolist()
    )
    return total_annual_CO2


def calc_annual_total_gas_cost(
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


def calc_annual_total_gas_CO2(
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


# ---------------------------------------------------------------------------------------
# -- CO2-Reduction-Measures


def calc_CO2_reduction_measures_yearly_embodied_kgCO2(
    _variant_CO2_measures: PhAdorbCO2MeasureCollection,
    _kg_CO2_per_USD: float,
) -> list[YearlyKgCO2]:
    """Return a list of all the Yearly-Embodied-kgCO2 for all the Variant's CO2-Reduction-Measures."""

    # -------------------------------------------------------------------------------
    # TODO: CHANGE TO USE COUNTRY INDEX, 0 for US,
    yearly_embodied_kgCO2_: list[YearlyKgCO2] = []

    for measure in _variant_CO2_measures:
        measure_kgCO2 = measure.cost * _kg_CO2_per_USD
        yearly_embodied_kgCO2_.append(YearlyKgCO2(measure_kgCO2, measure.year, measure.name))

    # TODO: Labor fraction should be subtracted out and have USA EF applied

    return yearly_embodied_kgCO2_


def calc_CO2_reduction_measures_yearly_embodied_CO2_cost(
    _yearly_embodied_kgCO2_: list[YearlyKgCO2], _USD_per_kgCO2=0.25
) -> list[YearlyCost]:
    """Return a list of all the Yearly-Embodied-CO2-Costs for all the Variant's CO2-Reduction-Measures."""
    return [
        YearlyCost(yearly_kgCO2.kg_CO2 * _USD_per_kgCO2, yearly_kgCO2.year, yearly_kgCO2.description)
        for yearly_kgCO2 in _yearly_embodied_kgCO2_
    ]


# TODO: Do  we need this? What is the '_envelope_labor_cost_fraction' doing here?
# def get_first_cost_embodied_CO2_cost(
#     _envelope_labor_cost_fraction: float,
#     _first_costs: YearlyCost,
#     _kg_CO2_per_USD: float,
# ) -> YearlyCost:
#     """Return the first cost of the embodied CO2 for the Carbon Measures."""

#     material_fraction: float = 1.0 - _envelope_labor_cost_fraction
#     material_first_cost = _first_costs.cost * material_fraction * _kg_CO2_per_USD
#     labor_first_cost = _first_costs.cost * _envelope_labor_cost_fraction * _kg_CO2_per_USD
#     total_first_cost = material_first_cost + labor_first_cost

#     return YearlyCost(total_first_cost, 0, "First Cost")


def calc_CO2_reduction_measures_yearly_install_costs(
    _variant_CO2_measures: PhAdorbCO2MeasureCollection,
) -> list[YearlyCost]:
    """Return a list of all the Yearly-Install-Costs (labor + material) for all the Variant's CO2-Reduction-Measures."""
    return [YearlyCost(measure.cost, measure.year, measure.name) for measure in _variant_CO2_measures]


# ---------------------------------------------------------------------------------------
# -- Constructions


def calc_constructions_yearly_embodied_kgCO2(
    _construction_collection: PhAdorbConstructionCollection, _analysis_duration, _kg_CO2_per_USD, _USD_per_kgCO2=0.25
) -> list[YearlyKgCO2]:
    """Return a list of all the Yearly-Embodied-CO2-Costs for all the Variant's Construction Materials."""
    yearly_embodied_kgCO2_: list[YearlyKgCO2] = []
    for const in _construction_collection:
        const_material_dollar_cost: float = const.cost * const.material_fraction
        const_material_embodied_kgCO2: float = const_material_dollar_cost * _kg_CO2_per_USD  # * _price_of_carbon

        if const.lifetime_years == 0:
            yearly_embodied_kgCO2_.append(YearlyKgCO2(const_material_embodied_kgCO2, 0, const.display_name))
        else:
            for year in range(0, _analysis_duration, const.lifetime_years):
                yearly_embodied_kgCO2_.append(YearlyKgCO2(const_material_embodied_kgCO2, year, const.display_name))
    return yearly_embodied_kgCO2_


def calc_constructions_yearly_embodied_CO2_cost(
    _yearly_embodied_kgCO2_: list[YearlyKgCO2], _USD_per_kgCO2=0.25
) -> list[YearlyCost]:
    """Return a list of all the Yearly-Embodied-CO2-Costs for all the Variant's Construction Materials."""
    return [
        YearlyCost(yearly_kgCO2.kg_CO2 * _USD_per_kgCO2, yearly_kgCO2.year, yearly_kgCO2.description)
        for yearly_kgCO2 in _yearly_embodied_kgCO2_
    ]


def calc_constructions_yearly_install_costs(
    _construction_collection: PhAdorbConstructionCollection,
    _analysis_duration,
) -> list[YearlyCost]:
    """Return a list of all the Yearly-Install-Costs (labor + material) for all the Variant's Constructions."""
    yearly_install_costs_ = []
    for const in _construction_collection:
        if const.lifetime_years == 0:
            yearly_install_costs_.append(YearlyCost(const.cost, 0, const.display_name))
        else:
            for year in range(0, _analysis_duration, const.lifetime_years):
                yearly_install_costs_.append(YearlyCost(const.cost, year, const.display_name))
    return yearly_install_costs_


# ---------------------------------------------------------------------------------------
# -- Mechanical Equipment & Appliances


def calc_equipment_yearly_embodied_kgCO2_(
    _equipment_collection: PhAdorbEquipmentCollection, _analysis_duration, _kg_CO2_per_USD
) -> list[YearlyKgCO2]:
    """Return a list of all the Yearly-Embodied-kgCO2 for all the Variant's Equipment."""
    yearly_embodied_kgCO2_: list[YearlyKgCO2] = []
    for equip in _equipment_collection:
        equip_material_cost: float = equip.cost * equip.material_fraction
        equip_material_embodied_CO2_cost: float = equip_material_cost * _kg_CO2_per_USD  # * _price_of_carbon

        if equip.lifetime_years == 0:
            yearly_embodied_kgCO2_.append(YearlyKgCO2(equip_material_embodied_CO2_cost, 0, equip.name))
        else:
            for year in range(0, _analysis_duration, equip.lifetime_years):
                yearly_embodied_kgCO2_.append(YearlyKgCO2(equip_material_embodied_CO2_cost, year, equip.name))
    return yearly_embodied_kgCO2_


def calc_equipment_yearly_embodied_CO2_cost(
    _yearly_embodied_kgCO2_: list[YearlyKgCO2], _USD_per_kgCO2=0.25
) -> list[YearlyCost]:
    """Return a list of all the Yearly-Embodied-CO2-Costs for all the Variant's Equipment."""
    return [
        YearlyCost(yearly_kgCO2.kg_CO2 * _USD_per_kgCO2, yearly_kgCO2.year, yearly_kgCO2.description)
        for yearly_kgCO2 in _yearly_embodied_kgCO2_
    ]


def calc_equipment_yearly_install_costs(
    _equipment_collection: PhAdorbEquipmentCollection,
    _analysis_duration,
) -> list[YearlyCost]:
    """Return a list of all the Yearly-Install-Costs (labor + material) for all the Variant's Equipment."""
    yearly_install_costs_ = []
    for equip in _equipment_collection:
        if equip.lifetime_years == 0:
            yearly_install_costs_.append(YearlyCost(equip.cost, 0, equip.name))
        else:
            for year in range(0, _analysis_duration, equip.lifetime_years):
                yearly_install_costs_.append(YearlyCost(equip.cost, year, equip.name))
    return yearly_install_costs_


# ---------------------------------------------------------------------------------------


def calc_variant_ADORB_costs(_variant: PhAdorbVariant, _output_tables_path: Path | None = None) -> pd.DataFrame:
    """Return a DataFrame with the Variant's ADORB costs for each year of the analysis duration."""

    # -----------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------
    # -- Electric: Annual Costs, Annual CO2
    annual_total_cost_electric = calc_annual_total_electric_cost(
        _variant.total_purchased_electricity_kwh,
        _variant.total_sold_electricity_kwh,
        _variant.electricity.purchase_price,
        _variant.electricity.sale_price,
        _variant.electricity.annual_base_price,
    )
    annual_hourly_CO2_electric = calc_annuals_hourly_electric_CO2(
        _variant.hourly_purchased_electricity_kwh,
        _variant.grid_region,
    )

    # -----------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------
    # -- Gas: Annual Costs, Annual CO2
    annual_total_cost_gas = calc_annual_total_gas_cost(
        _variant.gas.used,
        _variant.ep_meter_results_df,
        _variant.gas.purchase_price,
        _variant.gas.annual_base_price,
    )
    annual_total_CO2_gas = calc_annual_total_gas_CO2(
        _variant.gas.used,
        _variant.ep_meter_results_df,
    )

    # -----------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------
    # -- CO2-REDUCTION-MEASURES Costs
    carbon_measure_yearly_embodied_kgCO2 = calc_CO2_reduction_measures_yearly_embodied_kgCO2(
        _variant.all_carbon_measures,
        _variant.national_emissions.kg_CO2_per_USD,
    )
    carbon_measure_yearly_embodied_CO2_costs = calc_CO2_reduction_measures_yearly_embodied_CO2_cost(
        carbon_measure_yearly_embodied_kgCO2,
        _variant.price_of_carbon,
    )
    carbon_measure_yearly_install_costs = calc_CO2_reduction_measures_yearly_install_costs(_variant.all_carbon_measures)

    # -----------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------
    # -- CONSTRUCTIONS Costs
    construction_yearly_embodied_kgCO2 = calc_constructions_yearly_embodied_kgCO2(
        _variant.construction_collection,
        _variant.analysis_duration,
        _variant.national_emissions.kg_CO2_per_USD,
    )
    construction_yearly_embodied_CO2_costs = calc_constructions_yearly_embodied_CO2_cost(
        construction_yearly_embodied_kgCO2, _variant.price_of_carbon
    )
    construction_yearly_install_costs = calc_constructions_yearly_install_costs(
        _variant.construction_collection,
        _variant.analysis_duration,
    )

    # -----------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------
    # -- HVAC EQUIPMENT AND APPLIANCE Costs
    equipment_yearly_embodied_kgCO2_ = calc_equipment_yearly_embodied_kgCO2_(
        _variant.equipment_collection,
        _variant.analysis_duration,
        _variant.national_emissions.kg_CO2_per_USD,
    )
    equipment_yearly_embodied_CO2_costs = calc_equipment_yearly_embodied_CO2_cost(
        equipment_yearly_embodied_kgCO2_,
        _variant.price_of_carbon,
    )
    equipment_yearly_install_costs = calc_equipment_yearly_install_costs(
        _variant.equipment_collection,
        _variant.analysis_duration,
    )

    # -----------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------
    all_yearly_install_costs = (
        carbon_measure_yearly_install_costs + construction_yearly_install_costs + equipment_yearly_install_costs
    )
    all_yearly_embodied_kgCO2 = (
        carbon_measure_yearly_embodied_kgCO2 + construction_yearly_embodied_kgCO2 + equipment_yearly_embodied_kgCO2_
    )
    all_yearly_embodied_kgCO2_costs = (
        carbon_measure_yearly_embodied_CO2_costs
        + construction_yearly_embodied_CO2_costs
        + equipment_yearly_embodied_CO2_costs
    )

    if _output_tables_path:
        preview_variant_equipment(_variant.equipment_collection, _output_tables_path)
        preview_variant_constructions(_variant.construction_collection, _output_tables_path)
        preview_yearly_install_costs(all_yearly_install_costs, _output_tables_path)
        preview_yearly_embodied_kgCO2(all_yearly_embodied_kgCO2, _output_tables_path)
        preview_yearly_embodied_CO2_costs(all_yearly_embodied_kgCO2_costs, _output_tables_path)

    # -----------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------
    # -- Compute and return the ADORB costs DataFrame
    return adorb_cost.calculate_annual_ADORB_costs(
        _variant.analysis_duration,
        annual_total_cost_electric,
        annual_total_cost_gas,
        annual_hourly_CO2_electric,
        annual_total_CO2_gas,
        all_yearly_install_costs,
        all_yearly_embodied_kgCO2_costs,
        _variant.peak_electric_usage_W,
        _variant.price_of_carbon,
    )
