"""Country-level CO2 Emissions data per US-Dollar (kg-CO2/$USD)."""

import json
from pathlib import Path

from pydantic import BaseModel


class NationalEmissions(BaseModel):
    """National Emissions Data."""

    country_name: str
    us_trading_rank: int
    GDP_million_USD: float
    CO2_MT: float
    kg_CO2_per_USD: float


def load_national_emissions_from_json_file(_file_path: Path) -> dict[str, NationalEmissions]:
    """Load all of the National Emissions data from a JSON file."""
    with open(_file_path, "r") as json_file:
        all_emissions = (NationalEmissions(**item) for item in json.load(json_file))
        return {_.country_name: _ for _ in all_emissions}
