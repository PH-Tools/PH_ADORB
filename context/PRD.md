---
DATE: 2026-07-15
STATUS: CANONICAL PRD (WIP library)
---

# PH-ADORB — Product Requirements

## 1. Goal

Compute the **ADORB cost** for a building variant — the Phius-REVIVE 2024 full-cost-accounted, annualized life-cycle metric combining direct retrofit/maintenance cost, direct energy cost, operating + embodied carbon cost, and renewable-transition cost. Provide it as a clean, object-oriented Python library adapted from the Phius Research Committee's reference implementation.

## 2. Who uses it

- **honeybee_REVIVE_grasshopper** — calls PH-ADORB (via subprocess) to compute ADORB costs on the Grasshopper canvas.
- Researchers/Python users evaluating REVIVE retrofit scenarios (`pip install ph-adorb`).

## 3. What belongs here

- The ADORB cost calculation (`adorb_cost.py`) and the variant it evaluates (`variant.py`).
- The cost/carbon inputs: constructions, equipment, fuels, grid region, national emissions, measures, yearly values, E+ SQL results.
- `from_HBJSON/` (build a variant from a Honeybee-REVIVE model), `run/` (orchestrate calc + graph), `tables/` (tabular output).

## 4. Non-goals

- **Not a compliance tool.** WIP / research only; not Phius-approved.
- **No Grasshopper UI** — that is `honeybee_REVIVE_grasshopper`.
- **No IPy2.7 constraint** — this is a CPython numeric library and is not loaded into Rhino.

## 5. Success criteria

- Results match the Phius reference ADORB method (see `_reference/`).
- Runs cleanly in CPython 3.10+ with the numeric stack; 100% test coverage.
- Ingests Honeybee-REVIVE models via `from_HBJSON/` and produces cost + graph output.

## 6. Direction

- The docs are being rewritten/audited (currently partly inherited from honeybee-REVIVE) — see `planning/docs-rewrite-plan.md` and `planning/docs-plan.md`.
