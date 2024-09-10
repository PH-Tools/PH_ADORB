"""Fuel Types and cost related data."""

from enum import Enum
from pydantic import BaseModel


class FuelType(Enum):
    ELECTRICITY = "Electricity"
    NATURAL_GAS = "Natural Gas"


class Fuel(BaseModel):
    fuel_type: FuelType
    purchase_price: float
    sale_price: float
    annual_base_price: float
    used: bool = True

    @property
    def name(self) -> str:
        return self.fuel_type.value
