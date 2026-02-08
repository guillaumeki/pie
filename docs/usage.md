# Usage

## Installation
```bash
pip install -e .
```

## Parsing and Querying (DLGP)
This example parses a DLGP document, builds a fact base, and returns both
substitutions and projected answers.
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
projected = [
    tuple(sub.apply(var) for var in variables)
    for sub in answers
]
projected = sorted(projected, key=lambda row: tuple(str(term) for term in row))

print(answers)
print(projected)
```

## Using the Session API
This example uses the `ReasoningSession` helper and returns query answers.
```python
from prototyping_inference_engine.session.reasoning_session import ReasoningSession
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser

with ReasoningSession.create() as session:
    parser = DlgpeParser.instance()
    result = parser.parse("""
        @facts
        p(a,b).
        p(b,c).

        @queries
        ?(X) :- p(a,X).
    """)

    fb = session.create_fact_base(result["facts"])
    answers = list(session.evaluate_query(result["queries"][0], fb))
    print(answers)
```

## Working with IRIs
This example shows how to resolve a prefixed name into an absolute IRI.
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

iri = manager.create_iri_with_prefix("ex", "resource")
value = iri.recompose()
print(value)  # http://example.org/ns/resource
```

Parsing with DLGP stores the last `@base` and `@prefix` directives in the
`ParseResult` and `ReasoningSession` so you can reuse them when exporting.
Computed prefix directives (`@computed`) are stored as well.

## Exporting DLGP
This example parses a document and exports it back to DLGP with a writer.
```python
from prototyping_inference_engine.io.writers.dlgpe_writer import DlgpeWriter
from prototyping_inference_engine.session.reasoning_session import ReasoningSession

with ReasoningSession.create() as session:
    result = session.parse("""
        @base <http://example.org/base/>.
        @prefix ex: <http://example.org/ns/>.
        <rel>(ex:obj).
    """)

    writer = DlgpeWriter()
    output = writer.write(result)
    print(output)
```

## Computed Predicates (`@computed`)

PIE supports Integraal standard functions via `@computed` prefixes. To load the
standard library, declare `@computed <prefix>: <stdfct>.` and use the functions
as predicates where the **last argument** is the result. Any other computed
library will raise an error.

### Usage Modes
- Predicate form: `ig:sum(t1, ..., tn, Result)` where the **last argument** is
  the computed result.
- Functional term form: `ig:sum(t1, ..., tn)` used as a term. PIE rewrites it
  into an extra computed atom plus a fresh result variable, so it works
  anywhere a term is allowed, including under negation.

### Evaluation Rules
- `sum`, `minus`, `product`, `divide`, and `average` can infer **one missing
  term** (any single unbound argument, including the result).
- All other functions require **all input terms** to be bound; the result can
  be unbound (to compute) or bound (to check).

Example: `ig:sum(1, X, 3)` yields `X = 2`.

```prolog
@computed ig: <stdfct>.

@queries
?(X) :- ig:sum(1, X, 3).
```

Example: functional term usage (expanded to computed atoms internally).

```prolog
@computed ig: <stdfct>.

@facts
p(3).

@queries
?() :- p(ig:sum(1, 2)).
```

Example: functional term under negation.

```prolog
@computed ig: <stdfct>.

@facts
p(4).

@queries
?() :- not p(ig:sum(1, 2)).
```

Functions that can infer a single missing term (one unbound argument) include:
`sum`, `minus`, `product`, `divide`, and `average`.

### Signatures and Behavior
Arithmetic:
- `sum(t1, ..., tn, Result)` (n >= 1)
- `min(t1, ..., tn, Result)` (n >= 1)
- `max(t1, ..., tn, Result)` (n >= 1)
- `minus(t1, ..., tn, Result)` (n >= 1, left fold)
- `product(t1, ..., tn, Result)` (n >= 1)
- `divide(t1, t2, ..., tn, Result)` (n >= 2, left fold)
- `average(t1, ..., tn, Result)` (n >= 1)
- `median(t1, ..., tn, Result)` (n >= 1)
- `weightedAverage(pair1, ..., pairN, Result)` where `pair = ig:tuple(value, weight)`
- `weightedMedian(pair1, ..., pairN, Result)` where `pair = ig:tuple(value, weight)`

Comparisons and predicates (result is boolean literal):
- `isEven(value, Result)`
- `isOdd(value, Result)`
- `isPrime(value, Result)`
- `isGreaterThan(left, right, Result)`
- `isGreaterOrEqualsTo(left, right, Result)`
- `isSmallerThan(left, right, Result)`
- `isSmallerOrEqualsTo(left, right, Result)`
- `isLexicographicallyGreaterThan(left, right, Result)`
- `isLexicographicallyGreaterOrEqualsTo(left, right, Result)`
- `isLexicographicallySmallerThan(left, right, Result)`
- `isLexicographicallySmallerOrEqualsTo(left, right, Result)`
- `equals(t1, t2, ..., Result)` (n >= 2, true if all equal)
- `contains(container, value, Result)` (container can be collection or string)
- `isEmpty(collectionOrString, Result)`
- `isBlank(string, Result)`
- `isNumeric(value, Result)`

Strings and conversions:
- `concat(left, right, Result)` (strings or lists)
- `toLowerCase(string, Result)`
- `toUpperCase(string, Result)`
- `replace(string, target, replacement, Result)`
- `length(stringOrCollectionOrDict, Result)`
- `toString(term, Result)`
- `toStringWithDatatype(term, Result)`
- `toInt(term, Result)`
- `toFloat(term, Result)`
- `toBoolean(term, Result)`

Collections and dictionaries:
- `set(e1, ..., en, Result)` (n >= 0)
- `tuple(e1, ..., en, Result)` (n >= 0)
- `union(c1, ..., cn, Result)` (n >= 1)
- `intersection(c1, ..., cn, Result)` (n >= 1)
- `size(collectionOrDict, Result)`
- `isSubset(set1, set2, Result)`
- `isStrictSubset(set1, set2, Result)`
- `dict(pair1, ..., pairN, Result)` where `pair = ig:tuple(key, value)`
- `mergeDicts(left, right, Result)`
- `dictKeys(dict, Result)`
- `dictValues(dict, Result)`
- `get(container, indexOrKey, Result)` (index for tuples/lists, key for dicts)
- `containsKey(dict, key, Result)`
- `containsValue(dict, value, Result)`
- `toSet(collection, Result)`
- `toTuple(collection, Result)`

Example with collection functions:
The queries below yield:
- `T = (a, b, c)`
- `D = {a: b, b: c}`
- `K = {a, b}`
- `V = b`
- `U = {a, b, c}`

```prolog
@computed ig: <stdfct>.

@queries
?(T) :- ig:tuple(a, b, c, T).
?(D) :- ig:dict(ig:tuple(a, b), ig:tuple(b, c), D).
?(K) :- ig:dictKeys(ig:dict(ig:tuple(a, b), ig:tuple(b, c)), K).
?(V) :- ig:get(ig:tuple(a, b, c), 1, V).
?(U) :- ig:union(ig:set(a, b), ig:set(b, c), U).
```

## Functional Term Semantics
Functional terms are evaluated when they use a prefix declared by `@computed`
or when the function is registered in the session's Python function source.
If neither applies, the functional term is treated as a logical
(uninterpreted) functional term and is not evaluated by computed predicate
sources.

## Knowledge Bases and Rule Bases
`RuleBase` collects rules (including ontologies), while `KnowledgeBase` bundles
facts and rule bases together. Use the `ReasoningSession` helpers to create and
track them alongside fact bases when you need a persistent container for rules
or knowledge.

## Prepared Queries and Fact-Base Wrappers
Prepared queries (`PreparedQuery`, `PreparedFOQuery`) represent validated or
compiled query objects. `FOQueryFactory` centralizes query construction, and
`FOConjunctionFactBaseWrapper` exposes a fact base as a conjunction formula for
formula-level APIs.

## Delegation and Atom Filtering
Data sources can opt into `DatalogDelegable` to delegate rule/query evaluation
to external engines. Use `DelAtomWrapper` and `QueryableDataDelAtomsWrapper`
to filter out specific atoms before delegating evaluation.

## DLGP Features (Supported)
- Disjunction in head and body.
- Negation in body.
- Equality in queries.
- Sections: `@facts`, `@rules`, `@queries`, `@constraints`.
- `@base`, `@prefix`, and `@computed` directives with IRI resolution.

## DLGP Features (Not Supported)
- Arithmetic expressions.
- Comparison operators (`<`, `>`, `<=`, `>=`, `!=`).
- `@import`, `@view` directives.

## DLGP Example (.dlgp)
DLGP files use the `.dlgp` extension. This version uses `|` for disjunction.

```prolog
q(X) | r(Y) :- p(X,Y).
?(X) :- p(X,Y), q(Y).
```

## CLI
```bash
disjunctive-rewriter [file.dlgp] [-l LIMIT] [-v] [-m]
```
