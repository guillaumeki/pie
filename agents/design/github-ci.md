# Design: GitHub CI
Date: 2026-02-04
Status: Accepted

## Context
We want CI to run automatically on every push and pull request to prevent regressions. The project already uses mypy and unittest locally.

## Decision
Add a GitHub Actions workflow that runs mypy and the full unit test suite on Python 3.10 and 3.12 for both push and pull_request events.

## Rationale
GitHub Actions is native to GitHub and requires no extra infrastructure. Testing on two supported Python versions balances coverage and runtime.

## Alternatives Considered
- Single Python version only — rejected to keep compatibility confidence.
- External CI provider — rejected to avoid extra setup and credentials.

## Consequences
- Positive: automated regression detection on every push/PR.
- Negative: slightly longer CI time due to matrix runs.

## Follow-ups
- None.
