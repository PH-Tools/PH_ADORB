# PH_ADORB Documentation Plan

> Generated 2026-04-23. Check off items as completed.

## Overview

The `docs/` folder was bootstrapped by copying from `honeybee-REVIVE`. All content
currently references REVIVE, not PH_ADORB. This plan covers:

1. Rewriting the spoke docs (index, getting-started, packages/architecture)
2. Adding new content pages (concepts, CLI usage)
3. Auditing and updating every docstring in the source code for autodoc quality
4. Updating `nav.yml` to match the new structure

### Important: Python version note

PH_ADORB is **Python 3.10+** (uses `list[float]`, `dict[str, ...]`, `X | Y` unions).
The `.instructions.md` Python 2.7 / `# type:` comment rule was carried over from
honeybee-REVIVE and does **not** apply here. This repo uses native type annotations.
The ph-docs autodoc generator (`ast.parse()`) handles both styles.

---

## Phase 1 — Rewrite existing spoke pages

- [x] **1.1 `index.md`** — Rewrite front-matter for PH_ADORB (title, subtitle, version, pills)
- [x] **1.2 `getting-started.md`** — Rewrite for PH_ADORB: what it is, prerequisites, install, typical workflow diagram, links
- [x] **1.3 `packages.md` -> `architecture.md`** — Replace REVIVE packages page with a PH_ADORB architecture overview: module map, data flow, key classes
- [x] **1.4 `nav.yml`** — Update to reflect new page structure (remove REVIVE API entries)

## Phase 2 — Add new content pages

- [x] **2.1 `concepts.md`** — ADORB methodology explained: the five cost components, present value discounting, analysis duration, grid transition cost, embodied CO2
- [x] **2.2 `cli-usage.md`** — Document the two CLI scripts (`calc_HBJSON_ADORB_costs.py`, `generate_ADORB_cost_graph.py`): arguments, example invocations, output files

## Phase 3 — Docstring audit (source code)

Goal: every public class, property, method, and module-level function has a docstring
that meets the ph-docs autodoc format so the generated API reference pages are useful.

Rules (from `.instructions.md`):
- **Class**: line 1 = what IS this thing; optional extended context; `Attributes:` section for `__init__` attrs
- **Property**: one-line docstring
- **Method/Function**: imperative summary; `Arguments:` + `Returns:` sections when non-trivial
- **Enum**: summary + `Values:` section listing each allowed value
- **Skip**: `to_dict`, `from_dict`, `duplicate`, `__copy__`, `__str__`, `__repr__`, `__hash__`, private methods, trivial property getters

### 3.1 — Core data model modules

- [x] **`fuel.py`** — `PhAdorbFuelType` (enum, add Values docstring), `PhAdorbFuel` (add class + Attributes docstring)
- [x] **`grid_region.py`** — `PhAdorbGridRegion` (expand Attributes), `get_CO2_factors_as_df` (OK), free functions (OK)
- [x] **`national_emissions.py`** — `PhAdorbNationalEmissions` (add Attributes docstring)
- [x] **`yearly_values.py`** — `YearlyCost`, `YearlyKgCO2`, `YearlyPresentValueFactor` (add Attributes docstrings)
- [x] **`measures.py`** — `CO2MeasureType` (enum, add Values), `PhAdorbCO2ReductionMeasure` (add Attributes), `PhAdorbCO2MeasureCollection` (expand docstring, document `add_measure`/`get_measure`/properties)
- [x] **`constructions.py`** — `PhAdorbConstruction` (add Attributes), `PhAdorbConstructionCollection` (expand, document methods), `set_constructions_ft2_quantities` (has docstring, OK)
- [x] **`equipment.py`** — `PhAdorbEquipmentType` (enum, add Values), `PhAdorbEquipment` (add Attributes), `PhAdorbEquipmentCollection` (expand, document methods)

### 3.2 — Calculation modules

- [x] **`adorb_cost.py`** — Module docstring (OK). Functions: add `Arguments:` / `Returns:` sections to all 7 functions
- [x] **`variant.py`** — `PhAdorbVariant` (expand class docstring with Attributes). Free functions: add `Arguments:` / `Returns:` where missing. Fix `calc_annual_total_gas_CO2` (missing docstring entirely)

### 3.3 — I/O and integration modules

- [x] **`ep_sql_file.py`** — `DataFileSQL` (expand class docstring). Fix copy-paste docstring errors on `get_hourly_purchased_electricity_kwh`, `get_total_purchased_electricity_kwh`, `get_total_sold_electricity_kwh` (all say "Demand Rate [W]" but return kWh). Add docstring to `get_total_end_kwh_by_fuel_type`
- [x] **`from_HBJSON/read_HBJSON_file.py`** — Already well-documented. Minor: `HBJSONModelReadError` error message mentions "WUFI XML" — fixed to "ADORB Variant"
- [x] **`from_HBJSON/create_variant.py`** — Functions have one-liners, mostly OK. Add `Arguments:` / `Returns:` to `get_PhAdorbVariant_from_hb_model`

### 3.4 — Output / preview modules

- [x] **`tables/variant.py`** — Add docstrings to functions that lack them: `preview_hourly_electric_and_CO2`, `preview_yearly_energy_and_CO2`, `preview_variant_co2_measures`, `preview_variant_constructions`, `preview_yearly_install_costs`, `preview_yearly_embodied_kgCO2`, `preview_yearly_embodied_CO2_costs`, `add_total_row`

### 3.5 — CLI scripts

- [x] **`run/calc_HBJSON_ADORB_costs.py`** — Module docstring (OK). Add docstrings: `setup_logger`, `InputFileError`, `_remove_folder_and_contents` (has none)
- [x] **`run/generate_ADORB_cost_graph.py`** — Module docstring (OK). `InputFileError` (add docstring)

## Phase 4 — Final verification

- [x] **4.1** Verify every `.md` file (except `index.md`) is listed in `nav.yml`
- [x] **4.2** Verify front-matter on first file of each nav group has `card_title` + `card_description`
- [x] **4.3** Grep for any remaining "REVIVE" / "honeybee-revive" / "honeybee_revive" references in `docs/` — all remaining are legitimate upstream references
- [x] **4.4** Spot-check docstrings against autodoc format rules — 100% coverage of public classes/functions
- [x] **4.5** All 43 tests pass
