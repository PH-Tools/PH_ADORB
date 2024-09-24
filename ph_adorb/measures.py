# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""CO2 Reduction Measures and Collection"""

import json
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, PrivateAttr


class CO2MeasureType(str, Enum):
    PERFORMANCE = "PERFORMANCE"
    NON_PERFORMANCE = "NON_PERFORMANCE"


class PhAdorbCO2ReductionMeasure(BaseModel):
    """A CO2 Reduction Measure."""

    measure_type: CO2MeasureType
    name: str
    year: int
    cost: float
    kg_CO2: float | None
    country_name: str
    labor_fraction: float

    @property
    def material_fraction(self) -> float:
        return 1.0 - self.labor_fraction


class PhAdorbCO2MeasureCollection(BaseModel):
    """A collection of CO2 Reduction Measures."""

    _measures: dict[str, PhAdorbCO2ReductionMeasure] = PrivateAttr(default_factory=dict)

    def add_measure(self, factor: PhAdorbCO2ReductionMeasure) -> None:
        self._measures[factor.name] = factor

    def get_measure(self, key: str) -> PhAdorbCO2ReductionMeasure:
        return self._measures[key]

    def keys(self) -> list[str]:
        return [k for k, v in sorted(self._measures.items(), key=lambda x: x[1].year)]

    def values(self) -> list[PhAdorbCO2ReductionMeasure]:
        return list(sorted(self._measures.values(), key=lambda x: x.year))

    def __iter__(self):
        return iter(sorted(self._measures.values(), key=lambda x: x.year))

    def __contains__(self, key: str | PhAdorbCO2ReductionMeasure) -> bool:
        if isinstance(key, PhAdorbCO2ReductionMeasure):
            return key in self._measures.values()
        return key in self._measures

    def __len__(self) -> int:
        return len(self._measures)

    @property
    def performance_measures(self) -> "PhAdorbCO2MeasureCollection":
        """Return a collection of PERFORMANCE measures."""
        new_collection = PhAdorbCO2MeasureCollection()
        for measure in self.values():
            if measure.measure_type == CO2MeasureType.PERFORMANCE:
                new_collection.add_measure(measure)
        return new_collection

    @property
    def nonperformance_measures(self) -> "PhAdorbCO2MeasureCollection":
        """Return a collection of NON-PERFORMANCE measures."""
        new_collection = PhAdorbCO2MeasureCollection()
        for measure in self.values():
            if measure.measure_type == CO2MeasureType.NON_PERFORMANCE:
                new_collection.add_measure(measure)
        return new_collection


def write_CO2_measures_to_json_file(_file_path: Path, measures: dict[str, PhAdorbCO2ReductionMeasure]) -> None:
    """Write all of the CO2 Measure-Types to a JSON file."""
    with open(_file_path, "w") as json_file:
        json.dump([_.dict() for _ in measures.values()], json_file, indent=4)


def load_CO2_measures_from_json_file(_file_path: Path) -> dict[str, PhAdorbCO2ReductionMeasure]:
    """Load all of the CO2 Measure-Types from a JSON file."""
    with open(_file_path, "r") as json_file:
        all_measures = (PhAdorbCO2ReductionMeasure(**item) for item in json.load(json_file))
        return {_.name: _ for _ in all_measures}
