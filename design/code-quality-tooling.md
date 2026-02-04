# Design: Code Quality Tooling
Date: 2026-02-04
Status: Accepted

## Context
We need consistent, fast quality checks for linting, formatting, security, dependency auditing, coverage, and code health metrics.

## Decision
Adopt Ruff for linting/formatting/imports, Coverage for test coverage, Bandit and pip-audit for security, and Vulture/Radon for dead code and complexity metrics. Integrate these into CI, with Vulture/Radon as informational checks to reduce false-positive friction.

## Rationale
This toolchain provides broad coverage with minimal overlap and good performance. Ruff consolidates multiple linters, while Bandit/pip-audit add security signals. Vulture/Radon surface maintainability risks without blocking CI on first adoption.

## Alternatives Considered
- Separate Black + isort + flake8 — rejected in favor of Ruff consolidation.
- Blocking CI on Vulture/Radon — rejected to avoid false positives during initial adoption.

## Consequences
- Positive: consistent quality gate and visibility on code health.
- Negative: additional CI time and dependency management.

## Follow-ups
- Tighten Vulture/Radon thresholds once the baseline is stable.
