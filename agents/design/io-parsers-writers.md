# Design: IO Parsers/Writers Package
Date: 2026-02-05
Status: Accepted

## Context
PIE currently exposes parsing under `parser/` without a corresponding writer. We need
export capabilities and a clearer separation between reading and writing.

## Decision
Create `prototyping_inference_engine/io/` with `parsers/` and `writers/` subpackages.
Provide DLGPE writer support and re-export parsers for compatibility. Add strict handling
of relative @prefix declarations before @base in DLGPE/DLGP2 (configurable).

## Rationale
Separating IO improves discoverability and keeps parse/serialize responsibilities distinct.
A writer enables round-trip workflows and reuse of stored @base/@prefix context.

## Alternatives Considered
- Leave everything under `parser/` — rejected to avoid mixing read/write concerns.

## Consequences
- Positive: clearer IO surface, enables export pipelines.
- Negative: extra modules and docs to maintain.

## Follow-ups
- Add additional writers (DLGP2, RDF) as needed.
