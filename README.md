# Pie : Prototyping Inference Engine

Pie is a Python library for building [inference engines](https://en.wikipedia.org/wiki/Inference_engine). It allows rapid prototyping of software that requires logical reasoning capabilities.

The library supports:
- **Existential disjunctive rules** ([Disjunctive Datalog](https://en.wikipedia.org/wiki/Disjunctive_Datalog) with existentially quantified variables)
- **First-order queries** with conjunction, disjunction, negation, and quantifiers
- **[Backward chaining](https://en.wikipedia.org/wiki/Backward_chaining)** (query rewriting)
- **Extended DLGP 2.1 format** parser with disjunction support

## Installation

```bash
pip install -e .
```

Requires Python 3.10+ (uses match/case syntax).

## Progression

| Module | Status | Description |
|--------|--------|-------------|
| **API** | 90% | Core classes: terms, atoms, formulas, queries, fact bases, ontologies |
| **Data Abstraction** | 80% | ReadableData interface for heterogeneous data sources |
| **Query Evaluation** | 85% | Evaluating first-order queries against data sources |
| **DLGP Parser** | 80% | Extended DLGP 2.1 with disjunction support |
| **DLGPE Parser** | 70% | Extended Datalog+- with negation, sections (IRI resolution not implemented) |
| **Homomorphism** | 70% | Pattern matching with backtracking and indexing |
| **Backward Chaining** | 90% | UCQ rewriting with disjunctive existential rules |
| **Forward Chaining** | 0% | Not yet implemented |

## Quick Start

### Parsing and Querying

```python
from prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
from prototyping_inference_engine.query_evaluation.evaluator.fo_query_evaluators import GenericFOQueryEvaluator

# Parse facts and query
parser = Dlgp2Parser.instance()
facts = list(parser.parse_atoms("p(a,b). p(b,c). p(c,d)."))
query = parser.parse_query("?(X,Z) :- p(X,Y), p(Y,Z).")

# Create fact base and evaluate
fact_base = MutableInMemoryFactBase(facts)
evaluator = GenericFOQueryEvaluator()

# Get results as substitutions
for sub in evaluator.evaluate(query, fact_base):
    print(sub)  # {X -> a, Y -> b, Z -> c}, etc.

# Or get projected tuples
for answer in evaluator.evaluate_and_project(query, fact_base):
    print(answer)  # (a, c), (b, d)
```

### Using the Session API

```python
from prototyping_inference_engine.session.reasoning_session import ReasoningSession

with ReasoningSession() as session:
    # Parse DLGP content
    facts, rules, queries = session.parse_dlgp("""
        p(a,b). p(b,c).
        ?(X) :- p(a,X).
    """)

    # Create fact base and evaluate
    fb = session.create_fact_base(facts)
    for answer in session.evaluate_query(queries[0], fb):
        print(answer)  # (b,)
```

## Architecture

### Core API (`api/`)

- **Terms**: `Variable`, `Constant` with flyweight caching
- **Atoms**: Predicate + terms, implements `Substitutable`
- **Formulas**: `Atom`, `ConjunctionFormula`, `DisjunctionFormula`, `NegationFormula`, `ExistentialFormula`, `UniversalFormula`
- **Queries**: `FOQuery` wrapping formulas with answer variables
- **Fact Bases**: `MutableInMemoryFactBase`, `FrozenInMemoryFactBase`
- **Rules & Ontology**: Generic rules with disjunctive head support

### Data Abstraction (`api/data/`)

Abstraction layer for data sources (fact bases, SQL databases, REST APIs, etc.):

- **`ReadableData`**: Abstract interface for queryable data sources
- **`MaterializedData`**: Extension for fully iterable data sources
- **`BasicQuery`**: Simple query with predicate, bound positions, and answer variables
- **`AtomicPattern`**: Describes constraints for querying predicates (mandatory positions, type constraints)
- **`PositionConstraint`**: Validators for term types at positions (`GROUND`, `CONSTANT`, `VARIABLE`, etc.)

Data sources declare their capabilities via `AtomicPattern` and implement `evaluate(BasicQuery)` returning tuples of terms. Evaluators handle variable mapping and post-processing.

### Query Evaluation (`query_evaluation/`)

Hierarchical evaluator architecture:

```
QueryEvaluator[Q]
└── FOQueryEvaluator
    ├── AtomicFOQueryEvaluator
    ├── ConjunctiveFOQueryEvaluator
    ├── DisjunctiveFOQueryEvaluator
    ├── NegationFOQueryEvaluator
    ├── UniversalFOQueryEvaluator
    ├── ExistentialFOQueryEvaluator
    └── GenericFOQueryEvaluator (dispatches by formula type)
```

Each evaluator provides:
- `evaluate(query, data, substitution)` → `Iterator[Substitution]`
- `evaluate_and_project(query, data, substitution)` → `Iterator[Tuple[Term, ...]]`

Evaluators work with any `ReadableData` source, not just in-memory fact bases.

### Backward Chaining (`backward_chaining/`)

- `BreadthFirstRewriting` - UCQ rewriting algorithm
- `PieceUnifierAlgorithm` - computes most general piece unifiers
- `RewritingOperator` - applies rules to queries

### Parser (`parser/`)

#### DLGP 2.1 (`parser/dlgp/`)

Extended DLGP 2.1 format with disjunction:

```prolog
% Facts
p(a,b).

% Disjunctive rule
q(X); r(Y) :- p(X,Y).

% Conjunctive query
?(X) :- p(X,Y), q(Y).

% Disjunctive query
?() :- (p(X), q(X)); (r(X), s(X)).
```

#### DLGPE (`parser/dlgpe/`)

Extended Datalog+- format with additional features beyond DLGP 2.1.

**Supported features:**

| Feature | Syntax | Example |
|---------|--------|---------|
| Disjunction in head | `\|` | `p(X) \| q(X) :- r(X).` |
| Disjunction in body | `\|` | `h(X) :- p(X) \| q(X).` |
| Negation | `not` | `h(X) :- p(X), not q(X).` |
| Equality | `=` | `?(X,Y) :- p(X,Y), X = Y.` |
| Sections | `@facts`, `@rules`, `@queries`, `@constraints` | Organize knowledge base |
| Labels | `[name]` | `[rule1] h(X) :- b(X).` |

**Usage:**

```python
from prototyping_inference_engine.parser.dlgpe import DlgpeParser, DlgpeUnsupportedFeatureError

parser = DlgpeParser.instance()

# Parse DLGPE content
result = parser.parse("""
    @facts
    person(alice).
    person(bob).
    knows(alice, bob).

    @rules
    [transitivity] knows(X, Z) :- knows(X, Y), knows(Y, Z).
    stranger(X, Y) :- person(X), person(Y), not knows(X, Y).

    @queries
    ?(X) :- knows(alice, X).
""")

facts = result["facts"]
rules = result["rules"]
queries = result["queries"]

# Parse specific elements
atoms = list(parser.parse_atoms("p(a). q(b)."))
rules = list(parser.parse_rules("h(X) :- b(X). p(X) | q(X) :- r(X)."))
```

**Parsed but not used:** `@prefix`, `@base` (IRI resolution not implemented), typed literals.

**Not supported:** functional terms, arithmetic expressions, comparison operators (`<`, `>`, etc.), `@import`, `@computed`, `@view` directives.

## CLI Tools

```bash
# Query rewriter
disjunctive-rewriter [file.dlgp] [-l LIMIT] [-v] [-m]
```

## Running Tests

```bash
# All tests
python3 -m unittest discover -s prototyping_inference_engine -v

# Specific module
python3 -m unittest discover -s prototyping_inference_engine/query_evaluation -v
```

## License

[GNU General Public License v3 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.html)
