# Design: README Badges
Date: 2026-02-04
Status: Accepted

## Context
We want quick, low-maintenance visual indicators for basic project metadata.

## Decision
Add static Shields.io badges for license and supported Python version alongside the CI badge.

## Rationale
Static badges require no external services and communicate key info at a glance.

## Alternatives Considered
- Dynamic badges for tools (Ruff/Bandit/etc.) — deferred due to extra setup.

## Consequences
- Positive: clearer project metadata in the README.
- Negative: badge URLs must be updated if metadata changes.

## Follow-ups
- None.
