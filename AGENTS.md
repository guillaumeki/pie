# AGENTS.md

## Project Overview
Pie (Prototyping Inference Engine) is a Python library for building inference engines. It supports:
- Existential disjunctive rules (Disjunctive Datalog with existentially quantified variables)
- First-order queries with conjunction, disjunction, negation, and quantifiers
- Backward chaining (query rewriting) - ~90% complete
- Query evaluation against fact bases - ~85% complete
- Data abstraction for heterogeneous sources and multi-source collections
- Forward chaining - not yet implemented
- Extended DLGP 2.1 format parser with disjunction support
- DLGPE parser with negation, equality, and sections support (IRI resolution not implemented)

Requires Python 3.10+ (uses match/case syntax).

## Commands
### Git Remotes
Push to both remotes each time:
- `bitbucket` (Bitbucket)
- `origin` (GitHub, with Bitbucket as an additional push URL)

### Installation
```bash
pip install -e .
```

### Tests
```bash
# Run all tests
python3 -m unittest discover -s prototyping_inference_engine -v

# Run a single test file
python3 -m unittest prototyping_inference_engine.api.fact_base.test.test_fact_base -v

# Run a specific test class
python3 -m unittest prototyping_inference_engine.backward_chaining.test.test_breadth_first_rewriting.TestBreadthFirstRewriting
```

### CLI
```bash
# Query rewriter tool
disjunctive-rewriter [file.dlgp] [-l LIMIT] [-v] [-m]
```

## Architecture Notes
### Core API (`api/`)
- Terms: `Variable`, `Constant` with flyweight caching
- Atoms: predicate + terms, implements `Substitutable`
- Queries: `FOQuery`, `ConjunctiveQuery`, `UnionQuery[Q]`
- Fact bases: `MutableInMemoryFactBase`, `FrozenInMemoryFactBase`
- Rules & ontology: generic rules with disjunctive head support
- Term factories and storage strategies for predicate/term caching

### Data Abstraction (`api/data/`)
- `ReadableData` interface for queryable data sources
- `BasicQuery` with bound positions and answer variables
- `AtomicPattern` and `PositionConstraint` for declaring data source capabilities
- `DataCollection` for integrating multiple data sources

### Query Evaluation (`query_evaluation/`)
Hierarchical evaluator stack with `GenericFOQueryEvaluator` dispatching by formula type.
`QueryEvaluatorRegistry` provides centralized evaluator dispatch by query type.
Evaluators return `Iterator[Substitution]` via `evaluate()` or projected tuples via
`evaluate_and_project()`.

### Backward Chaining (`backward_chaining/`)
`BreadthFirstRewriting` UCQ rewriting algorithm with piece unifiers and rewriting operators.

### Parser (`parser/`)
- DLGP 2.1 (extended with disjunction) via `Dlgp2Parser.instance()`
- DLGPE with disjunction, negation, equality, sections via `DlgpeParser.instance()`

## Formats
DLGP sample:
```prolog
q(X); r(Y) :- p(X,Y).
?(X) :- p(X,Y), q(Y).
```

DLGPE sample:
```prolog
@facts
person(alice).

@rules
[transitivity] knows(X, Z) :- knows(X, Y), knows(Y, Z).

@queries
?(X) :- knows(alice, X).
```

## Code Style
- Comments must always be in English.
