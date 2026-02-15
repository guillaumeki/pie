# Changelog
All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [Unreleased]
- Added: DLGPE query-evaluation tests covering computed function terms and scheduler ordering.
- Changed: consolidated design documents into `agents/design/designs-compressed.md`.
- Changed: evaluation is query-only (FOQuery and higher-level queries); formula evaluators were removed.
- Changed: query evaluators now expose `prepare` for reuse of prepared queries.

## [2026-02-15]
- Added: minimal-evaluation stratification to minimize strata while preserving one-pass evaluation for acyclic SCCs.
- Changed: bumped version to 0.0.25.

## [2026-02-15]
- Added: igraph dependency for GRD stratification algorithms with PyPy-compatible graph routines.
- Changed: GRD stratification now delegates SCC and Bellman-Ford to igraph.
- Changed: bumped version to 0.0.24.

## [2026-02-15]
- Added: GRD stratification strategies (by-SCC, minimal, single-evaluation) with OCP-friendly strategy interface.
- Added: GRD stratification tests covering SCC and Bellman-Ford stratification outputs.
- Changed: bumped version to 0.0.23.

## [2026-02-15]
- Added: GRD top-level package with disjunctive head and safe-negation support.
- Added: GRD dependency checker abstraction with productivity checker.
- Changed: bumped version to 0.0.22.

## [2026-02-14]
- Added: rule validators for conjunctive and existential-disjunctive fragments.
- Changed: rules now use formula bodies and heads with matching free variables.
- Changed: DLGPE rule parsing now adds implicit quantifiers to satisfy rule invariants.
- Changed: DLGPE writer strips quantifiers when emitting rules.
- Changed: bumped version to 0.0.21.

## [2026-02-10]
- Added: prepared FOQuery implementations per formula, with lightweight result-bound estimation.
- Added: dynamic backtrack scheduling that prioritizes evaluable subqueries with smaller bounds.
- Added: optional `ReadableData.estimate_bound` and delegated support in collections and wrappers.
- Added: scheduler coverage test for bound-based ordering.
- Changed: FOQuery evaluators now prepare queries before execution.
- Changed: bumped version to 0.0.20.

## [2026-02-09]
- Added: JSON-based computed configuration with a versioned schema and extensible providers.
- Added: Python function loading via `@computed <prefix>: <path/to/config.json>` and functional-term validation.
- Added: documentation example, schema file, and tests for computed JSON loading.
- Changed: DLGPE parsing now accepts non-`stdfct` `@computed` directives and defers validation to session parsing.
- Changed: default computed JSON examples now use module-level functions without a class.
- Changed: release workflow now parses pyproject.toml with tomllib/tomli for Python 3.10 compatibility.
- Changed: bumped version to 0.0.19.

## [2026-02-08]
- Added: KnowledgeBase and RuleBase abstractions with ReasoningSession helpers.
- Added: CSVCopyable protocol for fact bases that can export CSV.
- Added: DatalogDelegable protocol and delegation wrappers (DelAtomWrapper, QueryableDataDelAtomsWrapper).
- Added: PreparedQuery and PreparedFOQuery interfaces.
- Added: FOQueryFactory package and backward-compatible re-export.
- Added: FOConjunctionFactBaseWrapper to expose fact bases as conjunction formulas.
- Added: identity-based term/predicate classes and factories, plus IdentityWrapper utility.
- Changed: functional terms split into logical vs evaluable terms based on `@computed` prefixes.
- Changed: DLGPE parsing treats registered Python functions as evaluable functional terms.
- Changed: tests avoid `str`/`repr` assertions and normalize unordered data for determinism.
- Changed: DLGPE parsing now uses injected term/predicate factories to enforce identity semantics.
- Updated: documentation to describe new APIs and functional-term semantics.
- Added: GitHub Actions release workflow for PyPI Trusted Publishing.
- Changed: change process now requires version updates for release-worthy changes.
- Changed: bumped version to 0.0.14.
- Changed: PyPI publishing now triggers on `v*` tags with a version/tag consistency check.
- Updated: Usage documentation now focuses on concrete usage flows with executable examples.
- Added: Usage reference with signatures and runnable examples for every computed function.
- Added: documentation tests for new usage examples and API snippets.
- Added: standard-function tests for invalid inputs, arity bounds, and functional-term substitution behavior.
- Changed: solver-backed standard functions now return no results for invalid inputs.

## [2026-02-07]
- Changed: allow functional terms under negation by delegating to inner evaluators.
- Added: negation evaluator tests for functional terms (including nested terms).
- Updated: documentation example for functional terms under negation.
- Changed: removed the DLGP2 parser and standardized on DLGPE (including `.dlgp` examples using `|`).
- Changed: normalized equality atoms in CQ containment to keep equivalence checks consistent.
- Updated: documentation now treats DLGPE as the DLGP version and uses `.dlgp` as the extension.
- Changed: removed `CLAUDE.md` as requested.

## [2026-02-06]
- Added: `@computed` directive support in DLGPE parsing with computed prefixes stored in parse results and sessions.
- Added: Integraal standard functions as computed predicates, including reversible evaluation for sum/minus/product/divide/average.
- Added: collection-valued literal creation via `LiteralFactory.create_from_value` for computed functions returning tuples, sets, and dicts.
- Added: tests for computed function evaluation with missing-argument inference.
- Added: broader standard-function tests covering collections, dictionaries, conversions, and edge cases.
- Changed: consolidated parsers/writers under `io/` and removed the `io.py` wrapper module.
- Changed: moved IRI utilities under `api/iri/`.
- Changed: moved Integraal standard functions under `api/data/functions/`.
- Changed: unittest discovery now runs with `-t .` to avoid stdlib `io` conflicts.
- Updated: documentation to describe computed predicates and supported Integraal functions.
- Updated: computed predicate examples to include collection and dictionary functions.
- Added: documentation example tests that execute runnable snippets and require coverage for all doc code blocks.
- Updated: computed predicate documentation with signatures, usage modes, and functional-term example.
- Added: documentation example tests now require explanatory text around code blocks.

## [2026-02-05]
- Fixed: add mypy to dev requirements so CI can run type checks.
- Changed: reorganized agent artifacts under `agents/` and added MkDocs docs with GitHub Pages publishing.
- Changed: expanded documentation content with standalone guides and examples.
- Changed: AtomEvaluator now delegates function-term conjunction evaluation via the registry to reduce coupling.
- Changed: change process now explicitly requires adding unit tests when relevant.
- Added: CI-generated coverage badge committed to the repository and displayed in README.
- Fixed: CI now commits the coverage badge when it is first created.
- Fixed: CI badge commit step now handles untracked detection and rebases before pushing.
- Fixed: coverage badge generation now runs only once per CI matrix and fails if coverage is missing.
- Fixed: coverage badge generation now removes the existing file before regenerating.
- Changed: removed Vulture from CI; keep it for local checks only.
- Added: IRI resolution for DLGPE/DLGP2 parsing with base/prefix context captured in parse results and sessions.
- Added: full IRI manager stack with parsing, resolution, normalization, preparators, and extensive tests.
- Added: IO package with parser and writer entry points, plus DLGPE writer export support.
- Changed: DLGPE/DLGP2 parsing now rejects relative @prefix before @base by default (configurable).
- Fixed: IRI relativization now treats trailing-slash base paths correctly (prevents extra `..` segments).
- Fixed: IRI parsing now preserves scheme-specific paths (e.g. `urn:isbn:...`) during recomposition.
- Fixed: IRI normalization keeps non-unreserved ASCII (like backslash) percent-encoded in extended mode.
- Fixed: IRI normalization now inserts `/` when authority is present with an empty path.
- Fixed: IRI relativization falls back to absolute IRIs when a relative candidate would resolve incorrectly.
- Added: extra IRI relativization regression cases for trailing-slash base paths.
- Added: more explicit IRI relativization expected-output test cases.
- Added: edge-case IRI relativization expected-output cases for queries, fragments, and opaque schemes.
- Added: broader IRI relativization coverage for params, ports, IPv6/IPvFuture, and network-path rejection.
- Added: IRI resolution and normalization edge-case coverage for dot segments, empty query/fragment, and invalid percent sequences.
- Changed: DLGPE computed directives now only accept Integraal standard functions via `@computed ig:<stdfct>`.
- Added: documentation updates clarifying Integraal standard function loading in DLGPE.
- Changed: tuned local quality tooling to reduce Bandit/Vulture noise and use a project-local pip-audit cache.
- Fixed: DLGPE parser now supports nested functional terms (required for standard function examples).

## [2026-02-04]
- Added: functional terms support via Python-backed readable data sources and computed predicates.
- Added: function-term rewrite helper shared by atom and conjunction evaluators.
- Changed: function evaluation now supports partial bindings via `min_bound` + solver in Python mode.
- Changed: query evaluation module reorganized by evaluator category with centralized errors.
- Changed: mypy cleanup across core APIs, parsers, unifiers, evaluators, and tests (mypy clean).
- Added: GitHub Actions CI running mypy and full unit tests on push/PR.
- Added: GitHub Actions CI badge in README.
- Fixed: CI now installs mypy and runtime requirements explicitly.
- Changed: enforce mypy + full test suite passing before commit/push.
- Added: code quality tooling (Ruff, Coverage, Bandit, pip-audit, Vulture, Radon, Hypothesis) with CI integration.
- Changed: applied Ruff formatting baseline across the codebase.
- Changed: documented before-push quality checklist in AGENTS.
- Added: README badges for license and Python version.

## [2026-02-03]
- Added: DLGPE comparison operators support (<, >, <=, >=, !=) with infix display and evaluation via readable data sources.
- Added: comparison data source and helper to evaluate queries with extra sources.
- Added: process templates (plan/design), Definition of Done, versioning guidance.
- Added: review and release checklists, conventional commits guidance.
- Added: process governance design doc and commit process design doc.
- Added: commit/push process step, commit template, and commit policy.
