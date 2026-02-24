# Architecture

## Overview
Pie is organized around core API types (terms, atoms, queries), evaluator stacks for first-order queries, and a DLGP (DLGPE version) parser.

## Core API (`prototyping_inference_engine.api`)

- Terms: `Variable`, `Constant` with flyweight caching.

- Atoms: predicates + terms, implement substitution behavior.

- Formulas: `Atom`, `ConjunctionFormula`, `DisjunctionFormula`, `NegationFormula`, `ExistentialFormula`, `UniversalFormula`.

- Queries: `FOQuery` wrapping formulas and answer variables.

- Fact bases: `MutableInMemoryFactBase`, `FrozenInMemoryFactBase`.

- Rule bases and ontologies with disjunctive head support.

- Knowledge bases for grouping facts with rule bases.

- Functional terms distinguish logical terms from evaluable terms tied to `@computed`.

## Data Abstraction (`prototyping_inference_engine.api.data`)

- `ReadableData` interface for queryable data sources.

- `MaterializedData` for fully iterable data sources.

- `BasicQuery`, `AtomicPattern`, and `PositionConstraint` to describe capabilities.

- `DataCollection` for integrating multiple data sources.

- View runtime sources (`api.data.views`) loaded from `.vd` declarations.

- `DatalogDelegable` for delegating rules and queries to external engines.

- Delegation wrappers (`DelAtomWrapper`, `QueryableDataDelAtomsWrapper`) for atom filtering.

## Query Evaluation (`prototyping_inference_engine.query_evaluation`)
Evaluator hierarchy:
```
QueryEvaluator[Q]
└── FOQueryEvaluator
    ├── AtomicFOQueryEvaluator
    ├── BacktrackingConjunctiveFOQueryEvaluator
    ├── DisjunctiveFOQueryEvaluator
    ├── NegationFOQueryEvaluator
    ├── UniversalFOQueryEvaluator
    ├── ExistentialFOQueryEvaluator
    └── GenericFOQueryEvaluator
```
Each evaluator can return substitutions or projected tuples.

## Backward Chaining (`prototyping_inference_engine.backward_chaining`)

- `BreadthFirstRewriting` UCQ rewriting algorithm.

- Piece unifiers and rewriting operators.

## Forward Chaining (`prototyping_inference_engine.forward_chaining`)

- Chase engine built from interchangeable strategies:
  - Schedulers: naive, predicate-based, GRD-based.
  - Trigger computation: naive, restricted, semi-naive, two-steps.
  - Trigger checkers: oblivious, semi-oblivious, restricted, equivalent, multi-checker.
  - Renamers: fresh, body skolem, frontier skolem, frontier-by-piece skolem.
  - Rule appliers: breadth-first, parallel, multi-thread, source-delegated.
  - Treatments: rule split, add created facts, compute core/local core, predicate-filter end, debug hooks.
  - Halting conditions: step limit, atom limit, timeout, external interruption, rules-to-apply, created-facts-at-previous-step.
- Stratified execution via GRD strata (`chase.metachase.stratified`).
- Lineage tracking pluggable (none, simple, federated).

## GRD (`prototyping_inference_engine.grd`)

- Graph of Rule Dependencies (GRD) with disjunctive heads and safe negation support.

- Dependency checkers to validate positive/negative edges.

- Stratification strategies (`BySccStratification`, `MinimalStratification`, `SingleEvaluationStratification`, `MinimalEvaluationStratification`) live under `prototyping_inference_engine.grd.stratification`.

- Stratification algorithms rely on igraph for SCC and shortest-path computations.

## IO (`prototyping_inference_engine.io`)

- Parsers under `prototyping_inference_engine.io.parsers`.

- Writers under `prototyping_inference_engine.io.writers`.

- DLGP parser (DLGPE version) for extended Datalog+- with disjunction, negation, equality, and sections.

- Import registry supports format-aware `@import`, including `.vd` view declarations.

## IRI Utilities (`prototyping_inference_engine.api.iri`)

- `IRIRef` for parsing, resolution, normalization, and relativization.

- `IRIManager` for base/prefix state and best-effort relativization.

- Optional normalizers and preparators for consistent IRI processing.

## Data Flow
Typical flow:
1. Parse facts and queries.
2. Build a fact base.
3. Evaluate with `GenericFOQueryEvaluator` or run rewriting for backward chaining.
