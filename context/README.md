# context/ — canonical repo documentation

Stable, ground-truth documentation for PH-ADORB. Distinct from `planning/` (in-flight work) and `docs/` (the public site published by the ph-docs hub).

As with PHX, the **deep architecture/concepts** already live in the public `docs/` spoke and are authoritative there; `context/` holds scope, a short orientation, and the engineering rules, and points to `docs/` for the detail.

## Index

| Doc | Read when you need… |
|-----|---------------------|
| [`PRD.md`](PRD.md) | What PH-ADORB computes, for whom, and what belongs here |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Short orientation + pointers to the authoritative deep docs |
| [`TECH_STACK.md`](TECH_STACK.md) | Runtime, deps, packaging, testing, CI, release |
| [`CODING_STANDARDS.md`](CODING_STANDARDS.md) | Style, numeric-correctness rules, testing |

Authoritative deep docs (in the public spoke): `../docs/architecture.md`, `../docs/concepts.md`, `../docs/cli-usage.md`.
Source references: `../_reference/` (Phius standard PDFs + assessment workbook).

## Maintenance rule

When a change alters the method or the object model, update the relevant doc (here or in `docs/`, wherever that topic is authoritative), and keep it matched to the Phius reference method.
