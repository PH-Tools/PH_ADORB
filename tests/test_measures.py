from ph_adorb.measures import CO2MeasureType, CO2ReductionMeasure, CO2MeasureCollection


def test_basic_CO2ReductionMeasure():
    measure = CO2ReductionMeasure(
        measure_type=CO2MeasureType.PERFORMANCE,
        name="Test Measure",
        year=2023,
        cost=1000,
        kg_CO2=100,
        country_name="DE",
        labor_fraction=0.4,
    )
    assert measure.name == "Test Measure"
    assert measure.year == 2023
    assert measure.cost == 1000
    assert measure.kg_CO2 == 100
    assert measure.country_name == "DE"
    assert measure.labor_fraction == 0.4
    assert measure.material_fraction == 0.6


def test_CO2ReductionMeasure_to_json():
    measure = CO2ReductionMeasure(
        measure_type=CO2MeasureType.PERFORMANCE,
        name="Test Measure",
        year=2023,
        cost=1000,
        kg_CO2=100,
        country_name="DE",
        labor_fraction=0.5,
    )
    json_str = measure.json()
    assert (
        json_str
        == '{"measure_type": "Performance", "name": "Test Measure", "year": 2023.0, "cost": 1000.0, "kg_CO2": 100.0, "country_name": "DE", "labor_fraction": 0.5}'
    )


def test_CO2ReductionMeasure_from_json():
    measure = CO2ReductionMeasure.parse_obj(
        {
            "measure_type": "Performance",
            "name": "Test Measure",
            "year": 2023,
            "cost": 1000,
            "kg_CO2": 100,
            "country_name": "DE",
            "labor_fraction": 0.5,
        }
    )
    assert measure.measure_type == CO2MeasureType.PERFORMANCE
    assert measure.name == "Test Measure"
    assert measure.year == 2023
    assert measure.cost == 1000
    assert measure.kg_CO2 == 100
    assert measure.country_name == "DE"
    assert measure.labor_fraction == 0.5
    assert measure.material_fraction == 0.5


def test_CO2ReductionMeasureCollection():
    collection = CO2MeasureCollection()
    measure1 = CO2ReductionMeasure(
        measure_type=CO2MeasureType.PERFORMANCE,
        name="Test Measure 1",
        year=2023,
        cost=1000,
        kg_CO2=100,
        country_name="DE",
        labor_fraction=0.5,
    )
    measure2 = CO2ReductionMeasure(
        measure_type=CO2MeasureType.PERFORMANCE,
        name="Test Measure 2",
        year=2024,
        cost=2000,
        kg_CO2=200,
        country_name="DE",
        labor_fraction=0.6,
    )
    collection.add_measure(measure1)
    collection.add_measure(measure2)
    assert len(collection) == 2
    assert collection.get_measure("Test Measure 1") == measure1
    assert collection.get_measure("Test Measure 2") == measure2

    assert measure1 in collection
    assert measure1.name in collection
    assert measure2 in collection
    assert measure2.name in collection
