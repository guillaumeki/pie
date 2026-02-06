# Design: DLGPE Nested Functional Terms
Date: 2026-02-06
Status: Accepted

## Context
PIE's DLGPE grammar only allowed functional terms as top-level arguments (non-functional nested arguments were required). DLGPE supports nested functional terms, and documentation examples relied on nesting.

## Decision
Extend the DLGPE grammar to allow functional terms within `term` and within function argument lists, and adjust the transformer to accept the new `term_list` rule.

## Rationale
Nested functional terms are part of the DLGPE syntax and required for the standard functions example to parse and evaluate correctly.

## Alternatives Considered
- Document "no nested functional terms" and force users to bind intermediates — rejected because it diverges from DLGPE.

## Consequences
- Positive: DLGPE parsing matches expected syntax, docs examples are executable.
- Negative: slightly broader grammar surface area.

## Follow-ups
- Keep doc examples covered by tests to avoid regressions.
