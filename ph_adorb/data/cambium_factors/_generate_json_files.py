"""Utility functions used to generate the Cambium Factors by Region JSON-Files."""

import os
from collections import defaultdict
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field


region_codes = [
    "AZNMc",
    "CAMXc",
    "ERCTc",
    "FRCCc",
    "MROEc",
    "MROWc",
    "NEWEc",
    "NWPPc",
    "NYSTc",
    "RFCEc",
    "RFCMc",
    "RFCWc",
    "RMPAc",
    "SPNOc",
    "SPSOc",
    "SRMVc",
    "SRMWc",
    "SRSOc",
    "SRTVc",
    "SRVCc",
]


class GridRegion(BaseModel):
    region_code: str
    hourly_CO2_factors: defaultdict[int, list[float]] = Field(default_factory=lambda: defaultdict(list))


# -- Setup the region objects....
regions: dict[str, GridRegion] = dict()
for region_code in region_codes:
    regions[region_code] = GridRegion(region_code=region_code)

# -- The original Cambium files (by year)...
_src_cambium_file_path = Path("/Users/em/Desktop/eppy_test/data/cambium_factors/factors_by_year")
for filename in sorted(os.listdir(_src_cambium_file_path)):
    filename = Path(filename)

    if filename.suffix != ".csv":
        continue

    year = filename.stem  # Thanks Al...

    hourlyBAEmissions = pd.read_csv(os.path.join(_src_cambium_file_path, filename))
    hourlyBAEmissions = hourlyBAEmissions.drop(hourlyBAEmissions.columns[0], axis=1)

    for region_name in hourlyBAEmissions.columns:  # grid-regions....
        region_hourly_data = list(hourlyBAEmissions[region_name])
        regions[region_name].hourly_CO2_factors[int(year)] = region_hourly_data


# -- Create the new (by region) JSON files
for _ in list(regions.values()):
    # Write the factor to file
    with open(f"/Users/em/Desktop/eppy_test/data/cambium_factors/{_.region_code}.json", "w") as f:
        f.write(_.json())
