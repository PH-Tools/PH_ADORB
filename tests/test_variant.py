import pandas as pd

from ph_adorb.grid_region import GridRegion
from ph_adorb.variant import (
    get_annual_electric_cost,
    get_annual_gas_CO2,
    get_annual_gas_cost,
    get_carbon_measures_cost,
    get_carbon_measures_embodied_CO2,
    get_carbon_measures_embodied_CO2_first_cost,
    get_hourly_electric_CO2,
)


def test_get_annual_electric_cost():
    df = pd.DataFrame(
        {
            "Whole Building:Facility Total Purchased Electricity Energy [J](Hourly)": [1000] * 100,
            "Whole Building:Facility Total Surplus Electricity Energy [J](Hourly)": [100] * 100,
        }
    )

    result = get_annual_electric_cost(
        _ep_hourly_results_df=df,
        _electric_purchase_price=0.1,
        _electric_sell_price=0.05,
        _electric_annual_base_price=100,
    )
    assert result == 100.0026391


def test_get_hourly_electric_CO2():
    df = pd.DataFrame(
        {
            "Whole Building:Facility Total Purchased Electricity Energy [J](Hourly)": [1000] * 100,
        }
    )
    grid_region_factors = GridRegion(
        region_code="Test",
        region_name="Germany",
        description="Germany",
        hourly_CO2_factors={k: v for k, v in zip(range(2023, 2023 + 89), [[0.0] * 100] * 89)},
    )
    result = get_hourly_electric_CO2(_hourly=df, _grid_region_factors=grid_region_factors)
    assert result == [0.0] * 89
