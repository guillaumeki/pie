# Design: CI Badge
Date: 2026-02-04
Status: Accepted

## Context
We want a quick visual indicator of CI health on the repository front page.

## Decision
Add a GitHub Actions CI badge to the top of the README, targeting the `CI` workflow on the `master` branch.

## Rationale
Badges provide immediate feedback without navigating to the Actions tab.

## Alternatives Considered
- No badge — rejected to keep CI status visible.

## Consequences
- Positive: quick status signal for contributors.
- Negative: badge URLs must be kept in sync if workflow names change.

## Follow-ups
- None.
