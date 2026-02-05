# Design: agent-artifacts-and-docs
Date: 2026-02-05
Status: Accepted

## Context
Agent-related artifacts (plans, design docs, process docs, templates) were spread across top-level folders, making the repository harder to scan. Documentation practices also needed to be standardized and published via GitHub Pages.

## Decision
Move agent artifacts under `agents/` with dedicated subfolders, formalize documentation practices, and publish Markdown docs via MkDocs + GitHub Pages.

## Rationale
Grouping non-code artifacts improves repository clarity, keeps the root focused on product code, and makes process materials easier to find. MkDocs is lightweight and matches the requested Markdown-first documentation approach.

## Alternatives Considered
- Keep artifacts at the repo root — rejected to reduce clutter and improve discoverability.
- Use Sphinx instead of MkDocs — rejected due to higher setup overhead for a Markdown-first workflow.

## Consequences
- Positive: clearer repo structure, consistent documentation expectations, and an easy path to publish docs.
- Negative: requires updating existing path references and maintaining a Pages workflow.

## Follow-ups
- Keep docs updated when behavior or design changes.
