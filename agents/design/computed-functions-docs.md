# Computed Functions Documentation (2026-02-06)

## Context
The documentation listed computed functions but lacked signatures, behavioral notes, and usage
clarity (predicate form vs functional term form). This made the feature difficult to use and
left doc examples ambiguous.

## Decision
- Add explicit signatures and behavior notes grouped by function category.
- Document both usage modes:
  - Predicate form with the result in the last argument.
  - Functional term form, rewritten into computed atoms internally.
- Add runnable examples for both usage modes.

## Consequences
- Documentation is now actionable with clear contracts and examples.
- Doc example tests enforce that the new snippets stay executable.
