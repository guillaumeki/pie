# Design: Computed JSON Default Module Example
Date: 2026-02-09
Status: Accepted

## Context
Computed function JSON examples currently show class-based Python loading, but the desired default is module-level functions without a class. Documentation should also show the full module content.

## Decision
Update the computed JSON documentation and examples to use `module` without `class`, and include the full example module content in the docs. Keep the schema and loader behavior unchanged so class-based loading remains optional.

## Rationale
Module-level functions are the most idiomatic Python usage and require less configuration. Keeping class support preserves compatibility while presenting the simplest default.

## Alternatives Considered
- Keep class-based examples — rejected because it conflicts with the requested default and adds unnecessary boilerplate.

## Consequences
- Positive: simpler, clearer documentation; no class declaration required for Python functions.
- Negative: none; class-based loading remains supported but less visible.

## Follow-ups
- None.
