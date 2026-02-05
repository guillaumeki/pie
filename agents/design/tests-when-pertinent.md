# Design: tests-when-pertinent
Date: 2026-02-05
Status: Accepted

## Context
The change process mandates running tests but does not explicitly require writing unit tests when changes warrant them.

## Decision
Add explicit language to the change process and Definition of Done requiring unit tests when relevant.

## Rationale
Making the expectation explicit reduces ambiguity and encourages coverage for behavioral changes.

## Alternatives Considered
- Keep the requirement implicit — rejected because it allows changes without corresponding tests.

## Consequences
- Positive: clearer quality expectations and improved coverage discipline.
- Negative: requires judgment calls for doc-only or no-behavior-change updates.

## Follow-ups
- None.
