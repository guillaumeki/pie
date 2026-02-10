# Plan: RuleCompilation-Based Atomic Evaluators
Date: 2026-02-09
Status: Draft

## Summary
Add RuleCompilation-based atomic evaluators (Inf and Unfolding) in PIE.

## Design Choices (with justification)
- Depend on the RuleCompilation protocol to avoid coupling evaluators to GRD internals.
- Implement InfAtomicFOQueryEvaluator and UnfoldingAtomicFOQueryEvaluator in evaluator/atom.
- Defer full behavior until the GRD implementation plan is complete.

## Files to Add / Modify
- prototyping_inference_engine/query_evaluation/evaluator/atom/inf_atomic_fo_query_evaluator.py
- prototyping_inference_engine/query_evaluation/evaluator/atom/unfolding_atomic_fo_query_evaluator.py
- prototyping_inference_engine/api/rule_compilation/ (protocol usage)
- Tests under corresponding evaluator test packages

## Alternatives Considered
- Implement evaluators without compilation — rejected because it is incomplete.

## Risks & Mitigations
- Missing GRD dependency — mitigate by gating implementation on the GRD plan.

## Testing
- Evaluator tests once GRD-backed RuleCompilation is available.
