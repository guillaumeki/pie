# Design: IRI Manager Stack
Date: 2026-02-05
Status: Accepted

## Context
PIE now supports IRI resolution in DLGPE/DLGP2 parsing, but the implementation was limited to
basic resolution without a complete IRI stack (strict parsing, normalization, preparator, and
manager). We need a full IRI subsystem compatible with irirefs (Java), including a real manager
for base/prefix handling and optional normalization.

## Decision
Introduce a dedicated `prototyping_inference_engine/iri/` package that provides:
- `IRIRef` for parsing, resolution, normalization, and relativization
- `IRINormalizer` with `StandardComposableNormalizer` and `ExtendedComposableNormalizer`
- `BasicStringPreparator` for HTML/XML entity decoding
- `IRIManager` for base/prefix resolution, normalization, and relativization helpers

Parsers (DLGPE/DLGP2) use an `IRIManager` configured with the no-op STRING normalizer and a
parser-specific base (disabled until `@base` is declared) to avoid unintended resolution.

## Rationale
Separating IRI concerns into a dedicated package keeps parser logic focused on syntax and
simplifies future reuse (e.g., export or new parsers). The manager provides a single place to
store base/prefix state, and optional normalization/preparation aligns with irirefs behavior
without altering data by default.

## Alternatives Considered
- Keep all IRI logic in `parser/` — rejected to avoid a monolithic parser and to enable reuse.
- Enable normalization by default — rejected to preserve input fidelity and match irirefs.

## Consequences
- Positive: richer IRI support with tests ported from irirefs; reusable manager for parsing
  and export workflows.
- Negative: more code and tests to maintain; slightly more moving parts in parser setup.

## Follow-ups
- Document IRI manager usage in `docs/` and README.
- Consider exporting prefix/base state in a future serializer.
