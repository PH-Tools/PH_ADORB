# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Fuel Types and cost related data."""

from enum import Enum

from pydantic import BaseModel


class PhAdorbFuelType(str, Enum):
    ELECTRICITY = "Electricity"
    NATURAL_GAS = "Natural Gas"


class PhAdorbFuel(BaseModel):
    fuel_type: PhAdorbFuelType
    purchase_price_per_kwh: float
    sale_price_per_kwh: float
    annual_base_price: float
    used: bool = True

    @property
    def name(self) -> str:
        return self.fuel_type.value
