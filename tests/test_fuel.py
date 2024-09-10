from ph_adorb.fuel import FuelType, Fuel


def test_fuel():
    fuel = Fuel(fuel_type=FuelType.ELECTRICITY, purchase_price=0.12, sale_price=0.08, annual_base_price=0.10, used=True)
    assert fuel.name == "Electricity"
    assert fuel.purchase_price == 0.12
    assert fuel.sale_price == 0.08
    assert fuel.annual_base_price == 0.10


def test_fuel_to_json():
    fuel = Fuel(fuel_type=FuelType.ELECTRICITY, purchase_price=0.12, sale_price=0.08, annual_base_price=0.10, used=True)
    json_str = fuel.json()
    assert (
        json_str
        == '{"fuel_type": "Electricity", "purchase_price": 0.12, "sale_price": 0.08, "annual_base_price": 0.1, "used": true}'
    )


def test_fuel_from_json():
    fuel = Fuel.parse_obj(
        {
            "fuel_type": "Electricity",
            "purchase_price": 0.12,
            "sale_price": 0.08,
            "annual_base_price": 0.10,
            "used": True,
        }
    )
    assert fuel.fuel_type == FuelType.ELECTRICITY
    assert fuel.purchase_price == 0.12
    assert fuel.sale_price == 0.08
    assert fuel.annual_base_price == 0.10
    assert fuel.used == True
    assert fuel.name == "Electricity"
