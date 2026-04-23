# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Equipment (mechanical, lighting, etc..), and Collection classes."""

import json
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, PrivateAttr


class PhAdorbEquipmentType(str, Enum):
    """Classification of building equipment types.

    Values:
        MECHANICAL: HVAC mechanical equipment (heat pumps, ERVs, etc.).
        HOT_WATER: Domestic hot water equipment.
        APPLIANCE: Plug-load appliances (refrigerators, stoves, etc.).
        LIGHTS: Lighting systems.
        PV_ARRAY: Photovoltaic solar panels.
        BATTERY: Battery energy storage systems.
    """

    MECHANICAL = "Mechanical"
    HOT_WATER = "Hot Water"
    APPLIANCE = "Appliance"
    LIGHTS = "Lights"
    PV_ARRAY = "PV Array"
    BATTERY = "Battery"


class PhAdorbEquipment(BaseModel):
    """A single piece of building equipment with cost and lifetime data.

    Attributes:
        name (str): Display name of the equipment.
        equipment_type (PhAdorbEquipmentType): Equipment classification.
        cost (float): Total installed cost in USD (labor + material).
        lifetime_years (int): Expected service life before replacement.
        labor_fraction (float): Fraction of cost attributable to labor (0.0-1.0).
    """

    name: str
    equipment_type: PhAdorbEquipmentType
    cost: float
    lifetime_years: int
    labor_fraction: float

    @property
    def material_fraction(self) -> float:
        """Fraction of cost attributable to materials (1 - labor_fraction)."""
        return 1.0 - self.labor_fraction

    def duplicate(self) -> "PhAdorbEquipment":
        return PhAdorbEquipment(
            name=self.name,
            equipment_type=self.equipment_type,
            cost=self.cost,
            lifetime_years=self.lifetime_years,
            labor_fraction=self.labor_fraction,
        )

    def __copy__(self) -> "PhAdorbEquipment":
        return self.duplicate()


class PhAdorbEquipmentCollection(BaseModel):
    """A dict-backed, iterable collection of equipment items.

    Equipment is keyed by name and sorted alphabetically when iterated.
    """

    _equipment: dict[str, PhAdorbEquipment] = PrivateAttr(default_factory=dict)

    def add_equipment(self, _ph_adorb_equipment: PhAdorbEquipment) -> None:
        """Add an equipment item to the collection."""
        self._equipment[_ph_adorb_equipment.name] = _ph_adorb_equipment

    def get_equipment(self, key: str) -> PhAdorbEquipment:
        """Return an equipment item by name."""
        return self._equipment[key]

    def keys(self) -> list[str]:
        """Return equipment names sorted alphabetically."""
        return [k for k, v in sorted(self._equipment.items(), key=lambda x: x[1].name)]

    def values(self) -> list[PhAdorbEquipment]:
        """Return equipment items sorted alphabetically by name."""
        return list(sorted(self._equipment.values(), key=lambda x: x.name))

    def __iter__(self):
        return iter(sorted(self._equipment.values(), key=lambda x: x.name))

    def __contains__(self, key: str | PhAdorbEquipment) -> bool:
        if isinstance(key, PhAdorbEquipment):
            return key in self._equipment.values()
        return key in self._equipment

    def __len__(self) -> int:
        return len(self._equipment)


def write_equipment_to_json_file(
    _file_path: Path, equipment: dict[str, PhAdorbEquipment]
) -> None:
    """Write all of the Equipment-Types to a JSON file."""
    with open(_file_path, "w") as json_file:
        json.dump([_.model_dump() for _ in equipment.values()], json_file, indent=4)


def load_equipment_from_json_file(_file_path: Path) -> dict[str, PhAdorbEquipment]:
    """Load all of the Equipment-Types from a JSON file."""
    with open(_file_path, "r") as json_file:
        all_equipment = (PhAdorbEquipment(**item) for item in json.load(json_file))
        return {_.name: _ for _ in all_equipment}
