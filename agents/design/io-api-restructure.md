# Design: IO/API Restructure
Date: 2026-02-06
Status: Accepted

## Context
PIE grew a split between `parser/`, `io_tools/`, and `io.py`, while IRI utilities
and standard functions were placed in mixed locations. This made the layout
harder to navigate and violated the “IO under io/” and “core utilities under
api/” expectations.

## Decision
- Consolidate parsers and writers under `prototyping_inference_engine/io/` with
  `parsers/` and `writers/` subpackages.
- Move IRI utilities to `prototyping_inference_engine/api/iri/`.
- Move Integraal standard functions to `prototyping_inference_engine/api/data/functions/`.
- Adjust unittest discovery to use `-t .` so `io/` can coexist with stdlib `io`.

## Rationale
The new layout keeps public IO entry points and implementations in one place,
promotes IRI handling as a core API concern, and avoids mixing abstractions
with concrete data sources.
Using `-t .` keeps test discovery anchored to the repository root and prevents
`io/` from being imported as the stdlib module.

## Alternatives Considered
- Keep parsers under `parser/` and wrappers under `io_tools/` — rejected to avoid
  duplication and honor the explicit IO consolidation requirement.
- Leave IRI utilities outside the API — rejected because they are reused beyond
  parsing.
- Keep functions directly under `api/data/` — rejected to prevent “catch-all”
  module growth.

## Consequences
- Positive: clearer module boundaries, more consistent structure, easier discovery.
- Negative: requires import path updates and migration of tests/docs.

## Follow-ups
- Review downstream imports if external users rely on the old module paths.
