# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Create a new Phius ADORB Variant from a Honeybee-Model."""

from collections import defaultdict
from pathlib import Path
from typing import Union

from honeybee.model import Model
from honeybee_energy.construction.opaque import OpaqueConstruction
from honeybee_energy.construction.window import WindowConstruction
from honeybee_energy.generator.pv import PVProperties
from honeybee_energy.load.lighting import Lighting
from honeybee_energy.load.process import Process
from honeybee_energy.properties.extension import (
    AllAirSystemProperties,
    DOASSystemProperties,
    HeatCoolSystemProperties,
    IdealAirSystemProperties,
)
from honeybee_energy.properties.model import ModelEnergyProperties
from honeybee_energy.properties.room import RoomEnergyProperties
from honeybee_energy.properties.shade import ShadeEnergyProperties

AnyHvacSystemProperties = Union[
    AllAirSystemProperties, DOASSystemProperties, HeatCoolSystemProperties, IdealAirSystemProperties
]
from honeybee_energy_revive.hvac.equipment import PhiusReviveHVACEquipment
from honeybee_energy_revive.properties.construction.opaque import OpaqueConstructionReviveProperties
from honeybee_energy_revive.properties.generator.pv import PVPropertiesReviveProperties
from honeybee_energy_revive.properties.hvac.allair import AllAirSystemReviveProperties
from honeybee_energy_revive.properties.hvac.doas import DOASSystemReviveProperties
from honeybee_energy_revive.properties.hvac.heatcool import HeatCoolSystemReviveProperties
from honeybee_energy_revive.properties.hvac.idealair import IdealAirSystemReviveProperties
from honeybee_energy_revive.properties.load.lighting import LightingReviveProperties
from honeybee_energy_revive.properties.load.process import ProcessReviveProperties
from honeybee_revive.properties.model import ModelReviveProperties

AnyHvacSystemReviveProperties = Union[
    AllAirSystemReviveProperties,
    DOASSystemReviveProperties,
    HeatCoolSystemReviveProperties,
    IdealAirSystemReviveProperties,
]

from ph_adorb.constructions import PhAdorbConstruction, PhAdorbConstructionCollection
from ph_adorb.ep_sql_file import DataFileSQL
from ph_adorb.equipment import PhAdorbEquipment, PhAdorbEquipmentCollection, PhAdorbEquipmentType
from ph_adorb.fuel import PhAdorbFuel, PhAdorbFuelType
from ph_adorb.grid_region import PhAdorbGridRegion, load_CO2_factors_from_json_file
from ph_adorb.measures import PhAdorbCO2MeasureCollection, PhAdorbCO2ReductionMeasure, CO2MeasureType
from ph_adorb.national_emissions import PhAdorbNationalEmissions
from ph_adorb.variant import PhAdorbVariant

# TODO: Add error / warning messages if GridRegion and NationalEmissions are not set in the HB-Model.


def get_hb_model_construction_quantities(_hb_model: Model) -> dict[str, float]:
    """Return a dictionary of total construction quantities (areas) from the HB-Model."""
    construction_quantities_ = defaultdict(float)
    for face in _hb_model.faces:
        for ap in face.apertures:
            construction_quantities_[ap.properties.energy.construction.identifier] += ap.area
        construction_quantities_[face.properties.energy.construction.identifier] += face.area
    return construction_quantities_


def get_PhAdorbGridRegion_from_hb_model(_hb_model_prop: ModelReviveProperties) -> PhAdorbGridRegion:
    """Get the Grid Region name from the HB-Model and load the data from file."""
    grid_region_data_path = Path(_hb_model_prop.grid_region.filepath)
    return load_CO2_factors_from_json_file(grid_region_data_path)


def get_PhAdorbNationalEmissions_from_hb_mode(_hb_model_prop: ModelReviveProperties) -> PhAdorbNationalEmissions:
    """Get the National Emissions data from the HB-Model."""
    return PhAdorbNationalEmissions(**_hb_model_prop.national_emissions_factors.to_dict())


def get_PhAdorbCO2Measures_from_hb_model(_hb_model_prop: ModelReviveProperties) -> PhAdorbCO2MeasureCollection:
    """Get all of the CO2 Reduction Measures from the HB-Model."""
    measure_collection_ = PhAdorbCO2MeasureCollection()
    for co2_measure in _hb_model_prop.co2_measures:
        measure_collection_.add_measure(
            PhAdorbCO2ReductionMeasure(
                measure_type=CO2MeasureType(co2_measure.measure_type),
                name=co2_measure.name,
                year=co2_measure.year,
                cost=co2_measure.cost,
                kg_CO2=co2_measure.kg_CO2,
                country_name=co2_measure.country_name,
                labor_fraction=co2_measure.labor_fraction,
            )
        )
    return measure_collection_


def convert_hb_construction(_hb_construction: OpaqueConstruction | WindowConstruction) -> PhAdorbConstruction:
    """Convert a Honeybee Opaque Construction to a Phius ADORB Construction."""
    hb_const_prop: OpaqueConstructionReviveProperties = getattr(_hb_construction.properties, "revive")
    return PhAdorbConstruction(
        display_name=_hb_construction.display_name,
        identifier=_hb_construction.identifier,
        CO2_kg_per_m2=hb_const_prop.kg_CO2_per_m2.value,
        cost_per_m2=hb_const_prop.cost_per_m2.value,
        lifetime_years=hb_const_prop.lifetime_years,
        labor_fraction=hb_const_prop.labor_fraction,
    )


def get_PhAdorbConstructions_from_hb_model(_hb_model: Model) -> PhAdorbConstructionCollection:
    """Return a ConstructionCollection with all of the Constructions from the HB-Model."""
    construction_areas = get_hb_model_construction_quantities(_hb_model)

    construction_collection = PhAdorbConstructionCollection()
    model_prop: ModelEnergyProperties = getattr(_hb_model.properties, "energy")
    for construction in model_prop.constructions:
        new_construction = convert_hb_construction(construction)
        new_construction.area_m2 = construction_areas[construction.identifier]
        construction_collection.add_construction(new_construction)

    return construction_collection


def convert_hb_process_load(process_load: Process) -> PhAdorbEquipment:
    """Convert a Honeybee Process-Load to a Phius ADORB Appliance Equipment."""
    process_prop: ProcessReviveProperties = getattr(process_load.properties, "revive")
    return PhAdorbEquipment(
        name=process_load.display_name,
        equipment_type=PhAdorbEquipmentType.APPLIANCE,
        cost=process_prop.cost,
        lifetime_years=process_prop.lifetime_years,
        labor_fraction=process_prop.labor_fraction,
    )


def convert_hbe_lighting(_hb_lighting: Lighting) -> PhAdorbEquipment:
    """Convert a Honeybee-Energy Lighting to a Phius ADORB Lighting Equipment."""
    lighting_prop: LightingReviveProperties = getattr(_hb_lighting.properties, "revive")
    return PhAdorbEquipment(
        name=_hb_lighting.display_name,
        equipment_type=PhAdorbEquipmentType.LIGHTS,
        cost=lighting_prop.cost,
        lifetime_years=lighting_prop.lifetime_years,
        labor_fraction=lighting_prop.labor_fraction,
    )


def convert_hb_shade_pv(_hb_pv: PVProperties) -> PhAdorbEquipment:
    """Convert a Honeybee-Energy PVProperties to a Phius ADORB PV Equipment."""
    pv_prop_revive: PVPropertiesReviveProperties = getattr(_hb_pv.properties, "revive")
    return PhAdorbEquipment(
        name=_hb_pv.display_name,
        equipment_type=PhAdorbEquipmentType.PV_ARRAY,
        cost=pv_prop_revive.cost,
        lifetime_years=pv_prop_revive.lifetime_years,
        labor_fraction=pv_prop_revive.labor_fraction,
    )


def convert_hb_hvac_equipment(_hb_hvac_equip: PhiusReviveHVACEquipment) -> PhAdorbEquipment:
    """Convert a Honeybee-Energy HVAC Equipment to a Phius ADORB HVAC Equipment."""
    return PhAdorbEquipment(
        name=_hb_hvac_equip.display_name,
        equipment_type=PhAdorbEquipmentType.MECHANICAL,
        cost=_hb_hvac_equip.cost,
        lifetime_years=_hb_hvac_equip.lifetime_years,
        labor_fraction=_hb_hvac_equip.labor_fraction,
    )


def get_PhAdorbEquipment_from_hb_model(_hb_model: Model) -> PhAdorbEquipmentCollection:
    """Return a EquipmentCollection with all of the Equipment (Appliances, HVAC, etc...) from the HB-Model."""

    equipment_collection_ = PhAdorbEquipmentCollection()

    for room in _hb_model.rooms:
        room_prop: RoomEnergyProperties = getattr(room.properties, "energy")

        # -- Add all of the Appliances from all of the HB-Rooms
        for process_load in room_prop.process_loads:
            equipment_collection_.add_equipment(convert_hb_process_load(process_load))

        # -- Add the room's lighting
        equipment_collection_.add_equipment(convert_hbe_lighting(room_prop.lighting))

        # -- Add the room's HVAC Equipment
        if not room_prop.hvac:
            continue
        hvac_props: AnyHvacSystemProperties = getattr(room_prop.hvac, "properties")
        hvac_prop_revive: AnyHvacSystemReviveProperties = getattr(hvac_props, "revive")
        for hb_hvac_equip in hvac_prop_revive.equipment_collection:
            equipment_collection_.add_equipment(convert_hb_hvac_equipment(hb_hvac_equip))

    # -- Add all the Model's Shades which have PV on them
    for shade in _hb_model.shades:
        shade_prop_e: ShadeEnergyProperties = getattr(shade.properties, "energy")
        if not shade_prop_e.pv_properties:
            continue
        equipment_collection_.add_equipment(convert_hb_shade_pv(shade_prop_e.pv_properties))

    return equipment_collection_


def get_PhAdorbFuels_from_hb_model(_hb_model: Model) -> tuple[PhAdorbFuel, PhAdorbFuel]:
    """Get the Electric and Natural-Gas Fuels from the HB-Model."""

    model_props: ModelReviveProperties = getattr(_hb_model.properties, "revive")
    hbrv_elec = model_props.fuels.get_fuel("ELECTRICITY")
    hb_nat_gas = model_props.fuels.get_fuel("NATURAL_GAS")

    electricity = PhAdorbFuel(
        fuel_type=PhAdorbFuelType.ELECTRICITY,
        purchase_price_per_kwh=hbrv_elec.purchase_price_per_kwh,
        sale_price_per_kwh=hbrv_elec.sale_price_per_kwh,
        annual_base_price=hbrv_elec.annual_base_price,
        used=True,
    )
    gas = PhAdorbFuel(
        fuel_type=PhAdorbFuelType.NATURAL_GAS,
        purchase_price_per_kwh=hb_nat_gas.purchase_price_per_kwh,
        sale_price_per_kwh=hb_nat_gas.sale_price_per_kwh,
        annual_base_price=hb_nat_gas.annual_base_price,
        used=True,
    )

    return electricity, gas


def get_PhAdorbVariant_from_hb_model(_hb_model: Model, _results_sql_file_path: Path) -> PhAdorbVariant:
    """Convert the HB-Model to a new ReviveVariant object.

    Arguments:
    ----------
        * hb_model (HB_Model): The Honeybee Model to convert.

    Returns:
    --------
        * ReviveVariant: The ReviveVariant object.
    """

    # -----------------------------------------------------------------------------------
    # -- Load in the EnergyPlus Simulation Result .SQL data file
    ep_results_sql = DataFileSQL(source_file_path=_results_sql_file_path)

    # -----------------------------------------------------------------------------------
    # -- Create the actual Variant
    hb_model_properties: ModelReviveProperties = getattr(_hb_model.properties, "revive")
    electricity, gas = get_PhAdorbFuels_from_hb_model(_hb_model)

    try:
        revive_variant = PhAdorbVariant(
            name=_hb_model.display_name or "unnamed",
            total_purchased_gas_kwh=ep_results_sql.get_total_purchased_gas_kwh(),
            hourly_purchased_electricity_kwh=ep_results_sql.get_hourly_purchased_electricity_kwh(),
            total_sold_electricity_kwh=ep_results_sql.get_total_sold_electricity_kwh(),
            peak_electric_usage_W=ep_results_sql.get_peak_electric_watts(),
            electricity=electricity,
            gas=gas,
            grid_region=get_PhAdorbGridRegion_from_hb_model(hb_model_properties),
            national_emissions=get_PhAdorbNationalEmissions_from_hb_mode(hb_model_properties),
            analysis_duration=hb_model_properties.analysis_duration,
            envelope_labor_cost_fraction=hb_model_properties.envelope_labor_cost_fraction,
            measure_collection=get_PhAdorbCO2Measures_from_hb_model(hb_model_properties),
            construction_collection=get_PhAdorbConstructions_from_hb_model(_hb_model),
            equipment_collection=get_PhAdorbEquipment_from_hb_model(_hb_model),
        )
    except Exception as e:
        msg = (
            "An error occurred while reading data from the EnergyPlus SQL file? Please be sure that "
            "you have set all of the required output-variables before running the EnergyPlus simulation"
        )
        raise Exception(msg, e)

    return revive_variant
