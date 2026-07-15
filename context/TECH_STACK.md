---
DATE: 2026-07-15
STATUS: CANONICAL
---

# PH-ADORB — Tech Stack

## Runtime

- **CPython ≥ 3.10.** A numeric library — not IPy2.7, not loaded into Rhino. The Grasshopper side calls it via subprocess.

## Dependencies

Runtime (`pyproject.toml`): `honeybee-energy`, `honeybee-revive`, `pandas`, `plotly`, `ph-units`, `rich`.
Dev extras: `black`, `isort`, `pytest`, `coverage`.

## Packaging

- setuptools + wheel; single package `ph_adorb`. Published to PyPI as **`PH-ADORB`**.

## Testing

- **pytest** — `python -m pytest`. Coverage via `coverage` (100% target; HTML → `_coverage_html/`).
- Tests in `tests/`, mirroring the package.

## Formatting

- **Black** + **isort**.

## Versioning & release

- Version in `pyproject.toml` `[project] version`. GitHub-Release-driven build/deploy via `.github/workflows/ci.yml`.

## Docs

- `docs/` is a **spoke** in the ph-docs Astro hub: `index.md`, `nav.yml`, plus hand-authored `getting-started.md`, `architecture.md`, `concepts.md`, `cli-usage.md`. Do not restructure `docs/`; keep `nav.yml` current. See `docs/.instructions.md`. The docs are mid-rewrite — see `planning/docs-rewrite-plan.md`.

## Reference material

- `_reference/` holds the Phius standard PDFs, the ADORB cost-calculation-method appendix, and the assessment workbook — the source method this library implements. Read-only reference; not part of the package.
