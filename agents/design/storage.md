# Storage Design

Date: 2026-02-17

## Context

PIE needs storage backends equivalent to Integraal storage features while preserving maintainability.
The original implementation mixes backend concerns and builder orchestration, which creates coupling.

## Decisions

1. Split storage responsibilities into dedicated modules:
- in-memory graph storage,
- triple store storage,
- RDBMS storage,
- virtual deletion wrapper,
- storage builder orchestration.

2. Keep capability contracts explicit:
- `ReadableData` for query evaluation,
- `MaterializedData` for full enumeration,
- `Writable` for mutation,
- `AtomAcceptance` for constrained writable stores.

3. Add `WritableReadableDataCollection` to route writes across heterogeneous readable backends without forcing `MaterializedData`.

4. Implement RDBMS through composable `driver + layout` abstractions:
- drivers: SQLite, PostgreSQL, MySQL, HSQLDB,
- layouts: AdHoc, EncodingAdHoc, Natural.

## SOLID Rationale

- SRP: each backend and strategy owns one concern.
- OCP: adding backend/layout is extension by implementation, not modification.
- LSP: constrained stores expose explicit acceptance checks before mutation.
- ISP: narrow protocols (`AtomAcceptance`, driver/layout contracts).
- DIP: builder depends on abstractions.

## Consequences

- Storage code remains testable without live infrastructure by mocking drivers.
- Integration tests for real backends can be added separately with containers.
- Evaluators can query storages transparently via `ReadableData`.
