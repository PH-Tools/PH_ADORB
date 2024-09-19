## - An Example of the ADORB Cost Calculation Process

from pathlib import Path

import pandas as pd
from pytest import approx
from rich import print

from ph_adorb.adorb_cost import calculate_variant_ADORB_costs
from ph_adorb.constructions import PhAdorbConstructionCollection, load_constructions_from_json_file
from ph_adorb.ep_csv_file import DataFileCSV, load_full_hourly_ep_output, load_monthly_meter_ep_output
from ph_adorb.ep_html_file import (
    DataFileEPTables,
    load_construction_cost_estimate_data,
    load_construction_quantities_data,
    load_peak_electric_usage_data,
)
from ph_adorb.equipment import (
    PhAdorbEquipment,
    PhAdorbEquipmentCollection,
    PhAdorbEquipmentType,
    load_equipment_from_json_file,
)
from ph_adorb.fuel import PhAdorbFuel, PhAdorbFuelType
from ph_adorb.grid_region import load_CO2_factors_from_json_file
from ph_adorb.measures import PhAdorbCO2MeasureCollection, load_CO2_measures_from_json_file
from ph_adorb.national_emissions import load_national_emissions_from_json_file
from ph_adorb.variant import PhAdorbVariant


def test_result_csv_file_values(_output_path: Path):
    # -----------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------
    # TEST THE RESULTING CSV FILE VALUES TO ENSURE ALL THE VALUES ARE THE SAME AS AL'S
    print("Testing the resulting CSV file.....", end="")
    output_csv_path = _output_path / "Test_Variant_ADORBresults.csv"
    assert output_csv_path.exists(), "The ADORB results CSV file was not created."

    result_df = pd.read_csv(output_csv_path)
    row_number, column_number = result_df.shape
    assert row_number == 50, f"Result CSV has the wrong number of rows. Got: {row_number}"
    assert column_number == 6, f"Result CSV has the wrong number of columns. Got: {column_number}"

    pv_direct = result_df["pv_direct_energy"].sum()
    assert pv_direct == approx(54831.2503), f"'pv_direct_energy' is incorrect. Got: {pv_direct}"

    pv_operational_CO2 = result_df["pv_operational_CO2"].sum()
    # OLD (with sorting error):
    # assert pv_operational_CO2 == approx(47328.76858), f"pv_operational_CO2is incorrect. Got: {pv_operational_CO2}"
    assert pv_operational_CO2 == approx(
        48212.80251852233
    ), f"'pv_operational_CO2' is incorrect. Got: {pv_operational_CO2}"

    pv_direct_MR = result_df["pv_direct_MR"].sum()
    assert pv_direct_MR == approx(39862.77294), f"'pv_direct_MR' is incorrect. Got: {pv_direct_MR}"

    pv_embodied_CO2 = result_df["pv_embodied_CO2"].sum()
    assert pv_embodied_CO2 == approx(4318.927631), f"'pv_embodied_CO2' is incorrect. Got: {pv_embodied_CO2}"

    pv_e_trans = result_df["pv_e_trans"].sum()
    assert pv_e_trans == approx(8257.006251), f"'pv_e_trans' is incorrect. Got: {pv_e_trans}"
    print("[green]all tests pass![/green]")


# ---------------------------------------------------------------------------------------
if __name__ == "__main__":
    print("- " * 50)
    # -----------------------------------------------------------------------------------
    # -- Define Region Settings
    variant_name = "Test_Variant"
    country_name = "USA"
    grid_region_name = "NWPPc"

    # -----------------------------------------------------------------------------------
    # -- Resource File Paths
    data_dir_path = Path("ph_adorb/data")
    national_emissions_path = data_dir_path / "national_emissions.json"
    grid_region_data_path = data_dir_path / "cambium_factors" / "NWPPc.json"
    measures_path = data_dir_path / "measures.json"
    constructions_path = data_dir_path / "constructions.json"
    equipment_path = data_dir_path / "equipment.json"

    # -- Input File Paths
    input_dir_path = Path("tests/_test_input")
    ep_full_hourly_results_csv = input_dir_path / "example_full_hourly.csv"
    ep_monthly_meter_results_csv = input_dir_path / "example_monthly_meter.csv"
    ep_table_results = input_dir_path / "example_annual_tables.htm"

    # -- Output File Paths
    output_dir_path = Path("tests/_test_output")
    ADORB_results_csv_path = output_dir_path / f"{variant_name}_ADORBresults.csv"

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
    grid_region = load_CO2_factors_from_json_file(grid_region_data_path)

    # -- Variant Measures
    all_measures_from_database = load_CO2_measures_from_json_file(measures_path)
    used_measures = PhAdorbCO2MeasureCollection()
    used_measures.add_measure(all_measures_from_database["HP Replace 1"])
    used_measures.add_measure(all_measures_from_database["HP Replace 2"])
    used_measures.add_measure(all_measures_from_database["HP Replace 3"])

    # -- Variant Constructions
    all_constructions_from_database = load_constructions_from_json_file(constructions_path)
    used_constructions = PhAdorbConstructionCollection()
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
    used_equipment = PhAdorbEquipmentCollection()
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
        PhAdorbEquipment(
            name="PV Array",
            equipment_type=PhAdorbEquipmentType.PV_ARRAY,
            cost=5,
            lifetime_years=25,
            labor_fraction=0.25,
        )
    )
    used_equipment.add_equipment(
        PhAdorbEquipment(
            name="Battery",
            equipment_type=PhAdorbEquipmentType.BATTERY,
            cost=3_894.54,
            lifetime_years=10,
            labor_fraction=0.5,
        )
    )

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
    # -- Setup a Variant with all its required attributes
    variant = PhAdorbVariant(
        name=variant_name,
        ep_hourly_results_df=ep_hourly_results.data,
        ep_meter_results_df=ep_meter_results.data,
        construction_cost_estimate=construction_cost_estimate.data,
        peak_electric_usage_W=peak_electric_usage_W.data,
        electricity=electricity,
        gas=gas,
        grid_region=grid_region,
        national_emissions=national_emissions[country_name],
        analysis_duration=50,
        envelope_labor_cost_fraction=0.4,
        measure_collection=used_measures,
        construction_collection=used_constructions,
        equipment_collection=used_equipment,
    )

    # -- Calculate the actual ADORB yearly costs
    variant_ADORB_df = calculate_variant_ADORB_costs(variant)

    # -- Output the ADORB results to a new CSV file
    variant_ADORB_df.to_csv(ADORB_results_csv_path)

    # -- Test the resulting CSV values
    test_result_csv_file_values(output_dir_path)
