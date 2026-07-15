---
DATE: 2026-07-15
STATUS: CANONICAL ENGINEERING STANDARD
---

# PH-ADORB — Coding Standards

## 1. Correctness is defined by the Phius reference method

This library is an object-oriented adaptation of the Phius Research Committee's ADORB implementation. The **method** in `_reference/` (Appendix A – ADORB Cost Calculation Method; Phius REVIVE 2024 Standard) is the correctness anchor. Do not change the math to "improve" it without a reference; when in doubt, match the Phius reference implementation and cite it.

## 2. CPython numeric library

- **CPython 3.10+**; `pandas`/`plotly`/`numpy` are expected and fine. No IronPython-2.7 constraint.
- Modern typing/idioms are fine (this is not loaded into Rhino).

## 3. Structure

- Keep the cost inputs as their own objects (`constructions`, `equipment`, `fuel`, `grid_region`, `national_emissions`, `measures`, `yearly_values`) feeding `variant.py`; keep `adorb_cost.py` the place the metric is assembled.
- Model ingestion stays in `from_HBJSON/`; orchestration/output in `run/` and `tables/`.

## 4. Formatting

- **Black** + **isort**.

## 5. Testing

- **pytest** — `python -m pytest`. **100% coverage** target. New behavior needs tests; numeric changes should be pinned against reference values where available.

## 6. Docs

- Docstrings feed the autodoc site — keep them in the `ph-docs` format (`docs/.instructions.md`). New/renamed public API → update `docs/nav.yml`. (Docs are mid-rewrite — see `planning/docs-rewrite-plan.md`.)

## Closeout checklist

- [ ] Numeric changes match / cite the Phius reference method (`_reference/`).
- [ ] `python -m pytest` passes at 100% coverage.
- [ ] black + isort clean.
- [ ] `docs/nav.yml` + docstrings updated for new/renamed public API.
