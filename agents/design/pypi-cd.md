# PyPI CD via GitHub Actions
Date: 2026-02-08

## Context
PIE needs a release pipeline that publishes packages to PyPI securely and with
minimal secret management.

## Decision
Use PyPI Trusted Publishing (OIDC) and a GitHub Actions workflow triggered by
GitHub releases.

## Rationale
- OIDC removes long-lived API tokens from repository secrets.
- GitHub Releases provide an explicit, auditable publish event.
- Separating build and publish stages keeps the publish job minimal and easy to
  reason about.

## Workflow Overview
- `build` job builds sdist + wheel with `python -m build` and uploads `dist/`.
- `publish` job downloads artifacts and uses `pypa/gh-action-pypi-publish`.

## Required PyPI Configuration
- Add a Trusted Publisher for the GitHub repository.
- Workflow file: `.github/workflows/release.yml`.
- Environment: `pypi` (matches the workflow environment).

## Versioning
The release process requires updating the project version in `pyproject.toml`
when changes are release-worthy.
