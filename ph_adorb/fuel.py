# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Fuel Types and cost related data."""

from enum import Enum

from pydantic import BaseModel


class PhAdorbFuelType(str, Enum):
    """Classification of energy fuel types.

    Values:
        ELECTRICITY: Grid-supplied electricity.
        NATURAL_GAS: Piped natural gas.
    """

    ELECTRICITY = "Electricity"
    NATURAL_GAS = "Natural Gas"


class PhAdorbFuel(BaseModel):
    """Pricing and usage data for a single fuel type.

    Attributes:
        fuel_type (PhAdorbFuelType): The fuel classification.
        purchase_price_per_kwh (float): Unit cost to buy energy ($/kWh).
        sale_price_per_kwh (float): Unit price for sold-back energy ($/kWh).
        annual_base_price (float): Fixed annual connection/service charge ($).
        used (bool): Whether this fuel is active in the building. Default: True.
    """

    fuel_type: PhAdorbFuelType
    purchase_price_per_kwh: float
    sale_price_per_kwh: float
    annual_base_price: float
    used: bool = True

    @property
    def name(self) -> str:
        """Return the display name of the fuel type."""
        return self.fuel_type.value
