# Design: Mypy Fixes 2026-02-04
Date: 2026-02-04
Status: Accepted

## Context
The codebase needed to pass mypy with explicit Optional defaults, protocol variance correctness, and typed internals. The goal was to fix typing errors without changing runtime behavior.

## Decision
Apply minimal, localized typing fixes: explicit Optional defaults, narrow casts where behavior is already correct, and small refactors to avoid ambiguous typing (e.g., replace reduce with loops).

## Rationale
This approach keeps behavior stable, reduces regression risk, and restores a clean mypy baseline without loosening type checking.

## Alternatives Considered
- Ignore mypy errors — rejected because it blocks type-driven regression detection.
- Relax mypy configuration — rejected to keep type safety as a guardrail.

## Consequences
- Positive: mypy clean; clearer type intent in core modules.
- Negative: more annotations and casts to maintain.

## Follow-ups
- None.
