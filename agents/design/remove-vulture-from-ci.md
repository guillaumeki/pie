# Design: remove-vulture-from-ci
Date: 2026-02-05
Status: Accepted

## Context
Vulture currently runs in CI as an informational step but does not fail the build. Successful CI runs typically hide logs, so the signal is rarely consumed.

## Decision
Remove Vulture from CI while keeping it in local quality checks.

## Rationale
CI should surface actionable failures; non-blocking Vulture output is better suited to manual/local use.

## Alternatives Considered
- Keep Vulture in CI as non-blocking — rejected because results are easy to miss.

## Consequences
- Positive: CI remains focused on failure signals.
- Negative: dead code detection is now a manual/local responsibility.

## Follow-ups
- None.
