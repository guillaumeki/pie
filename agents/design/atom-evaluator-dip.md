# Design: atom-evaluator-dip
Date: 2026-02-05
Status: Accepted

## Context
`AtomEvaluator` currently instantiates `BacktrackConjunctionEvaluator` directly when function-term rewriting expands an atom into multiple atoms. This couples the atom evaluator to a specific conjunction strategy.

## Decision
Route rewritten conjunction evaluation through the formula evaluator registry instead of instantiating a specific evaluator.

## Rationale
Delegation through the registry keeps the evaluator modular and aligns with DIP/SRP by removing a hard dependency on the backtracking conjunction evaluator.

## Alternatives Considered
- Inject `BacktrackConjunctionEvaluator` via constructor — rejected because it still ties to a concrete class.

## Consequences
- Positive: improved decoupling and easier evaluator substitution.
- Negative: depends on registry configuration for conjunctions.

## Follow-ups
- None.
