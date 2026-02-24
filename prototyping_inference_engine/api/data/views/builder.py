"""Builder for runtime view sources from declaration documents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus
from warnings import warn

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage
from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.data.views.backends.json_web_api import (
    JSONWebAPIViewBackend,
)
from prototyping_inference_engine.api.data.views.backends.mongodb import (
    MongoDBViewBackend,
)
from prototyping_inference_engine.api.data.views.backends.sparql import (
    SparqlEndpointViewBackend,
)
from prototyping_inference_engine.api.data.views.backends.sql import SQLViewBackend
from prototyping_inference_engine.api.data.views.errors import (
    UnsupportedDatasourceProtocolError,
    ViewLoadingError,
    ViewParseError,
)
from prototyping_inference_engine.api.data.views.model import (
    DatasourceDeclaration,
    DatasourceProtocol,
    MissingValuePolicy,
    ViewAttributeSpec,
    ViewDeclaration,
    ViewDocument,
)
from prototyping_inference_engine.api.data.views.source import (
    CompiledView,
    ViewQueryBackend,
    ViewRuntimeSource,
    build_relation_schema,
    non_mandatory_positions,
)
from prototyping_inference_engine.api.data.views.validation import (
    validate_view_document,
)
from prototyping_inference_engine.api.data.storage.rdbms.drivers import (
    HSQLDBDriver,
    MySQLDriver,
    PostgreSQLDriver,
    SQLiteDriver,
)


class ViewSourceBuilder:
    """Build runtime readable sources from view declaration files."""

    @staticmethod
    def load_from_file(
        path: str | Path,
        *,
        alias_prefix: str | None = None,
        literal_factory: LiteralFactory | None = None,
    ) -> tuple[ViewRuntimeSource, ...]:
        declaration_path = Path(path)
        data = _read_json(declaration_path)
        document = _parse_document(data)
        return ViewSourceBuilder.load_from_document(
            document,
            base_dir=declaration_path.parent,
            alias_prefix=alias_prefix,
            literal_factory=literal_factory,
        )

    @staticmethod
    def load_from_document(
        document: ViewDocument,
        *,
        base_dir: Path | None = None,
        alias_prefix: str | None = None,
        literal_factory: LiteralFactory | None = None,
    ) -> tuple[ViewRuntimeSource, ...]:
        validate_view_document(document, base_dir)

        factory = literal_factory or LiteralFactory(DictStorage())
        sources_by_id: dict[str, ViewRuntimeSource] = {}
        ordered_source_ids: list[str] = []

        for datasource in document.datasources:
            backend = _build_backend(datasource, base_dir)
            source = ViewRuntimeSource(
                name=datasource.id,
                backend=backend,
                literal_factory=factory,
            )
            sources_by_id[datasource.id] = source
            ordered_source_ids.append(datasource.id)

        for declaration in document.views:
            target_source = sources_by_id.get(declaration.datasource)
            if target_source is None:
                raise ViewLoadingError(
                    (
                        f"Cannot register view '{declaration.id}': unknown datasource "
                        f"'{declaration.datasource}'"
                    )
                )

            query_template = _load_query_template(declaration, base_dir)
            predicate_name = (
                f"{alias_prefix}:{declaration.id}" if alias_prefix else declaration.id
            )
            predicate = Predicate(predicate_name, declaration.arity)

            compiled = CompiledView(
                declaration=declaration,
                predicate=predicate,
                query_template=query_template,
                non_mandatory_positions=non_mandatory_positions(declaration),
                schema=build_relation_schema(predicate, declaration),
            )
            target_source.add_view(compiled)

        return tuple(sources_by_id[source_id] for source_id in ordered_source_ids)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ViewParseError(f"View declaration file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ViewParseError(f"Invalid JSON in view declaration file: {path}") from exc


def _parse_document(data: dict[str, Any]) -> ViewDocument:
    if not isinstance(data, dict):
        raise ViewParseError("View declaration root must be a JSON object")

    raw_datasources = data.get("datasources")
    raw_views = data.get("views")
    if not isinstance(raw_datasources, list):
        raise ViewParseError("'datasources' must be a JSON array")
    if not isinstance(raw_views, list):
        raise ViewParseError("'views' must be a JSON array")

    datasources = tuple(_parse_datasource(item) for item in raw_datasources)
    views = tuple(_parse_view(item) for item in raw_views)
    return ViewDocument(datasources=datasources, views=views)


def _parse_datasource(raw: object) -> DatasourceDeclaration:
    if not isinstance(raw, dict):
        raise ViewParseError("Each datasource declaration must be a JSON object")

    id_value = raw.get("id")
    protocol_value = raw.get("protocol")
    parameters_value = raw.get("parameters", {})

    if not isinstance(id_value, str) or not id_value:
        raise ViewParseError("Datasource 'id' must be a non-empty string")
    if not isinstance(protocol_value, str) or not protocol_value:
        raise ViewParseError("Datasource 'protocol' must be a non-empty string")
    if not isinstance(parameters_value, dict):
        raise ViewParseError("Datasource 'parameters' must be a JSON object")

    return DatasourceDeclaration(
        id=id_value,
        protocol=protocol_value,
        parameters=dict(parameters_value),
    )


def _parse_view(raw: object) -> ViewDeclaration:
    if not isinstance(raw, dict):
        raise ViewParseError("Each view declaration must be a JSON object")

    id_value = raw.get("id")
    datasource_value = raw.get("datasource")
    signature_value = raw.get("signature")

    if not isinstance(id_value, str) or not id_value:
        raise ViewParseError("View 'id' must be a non-empty string")
    if not isinstance(datasource_value, str) or not datasource_value:
        raise ViewParseError("View 'datasource' must be a non-empty string")
    if not isinstance(signature_value, list) or not signature_value:
        raise ViewParseError("View 'signature' must be a non-empty array")

    signature = tuple(_parse_signature_entry(entry) for entry in signature_value)

    query = raw.get("query")
    query_file = raw.get("queryFile")
    if query is not None and not isinstance(query, str):
        raise ViewParseError("View 'query' must be a string when present")
    if query_file is not None and not isinstance(query_file, str):
        raise ViewParseError("View 'queryFile' must be a string when present")

    position = raw.get("position")
    if position is not None and not isinstance(position, str):
        raise ViewParseError("View 'position' must be a string when present")

    metadata = raw.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}

    return ViewDeclaration(
        id=id_value,
        datasource=datasource_value,
        signature=signature,
        query=query,
        query_file=query_file,
        position=position,
        metadata=metadata,
    )


def _parse_signature_entry(raw: object) -> ViewAttributeSpec:
    if not isinstance(raw, dict):
        raise ViewParseError("Each signature entry must be a JSON object")

    mandatory = raw.get("mandatory")
    if mandatory is not None and not isinstance(mandatory, str):
        raise ViewParseError("Signature 'mandatory' must be a string when present")

    selection = raw.get("selection")
    if selection is not None and not isinstance(selection, str):
        raise ViewParseError("Signature 'selection' must be a string when present")

    if_missing_raw = raw.get("ifMissing")
    policy = MissingValuePolicy.FREEZE
    if if_missing_raw is not None:
        if not isinstance(if_missing_raw, str):
            raise ViewParseError("Signature 'ifMissing' must be a string when present")
        parsed_policy = MissingValuePolicy.from_label(if_missing_raw)
        if parsed_policy is None:
            warn(
                f"Unknown ifMissing policy '{if_missing_raw}', defaulting to FREEZE",
                stacklevel=2,
            )
        else:
            policy = parsed_policy

    return ViewAttributeSpec(
        mandatory=mandatory,
        if_missing=policy,
        selection=selection,
    )


def _load_query_template(declaration: ViewDeclaration, base_dir: Path | None) -> str:
    if declaration.query is not None:
        return declaration.query
    if declaration.query_file is None:
        raise ViewLoadingError(
            f"View '{declaration.id}' must define query or queryFile"
        )

    query_path = Path(declaration.query_file)
    if not query_path.is_absolute() and base_dir is not None:
        query_path = base_dir / query_path
    try:
        return query_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ViewLoadingError(
            f"View query file not found for view '{declaration.id}': {declaration.query_file}"
        ) from exc


def _build_backend(
    datasource: DatasourceDeclaration,
    base_dir: Path | None,
) -> ViewQueryBackend:
    protocol = DatasourceProtocol.from_label(datasource.protocol)
    if protocol is None:
        raise UnsupportedDatasourceProtocolError(
            f"Unsupported datasource protocol: {datasource.protocol}"
        )

    params = dict(datasource.parameters)

    if protocol == DatasourceProtocol.POSTGRESQL:
        dsn = _postgresql_dsn(params, base_dir)
        return SQLViewBackend(PostgreSQLDriver.from_dsn(dsn))

    if protocol == DatasourceProtocol.MYSQL:
        mysql_params = _mysql_params(params)
        return SQLViewBackend(MySQLDriver.from_params(**mysql_params))

    if protocol == DatasourceProtocol.SQLITE:
        sqlite_path = _resolve_sqlite_path(params, base_dir)
        return SQLViewBackend(SQLiteDriver.from_path(sqlite_path))

    if protocol == DatasourceProtocol.HSQLDB:
        jdbc_url = str(params.get("url", ""))
        if not jdbc_url:
            database = str(params.get("database", ""))
            if database:
                jdbc_url = f"jdbc:hsqldb:{database}"
        user = str(params.get("user", "sa"))
        password = _resolve_password(params, base_dir) or ""
        return SQLViewBackend(
            HSQLDBDriver.from_jdbc(jdbc_url, user=user, password=password)
        )

    if protocol == DatasourceProtocol.SPARQL_ENDPOINT:
        endpoint = str(params.get("url", ""))
        if not endpoint:
            raise ViewLoadingError(
                f"Datasource '{datasource.id}' requires 'url' for SparqlEndpoint"
            )
        sparql_user = str(params.get("user")) if "user" in params else None
        sparql_password = _resolve_password(params, base_dir)
        return SparqlEndpointViewBackend(
            endpoint, user=sparql_user, password=sparql_password
        )

    if protocol == DatasourceProtocol.JSON_WEB_API:
        api_user = str(params.get("user")) if "user" in params else None
        api_password = _resolve_password(params, base_dir)
        return JSONWebAPIViewBackend(user=api_user, password=api_password)

    if protocol == DatasourceProtocol.MONGODB:
        url = str(params.get("url", ""))
        database = str(params.get("database", ""))
        collection = str(params.get("collection", ""))
        if not url or not database or not collection:
            raise ViewLoadingError(
                (
                    f"Datasource '{datasource.id}' requires url/database/collection "
                    f"for MongoDB"
                )
            )
        return MongoDBViewBackend(url=url, database=database, collection=collection)

    raise UnsupportedDatasourceProtocolError(
        f"Unsupported datasource protocol: {datasource.protocol}"
    )


def _postgresql_dsn(params: dict[str, object], base_dir: Path | None) -> str:
    url = str(params.get("url", ""))
    database = str(params.get("database", ""))
    user = str(params.get("user")) if "user" in params else None
    password = _resolve_password(params, base_dir)

    if url.startswith("postgresql://"):
        return url

    if not url:
        raise ViewLoadingError("PostgreSQL datasource requires a 'url' parameter")

    auth = ""
    if user:
        auth = quote_plus(user)
        if password is not None:
            auth += ":" + quote_plus(password)
        auth += "@"

    if database:
        return f"postgresql://{auth}{url}/{database}"
    return f"postgresql://{auth}{url}"


def _mysql_params(params: dict[str, object]) -> dict[str, object]:
    url = str(params.get("url", ""))
    database = str(params.get("database", ""))
    if not url or not database:
        raise ViewLoadingError("MySQL datasource requires 'url' and 'database'")

    host = url
    port = 3306
    if ":" in url:
        host_part, port_part = url.rsplit(":", 1)
        host = host_part
        try:
            port = int(port_part)
        except ValueError:
            host = url

    resolved: dict[str, object] = {
        "host": host,
        "port": port,
        "database": database,
        "autocommit": True,
    }

    if "user" in params:
        resolved["user"] = params["user"]
    if "password" in params:
        resolved["password"] = params["password"]
    return resolved


def _resolve_sqlite_path(params: dict[str, object], base_dir: Path | None) -> str:
    path = str(params.get("url", ""))
    if not path:
        raise ViewLoadingError("SQLite datasource requires 'url'")
    candidate = Path(path)
    if not candidate.is_absolute() and base_dir is not None:
        candidate = base_dir / candidate
    return str(candidate)


def _resolve_password(params: dict[str, object], base_dir: Path | None) -> str | None:
    if "password" in params:
        return str(params["password"])

    password_file = params.get("passwordFile")
    if isinstance(password_file, str):
        candidate = Path(password_file)
        if not candidate.is_absolute() and base_dir is not None:
            candidate = base_dir / candidate
        return candidate.read_text(encoding="utf-8").strip()

    return None


def load_view_sources(
    path: str | Path,
    *,
    alias_prefix: str | None = None,
    literal_factory: LiteralFactory | None = None,
) -> tuple[ViewRuntimeSource, ...]:
    """Convenience function around ViewSourceBuilder.load_from_file."""
    return ViewSourceBuilder.load_from_file(
        path,
        alias_prefix=alias_prefix,
        literal_factory=literal_factory,
    )


def load_view_sources_from_document(
    document: ViewDocument,
    *,
    base_dir: Path | None = None,
    alias_prefix: str | None = None,
    literal_factory: LiteralFactory | None = None,
) -> tuple[ViewRuntimeSource, ...]:
    """Convenience function around ViewSourceBuilder.load_from_document."""
    return ViewSourceBuilder.load_from_document(
        document,
        base_dir=base_dir,
        alias_prefix=alias_prefix,
        literal_factory=literal_factory,
    )
