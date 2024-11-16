# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A simple 'YearlyCost object to store annual costs."""

from dataclasses import dataclass


@dataclass
class YearlyCost:
    """A single Yearly Cost for a building design."""

    cost: float
    year: int
    description: str = ""

    def __repr__(self) -> str:
        return f"YearlyCost(cost={self.cost :.1f}, year={self.year}, description={self.description})"


@dataclass
class YearlyKgCO2:
    """A single Yearly CO2 Emissions for a building design"""

    kg_CO2: float
    year: int
    description: str = ""

    def __repr__(self) -> str:
        return f"YearlyKgCO2(kg_CO2={self.kg_CO2 :.1f}, year={self.year}, description={self.description})"


@dataclass
class YearlyPresentValueFactor:
    """A single Yearly Present Value Factor for a building design."""

    factor: float
    year: int

    def __repr__(self) -> str:
        return f"YearlyPresentValueFactor(pv_factor={self.factor :.3f}, year={self.year})"
