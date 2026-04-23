# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Country-level CO2 Emissions data per US-Dollar (kg-CO2/$USD)."""

import json
from pathlib import Path

from pydantic import BaseModel


class PhAdorbNationalEmissions(BaseModel):
    """Country-level CO2 emissions intensity per US dollar of economic output.

    Used to convert material dollar costs into embodied kgCO2 via an economic
    input-output proxy for lifecycle assessment.

    Attributes:
        country_name (str): Country name (e.g., "United States").
        us_trading_rank (int): Rank among US trading partners.
        GDP_million_USD (float): Gross domestic product in millions of USD.
        CO2_MT (float): Total national CO2 emissions in megatonnes.
        kg_CO2_per_USD (float): Emissions intensity factor (kg CO2 per USD of GDP).
    """

    country_name: str
    us_trading_rank: int
    GDP_million_USD: float
    CO2_MT: float
    kg_CO2_per_USD: float


def write_national_emissions_to_json_file(
    _file_path: Path, _emissions: dict[str, PhAdorbNationalEmissions]
) -> None:
    """Write all of the National Emissions data to a JSON file."""
    with open(_file_path, "w") as json_file:
        json.dump([_.model_dump() for _ in _emissions.values()], json_file, indent=4)


def load_national_emissions_from_json_file(
    _file_path: Path,
) -> dict[str, PhAdorbNationalEmissions]:
    """Load all of the National Emissions data from a JSON file."""
    with open(_file_path, "r") as json_file:
        all_emissions = (
            PhAdorbNationalEmissions(**item) for item in json.load(json_file)
        )
        return {_.country_name: _ for _ in all_emissions}
