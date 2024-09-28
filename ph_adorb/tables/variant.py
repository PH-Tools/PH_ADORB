# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Functions to preview variant costs in table-format."""

from collections import defaultdict
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ph_adorb.measures import PhAdorbCO2MeasureCollection
from ph_adorb.constructions import PhAdorbConstructionCollection
from ph_adorb.equipment import PhAdorbEquipmentCollection
from ph_adorb.yearly_values import YearlyCost, YearlyKgCO2


def rich_table_to_html(_tbl: Table) -> str:
    """Convert a rich-Table to an HTML-table.

    Args:
        _tbl (Table): The rich Table to convert.
    Returns:
        str: The HTML table as a string.
    """

    # Extract headers
    headers = [column.header for column in _tbl.columns]

    # Extract row data
    rows = [[column._cells[i] for column in _tbl.columns] for i in range(_tbl.row_count)]

    # Construct HTML table with inline styling
    html_ = '<table style="border-collapse: collapse; width: 100%; font-family: sans-serif;">\n'
    html_ += f'  <caption style="caption-side: top; font-size: 1.5em; font-weight: bold; padding: 10px;">{_tbl.title}</caption>\n'
    html_ += '  <thead>\n    <tr style="background-color: #f2f2f2; font-weight: bold;">\n'
    for header in headers:
        html_ += f'      <th style="padding: 8px; text-align: center;">{header}</th>\n'
    html_ += "    </tr>\n  </thead>\n"
    html_ += "  <tbody>\n"
    for i, row in enumerate(rows):
        background_color = "#ffffff" if i % 2 == 0 else "#f2f2f2"
        html_ += f'    <tr style="background-color: {background_color};">\n'
        for cell in row:
            html_ += f'      <td style="padding: 8px; text-align: center;">{cell}</td>\n'
        html_ += "    </tr>\n"
    html_ += "  </tbody>\n</table>\n"

    return html_


def preview_hourly_electric_and_CO2(
    _hourly_kwh: list[float], _hourly_CO2_factors: dict[int, list[float]], _output_path: Path | None
) -> None:
    # Create the table
    tbl_ = Table(title="Hourly Electric Consumption (kWh) and CO2 Factors (kgCO2/kWh)", show_lines=True)
    tbl_.add_column("Hour", style="cyan", justify="center", min_width=20, no_wrap=True)
    tbl_.add_column("kWh", style="magenta", justify="center")
    for year in _hourly_CO2_factors.keys():
        tbl_.add_column(f"{year}", style="magenta", justify="center")

    # Iterate over the hourly data and add rows to the table
    for i, kwh in enumerate(_hourly_kwh):
        factors_by_year: list[str] = []
        for yearly_factors in _hourly_CO2_factors.values():
            factors_by_year.append(f"{yearly_factors[i]:,.2f}")
        tbl_.add_row(f"{i:04d}", f"{kwh:,.2f}", *factors_by_year)

    # Output the table to the console or write to a file
    if _output_path:
        html_table = rich_table_to_html(tbl_)
        with open(Path(_output_path / "hourly_electric_kwh.html"), "w") as f:
            f.write(html_table)
    else:
        console = Console()
        console.print(tbl_)


def preview_yearly_energy_and_CO2(
    _elec_kwh: float, _elec_CO2_by_future_year: list[float], _gas_kwh: float, _gas_CO2: float, _output_path: Path | None
) -> None:
    # Create the table
    tbl_ = Table(title="Future Annual Energy Consumption and CO2 Emissions", show_lines=True)
    tbl_.add_column("Year", style="cyan", justify="center", min_width=20, no_wrap=True)
    tbl_.add_column("Elec. kWh", style="magenta", justify="center")
    tbl_.add_column("Elec. kgCO2", style="magenta", justify="center")
    tbl_.add_column("Elec. Grid Factor (kgCO2/kWh)", style="magenta", justify="center")
    tbl_.add_column("Gas kWh", style="magenta", justify="center")
    tbl_.add_column("Gas kgCO2", style="magenta", justify="center")
    tbl_.add_column("Gas Grid Factor (kgCO2/kWh)", style="magenta", justify="center")

    # Iterate over the hourly data and add rows to the table
    for i, co2 in enumerate(
        _elec_CO2_by_future_year,
    ):
        try:
            elec_grid_factor = co2 / _elec_kwh
        except ZeroDivisionError:
            elec_grid_factor = 0.0

        try:
            gas_grid_factor = _gas_CO2 / _gas_kwh
        except ZeroDivisionError:
            gas_grid_factor = 0.0

        tbl_.add_row(
            f"{2023+i:02d}",
            f"{_elec_kwh:,.2f}",
            f"{co2:,.2f}",
            f"{elec_grid_factor:,.3f}",
            f"{_gas_kwh:,.2f}",
            f"{_gas_CO2:,.2f}",
            f"{gas_grid_factor:,.3f}",
        )

    # Output the table to the console or write to a file
    if _output_path:
        html_table = rich_table_to_html(tbl_)
        with open(Path(_output_path / "annual_electric_kwh_and_CO2.html"), "w") as f:
            f.write(html_table)
    else:
        console = Console()
        console.print(tbl_)


def preview_variant_co2_measures(
    _co2_measure_collection: PhAdorbCO2MeasureCollection, _output_path: Path | None
) -> None:
    # Create the table
    tbl_ = Table(title="Variant CO2 Reduction Measures", show_lines=True)
    tbl_.add_column("Measure", style="cyan", justify="center", min_width=20, no_wrap=True)
    tbl_.add_column("Type", style="magenta", justify="center")
    tbl_.add_column("Year", style="magenta", justify="center")
    tbl_.add_column("USD", style="magenta", justify="center")
    tbl_.add_column("(kgCO2)", style="magenta", justify="center")
    tbl_.add_column("Country Name", style="magenta", justify="center")
    tbl_.add_column("Labor Fraction [%]", style="magenta", justify="center")

    # Iterate over the CO2 measure collection and add rows to the table
    for measure in _co2_measure_collection:
        tbl_.add_row(
            measure.name,
            measure.measure_type.name,
            f"{measure.year}",
            f"{measure.cost:,.2f}",
            f"{measure.kg_CO2:.0f}" if measure.kg_CO2 is not None else "-",
            f"{measure.country_name}",
            f"{measure.labor_fraction * 100.0 :.0f}",
        )

    # Output the table to the console or write to a file
    if _output_path:
        html_table = rich_table_to_html(tbl_)
        with open(Path(_output_path / "co2_measures.html"), "w") as f:
            f.write(html_table)
    else:
        console = Console()
        console.print(tbl_)


def preview_variant_equipment(_equipment_collection: PhAdorbEquipmentCollection, _output_path: Path | None) -> None:
    # Create the table
    tbl_ = Table(title="Variant Equipment", show_lines=True)
    tbl_.add_column("Equipment/Appliance", style="cyan", justify="center", min_width=20, no_wrap=True)
    tbl_.add_column("Type", style="magenta", justify="center")
    tbl_.add_column("USD", style="magenta", justify="center")
    tbl_.add_column("Lifetime (years)", style="magenta", justify="center")
    tbl_.add_column("Labor Fraction [%]", style="magenta", justify="center")

    # Iterate over the equipment collection and add rows to the table
    for equipment in _equipment_collection:
        tbl_.add_row(
            equipment.name,
            equipment.equipment_type.name,
            f"{equipment.cost:,.2f}",
            f"{equipment.lifetime_years:.0f}",
            f"{equipment.labor_fraction * 100.0 :.0f}",
        )

    # Output the table to the console or write to a file
    if _output_path:
        html_table = rich_table_to_html(tbl_)
        with open(Path(_output_path / "equipment.html"), "w") as f:
            f.write(html_table)
    else:
        console = Console()
        console.print(tbl_)


def preview_variant_constructions(
    _construction_collection: PhAdorbConstructionCollection, _output_path: Path | None
) -> None:
    # Create the table
    tbl_ = Table(title="Variant Constructions", show_lines=True)
    tbl_.add_column("Construction", style="cyan", justify="center", min_width=20, no_wrap=True)
    tbl_.add_column("Area (M2)", style="magenta", justify="center")
    tbl_.add_column("USD/M2", style="magenta", justify="center")
    tbl_.add_column("Total USD", style="magenta", justify="center")
    tbl_.add_column("kgCO2 / M2", style="magenta", justify="center")
    tbl_.add_column("Total kgCO2", style="magenta", justify="center")
    tbl_.add_column("Lifetime (years)", style="magenta", justify="center")
    tbl_.add_column("Labor Fraction [%]", style="magenta", justify="center")

    # Iterate over the construction collection and add rows to the table
    for construction in _construction_collection:

        tbl_.add_row(
            construction.display_name,
            f"{construction.area_m2:,.2f}",
            f"{construction.cost_per_m2:,.2f}",
            f"{construction.cost:,.2f}",
            f"{construction.CO2_kg_per_m2:,.2f}",
            f"{construction.CO2_kg:,.2f}",
            f"{construction.lifetime_years:.0f}",
            f"{construction.labor_fraction * 100.0 :.0f}",
        )

    # Output the table to the console or write to a file
    if _output_path:
        html_table = rich_table_to_html(tbl_)
        with open(Path(_output_path / "constructions.html"), "w") as f:
            f.write(html_table)
    else:
        console = Console()
        console.print(tbl_)


def preview_yearly_install_costs(_input: list[YearlyCost], _output_path: Path | None) -> None:
    # Group the data by description
    grouped_data = defaultdict(lambda: defaultdict(float))
    unique_years = set()

    for item in _input:
        grouped_data[item.description][item.year] += item.cost
        unique_years.add(item.year)

    # Sort the years to ensure columns are in order
    sorted_years = sorted(unique_years)

    # Create the table
    tbl_ = Table(title="Variant Install Costs (USD) by Year", show_lines=True)
    tbl_.add_column("Description", style="cyan", justify="center", min_width=20, no_wrap=True)

    for year in sorted_years:
        tbl_.add_column(str(year), style="magenta", justify="center", min_width=8)

    for description, costs in grouped_data.items():
        row = [description] + [
            f"{costs.get(year, 0):,.2f}" if costs.get(year, 0) != 0 else "-" for year in sorted_years
        ]
        tbl_.add_row(*row)

    if _output_path:
        html_table = rich_table_to_html(tbl_)
        with open(Path(_output_path / "yearly_install_costs.html"), "w") as f:
            f.write(html_table)
    else:
        console = Console()
        console.print(tbl_)


def preview_yearly_embodied_kgCO2(_input: list[YearlyKgCO2], _output_path: Path | None) -> None:
    # Group the data by description
    grouped_data = defaultdict(lambda: defaultdict(float))
    unique_years = set()

    for item in _input:
        grouped_data[item.description][item.year] += item.kg_CO2
        unique_years.add(item.year)

    # Sort the years to ensure columns are in order
    sorted_years = sorted(unique_years)

    # Create the table
    tbl_ = Table(title="Variant Embodied-CO2 (kgCO2) by Year", show_lines=True)
    tbl_.add_column("Description", style="cyan", justify="center", min_width=20, no_wrap=True)

    for year in sorted_years:
        tbl_.add_column(str(year), style="magenta", justify="center", min_width=8)

    for description, costs in grouped_data.items():
        row = [description] + [
            f"{costs.get(year, 0):,.2f}" if costs.get(year, 0) != 0 else "-" for year in sorted_years
        ]
        tbl_.add_row(*row)

    if _output_path:
        html_table = rich_table_to_html(tbl_)
        with open(Path(_output_path / "yearly_embodied_CO2_kg.html"), "w") as f:
            f.write(html_table)
    else:
        console = Console()
        console.print(tbl_)


def preview_yearly_embodied_CO2_costs(_input: list[YearlyCost], _output_path: Path | None) -> None:
    # Group the data by description
    grouped_data = defaultdict(lambda: defaultdict(float))
    unique_years = set()

    for item in _input:
        grouped_data[item.description][item.year] += item.cost
        unique_years.add(item.year)

    # Sort the years to ensure columns are in order
    sorted_years = sorted(unique_years)

    # Create the table
    tbl_ = Table(title="Variant Embodied-CO2 Costs (USD) by Year.", show_lines=True)
    tbl_.add_column("Description", style="cyan", justify="center", min_width=20, no_wrap=True)

    for year in sorted_years:
        tbl_.add_column(str(year), style="magenta", justify="center", min_width=8)

    for description, costs in grouped_data.items():
        row = [description] + [
            f"{costs.get(year, 0):,.2f}" if costs.get(year, 0) != 0 else "-" for year in sorted_years
        ]
        tbl_.add_row(*row)

    if _output_path:
        html_table = rich_table_to_html(tbl_)
        with open(Path(_output_path / "yearly_embodied_CO2_costs.html"), "w") as f:
            f.write(html_table)
    else:
        console = Console()
        console.print(tbl_)
