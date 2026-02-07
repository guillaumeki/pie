# Remove DLGP2 Parser

Date: 2026-02-07

## Context
PIE maintained both DLGP 2.1 and DLGPE parsers. The codebase is moving to a
single parser to reduce duplication and keep behavior consistent.

## Decision
Remove the DLGP2 parser and route all parsing through DLGPE. `.dlgp` files are
still accepted, but they must use DLGPE-compatible syntax (notably `|` for
disjunction).

## Consequences
- One parser entry point (`DlgpeParser`) across the codebase.
- `.dlgp` examples are updated from `;` to `|`.
- Tests and docs reference DLGPE only.
