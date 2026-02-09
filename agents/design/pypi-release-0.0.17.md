# Design: PyPI Release Fix 0.0.17
Date: 2026-02-09
Status: Accepted

## Context
The release workflow failed to detect the version in pyproject.toml, blocking PyPI publishing.

## Decision
Relax the version parsing regex in `.github/workflows/release.yml` and publish patch release 0.0.17 with a matching tag.

## Rationale
The current regex is too strict. Allowing leading whitespace and single quotes makes the check reliable.

## Alternatives Considered
- Re-tag v0.0.16 — rejected because the workflow should be fixed for future releases.

## Consequences
- Positive: Release pipeline becomes robust and PyPI publishing succeeds.
- Negative: None.

## Follow-ups
- None.
