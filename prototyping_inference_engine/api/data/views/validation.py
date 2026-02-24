"""Semantic validation for view declaration documents."""

from __future__ import annotations

from pathlib import Path
from warnings import warn

from prototyping_inference_engine.api.data.views.errors import ViewValidationError
from prototyping_inference_engine.api.data.views.model import (
    DatasourceProtocol,
    MissingValuePolicy,
    ViewDocument,
)


_REQUIRED_PARAMETERS: dict[DatasourceProtocol, tuple[str, ...]] = {
    DatasourceProtocol.POSTGRESQL: ("url", "database"),
    DatasourceProtocol.MYSQL: ("url", "database"),
    DatasourceProtocol.HSQLDB: ("url", "database"),
    DatasourceProtocol.SQLITE: ("url",),
    DatasourceProtocol.MONGODB: ("url", "database"),
    DatasourceProtocol.SPARQL_ENDPOINT: ("url",),
    DatasourceProtocol.JSON_WEB_API: (),
}


def validate_view_document(
    document: ViewDocument, base_dir: Path | None = None
) -> None:
    """Validate semantic constraints for a parsed view document."""
    if not document.datasources:
        raise ViewValidationError("View document must declare at least one datasource")
    if not document.views:
        raise ViewValidationError("View document must declare at least one view")

    datasource_ids: set[str] = set()
    for datasource in document.datasources:
        if datasource.id in datasource_ids:
            raise ViewValidationError(
                f"Duplicate datasource identifier: {datasource.id}"
            )
        datasource_ids.add(datasource.id)

        parameters = dict(datasource.parameters)
        _validate_datasource_password_parameters(datasource.id, parameters, base_dir)

        protocol = DatasourceProtocol.from_label(datasource.protocol)
        if protocol is None:
            warn(
                f"Unknown datasource protocol '{datasource.protocol}' for datasource '{datasource.id}'",
                stacklevel=2,
            )
            continue

        required = _REQUIRED_PARAMETERS[protocol]
        missing_required = [name for name in required if name not in parameters]
        if missing_required:
            warn(
                (
                    f"Datasource '{datasource.id}' is missing required parameters "
                    f"for protocol '{datasource.protocol}': {', '.join(missing_required)}"
                ),
                stacklevel=2,
            )

    view_ids: set[str] = set()
    for view in document.views:
        if view.id in view_ids:
            raise ViewValidationError(f"Duplicate view identifier: {view.id}")
        view_ids.add(view.id)

        if view.datasource not in datasource_ids:
            raise ViewValidationError(
                f"View '{view.id}' references unknown datasource '{view.datasource}'"
            )

        _validate_view_query_fields(view.id, view.query, view.query_file, base_dir)

        for index, signature in enumerate(view.signature):
            if signature.if_missing not in {
                MissingValuePolicy.IGNORE,
                MissingValuePolicy.FREEZE,
                MissingValuePolicy.EXIST,
                MissingValuePolicy.OPTIONAL,
            }:
                warn(
                    (
                        f"View '{view.id}' has unsupported ifMissing policy at position "
                        f"{index}: {signature.if_missing}"
                    ),
                    stacklevel=2,
                )


def _validate_datasource_password_parameters(
    datasource_id: str,
    parameters: dict[str, object],
    base_dir: Path | None,
) -> None:
    password = parameters.get("password")
    password_file = parameters.get("passwordFile")

    if password is not None and password_file is not None:
        raise ViewValidationError(
            f"Datasource '{datasource_id}' cannot define both password and passwordFile"
        )

    if isinstance(password_file, str):
        candidate = Path(password_file)
        if not candidate.is_absolute() and base_dir is not None:
            candidate = base_dir / candidate
        if not candidate.exists() or not candidate.is_file():
            raise ViewValidationError(
                f"Datasource '{datasource_id}' passwordFile is not readable: {password_file}"
            )


def _validate_view_query_fields(
    view_id: str,
    query: str | None,
    query_file: str | None,
    base_dir: Path | None,
) -> None:
    has_query = query is not None
    has_query_file = query_file is not None

    if has_query and has_query_file:
        raise ViewValidationError(
            f"View '{view_id}' cannot define both query and queryFile"
        )
    if not has_query and not has_query_file:
        raise ViewValidationError(
            f"View '{view_id}' must define exactly one of query or queryFile"
        )

    if isinstance(query_file, str):
        candidate = Path(query_file)
        if not candidate.is_absolute() and base_dir is not None:
            candidate = base_dir / candidate
        if not candidate.exists() or not candidate.is_file():
            raise ViewValidationError(
                f"View '{view_id}' queryFile is not readable: {query_file}"
            )
