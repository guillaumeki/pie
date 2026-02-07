# Architecture

## Overview
Pie is organized around core API types (terms, atoms, queries), evaluator stacks for first-order queries, and a DLGPE parser.

## Core API (`prototyping_inference_engine.api`)
- Terms: `Variable`, `Constant` with flyweight caching.
- Atoms: predicates + terms, implement substitution behavior.
- Formulas: `Atom`, `ConjunctionFormula`, `DisjunctionFormula`, `NegationFormula`, `ExistentialFormula`, `UniversalFormula`.
- Queries: `FOQuery` wrapping formulas and answer variables.
- Fact bases: `MutableInMemoryFactBase`, `FrozenInMemoryFactBase`.
- Rules and ontologies with disjunctive head support.

## Data Abstraction (`prototyping_inference_engine.api.data`)
- `ReadableData` interface for queryable data sources.
- `MaterializedData` for fully iterable data sources.
- `BasicQuery`, `AtomicPattern`, and `PositionConstraint` to describe capabilities.
- `DataCollection` for integrating multiple data sources.

## Query Evaluation (`prototyping_inference_engine.query_evaluation`)
Evaluator hierarchy:
```
QueryEvaluator[Q]
└── FOQueryEvaluator
    ├── AtomicFOQueryEvaluator
    ├── ConjunctiveFOQueryEvaluator
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

## IO (`prototyping_inference_engine.io`)
- Parsers under `prototyping_inference_engine.io.parsers`.
- Writers under `prototyping_inference_engine.io.writers`.
- DLGPE parser for extended Datalog+- with disjunction, negation, equality, and sections.

## IRI Utilities (`prototyping_inference_engine.api.iri`)
- `IRIRef` for parsing, resolution, normalization, and relativization.
- `IRIManager` for base/prefix state and best-effort relativization.
- Optional normalizers and preparators for consistent IRI processing.

## Data Flow
Typical flow:
1. Parse facts and queries.
2. Build a fact base.
3. Evaluate with `GenericFOQueryEvaluator` or run rewriting for backward chaining.
