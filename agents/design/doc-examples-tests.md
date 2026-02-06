# Documentation Examples: Runnable And Tested (2026-02-06)

## Context
Documentation examples were drifting from real behavior, and some snippets were untested. We want
examples that are copy-paste runnable and guaranteed to stay in sync with the implementation.

## Decision
- All documentation code blocks are extracted by a unit test and must be registered in the test
  suite.
- Runnable snippets (Python and DLGPE/DLGP) are executed in tests, with explicit assertions on
  expected behavior.
- Shell examples are validated for presence/formatting but are not executed to avoid side effects.

## Rationale
- Centralized coverage prevents examples from silently rotting.
- Executing snippets catches API regressions and mismatches between docs and behavior early.
- Non-executed shell blocks avoid environment-specific failures while still enforcing coverage.

## Consequences
- Editing documentation examples requires updating the doc example test registry.
- CI coverage includes doc examples, so regressions are surfaced immediately.
