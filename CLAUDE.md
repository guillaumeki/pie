# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pie (Prototyping Inference Engine) is a Python library for building inference engines. It supports:
- Existential disjunctive rules (Disjunctive Datalog with existentially quantified variables)
- First-order queries with conjunction, disjunction, negation, and quantifiers
- Query evaluation against fact bases - 85% complete
- Backward chaining (query rewriting) - 90% complete
- Forward chaining - not yet implemented
- Extended DLGP 2.1 format parser with disjunction support

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
# Query rewriter tool
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
- `Query` → `AtomicQuery`, `ConjunctiveQuery`, `UnionConjunctiveQueries`
- Queries have answer variables and support substitution

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

### Parser (`parser/dlgp/`)

- `Dlgp2Parser` - singleton parser using Lark
- `Dlgp2Transformer` - transforms parse tree to domain objects
- Grammar in `dlgp2.lark`

### Query Evaluation (`query_evaluation/`)

Hierarchical evaluator architecture:
- `QueryEvaluator[Q]` - abstract base for all query evaluators
- `FOQueryEvaluator` - abstract base for first-order query evaluators
  - `AtomicFOQueryEvaluator` - atomic formulas
  - `ConjunctiveFOQueryEvaluator` - conjunctions (backtracking)
  - `DisjunctiveFOQueryEvaluator` - disjunctions
  - `NegationFOQueryEvaluator` - negation-as-failure
  - `UniversalFOQueryEvaluator` - universal quantification
  - `ExistentialFOQueryEvaluator` - existential quantification
  - `GenericFOQueryEvaluator` - dispatches by formula type
- `FOQueryEvaluatorRegistry` - singleton registry for evaluators

Internal formula evaluators (used by FOQueryEvaluators):
- `FormulaEvaluator[F]` - returns `Iterator[Substitution]`
- `AtomEvaluator`, `BacktrackConjunctionEvaluator`, etc.

### Homomorphism (`api/atom/set/homomorphism/`)

- `NaiveBacktrackHomomorphismAlgorithm` - backtracking-based pattern matching
- Schedulers control atom matching order: `ByVariableBacktrackScheduler`, `DynamicBacktrackScheduler`
- Index structures: `IndexByPredicate`, `IndexByTerm`, `IndexByTermAndPredicate`

## DLGP Format

```prolog
% Disjunctive rule
q(X); r(Y) :- p(X,Y).

% Conjunctive query
?(X) :- p(X,Y), q(Y).

% Disjunctive query
?() :- (g(U), e(U,V)); (r(U), e(U,V)).

% Facts
p(a,b).
```

## Key Patterns

- Use `Dlgp2Parser.instance()` singleton for parsing
- All substitutable objects implement `apply_substitution(self, sub) -> Self`
- `Variable.safe_renaming_substitution(vars)` creates fresh variable renaming
- `atom_operations.specialize(from_atom, to_atom, sub)` for atom specialization
- Use `GenericFOQueryEvaluator()` for query evaluation when formula type is unknown
- `evaluate()` returns `Iterator[Substitution]`, `evaluate_and_project()` returns tuples

## Code Style

- **Comments must always be in English** - All code comments, docstrings, and inline documentation must be written in English, regardless of the language used in conversation.
