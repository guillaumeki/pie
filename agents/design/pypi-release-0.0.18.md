# Design: PyPI Release Fix via tomllib 0.0.18
Date: 2026-02-09
Status: Accepted

## Context
Regex-based version parsing in the release workflow is failing in CI. The workflow already uses Python 3.10.

## Decision
Parse `pyproject.toml` with `tomllib` to obtain `project.version`, then publish release 0.0.18 with a matching tag.

## Rationale
TOML parsing is robust and avoids false negatives from regex matching.

## Alternatives Considered
- More regex tweaks — rejected as brittle compared to structured parsing.

## Consequences
- Positive: reliable version detection in release workflow.
- Negative: none.

## Follow-ups
- None.
