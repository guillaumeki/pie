# Usage

## Installation
```bash
pip install -e .
```

## Parsing and Querying (DLGPE)
```python
from prototyping_inference_engine.io import DlgpeParser
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
from prototyping_inference_engine.io import DlgpeParser

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

## Working with IRIs
```python
from prototyping_inference_engine.api.iri import (
    IRIManager,
    StandardComposableNormalizer,
    RFCNormalizationScheme,
)

manager = IRIManager(
    normalizer=StandardComposableNormalizer(RFCNormalizationScheme.STRING),
    iri_base="http://example.org/base/",
)
manager.set_prefix("ex", "http://example.org/ns/")

iri = manager.create_iri("ex:resource")
print(iri.recompose())  # http://example.org/ns/resource
```

Parsing with DLGPE/DLGP2 stores the last `@base` and `@prefix` directives in the
`ParseResult` and `ReasoningSession` so you can reuse them when exporting.
Computed prefix directives (`@computed`) are stored as well.

## Exporting DLGPE
```python
from prototyping_inference_engine.io import DlgpeWriter
from prototyping_inference_engine.io import DlgpeParser

parser = DlgpeParser.instance()
result = parser.parse("""
    @base <http://example.org/base/>.
    @prefix ex: <http://example.org/ns/>.
    <rel>(ex:obj).
""")

writer = DlgpeWriter()
print(writer.write(result))
```

## Computed Predicates (`@computed`)

PIE supports Integraal standard functions via `@computed` prefixes. Declare a
computed prefix and use the functions as predicates where the **last argument**
is the result.

```prolog
@computed ig: <http://example.org/functions#>.

@queries
?(X) :- ig:sum(1, X, 3).
```

Functions that can infer a single missing term (one unbound argument) include:
`sum`, `minus`, `product`, `divide`, and `average`.

Available Integraal standard functions:
`sum`, `min`, `max`, `minus`, `product`, `divide`, `average`, `median`, `isEven`,
`isOdd`, `isGreaterThan`, `isGreaterOrEqualsTo`, `isSmallerThan`,
`isSmallerOrEqualsTo`, `isLexicographicallyGreaterThan`,
`isLexicographicallyGreaterOrEqualsTo`, `isLexicographicallySmallerThan`,
`isLexicographicallySmallerOrEqualsTo`, `isPrime`, `equals`, `concat`,
`toLowerCase`, `toUpperCase`, `replace`, `length`, `weightedAverage`,
`weightedMedian`, `set`, `isSubset`, `isStrictSubset`, `union`, `size`,
`intersection`, `contains`, `isEmpty`, `isBlank`, `isNumeric`, `toString`,
`toStringWithDatatype`, `toInt`, `toFloat`, `toBoolean`, `toSet`, `toTuple`,
`dict`, `mergeDicts`, `dictKeys`, `dictValues`, `get`, `tuple`, `containsKey`,
`containsValue`.

Example with collection functions:

```prolog
@computed ig: <http://example.org/functions#>.

@queries
?(T) :- ig:tuple(a, b, c, T).
?(D) :- ig:dict(ig:tuple(a, b), ig:tuple(b, c), D).
?(K) :- ig:dictKeys(ig:dict(ig:tuple(a, b), ig:tuple(b, c)), K).
?(V) :- ig:get(ig:tuple(a, b, c), 1, V).
?(U) :- ig:union(ig:set(a, b), ig:set(b, c), U).
```

## DLGPE Features (Supported)
- Disjunction in head and body.
- Negation in body.
- Equality in queries.
- Sections: `@facts`, `@rules`, `@queries`, `@constraints`.
- `@base`, `@prefix`, and `@computed` directives with IRI resolution.

## DLGPE Features (Not Supported)
- Arithmetic expressions.
- Comparison operators (`<`, `>`, `<=`, `>=`, `!=`).
- `@import`, `@view` directives.

## DLGP 2.1 (Extended) Example
```prolog
q(X); r(Y) :- p(X,Y).
?(X) :- p(X,Y), q(Y).
```

## CLI
```bash
disjunctive-rewriter [file.dlgp] [-l LIMIT] [-v] [-m]
```
