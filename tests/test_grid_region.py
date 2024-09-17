from pathlib import Path

from ph_adorb.grid_region import GridRegion, load_CO2_factors_from_json_file, write_CO2_factors_to_json_file


def test_GridRegionFactors():
    hourly_CO2_factors = {2023: [460.1, 469.3], 2024: [460.1, 475.3], 2025: [434.1, 445.2]}
    grid_region_factors = GridRegion(
        region_code="DE", region_name="Germany", description="Germany", hourly_CO2_factors=hourly_CO2_factors
    )
    assert grid_region_factors.region_code == "DE"
    assert grid_region_factors.hourly_CO2_factors == hourly_CO2_factors
    assert grid_region_factors.get_CO2_factors_as_df().shape == (2, 3)


def test_GridRegionFactors_to_json():
    hourly_CO2_factors = {2023: [460.1, 469.3], 2024: [460.1, 475.3], 2025: [434.1, 445.2]}
    grid_region_factors = GridRegion(
        region_code="DE", region_name="Germany", description="Germany", hourly_CO2_factors=hourly_CO2_factors
    )
    json_str = grid_region_factors.json()
    assert (
        json_str
        == '{"region_code": "DE", "region_name": "Germany", "description": "Germany", "hourly_CO2_factors": {"2023": [460.1, 469.3], "2024": [460.1, 475.3], "2025": [434.1, 445.2]}}'
    )


def test_GridRegionFactors_from_json():
    hourly_CO2_factors = {2023: [460.1, 469.3], 2024: [460.1, 475.3], 2025: [434.1, 445.2]}
    grid_region_factors = GridRegion.parse_obj(
        {
            "region_code": "DE",
            "region_name": "Germany",
            "description": "Germany",
            "hourly_CO2_factors": {"2023": [460.1, 469.3], "2024": [460.1, 475.3], "2025": [434.1, 445.2]},
        }
    )
    assert grid_region_factors.region_code == "DE"
    assert grid_region_factors.hourly_CO2_factors == hourly_CO2_factors
    assert grid_region_factors.get_CO2_factors_as_df().shape == (2, 3)
    assert grid_region_factors.get_CO2_factors_as_df().columns.tolist() == [2023, 2024, 2025]


def test_GridRegion_json_file():
    hourly_CO2_factors = {2023: [460.1, 469.3], 2024: [460.1, 475.3], 2025: [434.1, 445.2]}
    grid_region_factors = GridRegion(
        region_code="DE", region_name="Germany", description="Germany", hourly_CO2_factors=hourly_CO2_factors
    )

    file_path = Path("test_grid_region.json")
    write_CO2_factors_to_json_file(file_path, grid_region_factors)

    # -- Read the JSON file data back in
    grid_region_factors_loaded = load_CO2_factors_from_json_file(Path("test_grid_region.json"))

    assert grid_region_factors == grid_region_factors_loaded
    assert grid_region_factors_loaded.get_CO2_factors_as_df().shape == (2, 3)
    assert grid_region_factors_loaded.get_CO2_factors_as_df().columns.tolist() == [2023, 2024, 2025]

    # -- Clean-up
    file_path.unlink()
