# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A script to generate an ADORB Costs graph from a CSV file.

This script is called from the command line with the following arguments:
    * [1] (str): The path to the CSV file to read in.
    * [2] (str): The path to the folder to save the graphs to.
"""

from collections import namedtuple
import os
import sys

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio


class InputFileError(Exception):
    def __init__(self, path) -> None:
        self.msg = f"\nCannot find the specified HBJSON file:'{path}'"
        super().__init__(self.msg)


Filepaths = namedtuple(
    "Filepaths",
    [
        "csv",
        "output",
    ],
)


def resolve_paths(_args: list[str]) -> Filepaths:
    """Sort out the file input and output paths. Make the output directory if needed.

    Arguments:
    ----------
        * _args (list[str]): sys.args list of input arguments.

    Returns:
    --------
        * Filepaths
    """

    assert len(_args) == 3, "Error: Incorrect number of arguments. Expected 2, got {}.".format(len(_args))

    # -----------------------------------------------------------------------------------
    # -- The HBJSON input file.
    csv_source_filepath = Path(_args[1])
    if not csv_source_filepath.exists():
        raise InputFileError(csv_source_filepath)

    # -----------------------------------------------------------------------------------
    # -- Graph output folder:
    output_filepath = Path(_args[2])
    if not output_filepath.parent.exists():
        print(f"\t>> Creating the directory: {output_filepath.parent}")
        os.mkdir(output_filepath.parent)

    # -- Make sure it is an HTML output
    output_filepath_ = output_filepath.parent / f"{output_filepath.stem}.html"

    return Filepaths(csv_source_filepath, output_filepath_)


if __name__ == "__main__":
    print("- " * 50)
    print(f"\t>> Using Python: {sys.version}")
    print(f"\t>> Running the script: '{__file__.split('/')[-1]}'")
    print(f"\t>> With the arguments:")
    print("\n".join([f"\t\t{i} | {a}" for i, a in enumerate(sys.argv)]))

    # --- Input / Output file Path
    # -------------------------------------------------------------------------
    print("\t>> Resolving file paths...")
    file_paths = resolve_paths(sys.argv)
    print(f"\t>> Source CSV File: '{file_paths.csv}'")
    print(f"\t>> Target Folder: '{file_paths.output}'")

    df = pd.read_csv(file_paths.csv)

    # -------------------------------------------------------------------------
    fig = go.Figure()
    fig.update_layout(title="test")
    # Add each category as a trace
    for column in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df[column], mode="lines", stackgroup="one", name=column  # Creates stacking behavior
            )
        )

    with open(file_paths.output, "w") as f:
        f.write(pio.to_html(fig, full_html=False, include_plotlyjs="cdn"))

    print("\t>> Done generating the ADORB Cost Graphs.")
    print("- " * 50)
