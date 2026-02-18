# Plan: Forward Chaining Implementation (Integraal Parity)
Date: 2026-02-18
Status: in_progress

## Objectives
Implement PIE forward chaining with functional parity against Integraal forward chaining while improving SOLID adherence and reducing coupling/duplication.

## Scope
- Forward chaining API and chase lifecycle.
- Chase builder with strategy configuration.
- Rule schedulers (naive, by-predicate, GRD).
- Rule applier pipeline:
  - body->query transformers
  - trigger computers
  - trigger checkers
  - trigger applier
  - existential renamers
  - facts handlers
  - rule applier variants (breadth-first, parallel, multithread, source-delegated datalog)
- Halting conditions.
- Treatments and stratified meta-chase.
- Descriptions and diagnostics.
- Port/replicate major Integraal forward-chaining tests and add missing component-level tests.

## SOLID design choices
- SRP: each concern isolated in dedicated protocol/class.
- OCP: builder composes interchangeable strategies.
- LSP: shared contracts for scheduler/applier/checker/computer.
- ISP: narrow protocols.
- DIP: chase engine depends on abstractions and injected strategies.

## Files to add/modify
- New package: `prototyping_inference_engine/forward_chaining/**`
- Session integration points if required later.
- Tests: `prototyping_inference_engine/forward_chaining/**/test/**`
- Design doc update: `agents/design/`.

## Validation
1. mypy
2. targeted forward_chaining tests
3. full unittest suite
4. ruff check / format check
5. coverage (target >90% on new module)
6. bandit, pip-audit, vulture, radon

## Execution order
1. Create package skeleton + protocols + core chase lifecycle
2. Implement schedulers + halting + treatments
3. Implement trigger pipeline + rule applier variants
4. Implement builder defaults and stratified chase
5. Port Integraal forward chaining tests + add unit tests
6. Run quality gates and fix issues
