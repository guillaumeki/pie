# Design: CI Mypy Installation
Date: 2026-02-05
Status: Accepted

## Context
The GitHub Actions workflow runs mypy, but the runner does not install mypy.

## Decision
Add `mypy` to `requirements-dev.txt` so CI and local dev share the same tool list.

## Rationale
Using a single dev requirements file keeps tooling consistent across environments.

## Consequences
- Positive: CI always has mypy available.
- Negative: None.

## Follow-ups
- None.
