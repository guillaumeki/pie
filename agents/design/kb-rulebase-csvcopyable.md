# Design: KnowledgeBase, RuleBase, CSVCopyable
Date: 2026-02-08
Status: Accepted

## Context
PIE needed a first-class way to group facts and rules (as in Integraal) and a
clear capability flag for fact bases that can export CSV content. These are
core API-level concepts and should integrate with the ReasoningSession lifecycle.

## Decision
- Introduce `RuleBase` and `KnowledgeBase` under `api/kb/`.
- Keep `Ontology` as a `RuleBase` implementation for disjunctive rules.
- Add a `CSVCopyable` protocol under `api/fact_base/protocols.py`.
- Extend `ReasoningSession` to create and track rule bases and knowledge bases.

## Rationale
`RuleBase` and `KnowledgeBase` provide explicit API types rather than ad-hoc
collections. `CSVCopyable` aligns with data-source capability checks without
imposing a concrete base class.

## Alternatives Considered
- Keep rules as raw lists in session state — rejected for lack of structure.
- Add CSV export as a mixin base class — rejected because protocol-based
  capability checks are more flexible in Python.

## Consequences
- Positive: clearer API semantics and session lifecycle integration.
- Negative: additional modules and tests to maintain.

## Follow-ups
- Document knowledge/rule base usage in `docs/` and README.
