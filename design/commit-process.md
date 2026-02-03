# Design: Commit and Push Process
Date: 2026-02-03
Status: Accepted

## Context
We need consistent, machine- and human-readable commit messages and a formal end step for change processing (commit + push).

## Decision
- Adopt Conventional Commits for important changes.
- Provide a commit message template and brief policy.
- Add commit + push as required final steps in the change process.
- Delete the plan after changelog and design docs are written.

## Rationale
Conventional Commits provides a standardized, SemVer-aligned structure that is easy to parse and review.

## Alternatives Considered
- Free-form commits — rejected due to inconsistency and poor automation support.

## Consequences
- Positive: more consistent history, easier release notes.
- Negative: slightly more process overhead.

## Follow-ups
- Keep `AGENTS.md` updated with the latest process documents.
