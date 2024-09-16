# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Electricity Grid Region with Hourly CO2 Emissions Factors."""

import json
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field


class GridRegion(BaseModel):
    """Regional CO2 Emissions Factors for single Electricity Grid Region."""

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


def write_CO2_factors_to_json_file(_file_path: Path, _grid_region: GridRegion):
    """Write the CO2 factors for the grid-region to a JSON file."""
    with open(_file_path, "w") as json_file:
        json.dump(_grid_region.dict(), json_file, indent=4)


def load_CO2_factors_from_json_file(_file_path: Path) -> GridRegion:
    """Load the CO2 factors for the grid-region from a JSON file."""
    with open(_file_path, "r") as json_file:
        return GridRegion(**json.load(json_file))
