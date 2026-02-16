# Design: Rule Compilation Package
Date: 2026-02-16
Status: Accepted

## Context
PIE needs rule compilation (as defined in the Integraal/Graal lineage) to speed up
query answering and rewriting. The existing behavior is spread across multiple
Integraal modules. We want a single, cohesive package that can be reused by
rewriting and query evaluation, while respecting Python module hierarchy rules
and OCP (new compilations without modifying existing core logic).

## Decision
Introduce a top-level package `prototyping_inference_engine/rule_compilation/` with:
- `api/` interfaces (`RuleCompilation`, `RuleCompilationCondition`, `RuleCompilationResult`).
- `id/` and `hierarchical/` implementations ported from Integraal.
- `NoCompilation` null object.
- Validation helpers for compilable rule fragments.

Integrate compilation into rewriting and query evaluation via optional
parameters and default to `NoCompilation` to preserve current behavior.

## Rationale
A dedicated package avoids scattering compilation logic across unrelated
modules, enforces SRP, and allows additional compilations to be added without
changing core algorithm code (OCP). The optional integration preserves existing
API behavior while enabling performance improvements where applicable.

## Alternatives Considered
- Keep compilation logic within rewriting/evaluation modules — rejected due to
  cross-module coupling and loss of reusability.
- Implement only a single compilation strategy — rejected to keep parity with
  Integraal and to support future extensions.

## Consequences
- Positive: Centralized, reusable compilation API and implementations.
- Positive: Clean integration points for algorithms via optional parameters.
- Negative: Additional module surface area and tests to maintain.

## Follow-ups
- Extend compilation support to additional fragments if needed.
- Add more tests once advanced compilation features are added.
