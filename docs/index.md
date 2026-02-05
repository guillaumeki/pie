# Pie Documentation

Pie (Prototyping Inference Engine) is a Python library for building inference engines with disjunctive rules, first-order queries, and parsers for DLGPE/DLGP.

## Features
- Existential disjunctive rules (Disjunctive Datalog with existentially quantified variables).
- First-order queries with conjunction, disjunction, negation, and quantifiers.
- Backward chaining (query rewriting).
- DLGPE parser with disjunction, negation, equality, sections, and IRI resolution for `@base`/`@prefix`.
- Extended DLGP 2.1 parser with disjunction support.

## Installation
```bash
pip install -e .
```

Requires Python 3.10+ (uses match/case syntax).

## Quick Start
```python
from prototyping_inference_engine.parser.dlgpe import DlgpeParser
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
from prototyping_inference_engine.query_evaluation.evaluator.fo_query_evaluators import GenericFOQueryEvaluator

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

for answer in evaluator.evaluate_and_project(query, fact_base):
    print(answer)  # (a, c), (b, d)
```

## Modules and Status
| Module | Status | Description |
|--------|--------|-------------|
| API | 90% | Core classes: terms, atoms, formulas, queries, fact bases, ontologies |
| Data Abstraction | 80% | ReadableData interface for heterogeneous data sources |
| Query Evaluation | 85% | Evaluating first-order queries against data sources |
| DLGPE Parser | 75% | Extended Datalog+- with negation, sections, and IRI resolution |
| DLGP Parser | 80% | Extended DLGP 2.1 with disjunction support |
| Homomorphism | 70% | Pattern matching with backtracking and indexing |
| Backward Chaining | 90% | UCQ rewriting with disjunctive existential rules |
| Forward Chaining | 0% | Not yet implemented |

## Next Steps
- Read the Usage guide for common workflows and CLI usage.
- Review Architecture for component-level details.
