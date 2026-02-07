# Negation with Functional Terms

Date: 2026-02-07

## Context
Functional terms are rewritten into computed atoms during evaluation. Negation
should remain agnostic of this rewriting and delegate to the inner evaluator.

## Decision
Remove the guard that rejected functional terms under negation. Negation now
delegates evaluation to the inner evaluator, which performs functional-term
rewriting as needed.

## Consequences
- Functional terms can appear under negation without special casing.
- Negation semantics are consistent with atom/conjunction evaluation.
- Additional tests cover simple and nested functional terms under negation.
