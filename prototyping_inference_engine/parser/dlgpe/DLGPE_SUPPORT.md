# DLGPE Support in PIE

This document describes the DLGPE features supported by PIE's parser.

## Reference

DLGPE grammar is based on: https://gitlab.inria.fr/jfbaget/dlgpe

## Supported Features

### Directives

| Directive | Status | Notes |
|-----------|--------|-------|
| `@base` | ✅ Supported | Parsed but IRI resolution not implemented |
| `@prefix` | ✅ Supported | Parsed but IRI resolution not implemented |
| `@top` | ✅ Supported | Parsed, stored in header |
| `@una` | ✅ Supported | Parsed, stored in header |
| `@import` | ❌ Not supported | Raises `DlgpeUnsupportedFeatureError` |
| `@computed` | ❌ Not supported | Raises `DlgpeUnsupportedFeatureError` |
| `@view` | ❌ Not supported | Raises `DlgpeUnsupportedFeatureError` |
| `@patterns` | ❌ Not supported | Raises `DlgpeUnsupportedFeatureError` |

### Sections

| Section | Status | Notes |
|---------|--------|-------|
| `@facts` | ✅ Supported | |
| `@rules` | ✅ Supported | |
| `@constraints` | ✅ Supported | |
| `@queries` | ✅ Supported | |

### Statements

| Statement Type | Status | Notes |
|----------------|--------|-------|
| Facts | ✅ Supported | `p(a, b).` |
| Rules | ✅ Supported | `h(X) :- b(X).` |
| Constraints | ✅ Supported | `! :- p(X), q(X).` |
| Queries | ✅ Supported | `?(X) :- p(X).` |

### Formula Features

| Feature | Status | Notes |
|---------|--------|-------|
| Atoms | ✅ Supported | `p(X, a)` |
| Conjunction | ✅ Supported | `p(X), q(X)` |
| Disjunction in head | ✅ Supported | `p(X) \| q(X) :- r(X).` |
| Disjunction in body | ✅ Supported | `h(X) :- p(X) \| q(X).` |
| Negation | ✅ Supported | `not p(X)` or `not (p(X), q(X))` |
| Equality | ✅ Supported | `X = Y` |
| Labels | ✅ Supported | `[rule1] p(X) :- q(X).` |

### Neck Types

| Neck | Status | Notes |
|------|--------|-------|
| `:-` | ✅ Supported | Standard neck |
| `::-` | ✅ Supported | Ground neck (parsed, semantics TBD) |

### Terms

| Term Type | Status | Notes |
|-----------|--------|-------|
| Named variables | ✅ Supported | `X`, `Var1`, `_x` |
| Anonymous variable | ✅ Supported | `_` |
| Constants | ✅ Supported | `a`, `const1` |
| IRI references | ✅ Supported | `<http://example.org/p>` |
| Prefixed names | ✅ Supported | `ex:predicate` |
| String literals | ✅ Supported | `"hello"`, `'world'` |
| Numeric literals | ✅ Supported | `42`, `3.14`, `1e10` |
| Boolean literals | ✅ Supported | `true`, `false` |
| Typed literals | ✅ Supported | `"42"^^xsd:integer` |

## Not Supported Features

The following features will raise `DlgpeUnsupportedFeatureError` when encountered:

### Terms

| Feature | Reason |
|---------|--------|
| Functional terms | PIE does not support function symbols: `f(X, Y)` |
| Arithmetic expressions | Not implemented: `X + 1`, `X * Y`, `X - 1`, `X / 2`, `X ** 2` |

### Atoms

| Feature | Reason |
|---------|--------|
| Comparison operators | Not implemented: `<`, `>`, `<=`, `>=`, `!=` |
| Pattern predicates | Macro system not implemented: `$pattern(X)` |
| Repeated atoms | Transitive closure not implemented: `p+(X, Y)`, `p*(X, Y)` |

### Other

| Feature | Reason |
|---------|--------|
| Subqueries | Not implemented: `Result(X) := p(X, Y)` |
| JSON metadata | Not implemented: `{"name": "rule1"} p(X) :- q(X).` |
| `@import` directive | Module system not implemented |
| `@computed` directive | Computed predicates not implemented |
| `@view` directive | Views not implemented |
| `@patterns` directive | Pattern system not implemented |

## Usage Example

```python
from prototyping_inference_engine.parser.dlgpe import DlgpeParser, DlgpeUnsupportedFeatureError

parser = DlgpeParser.instance()

# Parse a file
try:
    result = parser.parse_file("knowledge.dlgpe")
    facts = result["facts"]
    rules = result["rules"]
    queries = result["queries"]
    constraints = result["constraints"]
except DlgpeUnsupportedFeatureError as e:
    print(f"Unsupported feature: {e}")

# Parse text directly
result = parser.parse("""
    @prefix ex: <http://example.org/>.

    @facts
    ex:person(ex:alice).
    ex:person(ex:bob).
    ex:knows(ex:alice, ex:bob).

    @rules
    [r1] ex:friend(X, Y) :- ex:knows(X, Y), ex:knows(Y, X).

    @queries
    ?(X) :- ex:friend(ex:alice, X).
""")

# Parse specific elements
for atom in parser.parse_atoms("p(a). q(b)."):
    print(atom)

for rule in parser.parse_rules("h(X) :- b(X). g(X) | f(X) :- p(X)."):
    print(rule)
```

## Differences from DLGP 2.1

| Feature | DLGP 2.1 | DLGPE |
|---------|----------|-------|
| Body disjunction | ❌ | ✅ |
| Negation | ❌ | ✅ |
| Ground neck `::- ` | ❌ | ✅ |
| Extended directives | ❌ | ✅ (partial) |
| JSON metadata | ❌ | ❌ (not supported in PIE) |

## Future Work

Features that could be implemented in future versions:

1. **IRI resolution**: Properly resolve `@base` and `@prefix` directives
2. **Comparison operators**: Add support for `<`, `>`, `<=`, `>=`, `!=`
3. **Arithmetic expressions**: Add support for basic arithmetic
4. **Subqueries**: Implement subquery evaluation
5. **`@import` directive**: Support modular knowledge bases
