# API

## Public Interfaces
- Terms, atoms, queries, and fact bases under `prototyping_inference_engine.api`.
- Query evaluators under `prototyping_inference_engine.query_evaluation`.
- Parsers under `prototyping_inference_engine.parser`.
- Session API under `prototyping_inference_engine.session`.

## Key Classes
- `DlgpeParser` / `Dlgp2Parser`: parse knowledge bases and queries.
- `MutableInMemoryFactBase`: in-memory fact store for evaluation.
- `GenericFOQueryEvaluator`: evaluator dispatching by formula type.
- `ReasoningSession`: high-level evaluation workflow.

## API Notes
- Docstrings are the authoritative source for method-level behavior and edge cases.
- The module layout mirrors the functional areas described in Architecture.
