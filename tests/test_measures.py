from pathlib import Path

from ph_adorb.measures import (
    PhAdorbCO2MeasureCollection,
    CO2MeasureType,
    PhAdorbCO2ReductionMeasure,
    load_CO2_measures_from_json_file,
    write_CO2_measures_to_json_file,
)


def test_basic_CO2ReductionMeasure():
    measure = PhAdorbCO2ReductionMeasure(
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
    measure = PhAdorbCO2ReductionMeasure(
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
        == '{"measure_type": "PERFORMANCE", "name": "Test Measure", "year": 2023.0, "cost": 1000.0, "kg_CO2": 100.0, "country_name": "DE", "labor_fraction": 0.5}'
    )


def test_CO2ReductionMeasure_from_json():
    measure = PhAdorbCO2ReductionMeasure.parse_obj(
        {
            "measure_type": "PERFORMANCE",
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
    collection = PhAdorbCO2MeasureCollection()
    measure1 = PhAdorbCO2ReductionMeasure(
        measure_type=CO2MeasureType.PERFORMANCE,
        name="Test Measure 1",
        year=2023,
        cost=1000,
        kg_CO2=100,
        country_name="DE",
        labor_fraction=0.5,
    )
    measure2 = PhAdorbCO2ReductionMeasure(
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
    assert measure1 in collection.values()
    assert measure1.name in collection
    assert measure1.name in collection.keys()

    assert measure2 in collection
    assert measure2 in collection.values()
    assert measure2.name in collection
    assert measure2.name in collection.keys()


def test_CO2ReductionMeasureCollection_PERFORMANCE():
    collection = PhAdorbCO2MeasureCollection()
    measure1 = PhAdorbCO2ReductionMeasure(
        measure_type=CO2MeasureType.PERFORMANCE,
        name="Test Measure 1",
        year=2023,
        cost=1000,
        kg_CO2=100,
        country_name="DE",
        labor_fraction=0.5,
    )
    measure2 = PhAdorbCO2ReductionMeasure(
        measure_type=CO2MeasureType.PERFORMANCE,
        name="Test Measure 2",
        year=2024,
        cost=2000,
        kg_CO2=200,
        country_name="DE",
        labor_fraction=0.6,
    )
    measure3 = PhAdorbCO2ReductionMeasure(
        measure_type=CO2MeasureType.NON_PERFORMANCE,
        name="Test Measure 3",
        year=2024,
        cost=2000,
        kg_CO2=200,
        country_name="DE",
        labor_fraction=0.6,
    )
    collection.add_measure(measure1)
    collection.add_measure(measure2)
    collection.add_measure(measure3)

    assert len(collection) == 3
    assert len(collection.performance_measures) == 2
    assert len(collection.nonperformance_measures) == 1


def test_CO2ReductionMeasures_json_file():
    collection = PhAdorbCO2MeasureCollection()
    measure1 = PhAdorbCO2ReductionMeasure(
        measure_type=CO2MeasureType.PERFORMANCE,
        name="Test Measure 1",
        year=2023,
        cost=1000,
        kg_CO2=100,
        country_name="DE",
        labor_fraction=0.5,
    )
    measure2 = PhAdorbCO2ReductionMeasure(
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

    file_path = Path("test_measures.json")
    write_CO2_measures_to_json_file(file_path, {_.name: _ for _ in collection})

    # -- Read the JSON file data back in
    measures = load_CO2_measures_from_json_file(file_path)
    assert len(measures) == 2
    assert measures["Test Measure 1"] == measure1
    assert measures["Test Measure 2"] == measure2

    # -- Clean-up
    file_path.unlink()
