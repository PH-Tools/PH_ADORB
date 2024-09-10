from ph_adorb.national_emissions import NationalEmissions


def test_NationalEmissions():
    national_emissions = NationalEmissions(
        country_name="Germany",
        us_trading_rank=4,
        GDP_million_USD=4.2,
        CO2_MT=2.3,
        kg_CO2_per_USD=0.5,
    )
    assert national_emissions.country_name == "Germany"
    assert national_emissions.us_trading_rank == 4
    assert national_emissions.GDP_million_USD == 4.2
    assert national_emissions.CO2_MT == 2.3
    assert national_emissions.kg_CO2_per_USD == 0.5
    assert national_emissions.dict() == {
        "country_name": "Germany",
        "us_trading_rank": 4,
        "GDP_million_USD": 4.2,
        "CO2_MT": 2.3,
        "kg_CO2_per_USD": 0.5,
    }


def test_NationalEmissions_to_json():
    national_emissions = NationalEmissions(
        country_name="Germany",
        us_trading_rank=4,
        GDP_million_USD=4.2,
        CO2_MT=2.3,
        kg_CO2_per_USD=0.5,
    )
    json_str = national_emissions.json()
    assert (
        json_str
        == '{"country_name": "Germany", "us_trading_rank": 4, "GDP_million_USD": 4.2, "CO2_MT": 2.3, "kg_CO2_per_USD": 0.5}'
    )


def test_NationalEmissions_from_json():
    national_emissions = NationalEmissions.parse_obj(
        {
            "country_name": "Germany",
            "us_trading_rank": 4,
            "GDP_million_USD": 4.2,
            "CO2_MT": 2.3,
            "kg_CO2_per_USD": 0.5,
        }
    )
    assert national_emissions.country_name == "Germany"
    assert national_emissions.us_trading_rank == 4
    assert national_emissions.GDP_million_USD == 4.2
    assert national_emissions.CO2_MT == 2.3
    assert national_emissions.kg_CO2_per_USD == 0.5
    assert national_emissions.dict() == {
        "country_name": "Germany",
        "us_trading_rank": 4,
        "GDP_million_USD": 4.2,
        "CO2_MT": 2.3,
        "kg_CO2_per_USD": 0.5,
    }
