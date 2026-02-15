# Design: GRD Top-Level Package
Date: 2026-02-14
Status: Accepted

## Context
PIE needs a Graph of Rule Dependencies (GRD) that is reusable outside rule compilation,
and supports safe negation in bodies plus disjunctive heads (disjunction of conjunctive heads).

## Decision
Introduce a top-level package `prototyping_inference_engine/grd/` implementing GRD with
explicit dependency checkers and rule utilities for extracting positive/negative bodies
and head disjuncts.

## Rationale
Keeping GRD outside `api/` avoids coupling it to a specific API layer while still
providing a stable, reusable component. Disjunctive head support is implemented by
computing dependencies per head disjunct, matching Integraal’s semantics.

## Alternatives Considered
- Place GRD under `api/` — rejected to avoid coupling with the API module layout.
- Encode disjunction at the rule container level — rejected because disjunction is
  already formula-level in PIE.

## Consequences
- Positive: GRD can be reused outside rule compilation without extra adapters.
- Positive: Extensible dependency checkers for alternative semantics.
- Negative: Requires additional validation utilities for safe negation and disjuncts.

## Follow-ups
- Add more dependency checkers if future fragments require it.
