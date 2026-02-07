# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pie (Prototyping Inference Engine) is a Python library for building inference engines. It supports:
- Existential disjunctive rules (Disjunctive Datalog with existentially quantified variables)
- First-order queries with conjunction, disjunction, negation, and quantifiers
- Query evaluation against fact bases - 85% complete
- Backward chaining (query rewriting) - 90% complete
- Forward chaining - not yet implemented
- DLGPE format parser with negation, equality, and sections support

## Commands

### Running Tests
```bash
# Run all tests (requires Python 3.10+ for match/case syntax)
python3 -m unittest discover -s prototyping_inference_engine -v

# Run a single test file
python3 -m unittest prototyping_inference_engine.api.fact_base.test.test_fact_base -v

# Run a specific test class
python3 -m unittest prototyping_inference_engine.backward_chaining.test.test_breadth_first_rewriting.TestBreadthFirstRewriting
```

### CLI Application
```bash
# Query rewriter tool (DLGPE syntax; .dlgp supported)
disjunctive-rewriter [file.dlgp] [-l LIMIT] [-v] [-m]
```

### Installation
```bash
pip install -e .
```

## Architecture

### Core API (`api/`)

**Terms & Atoms:**
- `Term` → abstract base, implements `Substitutable`
  - `Variable` - uses flyweight pattern with global cache
  - `Constant` - cached via `@cache` decorator
- `Atom` - predicate + terms tuple, implements `Substitutable`
- `AtomSet` → `FrozenAtomSet`, `MutableAtomSet`

**Substitution System:**
- `Substitutable` - interface for objects that can have substitutions applied
- `Substitution` - dict[Variable, Term] with composition and application
- All core types (Term, Atom, AtomSet, Query) implement `Substitutable`

**Queries:**
- `Query` → `ConjunctiveQuery`, `UnionQuery[Q]` (generic union of queries)
- `UnionConjunctiveQueries` extends `UnionQuery[ConjunctiveQuery]` (for backward chaining)
- `FOQuery` - first-order queries with any formula type (for evaluation)
- Queries have answer variables and support substitution

**Term Factories (`api/atom/term/factory/`):**
- `VariableFactory`, `ConstantFactory`, `PredicateFactory` - create/cache terms
- Pluggable storage strategies for memory management

**Storage Strategies (`api/atom/term/storage/`):**
- `TermStorageStrategy` - protocol for cache interface
- `DictStorage` - simple dictionary cache
- `WeakRefStorage` - weak reference cache with automatic GC cleanup
- `GlobalCacheStorage` - adapter for existing global caches

**Rules & Ontology:**
- `Rule[BodyType, HeadType]` - generic rule with disjunctive head support
- `Ontology` - collection of rules and negative constraints

**FactBase:**
- `FactBase` → `InMemoryFactBase` → `FrozenInMemoryFactBase`, `MutableInMemoryFactBase`
- Uses metaclass `MetaFactBase` for operation tracking
- Supports `@fact_base_operation` decorator for marking supported operations

### Backward Chaining (`backward_chaining/`)

- `BreadthFirstRewriting` - main UCQ rewriting algorithm
- `PieceUnifier` / `DisjunctivePieceUnifier` - unification structures
- `PieceUnifierAlgorithm` - computes most general piece unifiers
- `RewritingOperator` - applies rules to queries

### Parser (`parser/`)

**DLGPE (`parser/dlgpe/`):**
- `DlgpeParser` - extended Datalog+- parser
- Supports: disjunction, negation (`not`), equality (`=`), sections (`@facts`, `@rules`, etc.)
- `DlgpeUnsupportedFeatureError` for unsupported features

### Query Evaluation (`query_evaluation/`)

Hierarchical evaluator architecture:
- `QueryEvaluator[Q]` - abstract base for all query evaluators
- `QueryEvaluatorRegistry` - centralized dispatch for query evaluation by type
- `FOQueryEvaluator` - abstract base for first-order query evaluators
  - `AtomicFOQueryEvaluator` - atomic formulas
  - `ConjunctiveFOQueryEvaluator` - conjunctions (backtracking)
  - `DisjunctiveFOQueryEvaluator` - disjunctions
  - `NegationFOQueryEvaluator` - negation-as-failure
  - `UniversalFOQueryEvaluator` - universal quantification
  - `ExistentialFOQueryEvaluator` - existential quantification
  - `GenericFOQueryEvaluator` - dispatches by formula type
- `UnionQueryEvaluator` - evaluates `UnionQuery[Q]` by evaluating each sub-query
- `ConjunctiveQueryEvaluator` - converts CQ to FOQuery and delegates

Internal formula evaluators (used by FOQueryEvaluators):
- `FormulaEvaluator[F]` - returns `Iterator[Substitution]`
- `AtomEvaluator`, `BacktrackConjunctionEvaluator` (supports equality atoms), etc.

### Homomorphism (`api/atom/set/homomorphism/`)

- `NaiveBacktrackHomomorphismAlgorithm` - backtracking-based pattern matching
- Schedulers control atom matching order: `ByVariableBacktrackScheduler`, `DynamicBacktrackScheduler`
- Index structures: `IndexByPredicate`, `IndexByTerm`, `IndexByTermAndPredicate`

## DLGP-Compatible (.dlgp) Format

DLGP files in this project are parsed with the DLGPE parser. Keep the `.dlgp`
extension, but use `|` for disjunction so the syntax is DLGPE-compatible.

```prolog
% Disjunctive rule
q(X) | r(Y) :- p(X,Y).

% Conjunctive query
?(X) :- p(X,Y), q(Y).

% Disjunctive query
?() :- (g(U), e(U,V)) | (r(U), e(U,V)).

% Facts
p(a,b).
```

## DLGPE Format

```prolog
@facts
person(alice).
knows(alice, bob).

@rules
[transitivity] knows(X, Z) :- knows(X, Y), knows(Y, Z).
stranger(X, Y) :- person(X), person(Y), not knows(X, Y).

@queries
?(X, Y) :- knows(X, Y), X = Y.
```

## Key Patterns

- Use `DlgpeParser.instance()` singleton for DLGPE parsing
- All substitutable objects implement `apply_substitution(self, sub) -> Self`
- `Variable.safe_renaming_substitution(vars)` creates fresh variable renaming
- `atom_operations.specialize(from_atom, to_atom, sub)` for atom specialization
- Use `GenericFOQueryEvaluator()` for query evaluation when formula type is unknown
- Use `QueryEvaluatorRegistry.instance()` for centralized query evaluation dispatch
- `evaluate()` returns `Iterator[Substitution]`, `evaluate_and_project()` returns tuples
- Convert CQ/UCQ to FOQuery via `cq.to_fo_query()` for evaluation
- `Substitution.normalize()` resolves transitive variable chains
- `UnionQuery[Q]` is the generic union type; `UnionConjunctiveQueries` for backward chaining

## Code Style

- **Comments must always be in English** - All code comments, docstrings, and inline documentation must be written in English, regardless of the language used in conversation.
