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
from ph_adorb.grid_region import load_CO2_factors_from_json_file
from ph_adorb.measures import CO2MeasureCollection, load_CO2_measures_from_json_file
from ph_adorb.national_emissions import load_national_emissions_from_json_file
from ph_adorb.variant import ReviveVariant

# TODO: Create the Variant from the HBJSON file data....


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
    # -- Define Region Settings
    variant_name = _hb_model.display_name or "unnamed"
    country_name = "USA"

    # -----------------------------------------------------------------------------------
    # -- Get the Grid Region with CO2 Emission Factors
    hb_model_prop: ModelReviveProperties = getattr(_hb_model.properties, "revive")
    print(f"\t>> Using Cambium Grid Region: {hb_model_prop.grid_region.display_name}")
    grid_region_data_path = Path(hb_model_prop.grid_region.filepath)
    print(f"\t>> Loading the Cambium file: {grid_region_data_path}")
    grid_region_data = load_CO2_factors_from_json_file(grid_region_data_path)

    # -----------------------------------------------------------------------------------
    # -- Resource File Paths
    data_dir_path = Path("/Users/em/Dropbox/bldgtyp-00/00_PH_Tools/PH_ADORB/ph_adorb/data")
    national_emissions_path = data_dir_path / "national_emissions.json"
    measures_path = data_dir_path / "measures.json"
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
    # -- Setup the variant's attributes (constructions, measures, factors, etc.)
    national_emissions = load_national_emissions_from_json_file(national_emissions_path)

    # -- Variant Measures
    all_measures_from_database = load_CO2_measures_from_json_file(measures_path)
    used_measures = CO2MeasureCollection()
    used_measures.add_measure(all_measures_from_database["HP Replace 1"])
    used_measures.add_measure(all_measures_from_database["HP Replace 2"])
    used_measures.add_measure(all_measures_from_database["HP Replace 3"])

    # -- Variant Constructions
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

    # -- Variant Equipment
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
    revive_variant = ReviveVariant(
        name=variant_name,
        ep_hourly_results_df=ep_hourly_results.data,
        ep_meter_results_df=ep_meter_results.data,
        construction_cost_estimate=construction_cost_estimate.data,
        peak_electric_usage_W=peak_electric_usage_W.data,
        electricity=electricity,
        gas=gas,
        grid_region=grid_region_data,
        national_emissions=national_emissions[country_name],
        analysis_duration=50,
        envelope_labor_cost_fraction=0.4,
        measure_collection=used_measures,
        construction_collection=used_constructions,
        equipment_collection=used_equipment,
    )

    return revive_variant
