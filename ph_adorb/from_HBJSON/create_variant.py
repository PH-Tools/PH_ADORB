# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Create a new Phius ADORB Variant from a Honeybee-Model."""

from pathlib import Path

from honeybee.model import Model
from honeybee_revive.properties.model import ModelReviveProperties

from ph_adorb.constructions import ConstructionCollection, load_constructions_from_json_file
from ph_adorb.ep_csv_file import DataFileCSV, load_full_hourly_ep_output, load_monthly_meter_ep_output
from ph_adorb.ep_html_file import (
    DataFileEPTables,
    load_construction_cost_estimate_data,
    load_construction_quantities_data,
    load_peak_electric_usage_data,
)
from ph_adorb.equipment import Equipment, EquipmentCollection, EquipmentType, load_equipment_from_json_file
from ph_adorb.fuel import Fuel, FuelType
from ph_adorb.grid_region import GridRegion, load_CO2_factors_from_json_file
from ph_adorb.measures import CO2MeasureCollection, CO2ReductionMeasure
from ph_adorb.national_emissions import NationalEmissions
from ph_adorb.variant import ReviveVariant

# TODO: Create the Variant from the HBJSON file data....

# TODO: Add error / warning messages if GridRegion and NationalEmissions are not set in the HB-Model.


def get_hb_model_GridRegion(_hb_model_prop: ModelReviveProperties) -> GridRegion:
    """Get the Grid Region name from the HB-Model and load the data from file."""
    grid_region_data_path = Path(_hb_model_prop.grid_region.filepath)
    return load_CO2_factors_from_json_file(grid_region_data_path)


def get_hb_model_NationalEmissions(_hb_model_prop: ModelReviveProperties) -> NationalEmissions:
    """Get the National Emissions data from the HB-Model."""
    return NationalEmissions(**_hb_model_prop.national_emissions_factors.to_dict())


def get_hb_model_CO2_measures(_hb_model_prop: ModelReviveProperties) -> CO2MeasureCollection:
    """Get all of the CO2 Reduction Measures from the HB-Model."""
    measure_collection_ = CO2MeasureCollection()
    for co2_measure in _hb_model_prop.co2_measures:
        measure_collection_.add_measure(
            CO2ReductionMeasure(
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


def get_hb_model_constructions(_hb_model: Model, constructions_path, construction_quantities) -> ConstructionCollection:

    # TODO: Refactor this to use the HB Model Constructions
    all_constructions_from_database = load_constructions_from_json_file(constructions_path)
    used_constructions = ConstructionCollection()
    used_constructions.add_construction(all_constructions_from_database["Exterior Wall"])
    used_constructions.add_construction(all_constructions_from_database["Exterior Roof"])
    used_constructions.add_construction(all_constructions_from_database["Exterior Slab UnIns"])
    used_constructions.add_construction(all_constructions_from_database["Interior Floor"])
    used_constructions.add_construction(all_constructions_from_database["EXT_Door1"])
    used_constructions.add_construction(all_constructions_from_database["Interior Wall"])
    used_constructions.add_construction(all_constructions_from_database["Window_U-0.5 g=0.4"])
    used_constructions.set_constructions_ft2_quantities(construction_quantities.data)

    return used_constructions


def get_hb_model_equipment(_hb_model: Model, equipment_path) -> EquipmentCollection:

    # TODO: Refactor this to get equipment from the HB-Model

    all_equipment_from_database = load_equipment_from_json_file(equipment_path)
    used_equipment = EquipmentCollection()
    used_equipment.add_equipment(all_equipment_from_database["GasFurnaceDXAC"])
    used_equipment.add_equipment(all_equipment_from_database["GasBoiler"])
    used_equipment.add_equipment(all_equipment_from_database["Refrigerator [360]"])
    used_equipment.add_equipment(all_equipment_from_database["Clothes Wash [160]"])
    used_equipment.add_equipment(all_equipment_from_database["Clothes Dryer"])
    used_equipment.add_equipment(all_equipment_from_database["Cooktop"])
    used_equipment.add_equipment(all_equipment_from_database["Dishwasher [360]"])
    used_equipment.add_equipment(all_equipment_from_database["Lights [60]"])

    # TODO: How to handle PV and Batteries? How is Al doing it?
    used_equipment.add_equipment(
        Equipment(
            name="PV Array",
            equipment_type=EquipmentType.PV_ARRAY,
            cost=5,
            lifetime_years=25,
            labor_fraction=0.25,
        )
    )
    used_equipment.add_equipment(
        Equipment(
            name="Battery",
            equipment_type=EquipmentType.BATTERY,
            cost=3_894.54,
            lifetime_years=10,
            labor_fraction=0.5,
        )
    )
    return used_equipment


def convert_hb_model_to_ReviveVariant(_hb_model: Model) -> ReviveVariant:
    """Convert the HB-Model to a new ReviveVariant object.

    Arguments:
    ----------
        * hb_model (HB_Model): The Honeybee Model to convert.

    Returns:
    --------
        * ReviveVariant: The ReviveVariant object.
    """

    # -----------------------------------------------------------------------------------
    # -- Resource File Paths
    data_dir_path = Path("/Users/em/Dropbox/bldgtyp-00/00_PH_Tools/PH_ADORB/ph_adorb/data")
    constructions_path = data_dir_path / "constructions.json"
    equipment_path = data_dir_path / "equipment.json"

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

    construction_quantities = DataFileEPTables[dict[str, float]](
        source_file_path=ep_table_results, loader=load_construction_quantities_data
    )
    construction_quantities.load_file_data()

    peak_electric_usage_W = DataFileEPTables[float](
        source_file_path=ep_table_results, loader=load_peak_electric_usage_data
    )
    peak_electric_usage_W.load_file_data()

    # -----------------------------------------------------------------------------------
    # -- Setup the Variant's Fuel Types and Costs
    electricity = Fuel(
        fuel_type=FuelType.ELECTRICITY,
        purchase_price=0.102,
        sale_price=0.6,
        annual_base_price=100.0,
        used=True,
    )
    gas = Fuel(
        fuel_type=FuelType.NATURAL_GAS,
        purchase_price=0.102,
        sale_price=0.0,
        annual_base_price=480.0,
        used=True,
    )

    # -----------------------------------------------------------------------------------
    # -- Create the actual Variant
    hb_model_properties: ModelReviveProperties = getattr(_hb_model.properties, "revive")
    revive_variant = ReviveVariant(
        name=_hb_model.display_name or "unnamed",
        ep_hourly_results_df=ep_hourly_results.data,
        ep_meter_results_df=ep_meter_results.data,
        construction_cost_estimate=construction_cost_estimate.data,
        peak_electric_usage_W=peak_electric_usage_W.data,
        electricity=electricity,
        gas=gas,
        grid_region=get_hb_model_GridRegion(hb_model_properties),
        national_emissions=get_hb_model_NationalEmissions(hb_model_properties),
        analysis_duration=hb_model_properties.analysis_duration,
        envelope_labor_cost_fraction=hb_model_properties.envelope_labor_cost_fraction,
        measure_collection=get_hb_model_CO2_measures(hb_model_properties),
        construction_collection=get_hb_model_constructions(_hb_model, constructions_path, construction_quantities),
        equipment_collection=get_hb_model_equipment(_hb_model, equipment_path),
    )

    return revive_variant
