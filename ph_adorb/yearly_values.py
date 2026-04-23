# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A simple 'YearlyCost object to store annual costs."""

from dataclasses import dataclass


@dataclass
class YearlyCost:
    """A single cost entry assigned to a specific year of the analysis.

    Attributes:
        cost (float): The dollar cost for this year.
        year (int): The year index (0-based) within the analysis duration.
        description (str): Label identifying the source (e.g., construction or equipment name).
    """

    cost: float
    year: int
    description: str = ""

    def __repr__(self) -> str:
        return f"YearlyCost(cost={self.cost :.1f}, year={self.year}, description={self.description})"


@dataclass
class YearlyKgCO2:
    """A single embodied CO2 entry assigned to a specific year of the analysis.

    Attributes:
        kg_CO2 (float): The embodied CO2 in kilograms for this year.
        year (int): The year index (0-based) within the analysis duration.
        description (str): Label identifying the source (e.g., construction or equipment name).
    """

    kg_CO2: float
    year: int
    description: str = ""

    def __repr__(self) -> str:
        return f"YearlyKgCO2(kg_CO2={self.kg_CO2 :.1f}, year={self.year}, description={self.description})"


@dataclass
class YearlyPresentValueFactor:
    """A present value discount factor for a specific year of the analysis.

    Attributes:
        factor (float): The discount factor, computed as (1 + rate)^year.
        year (int): The year number (1-based).
    """

    factor: float
    year: int

    def __repr__(self) -> str:
        return f"YearlyPresentValueFactor(pv_factor={self.factor :.3f}, year={self.year})"
