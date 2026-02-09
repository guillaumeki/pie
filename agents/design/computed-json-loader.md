# Design: Computed JSON Loader
Date: 2026-02-09
Status: Accepted

## Context
We need @computed to load Python functions from a JSON configuration file while keeping standard functions available via @computed <stdfct>. The configuration format must be versioned and extensible for future providers beyond Python.

## Decision
Introduce a JSON schema with a version field and a providers model. Support both a legacy "functions" block and a "providers.python" block. Load Python functions by importing a module (optionally a class) from a path resolved relative to the JSON file. Register functions under prefix-qualified names (prefix:function) and require JSON-loaded functions to be used as functional terms.

## Rationale
A versioned schema provides forward compatibility, while a providers map keeps room for future computed sources. Keeping imports relative to the JSON file reduces ambiguity and allows self-contained examples. Prefix-qualified registration aligns with functional term syntax and avoids naming collisions with regular predicates.

## Alternatives Considered
- Require only a single flat "functions" block — rejected to keep the format extensible.
- Bind JSON-loaded functions as predicates — rejected for now to avoid ambiguity with standard predicate usage.

## Consequences
- Positive: Computed functions can be configured without code changes and are ready for additional providers.
- Negative: JSON-loaded functions are limited to functional-term usage until predicate binding is added.

## Follow-ups
- Add additional providers when needed (e.g., remote or sandboxed evaluators).
