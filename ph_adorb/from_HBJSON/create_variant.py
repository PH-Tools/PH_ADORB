# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Create a new Phius ADORB Variant from a Honeybee-Model."""

from typing import Union
from pathlib import Path
from collections import defaultdict

from honeybee.model import Model
from honeybee_energy.construction.opaque import OpaqueConstruction
from honeybee_energy.construction.window import WindowConstruction
from honeybee_energy.load.process import Process
from honeybee_energy.load.lighting import Lighting
from honeybee_energy.generator.pv import PVProperties
from honeybee_energy.properties.model import ModelEnergyProperties
from honeybee_energy.properties.room import RoomEnergyProperties

from honeybee_energy.properties.extension import (
    AllAirSystemProperties,
    DOASSystemProperties,
    HeatCoolSystemProperties,
    IdealAirSystemProperties,
)

AnyHvacSystemProperties = Union[
    AllAirSystemProperties, DOASSystemProperties, HeatCoolSystemProperties, IdealAirSystemProperties
]
from honeybee_energy_revive.hvac.equipment import PhiusReviveHVACEquipment
from honeybee_revive.properties.model import ModelReviveProperties
from honeybee_energy_revive.properties.construction.opaque import OpaqueConstructionReviveProperties
from honeybee_energy_revive.properties.load.process import ProcessReviveProperties
from honeybee_energy_revive.properties.load.lighting import LightingReviveProperties
from honeybee_energy_revive.properties.generator.pv import PVPropertiesReviveProperties
from honeybee_energy_revive.properties.hvac.allair import AllAirSystemReviveProperties
from honeybee_energy_revive.properties.hvac.doas import DOASSystemReviveProperties
from honeybee_energy_revive.properties.hvac.heatcool import HeatCoolSystemReviveProperties
from honeybee_energy_revive.properties.hvac.idealair import IdealAirSystemReviveProperties

AnyHvacSystemReviveProperties = Union[
    AllAirSystemReviveProperties,
    DOASSystemReviveProperties,
    HeatCoolSystemReviveProperties,
    IdealAirSystemReviveProperties,
]

from ph_adorb.constructions import PhAdorbConstructionCollection
from ph_adorb.ep_csv_file import DataFileCSV, load_full_hourly_ep_output, load_monthly_meter_ep_output
from ph_adorb.ep_html_file import (
    DataFileEPTables,
    load_construction_cost_estimate_data,
    load_peak_electric_usage_data,
)
from ph_adorb.equipment import (
    PhAdorbEquipment,
    PhAdorbEquipmentCollection,
    PhAdorbEquipmentType,
)
from ph_adorb.fuel import PhAdorbFuel, PhAdorbFuelType
from ph_adorb.grid_region import PhAdorbGridRegion, load_CO2_factors_from_json_file
from ph_adorb.measures import PhAdorbCO2MeasureCollection, PhAdorbCO2ReductionMeasure
from ph_adorb.national_emissions import PhAdorbNationalEmissions
from ph_adorb.variant import PhAdorbVariant
from ph_adorb.constructions import PhAdorbConstruction


# TODO: Add error / warning messages if GridRegion and NationalEmissions are not set in the HB-Model.


def get_hb_model_construction_quantities(_hb_model: Model) -> dict[str, float]:
    """Return a dictionary of total construction quantities (areas) from the HB-Model."""
    construction_quantities_ = defaultdict(float)
    for face in _hb_model.faces:
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
                measure_type=co2_measure.measure_type.value,
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
        name=_hb_hvac_equip.identifier,
        equipment_type=PhAdorbEquipmentType.MECHANICAL,
        cost=_hb_hvac_equip.cost,
        lifetime_years=_hb_hvac_equip.lifetime_years,
        labor_fraction=_hb_hvac_equip.labor_fraction,
    )


def get_PhAdorbEquipment_from_hb_model(_hb_model: Model) -> PhAdorbEquipmentCollection:
    """Return a EquipmentCollection with all of the Equipment (Appliances, HVAC, etc...) from the HB-Model."""

    equipment_collection_ = PhAdorbEquipmentCollection()

    # -- Add all of the Appliances from all of the HB-Rooms
    for room in _hb_model.rooms:
        room_prop: RoomEnergyProperties = getattr(room.properties, "energy")
        for process_load in room_prop.process_loads:
            equipment_collection_.add_equipment(convert_hb_process_load(process_load))

        equipment_collection_.add_equipment(convert_hbe_lighting(room_prop.lighting))

    # -- Add all the Shades with PV on them
    for shade in _hb_model.shades:
        if not shade.properties.energy.pv_properties:
            continue
        equipment_collection_.add_equipment(convert_hb_shade_pv(shade.properties.energy.pv_properties))

    # -- Add all of the HVAC Equipment
    for room in _hb_model.rooms:
        room_prop: RoomEnergyProperties = getattr(room.properties, "energy")
        if not room_prop.hvac:
            continue

        hvac_props: AnyHvacSystemProperties = getattr(room_prop.hvac, "properties")
        hvac_prop_revive: AnyHvacSystemReviveProperties = getattr(hvac_props, "revive")
        for hb_hvac_equip in hvac_prop_revive.equipment_collection:
            equipment_collection_.add_equipment(convert_hb_hvac_equipment(hb_hvac_equip))

    # TODO: Batteries....
    equipment_collection_.add_equipment(
        PhAdorbEquipment(
            name="Battery",
            equipment_type=PhAdorbEquipmentType.BATTERY,
            cost=3_894.54,
            lifetime_years=10,
            labor_fraction=0.5,
        )
    )

    return equipment_collection_


def get_PhAdorbVariant_from_hb_model(_hb_model: Model) -> PhAdorbVariant:
    """Convert the HB-Model to a new ReviveVariant object.

    Arguments:
    ----------
        * hb_model (HB_Model): The Honeybee Model to convert.

    Returns:
    --------
        * ReviveVariant: The ReviveVariant object.
    """

    # -----------------------------------------------------------------------------------
    # -- Input File Paths
    input_dir_path = Path("/Users/em/Dropbox/bldgtyp-00/00_PH_Tools/PH_ADORB/tests/_test_input")
    ep_full_hourly_results_csv = input_dir_path / "example_full_hourly.csv"
    ep_monthly_meter_results_csv = input_dir_path / "example_monthly_meter.csv"
    ep_table_results = input_dir_path / "example_annual_tables.htm"

    # -----------------------------------------------------------------------------------
    # -- Load the EnergyPlus Simulation Result CSV Data
    ep_hourly_results = DataFileCSV(source_file_path=ep_full_hourly_results_csv, loader=load_full_hourly_ep_output)
    ep_hourly_results.load_file_data()

    ep_meter_results = DataFileCSV(source_file_path=ep_monthly_meter_results_csv, loader=load_monthly_meter_ep_output)
    ep_meter_results.load_file_data()

    # -----------------------------------------------------------------------------------
    # -- Load the EnergyPlus Simulation Result HTML Data
    construction_cost_estimate = DataFileEPTables[list](
        source_file_path=ep_table_results, loader=load_construction_cost_estimate_data
    )
    construction_cost_estimate.load_file_data()

    peak_electric_usage_W = DataFileEPTables[float](
        source_file_path=ep_table_results, loader=load_peak_electric_usage_data
    )
    peak_electric_usage_W.load_file_data()

    # -----------------------------------------------------------------------------------
    # -- Setup the Variant's Fuel Types and Costs
    electricity = PhAdorbFuel(
        fuel_type=PhAdorbFuelType.ELECTRICITY,
        purchase_price=0.102,
        sale_price=0.6,
        annual_base_price=100.0,
        used=True,
    )
    gas = PhAdorbFuel(
        fuel_type=PhAdorbFuelType.NATURAL_GAS,
        purchase_price=0.102,
        sale_price=0.0,
        annual_base_price=480.0,
        used=True,
    )

    # -----------------------------------------------------------------------------------
    # -- Create the actual Variant
    hb_model_properties: ModelReviveProperties = getattr(_hb_model.properties, "revive")
    revive_variant = PhAdorbVariant(
        name=_hb_model.display_name or "unnamed",
        ep_hourly_results_df=ep_hourly_results.data,
        ep_meter_results_df=ep_meter_results.data,
        construction_cost_estimate=construction_cost_estimate.data,
        peak_electric_usage_W=peak_electric_usage_W.data,
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

    return revive_variant
