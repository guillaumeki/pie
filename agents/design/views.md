# Views Design

Date: 2026-02-23

## Context

PIE needs virtual data sources that can be queried like regular `ReadableData`
without forcing users to materialize external datasets into a fact base. View
declarations must support multiple backend protocols and integrate with DLGPE
imports and session-based reasoning workflows.

## Decisions

1. Introduce a dedicated `api/data/views` package with explicit separation:
- declaration model (`model.py`),
- document loading and backend wiring (`builder.py`),
- validation (`validation.py`),
- runtime query exposure (`source.py`),
- missing-value policies (`missing_values.py`),
- backend adapters (`backends/*.py`).

2. Keep runtime views read-only and `ReadableData`-compatible:
- view sources expose `evaluate(...)` and optional schema metadata,
- no implicit promotion to `Writable` or `MaterializedData`.

3. Support two integration paths:
- `@view alias:<file.vd>` to bind an alias prefix for predicates,
- `@import <file.vd>` to import views as regular external sources.

4. Keep parser/session/import-registry decoupled:
- parser records view directives in header metadata,
- session resolves directives and merges view sources,
- import registry detects `.vd` and delegates to the view loader.

## SOLID Rationale

- SRP: parsing, validation, specialization, backend adaptation, and runtime
  exposure are isolated modules.
- OCP: adding a new backend protocol only requires a new backend adapter and
  registration in the builder.
- LSP: view sources fully satisfy `ReadableData` contracts expected by evaluators.
- ISP: backend interfaces are narrow (`ViewQueryBackend` and datasource protocol
  declarations).
- DIP: session and parser layers depend on builder/loader abstractions, not on
  backend implementation details.

## Consequences

- Views are query-transparent in reasoning sessions through `result.sources`.
- Aliased and imported views coexist with in-memory facts and other sources.
- Validation catches malformed declarations early (duplicate IDs, missing files,
  unsupported parameter combinations).
