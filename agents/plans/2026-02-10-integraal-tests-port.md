# Plan: Port Additional Query-Evaluation Tests
Date: 2026-02-10
Status: Completed

## Summary
Port remaining relevant query-evaluation tests from the reference suite into PIE, including
the TermPartition-to-equality rewrites and additional scheduling/computed-term cases.

## Design Choices
- Rewrite TermPartition constraints as explicit equality atoms in the formula.
- Preserve expected results from the reference tests as the oracle.
- Prefer extending existing FOQuery evaluator tests to avoid duplication.

## SOLID Alignment
- Single Responsibility: tests validate FOQuery evaluation behavior only.
- Interface Segregation: no new API surface beyond FOQuery evaluators.
- Open/Closed: add coverage without modifying evaluator internals.

## Module Hierarchy
- Tests live under `prototyping_inference_engine/query_evaluation/evaluator/test/`.

## Files To Modify
- `prototyping_inference_engine/query_evaluation/evaluator/test/test_atomic_fo_query_evaluator.py`
- `prototyping_inference_engine/query_evaluation/evaluator/test/test_backtrack_evaluator.py`
- `prototyping_inference_engine/query_evaluation/evaluator/test/test_prepared_query_scheduler.py`
- `prototyping_inference_engine/query_evaluation/evaluator/test/test_functional_terms.py` (new if needed)
- `CHANGELOG.md` (if coverage is release-worthy)

## Work Items
1. **Atomic evaluator gaps**
   - Add tests for:
     - Predicate absent from collection (no crash, empty results).
     - Predicate added after collection creation (dynamic collection behavior).
     - Computed function result projected as an answer variable.
   - Port TermPartition cases by adding equality atoms.
2. **Backtrack evaluator gaps**
   - Add tests combining computed atoms + explicit equality atoms.
   - Add tests with initial substitutions interacting with computed terms.
   - Port TermPartition cases by adding equality atoms.
3. **Scheduler gaps**
   - Add tests where conjunction includes negation + function terms.
   - Add test showing substitution after first evaluation changes scheduler choice.
4. **Functional term query tests**
   - Add logical-function-term matching tests (nested terms, no constants).
   - Add test that rejects incoherent conjunction with logical functional terms.
5. **Registry dispatch**
   - Add a direct QueryEvaluatorRegistry test for FOQuery + UnionQuery dispatch.

## Type Checking
- Run `mypy prototyping_inference_engine` and fix any issues.

## Tests
- Run full unit suite and coverage after adding tests.
