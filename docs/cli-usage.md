---
title: CLI Usage
---

# CLI Usage

PH-ADORB includes two command-line scripts for batch processing outside of Python.

## calc_HBJSON_ADORB_costs.py

Reads a Honeybee-REVIVE `.hbjson` model and an EnergyPlus `.sql` results file,
calculates yearly and cumulative ADORB costs, and writes the results to CSV files
plus a set of HTML preview tables.

### Arguments

| # | Argument | Description |
|---|----------|-------------|
| 1 | HBJSON path | Path to the `.hbjson` model file |
| 2 | SQL path | Path to the EnergyPlus `.sql` results file |
| 3 | Annual CSV path | Output path for the yearly ADORB costs CSV |
| 4 | Cumulative CSV path | Output path for the cumulative ADORB costs CSV |
| 5 | Tables folder path | Output folder for HTML preview tables |

### Example

```bash
python -m ph_adorb.run.calc_HBJSON_ADORB_costs \
    model.hbjson \
    results.sql \
    output/yearly.csv \
    output/cumulative.csv \
    output/tables/
```

### Outputs

- **Yearly CSV** — one row per year, five cost columns (`pv_direct_energy`,
  `pv_operational_CO2`, `pv_direct_MR`, `pv_embodied_CO2`, `pv_e_trans`)
- **Cumulative CSV** — running cumulative sum of the yearly costs
- **Preview tables/** — HTML files for inspection:
  - `hourly_electric_kwh.html` — hourly electricity + CO2 factors
  - `annual_electric_kwh_and_CO2.html` — annual energy + CO2 by future year
  - `co2_measures.html` — CO2 reduction measures summary
  - `constructions.html` — construction assemblies
  - `equipment.html` — equipment and appliances
  - `yearly_install_costs.html` — install costs by year
  - `yearly_embodied_CO2_kg.html` — embodied kgCO2 by year
  - `yearly_embodied_CO2_costs.html` — embodied CO2 costs by year
- **Log file** — `calc_HBJSON_ADORB_costs.log` written to the annual CSV directory

## generate_ADORB_cost_graph.py

Reads a cumulative ADORB costs CSV and generates a stacked area chart as an
interactive Plotly HTML file.

### Arguments

| # | Argument | Description |
|---|----------|-------------|
| 1 | CSV path | Path to the cumulative ADORB costs CSV |
| 2 | Output path | Path for the output HTML graph file |

### Example

```bash
python -m ph_adorb.run.generate_ADORB_cost_graph \
    output/cumulative.csv \
    output/adorb_graph.html
```

### Output

An interactive HTML file with a stacked area chart showing each cost category
over the analysis duration. The chart uses Plotly's CDN for rendering.
