# Core Processors Design
Date: 2026-02-17

## Context
PIE needed a clean core-processing implementation aligned with Integraal variants while reducing duplication and improving extensibility.

## Decisions
- Introduced `PieceSplitter` as a protocol to support multiple splitting strategies.
- Added default `VariableInducedPieceSplitter` implementation.
- Implemented the following core algorithm variants on `AtomSet`:
  - `NaiveCoreProcessor`
  - `ByPieceCoreProcessor` (`EXHAUSTIVE`, `BY_SPECIALISATION`, `BY_DELETION`)
  - `ByPieceAndVariableCoreProcessor`
  - `MultiThreadsByPieceCoreProcessor` (same three variants)
- Centralized shared behavior in `core_helpers.py` and `core_variants.py`.
- Added `MutableMaterializedCoreProcessor` adapter to run core reduction in-place on mutable materialized stores.
- Extended writable surfaces with deletion support (`remove`, `remove_all`) for mutable fact bases and writable collections.

## Rationale
- SOLID: split concerns by abstraction level and avoid large monolithic processors.
- OCP: new piece splitters and strategies can be added without modifying existing processors.
- Practical safety: by-piece variants include a final naive normalization pass to guarantee core output.

## Known Tradeoff
- The multithread variant synchronizes piece updates with a lock to preserve deterministic semantics.
