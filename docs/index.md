# Pie Documentation

Pie (Prototyping Inference Engine) is a Python library for building inference engines with disjunctive rules, first-order queries, and a DLGP (DLGPE version) parser.

## Features
- Existential disjunctive rules (Disjunctive Datalog with existentially quantified variables).
- First-order queries with conjunction, disjunction, negation, and quantifiers.
- Backward chaining (query rewriting).
- DLGP parser (DLGPE version) with disjunction, negation, equality, sections, and IRI resolution for `@base`/`@prefix`/`@computed`.
- Computed predicates via Integraal standard functions.
- Knowledge bases and rule bases for grouping facts and rules.
- Prepared query interfaces and FOQuery factory helpers.
- IRI utilities (parsing, resolution, normalization, and base/prefix management).
- IO helpers (parsers and writers, including DLGP export).

## Installation
```bash
pip install -e .
```

Requires Python 3.10+ (uses match/case syntax).

## Quick Start
Parse a DLGP document, build a fact base, and evaluate the query.
```python
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import GenericFOQueryEvaluator

parser = DlgpeParser.instance()
result = parser.parse("""
    @facts
    p(a,b).
    p(b,c).
    p(c,d).

    @queries
    ?(X,Z) :- p(X,Y), p(Y,Z).
""")

facts = result["facts"]
query = result["queries"][0]

fact_base = MutableInMemoryFactBase(facts)
evaluator = GenericFOQueryEvaluator()

variables = [Variable("X"), Variable("Z")]
answers = list(evaluator.evaluate(query, fact_base))
answers = [
    tuple(sub.apply(var) for var in variables)
    for sub in answers
]
answers = sorted(answers, key=lambda row: tuple(str(term) for term in row))
print(answers)  # (a, c), (b, d)
```

## Modules and Status
| Module | Status | Description |
|--------|--------|-------------|
| API | 90% | Core classes: terms, atoms, formulas, queries, fact bases, ontologies |
| Data Abstraction | 80% | ReadableData interface for heterogeneous data sources |
| Query Evaluation | 85% | Evaluating first-order queries against data sources |
| DLGP Parser (DLGPE) | 75% | Extended Datalog+- with negation, sections, and IRI resolution |
| Homomorphism | 70% | Pattern matching with backtracking and indexing |
| Backward Chaining | 90% | UCQ rewriting with disjunctive existential rules |
| Forward Chaining | 0% | Not yet implemented |

## Next Steps
- Read the Usage guide for common workflows and CLI usage.
- Review Architecture for component-level details.
