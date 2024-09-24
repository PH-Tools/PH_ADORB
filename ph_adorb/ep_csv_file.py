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


def load_monthly_meter_ep_output(_source_file_path: Path) -> pd.DataFrame:
    """Load the CSV and remove the warmup period (first 8 rows) and return the DataFrame."""

    df_monthly_meter = pd.read_csv(_source_file_path)

    warmup_rows = [0, 1, 2, 3, 4, 5, 6, 7]
    df_monthly_meter = df_monthly_meter.drop(index=warmup_rows)
    return df_monthly_meter
