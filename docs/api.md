# API

## Public Interfaces
- Terms, atoms, queries, and fact bases under `prototyping_inference_engine.api`.
- Knowledge bases and rule bases under `prototyping_inference_engine.api.kb`.
- Query evaluators under `prototyping_inference_engine.query_evaluation`.
- Parsers under `prototyping_inference_engine.io.parsers`.
- IRI utilities under `prototyping_inference_engine.api.iri`.
- IO helpers under `prototyping_inference_engine.io`.
- Session API under `prototyping_inference_engine.session`.

## Key Classes
- `DlgpeParser`: parse knowledge bases and queries.
- `MutableInMemoryFactBase`: in-memory fact store for evaluation.
- `GenericFOQueryEvaluator`: evaluator dispatching by formula type.
- `ReasoningSession`: high-level evaluation workflow.
- `IRIRef` / `IRIManager`: parse and resolve IRIs with base/prefix state.
- `DlgpeWriter`: write DLGP (DLGPE version) documents from parse results.
- `IntegraalStandardFunctionSource`: computed predicates for the standard function library.
- `RuleBase` / `KnowledgeBase`: rule and knowledge containers.
- `Rule`: formula-based rules; fragment validators live under `api.ontology.rule.validators`.
- `PreparedQuery` / `PreparedFOQuery`: prepared query interfaces.
- `FOQueryFactory`: central query construction utilities.
- `FOConjunctionFactBaseWrapper`: expose a fact base as a conjunction formula.
- `DatalogDelegable`: delegation hooks for rule and query evaluation.
- `DelAtomWrapper`: atom-filtering wrapper for delegable evaluation.
- `IdentityVariable` / `IdentityConstant` / `IdentityLiteral` / `IdentityPredicate`: identity-based term and predicate types with matching factories.

## API Notes
- Docstrings are the authoritative source for method-level behavior and edge cases.
- The module layout mirrors the functional areas described in Architecture.
- `PreparedQuery.estimate_bound(...)` returns a lightweight upper bound when available; it must avoid expensive evaluation.
