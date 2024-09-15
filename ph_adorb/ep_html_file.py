# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Functions to load and process the source data HTML files."""

from io import StringIO
from pathlib import Path
from typing import Callable, Generic, TypeVar, TextIO

import pandas as pd
from pydantic import BaseModel, PrivateAttr

from ph_adorb.read_html import title_table

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

    ### Arguments:
    * source_file_path : The path to the EnergyPlus HTML file.

    ### Returns:
    * The table data.
    """

    table_name = "Construction Cost Estimate Summary"
    with open(source_file_path, "r") as file_data:
        try:
            construction_cost_estimate = table_by_name(file_data, table_name) or []
        except UnboundLocalError:
            raise MissingTableError(table_name, source_file_path.name)

    if not construction_cost_estimate or len(construction_cost_estimate) != 2:
        raise MissingTableError(table_name, source_file_path.name)

    return construction_cost_estimate


def load_peak_electric_usage_data(source_file_path: Path) -> float:
    """Load the 'Annual and Peak Values - Electricity' table data from the HTML file.

    ### Arguments:
    * source_file_path : The path to the EnergyPlus HTML file.

    ### Returns:
    * The peak electric usage value in Watts.
    """

    table_name = "Annual and Peak Values - Electricity"
    with open(source_file_path, "r") as file_data:
        try:
            all_table_data = table_by_name(file_data, table_name) or []
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

    ### Arguments:
    * source_file_path : The path to the EnergyPlus HTML file.

    ### Returns:
    * A dict with the "Item Name" and "Quantity" (ft2).
    """

    table_name = "Cost Line Item Details"
    with open(source_file_path, "r") as file_data:
        try:
            all_table_data = table_by_name(file_data, table_name) or []
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


# ---------------------------------------------------------------------------------------
# HTML Table Reader Functions
# Adapted from EpPy library: /Users/em/Dropbox/bldgtyp-00/00_PH_Tools/PH_ADORB/.venv/lib/python3.10/site-packages/eppy/results/fasthtml.py
# So we don't have to import the entire EpPy library.


def decode_line(_input: str | bytes, _encoding="utf-8") -> str:
    """Decodes bytes to string, if needed.

    It will first attempt to decode line with value of `encoding`. If that fails, it will try
    with encoding="ISO-8859-2". If that fails, it will return line.

    Why is it trying encoding="ISO-8859-2". Looks like E+ uses this encoding in some example
    files and which is then output in the HTML file.

    ### Arguments:
    * _input : Line to decode
    * encoding : (default='utf-8') Encoding to use to decode bytes to string.

    ### Returns:
    * Decoded input.
    """

    # TODO this code looks fragile. Maybe use standard library HTML parse to deal with encoding?

    if isinstance(_input, bytes):
        try:
            return _input.decode(_encoding)
        except UnicodeDecodeError:
            try:
                return _input.decode("ISO-8859-2")
            except UnicodeDecodeError:
                # Fallback to replace undecodable bytes
                return _input.decode(errors="replace")
    elif isinstance(_input, str):
        return _input
    else:
        raise ValueError(f"file line must be of type 'str' or 'bytes'. Got: {type(_input)}")


def table_by_name(_file_handle: TextIO, _header: str) -> list | None:
    """fast extraction of the table using the header to identify the table

    This function reads only one table from the HTML file. This is in
    contrast to `read_html.title_table` that will read all the tables
    nto memory and allows you to interactively look thru them. The
    function `read_html.title_table` can be very slow on large HTML files.

    This function is useful when you know which file you are looking for.
    It looks for the title line that is in bold just before the table.
    Some tables don't have such a title in bold. This function will not
    work for tables that don't have a title in bold.

    ### Arguments:
    * _file_handle : A file handle to the E+ HTML table file
    * header : This is the title of the table you are looking for

    ### Returns:
    * (title, table)
        * title = previous item with a <b> tag
        * table = rows -> [[cell1, cell2, ..], [cell1, cell2, ..], ..]
    """
    html_header = f"<b>{_header}</b><br><br>"

    with _file_handle:

        for line in _file_handle:
            line = decode_line(line)

            if line.strip() == html_header:
                just_table = get_next_table(_file_handle)
                break
        else:
            just_table = None

    if just_table is None:
        return None

    _file_handle = StringIO(f"{html_header}\n{just_table}")
    h_tables = title_table(_file_handle)

    try:
        return list(h_tables[0])
    except IndexError:
        return None


def get_next_table(_file_handle: TextIO) -> str:
    """get the next table in the html file

    Continues to read the file line by line and collects lines from the start
    of the next table until the end of the table.

    ### Arguments:
    * _file_handle : A file handle to the E+ HTML table file

    ### Returns:
    * The table in HTML format
    """

    TAG = "<table"
    table_lines: list[str] = []

    # -----------------------------------------------------------------------------------
    for line in _file_handle:
        line = decode_line(line)
        if line.strip().startswith(TAG):
            table_lines.append(line)
            break

    # -----------------------------------------------------------------------------------
    for line in _file_handle:
        line = decode_line(line)
        table_lines.append(line)
        if line.strip().startswith(TAG):
            break

    return "".join(table_lines)
