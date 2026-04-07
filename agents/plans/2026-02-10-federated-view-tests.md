# Plan: Federated/View Semantics Tests
Date: 2026-02-10
Status: partially_completed

## Summary
Introduce test coverage for list-vs-set semantics in federated/view-backed data sources.
This corresponds to the commented view/federation tests in the reference suite and will
be implemented once PIE has comparable view/federation support.

## Audit Update (2026-04-07)

Comparable view/federation support now exists in PIE, so the original dependency
blocker is no longer valid.

Implemented evidence:
- View subsystem and runtime sources exist under
  `prototyping_inference_engine/api/data/views/`.
- Views design is documented in `agents/design/views.md` (dated 2026-02-23).
- Targeted view tests now exist and pass:
  - `prototyping_inference_engine.api.data.views.test.test_validation`
  - `prototyping_inference_engine.api.data.views.test.test_missing_value_policies`
  - `prototyping_inference_engine.api.data.views.test.test_view_builder_sqlite`
- Collection-level duplicate handling is covered in
  `prototyping_inference_engine/api/data/collection/test/test_materialized_collection.py`.

What is still missing relative to this draft:
- The originally envisioned dedicated "list semantics vs set semantics" test slice
  for federated/view-backed sources was not added as a standalone plan-sized unit.
- The current coverage validates view loading, validation, specialization,
  missing-value behavior, SQLite-backed execution, and collection deduplication,
  but not a one-to-one port of the exact reference-suite semantics described here.

Conclusion:
- Keep this plan as partially completed rather than draft.
- If strict parity for duplicate-sensitive federated/view semantics is still
  needed, open a follow-up plan scoped only to that remaining behavior.

## Design Choices
- Model a minimal view/federated data source that can expose duplicates.
- Separate “match” (list semantics) from query evaluation (set semantics).
- Keep tests isolated so they can be skipped until the feature exists.

## SOLID Alignment
- Single Responsibility: tests focus on semantics, not storage internals.
- Open/Closed: test harness should accept new federated backends without change.

## Module Hierarchy
- Place tests under `prototyping_inference_engine/api/data/collection/test/` or a
  dedicated `api/data/views/test/` package if a view subsystem is introduced.

## Files To Add / Modify (future)
- New view/federation data source implementation (TBD).
- Tests mirroring list-vs-set semantics.
- Documentation updates if new APIs are added.

## Dependencies
- Originally required implementation of a view/federated data source in PIE.
- This dependency is now satisfied by the `api/data/views` subsystem and related
  collection/runtime support.

## Type Checking
- Run `mypy prototyping_inference_engine` and fix any issues.

## Tests
- Full test suite + coverage once feature is available.
- As of 2026-04-07, targeted view tests pass; the exact duplicate-semantics
  reference slice remains a follow-up item if still desired.
