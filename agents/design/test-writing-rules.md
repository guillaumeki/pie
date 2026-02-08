# Design: Test Writing Rules (Determinism + No str/repr)
Date: 2026-02-08
Status: Accepted

## Context
Tests that assert on `__str__`/`__repr__` output are brittle and frequently fail
when formatting changes even though behavior is unchanged. Tests that rely on
unordered iteration (sets/dicts) are also flaky.

## Decision
- Forbid `str(...)` and `repr(...)` usage in tests.
- Require deterministic assertions in tests (sort or normalize unordered data).
- Refactor existing tests to assert on stable attributes (identifiers, values,
  datatypes, explicit fields).

## Rationale
This keeps tests focused on semantic behavior and prevents formatting changes
from causing unrelated failures.

## Alternatives Considered
- Keep string tests and update expectations with formatting changes — rejected
  because it encourages brittle tests and repeated churn.

## Consequences
- Positive: fewer flaky failures and clearer semantic coverage.
- Negative: less direct coverage of `__str__`/`__repr__` formatting.

## Follow-ups
- Ensure future tests follow the deterministic/semantic pattern.
