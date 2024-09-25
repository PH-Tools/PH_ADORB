# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Functions to preview variant costs in table-format."""

from collections import defaultdict
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ph_adorb.constructions import PhAdorbConstructionCollection
from ph_adorb.equipment import PhAdorbEquipmentCollection
from ph_adorb.yearly_values import YearlyCost, YearlyKgCO2


def preview_variant_equipment(_equipment_collection: PhAdorbEquipmentCollection, _output_path: Path | None) -> None:
    # Create the table
    table = Table(title="Variant Equipment", show_lines=True)
    table.add_column("Equipment", style="cyan", justify="center", min_width=20, no_wrap=True)
    table.add_column("Type", style="magenta", justify="center")
    table.add_column("USD", style="magenta", justify="center")
    table.add_column("Lifetime (years)", style="magenta", justify="center")
    table.add_column("Labor Fraction [%]", style="magenta", justify="center")

    # Iterate over the equipment collection and add rows to the table
    for equipment in _equipment_collection:
        table.add_row(
            equipment.name,
            equipment.equipment_type.name,
            f"{equipment.cost:,.2f}",
            f"{equipment.lifetime_years:.0f}",
            f"{equipment.labor_fraction * 100.0 :.0f}",
        )

    # Output the table to the console or write to a file
    if _output_path:
        with open(Path(_output_path / "equipment.txt"), "w") as f:
            file_console = Console(file=f)
            file_console.print(table)
    else:
        console = Console()
        console.print(table)


def preview_variant_constructions(
    _construction_collection: PhAdorbConstructionCollection, _output_path: Path | None
) -> None:
    # Create the table
    table = Table(title="Variant Constructions", show_lines=True)
    table.add_column("Construction", style="cyan", justify="center", min_width=20, no_wrap=True)
    table.add_column("Area (M2)", style="magenta", justify="center")
    table.add_column("USD/M2", style="magenta", justify="center")
    table.add_column("Total USD", style="magenta", justify="center")
    table.add_column("kgCO2 / M2", style="magenta", justify="center")
    table.add_column("Total kgCO2", style="magenta", justify="center")
    table.add_column("Lifetime (years)", style="magenta", justify="center")
    table.add_column("Labor Fraction [%]", style="magenta", justify="center")

    # Iterate over the construction collection and add rows to the table
    for construction in _construction_collection:

        table.add_row(
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
        with open(Path(_output_path / "constructions.txt"), "w") as f:
            file_console = Console(file=f)
            file_console.print(table)
    else:
        console = Console()
        console.print(table)


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
    table = Table(title="Variant Install Costs (USD) by Year", show_lines=True)
    table.add_column("Description", style="cyan", justify="center", min_width=20, no_wrap=True)

    for year in sorted_years:
        table.add_column(str(year), style="magenta", justify="center", min_width=8)

    for description, costs in grouped_data.items():
        row = [description] + [
            f"{costs.get(year, 0):,.2f}" if costs.get(year, 0) != 0 else "-" for year in sorted_years
        ]
        table.add_row(*row)

    if _output_path:
        with open(Path(_output_path / "yearly_install_costs.txt"), "w") as f:
            console = Console(file=f)
            console.print(table)
    else:
        console = Console()
        console.print(table)


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
    table = Table(title="Variant Embodied-CO2 (kgCO2) by Year", show_lines=True)
    table.add_column("Description", style="cyan", justify="center", min_width=20, no_wrap=True)

    for year in sorted_years:
        table.add_column(str(year), style="magenta", justify="center", min_width=8)

    for description, costs in grouped_data.items():
        row = [description] + [
            f"{costs.get(year, 0):,.2f}" if costs.get(year, 0) != 0 else "-" for year in sorted_years
        ]
        table.add_row(*row)

    if _output_path:
        with open(Path(_output_path / "yearly_embodied_CO2_kg.txt"), "w") as f:
            console = Console(file=f)
            console.print(table)
    else:
        console = Console()
        console.print(table)


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
    table = Table(title="Variant Embodied-CO2 Costs (USD) by Year.", show_lines=True)
    table.add_column("Description", style="cyan", justify="center", min_width=20, no_wrap=True)

    for year in sorted_years:
        table.add_column(str(year), style="magenta", justify="center", min_width=8)

    for description, costs in grouped_data.items():
        row = [description] + [
            f"{costs.get(year, 0):,.2f}" if costs.get(year, 0) != 0 else "-" for year in sorted_years
        ]
        table.add_row(*row)

    if _output_path:
        with open(Path(_output_path / "yearly_embodied_CO2_costs.txt"), "w") as f:
            console = Console(file=f)
            console.print(table)
    else:
        console = Console()
        console.print(table)
