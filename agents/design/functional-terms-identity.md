# Design: Logical vs Evaluable Functional Terms and Identity Factories
Date: 2026-02-08
Status: Accepted

## Context
PIE now supports computed predicates and functional terms via `@computed`.
It also needs a way to ensure strict identity-based equality for terms and
predicates when required, without mixing identity and value semantics.

## Decision
- Split functional terms into:
  - `LogicalFunctionalTerm` (uninterpreted, pure FO logic).
  - `EvaluableFunctionTerm` (interpreted via computed predicates).
- Treat functional terms as evaluable only when they use a prefix declared by
  `@computed`; otherwise treat them as logical functional terms.
- Add identity-based term and predicate classes with dedicated factories:
  `IdentityVariable`, `IdentityConstant`, `IdentityLiteral`,
  `IdentityPredicate`, and their factories.
- Provide a generic `IdentityWrapper` utility for non-API objects.
- Update parsing to use injected factories so a session can enforce identity
  semantics consistently.

## Rationale
Separating logical and evaluable terms avoids accidental evaluation of
purely logical terms and keeps computed prefixes explicit. Identity factories
allow strict reference semantics without polluting the default value-based
types. Session-level factories prevent mixing identity and value semantics.

## Alternatives Considered
- Add a flag to a single FunctionalTerm class — rejected because it obscures
  semantics and complicates evaluator checks.
- Enforce identity semantics globally — rejected because most workflows rely on
  value equality.

## Consequences
- Positive: explicit semantics for computed vs logical terms and safer identity
  handling.
- Negative: additional term classes and factory wiring.

## Follow-ups
- Document functional term semantics and identity factories in `docs/`.
