# Design: Formula-Based Rule Model
Date: 2026-02-14
Status: Accepted

## Context
PIE represents rules with disjunctive heads and supports algorithms that require
specific rule fragments (e.g., existential disjunctive rules). The previous
model encoded disjunction as a list of head queries, which did not match the
intended logical representation of disjunctive rules as disjunctive formulas.

## Decision
Represent rules as `Rule(body: Formula, head: Formula)` and make fragment
requirements explicit via validators. Free variables must match in body and
head; existential variables are those bound by ∃ in the head.

## Rationale
Using formulas for both sides aligns the API with PIE's logic capabilities,
avoids encoding disjunction at the container level, and makes rule semantics
explicit. Validators keep algorithms correct without hard-coding structural
assumptions into `Rule`.

## Alternatives Considered
- Keep `head: Iterable[Query]` and encode disjunction in Rule — rejected because
  it obscures the logical meaning and complicates formula-based reasoning.
- Introduce subclasses per fragment — rejected due to class proliferation and
  weaker separation of concerns.

## Consequences
- Positive: A single rule model matches the logical semantics and supports
  extended formulas.
- Positive: Algorithms can declare fragment requirements via validators.
- Negative: More explicit validation is required before running algorithms.
- Negative: Converters are needed when algorithms operate on CQ fragments.

## Follow-ups
- Update documentation to describe the formula-based Rule model and validators.
