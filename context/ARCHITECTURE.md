---
DATE: 2026-07-15
STATUS: ORIENTATION (deep docs are authoritative — see below)
---

# PH-ADORB — Architecture (orientation)

Short map. The **authoritative** deep docs live in the public spoke:

- [`../docs/architecture.md`](../docs/architecture.md) — full architecture
- [`../docs/concepts.md`](../docs/concepts.md) — the ADORB concepts/method
- [`../docs/cli-usage.md`](../docs/cli-usage.md) — running it

Source-of-truth method references (PDFs/workbook): [`../_reference/`](../_reference/).

## The shape

```
Honeybee-REVIVE HBJSON ──from_HBJSON──► Variant ──adorb_cost──► ADORB cost (+ tables, graph)
```

- **`variant.py`** — the building variant being evaluated (the central object).
- **`adorb_cost.py`** — the ADORB cost calculation over a variant.
- **Inputs:** `constructions.py`, `equipment.py`, `fuel.py`, `grid_region.py`, `national_emissions.py`, `measures.py`, `yearly_values.py`, `ep_sql_file.py` (EnergyPlus SQL results).
- **`from_HBJSON/`** — `read_HBJSON_file.py` + `create_variant.py`: build a `Variant` from a Honeybee-REVIVE model.
- **`run/`** — `calc_HBJSON_ADORB_costs.py` (orchestration) + `generate_ADORB_cost_graph.py` (plotly output).
- **`tables/`** — tabular output builders.

## Correctness anchor

This is an adaptation of the Phius Research Committee's reference implementation — the method in `_reference/` (Appendix A + the REVIVE 2024 standard) is the correctness anchor. See `CODING_STANDARDS.md`.
