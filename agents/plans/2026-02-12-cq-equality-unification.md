# Plan: CQ Equality Alignment With Unification
Date: 2026-02-12
Status: Done

## Summary
Align ConjunctiveQuery equality handling with FOQuery by compiling equality atoms into term partitions and applying them during piece unifier computation. This ensures CQ unification respects explicit equality constraints.

## Design Choices (with justification)
- Represent equality as the existing `SpecialPredicate.EQUALITY` atom — consistent with FOQuery evaluation and avoids new formula types.
- Compile CQ equality atoms into a `TermPartition` and join with unifier partitions — matches Integraal-style equality handling and removes reliance on `pre_substitution`.
- Exclude equality atoms from matchable atoms in unification — equality is a constraint, not a rule-head atom.

## Files to Add / Modify
- prototyping_inference_engine/api/query/conjunctive_query.py
- prototyping_inference_engine/backward_chaining/unifier/piece_unifier_algorithm.py
- prototyping_inference_engine/backward_chaining/unifier/piece_unifier.py
- prototyping_inference_engine/backward_chaining/test/test_piece_unifier_algorithm.py
- prototyping_inference_engine/backward_chaining/test/test_piece_unifier.py
- prototyping_inference_engine/api/query/test/test_query.py

## Alternatives Considered
- Keep equality only in FOQuery evaluation — rejected because CQ unification would ignore explicit equality constraints.
- Use `pre_substitution` for equality constraints — rejected because it only supports answer variables and is too restrictive.

## Risks & Mitigations
- Risk: unification behavior changes for existing queries without equality atoms.
  - Mitigation: add non-regression tests to confirm unchanged behavior.
- Risk: incorrect partition joins could reject valid unifiers.
  - Mitigation: targeted tests for variable-variable and variable-constant equalities.

## Testing
- mypy prototyping_inference_engine
- python3 -m unittest discover -s prototyping_inference_engine -t . -v
- ruff check .
- ruff format --check .
