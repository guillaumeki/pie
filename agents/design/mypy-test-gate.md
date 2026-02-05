# Design: Mypy/Test Gate for Commits
Date: 2026-02-04
Status: Accepted

## Context
We want to prevent pushing changes when mypy or tests are failing.

## Decision
Require successful `mypy prototyping_inference_engine` and the full unittest suite before any commit/push.

## Rationale
This enforces a clean baseline and avoids regressions reaching the repository.

## Alternatives Considered
- Soft guideline only — rejected to prevent accidental pushes.

## Consequences
- Positive: higher confidence in pushed changes.
- Negative: extra local time before commits.

## Follow-ups
- None.
