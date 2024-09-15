# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Functions to load and process the source data CSV files."""

from pathlib import Path
from typing import Callable

import pandas as pd
from pydantic import BaseModel, PrivateAttr


class NoDataLoadedError(Exception):
    def __init__(self, _file_name: str):
        message = f"File '{_file_name}' data loaded yet. Call .load_file_data() first."
        super().__init__(message)


class DataFileCSV(BaseModel):
    """A single .CSV Data File."""

    source_file_path: Path
    loader: Callable[[Path], pd.DataFrame]
    _data: pd.DataFrame | None = PrivateAttr(default=None)

    class Config:
        arbitrary_types_allowed = True

    @property
    def file_name(self) -> str:
        """The name of the file."""
        return self.source_file_path.name

    def load_file_data(self):
        """Read in the data from the source CSV, process, and and store the data."""
        self._data = self.loader(self.source_file_path)

    @property
    def data(self) -> pd.DataFrame:
        """The file's data as a Pandas DataFrame."""
        if self._data is None:
            raise NoDataLoadedError(self.file_name)
        return self._data


# ---------------------------------------------------------------------------------------
# CSV File Loader Functions


def load_full_hourly_ep_output(_source_file_path: Path) -> pd.DataFrame:
    """Load the CSV and remove the warmup period (first 8 rows) and return the DataFrame."""

    # -- Load the CSV
    df_hourly = pd.read_csv(_source_file_path)

    # -- Combine columns
    df_hourly.rename(columns={"Date/Time": "DateTime"}, inplace=True)
    df_hourly[["Date2", "Time"]] = df_hourly.DateTime.str.split(expand=True)
    df_hourly["Date"] = df_hourly["Date2"].map(str)
    df_hourly["Time"] = (pd.to_numeric(df_hourly["Time"].str.split(":").str[0]) - 1).astype(str).apply(
        lambda x: f"0{x}" if len(x) == 1 else x
    ) + df_hourly["Time"].str[2:]
    df_hourly["DateTime"] = df_hourly["Date"] + " " + df_hourly["Time"]
    df_hourly["DateTime"] = pd.to_datetime(df_hourly["DateTime"], format="%m/%d %H:%M:%S", exact=True)

    # -- Drop the warmup periods
    end_warmup = df_hourly[df_hourly["DateTime"] == "1900-01-01 00:00:00"].index[0]
    warmup_rows = [*range(0, end_warmup, 1)]
    df_hourly = df_hourly.drop(index=warmup_rows)
    df_hourly = df_hourly.reset_index()

    return df_hourly


def load_monthly_meter_ep_output(_source_file_path: Path) -> pd.DataFrame:
    """Load the CSV and remove the warmup period (first 8 rows) and return the DataFrame."""

    df_monthly_meter = pd.read_csv(_source_file_path)

    warmup_rows = [0, 1, 2, 3, 4, 5, 6, 7]
    df_monthly_meter = df_monthly_meter.drop(index=warmup_rows)
    return df_monthly_meter
