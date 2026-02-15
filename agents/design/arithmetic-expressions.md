# Design: DLGPE Arithmetic Expressions
Date: 2026-02-15
Status: Accepted

## Context
DLGPE defines arithmetic expressions in terms, equalities, and comparisons. PIE
already supports computed predicates via `EvaluableFunctionTerm` and the
standard function library, but arithmetic syntax was previously rejected at the
parser layer.

## Decision
Parse DLGPE arithmetic expressions and desugar them into `EvaluableFunctionTerm`
instances backed by the standard function library (`stdfct:`). Implement power
as `stdfct:power` and route evaluation through the existing computed function
pipeline. Ensure standard functions are automatically available when arithmetic
terms appear.

## Rationale
This leverages the existing computed-function evaluation stack, avoids
duplicating numeric evaluation logic, and keeps arithmetic support confined to
parser/transformer layers while maintaining OCP and SRP.

## Alternatives Considered
- Add a dedicated arithmetic AST and evaluator — rejected to avoid duplicating
  computed-function semantics and increasing evaluator complexity.
- Require explicit `@computed` for arithmetic expressions — rejected to align
  with DLGPE expectations that arithmetic is built-in.

## Consequences
- Positive: Arithmetic syntax works in DLGPE without additional directives.
- Positive: Evaluation reuses standard function infrastructure.
- Negative: Standard function coverage must include power (`stdfct:power`).

## Follow-ups
- Consider extending solver support for `stdfct:power` if inverse evaluation is
  needed.
