# Design: Integraal Standard Functions
Date: 2026-02-06
Status: Accepted

## Context
PIE needs to expose Integraal's standard functions via DLGPE `@computed` prefixes, while keeping the computed logic in a data source rather than encoding functional terms directly. The library must support reversible evaluation for functions where one missing argument can be derived.

## Decision
Implement a dedicated Integraal standard function module and a `ReadableData` source that binds computed predicates by IRI prefix. Add reversible solvers for `sum`, `minus`, `product`, `divide`, and `average`. Extend literal handling with `LiteralFactory.create_from_value` to support collection-valued literals.

## Rationale
Separating function definitions from the computed source keeps responsibilities clear and allows reuse. Mapping predicates by prefix integrates cleanly with DLGPE and avoids coupling to `__func__` predicates. Supporting collection literals is required for functions like `tuple`, `set`, and `dict`.

## Alternatives Considered
- Embed all logic into `PythonFunctionReadable` — rejected to avoid conflating standard library definitions with generic function execution.
- Keep `@computed` unsupported and require manual registration — rejected because DLGPE directives are part of the expected workflow.

## Consequences
- Positive: Computed functions are available in DLGPE with minimal user setup, and reversible evaluation improves query expressiveness.
- Negative: Additional literal handling logic increases the surface area of literal normalization and comparison.

## Follow-ups
- Document computed functions and usage examples in `docs/` and `README.md`.
- Expand test coverage for additional standard functions over time.
