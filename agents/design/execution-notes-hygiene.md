# Design: Execution Notes Hygiene
Date: 2026-02-06
Status: Accepted

## Context
Local quality checks reported noisy or confusing execution notes: Bandit reported a low-severity issue without details, pip-audit warned about cache permissions, and Vulture surfaced a large set of low-confidence false positives.

## Decision
- Exclude `__pycache__` paths from Bandit scans to avoid scanning bytecode artifacts.
- Run pip-audit with a project-local cache directory via `PIP_AUDIT_CACHE_DIR=.cache/pip-audit`.
- Configure Vulture with `min_confidence = 70` and ignore context manager variables `exc_type`, `exc_val`, and `exc_tb`.

## Rationale
These adjustments remove tool noise without disabling the checks or hiding meaningful issues, and they keep behavior consistent across environments.

## Alternatives Considered
- Disable Bandit/Vulture entirely — rejected because it would reduce safety and signal.
- Keep defaults and ignore warnings — rejected because the process requires clean execution notes.

## Consequences
- Positive: quieter, actionable tool outputs for local checks and CI.
- Negative: Vulture will not report low-confidence findings (<70%), which may hide some minor candidates for cleanup.

## Follow-ups
- Revisit Vulture thresholds if additional true positives are missed.
