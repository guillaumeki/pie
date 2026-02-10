# Design: Prepared Queries, Bounds, And Backtrack Scheduling
Date: 2026-02-10
Status: Accepted

## Context
FOQuery evaluators re-created subqueries during backtracking, and there was no
lightweight bound estimation to guide ordering. We need prepared queries that
cache as much work as possible, expose an inexpensive upper bound on result
counts, and use that bound to drive an optimized backtrack scheduler. The
estimate must be cheap and safe (upper bound only).

## Decision
- Add `estimate_bound(...)` to `PreparedQuery` with a lightweight contract.
- Implement prepared FOQuery types per formula (atomic, conjunction, disjunction,
  negation, existential, universal) and have FOQuery evaluators prepare and
  execute them.
- Add a dynamic scheduler inside prepared conjunction evaluation that selects
  the next subquery by the smallest available bound among evaluable candidates.
- Add optional `ReadableData.estimate_bound(...)` with a default `None` for
  unknown bounds; delegate through collections and wrappers.
- Preserve existing warning behavior for unsafe negation and universal
  quantification.

## Rationale
Prepared queries minimize repeated setup (especially in backtracking), while
lightweight bound estimates allow a deterministic, cost-aware ordering that
reduces intermediate results without expensive planning. The optional bound API
keeps data sources simple when no cheap estimate is available.

## Alternatives Considered
- Always compute exact counts by evaluating queries — rejected because the
  estimate must be lightweight and should not perform full evaluation.
- Keep static (sequential) scheduling — rejected because it ignores bound
  information and does not match the expected optimization behavior.

## Consequences
- Positive: Prepared evaluation is reusable, and the scheduler prioritizes
  smaller subqueries when bounds are available.
- Negative: More classes and logic in the FOQuery evaluator layer.

## Follow-ups
- Extend data sources with cheap bound estimates where possible.
- Add additional scheduler heuristics if needed (beyond bound-only ordering).
