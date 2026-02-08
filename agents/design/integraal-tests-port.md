## Integraal Test Port (Relevant Subset)

Date: 2026-02-08

### Context
We ported the relevant unit tests from Integraal’s model module into PIE. Only tests matching existing PIE APIs were considered (standard functions and functional terms). Java-specific or missing-API tests (e.g., ComputedAtomImpl, Java invokers, TermPartitionFactory) were intentionally skipped.

### Decisions
- Standard function evaluation should return no results when solver paths encounter invalid inputs (exceptions are caught and treated as empty results).
- Additional tests cover invalid inputs, arity bounds, and edge cases for computed standard functions.
- Functional term tests focus on PIE behaviors (groundness and substitution), avoiding Java-only semantics like eval/homomorphism.

### Consequences
- Invalid inputs in solver-backed standard functions yield empty answers instead of raising.
- Test coverage now mirrors relevant Integraal behaviors while matching PIE’s execution model.
