# PH-ADORB

A Python library that computes the **ADORB cost** — Annualized De-carbonization Of Retrofitted Buildings: a full-cost-accounted annualized life-cycle metric (direct retrofit + maintenance + energy costs + operating & embodied carbon cost + renewable-transition cost) used in the Phius-REVIVE 2024 standard. Published on PyPI as `PH-ADORB`. Source: https://github.com/PH-Tools/PH_ADORB

> **WIP / research only.** An object-oriented adaptation of the Phius Research Committee's reference implementation. Not affiliated with, reviewed, or approved by Phius; do not use for actual compliance.

> **Runtime:** **CPython ≥ 3.10** — this is a numeric library (`pandas`, `plotly`). It is *not* IPy2.7 and does not run in Rhino; the Grasshopper side (`honeybee_REVIVE_grasshopper`) calls it via a subprocess.

## What this repo is

A single package, `ph_adorb`. Core: `adorb_cost.py` (the metric), `variant.py` (the building variant being evaluated), plus the cost/carbon inputs (`constructions.py`, `equipment.py`, `fuel.py`, `grid_region.py`, `national_emissions.py`, `measures.py`, `yearly_values.py`, `ep_sql_file.py`). `from_HBJSON/` builds a variant from a Honeybee-REVIVE model; `run/` orchestrates the calc + graph; `tables/` builds tabular output.

## Where things live — read before working

| Working on… | Read |
|-------------|------|
| Product scope, what belongs here | `context/PRD.md` |
| Orientation + where the deep docs are | `context/ARCHITECTURE.md` |
| **Full** architecture / concepts (authoritative) | `docs/architecture.md`, `docs/concepts.md` |
| Code rules (style, numeric care, testing) | `context/CODING_STANDARDS.md` |
| Deps, packaging, CI, release | `context/TECH_STACK.md` |
| Current / in-flight work (incl. docs rewrite) | `planning/STATUS.md` |
| The public docs site (autodoc spoke — do not restructure) | `docs/.instructions.md` |
| Source PDFs / workbook (Phius standard, appendix) | `_reference/` |

Full context index: `context/README.md`.

## Hard rules

1. **Match the Phius reference method.** This is an adaptation of the Phius Research Committee's ADORB implementation — correctness means matching the referenced method (`_reference/Appendix A – ADORB Cost Calculation Method.pdf`, `_reference/Phius REVIVE 2024 Standard…pdf`). Don't "improve" the math without a reference.
2. **CPython numeric library.** `pandas`/`plotly` are fine and expected. No IPy2.7 constraint.
3. **Docs are an autodoc spoke.** New/renamed public API → update `docs/nav.yml` + docstrings in the `ph-docs` format (`docs/.instructions.md`). Never restructure `docs/`. (The docs are being rewritten — see `planning/docs-rewrite-plan.md`.)
4. **Verify before closeout:** `python -m pytest` (100% coverage target; HTML → `_coverage_html/`).

## Ecosystem

Consumes Honeybee-REVIVE models (`from_HBJSON/`), depends on `honeybee-revive` and `ph-units`. Invoked by **honeybee_REVIVE_grasshopper** via subprocess to produce ADORB costs on the Grasshopper canvas.
