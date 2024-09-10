from pytest import approx
from ph_adorb.constructions import Construction, ConstructionType, ConstructionCollection


def test_basic_construction():
    construction = Construction(
        name="Test Construction",
        construction_type=ConstructionType.EXTERIOR_WALL,
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    assert construction.name == "Test Construction"
    assert construction.construction_type == ConstructionType.EXTERIOR_WALL
    assert construction.CO2_kg_per_m2 == 100
    assert construction.cost_per_m2 == 1000
    assert construction.lifetime_years == 30
    assert construction.labor_fraction == 0.4
    assert construction.material_fraction == 0.6


def test_set_quantity_ft2():
    construction = Construction(
        name="Test Construction",
        construction_type=ConstructionType.EXTERIOR_WALL,
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    construction.set_quantity_ft2(1076.39)
    assert construction.quantity_m2 == approx(100.0)


def test_cost():
    construction = Construction(
        name="Test Construction",
        construction_type=ConstructionType.EXTERIOR_WALL,
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    construction.quantity_m2 = 100
    assert construction.cost == approx(100000.0)


def test_CO2_kg():
    construction = Construction(
        name="Test Construction",
        construction_type=ConstructionType.EXTERIOR_WALL,
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    construction.quantity_m2 = 100
    assert construction.CO2_kg == approx(10000.0)


def test_construction_to_json():
    construction = Construction(
        name="Test Construction",
        construction_type=ConstructionType.EXTERIOR_WALL,
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    json_str = construction.json()
    assert (
        json_str
        == '{"name": "Test Construction", "construction_type": "Exterior Wall", "CO2_kg_per_m2": 100.0, "cost_per_m2": 1000.0, "lifetime_years": 30, "labor_fraction": 0.4, "quantity_m2": 0.0}'
    )


def test_construction_from_json():
    construction = Construction.parse_obj(
        {
            "name": "Test Construction",
            "construction_type": "Exterior Wall",
            "CO2_kg_per_m2": 100,
            "cost_per_m2": 1000,
            "lifetime_years": 30,
            "labor_fraction": 0.4,
        }
    )
    assert construction.name == "Test Construction"
    assert construction.construction_type == ConstructionType.EXTERIOR_WALL
    assert construction.CO2_kg_per_m2 == 100
    assert construction.cost_per_m2 == 1000
    assert construction.lifetime_years == 30
    assert construction.labor_fraction == 0.4
    assert construction.material_fraction == 0.6


def test_duplicate_construction():
    construction = Construction(
        name="Test Construction",
        construction_type=ConstructionType.EXTERIOR_WALL,
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    construction2 = construction.duplicate()
    assert construction is not construction2
    assert construction == construction2


def test_construction_collection():
    collection = ConstructionCollection()
    construction1 = Construction(
        name="Test Construction 1",
        construction_type=ConstructionType.EXTERIOR_WALL,
        CO2_kg_per_m2=100,
        cost_per_m2=1000,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    construction2 = Construction(
        name="Test Construction 2",
        construction_type=ConstructionType.EXTERIOR_WALL,
        CO2_kg_per_m2=200,
        cost_per_m2=2000,
        lifetime_years=40,
        labor_fraction=0.5,
    )
    collection.add_construction(construction1)
    collection.add_construction(construction2)

    assert len(collection) == 2

    assert collection.get_construction("Test Construction 1") == construction1
    assert collection.get_construction("Test Construction 2") == construction2

    assert "Test Construction 1" in collection
    assert construction1 in collection

    assert "Test Construction 2" in collection
    assert construction2 in collection
