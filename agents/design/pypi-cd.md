# PyPI CD via Git Tags
Date: 2026-02-08

## Context
PIE needs automatic PyPI publication without manual GitHub Releases.

## Decision
Trigger the PyPI publish workflow on git tags matching `v*` and enforce that the
Git tag version matches `pyproject.toml`.

## Rationale
- Tag pushes enable fully automatic publication.
- A version/tag consistency check prevents accidental mismatches.

## Workflow Overview
- `build` job builds sdist + wheel with `python -m build`.
- The workflow validates `vX.Y.Z` matches `pyproject.toml` before building.
- `publish` job uses OIDC Trusted Publishing to upload to PyPI.

## Required PyPI Configuration
- Add a Trusted Publisher for the GitHub repository.
- Workflow file: `.github/workflows/release.yml`.
- Environment: `pypi` (optional but supported by the workflow).

## Versioning
When a release is justified, update `pyproject.toml` and push a tag of the form
`v<version>` (e.g., `v0.0.14`).
