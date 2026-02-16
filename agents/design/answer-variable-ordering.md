# Answer Variable Ordering

Date: 2026-02-12

## Context
FOQuery answer variables define the projection order of query results. The order is specified explicitly in query text (e.g., `?(X,Y)`), and must be preserved end-to-end.

## Decision
1. Preserve answer variable ordering as written in source queries.
2. Store answer variables as ordered tuples (no set/frozenset usage for answer vars).
3. Parsers return ordered tuples for explicit answer variables. For `*`, use a deterministic order by identifier.
4. Evaluators and documentation examples project answers in `FOQuery.answer_variables` order without re-sorting.

## Consequences
- Query results are deterministic and aligned with standard FO query semantics.
- Tests and documentation must avoid normalizing or sorting answer variable order.
 
