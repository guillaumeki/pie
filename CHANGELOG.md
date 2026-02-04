# Changelog
All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [Unreleased]

## [2026-02-04]
- Added: functional terms support via Python-backed readable data sources and computed predicates.
- Added: function-term rewrite helper shared by atom and conjunction evaluators.
- Changed: function evaluation now supports partial bindings via `min_bound` + solver in Python mode.
- Changed: query evaluation module reorganized by evaluator category with centralized errors.
- Changed: mypy cleanup across core APIs, parsers, unifiers, evaluators, and tests (mypy clean).

## [2026-02-03]
- Added: DLGPE comparison operators support (<, >, <=, >=, !=) with infix display and evaluation via readable data sources.
- Added: comparison data source and helper to evaluate queries with extra sources.
- Added: process templates (plan/design), Definition of Done, versioning guidance.
- Added: review and release checklists, conventional commits guidance.
- Added: process governance design doc and commit process design doc.
- Added: commit/push process step, commit template, and commit policy.
