# API

## Public Interfaces
- Terms, atoms, queries, and fact bases under `prototyping_inference_engine.api`.
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
- `IntegraalStandardFunctionSource`: computed predicates for Integraal standard functions.

## API Notes
- Docstrings are the authoritative source for method-level behavior and edge cases.
- The module layout mirrors the functional areas described in Architecture.
