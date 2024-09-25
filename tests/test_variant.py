import pandas as pd

from ph_adorb.grid_region import PhAdorbGridRegion
from ph_adorb.variant import calc_annual_total_electric_cost, calc_annuals_hourly_electric_CO2


def test_get_annual_electric_cost():
    result = calc_annual_total_electric_cost(
        _purchased_electricity_kwh=100.0,
        _sold_electricity_kwh=0.0,
        _electric_purchase_price_per_kwh=0.1,
        _electric_sell_price_per_kwh=0.05,
        _electric_annual_base_price=100,
    )
    assert result == 110.0


def test_get_hourly_electric_CO2():

    grid_region_factors = PhAdorbGridRegion(
        region_code="Test",
        region_name="Germany",
        description="Germany",
        hourly_CO2_factors={k: v for k, v in zip(range(2023, 2023 + 89), [[0.0] * 100] * 89)},
    )
    result = calc_annuals_hourly_electric_CO2(
        _hourly_purchased_electricity_kwh=[100.0, 100.0, 0.0], _grid_region_factors=grid_region_factors
    )
    assert result == [0.0] * 89


# TODO: Add tests for the remaining functions.
