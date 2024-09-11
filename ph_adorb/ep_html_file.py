"""Functions to load and process the source data HTML files."""

from pathlib import Path
from typing import Callable, TypeVar, Generic

import pandas as pd
from eppy.results.fasthtml import tablebyname
from pydantic import BaseModel, PrivateAttr

T = TypeVar("T")


class NoDataLoadedError(Exception):
    def __init__(self, _file_name: str):
        message = f"File '{_file_name}' data loaded yet. Call .load_file_data() first."
        super().__init__(message)


class MissingTableError(Exception):
    def __init__(self, _table_name: str, _file_name: str):
        message = f"Table '{_table_name}' not found in file '{_file_name}'."
        super().__init__(message)


class DataFileEPTables(BaseModel, Generic[T]):
    """A single .HTML Table Data File."""

    __annotations__ = {"T": T}

    source_file_path: Path
    loader: Callable[[Path], T]
    _data: T | None = PrivateAttr(default=None)

    class Config:
        arbitrary_types_allowed = True

    @property
    def file_name(self) -> str:
        """The name of the file."""
        return self.source_file_path.name

    def load_file_data(self):
        """Read in the data from the HTML Table file and store it."""
        self._data = self.loader(self.source_file_path)

    @property
    def data(self) -> T:
        """The file's data as a Pandas DataFrame."""
        if self._data is None:
            raise NoDataLoadedError(self.file_name)
        return self._data


# ---------------------------------------------------------------------------------------
# HTML Table Loader Functions


def load_construction_cost_estimate_data(source_file_path: Path) -> list:
    """Load the 'Construction Cost Estimate Summary' table data from the HTML file.

    Args:
        source_file_path (Path): The path to the EnergyPlus HTML file.
    Returns:
        (list): The table data as a list.
    """

    table_name = "Construction Cost Estimate Summary"
    with open(source_file_path, "r") as file_data:
        try:
            construction_cost_estimate = tablebyname(file_data, table_name) or []
        except UnboundLocalError:
            raise MissingTableError(table_name, source_file_path.name)

    if not construction_cost_estimate or len(construction_cost_estimate) != 2:
        raise MissingTableError(table_name, source_file_path.name)

    return construction_cost_estimate


def load_peak_electric_usage_data(source_file_path: Path) -> float:
    """Load the 'Annual and Peak Values - Electricity' table data from the HTML file.

    Args:
        source_file_path (Path): The path to the EnergyPlus HTML file.

    Returns:
        (float): The peak electric usage value in Watts.
    """

    table_name = "Annual and Peak Values - Electricity"
    with open(source_file_path, "r") as file_data:
        try:
            all_table_data = tablebyname(file_data, table_name) or []
        except UnboundLocalError:
            raise MissingTableError(table_name, source_file_path.name)

    if not all_table_data or len(all_table_data) != 2:
        raise MissingTableError(table_name, source_file_path.name)

    table_data = all_table_data[1]
    column_names = table_data[0]
    peak_electric_usage_df = pd.DataFrame(table_data[1:], columns=column_names).iloc[:-1]

    # DataFrame is missing a column name for the first column, so add it
    peak_electric_usage_df.columns = ["Item Name"] + peak_electric_usage_df.columns[1:].tolist()

    # -------------------------------------------------------------------------
    # -- Pull out the Peak Facility Electric Usage
    item_name = "Electricity:Facility"
    column_name = "Electricity Maximum Value [W]"

    # Get the peak electric usage value
    peak_electric_usage = peak_electric_usage_df.loc[
        peak_electric_usage_df["Item Name"] == item_name, column_name
    ].values[0]

    return float(peak_electric_usage)


def load_construction_quantities_data(source_file_path: Path) -> dict[str, float]:
    """Load the 'Construction Quantities' table data from the HTML file.

    Args:
        source_file_path (Path): The path to the EnergyPlus HTML file.

    Returns:
        (dict[str, float]): A dict with the "Item Name" and "Quantity" (ft2).
    """

    table_name = "Cost Line Item Details"
    with open(source_file_path, "r") as file_data:
        try:
            all_table_data = tablebyname(file_data, table_name) or []
        except UnboundLocalError:
            raise MissingTableError(table_name, source_file_path.name)

    if not all_table_data or len(all_table_data) != 2:
        raise MissingTableError(table_name, source_file_path.name)

    table_data = all_table_data[1]
    column_names = table_data[0]
    cost_line_item_detail_df = pd.DataFrame(table_data[1:], columns=column_names).iloc[:-1]

    # Change the 'Item Name' column to be all uppercase for more consistent lookups later on
    cost_line_item_detail_df["Item Name"] = cost_line_item_detail_df["Item Name"].str.upper()

    # Get a dict of the "Item Name" and "Quantity." columns
    return cost_line_item_detail_df.set_index("Item Name")["Quantity."].to_dict()
