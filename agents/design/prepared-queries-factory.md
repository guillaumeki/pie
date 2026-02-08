# Design: Prepared Queries, FOQueryFactory, FactBase Wrapper
Date: 2026-02-08
Status: Accepted

## Context
PIE needed a stable interface for prepared queries (validated or compiled
queries) and a dedicated factory for constructing FO queries. Integraal also
exposes a formula wrapper over a fact base as a conjunction.

## Decision
- Add `PreparedQuery` and `PreparedFOQuery` protocols under `api/query/`.
- Add `FOQueryFactory` under `api/query/factory/`.
- Add `FOConjunctionFactBaseWrapper` under `api/formula/` to expose a fact base
  as a conjunction formula.
- Preserve the legacy import path for FOQueryFactory via a re-export module.

## Rationale
Prepared query protocols allow decoupling evaluation logic from parsing and
validation. A factory centralizes construction and normalization logic. The
fact-base wrapper aligns with the formula APIs without changing existing
fact-base implementations.

## Alternatives Considered
- Keep factory in `api/query/` — rejected to avoid cluttering the query package.
- Represent fact bases as explicit conjunction formulas everywhere — rejected
  due to eager materialization cost.

## Consequences
- Positive: clearer API boundaries for query preparation and construction.
- Negative: extra module indirection for FOQueryFactory imports.

## Follow-ups
- Document prepared queries and the fact-base wrapper in `docs/`.
