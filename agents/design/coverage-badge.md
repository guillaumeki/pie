# Design: coverage-badge
Date: 2026-02-05
Status: Accepted

## Context
We want a coverage badge in the README without relying on external services.

## Decision
Generate a local SVG coverage badge in CI using `tj-actions/coverage-badge-py` and commit it to the repository on pushes to `master`. Keep a placeholder badge tracked so CI can update it reliably.

## Rationale
The action can read the local `.coverage` file produced by the test run and emit an SVG badge, keeping everything self-contained. Tracking a placeholder ensures the first badge update is detected and committed.

## Alternatives Considered
- Codecov or Coveralls — rejected to avoid external services.

## Consequences
- Positive: no external dependencies, badge reflects actual CI coverage.
- Negative: badge is only updated after CI runs on the default branch.

## Follow-ups
- None.
