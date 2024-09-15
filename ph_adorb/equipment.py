# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Equipment (mechanical, lighting, etc..), and Collection classes."""

import json
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, PrivateAttr


class EquipmentType(str, Enum):
    MECHANICAL = "Mechanical"
    HOT_WATER = "Hot Water"
    APPLIANCE = "Appliance"
    LIGHTS = "Lights"
    PV_ARRAY = "PV Array"
    BATTERY = "Battery"


class Equipment(BaseModel):
    """A single piece of Equipment."""

    name: str
    equipment_type: EquipmentType
    cost: float
    lifetime_years: int
    labor_fraction: float

    @property
    def material_fraction(self) -> float:
        return 1.0 - self.labor_fraction

    def duplicate(self) -> "Equipment":
        return Equipment(
            name=self.name,
            equipment_type=self.equipment_type,
            cost=self.cost,
            lifetime_years=self.lifetime_years,
            labor_fraction=self.labor_fraction,
        )

    def __copy__(self) -> "Equipment":
        return self.duplicate()


class EquipmentCollection(BaseModel):
    """A collection of Equipment."""

    _equipment: dict[str, Equipment] = PrivateAttr(default_factory=dict)

    def add_equipment(self, factor: Equipment) -> None:
        self._equipment[factor.name] = factor

    def get_equipment(self, key: str) -> Equipment:
        return self._equipment[key]

    def keys(self) -> list[str]:
        return [k for k, v in sorted(self._equipment.items(), key=lambda x: x[1].name)]

    def values(self) -> list[Equipment]:
        return list(sorted(self._equipment.values(), key=lambda x: x.name))

    def __iter__(self):
        return iter(sorted(self._equipment.values(), key=lambda x: x.name))

    def __contains__(self, key: str | Equipment) -> bool:
        if isinstance(key, Equipment):
            return key in self._equipment.values()
        return key in self._equipment

    def __len__(self) -> int:
        return len(self._equipment)


def write_equipment_to_json_file(_file_path: Path, equipment: dict[str, Equipment]) -> None:
    """Write all of the Equipment-Types to a JSON file."""
    with open(_file_path, "w") as json_file:
        json.dump([_.dict() for _ in equipment.values()], json_file, indent=4)


def load_equipment_from_json_file(_file_path: Path) -> dict[str, Equipment]:
    """Load all of the Equipment-Types from a JSON file."""
    with open(_file_path, "r") as json_file:
        all_equipment = (Equipment(**item) for item in json.load(json_file))
        return {_.name: _ for _ in all_equipment}
