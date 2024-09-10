"""Assembly (wall, floor, etc..) Constructions, and Collection classes."""

import json
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, PrivateAttr


class ConstructionType(str, Enum):
    EXTERIOR_DOOR = "Exterior Door"
    EXTERIOR_WINDOW = "Exterior Window"
    EXTERIOR_WALL = "Exterior Wall"
    EXTERIOR_FLOOR = "Exterior Floor"
    EXTERIOR_ROOF = "Exterior Roof"
    INTERIOR_WALL = "Interior Wall"
    INTERIOR_FLOOR = "Interior Floor"


class Construction(BaseModel):
    """A single Construction."""

    name: str
    construction_type: ConstructionType
    CO2_kg_per_m2: float
    cost_per_m2: float
    lifetime_years: int
    labor_fraction: float
    quantity_m2: float = 0.0

    @property
    def quantity_ft2(self) -> float:
        return self.quantity_m2 * 10.7639

    def set_quantity_ft2(self, _value: float) -> None:
        self.quantity_m2 = _value / 10.7639

    @property
    def cost(self) -> float:
        """Total Cost (quantity * cost_per_m2)."""
        return self.quantity_m2 * self.cost_per_m2

    @property
    def CO2_kg(self) -> float:
        """Total CO2 (quantity * CO2_kg_per_m2)."""
        return self.quantity_m2 * self.CO2_kg_per_m2

    @property
    def material_fraction(self) -> float:
        return 1.0 - self.labor_fraction

    def duplicate(self) -> "Construction":
        return Construction(
            name=self.name,
            construction_type=self.construction_type,
            CO2_kg_per_m2=self.CO2_kg_per_m2,
            cost_per_m2=self.cost_per_m2,
            lifetime_years=self.lifetime_years,
            labor_fraction=self.labor_fraction,
        )

    def __copy__(self) -> "Construction":
        return self.duplicate()


class ConstructionCollection(BaseModel):
    """A collection of Constructions."""

    _constructions: dict[str, Construction] = PrivateAttr(default_factory=dict)

    def add_construction(self, _construction: Construction) -> None:
        self._constructions[_construction.name] = _construction

    def get_construction(self, key: str) -> Construction:
        return self._constructions[key]

    def keys(self) -> list[str]:
        return [k for k, v in sorted(self._constructions.items(), key=lambda x: x[1].name)]

    def values(self) -> list[Construction]:
        return list(sorted(self._constructions.values(), key=lambda x: x.name))

    def __iter__(self):
        return iter(sorted(self._constructions.values(), key=lambda x: x.name))

    def __len__(self) -> int:
        return len(self._constructions)

    def __contains__(self, key: str | Construction) -> bool:
        if isinstance(key, Construction):
            return key in self._constructions.values()
        return key in self._constructions

    def set_constructions_ft2_quantities(self, _construction_quantities_ft2: dict[str, float]) -> None:
        """Set the quantity (ft2) of each Construction.

        Args:
            * _construction_quantities (dict[str, float]): A dictionary of Construction
                names, with their quantities (ft2).
        """

        def _clean_name(n: str) -> str:
            return n.upper().replace(" ", "_")

        _construction_quantities_ft2 = {_clean_name(k): v for k, v in _construction_quantities_ft2.items()}

        old_constructions = list(self._constructions.values())
        self._constructions = {}
        for construction in old_constructions:
            new_construction = construction.duplicate()
            new_construction.set_quantity_ft2(_construction_quantities_ft2[_clean_name(construction.name)])
            self.add_construction(new_construction)


def write_constructions_to_json_file(_file_path: Path, _constructions: dict[str, Construction]) -> None:
    """Write all of the Construction-Types to a JSON file."""
    with open(_file_path, "w") as json_file:
        json.dump([_.dict() for _ in _constructions.values()], json_file, indent=4)


def load_constructions_from_json_file(_file_path: Path) -> dict[str, Construction]:
    """Load all of the Construction-Types from a JSON file."""
    with open(_file_path, "r") as json_file:
        all_constructions = (Construction(**item) for item in json.load(json_file))
        return {_.name: _ for _ in all_constructions}
