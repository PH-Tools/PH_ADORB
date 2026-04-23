# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Electricity Grid Region with Hourly CO2 Emissions Factors."""

import json
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field


class PhAdorbGridRegion(BaseModel):
    """Regional CO2 emissions factors for a single electricity grid region.

    Holds hourly CO2 emission rates (kg CO2/MWh) for each projected future year,
    sourced from NREL Cambium data. Used to convert hourly purchased electricity
    into annual operational CO2 emissions.

    Attributes:
        region_code (str): NREL Cambium region code (e.g., "RFCWc").
        region_name (str): Human-readable region name.
        description (str): Description of the grid region.
        hourly_CO2_factors (dict[int, list[float]]): Mapping of year -> 8760 hourly
            CO2 factors (kg CO2/MWh). Keys are integer years (2023-2111).
    """

    region_code: str
    region_name: str
    description: str
    hourly_CO2_factors: dict[int, list[float]] = Field(default_factory=dict)

    def get_CO2_factors_as_df(self) -> pd.DataFrame:
        """
        Returns the CO2 factors as a pandas DataFrame.

        Column=years, rows=hours of the year.
        | Hour | 2023  | 2024  | 2025  |
        |------|-------|-------|-------|
        | 0    | 460.1 | 460.1 | 434.1 |
        | 1    | 469.3 | 475.3 | 445.2 |
        | ...  | ...   | ...   | ...   |
        | 8759 | 460.1 | 460.1 | 434.1 |
        """
        return pd.DataFrame(self.hourly_CO2_factors)


def write_CO2_factors_to_json_file(_file_path: Path, _grid_region: PhAdorbGridRegion):
    """Write the CO2 factors for the grid-region to a JSON file."""
    with open(_file_path, "w") as json_file:
        json.dump(_grid_region.model_dump(), json_file, indent=4)


def load_CO2_factors_from_json_file(_file_path: Path) -> PhAdorbGridRegion:
    """Load the CO2 factors for the grid-region from a JSON file."""
    with open(_file_path, "r") as json_file:
        return PhAdorbGridRegion(**json.load(json_file))
