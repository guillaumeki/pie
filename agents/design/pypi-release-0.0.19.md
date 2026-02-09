# Design: PyPI Release Fix tomllib/tomli 0.0.19
Date: 2026-02-09
Status: Accepted

## Context
The release workflow runs on Python 3.10, where tomllib is unavailable, causing version detection to fail.

## Decision
Use tomllib if available, otherwise fall back to tomli, and release 0.0.19.

## Rationale
This keeps structured parsing while remaining compatible with Python 3.10.

## Alternatives Considered
- Use regex again — rejected as brittle.

## Consequences
- Positive: reliable version detection on Python 3.10.
- Negative: workflow needs tomli installed for Python <3.11.

## Follow-ups
- None.
