from pathlib import Path
import pytest
from ph_adorb.ep_csv_file import (
    DataFileCSV,
    load_monthly_meter_ep_output,
    load_full_hourly_ep_output,
    NoDataLoadedError,
)


def test_read_monthly_meter_csv_file():
    """Test reading in a CSV file."""
    _source_file_path = Path("tests/_test_input/example_monthly_meter.csv")

    data_file = DataFileCSV(source_file_path=_source_file_path, loader=load_monthly_meter_ep_output)
    assert data_file.file_name == "example_monthly_meter.csv"

    with pytest.raises(NoDataLoadedError):
        data_file.data

    data_file.load_file_data()
    assert data_file.data.shape == (12, 8)


def test_read_full_hourly_csv_file():
    """Test reading in a CSV file."""
    _source_file_path = Path("tests/_test_input/example_full_hourly.csv")

    data_file = DataFileCSV(source_file_path=_source_file_path, loader=load_full_hourly_ep_output)
    assert data_file.file_name == "example_full_hourly.csv"

    with pytest.raises(NoDataLoadedError):
        data_file.data

    data_file.load_file_data()
    assert data_file.data.shape == (8760, 53)
