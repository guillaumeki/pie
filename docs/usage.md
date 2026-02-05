# Usage

## Installation
```bash
pip install -e .
```

## Parsing and Querying (DLGPE)
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

for sub in evaluator.evaluate(query, fact_base):
    print(sub)

for answer in evaluator.evaluate_and_project(query, fact_base):
    print(answer)
```

## Using the Session API
```python
from prototyping_inference_engine.session.reasoning_session import ReasoningSession
from prototyping_inference_engine.parser.dlgpe import DlgpeParser

with ReasoningSession() as session:
    parser = DlgpeParser.instance()
    result = parser.parse("""
        @facts
        p(a,b).
        p(b,c).

        @queries
        ?(X) :- p(a,X).
    """)

    fb = session.create_fact_base(result["facts"])
    for answer in session.evaluate_query(result["queries"][0], fb):
        print(answer)
```

## DLGPE Features (Supported)
- Disjunction in head and body.
- Negation in body.
- Equality in queries.
- Sections: `@facts`, `@rules`, `@queries`, `@constraints`.
- `@base` and `@prefix` directives with IRI resolution.

## DLGPE Features (Not Supported)
- Functional terms.
- Arithmetic expressions.
- Comparison operators (`<`, `>`, `<=`, `>=`, `!=`).
- `@import`, `@computed`, `@view` directives.

## DLGP 2.1 (Extended) Example
```prolog
q(X); r(Y) :- p(X,Y).
?(X) :- p(X,Y), q(Y).
```

## CLI
```bash
disjunctive-rewriter [file.dlgp] [-l LIMIT] [-v] [-m]
```
