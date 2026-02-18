# Forward Chaining (Chase) — 2026-02-18

## Goal
Provide a SOLID, pluggable forward-chaining engine (chase) matching Integraal features while staying compliant with PIE abstractions (ReadableData/MaterializedData/Writable) and enabling strategy swaps (schedulers, trigger computation, renamers, rule appliers, halting conditions, lineage).

## Architecture
- **ChaseImpl** orchestrates rule application steps with:
  - **RuleScheduler** variants: naive, predicate-based, GRD-based.
  - **TriggerComputer** variants: naive, restricted, semi-naive, two-steps.
  - **TriggerChecker** variants: oblivious, semi-oblivious, restricted, equivalent, multi-checker.
  - **Renamers**: fresh, body-skolem, frontier-skolem, frontier-by-piece-skolem.
  - **RuleAppliers**: breadth-first, parallel (threaded), multi-thread, source-delegated Datalog.
  - **HaltingConditions**: step limit, atom limit, timeout, external interruption, created-facts-at-previous-step, rules-to-apply.
  - **Treatments**: rule split, add created facts, compute core/local core, predicate-filter end, debug hooks.
- **ChasableData** wraps writable/materialized data plus lineage tracker; handles created facts and deduplication.
- **StratifiedChase** runs per-stratum (GRD) with optional wrapper via `StratifiedChaseBuilder`.
- **Lineage**: pluggable (none, simple, federated) with replay metadata at rule application.
- **Description objects** expose the configured chase (useful for debugging and docs).

## SOLID notes
- SRP: each concern (scheduling, trigger computation/checking, renaming, application, halting, treatment) in its module.
- OCP: new strategies can be injected via builders without touching consumers.
- LSP: RuleApplier and TriggerComputer respect common protocol; MaterializedData/Writable separated from ReadableData.
- ISP: fine-grained protocols (TriggerChecker, Renamer, FactsHandler).
- DIP: builders depend on abstractions (protocols) and assemble concrete implementations.

## Design choices vs Integraal
- Keep chase step result with `applied_rules=None` on first step (Integraal semantics) to keep schedulers consistent.
- Use hashable `SubstitutionKey` to store substitutions in sets/maps (avoid mutable hashing issues).
- Fact handlers split direct vs delegated application for external stores.
- Multithreaded applier delegates concurrency to rule-level application; still reuses trigger computation shared logic.

## Testing
- `prototyping_inference_engine/forward_chaining/chase/test/test_forward_chaining.py` covers:
  - schedulers, appliers, trigger computers/checkers, renamers, treatments, stratified chase, function-term heads.
- Integration with existing data abstractions (MaterializedData/Writable) via ChasableData and builders.

## Documentation impact
- Add README/architecture docs describing forward chaining availability and configuration knobs.
- Keep mkdocs site in sync (`mkdocs build --clean`).
