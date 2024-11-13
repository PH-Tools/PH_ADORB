# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""
This script is an example of how to calculate ADORB Costs from a Honeybee-Model-HBJSON-File, 
and output the results to a CSV file. THis script uses test-files which are stored locally to 
provide the relevant inputs (HBJSON) and the outputs should be saved to a local directory as well.
"""


from pathlib import Path

from ph_adorb.from_HBJSON import create_variant, read_HBJSON_file
from ph_adorb.variant import calc_variant_yearly_ADORB_costs

# --- Input / Output file Path
# -------------------------------------------------------------------------
INPUT_HBJSON_FILE_PATH = Path("tests/_test_input/example.hbjson")
INPUT_SQL_RESULTS_FILE_PATH = Path("tests/_test_input/example_full_hourly.sql")
OUTPUT_CSV_FILE_PATH = Path("tests/_test_output/example.csv")

if __name__ == "__main__":
    # --- Read in the existing HB-JSON-File
    # -------------------------------------------------------------------------
    print("- " * 50)
    print(f"Loading the Honeybee-Model from the HBJSON file: {INPUT_HBJSON_FILE_PATH}")
    hb_json_dict = read_HBJSON_file.read_hb_json_from_file(INPUT_HBJSON_FILE_PATH)

    # -- Re-Build the Honeybee-Model from the HBJSON-Dict
    # -------------------------------------------------------------------------
    hb_model = read_HBJSON_file.convert_hbjson_dict_to_hb_model(hb_json_dict)
    print(f">> Honeybee-Model '{hb_model.display_name}' successfully re-built from file.")

    # --- Generate the PH-ADORB-Variant from the Honeybee-Model
    revive_variant = create_variant.get_PhAdorbVariant_from_hb_model(hb_model, INPUT_SQL_RESULTS_FILE_PATH)

    # --- Get the ADORB Costs for the PH-ADORB-Variant
    # -------------------------------------------------------------------------
    variant_ADORB_df = calc_variant_yearly_ADORB_costs(
        revive_variant, _output_tables_path=Path("tests/_test_output/tables")
    )

    # --- Output the ADORB Costs to a CSV File
    # -------------------------------------------------------------------------
    variant_ADORB_df.to_csv(OUTPUT_CSV_FILE_PATH)
    print(f">> The CSV file has been saved to: {OUTPUT_CSV_FILE_PATH}")
    print(">> Done calculating the ADORB Costs.")
    print("- " * 50)
