# Design Notes (Compressed)
Date: 2026-02-11
Status: Active

This document summarizes the current design of PIE. It is a compressed, current-state view of prior design decisions. Each section includes the dates of the decisions it reflects.

## Scope
Dates: 2026-02-03, 2026-02-04, 2026-02-05, 2026-02-06, 2026-02-07, 2026-02-08, 2026-02-09, 2026-02-10, 2026-02-11
PIE is a Python 3.10+ library for inference engines with DLGPE parsing, rule/query abstractions, backward chaining, and FOQuery evaluation. The architecture favors explicit APIs, predictable module layout, and test-verified documentation.

## Repository Layout And Module Hierarchy
Dates: 2026-02-06, 2026-02-05
- Flat layout with importable packages at repo root; no `src/` layout.
- Core code lives under `prototyping_inference_engine/` with explicit subpackages (no catch-all modules).
- IO is under `prototyping_inference_engine/io/` with `parsers/` and `writers/`.
- IRI utilities are under `prototyping_inference_engine/api/iri/`.

## Core API Concepts
Dates: 2026-02-08, 2026-02-06
- Terms: `Variable`, `Constant`, and identity-aware term/predicate factories.
- Atoms: predicate + terms, substitution-aware.
- Queries: `FOQuery`, `ConjunctiveQuery`, `UnionQuery` with answer variables.
- Knowledge types: `RuleBase`, `KnowledgeBase`, and `Ontology` for disjunctive rules.
- Fact base capability protocols (e.g., `CSVCopyable`) to avoid hard dependencies.

## DLGPE Parsing And IRI Handling
Dates: 2026-02-06, 2026-02-07
- DLGPE is the canonical syntax; `.dlgp` files use DLGPE semantics.
- Nested functional terms are supported in DLGPE grammar.
- Parsing resolves IRIs and preserves prefix/base context in parse results.
- Undefined prefixes raise parsing errors to ensure consistent IRI resolution.

## Computed Functions And `@computed`
Dates: 2026-02-06, 2026-02-09
- `@computed` directives declare computed prefixes.
- Computed prefixes can map to standard functions (`<stdfct>`) and JSON configuration files for Python functions.
- Standard functions are exposed as computed predicates via `ReadableData` sources and support reversible evaluation for a subset (e.g., sum/minus/product/divide/average).
- JSON configuration defaults to module-level functions (no class required). Class-based loading remains optional.

## Query Evaluation And Prepared Queries
Dates: 2026-02-04, 2026-02-05, 2026-02-08, 2026-02-10
- FOQuery evaluators prepare queries before execution, per formula type.
- Prepared queries are cached for sub-formulas to avoid rebuilding during backtracking.
- Lightweight bound estimation guides scheduler ordering; the estimate is intended to be cheap.
- Backtracking conjunction evaluation uses a dynamic scheduler and prepared subqueries.
- Function-term rewriting expands terms into computed atoms and is evaluated via the FOQuery registry to decouple evaluators.
- Atomic FOQueries route through the prepared atomic query path to reuse preparation logic.
- Evaluation is defined on queries (FOQuery and higher-level query types), not on standalone formulas.

## Data Abstraction And Collections
Dates: 2026-02-08
- `ReadableData` provides query capability, atomic patterns, and optional bound estimation.
- Data collections compose multiple data sources with predicate introspection and delegation wrappers.

## Backward Chaining
Dates: 2026-02-04
- Breadth-first UCQ rewriting with piece unifiers is the primary algorithm.
- Designed to interoperate with FOQuery evaluation and prepared query interfaces.

## Documentation, Tests, And CI
Dates: 2026-02-04, 2026-02-05, 2026-02-06, 2026-02-07, 2026-02-08, 2026-02-11
- Documentation is written in Markdown under `docs/` and built with MkDocs.
- Every documentation code block is surrounded by explanatory text and must be covered by a unit test.
- Runnable examples are executed in tests to prevent doc drift.
- CI enforces mypy, unit tests, Ruff lint/format, and coverage; Bandit and pip-audit run for security.
- CI validates CPython 3.10/3.12 and PyPy 3.10 runtime compatibility.

## Process And Release Practices
Dates: 2026-02-03, 2026-02-04, 2026-02-08, 2026-02-09
- Changes follow a plan-first process with design docs and changelog updates.
- Release workflow validates tag/version alignment and uses trusted publishing for PyPI.
- Conventional commits are required for important changes.

## Standard Functions Note
Dates: 2026-02-06
- Standard functions are treated as a built-in computed library under the `stdfct:` namespace.
