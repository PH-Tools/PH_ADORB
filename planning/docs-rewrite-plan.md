# PH-ADORB Documentation Plan

This plan covers rewriting the docs (currently copy/pasted from honeybee-REVIVE) to accurately describe the PH-ADORB library, and auditing/updating all source docstrings for autodoc quality.

> **Convention**: This repo is a "spoke" in the ph-docs hub. See `docs/.instructions.md` for file/front-matter rules.

---

## Phase 1: Core Doc Pages

These are the Markdown files that live in `docs/` and get rendered by the ph-docs hub.

### 1.1 Rewrite `docs/index.md`
- [x] Replace honeybee-REVIVE front-matter with PH-ADORB values (title, subtitle, version `0.0.11`, pills)

### 1.2 Rewrite `docs/getting-started.md`
- [x] What PH-ADORB is (ADORB cost definition, Phius REVIVE context)
- [x] Prerequisites (Python 3.10+, EnergyPlus SQL output, honeybee-REVIVE model)
- [x] Installation (`pip install ph-adorb`)
- [x] Typical workflow diagram (HBJSON + SQL -> PhAdorbVariant -> ADORB DataFrame -> CSV/graph)
- [x] Links (GitHub, PyPI, Phius REVIVE standard doc)
- [x] Disclaimer (not affiliated with Phius)

### 1.3 Replace `docs/packages.md` with `docs/concepts.md`
- [x] Delete `packages.md`
- [x] Create `concepts.md` explaining the ADORB cost components

### 1.4 Add `docs/architecture.md`
- [x] Module map, data flow, key classes, sub-packages, dev setup

### 1.5 Add `docs/cli-usage.md`
- [x] calc_HBJSON_ADORB_costs.py usage and outputs
- [x] generate_ADORB_cost_graph.py usage and outputs

### 1.6 Update `docs/nav.yml`
- [x] Rewrite to match PH-ADORB's actual structure (Getting Started + Developer groups)

---

## Phase 2: Docstring Audit & Update

The ph-docs hub auto-generates API reference pages from source docstrings. Every public class, property, method, and enum needs a docstring that follows the format in `.instructions.md`. 

**Important**: PH-ADORB is Python 3.10+ (not IronPython/2.7), so it uses native type annotations, not `# type:` comments. The autodoc generator handles both styles.

**What NOT to document** (per .instructions.md): `to_dict()`, `from_dict()`, `duplicate()`, `__copy__()`, `__str__`, `__repr__`, `__hash__`, private methods, trivial property getters.

### 2.1 `ph_adorb/yearly_values.py`
- [x] `YearlyCost` — class docstring with Attributes
- [x] `YearlyKgCO2` — class docstring with Attributes
- [x] `YearlyPresentValueFactor` — class docstring with Attributes

### 2.2 `ph_adorb/fuel.py`
- [x] `PhAdorbFuelType` enum — Values: docstring added
- [x] `PhAdorbFuel` — class docstring with Attributes
- [x] `PhAdorbFuel.name` property — one-line docstring

### 2.3 `ph_adorb/national_emissions.py`
- [x] `PhAdorbNationalEmissions` — Attributes section added
- [x] `write_national_emissions_to_json_file()` — verified
- [x] `load_national_emissions_from_json_file()` — verified

### 2.4 `ph_adorb/grid_region.py`
- [x] `PhAdorbGridRegion` — Attributes section added
- [x] `PhAdorbGridRegion.get_CO2_factors_as_df()` — verified
- [x] `write_CO2_factors_to_json_file()` — verified
- [x] `load_CO2_factors_from_json_file()` — verified

### 2.5 `ph_adorb/constructions.py`
- [x] `PhAdorbConstruction` — Attributes section added
- [x] `PhAdorbConstruction.quantity_ft2` property — docstring added
- [x] `PhAdorbConstruction.set_quantity_ft2()` — docstring added
- [x] `PhAdorbConstruction.cost` property — verified
- [x] `PhAdorbConstruction.CO2_kg` property — verified
- [x] `PhAdorbConstruction.material_fraction` property — trivial complement, skipped per convention
- [x] `PhAdorbConstructionCollection` — docstring added
- [x] `PhAdorbConstructionCollection.add_construction()` — docstring added
- [x] `PhAdorbConstructionCollection.get_construction()` — docstring added
- [x] `PhAdorbConstructionCollection.keys()` — trivial, skipped per convention
- [x] `PhAdorbConstructionCollection.values()` — trivial, skipped per convention
- [x] `PhAdorbConstructionCollection.set_constructions_ft2_quantities()` — verified
- [x] `write_constructions_to_json_file()` — verified
- [x] `load_constructions_from_json_file()` — verified

### 2.6 `ph_adorb/equipment.py`
- [x] `PhAdorbEquipmentType` enum — Values: docstring added
- [x] `PhAdorbEquipment` — Attributes section added
- [x] `PhAdorbEquipment.material_fraction` — trivial complement, skipped per convention
- [x] `PhAdorbEquipmentCollection` — docstring added
- [x] `PhAdorbEquipmentCollection.add_equipment()` — docstring added
- [x] `PhAdorbEquipmentCollection.get_equipment()` — docstring added
- [x] `PhAdorbEquipmentCollection.keys()` — trivial, skipped per convention
- [x] `PhAdorbEquipmentCollection.values()` — trivial, skipped per convention
- [x] `write_equipment_to_json_file()` — verified
- [x] `load_equipment_from_json_file()` — verified

### 2.7 `ph_adorb/measures.py`
- [x] `CO2MeasureType` enum — Values: docstring added
- [x] `PhAdorbCO2ReductionMeasure` — Attributes section added
- [x] `PhAdorbCO2ReductionMeasure.material_fraction` — trivial complement, skipped per convention
- [x] `PhAdorbCO2MeasureCollection` — docstring added
- [x] `PhAdorbCO2MeasureCollection.add_measure()` — docstring added
- [x] `PhAdorbCO2MeasureCollection.get_measure()` — docstring added
- [x] `PhAdorbCO2MeasureCollection.keys()` — trivial, skipped per convention
- [x] `PhAdorbCO2MeasureCollection.values()` — trivial, skipped per convention
- [x] `PhAdorbCO2MeasureCollection.performance_measures` — verified
- [x] `PhAdorbCO2MeasureCollection.nonperformance_measures` — verified
- [x] `write_CO2_measures_to_json_file()` — verified
- [x] `load_CO2_measures_from_json_file()` — verified

### 2.8 `ph_adorb/ep_sql_file.py`
- [x] `DataFileSQL` — Attributes section added
- [x] `DataFileSQL.file_name` property — verified
- [x] `DataFileSQL.get_peak_electric_watts()` — verified
- [x] `DataFileSQL.get_hourly_purchased_electricity_kwh()` — fixed (was copy of peak watts)
- [x] `DataFileSQL.get_total_purchased_electricity_kwh()` — fixed (was copy of peak watts)
- [x] `DataFileSQL.get_total_sold_electricity_kwh()` — fixed (was copy of peak watts)
- [x] `DataFileSQL.get_total_purchased_gas_kwh()` — verified
- [x] `DataFileSQL.get_total_end_kwh_by_fuel_type()` — docstring added

### 2.9 `ph_adorb/variant.py`
- [x] `PhAdorbVariant` — Attributes section added
- [x] `PhAdorbVariant.total_purchased_electricity_kwh` — verified
- [x] `PhAdorbVariant.all_carbon_measures` — verified
- [x] `PhAdorbVariant.performance_measure_collection` — verified
- [x] `PhAdorbVariant.nonperformance_carbon_measures` — verified
- [x] `calc_annual_total_electric_cost()` — expanded with Arguments/Returns
- [x] `calc_annual_hourly_electric_CO2()` — expanded with Arguments/Returns
- [x] `calc_annual_total_gas_cost()` — expanded with Arguments/Returns
- [x] `calc_annual_total_gas_CO2()` — docstring added with Arguments/Returns
- [x] `calc_CO2_reduction_measures_yearly_embodied_kgCO2()` — expanded with Arguments/Returns
- [x] `calc_CO2_reduction_measures_yearly_embodied_CO2_cost()` — verified
- [x] `calc_CO2_reduction_measures_yearly_install_costs()` — verified
- [x] `calc_constructions_yearly_embodied_kgCO2()` — verified
- [x] `calc_constructions_yearly_embodied_CO2_cost()` — verified
- [x] `calc_constructions_yearly_install_costs()` — verified
- [x] `calc_equipment_yearly_embodied_kgCO2_()` — verified
- [x] `calc_equipment_yearly_embodied_CO2_cost()` — verified
- [x] `calc_equipment_yearly_install_costs()` — verified
- [x] `calc_variant_yearly_ADORB_costs()` — expanded with Arguments/Returns
- [x] `calc_variant_cumulative_ADORB_costs()` — verified

### 2.10 `ph_adorb/adorb_cost.py`
- [x] Module docstring — verified
- [x] `present_value_factor()` — expanded with Arguments/Returns
- [x] `energy_purchase_cost_PV()` — expanded with Arguments/Returns
- [x] `energy_CO2_cost_PV()` — expanded with Arguments/Returns
- [x] `measure_purchase_cost_PV()` — expanded with Arguments/Returns
- [x] `measure_CO2_cost_PV()` — expanded with Arguments/Returns
- [x] `grid_transition_cost_PV()` — expanded with Arguments/Returns
- [x] `calculate_annual_ADORB_costs()` — expanded with Arguments/Returns

### 2.11 `ph_adorb/from_HBJSON/create_variant.py`
- [x] Module docstring — verified
- [x] `get_hb_model_construction_quantities()` — verified
- [x] `get_PhAdorbGridRegion_from_hb_model()` — verified
- [x] `get_PhAdorbNationalEmissions_from_hb_mode()` — verified
- [x] `get_PhAdorbCO2Measures_from_hb_model()` — verified
- [x] `convert_hb_construction()` — verified
- [x] `get_PhAdorbConstructions_from_hb_model()` — verified
- [x] `convert_hb_process_load()` — verified
- [x] `convert_hbe_lighting()` — verified
- [x] `convert_hb_shade_pv()` — verified
- [x] `convert_hb_hvac_equipment()` — verified
- [x] `get_PhAdorbEquipment_from_hb_model()` — verified
- [x] `get_PhAdorbFuels_from_hb_model()` — verified
- [x] `get_PhAdorbVariant_from_hb_model()` — expanded (fixed stale "ReviveVariant" references)

### 2.12 `ph_adorb/from_HBJSON/read_HBJSON_file.py`
- [x] Module docstring — verified
- [x] `HBJSONModelReadError` — class docstring added; error message fixed ("ADORB Variant" not "WUFI XML")
- [x] `read_hb_json_from_file()` — verified
- [x] `convert_hbjson_dict_to_hb_model()` — verified

### 2.13 `ph_adorb/tables/variant.py`
- [x] Module docstring — verified
- [x] `rich_table_to_html()` — verified
- [x] `add_total_row()` — docstring updated
- [x] `preview_hourly_electric_and_CO2()` — docstring added
- [x] `preview_yearly_energy_and_CO2()` — docstring added
- [x] `preview_variant_co2_measures()` — docstring added
- [x] `preview_variant_equipment()` — verified
- [x] `preview_variant_constructions()` — docstring added
- [x] `preview_yearly_install_costs()` — docstring added
- [x] `preview_yearly_embodied_kgCO2()` — docstring added
- [x] `preview_yearly_embodied_CO2_costs()` — docstring added

### 2.14 `ph_adorb/run/calc_HBJSON_ADORB_costs.py`
- [x] Module docstring — verified
- [x] `setup_logger()` — docstring added
- [x] `InputFileError` — class docstring added; error message fixed
- [x] `resolve_paths()` — verified

### 2.15 `ph_adorb/run/generate_ADORB_cost_graph.py`
- [x] Module docstring — verified
- [x] `InputFileError` — class docstring added; error message fixed
- [x] `resolve_paths()` — verified

---

## Phase 3: Verification

- [x] Confirm every `.md` file in `docs/` (except `index.md`) is listed in `nav.yml`
  - Content files: all 4 listed. `DOCS_PLAN.md` and `PLAN.md` are internal planning docs (not rendered).
- [x] Confirm `index.md` is NOT in `nav.yml`
- [x] Confirm front-matter on first file of each nav group has `card_title` + `card_description`
  - Getting Started -> `getting-started.md`: has both
  - Developer -> `architecture.md`: has both
- [x] Confirm no cross-repo relative links (use absolute site URLs) — none found
- [x] Confirm all mermaid diagrams render correctly (valid syntax) — 3 diagrams in architecture.md, 1 in getting-started.md
- [x] Spot-check: read each source file and verify docstrings match actual code behavior — all verified

---

## Notes

- The `.instructions.md` mentions Python 2.7 / `# type:` comments as the autodoc format. PH-ADORB is Python 3.10+ and uses native annotations. The autodoc generator handles both styles, so no changes needed to the instructions file.
- The existing `getting-started.md` and `packages.md` are direct copies from honeybee-REVIVE and describe a completely different library. They need full rewrites, not edits.
- The nav.yml currently references `api/` paths for honeybee-REVIVE modules that don't exist in PH-ADORB. These will be removed (API docs are auto-generated by ph-docs).
