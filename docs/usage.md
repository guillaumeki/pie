# Usage

## Installation
```bash
pip install -e .
```

## Parsing and Querying (DLGPE)
This example parses a DLGPE document, builds a fact base, and returns both
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
projected = sorted(
    projected, key=lambda row: tuple(term.identifier for term in row)
)

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

Parsing with DLGPE stores the last `@base` and `@prefix` directives in the
`ParseResult` and `ReasoningSession` so you can reuse them when exporting.
Computed prefix directives (`@computed`) are stored as well.

## Exporting DLGPE
This example parses a document and exports it back to DLGPE with a writer.
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

## Loading Computed Functions (`@computed`)
PIE supports Integraal standard functions via `@computed` prefixes. To load the
standard library, declare `@computed <prefix>: <stdfct>.` and use the functions
as predicates where the **last argument** is the result. Computed functions can
also be loaded from JSON configuration files (schema: `docs/computed-json-schema.json`).

Example: `ig:sum(1, X, 3)` yields `X = 2`.

```prolog
@computed ig: <stdfct>.

@queries
?(X) :- ig:sum(1, X, 3).
```

## Loading Computed Functions from JSON
JSON configurations let you bind a prefix to Python functions. The JSON format
accepts a legacy `functions` block and an extensible `providers` block. The
example below uses the legacy form for brevity and points directly at a module.

Define the Python functions in a module (example file:
`docs/examples/computed/computed_utils.py`):

```python
def increment(value: int) -> int:
    return value + 1
```

```json
{
  "schema_version": 1,
  "default": {
    "functions": {
      "path": ".",
      "module": "computed_utils"
    }
  }
}
```

Functions loaded from JSON are used as functional terms (the result is placed
directly in the term position).

```prolog
@computed ex: <docs/examples/computed/functions.json>.

@facts
p(2).

@queries
?() :- p(ex:increment(1)).
```

## Using Functional Terms
Computed predicates can also be used as functional terms. PIE rewrites them into
extra computed atoms plus a fresh result variable, so they work anywhere a term
is allowed.

```prolog
@computed ig: <stdfct>.

@facts
p(3).

@queries
?() :- p(ig:sum(1, 2)).
```

## Using Computed Terms Under Negation
Computed functional terms work under negation as well.

```prolog
@computed ig: <stdfct>.

@facts
p(4).

@queries
?() :- not p(ig:sum(1, 2)).
```

## Computed Function Reference
All functions below are provided by the Integraal standard library. Each
function is listed with its signature and a brief description. The example
blocks in this section contain one query per function, in the same order as the
lists.

### Arithmetic Functions
- `sum(t1, ..., tn, Result)` (n >= 1): Sum of all numeric inputs.
- `min(t1, ..., tn, Result)` (n >= 1): Minimum numeric value.
- `max(t1, ..., tn, Result)` (n >= 1): Maximum numeric value.
- `minus(t1, ..., tn, Result)` (n >= 1): Left-fold subtraction.
- `product(t1, ..., tn, Result)` (n >= 1): Product of all numeric inputs.
- `divide(t1, t2, ..., tn, Result)` (n >= 2): Left-fold division.
- `average(t1, ..., tn, Result)` (n >= 1): Arithmetic mean.
- `median(t1, ..., tn, Result)` (n >= 1): Median value.
- `weightedAverage(pair1, ..., pairN, Result)`: Weighted average.
- `weightedMedian(pair1, ..., pairN, Result)`: Weighted median.

Arithmetic examples (one query per function, in the same order):

```prolog
@computed ig: <stdfct>.

@queries
?(S) :- ig:sum(1, 2, S).
?(Mi) :- ig:min(3, 1, Mi).
?(Ma) :- ig:max(3, 1, Ma).
?(D) :- ig:minus(10, 3, D).
?(P) :- ig:product(2, 3, P).
?(Q) :- ig:divide(8.0, 2.0, Q).
?(A) :- ig:average(2.0, 4.0, A).
?(Md) :- ig:median(2, 9, 4, Md).
?(WA) :- ig:weightedAverage(ig:tuple(10, 1), ig:tuple(20, 3), WA).
?(WM) :- ig:weightedMedian(ig:tuple(10, 1), ig:tuple(20, 3), WM).
```

### Comparison and Predicate Functions
- `isEven(value, Result)`: True if value is an even integer.
- `isOdd(value, Result)`: True if value is an odd integer.
- `isPrime(value, Result)`: True if value is prime.
- `isGreaterThan(left, right, Result)`: True if left > right.
- `isGreaterOrEqualsTo(left, right, Result)`: True if left >= right.
- `isSmallerThan(left, right, Result)`: True if left < right.
- `isSmallerOrEqualsTo(left, right, Result)`: True if left <= right.
- `isLexicographicallyGreaterThan(left, right, Result)`: True if left > right (lexicographic).
- `isLexicographicallyGreaterOrEqualsTo(left, right, Result)`: True if left >= right (lexicographic).
- `isLexicographicallySmallerThan(left, right, Result)`: True if left < right (lexicographic).
- `isLexicographicallySmallerOrEqualsTo(left, right, Result)`: True if left <= right (lexicographic).
- `equals(t1, t2, ..., Result)` (n >= 2): True if all values are equal.
- `contains(container, value, Result)`: True if value is in collection or substring.
- `isEmpty(value, Result)`: True if value is empty (collection or string).
- `isBlank(value, Result)`: True if string is blank.
- `isNumeric(value, Result)`: True if value is numeric or numeric string.

Comparison examples (one query per function, in the same order):

```prolog
@computed ig: <stdfct>.

@queries
?(E) :- ig:isEven(4, E).
?(O) :- ig:isOdd(3, O).
?(Pr) :- ig:isPrime(7, Pr).
?(Gt) :- ig:isGreaterThan(5, 2, Gt).
?(Ge) :- ig:isGreaterOrEqualsTo(2, 2, Ge).
?(Lt) :- ig:isSmallerThan(1, 3, Lt).
?(Le) :- ig:isSmallerOrEqualsTo(2, 2, Le).
?(Lg) :- ig:isLexicographicallyGreaterThan("b", "a", Lg).
?(Lge) :- ig:isLexicographicallyGreaterOrEqualsTo("a", "a", Lge).
?(Ls) :- ig:isLexicographicallySmallerThan("a", "b", Ls).
?(Lse) :- ig:isLexicographicallySmallerOrEqualsTo("a", "a", Lse).
?(Eq) :- ig:equals(5, 5, 5, Eq).
?(C) :- ig:contains(ig:tuple(a, b), a, C).
?(Em) :- ig:isEmpty(ig:set(), Em).
?(Bl) :- ig:isBlank("   ", Bl).
?(Nu) :- ig:isNumeric("12.5", Nu).
```

### String and Conversion Functions
- `concat(left, right, Result)`: Concatenate strings or lists.
- `toLowerCase(value, Result)`: Lowercase string.
- `toUpperCase(value, Result)`: Uppercase string.
- `replace(value, target, replacement, Result)`: Replace substrings.
- `length(value, Result)`: Length of string or collection.
- `toString(term, Result)`: String representation of term.
- `toStringWithDatatype(term, Result)`: String representation with datatype.
- `toInt(term, Result)`: Convert to integer.
- `toFloat(term, Result)`: Convert to float.
- `toBoolean(term, Result)`: Convert to boolean.

String and conversion examples (one query per function, in the same order):

```prolog
@computed ig: <stdfct>.

@queries
?(C) :- ig:concat("foo", "bar", C).
?(Lo) :- ig:toLowerCase("AbC", Lo).
?(Up) :- ig:toUpperCase("AbC", Up).
?(Re) :- ig:replace("abc", "b", "B", Re).
?(Le) :- ig:length("abcd", Le).
?(Ts) :- ig:toString(1, Ts).
?(Td) :- ig:toStringWithDatatype(1, Td).
?(Ti) :- ig:toInt("12", Ti).
?(Tf) :- ig:toFloat("1.5", Tf).
?(Tb) :- ig:toBoolean("true", Tb).
```

### Collection and Dictionary Functions
- `set(e1, ..., en, Result)` (n >= 0): Build a set.
- `tuple(e1, ..., en, Result)` (n >= 0): Build a tuple literal.
- `union(c1, ..., cn, Result)` (n >= 1): Union of collections.
- `size(value, Result)`: Size of collection or dict.
- `intersection(c1, ..., cn, Result)` (n >= 1): Intersection of collections.
- `isSubset(left, right, Result)`: True if left is subset of right.
- `isStrictSubset(left, right, Result)`: True if left is strict subset of right.
- `dict(pair1, ..., pairN, Result)`: Build a dict from pairs.
- `mergeDicts(left, right, Result)`: Merge two dicts.
- `dictKeys(dict, Result)`: Set of keys.
- `dictValues(dict, Result)`: List of values.
- `get(container, indexOrKey, Result)`: Index lists/tuples or key in dict.
- `containsKey(dict, key, Result)`: True if key exists.
- `containsValue(dict, value, Result)`: True if value exists.
- `toSet(collection, Result)`: Convert collection to set.
- `toTuple(collection, Result)`: Convert collection to tuple literal.

Collection examples (one query per function, in the same order):

```prolog
@computed ig: <stdfct>.

@queries
?(S) :- ig:set(a, b, S).
?(T) :- ig:tuple(a, b, T).
?(U) :- ig:union(ig:set(a, b), ig:set(b, c), U).
?(Sz) :- ig:size(ig:set(a, b), Sz).
?(I) :- ig:intersection(ig:set(a, b), ig:set(b, c), I).
?(Su) :- ig:isSubset(ig:set(a), ig:set(a, b), Su).
?(Ss) :- ig:isStrictSubset(ig:set(a), ig:set(a, b), Ss).
?(D) :- ig:dict(ig:tuple(a, b), ig:tuple(b, c), D).
?(M) :- ig:mergeDicts(ig:dict(ig:tuple(a, b)), ig:dict(ig:tuple(c, d)), M).
?(K) :- ig:dictKeys(ig:dict(ig:tuple(a, b), ig:tuple(b, c)), K).
?(V) :- ig:dictValues(ig:dict(ig:tuple(a, b), ig:tuple(b, c)), V).
?(G) :- ig:get(ig:tuple(a, b, c), 1, G).
?(Ck) :- ig:containsKey(ig:dict(ig:tuple(a, b)), a, Ck).
?(Cv) :- ig:containsValue(ig:dict(ig:tuple(a, b)), b, Cv).
?(Ts) :- ig:toSet(ig:tuple(a, b), Ts).
?(Tt) :- ig:toTuple(ig:tuple(a, b), Tt).
```

## Knowledge Bases and Rule Bases
Use `RuleBase` to store rules and `KnowledgeBase` to bundle rules with facts.

```python
from prototyping_inference_engine.session.reasoning_session import ReasoningSession

with ReasoningSession.create() as session:
    result = session.parse("""
        @facts
        p(a).

        @rules
        q(X) :- p(X).
    """)

    fb = session.create_fact_base(result.facts)
    rb = session.create_rule_base(set(result.rules))
    kb = session.create_knowledge_base(fb, rb)

    fact_count = len(kb.fact_base)
    rule_count = len(kb.rule_base.rules)
    print(fact_count)
    print(rule_count)
```

## Prepared Queries and FOQueryFactory
Use `FOQueryFactory` to construct queries and `PreparedFOQueryDefaults` to build
prepared executors for those queries.

```python
from prototyping_inference_engine.api.query.prepared_fo_query import PreparedFOQueryDefaults
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.session.reasoning_session import ReasoningSession


class SimplePreparedQuery(PreparedFOQueryDefaults):
    def __init__(self, query):
        self.query = query

    def execute(self, assignation: Substitution):
        return [assignation]


with ReasoningSession.create() as session:
    query = session.fo_query().builder().atom("p", "a").build()
    prepared = SimplePreparedQuery(query)
    answers = list(prepared.execute_empty())
    print(answers)
```

## Wrapping a Fact Base as a Formula
Use `FOConjunctionFactBaseWrapper` when you need a formula view of a fact base.

```python
from prototyping_inference_engine.api.formula.fo_conjunction_fact_base_wrapper import (
    FOConjunctionFactBaseWrapper,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser

facts = DlgpeParser.instance().parse_atoms("p(a), q(b).")
fact_base = MutableInMemoryFactBase(facts)
wrapper = FOConjunctionFactBaseWrapper(fact_base)

atom_count = len(wrapper.atoms)
free_count = len(wrapper.free_variables)
print(atom_count)
print(free_count)
```

## Delegation and Atom Filtering
Use `DatalogDelegable` for data sources that can evaluate datalog rules or
queries directly. Use `QueryableDataDelAtomsWrapper` to hide specific atoms
without mutating the underlying data source.

```python
from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.datalog_delegable import DatalogDelegable
from prototyping_inference_engine.api.data.queryable_data_del_atoms_wrapper import (
    QueryableDataDelAtomsWrapper,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase


class DelegableFactBase(MutableInMemoryFactBase, DatalogDelegable):
    def delegate_rules(self, rules):
        return False

    def delegate_query(self, query, count_answers_only=False):
        return iter(self.evaluate(query))


predicate = Predicate("p", 1)
removed = Atom(predicate, Constant("b"))

fact_base = DelegableFactBase(
    [Atom(predicate, Constant("a")), removed]
)
query = BasicQuery(predicate, {}, {0: Variable("X")})

delegated: list[tuple[Constant]] = []
if isinstance(fact_base, DatalogDelegable):
    delegated = list(fact_base.delegate_query(query))

filtered = QueryableDataDelAtomsWrapper(fact_base, [removed])
filtered_results = list(filtered.evaluate(query))

print(delegated)
print(filtered_results)
```

## Using DLGP Syntax
DLGP files use the `.dlgp` extension. This version uses `|` for disjunction and
supports negation in rule bodies.

```prolog
q(X) | r(Y) :- p(X,Y).
?(X) :- p(X,Y), q(Y).
```

## CLI
```bash
disjunctive-rewriter [file.dlgp] [-l LIMIT] [-v] [-m]
```
