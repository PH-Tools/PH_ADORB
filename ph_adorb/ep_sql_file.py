# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Functions to load and process the source data SQL files."""

from pathlib import Path
from pydantic import BaseModel
import sqlite3

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
