from pathlib import Path

import pytest

from ph_adorb.ep_html_file import (
    DataFileEPTables,
    MissingTableError,
    NoDataLoadedError,
    load_construction_cost_estimate_data,
    load_peak_electric_usage_data,
)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_load_construction_cost_estimate_data():
    """Test loading the 'Construction Cost Estimate Summary' table data."""
    _source_file_path = Path("tests/_test_input/example_annual_tables.htm")
    file_data = DataFileEPTables(source_file_path=_source_file_path, loader=load_construction_cost_estimate_data)

    with pytest.raises(NoDataLoadedError):
        file_data.data

    """
    NOTE: if not ignored:
        FAILED tests/test_ep_html_file.py::test_load_construction_cost_estimate_data 
        - DeprecationWarning: The 'strip_cdata' option of HTMLParser() has never 
        done anything and will eventually be removed.
    """
    file_data.load_file_data()
    assert file_data.data is not None
    assert len(file_data.data) == 2
    assert len(file_data.data[0]) == 34


def test_malformed_construction_cost_estimate_htm_file():
    # -- Create a temporary fake HTML file without the right table
    fake_html_file = Path("tests/_test_input/fake.htm")

    with open(fake_html_file, "w") as file:
        file.write("<html><body><table><tr><td>fake</td></tr></table></body></html>")

    file_data = DataFileEPTables(source_file_path=fake_html_file, loader=load_construction_cost_estimate_data)

    try:
        with pytest.raises(MissingTableError):
            file_data.load_file_data()
    finally:
        # -- Cleanup
        fake_html_file.unlink()


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_load_peak_electric_usage_data():
    """Test loading the 'Annual and Peak Values - Electricity' table data."""
    _source_file_path = Path("tests/_test_input/example_annual_tables.htm")
    file_data = DataFileEPTables(source_file_path=_source_file_path, loader=load_peak_electric_usage_data)

    with pytest.raises(NoDataLoadedError):
        file_data.data

    file_data.load_file_data()
    assert file_data.data == 3_932.53


def test_malformed_peak_electric_usage_htm_file():
    # -- Create a temporary fake HTML file without the right table
    fake_html_file = Path("tests/_test_input/fake.htm")

    with open(fake_html_file, "w") as file:
        file.write("<html><body><table><tr><td>fake</td></tr></table></body></html>")

    file_data = DataFileEPTables(source_file_path=fake_html_file, loader=load_peak_electric_usage_data)

    try:
        with pytest.raises(MissingTableError):
            file_data.load_file_data()
    finally:
        # -- Cleanup
        fake_html_file.unlink()
