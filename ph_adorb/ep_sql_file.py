# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Functions to load and process the source data SQL files."""

import sqlite3
from collections import defaultdict
from pathlib import Path

from ph_units.unit_type import Unit
from pydantic import BaseModel

KWH_PER_JOULE = 0.0000002778


class DataFileSQL(BaseModel):
    """A single EnergyPlus results .SQL Data File."""

    source_file_path: Path

    @property
    def file_name(self) -> str:
        """The name of the file."""
        return self.source_file_path.name

    def get_peak_electric_watts(self) -> float:
        """Get the 'Facility Total Building Electricity Demand Rate' [W] from the SQL File."""
        conn = sqlite3.connect(self.source_file_path)
        try:
            c = conn.cursor()
            c.execute(
                "SELECT MAX(Value) FROM 'ReportVariableWithTime' "
                "WHERE Name='Facility Total Building Electricity Demand Rate'"
            )
            peak_electric_watts_ = c.fetchone()[0]
        except Exception as e:
            conn.close()
            raise Exception(str(e))
        finally:
            conn.close()

        return peak_electric_watts_

    def get_hourly_purchased_electricity_kwh(self) -> list[float]:
        """Get the 'Facility Total Building Electricity Demand Rate' [W] from the SQL File."""
        conn = sqlite3.connect(self.source_file_path)
        try:
            c = conn.cursor()
            c.execute(
                "SELECT Value FROM 'ReportVariableWithTime' " "WHERE Name='Facility Total Purchased Electricity Energy'"
            )
            total_purchased_electricity_kwh_ = [_[0] * KWH_PER_JOULE for _ in c.fetchall()]
        except Exception as e:
            conn.close()
            raise Exception(str(e))
        finally:
            conn.close()

        return total_purchased_electricity_kwh_

    def get_total_purchased_electricity_kwh(self) -> float:
        """Get the 'Facility Total Building Electricity Demand Rate' [W] from the SQL File."""
        conn = sqlite3.connect(self.source_file_path)
        try:
            c = conn.cursor()
            c.execute(
                "SELECT SUM(Value) FROM 'ReportVariableWithTime' "
                "WHERE Name='Facility Total Purchased Electricity Energy'"
            )
            total_purchased_electricity_kwh_ = c.fetchone()[0] * KWH_PER_JOULE
        except Exception as e:
            conn.close()
            raise Exception(str(e))
        finally:
            conn.close()

        return total_purchased_electricity_kwh_

    def get_total_sold_electricity_kwh(self) -> float:
        """Get the 'Facility Total Building Electricity Demand Rate' [W] from the SQL File."""
        conn = sqlite3.connect(self.source_file_path)
        try:
            c = conn.cursor()
            c.execute(
                "SELECT SUM(Value) FROM 'ReportVariableWithTime' "
                "WHERE Name='Facility Total Surplus Electricity Energy'"
            )
            total_sold_electricity_kwh_ = c.fetchone()[0] * KWH_PER_JOULE
        except Exception as e:
            conn.close()
            raise Exception(str(e))
        finally:
            conn.close()

        return total_sold_electricity_kwh_

    def get_total_purchased_gas_kwh(self) -> float:
        """Return the total purchased gas in KWH."""
        fuel_use_dict = self.get_total_end_kwh_by_fuel_type()
        return fuel_use_dict["Natural Gas"]

    def get_total_end_kwh_by_fuel_type(self) -> dict[str, float]:
        # -- Get the data from the SQL file
        conn = sqlite3.connect(self.source_file_path)
        try:
            c = conn.cursor()
            c.execute(
                "SELECT ColumnName, RowName, Value, Units FROM TabularDataWithStrings "
                "WHERE TableName='End Uses By Subcategory' AND ReportName='AnnualBuildingUtilityPerformanceSummary'"
            )
            table_data = c.fetchall()
            conn.close()
        except Exception as e:
            conn.close()
            raise Exception(str(e))
        finally:
            conn.close()

        # -- Collect all the SQL data into a dictionary
        table_dict = defaultdict(dict)
        for item in table_data:
            fuel_type_name, end_use_name, value, unit = item
            try:
                table_dict[fuel_type_name][end_use_name] = Unit(value, unit).as_a("KWH").value
            except ValueError:
                # -- Not an energy number (m3/s, etc...)
                pass

        # -- Total the data by fuel-type
        energy_by_fuel_type = {}
        for fuel_type, end_use_data in table_dict.items():
            energy_by_fuel_type[fuel_type] = sum(end_use_data.values())

        return energy_by_fuel_type
