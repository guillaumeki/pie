# Design: Datalog Delegation and DelAtom Wrappers
Date: 2026-02-08
Status: Accepted

## Context
Some data sources can delegate rule/query evaluation to external engines, and
computed predicates may need to be selectively removed before evaluation.

## Decision
- Add `DatalogDelegable` protocol in `api/data/` exposing rule and query
  delegation hooks.
- Add `DelAtomWrapper` to filter a configured set of atoms from a query.
- Add `QueryableDataDelAtomsWrapper` to filter evaluation results by removing
  atoms from underlying data sources.

## Rationale
Protocols keep the data abstraction flexible and avoid coupling to a concrete
backend. The wrappers allow reusing existing evaluators while excluding
unsupported computed atoms.

## Alternatives Considered
- Embed delegation hooks in `ReadableData` — rejected because not all data
  sources can or should implement it.
- Remove atoms inside evaluators — rejected to keep evaluator logic generic.

## Consequences
- Positive: external delegation is explicit and optional; computed-atom filtering
  is reusable.
- Negative: extra wrapper layers to understand when debugging evaluation flows.

## Follow-ups
- Document delegation patterns and wrappers in `docs/`.
