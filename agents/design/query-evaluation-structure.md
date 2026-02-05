# Design: Query Evaluation Structure
Date: 2026-02-04
Status: Accepted

## Context
The query evaluation package accumulated many classes under a single
`query_evaluation.evaluator` module. This made navigation and ownership
unclear because formula evaluators, FOQuery evaluators, and generic query
evaluators had distinct responsibilities.

## Decision
- Group evaluators by formula type: atom, conjunction, disjunction, negation,
  and quantifiers.
- Separate FOQuery evaluators and their registry from formula evaluators.
- Separate generic query evaluators (Union/Conjunctive) and registry.
- Isolate functional-term rewriting utilities under a dedicated module.
- Centralize evaluator errors in `evaluator/errors.py`.

## Rationale
This structure aligns modules with conceptual categories, reduces cognitive
load, and improves discoverability without altering evaluation behavior.

## Alternatives Considered
- Keep all evaluators flat with naming conventions only — rejected because
  it does not solve discoverability or ownership boundaries.
- Split by “query vs formula” only — rejected because logical connective
  evaluators still form a large, mixed module set.

## Consequences
- Positive: clearer imports, easier navigation, and cleaner separation
  between registries and evaluators.
- Negative: requires updating imports and may break external callers that
  imported from the old paths.

## Follow-ups
- Consider documenting the new module layout in `README.md`.
