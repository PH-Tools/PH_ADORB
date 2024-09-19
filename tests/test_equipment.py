from pathlib import Path

from ph_adorb.equipment import (
    PhAdorbEquipment,
    PhAdorbEquipmentCollection,
    PhAdorbEquipmentType,
    load_equipment_from_json_file,
    write_equipment_to_json_file,
)


def test_basic_equipment():
    equip = PhAdorbEquipment(
        name="Test Equipment",
        equipment_type=PhAdorbEquipmentType.MECHANICAL,
        cost=1000.0,
        lifetime_years=10,
        labor_fraction=0.2,
    )
    assert equip.name == "Test Equipment"
    assert equip.equipment_type == PhAdorbEquipmentType.MECHANICAL
    assert equip.cost == 1000.0
    assert equip.lifetime_years == 10
    assert equip.labor_fraction == 0.2
    assert equip.material_fraction == 0.8


def test_equipment_duplicate():
    equip = PhAdorbEquipment(
        name="Test Equipment",
        equipment_type=PhAdorbEquipmentType.MECHANICAL,
        cost=1000.0,
        lifetime_years=10,
        labor_fraction=0.2,
    )
    equip2 = equip.duplicate()
    assert equip is not equip2
    assert equip == equip2


def test_equipment_copy():
    equip = PhAdorbEquipment(
        name="Test Equipment",
        equipment_type=PhAdorbEquipmentType.MECHANICAL,
        cost=1000.0,
        lifetime_years=10,
        labor_fraction=0.2,
    )
    equip2 = equip.__copy__()
    assert equip is not equip2
    assert equip == equip2


def test_equipment_to_json():
    equip = PhAdorbEquipment(
        name="Test Equipment",
        equipment_type=PhAdorbEquipmentType.MECHANICAL,
        cost=1000.0,
        lifetime_years=10,
        labor_fraction=0.2,
    )
    json_str = equip.json()
    assert (
        json_str
        == '{"name": "Test Equipment", "equipment_type": "Mechanical", "cost": 1000.0, "lifetime_years": 10, "labor_fraction": 0.2}'
    )


def test_equipment_from_json():
    json_str = '{"name": "Test Equipment", "equipment_type": "Mechanical", "cost": 1000.0, "lifetime_years": 10, "labor_fraction": 0.2}'
    equip = PhAdorbEquipment.parse_raw(json_str)
    assert equip.name == "Test Equipment"
    assert equip.equipment_type == PhAdorbEquipmentType.MECHANICAL
    assert equip.cost == 1000.0
    assert equip.lifetime_years == 10
    assert equip.labor_fraction == 0.2
    assert equip.material_fraction == 0.8


def test_EquipmentCollection():
    equip1 = PhAdorbEquipment(
        name="Test Mechanical",
        equipment_type=PhAdorbEquipmentType.MECHANICAL,
        cost=1000.0,
        lifetime_years=10,
        labor_fraction=0.2,
    )
    equip2 = PhAdorbEquipment(
        name="Test Lights",
        equipment_type=PhAdorbEquipmentType.LIGHTS,
        cost=2000.0,
        lifetime_years=20,
        labor_fraction=0.3,
    )
    equip3 = PhAdorbEquipment(
        name="Test Appliance",
        equipment_type=PhAdorbEquipmentType.APPLIANCE,
        cost=3000.0,
        lifetime_years=30,
        labor_fraction=0.4,
    )
    equip_collection = PhAdorbEquipmentCollection()
    equip_collection.add_equipment(equip1)
    equip_collection.add_equipment(equip2)
    equip_collection.add_equipment(equip3)

    assert len(equip_collection) == 3
    assert equip_collection.get_equipment(equip1.name) == equip1
    assert equip_collection.get_equipment(equip2.name) == equip2
    assert equip_collection.get_equipment(equip3.name) == equip3

    # -- Test Keys and Values, Contains
    assert equip1 in equip_collection
    assert equip1 in equip_collection.values()
    assert equip1.name in equip_collection
    assert equip1.name in equip_collection.keys()

    assert equip2 in equip_collection
    assert equip2 in equip_collection.values()
    assert equip2.name in equip_collection
    assert equip2.name in equip_collection.keys()

    assert equip3 in equip_collection
    assert equip3 in equip_collection.values()
    assert equip3.name in equip_collection
    assert equip3.name in equip_collection.keys()

    # -- Test Iteration
    for equip in equip_collection:
        assert isinstance(equip, PhAdorbEquipment)


def test_equipment_json_file():
    equip1 = PhAdorbEquipment(
        name="Test Mechanical",
        equipment_type=PhAdorbEquipmentType.MECHANICAL,
        cost=1000.0,
        lifetime_years=10,
        labor_fraction=0.2,
    )
    equip2 = PhAdorbEquipment(
        name="Test Lights",
        equipment_type=PhAdorbEquipmentType.LIGHTS,
        cost=2000.0,
        lifetime_years=20,
        labor_fraction=0.3,
    )
    equip3 = PhAdorbEquipment(
        name="Test Appliance",
        equipment_type=PhAdorbEquipmentType.APPLIANCE,
        cost=3000.0,
        lifetime_years=30,
        labor_fraction=0.4,
    )

    file_path = Path("test_equipment.json")
    write_equipment_to_json_file(file_path, {_.name: _ for _ in [equip1, equip2, equip3]})

    # -- Read the JSON file back in
    equipment = load_equipment_from_json_file(file_path)
    assert len(equipment) == 3
    assert equipment["Test Mechanical"] == equip1
    assert equipment["Test Lights"] == equip2
    assert equipment["Test Appliance"] == equip3

    # -- Cleanup
    file_path.unlink()
