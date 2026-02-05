# Design: Process Templates and Governance
Date: 2026-02-03
Status: Accepted

## Context
The project needs a repeatable, agent-friendly process for proposing, approving, executing, and documenting important changes. This includes plans, design decisions, and a readable changelog.

## Decision
Adopt:
- Keep a Changelog format for `CHANGELOG.md`.
- Semantic Versioning (SemVer) for version semantics.
- ADR/MADR-inspired design docs for decisions.
- A standardized plan template for change proposals.
- Definition of Done checklist for quality gates.
- Review and release checklists to reduce regressions.

## Rationale
These formats are widely recognized, concise, and provide consistent structure for both humans and automated agents.

## Alternatives Considered
- Custom changelog format — rejected due to interoperability concerns.
- No formal versioning rules — rejected due to ambiguity on breaking changes.

## Consequences
- Positive: consistent process and improved traceability.
- Negative: added overhead for small changes (mitigated by limiting the process to important changes).

## Follow-ups
- Keep `AGENTS.md` up to date with new plans and design docs.
