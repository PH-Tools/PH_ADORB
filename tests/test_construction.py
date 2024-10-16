from copy import copy
from pathlib import Path

from pytest import approx

from ph_adorb.constructions import (
    PhAdorbConstruction,
    PhAdorbConstructionCollection,
    load_constructions_from_json_file,
    write_constructions_to_json_file,
)


def test_basic_construction():
    construction = PhAdorbConstruction(
        display_name="Test Construction",
        identifier="Test Construction",
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    assert construction.display_name == "Test Construction"
    assert construction.CO2_kg_per_m2 == 100
    assert construction.cost_per_m2 == 1000
    assert construction.lifetime_years == 30
    assert construction.labor_fraction == 0.4
    assert construction.material_fraction == 0.6


def test_set_quantity_ft2():
    construction = PhAdorbConstruction(
        display_name="Test Construction",
        identifier="Test Construction",
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    construction.set_quantity_ft2(1076.39)
    assert construction.area_m2 == approx(100.0)
    assert construction.quantity_ft2 == approx(1076.39)


def test_cost():
    construction = PhAdorbConstruction(
        display_name="Test Construction",
        identifier="Test Construction",
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    construction.area_m2 = 100
    assert construction.cost == approx(100000.0)


def test_CO2_kg():
    construction = PhAdorbConstruction(
        display_name="Test Construction",
        identifier="Test Construction",
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    construction.area_m2 = 100
    assert construction.CO2_kg == approx(10000.0)


def test_construction_to_json():
    construction = PhAdorbConstruction(
        display_name="Test Construction",
        identifier="Test Construction",
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    json_str = construction.json()
    assert (
        json_str
        == '{"display_name": "Test Construction", "identifier": "Test Construction", "CO2_kg_per_m2": 100.0, "cost_per_m2": 1000.0, "lifetime_years": 30, "labor_fraction": 0.4, "area_m2": 0.0}'
    )


def test_construction_from_json():
    construction = PhAdorbConstruction.parse_obj(
        {
            "display_name": "Test Construction",
            "identifier": "Test Construction",
            "CO2_kg_per_m2": 100,
            "cost_per_m2": 1000,
            "lifetime_years": 30,
            "labor_fraction": 0.4,
        }
    )
    assert construction.display_name == "Test Construction"
    assert construction.identifier == "Test Construction"
    assert construction.CO2_kg_per_m2 == 100
    assert construction.cost_per_m2 == 1000
    assert construction.lifetime_years == 30
    assert construction.labor_fraction == 0.4
    assert construction.material_fraction == 0.6


def test_duplicate_construction():
    construction = PhAdorbConstruction(
        display_name="Test Construction",
        identifier="Test Construction",
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )

    construction2 = construction.duplicate()
    assert construction is not construction2
    assert construction == construction2

    construction3 = copy(construction)
    assert construction is not construction3
    assert construction == construction3


def test_construction_collection():
    collection = PhAdorbConstructionCollection()
    construction1 = PhAdorbConstruction(
        display_name="Test Construction 1",
        identifier="Test Construction 1",
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    construction2 = PhAdorbConstruction(
        display_name="Test Construction 2",
        identifier="Test Construction 1",
        CO2_kg_per_m2=200,
        cost_per_m2=2000,
        lifetime_years=40,
        labor_fraction=0.5,
    )
    collection.add_construction(construction1)
    collection.add_construction(construction2)

    assert len(collection) == 2

    # Test Getting Construction
    assert collection.get_construction("Test Construction 1") == construction1
    assert collection.get_construction("Test Construction 2") == construction2

    # Test Keys, Values, Contains
    assert "Test Construction 1" in collection
    assert "Test Construction 1" in collection.keys()
    assert construction1 in collection
    assert construction1 in collection.values()

    assert "Test Construction 2" in collection
    assert "Test Construction 2" in collection.keys()
    assert construction2 in collection
    assert construction2 in collection.values()

    # Test iteration
    for construction in collection:
        assert isinstance(construction, PhAdorbConstruction)


def test_set_construction_f2_quantities():
    collection = PhAdorbConstructionCollection()
    construction1 = PhAdorbConstruction(
        display_name="Test Construction 1",
        identifier="Test Construction 1",
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    construction2 = PhAdorbConstruction(
        display_name="Test Construction 2",
        identifier="Test Construction 1",
        CO2_kg_per_m2=200,
        cost_per_m2=2000,
        lifetime_years=40,
        labor_fraction=0.5,
    )
    collection.add_construction(construction1)
    collection.add_construction(construction2)

    quantities = {"TEST CONSTRUCTION 1": 1076.39, "TesT construction 2": 1076.39}
    collection.set_constructions_ft2_quantities(quantities)
    assert collection.get_construction("Test Construction 1").area_m2 == approx(100.0)
    assert collection.get_construction("Test Construction 2").area_m2 == approx(100.0)


def test_constructions_json_file():
    # -- Create a temp JSON file with some constructions
    c1 = PhAdorbConstruction(
        display_name="Test Construction 1",
        identifier="Test Construction 1",
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    c2 = PhAdorbConstruction(
        display_name="Test Construction 2",
        identifier="Test Construction 1",
        CO2_kg_per_m2=200,
        cost_per_m2=2000,
        lifetime_years=40,
        labor_fraction=0.5,
    )
    constructions = [c1, c2]

    file_path = Path("temp.json")
    write_constructions_to_json_file(file_path, {_.display_name: _ for _ in constructions})

    # -- Read the JSON file back in
    constructions2 = load_constructions_from_json_file(file_path)
    assert len(constructions2) == 2
    assert constructions2["Test Construction 1"] == c1
    assert constructions2["Test Construction 2"] == c2

    # -- Clean up
    file_path.unlink()
