# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A script to calculate ADORB Costs from a Honeybee-Model-HBJSON-File, and outputs to a CSV file.

This script is called from the command line with the following arguments:
    * [1] (str): The path to the HBJSON file to read in.
    * [2] (str): The path to the output CSV file.
"""

import os
import sys
from pathlib import Path

from ph_adorb.from_HBJSON import create_variant, read_HBJSON_file
from ph_adorb.variant import calc_variant_ADORB_costs


class InputFileError(Exception):
    def __init__(self, path) -> None:
        self.msg = f"\nCannot find the specified HBJSON file:'{path}'"
        super().__init__(self.msg)


def resolve_paths(_args: list[str]) -> tuple[Path, Path, Path]:
    """Sort out the file input and output paths. Make the output directory if needed.

    Arguments:
    ----------
        * _args (list[str]): sys.args list of input arguments.

    Returns:
    --------
        * Tuple
            - [1] (str): The HBJSON Source file path.
            - [2] (str): The path to the EnergyPlus Results SQL File
            - [3] (str): The ADORB CSV Target path.
    """

    assert len(_args) == 4, "Error: Incorrect number of arguments."

    # -- Check if the HBJSON file exists.
    hbjson_source_filepath = Path(_args[1])
    if not hbjson_source_filepath.exists():
        raise InputFileError(hbjson_source_filepath)

    results_sql_file = Path(_args[2])
    if not results_sql_file.exists():
        raise InputFileError(results_sql_file)

    # -- If the folder of the target_csv_filepath does not exist, make it.
    target_csv_filepath = Path(_args[3])
    target_dir = target_csv_filepath.parent
    if not target_dir.exists():
        os.mkdir(target_dir)

    # -- If the target CSV already exists, delete it.
    if target_csv_filepath.exists():
        os.remove(target_csv_filepath)

    return hbjson_source_filepath, results_sql_file, target_csv_filepath


if __name__ == "__main__":
    print("- " * 50)
    print(f"\t>> Using Python: {sys.version}")
    print(f"\t>> Running the script: '{__file__.split('/')[-1]}'")
    print(f"\t>> With the arguments:")
    print("\n".join([f"\t\t{i} | {a}" for i, a in enumerate(sys.argv)]))

    # --- Input / Output file Path
    # -------------------------------------------------------------------------
    print("\t>> Resolving file paths...")
    INPUT_HBJSON_FILE_PATH, INPUT_SQL_RESULTS_FILE_PATH, OUTPUT_CSV_FILE_PATH = resolve_paths(sys.argv)
    print(f"\t>> Source HBJSON File: '{INPUT_HBJSON_FILE_PATH}'")
    print(f"\t>> Source SQL File: '{INPUT_SQL_RESULTS_FILE_PATH}'")
    print(f"\t>> Target CSV File: '{OUTPUT_CSV_FILE_PATH}'")

    # --- Read in the existing HB-JSON-File
    # -------------------------------------------------------------------------
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
    variant_ADORB_df = calc_variant_ADORB_costs(revive_variant)

    # --- Output the ADORB Costs to a CSV File
    # -------------------------------------------------------------------------
    variant_ADORB_df.to_csv(OUTPUT_CSV_FILE_PATH)
    print("\t>> Done calculating the ADORB Costs. The CSV file has been saved.")
    print("- " * 50)
