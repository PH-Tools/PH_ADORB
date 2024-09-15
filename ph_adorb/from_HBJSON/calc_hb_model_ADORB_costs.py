# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Run script to calculate ADORB Costs from a Honeybee-Model's HBJSON.

This script is called from the command line with the following arguments:
    * [1] (str): The path to the HBJSON file to read in.
    * [2] (str): The path to the output CSV file.
"""

import os
import sys
from pathlib import Path

from ph_adorb.adorb_cost import calculate_variant_ADORB_costs
from ph_adorb.from_HBJSON import create_variant, read_HBJSON_file


class InputFileError(Exception):
    def __init__(self, path) -> None:
        self.msg = f"\nCannot find the specified HBJSON file:'{path}'"
        super().__init__(self.msg)


def resolve_paths(_args: list[str]) -> tuple[Path, Path]:
    """Sort out the file input and output paths. Make the output directory if needed.

    Arguments:
    ----------
        * _args (list[str]): sys.args list of input arguments.

    Returns:
    --------
        * Tuple
            - [1] (str): The HBJSON Source file path.
            - [2] (str): The ADORB CSV Target path.
    """

    print(">> Resolving file paths...")
    assert len(_args) == 3, "Error: Incorrect number of arguments."

    # -- Check if the HBJSON file exists.
    hbjson_source_filepath = Path(_args[1])
    if not hbjson_source_filepath.exists():
        raise InputFileError(hbjson_source_filepath)

    # -- If the folder of the target_csv_filepath does not exist, make it.
    target_csv_filepath = Path(_args[2])
    target_dir = target_csv_filepath.parent
    if not target_dir.exists():
        os.mkdir(target_dir)

    # -- If the target CSV already exists, delete it.
    if target_csv_filepath.exists():
        os.remove(target_csv_filepath)

    return hbjson_source_filepath, target_csv_filepath


if __name__ == "__main__":
    print("- " * 50)
    print(f">> Using Python: {sys.version}")
    print(f">> Running the script: '{__file__.split('/')[-1]}'")
    print(f">> With the arguments:")
    print("\n".join([f"\t{i} | {a}" for i, a in enumerate(sys.argv)]))

    # --- Input / Output file Path
    # -------------------------------------------------------------------------
    SOURCE_HBJSON_FILE, TARGET_CSV_FILE = resolve_paths(sys.argv)
    print(f">> Source HBJSON File: '{SOURCE_HBJSON_FILE}'")
    print(f">> Target CSV File: '{TARGET_CSV_FILE}'")

    # --- Read in the existing HB_JSON and re-build the HB Model
    # -------------------------------------------------------------------------
    hb_json_dict = read_HBJSON_file.read_hb_json_from_file(SOURCE_HBJSON_FILE)
    hb_model = read_HBJSON_file.convert_hbjson_dict_to_hb_model(hb_json_dict)
    print(f">> HB Model '{hb_model.display_name}' successfully re-built.")

    # --- Generate the Revive Variant.
    revive_variant = create_variant.convert_hb_model_to_ReviveVariant(hb_model)

    # --- Calculate the ADORB cCosts, output as a CSV File
    # -------------------------------------------------------------------------
    variant_ADORB_df = calculate_variant_ADORB_costs(revive_variant)
    variant_ADORB_df.to_csv(TARGET_CSV_FILE)
