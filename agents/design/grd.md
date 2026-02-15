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
- Add stratification strategies for GRD consumers.

## Update: Stratification Strategies (OCP)
Date: 2026-02-15

### Context
GRD needs by-SCC, minimal, and single-evaluation stratifications without coupling
GRD to concrete algorithms or requiring GRD changes when adding new strategies.

### Decision
Introduce a `StratificationStrategy` interface with concrete strategies
(`BySccStratification`, `MinimalStratification`, `SingleEvaluationStratification`).
Expose a single `GRD.stratify(strategy)` entry point and keep GRD focused on graph
construction and queries.

### Rationale
This keeps the GRD API closed for modification (OCP) while allowing extension
through new strategy classes. It also preserves SRP by keeping stratification
logic outside the GRD graph implementation.

## Update: igraph for Stratification Algorithms
Date: 2026-02-15

### Context
The GRD stratification uses generic graph algorithms (SCC, Bellman-Ford) that
should not be implemented inside domain logic. The project also requires PyPy
compatibility for dependencies.

### Decision
Use `igraph` for Bellman-Ford and SCC computations inside stratification
strategies, keeping only orchestration logic in `grd/` and delegating
algorithmic work to an external, PyPy-compatible library.

### Rationale
This avoids mixing generic algorithms with business logic while relying on
optimized, well-tested graph routines with PyPy support.
