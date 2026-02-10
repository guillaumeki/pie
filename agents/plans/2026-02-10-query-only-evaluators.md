# Plan: Query-Only Evaluators
Date: 2026-02-10
Status: Completed

## Design Choices
- Remove FormulaEvaluator as a public evaluation path; evaluation is defined only on FOQuery/Query evaluators.
- Keep evaluator registries query-oriented (FOQuery and Query registries only).
- Preserve behavior by moving formula-specific logic into FOQuery evaluators or prepared FOQuery implementations.

## SOLID Alignment
- Single Responsibility: evaluators focus on query evaluation only.
- Interface Segregation: consumers use one evaluator interface instead of two overlapping ones.

## Module Hierarchy
- Keep evaluators under `query_evaluation/evaluator/fo_query/` and `query_evaluation/evaluator/query/`.
- Remove or deprecate `query_evaluation/evaluator/registry/` and `query_evaluation/evaluator/atom/` formula paths.

## Files To Modify
- `prototyping_inference_engine/query_evaluation/evaluator/registry/*`
- `prototyping_inference_engine/query_evaluation/evaluator/atom/atom_evaluator.py`
- `prototyping_inference_engine/query_evaluation/evaluator/conjunction/*`
- `prototyping_inference_engine/query_evaluation/evaluator/negation/*`
- `prototyping_inference_engine/query_evaluation/evaluator/fo_query/*`
- Tests under `prototyping_inference_engine/query_evaluation/evaluator/test/`
- `CHANGELOG.md`
- `agents/design/designs-compressed.md`

## Type Checking
- Run `mypy prototyping_inference_engine` and fix any issues.

## Tests To Add
- Update evaluator tests to use FOQuery evaluators only.
- Add regression tests ensuring registry resolution for FOQuery types.

## Steps
1. [x] Inventory FormulaEvaluator usage, registry calls, and formula-specific evaluation entry points.
2. [x] Implement query-only evaluator interfaces and migrate formula evaluator callers.
3. [x] Update tests and documentation to the new API.
4. [x] Run required checks and finalize changes.
