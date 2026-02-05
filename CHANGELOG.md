# Changelog
All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [Unreleased]

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
