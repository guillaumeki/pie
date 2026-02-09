# Design: PyPI Release 0.0.16
Date: 2026-02-09
Status: Accepted

## Context
A new commit updated documentation examples for computed JSON loading. The PyPI release workflow triggers only on `v*` tags that match `pyproject.toml`.

## Decision
Bump the project version to 0.0.16 and create a matching `v0.0.16` tag.

## Rationale
The change is a documentation/example adjustment without API impact, so a patch release is appropriate. The workflow requires the tag/version match to publish.

## Alternatives Considered
- Skip the release — rejected because the user requested PyPI deployment.

## Consequences
- Positive: PyPI release triggers automatically with the matching tag.
- Negative: None.

## Follow-ups
- None.
