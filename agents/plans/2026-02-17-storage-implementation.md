# Storage Implementation Plan (Integraal Parity)

Date: 2026-02-17

## Scope

Implement storage features inspired by Integraal storage with SOLID architecture:

- In-memory graph store variants based on LightInMemoryGraphStore.
- Triple store backend as MaterializedData + Writable.
- RDBMS store family with layout strategies and driver abstraction.
- Heterogeneous writable collection for transparent routing.
- Virtual deletion storage wrapper.
- Tests ported/adapted from Integraal storage tests and new LSP/contract tests.

## Key Decisions

1. Capabilities are separated by interface contracts:
   - ReadableData: query delegation.
   - MaterializedData: full enumeration.
   - Writable: mutation.
2. Triple store is implemented as MaterializedData (project decision), with explicit write/query constraints through validation contracts.
3. In-memory set storage is not added (already covered by existing fact base implementations).
4. Storage orchestration uses composition (builders/factories/strategies) to avoid monolithic coupling.
5. SQL backends are abstracted by driver + layout protocols. SQLite is executable in unit tests; other backends are covered by driver unit tests and optional integration tests.

## SOLID Mapping

- SRP: separate modules for drivers, layouts, stores, wrappers, and builders.
- OCP: new backend/layout via protocol implementation without changing evaluators.
- LSP: explicit acceptance contract for constrained writable storages.
- ISP: small protocols (driver, layout, writable acceptance).
- DIP: builder depends on abstractions, not concrete backends.

## Files To Add/Modify

- Add `prototyping_inference_engine/api/data/storage/` package:
  - `__init__.py`
  - `protocols.py`
  - `acceptance.py`
  - `in_memory_graph_storage.py`
  - `triple_store_storage.py`
  - `virtual_delete_storage.py`
  - `builder.py`
  - `rdbms_store.py`
  - `rdbms/` subpackage with `drivers.py` and `layouts.py`
- Add `prototyping_inference_engine/api/data/collection/writable_readable_collection.py`
- Update `prototyping_inference_engine/api/data/collection/builder.py`
- Update exports in `prototyping_inference_engine/api/data/__init__.py`
- Add unit tests under `prototyping_inference_engine/api/data/storage/test/`
- Add/extend collection tests for heterogeneous writable routing.
- Update design docs:
  - `agents/design/storage.md`
  - `AGENTS.md` tracked plans/docs.

## Test Plan

1. Port/adapt storage common tests from Integraal:
   - add/remove/evaluate/predicate and term access.
2. Port/adapt virtual deletion wrapper tests.
3. Add triple store tests:
   - arity constraints.
   - materialized behavior.
   - writable acceptance contract.
4. Add RDBMS tests:
   - layout SQL generation.
   - driver configuration and capability checks.
   - SQLite execution tests.
   - optional integration tests for PostgreSQL/MySQL/HSQLDB/Triple store with container/mocks.
5. Add LSP-focused tests for routing through `ReadableData` and heterogeneous writable collection.

## Validation Commands

1. `mypy prototyping_inference_engine`
2. `python3 -m unittest discover -s prototyping_inference_engine -t . -v`
3. `ruff check .`
4. `ruff format --check .`
5. `python3 -m coverage run -m unittest discover -s prototyping_inference_engine -t . -v`
6. `python3 -m coverage report -m`
